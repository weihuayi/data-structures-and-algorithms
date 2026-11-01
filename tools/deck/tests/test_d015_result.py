"""The actual construction answer must contain the requested resulting graph."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import DECKS, render_document


class Graphs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.graphs = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'svg':
            self.current = dict(vertices=[], edges=[], arrows=0)
            self.graphs.append(self.current)
        if self.current is not None:
            if 'data-vertex' in attrs: self.current['vertices'].append(attrs['data-vertex'])
            if 'data-edge' in attrs: self.current['edges'].append(attrs['data-edge'])
            if 'graph-arrow' in attrs.get('class', '').split(): self.current['arrows'] += 1

    def handle_endtag(self, tag):
        if tag == 'svg': self.current = None


def completed_graph_valid(html):
    parser = Graphs(); parser.feed(html)
    if len(parser.graphs) != 1: return False
    graph = parser.graphs[0]
    # Expected task result is written independently of the rendering helper.
    return (len(graph['vertices']) == 7 and set(graph['vertices']) == set('ABCDEFG') and
            len(graph['edges']) == 8 and
            set(graph['edges']) == {'A-C', 'A-E', 'B-D', 'E-D', 'C-F', 'D-F', 'C-G', 'E-G'} and
            graph['arrows'] == 8)


class ConstructionAnswerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html, _ = render_document(DECKS / 'd015-topological-and-critical-path')
        page = html.split('data-page-id="aov"', 1)[1].split('</section>', 1)[0]
        cls.input, cls.answer = page.split('data-task-answer', 1)

    def test_result_and_input_in_final_generated_document(self):
        self.assertTrue(completed_graph_valid(self.answer))
        parser = Graphs(); parser.feed(self.input)
        self.assertEqual(len(parser.graphs), 1)
        self.assertEqual(set(parser.graphs[0]['vertices']), set('ABCDEF'))
        self.assertNotIn('C-G', parser.graphs[0]['edges'])

    def test_missing_reversed_extra_or_undirected_answer_is_rejected(self):
        faults = [self.answer.replace('data-edge="C-G"', 'data-missing="C-G"'),
                  self.answer.replace('data-edge="C-G"', 'data-edge="G-C"'),
                  self.answer.replace('data-edge="C-G"', 'data-edge="D-G"'),
                  self.answer.replace('data-vertex="G"', 'data-vertex="F"'),
                  self.answer.replace('class="graph-arrow marked"', 'class="line"'),
                  self.answer.replace('</svg>', '<g data-edge="D-G"></g></svg>')]
        for bad in faults:
            self.assertFalse(completed_graph_valid(bad))


if __name__ == '__main__':
    unittest.main()
