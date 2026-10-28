"""D013 visible-content order: terms, definitions, and page dependencies."""
import sys
import unittest
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'deck'))
from build import load_deck

DECK = ROOT / 'course/decks/d013-mst-and-union-find'


class D013ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_deck(DECK)
        cls.slides = cls.mod.SLIDES

    def text(self, page):
        return ' '.join(self.slides[page - 1])

    def first_page(self, term):
        return next(i for i in range(1, len(self.slides) + 1) if term in self.text(i))

    def test_page_count_and_no_legacy_page_definitions(self):
        self.assertEqual(len(self.slides), 33)
        self.assertFalse(hasattr(self.mod, '_LEGACY_SLIDES'))

    def test_acronyms_are_defined_at_first_visible_use(self):
        cases = [
            ('MST', 6, 'Minimum Spanning Tree'),
            ('MSF', 15, 'Minimum Spanning Forest'),
            ('Prim', 11, "Prim's Algorithm"),
            ('Kruskal', 17, "Kruskal's Algorithm"),
            ('DSU', 19, 'Disjoint Set Union'),
            ('Union-Find', 19, 'Union-Find'),
        ]
        for term, page, definition in cases:
            self.assertEqual(self.first_page(term), page, term)
            self.assertIn(definition, self.text(page), term)

    def test_outline_and_part_titles_avoid_unintroduced_names(self):
        for page in (2, 10, 16):
            text = self.text(page)
            for term in ('MST', 'MSF', 'Prim', 'Kruskal', 'DSU', '并查集'):
                self.assertNotIn(term, text, (page, term))
        self.assertIn('怎样定义连接全网的最低成本问题？', self.text(2))
        self.assertIn('怎样从一个顶点出发，逐步扩张连接区域？', self.text(2))
        self.assertIn('怎样按照边的成本顺序，逐步合并不同分组？', self.text(2))
        self.assertIn('怎样检查结果、分析计算代价并解决新问题？', self.text(2))

    def test_prim_auxiliary_state_precedes_player(self):
        aux = self.text(12)
        self.assertIn('辅助信息', aux)
        for term in ('U', 'F', 'key[v]', 'parent[v]', 'has_key', 'used'):
            self.assertIn(term, aux)
        self.assertIn('不是从起点到 v 的路径长度', aux)
        self.assertNotIn('data-tree-player', aux)
        self.assertIn('data-tree-player', self.text(13))

    def test_kruskal_player_precedes_dsu_definition_and_hides_parent_pointers(self):
        player = self.text(18)
        self.assertIn('当前分组', player)
        self.assertIn('data-tree-player', player)
        self.assertNotIn('DSU', player)
        self.assertNotIn('父指针', player)
        dsu = self.text(19)
        self.assertIn('Disjoint Set Union', dsu)
        self.assertIn('不能单独保证 MST 的全局最优', dsu)
        self.assertIn('当前已经接受的边', dsu)

    def test_cut_and_exchange_figures_state_all_premises(self):
        diagrams = [ET.fromstring(s) for s in re.findall(r'<svg.*?</svg>', self.text(8))]
        self.assertEqual(len(diagrams), 2)
        for svg, expected_s in zip(diagrams, ({'A', 'B'}, {'A', 'B', 'C'})):
            inside = {g.attrib['data-vertex'] for g in svg.findall('.//g[@data-state="visited"]')}
            self.assertEqual(inside, expected_s)
            self.assertIsNotNone(svg.find('.//g[@class="graph-region"]'))
            crossing, candidate = [], []
            for g in svg.findall('.//g[@data-edge]'):
                a, b = g.attrib['data-edge'].split('-')
                classes = g.find('path').attrib['class'].split()
                cross = (a in inside) != (b in inside)
                if 'marked' in classes:
                    self.assertFalse(cross, 'cut must respect selected F')
                if cross:
                    crossing.append(int(g.find('text[@class="graph-label"]').text))
                if 'candidate' in classes:
                    self.assertTrue(cross)
                    candidate.append(int(g.find('text[@class="graph-label"]').text))
            self.assertEqual(candidate, [min(crossing)])

        stages = [ET.fromstring(s) for s in re.findall(r'<svg.*?</svg>', self.text(9))]
        self.assertEqual(len(stages), 3)
        selected = []
        for svg in stages:
            selected.append({g.attrib['data-edge'] for g in svg.findall('.//g[@data-edge]')
                             if 'marked' in g.find('path').attrib['class'].split()})
        self.assertEqual(selected, [{'A-B', 'B-C'}, {'A-B', 'B-C'}, {'A-B', 'A-C'}])
        self.assertTrue(all('A-B' in edges for edges in selected), 'exchange preserves F')
        self.assertIn('跨回', self.text(9))
        self.assertIn(r'\(f\notin F\)', self.text(9))
        self.assertIn(r'\(F=\varnothing\)', self.text(9))
        self.assertIn('已选边连通全部顶点并组成一棵树', self.text(9))

    def test_textbook_notation_uses_math_without_extra_cut_terminology(self):
        page = self.text(8)
        self.assertIn(r'\(U=\{A,B\}\)', page)
        self.assertIn(r'\(V-U=\{C,D,E\}\)', page)
        self.assertIn('教材 MST 性质', page)
        for title, body, _ in self.slides:
            self.assertNotIn('割', title + body)
        for number in (8, 9, 11, 12, 13, 17):
            for old in ('S=', 'S′=', 'V∖S', '已纳入 S', '接入 S'):
                self.assertNotIn(old, self.text(number))

    def test_dsu_static_figures_use_real_snapshots_and_are_labeled(self):
        objects = self.text(20)
        self.assertIn('真实快照', objects)
        self.assertIn('p[D]=A', objects)
        self.assertIn('已拒绝的 AC', objects)
        self.assertIn('已选边集合', objects)
        self.assertIn(r'\(F=\{AB,BC,CD\}\)', objects)
        self.assertIn('E 单独成树', objects)
        compress = self.text(21)
        self.assertIn('独立辅助例（不是主例）', compress)
        self.assertIn('压缩前', compress)
        self.assertIn('压缩后', compress)
        self.assertIn('p[D]=C', compress)
        self.assertNotIn('data-tree-player', compress)

    def test_exercise_input_visible_and_answer_collapsed(self):
        exercise = self.text(29)
        self.assertIn('PQ=3', exercise)
        self.assertIn('PR=1', exercise)
        self.assertIn('QR=2', exercise)
        self.assertIn('QS=4', exercise)
        self.assertIn('RS=5', exercise)
        self.assertIn('总权 7', exercise)
        self.assertNotIn('PQ=4', exercise)
        self.assertNotIn('QS=1', exercise)
        self.assertIn('<details><summary>核对答案与理由（7+2 分钟）</summary>', exercise)
        self.assertNotIn('<details open', exercise)

    def test_independent_dsu_diagnostic_keeps_input_outside_answer(self):
        page = self.text(22)
        visible, solution = page.split('<details>', 1)
        for edge in ('A-B', 'C-D', 'D-B'):
            self.assertIn(f'data-edge="{edge}"', visible)
        self.assertNotIn('data-edge="C-B"', visible)
        self.assertIn('find(C)', visible)
        self.assertIn('p[C] 从 D 改为 B', solution)
        self.assertIn(r'\(F\) 不变', solution)
        self.assertNotIn('<details open', page)


if __name__ == '__main__':
    unittest.main()
