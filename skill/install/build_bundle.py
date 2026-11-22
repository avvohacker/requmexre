#!/usr/bin/env python3
"""Rebuild the self-extracting account bundle and update the loader's SHA-256.

The bundle is one base64(bz2(json)) string. It carries every installed file
except the bootstrap loader itself; the loader downloads it, verifies the hash
and unpacks it. Run this after changing anything under skill/requmexre/:

    python3 skill/install/build_bundle.py

`--check` verifies the checked-in bundle and the loader pin without writing.
"""

from __future__ import annotations

import base64
import bz2
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "skill" / "requmexre"
BUNDLE = HERE / "requmexre.bundle"
LOADER = HERE / "requmexre.py"

INCLUDE = (
    "SKILL.md",
    "references/RULES.md",
    "references/mappings.md",
    "references/review.md",
    "references/fwo-example.md",
    "assets/mappings.json",
    "assets/template.json",
    "assets/requmexre.schema.json",
    "scripts/validate.py",
    "scripts/render.py",
    "scripts/verify_citations.py",
)


def build_payload(source=SOURCE):
    """Return the exact base64 text stored in requmexre.bundle."""
    data = {
        name: (Path(source) / name).read_text(encoding="utf-8")
        for name in INCLUDE
    }
    encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(bz2.compress(encoded, 9)).decode("ascii")


def digest(payload):
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def loader_digest(path=LOADER):
    text = Path(path).read_text(encoding="utf-8")
    match = re.search(r'BUNDLE_SHA256 = "([0-9a-f]{64})"', text)
    if not match:
        raise SystemExit(f"{path} has no BUNDLE_SHA256 pin")
    return match.group(1)


def write_bundle(payload, path=BUNDLE):
    Path(path).write_text(payload + "\n", encoding="utf-8")


def write_loader_digest(value, path=LOADER):
    text = Path(path).read_text(encoding="utf-8")
    updated, count = re.subn(
        r'(BUNDLE_SHA256 = ")[0-9a-f]{64}(")',
        rf"\g<1>{value}\g<2>",
        text,
    )
    if count != 1:
        raise SystemExit(f"{path} has no single BUNDLE_SHA256 pin")
    Path(path).write_text(updated, encoding="utf-8")


def main(argv):
    payload = build_payload()
    value = digest(payload)
    if "--check" in argv:
        bundle = BUNDLE.read_text(encoding="utf-8").strip()
        pinned = loader_digest()
        if bundle != payload:
            print("bundle is stale; run python3 skill/install/build_bundle.py")
            return 1
        if pinned != value:
            print("loader hash is stale; run python3 skill/install/build_bundle.py")
            return 1
        print(f"bundle and loader hash are current: {value}")
        return 0
    write_bundle(payload)
    write_loader_digest(value)
    print(f"wrote {BUNDLE} ({len(payload)} chars)")
    print(f"sha256 {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
