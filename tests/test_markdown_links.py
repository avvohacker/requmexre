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


CASES = [
    pytest.param(source, target, id=f"{source.relative_to(ROOT)} -> {target}")
    for source in markdown_files()
    for target in relative_links(source)
]


@pytest.mark.parametrize("source,target", CASES)
def test_relative_link_resolves(source: Path, target: str) -> None:
    path = (source.parent / unquote(target.split("#", 1)[0])).resolve()
    assert path.exists(), f"{source.relative_to(ROOT)} links to missing {target}"
