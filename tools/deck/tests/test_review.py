"""A machine pass alone, stale content and unresolved blockers cannot close work."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review import DIMENSIONS, content_snapshot, evidence_files, new_review, review_checks, sha256


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/'repo'; self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.source = self.root/'course/decks/test/slides.py'
        self.source.parent.mkdir(parents=True); self.source.write_text('SLIDES=[]\n')
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                        'commit', '-qm', 'fixture'], cwd=self.root, check=True)
        folder = Path(self.temp.name)/'evidence'; folder.mkdir()
        (folder/'browser.log').write_text('scoped browser evidence\n')
        self.report = dict(status='scoped-pass', revision=content_snapshot(self.root),
                           scope=dict(full=['D001'], examples=['patterns'], defaults=[]),
                           evidenceFiles=evidence_files(folder))
        self.path = folder/'verification.json'; self.write_report()
        self.record = new_review(self.path)
        self.record['reviewer']['identity'] = 'AI fixture'
        for entry in self.record['dimensions'].values():
            entry.update(status='reviewed', notes='Concrete content judgment', evidence=['browser.log'])
        for entry in self.record['targets'].values():
            entry.update(status='reviewed', pages=['task'], states=['initial, expanded'], evidence=['browser.log'])

    def tearDown(self):
        self.temp.cleanup()

    def write_report(self):
        self.path.write_text(json.dumps(self.report))

    def failures(self, record=None):
        return {c['check'] for c in review_checks(record or self.record, self.report, self.path, root=self.root)
                if c['status'] == 'fail'}

    def test_valid_explicit_review_and_pending_template(self):
        self.assertEqual(self.failures(), set())
        pending = new_review(self.path)
        self.assertIn('review-attribution', self.failures(pending))
        self.assertTrue(any(x.startswith('review-dimension/') for x in self.failures(pending)))
        self.assertIn('review-target/D001', self.failures(pending))

    def test_missing_dimension_target_and_evidence_fail(self):
        for mutation, expected in [
            (lambda r:r['dimensions'].pop(DIMENSIONS[0]), 'review-dimensions'),
            (lambda r:r['targets'].pop('D001'), 'review-targets'),
            (lambda r:r['dimensions']['goals'].update(evidence=['missing.png']), 'review-dimension/goals')]:
            record = copy.deepcopy(self.record); mutation(record)
            self.assertIn(expected, self.failures(record))

    def test_targeted_legacy_review_cannot_be_omitted(self):
        self.report['scope']['review'] = ['D013']; self.write_report()
        record = new_review(self.path)
        self.assertEqual(set(record['targets']), {'D001','patterns','D013'})
        self.record['verificationSha256'] = sha256(self.path)
        self.assertIn('review-targets', self.failures())
        self.record['targets']['D013'] = dict(status='reviewed',pages=['13'],states=['expanded'],evidence=['browser.log'])
        self.assertEqual(self.failures(),set())

    def test_null_judgments_or_omitted_findings_are_not_completed_reviews(self):
        record = copy.deepcopy(self.record)
        record['dimensions']['goals']['notes'] = None
        self.assertIn('review-dimension/goals', self.failures(record))
        record = copy.deepcopy(self.record); record.pop('findings')
        self.assertIn('review-findings', self.failures(record))

    def test_source_rules_untracked_and_deleted_files_change_revision(self):
        original = content_snapshot(self.root)['contentSha256']
        self.source.write_text('SLIDES=[1]\n')
        self.assertIn('review-freshness', self.failures())
        self.source.write_text('SLIDES=[]\n')
        self.assertEqual(original, content_snapshot(self.root)['contentSha256'])
        rules = self.root/'course/AGENTS.md'; rules.write_text('New scope\n')
        self.assertIn('review-freshness', self.failures())
        rules.unlink(); self.source.unlink()
        self.assertIn('review-freshness', self.failures())

    def test_machine_report_and_artifact_mutation_fail(self):
        self.path.write_text(self.path.read_text()+'\n')
        self.assertIn('machine-binding', self.failures())
        (self.path.parent/'browser.log').unlink()
        self.assertIn('machine-evidence', self.failures())

    def test_static_failed_and_incomplete_runs_cannot_close_delivery(self):
        for status in ['static-only-pass', 'incomplete', 'fail']:
            self.report['status'] = status; self.write_report()
            self.record['verificationSha256'] = sha256(self.path)
            self.assertIn('machine-scope', self.failures())

    def test_unresolved_blocker_requires_disposition_and_recheck(self):
        finding = dict(severity='blocking', status='open', location='D001/task',
                       description='Wrong answer', disposition='Will fix', evidence=['browser.log'])
        self.record['findings'] = [finding]
        self.assertIn('review-finding/1', self.failures())
        finding.update(status='resolved', disposition='Fixed and rechecked')
        self.assertEqual(self.failures(), set())
        finding['evidence'] = []
        self.assertIn('review-finding/1', self.failures())

    def test_commit_metadata_alone_does_not_invalidate_content_binding(self):
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                        'commit', '--allow-empty', '-qm', 'metadata only'], cwd=self.root, check=True)
        self.assertEqual(self.failures(), set())


if __name__ == '__main__':
    unittest.main()
