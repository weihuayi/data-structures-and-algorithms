#!/usr/bin/env python3
"""One local/CI entry: static all, semantic tests, then scoped browser checks."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from build import ROOT
from impact import analyze, git_changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--all', action='store_true', dest='all_decks')
    parser.add_argument('--static-only', action='store_true', help='No browser checks; report this limited scope explicitly')
    parser.add_argument('--output', type=Path, help='A new directory; never overwrite previous evidence')
    args = parser.parse_args()
    base_sha = subprocess.check_output(['git', 'rev-parse', '--verify', args.base + '^{commit}'], cwd=ROOT, text=True).strip()
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='course-verify-'))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    impact = analyze(git_changes(base_sha), all_decks=args.all_decks)
    (output / 'impact.json').write_text(json.dumps(impact, ensure_ascii=False, indent=2) + '\n')
    records = []

    def run(name, argv):
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
            code, log = result.returncode, result.stdout + result.stderr
        except OSError as error:
            code, log = 2, str(error)
        (output / (name + '.log')).write_text(log, encoding='utf-8')
        records.append(dict(name=name, command=argv, returncode=code))
        print(f'{name}: exit {code}; {output / (name + ".log")}', flush=True)
        return code

    check = [sys.executable, 'tools/deck/check.py']
    run('static', check + ['all', *impact['examples'], '--static-only', '--output', str(output / 'static')])
    run('semantic', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tools/deck/tests'])
    # Failed static/semantic checks must not be hidden by later browser results.
    legacy_comparison = None
    if not args.static_only and all(r['returncode'] == 0 for r in records):
        node = os.environ.get('DECK_NODE') or 'node'
        run('checker-regression', [node, '--test', 'tools/deck/tests/check_browser.test.cjs'])
        targets = impact['full'] + impact['examples']
        if targets:
            run('adopted-full', check + targets + ['--screenshots', 'pages', '--output', str(output / 'full')])
        if impact['defaults']:
            legacy_code = run('legacy-defaults', check + impact['defaults'] + ['--default-pages', '--screenshots', 'failures',
                                                                             '--output', str(output / 'defaults')])
            if legacy_code == 1:
                comparison_code = run('legacy-baseline', [sys.executable, 'tools/deck/legacy_baseline.py',
                    '--base', base_sha, '--current', str(output/'defaults/browser-report.json'),
                    '--output', str(output/'baseline')])
                comparison_file = output/'baseline/comparison.json'
                if comparison_file.exists():
                    legacy_comparison = json.loads(comparison_file.read_text())
                if comparison_code == 0 and legacy_comparison and legacy_comparison['status'] == 'existing-findings':
                    records[-2]['classification'] = 'existing-layout-findings; raw exit code preserved'
    codes = [r['returncode'] for r in records if 'classification' not in r]
    status = ('fail' if any(code not in (0, 2) for code in codes) else 'incomplete' if 2 in codes
              else 'static-only-pass' if args.static_only else 'scoped-pass-with-legacy-findings' if legacy_comparison else 'scoped-pass')
    report = dict(status=status, createdAt=datetime.now(timezone.utc).isoformat(), base=args.base, baseSha=base_sha,
                  legacyComparison=legacy_comparison,
                  scope=impact, runs=records,
                  manualReview='Not inferred. Record pages, operations and findings separately.',
                  limits=['scoped-pass is not full interaction verification of every legacy lesson.',
                          'No new AI session or classroom learning effects were tested by this command.'])
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'{status}: {output / "verification.json"}')
    return 1 if status == 'fail' else 2 if status == 'incomplete' else 0


if __name__ == '__main__':
    raise SystemExit(main())
