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
