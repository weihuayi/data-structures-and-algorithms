"""R6 D018: cognitive states, reviewed prototype integration and C11 CLI regression.

These checks prove declared artifacts and executions, not classroom learning.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from build import DECKS, load_deck
from cognitive_checks import storyboard_checks
from check_homework import check_page

DECK = DECKS / "d018-hashing"
IDS = (
    "cover outline part-bridge recall-avl access-vs-lookup part-mapping "
    "direct-space hash-map detect-collision part-collision chaining chain-lookup "
    "linear-probe linear-probe-complete mechanism-compare part-correctness "
    "probe-find probe-delete probe-delete-tombstone probe-miss invariant "
    "reuse-and-duplicate part-cost cost-units cost-asl cost-asl-fail same-load "
    "quadratic-note expected-cost part-choice choice-task code-bridge summary homework"
).split()


class D018R6DeckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_deck(DECK)
        cls.pages = cls.module.COURSE.pages
        cls.by_id = dict(zip([p["id"] for p in cls.pages], cls.module.SLIDES))

    def test_page_identity_and_storyboard(self):
        self.assertEqual([p["id"] for p in self.pages], IDS)
        self.assertEqual(len(self.pages), 34)
        self.assertEqual([c["status"] for c in storyboard_checks(DECK, self.module.COURSE)],
                         ["pass", "pass"])
        self.assertEqual(self.pages[-1]["role"], "closing")

    def test_five_reviewed_prototypes_were_integrated_into_formal_pages(self):
        roles = {
            "chaining": "hash-v2-chainsvg",
            "chain-lookup": "hash-v2-chainsvg",
            "linear-probe": "hash-v2-slots",
            "linear-probe-complete": "hash-v2-slots",
            "probe-delete": 'data-scene="not-this-marker"',
            "probe-delete-tombstone": "DELETED",
            "cost-asl-fail": "17/7",
        }
        for page, marker in roles.items():
            body = self.by_id[page][1]
            if page != "probe-delete":
                self.assertIn(marker, body, page)
            self.assertIn('data-course-component="task-workspace"', body, page)
            self.assertIn("data-task-input", body, page)
            self.assertIn("data-task-answer", body, page)
        self.assertIn("W", self.by_id["probe-delete"][1])
        self.assertIn("恢复合法状态 A", self.by_id["probe-delete-tombstone"][1])

    def test_state_boundary_and_no_prediction_leakage(self):
        self.assertIn("不能作为后续合法状态", self.by_id["probe-delete"][1])
        self.assertIn("状态 B", self.by_id["probe-delete-tombstone"][1])
        self.assertIn("未删除", self.by_id["cost-asl-fail"][1])
        self.assertIn("查询", self.by_id["cost-asl-fail"][1])
        self.assertIn("DELETED", self.by_id["invariant"][1])
        self.assertIn("EMPTY", self.by_id["invariant"][1])

    def test_formal_homework_and_c11_correspondence(self):
        body = self.by_id["homework"][1]
        self.assertEqual(check_page(DECK, "课后怎样预测、运行和核对？", body), [])
        for arg in ("chain", "scenarios", "demo", "--self-test"):
            self.assertIn(arg, body)
            self.assertIn(arg, self.by_id["code-bridge"][1])


@unittest.skipUnless(shutil.which("gcc"), "GCC needed for C11 execution")
class D018R6C11Tests(unittest.TestCase):
    def test_all_modes_and_debug_build(self):
        source = DECK / "code" / "hash_demo.c"
        with tempfile.TemporaryDirectory(prefix="d018-r6-") as tmp:
            for release_flags in ((), ("-DNDEBUG",)):
                exe = str(Path(tmp) / ("hash-demo-release" if release_flags else "hash-demo"))
                build = subprocess.run(
                    ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                     *release_flags, str(source), "-o", exe],
                    capture_output=True, text=True, timeout=30
                )
                self.assertEqual(build.returncode, 0, build.stderr)
                for mode, expected in (
                    ("--self-test", "D018 self-test: PASS"),
                    ("chain", "bucket[3] head -> 10 -> 17 -> 24 -> NULL"),
                    ("build", "insert(24): check 3 -> 4 -> 5"),
                    ("scenarios", "W: WRONG deletion"),
                    ("demo", "After insertion:")
                ):
                    with self.subTest(release=release_flags, mode=mode):
                        run = subprocess.run([exe, mode], capture_output=True,
                                             text=True, timeout=10)
                        self.assertEqual(run.returncode, 0, run.stderr)
                        self.assertIn(expected, run.stdout)
                unknown = subprocess.run([exe, "not-a-mode"], capture_output=True,
                                         text=True, timeout=10)
                self.assertEqual(unknown.returncode, 2)


if __name__ == "__main__":
    unittest.main()
