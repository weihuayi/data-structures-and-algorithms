#!/usr/bin/env python3
"""Keep raw legacy failures; distinguish identical baseline layout findings.

Only unchanged default-page DOM with exactly matching layout failures can be
classified as existing. Missing resources, font failures, incomplete checks and
new/changed layout failures remain blocking. No report is edited in place.
"""
import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

from build import ROOT


def finding_key(check):
    return tuple(check.get(k) for k in ('deck', 'viewport', 'page', 'title', 'state', 'check'))


def compare(current, baseline):
    old = {finding_key(c): c for c in baseline['checks'] if c['status'] == 'fail'}
    existing, regressions = [], []
    for c in current['checks']:
        if c['status'] == 'pass':
            continue
        prior = old.get(finding_key(c))
        unchanged = (c['status'] == 'fail' and c['check'] == 'projection-layout' and prior
                     and c.get('pageFingerprint') and c['pageFingerprint'] == prior.get('pageFingerprint')
                     and c['detail'] == prior['detail'])
        (existing if unchanged else regressions).append(c)
    return dict(status='regressions' if regressions else 'existing-findings' if existing else 'pass',
                existing=existing, regressions=regressions,
                limits=['Raw current and baseline reports remain unchanged and may both contain failures.',
                        'Comparison covers default-page layout only, not local overlap or legacy interactions.',
                        'Changed page HTML, new/increased overflow and non-layout failures are not accepted as existing.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--current', required=True, type=Path, help='Current default-pages browser-report.json')
    parser.add_argument('--output', required=True, type=Path, help='New comparison directory')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    try:
        sha = subprocess.check_output(['git', 'rev-parse', '--verify', args.base + '^{commit}'], cwd=ROOT, text=True).strip()
        current = json.loads(args.current.read_text())
        if current.get('scope') != 'default-pages':
            raise ValueError('Only default-pages evidence can be compared here')
        with tempfile.TemporaryDirectory(prefix='course-baseline-') as folder:
            root = Path(folder)
            archive = subprocess.check_output(['git', 'archive', '--format=tar', sha], cwd=ROOT)
            with tarfile.open(fileobj=io.BytesIO(archive)) as data:
                data.extractall(root, filter='data')
            names = sorted({c['deck'] for c in current['checks']})
            decks = [dict(id=name, url=(root / 'course/decks' / name / 'index.html').as_uri()) for name in names]
            config = dict(decks=decks, viewports=[[1280,720],[1440,900]], scope='default-pages',
                          output=str(args.output.resolve()), screenshots='failures',
                          playwrightModule=os.environ.get('DECK_PLAYWRIGHT_MODULE') or 'playwright',
                          executablePath=os.environ.get('DECK_BROWSER_EXECUTABLE'))
            config_path = args.output / 'browser-input.json'
            config_path.write_text(json.dumps(config))
            result = subprocess.run([os.environ.get('DECK_NODE') or 'node', str(Path(__file__).with_name('check-browser.cjs')),
                                     str(config_path.resolve())], capture_output=True, text=True)
            (args.output / 'browser.log').write_text(result.stdout + result.stderr)
            if result.returncode not in (0,1) or not (args.output/'browser-report.json').exists():
                raise RuntimeError('Baseline browser check is incomplete; inspect browser.log')
            baseline = json.loads((args.output/'browser-report.json').read_text())
            if any(c['status'] != 'pass' and c['check'] != 'projection-layout' for c in baseline['checks']):
                raise ValueError('Baseline has non-layout failures; comparison is not usable')
            if baseline.get('browserVersion') != current.get('browserVersion') or baseline.get('node') != current.get('node'):
                raise ValueError('Current and baseline must use the same browser and Node versions')
            report = compare(current, baseline)
            report.update(baseSha=sha, currentReport=str(args.current.resolve()),
                          baselineReport=str((args.output/'browser-report.json').resolve()))
        code = 1 if report['regressions'] else 0
    except (OSError, ValueError, subprocess.CalledProcessError, RuntimeError) as error:
        report, code = dict(status='incomplete', error=str(error)), 2
    (args.output/'comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f"{report['status']}: {args.output/'comparison.json'}")
    return code


if __name__ == '__main__':
    raise SystemExit(main())
