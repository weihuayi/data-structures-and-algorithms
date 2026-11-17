#!/usr/bin/env python3
r"""Opt-in audit of unmarked mathematical notation in Deck prose.

This diagnoses only high-confidence candidates. It does not mutate slides or
infer mathematical correctness. LaTeX already delimited with \(..\) or \[..],
code, SVG, style/script, and menu options are intentionally excluded.

Usage:
  python3 tools/deck/math_audit.py --deck d018-hashing
  python3 tools/deck/math_audit.py --deck d018-hashing --output /tmp/d018-math.json
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from build import DECKS, load_deck

IGNORE_TAGS = frozenset(
    {"code", "pre", "svg", "style", "script", "noscript", "option", "textarea"}
)
MATH_DELIMITERS = ((r"\(", r"\)"), (r"\[", r"\]"))
PATTERNS = (
    ("hash-function", re.compile(r"(?<![\w])(?:h|H)\s*\(\s*(?:k|key|\d+)\s*\)")),
    ("probe-function", re.compile(r"(?<![\w])p\s*\(\s*(?:k|\d+)\s*,\s*(?:i|\d+)\s*\)")),
    ("asymptotic-bound", re.compile(
        r"(?<![\w])(?:O|Ω|Θ)\s*\(\s*(?:1|m|n|log\s*n|n\s*\^\s*\d+|g\(n\))\s*\)"
    )),
    ("numeric-assignment", re.compile(
        r"(?<![\w])(?:ASL|m|n|r|α)\s*=\s*(?:\d+(?:\.\d+)?|[0-9]\/[0-9])"
    )),
)


@dataclass(frozen=True)
class Finding:
    page_id: str
    rule: str
    expression: str
    line: int
    column: int
    context: str


def strip_delimited_math(text: str) -> tuple[str, list[str]]:
    """Keep non-math prose, replacing well-formed math spans by spaces.

    No attempt is made to interpret arbitrary TeX; browser KaTeX checks that.
    """
    output = []
    unmatched = []
    i = 0
    while i < len(text):
        opening = next(((start, end) for start, end in MATH_DELIMITERS
                        if text.startswith(start, i)), None)
        if opening is None:
            output.append(text[i])
            i += 1
            continue
        start, end = opening
        finish = text.find(end, i + len(start))
        if finish < 0:
            unmatched.append(start)
            output.append(" " * (len(text) - i))
            break
        output.append(" " * (finish + len(end) - i))
        i = finish + len(end)
    return "".join(output), unmatched


class _ProseAudit(HTMLParser):
    def __init__(self, page_id: str):
        super().__init__(convert_charrefs=True)
        self.page_id = page_id
        self.tags: list[str] = []
        self.findings: list[Finding] = []

    def handle_starttag(self, tag: str, attrs):
        self.tags.append(tag)

    def handle_startendtag(self, tag: str, attrs):
        # Self-closing elements do not establish an ancestor scope.
        pass

    def handle_endtag(self, tag: str):
        if tag in self.tags:
            last = len(self.tags) - 1 - self.tags[::-1].index(tag)
            del self.tags[last:]

    def handle_data(self, data: str):
        if any(tag in IGNORE_TAGS for tag in self.tags):
            return
        line, column = self.getpos()
        prose, dangling = strip_delimited_math(data)
        for start in dangling:
            self.findings.append(Finding(
                self.page_id, "unclosed-math", start, line, column,
                data[max(0, len(data)-100):]
            ))
        for name, pattern in PATTERNS:
            for match in pattern.finditer(prose):
                begin, end = match.span()
                self.findings.append(Finding(
                    self.page_id, name, match.group(0), line, column + begin,
                    data[max(0, begin-40):min(len(data), end+40)]
                ))


def audit_html(page_id: str, html: str) -> list[Finding]:
    parser = _ProseAudit(page_id)
    parser.feed(html)
    parser.close()
    return parser.findings


def audit_pages(pages: list[dict]) -> list[Finding]:
    return [
        finding
        for page in pages
        for finding in audit_html(page["id"], page.get("body", ""))
    ]


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--deck", default="d018-hashing",
                     help="Deck directory under course/decks, e.g. d018-hashing")
    arg.add_argument("--output", type=Path,
                     help="Optional JSON diagnostic report path")
    args = arg.parse_args()
    folder = DECKS / args.deck
    if not (folder / "slides.py").is_file():
        arg.error(f"No Deck source at {folder}")
    mod = load_deck(folder)
    if not hasattr(mod, "PAGES"):
        arg.error(f"{args.deck} has no PAGES data model; audit requires opt-in")
    results = audit_pages(mod.PAGES)
    report = {
        "deck": args.deck,
        "pages_scanned": len(mod.PAGES),
        "finding_count": len(results),
        "status": "review-candidates" if results else "no-known-patterns",
        "findings": [asdict(x) for x in results],
        "limits": [
            "Detects only known text patterns; no proof of complete LaTeX use.",
            "Excludes code, SVG, styles, options and delimited LaTeX.",
            "Correctness, context and pedagogical suitability require expert review."
        ],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # Candidates are warnings; unclosed known delimiters are definite errors.
    return 1 if any(x.rule == "unclosed-math" for x in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
