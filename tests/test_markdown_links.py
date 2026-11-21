"""Relative Markdown links must point at files that exist.

A rename that leaves a link behind is invisible to the validator and to the
site build, so it is caught here. External URLs, pure anchors and generated
directories are out of scope: the first need a network, the second are checked
by the renderer, and the third are rebuildable.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATED = {".git", ".venv", "_out", "__pycache__", ".pytest_cache", "node_modules"}
FENCE = re.compile(r"```.*?```", re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not GENERATED.intersection(path.parts)
    )


def relative_links(source: Path) -> list[str]:
    """Return the link targets that name a path inside this repository."""

    text = FENCE.sub("", source.read_text(encoding="utf-8"))
    targets = []
    for target in LINK.findall(text):
        target = target.strip()
        if not target or target.startswith(("#", "//")) or SCHEME.match(target):
            continue
        targets.append(target)
    return targets


def missing_links(source: Path) -> list[str]:
    """Return the relative targets of source that do not resolve to a file."""

    missing = []
    for target in relative_links(source):
        path = (source.parent / unquote(target.split("#", 1)[0])).resolve()
        if not path.exists():
            missing.append(target)
    return missing


CASES = [
    pytest.param(source, target, id=f"{source.relative_to(ROOT)} -> {target}")
    for source in markdown_files()
    for target in relative_links(source)
]


def test_relative_links_are_collected() -> None:
    assert markdown_files(), "no Markdown files found"
    assert CASES, "no relative Markdown links found"


@pytest.mark.parametrize("source,target", CASES)
def test_relative_link_resolves(source: Path, target: str) -> None:
    assert target not in missing_links(source), (
        f"{source.relative_to(ROOT)} links to missing {target}"
    )


def test_broken_relative_link_is_reported(tmp_path: Path) -> None:
    source = tmp_path / "draft.md"
    (tmp_path / "present.md").write_text("ok\n", encoding="utf-8")
    source.write_text(
        "[good](present.md)\n[broken](missing.md)\n",
        encoding="utf-8",
    )

    assert missing_links(source) == ["missing.md"]
