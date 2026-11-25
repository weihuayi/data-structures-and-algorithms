"""R2 automated safeguards for terminology, prerequisites and task scope.

These checks prevent known regressions; they do not measure student learning.
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools" / "deck"))


def load():
    spec = importlib.util.spec_from_file_location("d020_r2_deck", HERE / "slides.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CognitiveContinuityR2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()
        cls.by_id = {
            p["id"]: cls.mod.SLIDES[index][1]
            for index, p in enumerate(cls.mod.COURSE.pages)
        }

    def test_all_34_pages_still_have_unique_goals(self):
        self.assertEqual(len(self.mod.COURSE.pages), 34)
        self.assertEqual(len(self.by_id), 34)
        for p in self.mod.COURSE.pages:
            with self.subTest(page=p["id"]):
                self.assertTrue(p.get("goal"))
        self.assertEqual([s.id for s in self.mod.COURSE.sections],
                         ["selection", "merge", "radix", "choice"])

    def test_terminology_precedes_dependent_reasoning(self):
        milestones = [
            ("heap-contract", "最大堆（max-heap）"),
            ("heap-array", "heapSize"),
            ("sift-down", "向下调整（siftDown）"),
            ("build-heap", "自底向上建堆（buildHeap）"),
            ("merge-opportunity", "有序归并（merge）"),
            ("merge-recursion", "归并排序（merge sort）"),
            ("radix-opportunity", "基数排序（radix sort）"),
            ("radix-opportunity", "最低有效位优先（LSD）"),
            ("radix-linked-trace", "head/tail/next"),
        ]
        for page, term in milestones:
            with self.subTest(page=page, term=term):
                self.assertIn(term, self.by_id[page])
        self.assertIn("从 0 起下标", self.by_id["heap-array"])
        self.assertIn("heapSize 是当前有效堆前缀的长度",
                      self.by_id["heap-array"])

    def test_maximum_selection_continuity_and_heap_preconditions(self):
        for pid in ("simple-selection","tournament-bridge","heap-opportunity","mechanism-synthesis"):
            self.assertIn("最大值", self.by_id[pid])
            self.assertNotIn("最小值", self.by_id[pid])
        self.assertIn(r"\(-\infty\)",self.by_id["tournament-bridge"])
        self.assertIn("从哪些问题理解和选择排序算法？",self.mod.SLIDES[1][0])
        self.assertIn("两个孩子子树原本均为堆", self.by_id["sift-down"])
        self.assertIn('data-heap-state="5,7,8,2,3,1,6"', self.by_id["build-heap"])
        self.assertIn("：[4,6,7,3,1,2,5]", self.by_id["heap-independent"])
        self.assertIn("siftDown", self.by_id["sift-counterexample"])

    def test_exercises_answer_withholding(self):
        for pid in ("tournament-bridge", "heap-independent",
                    "stable-merge-independent", "radix-independent",
                    "comparison-model", "choice-independent"):
            with self.subTest(page=pid):
                html = self.by_id[pid]
                self.assertIn("data-task-input", html)
                self.assertIn("data-task-prompt", html)
                self.assertIn("data-task-answer", html)
                self.assertIn("<details", html)
                self.assertNotIn("<details open", html)
        inp = self.by_id["tournament-bridge"].split("data-task-input", 1)[1]
        inp = inp.split("data-task-prompt", 1)[0]
        self.assertNotIn("只需更新", inp)
        self.assertNotIn("胜者路径", inp)
        p3 = self.by_id["radix-independent"]
        self.assertIn("一轮个位排序后并非已经全局有序", p3)
        self.assertNotIn("再按十位稳定处理，可得到", p3)

    def test_merge_operation_precedes_merge_sort(self):
        self.assertIn("有序归并（merge）", self.by_id["merge-opportunity"])
        self.assertIn("归并排序（merge sort）", self.by_id["merge-recursion"])
        self.assertIn("相等先取左侧", self.by_id["merge-invariant"])
        self.assertIn("若某侧耗尽", self.by_id["merge-invariant"])

    def test_radix_stability_and_model_conditions(self):
        self.assertIn("21 和 22", self.by_id["radix-stability"])
        self.assertIn("22→21", self.by_id["radix-stability"])
        self.assertIn(r"\(d\)", self.by_id["radix-stability"])
        self.assertIn(r"\(b\)", self.by_id["radix-stability"])
        self.assertNotIn("Omega", self.by_id["radix-opportunity"])
        self.assertIn(r"\Omega(n\log n)", self.by_id["comparison-model"])

    def test_p4_uses_learned_mechanisms_or_given_duality(self):
        p4 = self.by_id["choice-independent"]
        self.assertIn("最小堆是最大堆的对偶", p4)
        self.assertIn("稳定 LSD", p4)
        self.assertIn("通用稳定数组归并排序", p4)
        self.assertIn(r"k\ge 2", p4)
        self.assertNotIn("稳定计数排序", p4)

    def test_no_teacher_backstage_in_student_pages(self):
        text = "\n".join(self.by_id.values())
        for phrase in ("机动时间", "如果学生仍不能解释",
                       "尚未正式发布", "教学设计预算", "教师专业支撑"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_storyboard_and_audit_page_ids(self):
        board = (HERE / "storyboard.md").read_text(encoding="utf-8")
        audit = (HERE / "tests" / "COGNITIVE_CONTINUITY_REVIEW.md").read_text(encoding="utf-8")
        ids = re.findall(r"^\| `([a-z0-9_-]+)` ／ S[0-7] \| \d\d \|", board, re.M)
        self.assertEqual(ids, [p["id"] for p in self.mod.COURSE.pages])
        for p in self.mod.COURSE.pages:
            self.assertIn(chr(96) + p["id"] + chr(96), audit)
        self.assertIn("C1 动机", audit)
        self.assertIn("C7 认知接续", audit)
        self.assertNotIn("|教学总时间", board)


if __name__ == "__main__":
    unittest.main()
