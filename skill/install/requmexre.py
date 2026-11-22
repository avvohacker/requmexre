#!/usr/bin/env python3
"""requmexre — bootstrap installer. Run: python3 scripts/requmexre.py unpack"""
import base64
import bz2
import hashlib
import json
import sys
import tempfile
import types
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUNDLE_URL = "https://raw.githubusercontent.com/avvohacker/requmexre/main/skill/install/requmexre.bundle"
BUNDLE_SHA256 = "7a3a492e82c64ce5a4f5aeda71ee72c3e9da3a1a20428b9c9869eea5593d055e"
_CACHE = None


def bundle_text():
    for candidate in (HERE / "requmexre.bundle", ROOT / "requmexre.bundle"):
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    try:
        with urllib.request.urlopen(BUNDLE_URL, timeout=30) as response:
            return response.read().decode("utf-8")
    except OSError as error:
        raise SystemExit(f"cannot fetch the requmexre bundle: {error}") from error


def package():
    global _CACHE
    if _CACHE is None:
        text = "".join(bundle_text().split())
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != BUNDLE_SHA256:
            raise SystemExit("the requmexre bundle is corrupted or has been replaced; reinstall requmexre")
        _CACHE = json.loads(bz2.decompress(base64.b64decode(text)).decode("utf-8"))
    return _CACHE


def unpack(quiet=False):
    for relative, text in package().items():
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_text(encoding="utf-8") == text:
            continue
        target.write_text(text, encoding="utf-8")
        if not quiet:
            print(f"wrote {target}")


def working_root():
    try:
        unpack(True)
        return ROOT
    except OSError:
        temporary = Path(tempfile.mkdtemp(prefix="requmexre-"))
        for relative, text in package().items():
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        print(f"temporary copy: {temporary}", file=sys.stderr)
        return temporary


def load_module(root, name):
    path = root / "scripts" / f"{name}.py"
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(package()[f"scripts/{name}.py"], str(path), "exec"), module.__dict__)
    return module


COMMANDS = {"validate": "validate", "render": "render", "verify": "verify_citations"}


def main(argv):
    if not argv:
        print("usage: requmexre.py {unpack|validate|render|verify} ...", file=sys.stderr)
        return 2
    command = argv[0]
    if command in ("--version", "version"):
        print("requmexre bundle v1.2")
        return 0
    if command == "unpack":
        unpack()
        print("read SKILL.md before using the skill.")
        return 0
    name = COMMANDS.get(command)
    if name is None:
        print(f"unknown command {command!r}", file=sys.stderr)
        return 2
    root = working_root()
    validate = load_module(root, "validate") if name in ("validate", "render") else None
    return (validate if name == "validate" else load_module(root, name)).main(argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
