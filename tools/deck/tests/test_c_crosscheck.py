"""Cross-check the classroom C program against the Python state model."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'deck'))
from graph_trace import INDEX, NODES, bfs_states, dfs_states


def parse_output(text):
    blocks, current = {}, None
    for line in text.splitlines():
        m = re.match(r'^([^:]+): order=([A-Z]+) scans=(\d+) roots=(\d+)$', line)
        if m:
            current = m.group(1)
            blocks[current] = {'order': m.group(2), 'scans': int(m.group(3)),
                               'roots': int(m.group(4))}
        elif current and line.startswith('parent:'):
            blocks[current]['parent'] = tuple(int(x) for x in line.split(':', 1)[1].split())
        elif current and line.startswith(('distance-from-A:', 'tree-depth:')):
            key = line.split(':', 1)[0]
            blocks[current][key] = tuple(int(x) for x in line.split(':', 1)[1].split())
    return blocks


def py_parent(states):
    return tuple(-1 if states[-1]['parent'].get(v) is None else INDEX[states[-1]['parent'][v]]
                 for v in NODES)


@unittest.skipUnless(shutil.which('gcc'), 'gcc is required for the C/Python cross-check')
class ClassroomCCrossCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        exe = Path(cls.tmp.name) / 'd012'
        subprocess.run(
            ['gcc', '-std=c11', '-Wall', '-Wextra',
             str(ROOT / 'course/decks/d012-graph-traversal/code/traversal_demo.c'),
             '-o', str(exe)],
            check=True, capture_output=True, text=True)
        cls.raw = subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout
        cls.blocks = parse_output(cls.raw)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_classroom_checks_are_reported(self):
        self.assertIn('All classroom checks passed.', self.raw)

    def test_dfs_recursive_and_frame_match_python(self):
        for name in ('DFS/list', 'DFS/stack'):
            c = self.blocks[name]
            py = dfs_states()
            self.assertEqual(c['order'], ''.join(py[-1]['output']))
            self.assertEqual(c['parent'], py_parent(py))
            self.assertEqual(c['tree-depth'],
                             tuple(py[-1]['distance'].get(v, -1) for v in NODES))
            self.assertEqual(c['scans'], 8)

    def test_bfs_list_and_matrix_match_python(self):
        py = bfs_states()
        for name, scans in (('BFS/list', 8), ('BFS/matrix', 20)):
            c = self.blocks[name]
            self.assertEqual(c['order'], ''.join(py[-1]['output']))
            self.assertEqual(c['parent'], py_parent(py))
            self.assertEqual(c['distance-from-A'],
                             tuple(-1 if v not in py[-1]['distance'] else py[-1]['distance'][v]
                                   for v in NODES))
            self.assertEqual(c['scans'], scans)

    def test_descending_order_matches_python(self):
        dfs, bfs = dfs_states(order='desc'), bfs_states(order='desc')
        self.assertEqual(self.blocks['DFS/reverse']['order'], ''.join(dfs[-1]['output']))
        self.assertEqual(self.blocks['DFS/reverse']['parent'], py_parent(dfs))
        self.assertEqual(self.blocks['BFS/reverse']['order'], ''.join(bfs[-1]['output']))
        self.assertEqual(self.blocks['BFS/reverse']['parent'], py_parent(bfs))

    def test_whole_graph_and_homework_expected_states(self):
        c = self.blocks['BFS/all']
        self.assertEqual((c['order'], c['scans'], c['roots']), ('ABCDE', 8, 2))
        self.assertEqual(c['parent'], (-1, 0, 0, 2, -1))
        hw = self.blocks['homework+BFS']
        self.assertEqual((hw['order'], hw['scans'], hw['roots']), ('ABCDE', 10, 1))
        self.assertEqual(hw['parent'], (-1, 0, 0, 2, 3))
        self.assertEqual(hw['distance-from-A'], (0, 1, 1, 2, 3))


if __name__ == '__main__':
    unittest.main()
