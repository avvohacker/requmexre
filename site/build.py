#!/usr/bin/env python3
"""Build the requmexre GitHub Pages site.

Renders README.md and schema/RULES.md into one static page at site/_out/index.html
and publishes the JSON Schema at the path its `$id` names.
Relative links to repository files are rewritten: RULES.md becomes the on-page
#rules section, everything else points at the file on GitHub.

    python3 site/build.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from string import Template

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
OUT = SITE / "_out"
REPO_URL = "https://github.com/avvohacker/requmexre"
BLOB_URL = f"{REPO_URL}/blob/main"
SITE_URL = "https://avvohacker.github.io/requmexre/"
SCHEMA_PATH = ROOT / "schema" / "requmexre.schema.json"

try:
    import markdown
except ImportError:  # pragma: no cover - reported, not raised
    sys.exit("markdown is not installed. Run: python3 -m pip install markdown==3.7")

CSS = """
:root {
  color-scheme: light dark;
  --paper: #fcfbf7;
  --ink: #1b1a17;
  --muted: #625f57;
  --rule: #e2ded3;
  --accent: #8a3b12;
  --code: #f2efe7;
  --head: #f5f2ea;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #15140f;
    --ink: #e8e4d9;
    --muted: #a39e91;
    --rule: #35322a;
    --accent: #e5a06b;
    --code: #201e18;
    --head: #1d1b15;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font: 17px/1.65 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  text-rendering: optimizeLegibility;
}
.wrap { max-width: 46rem; margin: 0 auto; padding: 0 1.25rem; }
.bar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--paper);
  border-bottom: 1px solid var(--rule);
}
.bar .wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 3.25rem;
}
.wordmark {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  font-size: 1.05rem;
  letter-spacing: 0.01em;
  color: var(--ink);
  text-decoration: none;
}
nav { display: flex; gap: 1.1rem; font-size: 0.85rem; }
nav a { color: var(--muted); text-decoration: none; }
nav a:hover, nav a:focus-visible { color: var(--ink); }
main { padding-top: 2.2rem; padding-bottom: 4rem; }
section { scroll-margin-top: 4rem; }
h1, h2, h3, h4 {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: -0.005em;
}
h1 { font-size: 2.3rem; margin: 0 0 1rem; }
h2 { font-size: 1.45rem; margin: 2.8rem 0 0.9rem; padding-top: 1.6rem; border-top: 1px solid var(--rule); }
h3 { font-size: 1.15rem; margin: 2rem 0 0.6rem; }
p { margin: 0 0 1.1rem; }
a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
a:hover { text-decoration-thickness: 2px; }
ul, ol { padding-left: 1.3rem; margin: 0 0 1.2rem; }
li { margin: 0.25rem 0; }
li > p { margin-bottom: 0.4rem; }
code {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 0.88em;
  background: var(--code);
  padding: 0.12em 0.35em;
  border-radius: 4px;
}
pre {
  background: var(--code);
  border: 1px solid var(--rule);
  border-radius: 8px;
  padding: 1rem 1.1rem;
  overflow-x: auto;
  line-height: 1.5;
  margin: 0 0 1.4rem;
}
pre code { background: none; padding: 0; font-size: 0.85rem; }
blockquote {
  margin: 1.6rem 0;
  padding: 0.1rem 0 0.1rem 1.1rem;
  border-left: 3px solid var(--accent);
  color: var(--muted);
}
blockquote p:last-child { margin-bottom: 0; }
table { width: 100%; border-collapse: collapse; margin: 0 0 1.6rem; font-size: 0.92rem; }
th, td { text-align: left; padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { background: var(--head); font-weight: 600; }
thead th { border-bottom: 2px solid var(--rule); }
#readme > p:first-of-type { font-size: 1.1rem; color: var(--muted); }
main > section + section { margin-top: 4rem; padding-top: 2.5rem; border-top: 2px solid var(--rule); }
footer { border-top: 1px solid var(--rule); padding: 1.6rem 0 2.4rem; color: var(--muted); font-size: 0.85rem; }
footer p { margin: 0 0 0.3rem; }
@media (max-width: 34rem) {
  body { font-size: 16px; }
  h1 { font-size: 1.9rem; }
  .bar .wrap { flex-wrap: wrap; padding-top: 0.55rem; padding-bottom: 0.55rem; }
  nav { gap: 0.8rem; }
  table { font-size: 0.82rem; }
  th, td { padding: 0.4rem 0.45rem; }
}
"""

PAGE = Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>requmexre — research question, methodology, expected results</title>
<meta name="description" content="requmexre: a machine-readable model of a research plan as research question, methodology and expected results. JSON Schema, two-layer validator and funder mappings.">
<meta name="theme-color" content="#fcfbf7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#15140f" media="(prefers-color-scheme: dark)">
<style>$css</style>
</head>
<body>
<header class="bar">
  <div class="wrap">
    <a class="wordmark" href="#readme">requmexre</a>
    <nav aria-label="Sections">
      <a href="#readme">README</a>
      <a href="#rules">Rules</a>
      <a href="#sources">Sources</a>
      <a href="$repo">GitHub</a>
    </nav>
  </div>
</header>
<main class="wrap">
  <section id="readme" aria-label="README">
$readme
  </section>
  <section id="rules" aria-label="Rules">
$rules
  </section>
  <section id="sources" aria-label="Sources">
$sources
  </section>
</main>
<footer>
  <div class="wrap">
    <p>requmexre v1.0 · 2026 · Licence: all rights reserved</p>
    <p>Built from <code>README.md</code>, <code>schema/RULES.md</code> and <code>SOURCES.md</code> by <code>site/build.py</code>.</p>
  </div>
</footer>
</body>
</html>
""")

LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def rewrite_links(text: str) -> str:
    """Send relative Markdown links to the on-page section or to GitHub."""

    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        path, _, anchor = target.partition("#")
        if path.endswith("RULES.md"):
            return f"[{label}](#rules)"
        if path == "SOURCES.md":
            return f"[{label}](#sources)"
        if path == "README.md":
            return f"[{label}](#readme)"
        suffix = f"#{anchor}" if anchor else ""
        return f"[{label}]({BLOB_URL}/{path}{suffix})"

    return LINK.sub(replace, text)


def render(text: str) -> str:
    return markdown.markdown(
        rewrite_links(text),
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )


def main() -> int:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rules = (ROOT / "schema" / "RULES.md").read_text(encoding="utf-8")
    sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    page = PAGE.substitute(
        css=CSS,
        readme=render(readme),
        rules=render(rules),
        sources=render(sources),
        repo=REPO_URL,
        blob=BLOB_URL,
    )
    target = OUT / "index.html"
    target.write_text(page, encoding="utf-8")
    print(f"wrote {target} ({len(page):,} bytes)")

    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    schema_id = json.loads(schema_text)["$id"]
    if not schema_id.startswith(SITE_URL):
        sys.exit(f"schema $id {schema_id} does not start with {SITE_URL}")
    schema_target = OUT / schema_id[len(SITE_URL):]
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    schema_target.write_text(schema_text, encoding="utf-8")
    print(f"wrote {schema_target} ({len(schema_text):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
