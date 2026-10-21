"""General graph semantics independent of classroom examples."""
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graph_diagram import graph


class GraphDiagramTests(unittest.TestCase):
    def svg(self, **options):
        html = graph({'P': (50,50), 'Q': (200,50), 'I': (400,50)},
                     [('P','Q')], caption='P < Q & isolated I', **options)
        return ET.fromstring(html[html.index('<svg'):html.index('</svg>')+6])

    def test_undirected_keeps_isolate_and_one_logical_edge(self):
        svg = self.svg(marked=[('P','Q')])
        self.assertEqual([n.attrib['data-vertex'] for n in svg.findall('.//g[@data-vertex]')], ['P','Q','I'])
        self.assertEqual(len(svg.findall('.//g[@data-edge]')), 1)
        self.assertEqual(len(svg.findall('.//path')), 1)
        self.assertIn('marked', svg.find('.//path').attrib['class'])
        self.assertEqual(svg.find('title').text, 'P < Q & isolated I')

    def test_directed_arrow_stops_at_boundary_and_keeps_zero(self):
        svg = self.svg(directed=True, labels={('P','Q'):0})
        self.assertEqual(svg.find('.//path').attrib['d'], 'M 74.0 50.0 L 176.0 50.0')
        self.assertEqual(svg.find('.//text[@class="graph-label"]').text, '0')
        self.assertIsNotNone(svg.find('.//path[@class="graph-arrow"]'))

    def test_coincident_endpoints_rejected(self):
        with self.assertRaises(ValueError):
            graph({'P':(0,0),'Q':(0,0)}, [('P','Q')], caption='invalid')

    def test_undirected_marking_ignores_endpoint_order(self):
        for marked in [[('P', 'Q')], [('Q', 'P')]]:
            svg = self.svg(marked=marked)
            self.assertEqual(svg.find('.//path').attrib['class'], 'graph-edge marked')

    def test_directed_marking_preserves_direction(self):
        html = graph({'P': (50,50), 'Q': (200,50)},
                     [('P','Q'), ('Q','P')], caption='Two different arcs',
                     directed=True, marked=[('Q','P')])
        svg = ET.fromstring(html[html.index('<svg'):html.index('</svg>')+6])
        forward = svg.find('.//g[@data-edge="P-Q"]')
        reverse = svg.find('.//g[@data-edge="Q-P"]')
        self.assertEqual(forward.find('path').attrib['class'], 'graph-edge')
        self.assertEqual(reverse.find('path').attrib['class'], 'graph-edge marked')
        self.assertEqual(reverse.findall('path')[1].attrib['class'], 'graph-arrow marked')
        self.assertEqual(reverse.find('path').attrib['d'], 'M 176.0 50.0 L 74.0 50.0')

    def test_legend_requires_an_existing_marked_edge(self):
        nodes = {'P': (50,50), 'Q': (200,50), 'I': (400,50)}
        for marked in [(), [('Q', 'I')]]:
            html = graph(nodes, [('P','Q')], caption='Only PQ exists', marked=marked)
            self.assertNotIn('graph-legend', html)
        html = graph(nodes, [('P','Q')], caption='Only PQ exists', marked=[('Q','P')])
        self.assertIn('graph-legend', html)
        self.assertIn('红色粗实线', html)
        # Reversing a directed mark must not produce a false legend either.
        html = graph(nodes, [('P','Q')], caption='Only P to Q',
                     marked=[('Q','P')], directed=True)
        self.assertNotIn('graph-legend', html)

    def test_highlight_style_and_node_annotations(self):
        css = (Path(__file__).resolve().parents[1] / 'deck.css').read_text()
        self.assertIn('.graph-edge.marked{stroke:#c62828;stroke-width:6;stroke-dasharray:none}', css)
        svg = self.svg(node_details={'P': '编号 0', 'I': '度 0'})
        self.assertEqual([x.text for x in svg.findall('.//text[@class="graph-detail"]')],
                         ['编号 0', '度 0'])
