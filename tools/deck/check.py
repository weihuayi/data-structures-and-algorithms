#!/usr/bin/env python3
"""Read-only Deck checks; browser coverage is never inferred from a build pass."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

from build import DECKS, EXAMPLES, ROOT, PLAN_START, PLAN_END, load_deck, render_document
from components import contract_checks
from dependencies import dependency_manifest

LEGACY_FILE = Path(__file__).with_name('legacy.json')


def select_decks(names):
    decks = sorted(p for p in DECKS.iterdir() if (p / 'slides.py').is_file())
    if not names:
        return decks
    selected = set()
    for name in names:
        if name.lower() == 'all':
            selected.update(decks)
            continue
        examples = list(EXAMPLES.iterdir()) if EXAMPLES.exists() else []
        matches = [p for p in decks + examples if (p / 'slides.py').is_file() and name.lower() in (p.name.lower(), p.name.split('-', 1)[0].lower())]
        if len(matches) != 1:
            raise ValueError(f'Unknown or ambiguous Deck: {name}')
        selected.add(matches[0])
    return sorted(selected)


def check_source(deck):
    result = {'deck': deck.name, 'checks': [], 'sourceSha256': hashlib.sha256((deck / 'slides.py').read_bytes()).hexdigest()}
    try:
        expected, count = render_document(deck)
        if count <= 0:
            raise ValueError('SLIDES must contain at least one slide')
        current = (deck / 'index.html').read_bytes()
        matches = current == expected.encode('utf-8')
        result.update(slides=count, htmlSha256=hashlib.sha256(current).hexdigest())
        result['checks'].append({'check': 'build-consistency', 'status': 'pass' if matches else 'fail',
                                 'detail': 'index.html matches source' if matches else 'index.html is stale; run tools/deck/build.py for this Deck'})
        mod = load_deck(deck)
        course = getattr(mod, 'COURSE', None)
        legacy = json.loads(LEGACY_FILE.read_text())['legacy']
        repo_deck = deck.is_relative_to(ROOT) and deck.parent == DECKS
        folder_id = deck.name.split('-', 1)[0].upper()
        if repo_deck:
            result['checks'].append({'check': 'deck-identity', 'status': 'pass' if mod.DECK_ID == folder_id else 'fail',
                                     'detail': f'DECK_ID={mod.DECK_ID}; directory identity={folder_id}; update copied source identity'})
        required = repo_deck and folder_id not in legacy
        result['contract'] = {'status': 'required-but-missing' if required and course is None else 'legacy' if course is None else 'adopted',
                              'version': getattr(course, 'version', None)}
        if required:
            result['checks'].append({'check': 'contract-adoption', 'status': 'pass' if course is not None else 'fail',
                                     'detail': 'New/adopted lessons must expose COURSE; only the explicit legacy baseline may defer migration'})
        if course is not None:
            result['checks'].extend(contract_checks(course, mod.SLIDES))
            result['contract']['navigation'] = course.navigation
            result['contract']['navigationReason'] = course.navigation_reason
            result['contract']['pages'] = course.pages
            readme = deck / 'README.md'
            if readme.exists() and (PLAN_START in readme.read_text() or PLAN_END in readme.read_text()):
                text = readme.read_text(encoding='utf-8')
                marked = text.count(PLAN_START) == 1 and text.count(PLAN_END) == 1 and text.index(PLAN_START) < text.index(PLAN_END)
                synced = marked and text.split(PLAN_START)[1].split(PLAN_END)[0].strip() == course.page_plan_markdown()
                result['checks'].append({'check': 'design-card-page-plan', 'status': 'pass' if synced else 'fail',
                                         'detail': 'Regenerate the marked page-plan table with tools/deck/build.py; prose stays manually maintained'})
        result['dependencies'] = dependency_manifest(deck, document=expected,
                                                     extra=getattr(mod, 'DEPENDENCIES', ()))
        if deck.is_relative_to(ROOT):
            valid = not result['dependencies']['missing'] and not result['dependencies']['outside']
            result['checks'].append({'check': 'local-dependencies', 'status': 'pass' if valid else 'fail',
                                     'detail': json.dumps({k: result['dependencies'][k] for k in ('missing', 'outside')})})
    except Exception as exc:
        result['checks'].append({'check': 'source-inspection' if result['checks'] else 'build-consistency',
                                 'status': 'fail', 'detail': f'{type(exc).__name__}: {exc}'})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('decks', nargs='*', help='D008 D009 / directory names / all (default)')
    parser.add_argument('--static-only', action='store_true', help='Only compare generated HTML; explicitly excludes browser checks')
    parser.add_argument('--default-pages', action='store_true', help='Browser checks only initial pages; excludes all interaction coverage')
    parser.add_argument('--output', type=Path, help='New report directory (default: a new temporary directory)')
    parser.add_argument('--node', default=os.environ.get('DECK_NODE') or shutil.which('node'))
    parser.add_argument('--playwright-module', default=os.environ.get('DECK_PLAYWRIGHT_MODULE'), help='Path or module name, default: playwright')
    parser.add_argument('--browser-executable', default=os.environ.get('DECK_BROWSER_EXECUTABLE'), help='Use existing Chrome/Chromium; never auto-install')
    parser.add_argument('--screenshots', choices=['failures', 'pages', 'all', 'none'], default='failures')
    args = parser.parse_args(argv)
    try:
        decks = select_decks(args.decks)
        output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='deck-check-'))
        if args.output:
            output.mkdir(parents=True, exist_ok=False)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.static_only and args.default_pages:
        parser.error('--static-only and --default-pages are different scopes; choose one')
    validators = ['check.py', 'check-browser.cjs', 'components.py', 'dependencies.py', 'legacy.json',
                  'impact.py', 'verify.py', 'legacy_baseline.py', 'package-lock.json']
    report = {'schemaVersion': 2, 'createdAt': datetime.now(timezone.utc).isoformat(),
              'mode': 'static-only' if args.static_only else 'default-pages' if args.default_pages else 'full', 'python': sys.version.split()[0],
              'validationFiles': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in validators},
              'contractSha256': hashlib.sha256((ROOT / 'docs/design/deck-contract.md').read_bytes()).hexdigest(),
              'viewports': [[1280, 720], [1440, 900]], 'decks': [check_source(p) for p in decks],
              'browser': {'status': 'not-requested' if args.static_only else 'pending'},
              'limits': ['No proof of teaching effectiveness or mathematical correctness.',
                         'Only data-tree-player has a step-control adapter; other interactions are reported uncovered.',
                         'Teacher-note expansion may scroll vertically; learner disclosures are checked for viewport overflow.',
                         'Page roles and input markers do not prove pedagogical adequacy or absence of answer leakage.',
                         'Default-pages mode excludes all interaction, reading and print checks.']}
    eligible = [p for p, r in zip(decks, report['decks']) if all(c['status'] == 'pass' for c in r['checks'])]
    if not args.static_only:
        if eligible:
            manifest = {'decks': [{'id': p.name, 'url': (p / 'index.html').as_uri(), 'slides': r['slides']} for p, r in zip(decks, report['decks']) if p in eligible],
                        'viewports': report['viewports'], 'output': str(output), 'screenshots': args.screenshots,
                        'playwrightModule': args.playwright_module or 'playwright', 'executablePath': args.browser_executable,
                        'scope': 'default-pages' if args.default_pages else 'full'}
            manifest_path = output / 'browser-input.json'
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            try:
                if not args.node:
                    raise FileNotFoundError('Node.js not found; use --node or DECK_NODE')
                completed = subprocess.run([args.node, str(Path(__file__).with_name('check-browser.cjs')), str(manifest_path)],
                                           capture_output=True, text=True, timeout=600)
                (output / 'browser.log').write_text(completed.stdout + completed.stderr, encoding='utf-8')
                browser_report = output / 'browser-report.json'
                if not browser_report.is_file() or completed.returncode not in (0, 1, 2):
                    raise RuntimeError(f'Browser checker exited {completed.returncode}; see browser.log')
                report['browser'] = json.loads(browser_report.read_text(encoding='utf-8'))
            except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as exc:
                report['browser'] = {'status': 'unavailable', 'error': str(exc)}
        else:
            report['browser'] = {'status': 'skipped', 'reason': 'No Deck passed build consistency'}
    failed = any(c['status'] == 'fail' for d in report['decks'] for c in d['checks'])
    browser_status = report['browser']['status']
    if failed or browser_status == 'fail':
        report['status'], exit_code = 'fail', 1
    elif not args.static_only and browser_status != 'pass':
        report['status'], exit_code = 'incomplete', 2
    else:
        report['status'], exit_code = ('static-only-pass' if args.static_only else 'default-pages-pass' if args.default_pages else 'pass'), 0
    report_path = output / 'report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{report["status"].upper()}: {len(decks)} Deck(s); report: {report_path}')
    for d in report['decks']:
        for c in d['checks']:
            if c['status'] != 'pass':
                print(f'{d["deck"]} {c["check"]}: {c["detail"]}')
    for c in report['browser'].get('checks', []):
        if c['status'] != 'pass':
            print(f'{c.get("deck", "browser")} page={c.get("page", "-")} '
                  f'viewport={c.get("viewport", "-")} state={c.get("state", "-")} '
                  f'{c["check"]}: {c["detail"]}')
    if 'error' in report['browser']:
        print(report['browser']['error'])
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
