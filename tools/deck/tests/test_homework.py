"""Real and negative fixtures for homework contract and local C execution."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "deck"))
from build import DECKS, load_deck
from check_homework import check_all, check_page


class HomeworkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck = DECKS / "d016-search-order-and-asl"
        model = load_deck(cls.deck)
        cls.title, cls.body = [(t, b) for t, b, _ in model.SLIDES
                               if "课后" in t and ("核对" in t or "作业" in t)][0]

    def test_all_lessons_have_structurally_complete_homework(self):
        count, issues = check_all()
        self.assertGreaterEqual(count, 16)
        self.assertEqual(issues, [])

    def test_d016_requires_concrete_A_and_B(self):
        self.assertEqual(check_page(self.deck, self.title, self.body), [])
        for old, problem in [
            ("第 7 章选择题", "no concrete textbook"),
            ("<strong>A · 书本习题", "missing formal A"),
            ("<strong>B · 程序实践", "missing formal B"),
            ("过程记录", "process record"),
            ("homework-guide.md", "shared homework guide"),
        ]:
            with self.subTest(removed=old):
                fake = self.body.replace(old, "no-longer-present")
                issues = check_page(self.deck, self.title, fake)
                self.assertTrue(any(problem in msg for msg in issues), issues)

    def test_conditional_homework_and_repository_execution_rejected(self):
        for bad, expected in [
            ("如另行布置为正式作业", "demoted"),
            ("要求在仓库执行", "repository execution"),
        ]:
            with self.subTest(bad=bad):
                issues = check_page(self.deck, self.title, self.body + bad)
                self.assertTrue(any(expected in msg for msg in issues), issues)

    def test_missing_code_reference_rejected(self):
        fake = self.body.replace("code/search_demo.c", "code/absent_demo.c")
        self.assertTrue(any("missing referenced" in x
                            for x in check_page(self.deck, self.title, fake)))

    def test_unspecified_tmp_path_rejected(self):
        fake = self.body.replace("个人电脑", "设备").replace("本地", "设备").replace("Linux", "设备")
        fake += "<code>/tmp/d016</code>"
        self.assertTrue(any("local-environment explanation" in x
                            for x in check_page(self.deck, self.title, fake)))


@unittest.skipUnless(shutil.which("gcc"), "GCC required for local C regression")
class HomeworkCExecutionTests(unittest.TestCase):
    def test_d012_d016_actual_homework_programs(self):
        cases = [
            ("d012-graph-traversal", "traversal_demo.c", (), "homework+BFS"),
            ("d013-mst-and-union-find", "mst_demo.c", (), "homework"),
            ("d014-shortest-path", "shortest_path_demo.c", ("homework",), ""),
            ("d015-topological-and-critical-path", "dependency_demo.c", ("homework",), ""),
            ("d016-search-order-and-asl", "search_demo.c", ("last",), ""),
            ("d016-search-order-and-asl", "search_demo.c", ("block28",), ""),
        ]
        with tempfile.TemporaryDirectory(prefix="course-homework-") as tmp:
            compiled = {}
            for deck, source, arguments, marker in cases:
                with self.subTest(deck=deck, command=arguments):
                    key = (deck, source)
                    exe = compiled.get(key)
                    if exe is None:
                        exe = str(Path(tmp) / f"program-{len(compiled)}")
                        command = ["gcc", "-std=c11", "-Wall", "-Wextra",
                                   str(DECKS / deck / "code" / source), "-o", exe]
                        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        compiled[key] = exe
                    result = subprocess.run([exe, *arguments], capture_output=True,
                                            text=True, timeout=15)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertTrue(result.stdout.strip(), "no exercise output")
                    if marker:
                        self.assertIn(marker, result.stdout)


if __name__ == "__main__":
    unittest.main()
