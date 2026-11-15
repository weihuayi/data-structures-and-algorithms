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
from review import content_snapshot, evidence_files


def diagnostic_summary(output, records, *, sample_limit=12):
    """Preserve raw run results; add bounded, source-linked failure locations."""
    result = dict(blockingCount=0, historicalCount=0, blocking=[], historical=[], omitted=0)
    for run in records:
        if run['returncode'] == 0:
            continue
        phase = run['name']
        # Stage names are log labels; check.py writes reports under separate folders.
        folder = {'adopted-full': 'full',
                  'legacy-review-context': 'review-context',
                  'legacy-defaults': 'defaults',
                  'legacy-baseline': 'baseline'}.get(phase, phase)
        historical = 'classification' in run
        key = 'historical' if historical else 'blocking'
        count_key = 'historicalCount' if historical else 'blockingCount'
        found = []
        report_file = output / folder / 'report.json'
        if report_file.is_file():
            try:
                report = json.loads(report_file.read_text(encoding='utf-8'))
                found.extend(dict(phase=phase, check=c.get('check'), detail=c.get('detail'),
                                  evidence=f'{folder}/report.json')
                             for c in report.get('contextChecks', ()) if c.get('status') == 'fail')
                for deck in report.get('decks', ()):
                    found.extend(dict(phase=phase, deck=deck.get('deck'), check=c.get('check'),
                                      page=c.get('page'), pageId=c.get('pageId'),
                                      detail=c.get('detail'), evidence=f'{folder}/report.json')
                                 for c in deck.get('checks', ()) if c.get('status') == 'fail')
            except (OSError, ValueError, TypeError) as exc:
                found.append(dict(phase=phase, detail='Unreadable machine report: ' + str(exc),
                                  evidence=f'{folder}/report.json'))
        browser_file = output / folder / 'browser-report.json'
        if browser_file.is_file():
            try:
                browser = json.loads(browser_file.read_text(encoding='utf-8'))
                for c in browser.get('checks', ()):
                    if c.get('status') == 'fail':
                        shot = c.get('screenshot')
                        found.append(dict(phase=phase, deck=c.get('deck'), page=c.get('page'),
                                          pageId=c.get('pageId'), viewport=c.get('viewport'),
                                          state=c.get('state'), check=c.get('check'),
                                          detail=c.get('detail'),
                                          evidence=(folder + '/' + shot) if shot else f'{folder}/browser-report.json'))
            except (OSError, ValueError, TypeError) as exc:
                found.append(dict(phase=phase, detail='Unreadable browser report: ' + str(exc),
                                  evidence=f'{folder}/browser-report.json'))
        if not found:
            found.append(dict(phase=phase, check='phase-result',
                              detail=f'Exit {run["returncode"]}; inspect {phase}.log',
                              evidence=phase + '.log'))
        result[count_key] += len(found)
        available = max(0, sample_limit - len(result[key]))
        result[key].extend(found[:available])
        result['omitted'] += len(found) - available
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='HEAD')
    parser.add_argument('--all', action='store_true', dest='all_decks')
    parser.add_argument('--static-only', action='store_true', help='No browser checks; report this limited scope explicitly')
    parser.add_argument('--output', type=Path, help='A new directory; never overwrite previous evidence')
    parser.add_argument('--screenshots', choices=['failures', 'pages', 'all', 'none'], default='pages',
                        help='Full-scope evidence capture; legacy defaults retain failure screenshots')
    args = parser.parse_args()
    base_sha = subprocess.check_output(['git', 'rev-parse', '--verify', args.base + '^{commit}'], cwd=ROOT, text=True).strip()
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='course-verify-'))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    impact = analyze(git_changes(base_sha), all_decks=args.all_decks)
    (output / 'impact.json').write_text(json.dumps(impact, ensure_ascii=False, indent=2) + '\n')
    records = []
    revision = content_snapshot()

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
    run('homework-contract', [sys.executable, 'tools/deck/check_homework.py'])
    run('semantic', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tools/deck/tests'])
    # Failed static/semantic checks must not be hidden by later browser results.
    legacy_comparison = None
    if not args.static_only and all(r['returncode'] == 0 for r in records):
        node = os.environ.get('DECK_NODE') or 'node'
        run('checker-regression', [node, '--test', 'tools/deck/tests/check_browser.test.cjs'])
        targets = impact['full'] + impact['examples']
        if targets:
            run('adopted-full', check + targets + ['--screenshots', args.screenshots, '--output', str(output / 'full')])
        if impact['review']:
            run('legacy-review-context', check + impact['review'] + ['--review-context-only', '--screenshots', args.screenshots,
                                                                    '--output', str(output / 'review-context')])
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
    changed_during_run = revision['contentSha256'] != content_snapshot()['contentSha256']
    if changed_during_run:
        codes.append(2)
    status = ('fail' if any(code not in (0, 2) for code in codes) else 'incomplete' if 2 in codes
              else 'static-only-pass' if args.static_only else 'scoped-pass-with-legacy-findings' if legacy_comparison else 'scoped-pass')
    diagnostics = diagnostic_summary(output, records)
    report = dict(status=status, createdAt=datetime.now(timezone.utc).isoformat(), base=args.base, baseSha=base_sha,
                  revision=revision, evidenceFiles=evidence_files(output),
                  deliveryStatus='pending-review', contentChangedDuringRun=changed_during_run,
                  legacyComparison=legacy_comparison,
                  scope=impact, runs=records, diagnostics=diagnostics,
                  aiReview='Not inferred. Use review.py init/check after explicit content and visual self-review.',
                  limits=['scoped-pass is not full interaction verification of every legacy lesson.',
                          'No new AI session or classroom learning effects were tested by this command.'])
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for label in ('blocking', 'historical'):
        count = diagnostics['blockingCount' if label == 'blocking' else 'historicalCount']
        if count:
            print(f'{label}: {count} finding(s); report has up to 12 locations', flush=True)
            for issue in diagnostics[label][:5]:
                location = ' '.join(str(issue[x]) for x in ('deck', 'pageId', 'viewport')
                                    if issue.get(x) is not None)
                print(f'  {issue["phase"]} {location} {issue.get("check", "")}: '
                      f'{issue.get("detail", "")}; {issue["evidence"]}', flush=True)
    print(f'{status}: {output / "verification.json"}')
    return 1 if status == 'fail' else 2 if status == 'incomplete' else 0


if __name__ == '__main__':
    raise SystemExit(main())
