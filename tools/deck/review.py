#!/usr/bin/env python3
"""Bind an explicit AI review to current content and unchanged machine evidence.

This checks record completeness and freshness, not whether the reviewer made a
sound teaching judgment. It never upgrades the original machine report.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from build import ROOT

DIMENSIONS = ('goals', 'continuity', 'organization', 'representation', 'interaction', 'verification')
READY_MACHINE = {'scoped-pass', 'scoped-pass-with-legacy-findings'}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_snapshot(root=ROOT):
    raw = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root)
    names = sorted({p.decode() for p in raw.split(b'\0') if p})
    names = [p for p in names if p == 'AGENTS.md' or
             p.startswith(('course/', 'tools/deck/', 'docs/design/', '.github/'))]
    files = {p: sha256(root / p) if (root / p).is_file() else None for p in names}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    return dict(contentSha256=digest, head=head, files=files,
                scope='Tracked and nonignored course, deck tools, design docs, CI and root instructions; HEAD is informational')


def evidence_files(folder):
    return {p.relative_to(folder).as_posix(): sha256(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def new_review(verification_path):
    report = json.loads(verification_path.read_text(encoding='utf-8'))
    return dict(schemaVersion=1, createdAt=datetime.now(timezone.utc).isoformat(),
                reviewer=dict(kind='ai-self-review', identity=''),
                verificationSha256=sha256(verification_path),
                contentSha256=report['revision']['contentSha256'],
                dimensions={key: dict(status='pending', notes='', evidence=[]) for key in DIMENSIONS},
                targets={key: dict(status='pending', pages=[], states=[], evidence=[])
                         for key in report['scope']['full'] + report['scope']['examples']},
                findings=[],
                limits=['Completeness and freshness do not prove the AI review is correct.',
                        'Teacher review, classroom use and learning evidence are separate.'])


def review_checks(record, report, verification_path, *, root=ROOT):
    checks = []
    def add(name, ok, detail):
        checks.append(dict(check=name, status='pass' if ok else 'fail', detail=detail))
    bound = report.get('evidenceFiles', {})
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def evidence(value):
        return isinstance(value, list) and bool(value) and all(isinstance(p, str) and p in bound for p in value)
    add('review-schema', record.get('schemaVersion') == 1, 'Supported explicit review schema')
    who = record.get('reviewer', {})
    add('review-attribution', isinstance(who, dict) and who.get('kind') == 'ai-self-review' and
        text(who.get('identity')), 'AI self-review is attributed separately from teacher review')
    add('machine-scope', report.get('status') in READY_MACHINE,
        'A full scoped machine run must finish; static-only, failed or incomplete evidence cannot close delivery')
    add('machine-binding', record.get('verificationSha256') == sha256(verification_path),
        'Review belongs to this unchanged verification report')
    current = content_snapshot(root)['contentSha256']
    add('review-freshness', current == record.get('contentSha256') == report.get('revision', {}).get('contentSha256'),
        'Current content and dependencies match the reviewed, verified content')
    add('machine-evidence', bool(bound) and all(
        (verification_path.parent / p).resolve().is_relative_to(verification_path.parent.resolve()) and
        (verification_path.parent / p).is_file() and sha256(verification_path.parent / p) == digest
        for p, digest in bound.items()), 'Referenced logs, reports and screenshots exist and retain their hashes')
    dimensions = record.get('dimensions', {})
    add('review-dimensions', isinstance(dimensions, dict) and set(dimensions) == set(DIMENSIONS),
        'All six course dimensions are explicitly considered')
    for key in DIMENSIONS:
        entry = dimensions.get(key, {}) if isinstance(dimensions, dict) else {}
        valid = (isinstance(entry, dict) and entry.get('status') in {'reviewed', 'not-applicable'} and
                 text(entry.get('notes')) and evidence(entry.get('evidence')))
        add('review-dimension/' + key, valid, 'Record judgment or applicability reason and bound evidence')
    targets = record.get('targets', {})
    required = set(report.get('scope', {}).get('full', []) + report.get('scope', {}).get('examples', []))
    add('review-targets', isinstance(targets, dict) and set(targets) == required,
        'Review explicitly covers the selected full-scope lessons and examples')
    for key in sorted(required):
        entry = targets.get(key, {}) if isinstance(targets, dict) else {}
        valid = (isinstance(entry, dict) and entry.get('status') == 'reviewed' and
                 isinstance(entry.get('pages'), list) and bool(entry['pages']) and
                 isinstance(entry.get('states'), list) and bool(entry['states']) and
                 all(isinstance(x, str) and x.strip() for x in entry['pages'] + entry['states']) and
                 evidence(entry.get('evidence')))
        add('review-target/' + key, valid, 'Declare reviewed pages, operations and evidence; limits stay explicit')
    findings = record.get('findings')
    add('review-findings', isinstance(findings, list), 'Findings are an explicit list, including an empty list')
    for index, item in enumerate(findings if isinstance(findings, list) else [None], 1):
        valid = (isinstance(item, dict) and item.get('severity') in {'blocking', 'advisory', 'legacy'} and
                 item.get('status') in {'resolved', 'open'} and text(item.get('location')) and
                 text(item.get('description')) and text(item.get('disposition')) and
                 evidence(item.get('evidence')) and
                 (item['severity'] != 'blocking' or item['status'] == 'resolved'))
        add('review-finding/' + str(index), valid, 'Blocking findings resolved; every finding has disposition and recheck evidence')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'check'])
    parser.add_argument('--verification', required=True, type=Path)
    parser.add_argument('--review', required=True, type=Path, help='Explicit AI self-review JSON, outside the repository')
    parser.add_argument('--output', type=Path, help='Optional new closure-result file')
    args = parser.parse_args()
    try:
        if args.review.resolve().is_relative_to(ROOT):
            raise ValueError('Keep generated evidence and review JSON outside the repository; commit a concise design/review summary instead')
        if args.action == 'init':
            record = new_review(args.verification)
            with args.review.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
            print(f'pending-review: {args.review}')
            return 0
        record = json.loads(args.review.read_text(encoding='utf-8'))
        report = json.loads(args.verification.read_text(encoding='utf-8'))
        checks = review_checks(record, report, args.verification)
        valid = all(c['status'] == 'pass' for c in checks)
        result = dict(status='ready-for-teacher-review' if valid else 'review-incomplete', checks=checks,
                      limits=['This checks the declared review and evidence, not its teaching judgment or learning effects.'])
        if args.output:
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if valid else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(2, f'incomplete: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
