"""Regression checks for the *isolated* R4 teaching-visual prototypes.

Do not mistake the preview for the live 32-page D017 or final 37-page deck.
"""
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
PREVIEW = ROOT / 'course/decks/d017-bst-avl/prototypes/r4-five-page-review.html'
CHECK = PREVIEW.parent / 'check_visual.cjs'
IDS = ('recall-sorted', 'bst-check', 'bst-delete-two',
       'right-rotate', 'independent-avl')


class Sections(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.closed = 0
    def handle_starttag(self, tag, attrs):
        meta = dict(attrs)
        if tag == 'section' and 'slide' in meta.get('class', '').split():
            self.ids.append(meta.get('data-page-id'))
        if tag == 'details' and 'feedback' in meta.get('class', '').split():
            if 'open' not in meta:
                self.closed += 1


class PrototypeTests(unittest.TestCase):
    def test_five_independent_prototypes_with_closed_prediction_answers(self):
        source = PREVIEW.read_text(encoding='utf-8')
        parsed = Sections()
        parsed.feed(source)
        self.assertEqual(parsed.ids, list(IDS))
        self.assertEqual(parsed.closed, 4)
        self.assertIn('数据不断', (ROOT/'course/decks/d017-bst-avl/storyboard.md').read_text(encoding='utf-8'))
        self.assertIn('class="tree"', source)
        self.assertIn('根25', source)  # Answer exists but is not default-visible.
        self.assertNotIn('id="independent-avl" aria-label="原型 5：插入 27 后，根25', source)

    def test_real_browser_at_both_projection_sizes(self):
        if not (ROOT/'tools/deck/node_modules/playwright').exists():
            self.skipTest('Playwright not installed; run npm ci in tools/deck to enable visual check')
        node = 'node'
        with tempfile.TemporaryDirectory() as tmp:
            # CI retains screenshots in its already uploaded verification folder.
            output = (Path('/tmp/course-verification/d017-r4-preview') if os.environ.get('CI')
                      else Path(tmp))
            env = {**os.environ, 'D017_R4_SCREENSHOT_DIR': str(output)}
            proc = subprocess.run([node, str(CHECK)], cwd=ROOT, env=env,
                                  capture_output=True, text=True, timeout=150)
            self.assertEqual(proc.returncode, 0, proc.stdout+'\n'+proc.stderr)
            report=json.loads((output/'review-report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['failures'], [])
            self.assertEqual(len(report['checks']), 18)  # 10 defaults, 8 expanded.
            for id_ in IDS:
                for vp in ('1280x720', '1440x900'):
                    self.assertTrue((output/(id_+'-'+vp+'-default.png')).is_file())
                    if id_ != 'right-rotate':
                        self.assertTrue((output/(id_+'-'+vp+'-answer-bottom.png')).is_file())


if __name__ == '__main__':
    unittest.main()
