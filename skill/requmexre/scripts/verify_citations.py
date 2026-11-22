#!/usr/bin/env python3
"""requmexre — citation verifier.

Reads `warrant.evidence` and checks each entry against the record it names.

What it checks
- an identifier: DOI, PMID, arXiv ID, ISBN or URL;
- that the record exists;
- that the citation's year and title agree with the record;
- whether the record is open access, and whether an abstract is available.

What it cannot check
- that the source says what the document attributes to it. It compares the
  abstract with the gap statement only as a signal; the full text may be
  paywalled. The report names that limit on every run.

No API key is required. `REQMEXRE_CONTACT_EMAIL` is used for the Crossref and
OpenAlex polite pools; `NCBI_API_KEY` raises the PubMed rate limit. Neither is
written to the document.

Usage
    python3 verify_citations.py plan.json
    python3 verify_citations.py --json plan.json
    python3 verify_citations.py --offline plan.json
    python3 verify_citations.py --strict plan.json

Exit status: 0 no citation failed; 1 a citation was not found or its metadata
disagrees; 2 bad usage. `--strict` also fails an entry with no identifier, an
unreachable service or an unchecked entry.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

VERSION = "1.2"
CONTACT = os.environ.get("REQMEXRE_CONTACT_EMAIL", "").strip()
NCBI_KEY = os.environ.get("NCBI_API_KEY", "").strip()
USER_AGENT = f"requmexre/{VERSION} citation-checker"
if CONTACT:
    USER_AGENT += f" (mailto:{CONTACT})"

DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]+", re.IGNORECASE)
PMID_RE = re.compile(r"\bpmid\s*:?\s*(\d{1,9})\b", re.IGNORECASE)
ARXIV_RE = re.compile(
    r"\barxiv\s*(?::|/|\s)\s*"
    r"(\d{4}\.\d{4,5}(?:v\d+)?|[a-z][a-z-]*(?:\.[A-Z]{2})?/\d{7})",
    re.IGNORECASE,
)
ISBN_RE = re.compile(
    r"\bisbn(?:-1[03])?\s*:?\s*((?:97[89][\s-]?)?(?:\d[\s-]?){9}[\dXx])",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

STOPWORDS = set(
    """a an the and or but if then than that this these those of to in on at by for
    with from into over under as is are was were be been being do does did done have
    has had not no nor so such it its their they we you he she them our your his her
    who whom whose which what when where why how whether there here also more most
    less least other another any all each both some only very can could should would
    may might must will shall about after before between among during through within
    without upon against per via using used use study studies research paper article
    literature evidence data result results finding findings""".split()
)

GENERIC_TOPIC_WORDS = STOPWORDS | {
    "association",
    "collected",
    "different",
    "estimated",
    "local",
    "agencies",
}


class ResolutionError(Exception):
    """A record that cannot be resolved, with a status for the report."""

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass(frozen=True)
class Identifier:
    kind: str
    value: str

    def label(self) -> str:
        return f"{self.kind.upper()} {self.value}"


@dataclass
class Record:
    source: str
    title: str = ""
    year: int | None = None
    authors: list[str] = field(default_factory=list)
    container: str = ""
    abstract: str = ""
    oa_status: str = "unknown"
    oa_url: str = ""
    url: str = ""

    def to_dict(self) -> dict:
        abstract = self.abstract.strip()
        return {
            "source": self.source,
            "title": self.title,
            "year": self.year,
            "authors": self.authors,
            "container": self.container,
            "abstract": abstract[:4000],
            "abstract_truncated": len(abstract) > 4000,
            "open_access": {
                "status": self.oa_status,
                "url": self.oa_url,
                "full_text": "paywalled" if self.oa_status == "closed" else "unknown",
            },
            "url": self.url,
        }


# --------------------------------------------------------------------------
# Identifiers
# --------------------------------------------------------------------------


def _clean_url(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[.,;:]+$", "", value)
    while value.endswith(")") and value.count("(") < value.count(")"):
        value = value[:-1]
    return value


def _clean_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[.,;:]+$", "", value)
    while value.endswith(")") and value.count("(") < value.count(")"):
        value = value[:-1]
    return value.lower()


def _clean_isbn(value: str) -> str:
    return re.sub(r"[\s-]", "", value).upper()


def extract_identifier(text: str) -> Identifier | None:
    """Return the first identifier in text, in priority order."""
    match = DOI_RE.search(text)
    if match:
        return Identifier("doi", _clean_doi(match.group(0)))

    match = PMID_RE.search(text)
    if match:
        return Identifier("pmid", match.group(1))

    match = ARXIV_RE.search(text)
    if match:
        return Identifier("arxiv", match.group(1))

    match = ISBN_RE.search(text)
    if match:
        return Identifier("isbn", _clean_isbn(match.group(1)))

    match = URL_RE.search(text)
    if match:
        return Identifier("url", _clean_url(match.group(0)))

    return None


# --------------------------------------------------------------------------
# Network
# --------------------------------------------------------------------------


def _host(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc or "the service"


class Client:
    """A small, polite HTTP client with no third-party dependency."""

    def __init__(
        self,
        timeout: float = 10.0,
        delay: float = 0.2,
        offline: bool = False,
    ) -> None:
        self.timeout = timeout
        self.delay = delay
        self.offline = offline
        self._last = 0.0

    def _wait(self) -> None:
        if self.delay <= 0:
            return
        pause = self.delay - (time.monotonic() - self._last)
        if pause > 0:
            time.sleep(pause)

    def get(self, url: str, limit: int = 262144) -> tuple[int, bytes, str]:
        if self.offline:
            raise ResolutionError("unchecked", "offline mode: no request made")
        self._wait()
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json, application/atom+xml, text/html;q=0.9, */*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read(limit), response.geturl()
        except urllib.error.HTTPError as error:
            return error.code, b"", url
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            reason = getattr(error, "reason", error)
            raise ResolutionError(
                "unreachable", f"{_host(url)}: {type(error).__name__}: {reason}"
            ) from error
        finally:
            self._last = time.monotonic()

    def get_json(self, url: str) -> dict:
        status, body, _ = self.get(url)
        if status in (401, 403):
            raise ResolutionError("restricted", f"{_host(url)} returned HTTP {status}")
        if status in (404, 410):
            raise ResolutionError("not_found", f"{_host(url)} returned HTTP {status}")
        if status >= 400:
            raise ResolutionError("unreachable", f"{_host(url)} returned HTTP {status}")
        try:
            data = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ResolutionError(
                "unreachable", f"{_host(url)} returned no readable JSON"
            ) from error
        if not isinstance(data, dict):
            raise ResolutionError("unreachable", f"{_host(url)} returned no JSON object")
        return data

    def get_text(self, url: str) -> str:
        status, body, _ = self.get(url)
        if status in (401, 403):
            raise ResolutionError("restricted", f"{_host(url)} returned HTTP {status}")
        if status in (404, 410):
            raise ResolutionError("not_found", f"{_host(url)} returned HTTP {status}")
        if status >= 400:
            raise ResolutionError("unreachable", f"{_host(url)} returned HTTP {status}")
        return body.decode("utf-8", "replace")


# --------------------------------------------------------------------------
# Resolvers
# --------------------------------------------------------------------------


def _abstract_from_inverted(index) -> str:
    if not isinstance(index, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for word, places in index.items():
        if not isinstance(places, list):
            continue
        for place in places:
            if isinstance(place, int):
                positions.append((place, word))
    return " ".join(word for _, word in sorted(positions))


def _from_openalex(data: dict) -> Record:
    authors = []
    for authorship in data.get("authorships") or []:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author") or {}
        name = author.get("display_name") or authorship.get("raw_author_name") or ""
        if name:
            authors.append(name)
    location = data.get("primary_location") or {}
    source = location.get("source") or {}
    oa = data.get("open_access") or {}
    best = data.get("best_oa_location") or {}
    status = oa.get("oa_status")
    if not status:
        status = "open" if oa.get("is_oa") else "unknown"
    return Record(
        source="openalex",
        title=data.get("title") or data.get("display_name") or "",
        year=data.get("publication_year"),
        authors=authors,
        container=source.get("display_name") or "",
        abstract=_abstract_from_inverted(data.get("abstract_inverted_index")),
        oa_status=status,
        oa_url=oa.get("oa_url")
        or best.get("pdf_url")
        or best.get("landing_page_url")
        or "",
        url=data.get("id") or "",
    )


def _resolve_openalex(identifier: Identifier, client: Client) -> Record:
    path = urllib.parse.quote(f"{identifier.kind}:{identifier.value}", safe=":/")
    url = f"https://api.openalex.org/works/{path}"
    if CONTACT:
        url += "?" + urllib.parse.urlencode({"mailto": CONTACT})
    return _from_openalex(client.get_json(url))


def _first_year(value) -> int | None:
    if not isinstance(value, dict):
        return None
    parts = value.get("date-parts") or []
    if parts and isinstance(parts[0], list) and parts[0]:
        try:
            return int(parts[0][0])
        except (TypeError, ValueError):
            return None
    return None


def _year_from_text(value: str) -> int | None:
    match = YEAR_RE.search(str(value))
    return int(match.group(0)) if match else None


def _strip_tags(value: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", value).split())


def _resolve_crossref(doi: str, client: Client) -> Record:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    message = client.get_json(url).get("message") or {}
    authors = [
        item.get("family") or item.get("name") or ""
        for item in message.get("author") or []
        if isinstance(item, dict)
    ]
    year = (
        _first_year(message.get("issued"))
        or _first_year(message.get("published-print"))
        or _first_year(message.get("published-online"))
    )
    return Record(
        source="crossref",
        title=" ".join(message.get("title") or []),
        year=year,
        authors=[author for author in authors if author],
        container=" ".join(message.get("container-title") or []),
        abstract=_strip_tags(message.get("abstract") or ""),
        oa_status="unknown",
        url=message.get("URL") or f"https://doi.org/{doi}",
    )


def _resolve_pubmed(pmid: str, client: Client) -> Record:
    query = {"db": "pubmed", "id": pmid, "retmode": "json", "tool": "requmexre"}
    if CONTACT:
        query["email"] = CONTACT
    if NCBI_KEY:
        query["api_key"] = NCBI_KEY
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + (
        urllib.parse.urlencode(query)
    )
    data = client.get_json(url)
    item = (data.get("result") or {}).get(pmid)
    if not isinstance(item, dict) or item.get("error"):
        raise ResolutionError("not_found", f"PubMed has no record for PMID {pmid}")
    return Record(
        source="pubmed",
        title=str(item.get("title") or "").rstrip("."),
        year=_year_from_text(item.get("pubdate") or ""),
        authors=[
            str(author.get("name") or "")
            for author in item.get("authors") or []
            if isinstance(author, dict)
        ],
        container=item.get("fulljournalname") or "",
        oa_status="unknown",
        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    )


def _resolve_arxiv(arxiv_id: str, client: Client) -> Record:
    query = urllib.parse.urlencode({"id_list": arxiv_id})
    text = client.get_text(f"https://export.arxiv.org/api/query?{query}")
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as error:
        raise ResolutionError("unreachable", "arXiv returned no readable Atom feed") from error
    namespace = {"a": "http://www.w3.org/2005/Atom"}
    entries = root.findall("a:entry", namespace)
    if not entries:
        raise ResolutionError("not_found", f"arXiv has no record for {arxiv_id}")
    entry = entries[0]
    title = " ".join(
        (entry.findtext("a:title", default="", namespaces=namespace) or "").split()
    )
    published = entry.findtext("a:published", default="", namespaces=namespace) or ""
    authors = [
        " ".join((author.findtext("a:name", default="", namespaces=namespace) or "").split())
        for author in entry.findall("a:author", namespace)
    ]
    summary = " ".join(
        (entry.findtext("a:summary", default="", namespaces=namespace) or "").split()
    )
    journal = (
        entry.findtext(
            "{http://arxiv.org/schemas/atom}journal_ref",
            default="",
            namespaces=namespace,
        )
        or ""
    )
    return Record(
        source="arxiv",
        title=title,
        year=_year_from_text(published),
        authors=[author for author in authors if author],
        container=journal,
        abstract=summary,
        oa_status="green",
        oa_url=f"https://arxiv.org/abs/{arxiv_id}",
        url=f"https://arxiv.org/abs/{arxiv_id}",
    )


def _resolve_isbn(isbn: str, client: Client) -> Record:
    query = urllib.parse.urlencode(
        {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
    )
    data = client.get_json(f"https://openlibrary.org/api/books?{query}")
    item = data.get(f"ISBN:{isbn}")
    if not isinstance(item, dict):
        raise ResolutionError("not_found", f"Open Library has no record for ISBN {isbn}")
    return Record(
        source="openlibrary",
        title=str(item.get("title") or ""),
        year=_year_from_text(item.get("publish_date") or ""),
        authors=[
            str(author.get("name") or "")
            for author in item.get("authors") or []
            if isinstance(author, dict)
        ],
        container="; ".join(
            str(publisher.get("name") or "")
            for publisher in item.get("publishers") or []
            if isinstance(publisher, dict)
        ),
        oa_status="unknown",
        url=str(item.get("url") or ""),
    )


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def _html_title(body: bytes) -> str:
    parser = _TitleParser()
    try:
        parser.feed(body.decode("utf-8", "replace"))
    except Exception:
        return ""
    return " ".join(" ".join(parser.parts).split())


def _resolve_url(url: str, client: Client) -> Record:
    status, body, final = client.get(url)
    if status in (401, 403):
        raise ResolutionError("restricted", f"{_host(url)} returned HTTP {status}")
    if status in (404, 410):
        raise ResolutionError("not_found", f"{_host(url)} returned HTTP {status}")
    if status >= 400:
        raise ResolutionError("unreachable", f"{_host(url)} returned HTTP {status}")
    return Record(
        source="url",
        title=_html_title(body),
        oa_status="url",
        oa_url=final,
        url=final,
    )


def _with_fallback(primary, fallback):
    """Try the first service, then the second; keep the informative failure."""
    try:
        return primary()
    except ResolutionError as first:
        try:
            return fallback()
        except ResolutionError as second:
            if second.status == "not_found" and first.status != "not_found":
                raise first
            raise


def resolve(identifier: Identifier, client: Client) -> Record:
    """Resolve one identifier to a record, or raise ResolutionError."""
    if identifier.kind == "doi":
        return _with_fallback(
            lambda: _resolve_openalex(identifier, client),
            lambda: _resolve_crossref(identifier.value, client),
        )

    if identifier.kind == "pmid":
        return _with_fallback(
            lambda: _resolve_openalex(identifier, client),
            lambda: _resolve_pubmed(identifier.value, client),
        )

    if identifier.kind == "arxiv":
        return _resolve_arxiv(identifier.value, client)
    if identifier.kind == "isbn":
        return _resolve_isbn(identifier.value, client)
    if identifier.kind == "url":
        return _resolve_url(identifier.value, client)
    raise ResolutionError("unreachable", f"unknown identifier kind {identifier.kind!r}")


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _words(text: str) -> list[str]:
    return [word for word in _normalise(text).split() if len(word) > 2 and word not in STOPWORDS]


def _surname(name: str) -> str:
    name = name.strip()
    if not name:
        return ""
    if "," in name:
        return name.split(",", 1)[0].strip()
    parts = name.split()
    if len(parts) > 1 and len(parts[-1].rstrip(".")) <= 2:
        return parts[-2]
    return parts[-1]


def check_record(citation: str, record: Record) -> list[dict]:
    """Compare what the citation asserts with the record's metadata."""
    checks: list[dict] = []

    cited_years = sorted({int(match.group(0)) for match in YEAR_RE.finditer(citation)})
    if record.year is None:
        checks.append(
            {"name": "year", "status": "unavailable", "detail": "the record has no year"}
        )
    elif cited_years:
        if any(abs(record.year - year) <= 1 for year in cited_years):
            checks.append(
                {"name": "year", "status": "agree", "detail": f"record year {record.year}"}
            )
        else:
            checks.append(
                {
                    "name": "year",
                    "status": "disagree",
                    "detail": (
                        "citation says "
                        + ", ".join(str(year) for year in cited_years)
                        + f"; record says {record.year}"
                    ),
                }
            )
    else:
        checks.append(
            {
                "name": "year",
                "status": "not_in_citation",
                "detail": f"record year {record.year}; the citation states no year",
            }
        )

    title_words = set(_words(record.title))
    if not record.title:
        checks.append(
            {"name": "title", "status": "unavailable", "detail": "the record has no title"}
        )
    elif len(title_words) < 2:
        checks.append(
            {
                "name": "title",
                "status": "unavailable",
                "detail": "the record title is too short to compare",
            }
        )
    else:
        cited_words = set(_words(citation))
        shared = title_words & cited_words
        ratio = len(shared) / len(title_words)
        if ratio >= 0.6:
            checks.append(
                {
                    "name": "title",
                    "status": "agree",
                    "detail": f"{round(ratio * 100)} per cent of the record title is in the citation",
                }
            )
        elif not shared:
            checks.append(
                {
                    "name": "title",
                    "status": "not_in_citation",
                    "detail": "the citation states no words from the record title",
                }
            )
        else:
            checks.append(
                {
                    "name": "title",
                    "status": "partial",
                    "detail": (
                        f"only {round(ratio * 100)} per cent of the record title is in the "
                        f"citation: {record.title!r}"
                    ),
                }
            )

    surnames = {_surname(author) for author in record.authors if _surname(author)}
    if not surnames:
        checks.append(
            {"name": "author", "status": "unavailable", "detail": "the record has no author"}
        )
    else:
        cited = " " + _normalise(citation) + " "
        found = sorted(
            surname for surname in surnames if f" {_normalise(surname)} " in cited
        )
        if found:
            checks.append(
                {
                    "name": "author",
                    "status": "agree",
                    "detail": "the citation names " + ", ".join(found),
                }
            )
        else:
            checks.append(
                {
                    "name": "author",
                    "status": "not_in_citation",
                    "detail": "no author surname from the record appears in the citation",
                }
            )

    return checks


def topic_signal(gap: str, record: Record) -> dict | None:
    """A lexical signal, not a verdict, when an abstract is available."""
    if not gap or not record.abstract:
        return None
    gap_words = {word for word in _words(gap) if word not in GENERIC_TOPIC_WORDS}
    abstract_words = set(_words(record.abstract))
    shared = sorted(gap_words & abstract_words)
    ratio = len(shared) / max(1, len(gap_words))
    return {
        "name": "topic",
        "status": "signal",
        "ratio": round(ratio, 2),
        "shared": shared[:10],
        "detail": (
            "the abstract shares "
            + (", ".join(shared[:6]) if shared else "no content words")
            + " with the gap statement; read the abstract before treating it as support"
        ),
    }


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


def verify_document(document: dict, client: Client, strict: bool = False) -> dict:
    warrant = document.get("warrant") if isinstance(document, dict) else None
    evidence = warrant.get("evidence") if isinstance(warrant, dict) else None
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("the document has no non-empty warrant.evidence list")
    gap = str(warrant.get("gap_statement") or "")

    citations = []
    for index, citation in enumerate(evidence):
        text = str(citation)
        entry = {"index": index + 1, "citation": text}
        identifier = extract_identifier(text)
        if identifier is None:
            entry.update(
                status="no_identifier",
                note="add a DOI, PMID, arXiv ID, ISBN or URL so the source can be found",
            )
            citations.append(entry)
            continue

        entry["identifier"] = {"kind": identifier.kind, "value": identifier.value}
        if client.offline:
            entry.update(status="unchecked", note="offline mode: no request made")
            citations.append(entry)
            continue

        try:
            record = resolve(identifier, client)
        except ResolutionError as error:
            entry.update(status=error.status, note=error.message)
            citations.append(entry)
            continue

        checks = check_record(text, record)
        topic = topic_signal(gap, record)
        if topic is not None:
            checks.append(topic)
        entries = [check for check in checks if check["status"] in ("disagree", "partial")]
        entry.update(
            status="mismatch" if entries else "ok",
            record=record.to_dict(),
            checks=checks,
        )
        if entries:
            entry["note"] = "; ".join(
                f"{check['name']}: {check['detail']}" for check in entries
            )
        elif record.oa_status == "closed":
            entry["note"] = "metadata agrees; full text is paywalled and was not read"
        citations.append(entry)

    failed = [entry for entry in citations if entry["status"] in ("mismatch", "not_found")]
    unresolved = [
        entry
        for entry in citations
        if entry["status"] in ("restricted", "unreachable", "no_identifier", "unchecked")
    ]
    ok = not failed and (not strict or not unresolved)

    return {
        "tool": "requmexre-citations",
        "version": VERSION,
        "ok": ok,
        "strict": strict,
        "offline": client.offline,
        "total": len(citations),
        "verified": sum(1 for entry in citations if entry["status"] == "ok"),
        "failed": len(failed),
        "unresolved": len(unresolved),
        "limits": (
            "Metadata only: a paywalled full text is not read, and a claim is not "
            "verified against it. The topic check is a lexical signal, not a verdict."
        ),
        "citations": citations,
    }


def _label(status: str) -> str:
    return {
        "ok": "OK",
        "mismatch": "FAIL",
        "not_found": "FAIL",
        "restricted": "WARN",
        "unreachable": "WARN",
        "no_identifier": "WARN",
        "unchecked": "SKIP",
    }.get(status, "WARN")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="verify_citations.py",
        description=(
            "Check the sources in warrant.evidence: identifiers, existence, title, "
            "year, author and open-access status."
        ),
        epilog=(
            "Exit status: 0 every citation was resolved without a mismatch; 1 a "
            "citation was not found or its metadata disagrees; 2 bad usage. "
            "--strict also fails an entry left unresolved."
        ),
    )
    parser.add_argument("file", nargs="?", metavar="DOCUMENT", help="a validated plan.json")
    parser.add_argument("--json", action="store_true", help="write one JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when a citation has no identifier, the service is unreachable, or the entry was not checked",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="extract identifiers without making a network request",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, metavar="SECONDS", help="request timeout"
    )
    parser.add_argument(
        "--delay", type=float, default=0.2, metavar="SECONDS", help="pause between requests"
    )
    parser.add_argument("--version", action="version", version=f"requmexre citations v{VERSION}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.file:
        print(
            "no document given. Pass a plan.json to check its warrant.evidence.",
            file=sys.stderr,
        )
        return 2

    path = Path(args.file)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read {path}: {error}", file=sys.stderr)
        return 2

    client = Client(timeout=args.timeout, delay=args.delay, offline=args.offline)
    try:
        report = verify_document(document, client, strict=args.strict)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"requmexre citation check v{VERSION} — source metadata, not full text\n")
        for entry in report["citations"]:
            identifier = entry.get("identifier")
            label = identifier["kind"].upper() + " " + identifier["value"] if identifier else "no identifier"
            record = entry.get("record") or {}
            detail = record.get("title") or entry.get("note") or ""
            print(f"{_label(entry['status']):<5} [{entry['index']}] {label:<34} {detail}")
            for check in entry.get("checks") or []:
                if check["status"] == "agree":
                    continue
                if check["status"] == "signal":
                    print(f"      topic: {check['detail']}")
                    continue
                print(f"      {check['name']}: {check['status']} — {check['detail']}")
            if entry.get("note") and entry["status"] == "ok":
                print(f"      note: {entry['note']}")
        print()
        print(
            f"{report['verified']} of {report['total']} citations verified; "
            f"{report['unresolved']} unresolved; {report['failed']} failed."
        )
        if args.offline:
            print("Offline: identifiers were extracted but no source was checked.")
        print("Metadata only: a paywalled full text is not read, and a claim is not verified against it.")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
