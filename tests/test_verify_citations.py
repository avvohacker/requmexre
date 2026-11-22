"""Citation checks: identifiers, metadata agreement and the offline CLI.

The verifier must never make a network request in this suite. The resolver is
patched for the metadata cases, and the CLI is run with --offline; the live
services are exercised by hand, not by CI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import verify_citations as vc

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skill" / "requmexre" / "assets" / "template.json"


def plan_with(evidence, gap="Green space and walking among older adults."):
    document = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    document["warrant"]["evidence"] = evidence
    document["warrant"]["gap_statement"] = gap
    return document


# --------------------------------------------------------------------------
# Identifier extraction
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "citation,kind,value",
    [
        ("LeCun, Bengio and Hinton, Deep learning, Nature, 2015, doi:10.1038/nature14539", "doi", "10.1038/nature14539"),
        ("https://doi.org/10.1038/NATURE14539", "doi", "10.1038/nature14539"),
        ("LeCun et al., Deep learning, PMID: 26017442", "pmid", "26017442"),
        ("Vaswani et al., Attention is all you need, arXiv:1706.03762", "arxiv", "1706.03762"),
        ("Knuth, The Art of Computer Programming, ISBN 978-0-201-89683-1", "isbn", "9780201896831"),
        ("Report at https://example.org/a/report.pdf", "url", "https://example.org/a/report.pdf"),
    ],
    ids=["doi", "doi-url", "pmid", "arxiv", "isbn", "url"],
)
def test_extracts_the_identifier(citation, kind, value):
    identifier = vc.extract_identifier(citation)

    assert identifier is not None
    assert identifier.kind == kind
    assert identifier.value == value


def test_a_doi_with_balanced_parentheses_survives_cleaning():
    identifier = vc.extract_identifier(
        "The Lancet, 2018, doi:10.1016/S0140-6736(18)32279-7."
    )

    assert identifier is not None
    assert identifier.value == "10.1016/s0140-6736(18)32279-7"


def test_a_citation_without_an_identifier_is_reported():
    assert vc.extract_identifier("City of Ghent, green-space inventory, 2025") is None


# --------------------------------------------------------------------------
# Metadata checks
# --------------------------------------------------------------------------


def record():
    return vc.Record(
        source="test",
        title="Deep learning for image classification",
        year=2015,
        authors=["Yann LeCun", "Yoshua Bengio"],
    )


def status(checks, name):
    return next(check["status"] for check in checks if check["name"] == name)


def test_year_and_title_agree():
    checks = vc.check_record(
        "LeCun and Bengio, Deep learning for image classification, 2015, doi:10.1000/x",
        record(),
    )

    assert status(checks, "year") == "agree"
    assert status(checks, "title") == "agree"
    assert status(checks, "author") == "agree"


def test_a_year_mismatch_is_a_disagreement():
    checks = vc.check_record(
        "LeCun and Bengio, Deep learning for image classification, 2019", record()
    )

    assert status(checks, "year") == "disagree"


def test_a_two_word_title_is_still_compared():
    item = vc.Record(source="test", title="Deep learning", year=2015, authors=["Yann LeCun"])

    checks = vc.check_record("LeCun, Deep learning, 2015", item)

    assert status(checks, "title") == "agree"


def test_a_partial_title_is_a_warning_not_an_agreement():
    checks = vc.check_record("LeCun, Deep learning, 2015", record())

    assert status(checks, "title") == "partial"


def test_a_citation_without_a_title_is_not_flagged_as_a_mismatch():
    checks = vc.check_record("LeCun and Bengio, 2015, doi:10.1000/x", record())

    assert status(checks, "title") == "not_in_citation"


def test_a_missing_author_is_reported_as_not_in_the_citation():
    checks = vc.check_record("Deep learning for image classification, 2015", record())

    assert status(checks, "author") == "not_in_citation"


def test_topic_overlap_is_a_signal_when_an_abstract_exists():
    item = record()
    item.abstract = "Green space is associated with walking among older adults."

    signal = vc.topic_signal("Green space and walking among older adults", item)

    assert signal is not None
    assert signal["status"] == "signal"
    assert "walking" in signal["shared"]


# --------------------------------------------------------------------------
# Report and CLI
# --------------------------------------------------------------------------


def test_offline_mode_extracts_without_calling_the_resolver(monkeypatch):
    def fail(*arguments, **keywords):
        raise AssertionError("the resolver must not run offline")

    monkeypatch.setattr(vc, "resolve", fail)
    report = vc.verify_document(
        plan_with(["LeCun, Deep learning, 2015, doi:10.1038/nature14539"]),
        vc.Client(offline=True),
    )

    assert report["ok"] is True
    assert report["offline"] is True
    assert report["citations"][0]["status"] == "unchecked"
    assert report["citations"][0]["identifier"]["kind"] == "doi"


def test_offline_strict_fails_an_unchecked_entry():
    report = vc.verify_document(
        plan_with(["LeCun, Deep learning, 2015, doi:10.1038/nature14539"]),
        vc.Client(offline=True),
        strict=True,
    )

    assert report["ok"] is False
    assert report["unresolved"] == 1


def test_a_missing_identifier_is_a_warning_not_a_failure():
    report = vc.verify_document(
        plan_with(["City of Ghent, green-space inventory, 2025"]),
        vc.Client(offline=True),
    )

    assert report["ok"] is True
    assert report["citations"][0]["status"] == "no_identifier"
    assert report["unresolved"] == 1


def test_a_not_found_source_fails(monkeypatch):
    def missing(identifier, client):
        raise vc.ResolutionError("not_found", "no record")

    monkeypatch.setattr(vc, "resolve", missing)
    report = vc.verify_document(
        plan_with(["LeCun, Deep learning, 2015, doi:10.1038/nature14539"]),
        vc.Client(delay=0),
    )

    assert report["ok"] is False
    assert report["citations"][0]["status"] == "not_found"
    assert report["failed"] == 1


def test_a_doi_falls_back_to_crossref(monkeypatch):
    def missing(identifier, client):
        raise vc.ResolutionError("not_found", "not in OpenAlex")

    monkeypatch.setattr(vc, "_resolve_openalex", missing)
    monkeypatch.setattr(vc, "_resolve_crossref", lambda doi, client: record())

    resolved = vc.resolve(vc.Identifier("doi", "10.1000/x"), vc.Client(offline=True))

    assert resolved.source == "test"


def test_a_metadata_mismatch_fails(monkeypatch):
    def other(identifier, client):
        return vc.Record(
            source="test",
            title="A different paper about something else",
            year=1990,
            authors=["Someone Else"],
        )

    monkeypatch.setattr(vc, "resolve", other)
    report = vc.verify_document(
        plan_with(["LeCun, Deep learning for image classification, 2015, doi:10.1000/x"]),
        vc.Client(delay=0),
    )

    assert report["ok"] is False
    assert report["citations"][0]["status"] == "mismatch"
    assert report["failed"] == 1


def test_cli_json_report_with_offline(tmp_path, capsys):
    path = tmp_path / "plan.json"
    path.write_text(
        json.dumps(plan_with(["LeCun, Deep learning, 2015, doi:10.1038/nature14539"])),
        encoding="utf-8",
    )

    code = vc.main(["--json", "--offline", str(path)])
    report = json.loads(capsys.readouterr().out)

    assert code == 0
    assert report["tool"] == "requmexre-citations"
    assert report["total"] == 1
    assert report["citations"][0]["status"] == "unchecked"
    assert "Metadata only" in report["limits"]


def test_cli_refuses_a_missing_file(tmp_path):
    assert vc.main(["--offline", str(tmp_path / "absent.json")]) == 2


def test_cli_refuses_a_document_without_evidence(tmp_path):
    path = tmp_path / "plan.json"
    document = plan_with([])
    path.write_text(json.dumps(document), encoding="utf-8")

    assert vc.main(["--offline", str(path)]) == 2


def test_cli_help_documents_the_offline_flag():
    result = subprocess.run(
        [sys.executable, str(ROOT / "schema" / "verify_citations.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0
    assert "--offline" in result.stdout
    assert "--strict" in result.stdout
