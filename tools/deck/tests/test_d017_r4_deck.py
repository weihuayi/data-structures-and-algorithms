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
import xml.etree.ElementTree as ET

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
        # A slide header is student-visible; do not require redundant body terminology.
        self.assertIn("Binary Search Tree", "".join(self.by_id["bst-order"][:2]))
        self.assertIn("Adelson-Velsky", self.by_id["avl-definition"][1])
        self.assertIn("Balance Factor", self.by_id["bf-calculate"][1])
        self.assertIn("left, *right", self.by_id["bst-node-links"][1])
        self.assertIn("Node *middle", self.by_id["rotation-order"][1])

    def test_r6_all_task_questions_use_one_emphasis_border(self):
        """Avoid stacking the outer course-prompt border and inner d17-question border."""
        task_pages = {
            "recall-sorted", "update-array", "bst-check", "bst-transfer",
            "bst-delete-two", "compare-path", "bf-every-node",
            "lr-single-fails", "independent-avl",
        }
        actual = set()
        for page in self.pages:
            page_id = page["id"]
            body = self.by_id[page_id][1]
            with self.subTest(page=page_id):
                self.assertNotRegex(
                    body,
                    r'<div class="course-prompt"[^>]*>\\s*<div class="d17-question">',
                    "A nested question frame produces two emphasis borders")
                if '<div class="course-prompt"' in body:
                    actual.add(page_id)
                    self.assertIn('data-task-prompt', body)
                    self.assertIn('data-task-answer', body)
        self.assertEqual(actual, task_pages)
        self.assertIn(
            '<div class="course-prompt" data-task-prompt>只检查根30就够了吗？还应检查哪些内部结点？</div>',
            self.by_id["bf-every-node"][1])
        # Independent explanatory emphasis is intentional; do not remove it.
        for page_id in ("bst-order", "need-balance", "synthesis"):
            self.assertIn('class="d17-question"', self.by_id[page_id][1])

    def test_r6_general_right_rotation_preserves_subtree_structure(self):
        body = self.by_id["rotation-order"][1]
        match = re.search(r'<svg class="d17-tree"[^>]*>.*?</svg>', body, re.S)
        self.assertIsNotNone(match, "The general rotation must include both trees")
        svg = ET.fromstring(match.group())
        states = {g.attrib["data-rotation-state"]: g for g in svg.iter()
                  if "data-rotation-state" in g.attrib}
        self.assertEqual(set(states), {"before", "after"})
        expected = {
            "before": {"z-y", "z-C", "y-A", "y-B"},
            "after": {"y-A", "y-z", "z-B", "z-C"},
        }
        for state, edges in expected.items():
            with self.subTest(state=state):
                tree = states[state]
                self.assertEqual(
                    {e.attrib["data-edge"] for e in tree.iter()
                     if "data-edge" in e.attrib}, edges)
                self.assertEqual(
                    {n.attrib["data-node"] for n in tree.iter()
                     if "data-node" in n.attrib}, {"y", "z"})
                self.assertEqual(
                    {n.attrib["data-subtree"] for n in tree.iter()
                     if "data-subtree" in n.attrib}, {"A", "B", "C"})
                # Nodes are circles; entire subtrees are triangular shapes.
                for n in tree.iter():
                    if "data-node" in n.attrib:
                        self.assertTrue(any(c.tag.endswith("circle") for c in n))
                    if "data-subtree" in n.attrib:
                        self.assertTrue(any(c.tag.endswith("path") for c in n))
        for phrase in ("不是单个结点", "中序关键字序列", "Node *middle",
                       "z-&gt;left = middle", r"\(\operatorname{inorder}"):
            self.assertIn(phrase, body)

    def test_c11_code_previews_have_readable_contrast(self):
        """A present DOM/code string is not sufficient if CSS makes it invisible."""
        for page_id in ("bst-node-links", "rotation-order", "homework"):
            body = self.by_id[page_id][1]
            self.assertRegex(body, r'<pre class="d17-code"><code>[^<]+</code></pre>')
        self.assertIn("typedef struct Node", self.by_id["bst-node-links"][1])

        css = self.by_id["cover"][1]
        rule = re.search(r"[.]deck [.]d017 [.]d17-code[{]([^{}]+)[}]", css)
        self.assertIsNotNone(rule, "Find the actual lesson-specific code style")
        declarations = dict(
            item.strip().split(":", 1)
            for item in rule.group(1).split(";") if ":" in item
        )
        # The base pre style uses pale text for a dark background; this
        # lesson overrides the background, so it must override color too.
        fg, bg = declarations.get("color"), declarations.get("background")
        self.assertRegex(fg or "", r"^#[0-9a-fA-F]{6}$")
        self.assertRegex(bg or "", r"^#[0-9a-fA-F]{6}$")

        def luminance(color):
            rgb = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
            linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
                      for x in rgb]
            return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

        lighter, darker = sorted((luminance(fg), luminance(bg)), reverse=True)
        contrast = (lighter + 0.05) / (darker + 0.05)
        self.assertGreaterEqual(contrast, 7.0, "C11 examples must remain legible on projection")

    def test_inorder_introduced_before_two_distinct_deletions(self):
        pages = {item["id"]: item for item in self.pages}
        self.assertLess(EXPECTED.index("bst-order"), EXPECTED.index("bst-delete-cases"))
        self.assertLess(EXPECTED.index("bst-delete-cases"), EXPECTED.index("bst-delete-two"))
        definition = self.by_id["bst-order"][1]
        self.assertIn("中序遍历", definition)
        self.assertIn("左子树 → 结点 → 右子树", definition)
        self.assertIn("中序关键字递增", definition)

        single_title, single_body, _ = self.by_id["bst-delete-cases"]
        self.assertIn("删除 27", single_title)
        self.assertIn("删除结点 27", single_body)
        self.assertIn("20 的右链接由 27 改指向 25", single_body)
        self.assertIn("重新从完整 T1", single_body)

        two_title, two_body, _ = self.by_id["bst-delete-two"]
        self.assertIn("删除根30", two_title)
        initial = two_body.split("<summary>核对答案与理由</summary>", 1)[0]
        self.assertIn("中序前驱", initial)
        self.assertIn("完整 T1", initial)
        self.assertNotIn("中序前驱为", initial)
        self.assertIn("中序前驱为", two_body.split("<summary>核对答案与理由</summary>", 1)[1])

    def test_math_typesetting_on_conceptual_pages(self):
        """Mathematical relationships must use KaTeX delimiters, not plain pseudo-formulas."""
        required = {
            "build-shape-chain": [r"\(16&lt;20&lt;27", r"\(h=7\)"],
            "worst-shape": [r"\(O(h)\)", r"\(O(n)\)", r"\(\not\Rightarrow"],
            "height-observe": [r"\(h(v)=1+\max\{", r"h(L(v))"],
            "avl-definition": [r"\(\lvert h(L(v))"],
            "bf-calculate": [r"\(\mathrm{BF}(v)=h(L(v))", r"\(\mathrm{BF}(v)\in"],
            "structure-choice": [r"\(O(\log n)\)"],
            "synthesis": [r"\(\lvert\mathrm{BF}(v)\rvert"],
        }
        for page_id, fragments in required.items():
            body = self.by_id[page_id][1]
            for fragment in fragments:
                with self.subTest(page=page_id,fragment=fragment):
                    self.assertIn(fragment, body)
        self.assertTrue(self.deck.MATH, "The deck must load the KaTeX renderer")

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
