"""Discoverable course context; instruction files are validation dependencies."""
from html import unescape
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from build import ROOT

AGENTS_FILES = ('AGENTS.md', 'course/AGENTS.md', 'course/decks/AGENTS.md',
                'tools/deck/AGENTS.md')
CONTEXT_FILES = (*AGENTS_FILES, 'docs/design/deck-contract.md',
                 'docs/design/deck-revision-guide.md', 'tools/deck/README.md')


def context_paths(deck, root=ROOT):
    """Existing ancestor instructions plus the shared tool/normative context.

    Supports additional per-package instructions without requiring them in every
    lesson. Missing mandatory entry files are reported by context_checks.
    """
    root, deck = root.resolve(), deck.resolve()
    paths = {root / p for p in CONTEXT_FILES if (root / p).is_file()}
    if deck.is_relative_to(root):
        paths.update(p / 'AGENTS.md' for p in (deck, *deck.parents)
                     if p.is_relative_to(root) and (p / 'AGENTS.md').is_file())
    return sorted(paths)


def context_checks(root=ROOT):
    checks = []
    for name in CONTEXT_FILES:
        path = root / name
        exists = path.is_file()
        checks.append(dict(check='context-entry/' + name, status='pass' if exists else 'fail',
                           detail='Required current context entry exists'))
        if not exists:
            continue
        for target in re.findall(r'\[[^\]]+\]\(([^\s)]+)\)', path.read_text(encoding='utf-8')):
            url = urlsplit(unescape(target))
            if url.scheme or url.netloc or not url.path:
                continue
            linked = (path.parent / unquote(url.path)).resolve()
            valid = linked.is_relative_to(root.resolve()) and linked.exists()
            checks.append(dict(check='context-link/' + name, status='pass' if valid else 'fail',
                               detail=target))
    return checks
