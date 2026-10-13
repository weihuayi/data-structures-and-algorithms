"""Checker failures must be observable without repairing the input."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
import check


class DeckCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.deck = self.root / 'd999-fixture'
        self.deck.mkdir()
        (self.deck / 'slides.py').write_text("DECK_ID='D999'\nTITLE='Fixture'\nSLIDES=[('Question', '<p>Input</p>', 'Test')]\n")

    def test_render_and_stale_comparison_does_not_write(self):
        doc, count = build.render_document(self.deck)
        self.assertEqual(count, 1)
        self.assertFalse((self.deck / 'index.html').exists())
        build.render(self.deck)
        self.assertEqual((self.deck / 'index.html').read_text(), doc)
        self.assertEqual(check.check_source(self.deck)['checks'][0]['status'], 'pass')
        (self.deck / 'index.html').write_text('stale')
        self.assertEqual(check.check_source(self.deck)['checks'][0]['status'], 'fail')
        self.assertEqual((self.deck / 'index.html').read_text(), 'stale')

    def test_missing_or_invalid_source_reports_failure(self):
        self.assertEqual(check.check_source(self.deck)['checks'][0]['status'], 'fail')
        (self.deck / 'slides.py').write_text('invalid Python !!!')
        self.assertEqual(check.check_source(self.deck)['checks'][0]['status'], 'fail')

    def test_selection_rejects_partial_mistakes(self):
        with patch.object(check, 'DECKS', self.root):
            self.assertEqual(check.select_decks(['D999']), [self.deck])
            with self.assertRaises(ValueError):
                check.select_decks(['D999', 'D998'])

    def test_static_mode_and_missing_runtime_are_distinct(self):
        build.render(self.deck)
        for flags, expected_code, expected_status in [(['--static-only'], 0, 'static-only-pass'), (['--node', str(self.root / 'missing-node')], 2, 'incomplete')]:
            out = self.root / expected_status
            with patch.object(check, 'DECKS', self.root), redirect_stdout(io.StringIO()):
                code = check.main(['D999', '--output', str(out), *flags])
            report = json.loads((out / 'report.json').read_text())
            self.assertEqual(code, expected_code)
            self.assertEqual(report['status'], expected_status)


if __name__ == '__main__':
    unittest.main()
