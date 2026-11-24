"""Focused D020 source and pedagogy-contract checks, not a learning-effect test."""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools" / "deck"))
from components import contract_checks

EXPECTED = [
    "cover", "outline", "part-selection", "sort-contract-recall",
    "simple-selection", "tournament-bridge", "heap-opportunity",
    "heap-contract", "heap-array", "heap-vs-bst", "sift-down",
    "sift-counterexample", "build-heap", "heap-independent",
    "heapsort-boundary", "heap-checkpoint", "part-merge",
    "merge-opportunity", "merge-trace", "stable-merge-independent",
    "merge-invariant", "merge-recursion", "merge-cost", "part-radix",
    "radix-opportunity", "radix-buckets", "radix-linked-trace",
    "radix-independent", "radix-stability", "part-choice",
    "comparison-model", "choice-independent", "mechanism-synthesis",
    "homework-bridge",
]


def load():
    spec = importlib.util.spec_from_file_location("d020_deck", HERE / "slides.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class D020DeckChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()
        cls.pages = {p["id"]: (p, cls.mod.SLIDES[i])
                     for i, p in enumerate(cls.mod.COURSE.pages)}

    def test_course_deck_declared_sections(self):
        self.assertEqual(self.mod.DECK_ID, "D020")
        self.assertEqual([s.id for s in self.mod.COURSE.sections],
                         ["selection", "merge", "radix", "choice"])
        self.assertEqual(self.mod.PAGE_IDS, EXPECTED)
        self.assertEqual(len(self.mod.SLIDES), 34)
        failures = [c for c in contract_checks(self.mod.COURSE, self.mod.SLIDES)
                    if c["status"] != "pass"]
        self.assertFalse(failures, failures)

    def test_storyboard_page_ids_match(self):
        board = (HERE / "storyboard.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| `([a-z0-9_-]+)` ／ S[0-7] \| \d+ \|", board, re.M)
        self.assertEqual(rows, EXPECTED)
        self.assertEqual(rows.count("part-selection"), 1)
        self.assertEqual(rows.count("part-radix"), 1)

    def test_all_key_tasks_have_separate_input_prompt_and_answer(self):
        for pid in ("sort-contract-recall", "tournament-bridge",
                    "sift-counterexample", "heap-independent",
                    "heapsort-boundary", "heap-checkpoint",
                    "stable-merge-independent", "merge-recursion",
                    "radix-independent", "comparison-model", "choice-independent"):
            page, slide = self.pages[pid]
            with self.subTest(pid=pid):
                self.assertEqual(page["role"], "exercise")
                body = slide[1]
                self.assertIn('data-course-component="task-workspace"', body)
                self.assertIn("data-task-input", body)
                self.assertIn("data-task-prompt", body)
                self.assertIn("data-task-answer", body)
                self.assertIn("<summary>", body)

    def test_qa_learning_evidence_present(self):
        criteria = {
            "tournament-bridge": ["E1a", "胜者路径"],
            "heapsort-boundary": ["E1b", "heapSize"],
            "merge-recursion": ["E2", "递归排序"],
            "comparison-model": ["E3", "模型"],
            "heap-independent": ["P1", "下沉"],
            "stable-merge-independent": ["P2", "甲"],
            "radix-independent": ["P3", "桶"],
            "choice-independent": ["P4", "约束"],
        }
        for pid, terms in criteria.items():
            body = self.pages[pid][1][1]
            for term in terms:
                with self.subTest(pid=pid,term=term):
                    self.assertIn(term, body)

    def test_examples_and_notation(self):
        self.assertIn("siftDown", self.pages["sift-counterexample"][1][1])
        self.assertIn("head/tail/next", self.pages["radix-linked-trace"][1][1])
        self.assertIn("LSD", self.pages["radix-stability"][1][1])
        self.assertIn("heapSize", self.pages["heapsort-boundary"][1][1])
        self.assertIn("关键字", self.pages["sort-contract-recall"][1][1])
        self.assertIn("lesson.css", self.pages["cover"][1][1])
        self.assertIn("prototypes/trace.js", self.pages["cover"][1][1])
        self.assertIn("lesson.js", self.pages["cover"][1][1])

    def test_official_homework_is_only_closing_page(self):
        page, slide = self.pages["homework-bridge"]
        self.assertEqual(page["role"], "closing")
        self.assertIn("教材作业（必做）", slide[1])
        self.assertIn("C11 程序实践（必做）", slide[1])
        self.assertIn("code/sorting_d020_demo.c", slide[1])
        self.assertIn("个人电脑", slide[1])
        self.assertIn("选做不提交", slide[1])


if __name__ == "__main__":
    unittest.main()
