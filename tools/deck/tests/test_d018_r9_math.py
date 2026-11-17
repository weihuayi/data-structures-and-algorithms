"""D018 R9: semantic anchors, LaTeX consistency, and audit fault fixtures."""
from pathlib import Path
import re
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from build import DECKS, load_deck
from math_audit import audit_html, audit_pages

DECK = DECKS / "d018-hashing"


class D018R9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_deck(DECK)
        cls.pages = cls.mod.PAGES
        cls.by_id = {page["id"]: page for page in cls.pages}
        cls.html = (DECK / "index.html").read_text(encoding="utf-8")

    def test_stable_structure_and_bst_prior_knowledge(self):
        self.assertEqual(len(self.pages), 34)
        self.assertEqual(self.pages[3]["id"], "recall-avl")  # Stable legacy ID.
        p4 = self.by_id["recall-avl"]
        self.assertIn("BST", p4["title"])
        self.assertNotIn("AVL 是根据什么信息", p4["title"])
        self.assertIn("BST 的全子树顺序性质", p4["body"])
        self.assertIn("AVL 在 BST 顺序性质之外", p4["body"])
        self.assertIn(r"\(35&lt;40\)", p4["body"])
        self.assertIn("40 → 25 → 35", p4["body"].split("<details", 1)[1])
        self.assertNotIn("40 → 25 → 35", p4["body"].split("<details", 1)[0])
        self.assertIn("D017 BST 的有序查找路径", self.mod.COURSE.sections[0].scope)

    def test_direct_address_space_illustration_and_hash_parameter(self):
        p7 = self.by_id["direct-space"]["body"]
        self.assertIn('class="hash-r9-space"', p7)
        self.assertIn("不按比例", p7)
        self.assertIn("不是后续散列主例", p7)
        self.assertEqual(p7.count('class="hash-r9-slot record"'), 3)
        self.assertIn(r"\(n=3\)", p7)
        self.assertIn(r"31\,002\,457", p7)
        self.assertEqual(31002456 + 1, 31002457)
        p8 = self.by_id["hash-map"]["body"]
        for term in (r"\(h(k)=k\bmod m\)", r"\(m=7\)",
                     r"\(h(10)=10\bmod7=3\)", r"\(0,\ldots,6\)"):
            self.assertIn(term, p8)
        p9 = self.by_id["detect-collision"]["body"]
        for k in (17,24,13):
            self.assertIn(r"\(h(" + str(k) + r")\)", p9.split("<details", 1)[0])
            self.assertIn(r"\(h(" + str(k) + r")=" + ("6" if k == 13 else "3") + r"\)", p9.split("<details", 1)[1])
        self.assertNotIn(r"\(h(17)=3\)", p9.split("<details", 1)[0])

    def test_bucket_and_cost_math(self):
        p12 = self.by_id["chain-lookup"]["body"]
        self.assertIn(r"关键字 \(k\) 都归属于 \(h(k)\)", p12)
        self.assertIn(r"\(h(24)=h(31)=3\)", p12)
        p29 = self.by_id["expected-cost"]["body"]
        self.assertIn("常数时间", self.by_id["expected-cost"]["title"])
        for expr in (r"\(O(m)\)", r"\(m=\Theta(n)\)",
                     r"\(O(n)\)", r"\(O(1)\)", r"\(O(\log n)\)",
                     r"\(O(g(n))\)", r"\(\Omega(g(n))\)",
                     r"\(\Theta(g(n))\)"):
            self.assertIn(expr, p29)
        for term in ("渐近上界","渐近下界","渐近紧确界",
                     "最坏","期望","摊还"):
            self.assertIn(term,p29)
        self.assertIn(r"\(ASL_{\mathrm{succ}}=1\)",self.by_id["same-load"]["body"])
        self.assertIn(r"\(ASL_{\mathrm{succ}}=2.5\)",self.by_id["same-load"]["body"])

    def test_math_audit_clean_for_all_34_page_bodies(self):
        self.assertEqual([],audit_pages(self.pages))

    def test_math_audit_detects_true_omissions(self):
        cases = [
            ("hash-function", "<p>独立计算 h(17) 和 h(24)。</p>"),
            ("probe-function", "<p>p(17,1)=4；访问下一个槽。</p>"),
            ("asymptotic-bound", "<p>最坏 O(n)；期望 O(1)。</p>"),
            ("numeric-assignment", "<p>令 m=7、r=3。</p>"),
            ("unclosed-math", r"<p>计算 \(h(17)=3。</p>")
        ]
        for expected, markup in cases:
            with self.subTest(expected=expected):
                found = audit_html("fault",markup)
                self.assertIn(expected,[x.rule for x in found])

    def test_math_audit_excludes_literal_and_already_formatted(self):
        markup = (r"<p>\(h(17)=3\)，数学式已经标记；ASL 作为名词可保留。</p>"
                  r"<pre>h(17)=3; O(n)</pre>"
                  r"<code>p(17,1)=4</code>"
                  r"<svg><text>h(k) 和 O(n)</text></svg>"
                  r"<style>.x::before{content:'O(n)'}</style>"
                  r"<select><option>m=7</option></select>")
        self.assertEqual([],audit_html("demo",markup))

    def test_generated_html_carries_changed_semantics(self):
        for text in ("BST 为什么能够通过比较排除整棵子树？",
                     "为什么散列查找不能无条件保证常数时间？",
                     'class="hash-r9-space"',
                     r"\(\Omega(g(n))\)"):
            self.assertIn(text,self.html)
        self.assertIn('data-page-id="direct-space"',self.html)
        self.assertEqual(len(re.findall(r'<section class="slide"',self.html)),34)


if __name__ == "__main__":
    unittest.main()
