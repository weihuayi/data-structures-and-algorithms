"""D013 content and interaction contracts; geometry is checked in the browser."""
import sys
import unittest
from pathlib import Path

DECK_DIR = Path(__file__).resolve().parents[3] / "course/decks/d013-mst-and-union-find"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import load_deck, render_document


class D013PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck = load_deck(DECK_DIR)
        cls.slides = cls.deck.SLIDES

    def test_no_teacher_notes_anywhere(self):
        self.assertEqual(len(self.slides), 33)
        for title, body, _ in self.slides:
            with self.subTest(slide=title):
                self.assertNotIn('class="teacher-note"', body)
                self.assertNotIn("教学注记", body)

    def test_outline_does_not_show_internal_break(self):
        self.assertNotIn("分钟断点", self.slides[1][1])

    def test_mst_definition_uses_katex(self):
        self.assertTrue(self.deck.MATH)
        self.assertIn(r"\(G=(V,E,w)\)", self.slides[5][1])
        self.assertIn(r"\sum_{e\in T}", self.slides[5][1])
        self.assertNotIn("本例非负建设成本下", self.slides[5][1])

    def test_exchange_example_is_explicit(self):
        page = self.slides[8][1]
        self.assertIn("独立辅助例", page)
        self.assertEqual(page.count('<figure class="graph-figure">'), 3)
        for marker in (r"\(F=\{AB\}\)", "e=AC", "f=BC", "T′"):
            self.assertIn(marker, page)

    def test_start_at_c_has_graph_and_hidden_answer(self):
        page = self.slides[13][1]
        self.assertIn('data-vertex="C"', page)
        self.assertIn("graph-figure", page)
        self.assertIn("<details><summary>核对答案与理由</summary>", page)
        self.assertIn("BA:1", page)

    def test_disconnected_graph_removes_both_edges(self):
        page = self.slides[14][1]
        self.assertIn('data-vertex="E"', page)
        self.assertNotIn('data-edge="C-E"', page)
        self.assertNotIn('data-edge="D-E"', page)
        self.assertIn("最小生成森林", page)

    def test_complexity_uses_big_o(self):
        self.assertIn(r"\(O(n^2)\)", self.slides[25][1])

    def test_textbook_mapping_and_full_scan_contract_are_visible(self):
        mapping = self.slides[26][1]
        for term in ('lowcost', 'adjvex', 'Vexset', 'present', 'weight', 'find(v)'):
            self.assertIn(term, mapping)
        self.assertIn('扫描全部边', self.slides[16][1])
        self.assertIn('未处理', self.slides[28][1])

    def test_generated_html_matches_source(self):
        expected, count = render_document(DECK_DIR)
        self.assertEqual(count, 33)
        self.assertEqual((DECK_DIR / "index.html").read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
