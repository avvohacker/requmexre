"""The account bundle must be a fresh build of the skill, pinned by the loader.

The bootstrap loader ships a SHA-256, and the bundle is a generated artifact.
This test rebuilds the payload from skill/requmexre/, compares the digest with
the pin in the loader, and checks that the checked-in bundle contains the same
source bytes. A stale bundle or a forgotten hash update fails here.
"""

from __future__ import annotations

import base64
import bz2
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "skill" / "install"
BUILD = INSTALL / "build_bundle.py"
BUNDLE = INSTALL / "requmexre.bundle"
LOADER = INSTALL / "requmexre.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("requmexre_build_bundle", BUILD)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rebuilt_bundle_matches_the_checked_in_bundle_and_loader_hash():
    builder = load_builder()
    payload = builder.build_payload()
    expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    loader = LOADER.read_text(encoding="utf-8")
    match = re.search(r'BUNDLE_SHA256 = "([0-9a-f]{64})"', loader)
    assert match, "the loader has no BUNDLE_SHA256 pin"
    assert match.group(1) == expected

    assert BUNDLE.read_text(encoding="utf-8").strip() == payload

    package = json.loads(bz2.decompress(base64.b64decode(payload)).decode("utf-8"))
    assert set(package) == set(builder.INCLUDE)
    for relative, text in package.items():
        source = ROOT / "skill" / "requmexre" / relative
        assert source.read_text(encoding="utf-8") == text
