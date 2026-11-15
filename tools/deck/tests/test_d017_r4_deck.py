"""R4 D017: 37-page teaching implementation and executable evidence.

Technical checks complement, but do not replace, teachers' slide review.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

DECK_TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DECK_TOOL))
from build import DECKS, load_deck
from cognitive_checks import prediction_checks, storyboard_checks

DECK = DECKS / "d017-bst-avl"
EXPECTED = (
    "cover outline part-bridge recall-sorted update-array "
    "part-bst bst-node-links bst-order bst-search bst-insert bst-check bst-transfer "
    "bst-delete-cases bst-delete-two part-height build-shape-balanced build-shape-chain "
    "compare-path worst-shape need-balance part-avl height-observe avl-definition "
    "bf-calculate bf-every-node ll-trigger right-rotate rotation-order lr-single-fails "
    "lr-double-stage1 lr-double mirror-cases independent-avl part-choice structure-choice "
    "synthesis homework"
).split()


class D017R4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck = load_deck(DECK)
        cls.pages = cls.deck.COURSE.pages
        cls.by_id = dict(zip([p["id"] for p in cls.pages], cls.deck.SLIDES))

    def test_exact_37_page_storyboard_registration(self):
        self.assertEqual([p["id"] for p in self.pages], EXPECTED)
        self.assertEqual(len(self.pages), 37)
        self.assertEqual([c["status"] for c in storyboard_checks(DECK, self.deck.COURSE)],
                         ["pass", "pass"])
        self.assertNotIn("two-builds", self.by_id)
        self.assertNotIn("c-bridge", self.by_id)

    def test_core_pretraining_and_visual_inputs(self):
        self.assertNotIn("BST", self.by_id["cover"][0] + self.by_id["cover"][1])
        self.assertNotIn("AVL", self.by_id["cover"][0] + self.by_id["cover"][1])
        for page in ("bst-check", "bst-delete-two", "independent-avl",
                     "bst-transfer", "bf-every-node"):
            title, body, _ = self.by_id[page]
            self.assertIn('data-course-component="task-workspace"', body, page)
            self.assertIn("data-task-input", body, page)
            self.assertIn("data-task-prompt", body, page)
            self.assertIn("data-task-answer", body, page)
            self.assertIn('<svg class="d17-tree"', body, page)
        self.assertIn("Binary Search Tree", self.by_id["bst-order"][1])
        self.assertIn("Adelson-Velsky", self.by_id["avl-definition"][1])
        self.assertIn("Balance Factor", self.by_id["bf-calculate"][1])
        self.assertIn("left, *right", self.by_id["bst-node-links"][1])
        self.assertIn("Node *middle", self.by_id["rotation-order"][1])

    def test_predicted_results_remain_hidden(self):
        marked = {p["id"] for p in self.pages if p.get("withheld_results")}
        self.assertEqual(marked,
            {"update-array","bst-check","bst-transfer","bst-delete-two",
             "compare-path","bf-every-node","lr-single-fails","independent-avl"})
        checks = prediction_checks(self.deck.COURSE, self.deck.SLIDES)
        self.assertTrue(all(c["status"] == "pass" for c in checks), checks)

    def test_formal_homework_unmodified(self):
        homework = self.by_id["homework"][1]
        for required in ("选择题 (7)(8)", "应用题 (2)", "算法设计题(2)",
                         "code/bst_avl_demo.c", "./d017_demo bst", "./d017_demo avl",
                         "飞书"):
            self.assertIn(required, homework)
        self.assertIn("可选核验", homework)

    def test_r4_c11_transfer_case(self):
        cc = shutil.which("gcc") or shutil.which("cc")
        if not cc:
            self.skipTest("C11 compiler not installed")
        code = DECK / "code/bst_avl_demo.c"
        with tempfile.TemporaryDirectory() as folder:
            exe = str(Path(folder) / "d017_demo")
            compile_result = subprocess.run(
                [cc, "-std=c11", "-Wall", "-Wextra", "-Werror", str(code), "-o", exe],
                text=True, capture_output=True, timeout=45)
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            for mode, marker in (("bst", "BST_A height=3"),
                                 ("avl", "AVL_LR root=20"),
                                 ("avl27", "AVL_27 root=25 height=3 rotations=2"),
                                 ("test", "ALL_TESTS_PASSED")):
                proc = subprocess.run([exe, mode], text=True, capture_output=True, timeout=15)
                self.assertEqual(proc.returncode, 0, mode + ": " + proc.stderr)
                self.assertIn(marker, proc.stdout)


if __name__ == "__main__":
    unittest.main()
