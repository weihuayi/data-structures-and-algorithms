#!/usr/bin/env python3
"""Select regression targets from local dependencies and a git comparison."""
import argparse
import json
from pathlib import Path
import subprocess

from build import ROOT, DECKS, EXAMPLES, load_deck, render_document
from dependencies import dependency_manifest

VALIDATION = {'tools/deck/check.py', 'tools/deck/check-browser.cjs',
              'tools/deck/dependencies.py', 'tools/deck/impact.py', 'tools/deck/verify.py',
              'tools/deck/legacy_baseline.py', 'tools/deck/legacy.json'}
POLICY = {'AGENTS.md', 'docs/design/deck-contract.md'}


def git_changes(base, root=ROOT):
    # Arguments are passed directly, never interpolated into a shell command.
    subprocess.run(['git', 'rev-parse', '--verify', base + '^{commit}'], cwd=root,
                   check=True, capture_output=True)
    tracked = subprocess.check_output(['git', 'diff', '--name-only', '-z', base, '--'], cwd=root)
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=root)
    return sorted(set(x.decode() for x in (tracked + new).split(b'\0') if x))


def analyze(changed, *, all_decks=False):
    changed = set(changed)
    legacy = json.loads(Path(__file__).with_name('legacy.json').read_text())['legacy']
    full, defaults, reasons, covered = [], [], {}, set()
    for deck in sorted(p for p in DECKS.iterdir() if (p / 'slides.py').is_file()):
        key = deck.name.split('-', 1)[0].upper()
        prefix = deck.relative_to(ROOT).as_posix() + '/'
        why = []
        try:
            mod = load_deck(deck)
            adopted = getattr(mod, 'COURSE', None) is not None or mod.DECK_ID not in legacy
            doc, _ = render_document(deck)
            manifest = dependency_manifest(deck, document=doc, extra=getattr(mod, 'DEPENDENCIES', ()))
            intersection = changed & (set(manifest['files']) | set(manifest['missing']))
            covered |= intersection
            why += sorted(intersection)
            if adopted:
                why += sorted(changed & POLICY)
        except Exception as error:
            # A broken dependency must expand coverage, never silently remove it.
            adopted = True
            why.append('Dependency inspection failed: ' + str(error))
        why += sorted(p for p in changed if p.startswith(prefix))
        why += sorted(changed & VALIDATION)
        if all_decks:
            why.append('Requested all lessons')
        if why:
            (full if adopted else defaults).append(key)
            reasons[key] = sorted(set(why))
    unknown_shared = [p for p in changed - covered if p.startswith('tools/deck/')
                      and '/' not in p[len('tools/deck/'):]
                      and Path(p).suffix in {'.py', '.css', '.js', '.cjs'}
                      and p not in VALIDATION]
    if unknown_shared:
        for deck in sorted(p for p in DECKS.iterdir() if (p / 'slides.py').is_file()):
            key = deck.name.split('-', 1)[0].upper()
            if key not in full and key not in defaults:
                try:
                    adopted = getattr(load_deck(deck), 'COURSE', None) is not None
                except Exception:
                    adopted = True
                (full if adopted else defaults).append(key)
            reasons.setdefault(key, []).extend('Unresolved shared impact: ' + p for p in unknown_shared)
    return dict(changed=sorted(changed), full=sorted(full), defaults=sorted(defaults),
                examples=sorted(p.name for p in EXAMPLES.iterdir() if (p / 'slides.py').is_file()),
                reasons=reasons,
                limits=['Legacy defaults exclude interaction, reading and print verification.',
                        'Dynamic dependencies must be declared; unresolved shared changes expand scope.',
                        'Teaching content and default-visible answers require manual review.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--all', action='store_true', dest='all_decks')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = analyze(git_changes(args.base), all_decks=args.all_decks)
    result['base'] = args.base
    data = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(data, encoding='utf-8')
    print(data, end='')


if __name__ == '__main__':
    main()
