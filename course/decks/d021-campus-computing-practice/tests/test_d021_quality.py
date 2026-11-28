"""D021 source, release contract and independent reference output regression."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools" / "deck"))
from build import load_deck, render_document
from check_homework import check_page
from cognitive_checks import storyboard_checks, prediction_checks

DECK = ROOT / "course/decks/d021-campus-computing-practice"
TASK = ROOT / "course/assignments/campus-computing-practice"
REF = TASK / "reference"


class D021Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_deck(DECK)
        cls.pages = dict(zip(cls.model.PAGE_IDS, cls.model.SLIDES))

    def test_build_and_storyboard(self):
        doc, count = render_document(DECK)
        self.assertEqual(doc, (DECK / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(count, len(set(self.model.PAGE_IDS)))
        for check in storyboard_checks(DECK, self.model.COURSE) + prediction_checks(self.model.COURSE, self.model.SLIDES):
            self.assertEqual(check["status"], "pass", check)

    def test_open_discussion_precedes_model_and_release(self):
        ids = self.model.PAGE_IDS
        self.assertLess(ids.index("open-discussion"), ids.index("define-task"))
        self.assertLess(ids.index("define-task"), ids.index("practice-a"))
        self.assertEqual(ids[-1], "final-practice-release")
        title, body, _ = self.model.SLIDES[-1]
        self.assertEqual(check_page(DECK, title, body), [])
        self.assertTrue(check_page(DECK, title, body.replace("独立完成", "完成")))
        self.assertTrue(check_page(DECK, title, body.replace("不要求立即选题", "立即选题")))

    def test_professional_boundaries(self):
        a = (TASK / "README.md").read_text(encoding="utf-8")
        for fragment in ("课程之间不重叠", "原始路网 0 到 5", "按编号的数值升序", "平均、最大等待时间均不定义"):
            self.assertIn(fragment, a)
        for key in ("practice-a", "practice-b", "practice-c"):
            self.assertIn("现实背景", self.pages[key][1])
            self.assertIn("计算任务", self.pages[key][1])
        self.assertIn("固定非负通行时间", self.pages["multiple-tasks"][1])
        self.assertIn("编号唯一", self.pages["define-task"][1])

    def test_reference_programs_strict_c11_and_outputs(self):
        cases = {
            "task_a_timetable.c": ["C1 -> C2：可用 20 分钟，需要 25 分钟：不足 5 分钟", "C4 -> C5：可用 20 分钟，需要 25 分钟：不足 5 分钟", "C2 -> C3：可用 20 分钟，需要 20 分钟：满足", "所有相邻课程均满足移动时间要求", "课表为空"],
            "task_b_campus_bfs.c": ["0 -> 1 -> 4 -> 5", "0 -> 2 -> 3 -> 5", "不可达", "路径（0 条边）：2"],
            "task_c_service_queue.c": ["平均等待时间：2.17 分钟", "最大等待时间：5 分钟", "平均等待时间：1.67 分钟", "最大等待时间：4 分钟", "没有请求", "平均等待时间：0.00 分钟"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            for file, expected in cases.items():
                with self.subTest(file=file):
                    exe = Path(tmp) / file.removesuffix(".c")
                    result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic", str(REF / file), "-o", str(exe)], capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    output = subprocess.run([str(exe)], capture_output=True, text=True, check=True, timeout=10).stdout
                    for value in expected:
                        self.assertIn(value, output)
                    if file.startswith("task_a"):
                        self.assertEqual(output.count("不足 5 分钟"), 2)
                    if file.startswith("task_c"):
                        ties = output.split("边界测试：编号数值排序", 1)[1]
                        self.assertLess(ties.index("R2"), ties.index("R10"))
                        self.assertIn("平均等待时间：0.50 分钟", ties)


if __name__ == "__main__":
    unittest.main()
