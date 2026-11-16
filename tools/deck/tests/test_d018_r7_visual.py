"""D018 R7: bounded visual-alignment trial checks.

Only cover, detect-collision, and chain-lookup are in the R7 trial scope.
These structural checks supplement, not replace, computed browser typography.
"""
import re
import unittest
from pathlib import Path
import sys

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from build import DECKS, load_deck

DECK = DECKS / "d018-hashing"


class D018R7VisualStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod = load_deck(DECK)
        cls.pages = mod.COURSE.pages
        cls.body = dict(zip((p["id"] for p in cls.pages), (s[1] for s in mod.SLIDES)))

    def test_scope_is_three_pages_and_preserves_structure(self):
        self.assertEqual(len(self.pages), 34)
        cover = self.body["cover"]
        self.assertIn("R7 visual alignment trial", cover)
        for ident in ("cover", "detect-collision", "chain-lookup"):
            self.assertIn('data-page-id="' + ident + '"', cover)
        for ident in ("detect-collision", "chain-lookup"):
            self.assertIn('data-course-component="task-workspace"', self.body[ident])
            self.assertIn("data-task-input", self.body[ident])
            self.assertIn("data-task-answer", self.body[ident])
        self.assertIn('hash-r7-mapping', self.body["detect-collision"])
        self.assertIn('hash-r7-chain-page', self.body["chain-lookup"])

    def test_visible_visual_object_has_correct_full_state(self):
        mapping = self.body["detect-collision"]
        self.assertEqual(len(re.findall(r'data-slot="[0-6]"', mapping)), 7)
        self.assertIn('data-state="OCCUPIED"', mapping)
        self.assertIn("独立计算 h(17)", mapping)
        chain = self.body["chain-lookup"]
        self.assertIn("hash-v2-chainsvg", chain)
        self.assertIn('viewBox="0 0 1080 312"', chain)
        self.assertEqual(chain.count('class="hash-r7-bucket-head'), 7)
        self.assertEqual(chain.count('class="hash-r7-chain-node"'), 4)
        for key in ("10", "17", "24", "13"):
            self.assertIn('>' + key + '</text>', chain)
        self.assertIn("NULL", chain)

    def test_projector_typography_explicit_not_downscaled_by_em(self):
        css = self.body["cover"]
        for required in (".hash-r7-cover-lead", ".hash-r7-cover-sequence",
                         ".hash-r7-mapping .course-prompt", ".hash-r7-mapping .hash-v2-state",
                         ".hash-r7-chain-page .course-prompt", ".hash-r7-chain-key",
                         ".hash-r7-chain-next"):
            self.assertIn(required, css)
        self.assertIn("font-size:clamp(24px,1.85vw,29px)", css)
        self.assertIn("font-size:clamp(17px,1.18vw,20px)", css)
        # Fail rather than silently replacing the old program or homework content.
        self.assertIn("code/hash_demo.c", self.body["homework"])
        self.assertIn("DELETED", self.body["probe-delete-tombstone"])


if __name__ == "__main__":
    unittest.main()
