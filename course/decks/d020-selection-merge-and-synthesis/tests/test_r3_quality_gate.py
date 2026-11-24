"""D020 QA-09–14: source, stage-budget and assessment boundary contracts.

These checks establish design consistency, not teaching effectiveness.
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools" / "deck"))


def read(path):
    return (HERE / path).read_text(encoding="utf-8")


def deck():
    spec = importlib.util.spec_from_file_location("d020_r3_deck", HERE / "slides.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ThirdRoundGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = deck()
        cls.by_id = {x["id"]: (x, cls.m.SLIDES[i][1])
                     for i, x in enumerate(cls.m.COURSE.pages)}
        cls.report = read("tests/QUALITY_GATE_R3.md")

    def test_34_pages_and_core_task_roles(self):
        self.assertEqual(len(self.by_id), 34)
        for pid in ("heap-independent", "stable-merge-independent",
                    "radix-independent", "radix-stability",
                    "comparison-model", "choice-independent"):
            with self.subTest(pid=pid):
                meta, html = self.by_id[pid]
                self.assertEqual(meta["role"], "exercise")
                self.assertIn("data-task-input", html)
                self.assertIn("data-task-answer", html)
                self.assertIn("<details", html)
                self.assertNotIn("<details open", html)

    def test_radix_stability_has_independent_condition_check(self):
        html = self.by_id["radix-stability"][1]
        self.assertIn("快速独立判断", html)
        self.assertIn("21 和 22", html)
        self.assertIn("22→21", html)
        self.assertIn(r"O(d(n+b))", html)

    def test_p4_core_and_extension_constraints_are_explicit(self):
        html = self.by_id["choice-independent"][1]
        self.assertIn("A、B 必答", html)
        self.assertIn("C 为时间允许时的迁移挑战", html)
        self.assertIn("此情境不要求稳定", html)
        self.assertIn("相同关键字", html)
        self.assertIn("最小堆是最大堆的对偶", html)
        self.assertNotIn("稳定计数排序", html)

    def test_c11_radix_buffer_key_domain_and_digit_size_are_guarded(self):
        src = read("code/sorting_d020_demo.c")
        for marker in ("n > 32", "a[i].key < 0", "digits < needed",
                       "unsigned long long divisor = 1ULL",
                       "digit + 1 < digits", "maximum_digits"):
            with self.subTest(marker=marker):
                self.assertIn(marker, src)
        self.assertNotIn("int divisor = 1;", src)
        self.assertNotIn("divisor *= 10;", src)

    def test_design_budget_and_timed_fallback_are_consistent(self):
        rows = re.findall(
            r"^\| `[a-z0-9_-]+` ／ S([0-7]) \| \d\d \|.*?\| ([0-9]+(?:\.[0-9]+)?) \|$",
            read("storyboard.md"), re.M)
        self.assertEqual(len(rows), 34)
        stages = {f"S{i}":0.0 for i in range(8)}
        for stage,minutes in rows:
            stages["S"+stage] += float(minutes)
        self.assertEqual(stages, dict(zip(stages, [5,6,27,4,18,14,8,3])))
        self.assertEqual(sum(stages.values()),85)
        self.assertEqual(sum(stages[f"S{i}"] for i in range(4)),42)
        self.assertEqual(sum(stages[f"S{i}"] for i in range(4,8)),43)
        for statement in ("78 分钟教学 + 2 分钟机动 = 80 分钟",
                          "85+8", "93 分钟", "P4 A/B", "教师试讲记录模板"):
            self.assertIn(statement, self.report)

    def test_qualified_claims_and_teacher_signoff(self):
        for phrase in ("不等于学生掌握", "不是实际试讲记录",
                       "待验证", "P0"):
            self.assertIn(phrase, self.report)
        self.assertNotIn("学生已全部掌握", self.report)


if __name__ == "__main__":
    unittest.main()
