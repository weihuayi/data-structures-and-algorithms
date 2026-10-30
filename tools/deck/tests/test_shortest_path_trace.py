"""Shortest-path semantics, independent small-graph oracle, and C cross-check."""
import json
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'deck'))
from shortest_path_trace import (
    MAIN_NODES, MAIN_EDGES, EXERCISE_NODES, EXERCISE_EDGES,
    dijkstra_states, recover_path, floyd_stages,
)


def exact_distances(vertices, edges, source, directed=False):
    """Enumerate simple paths: independent of greedy order or relaxation."""
    adjacency = {v: [] for v in vertices}
    for a, b, w in edges:
        adjacency[a].append((b, w))
        if not directed:
            adjacency[b].append((a, w))
    best = dict.fromkeys(vertices)

    def visit(u, seen, cost):
        if best[u] is None or cost < best[u]:
            best[u] = cost
        for v, w in adjacency[u]:
            if v not in seen:
                visit(v, seen | {v}, cost + w)

    visit(source, {source}, 0)
    return best


class ShortestPathSemanticsTests(unittest.TestCase):
    def test_main_distances_and_real_predecessor_path(self):
        end = dijkstra_states()[-1]
        self.assertEqual(end['distance'], dict(A=0, B=3, C=2, D=4, E=7))
        self.assertEqual(end['order'], tuple('ACBDE'))
        self.assertEqual(recover_path(end, 'E'), tuple('ABDE'))

    def test_confirmation_and_scanning_are_separate(self):
        states = dijkstra_states()
        confirm_b = next(s for s in states if s['phase'] == 'confirm' and s['current'] == 'B')
        end_b = next(s for s in states if s['phase'] == 'round-end' and s['current'] == 'B')
        self.assertIn('B', confirm_b['settled'])
        self.assertEqual((confirm_b['distance']['D'], confirm_b['distance']['E']), (7, None))
        self.assertEqual((end_b['distance']['D'], end_b['distance']['E']), (4, 10))

    def test_selection_boundary_has_correct_settled_labels_and_relaxed_edges(self):
        states = dijkstra_states()
        exact = exact_distances(MAIN_NODES, MAIN_EDGES, 'A')
        for s in states:
            if s['phase'] != 'select':
                continue
            for u in s['settled']:
                self.assertEqual(s['distance'][u], exact[u])
                for a, b, w in MAIN_EDGES:
                    if u not in (a, b):
                        continue
                    v = b if a == u else a
                    self.assertIsNotNone(s['distance'][v])
                    self.assertLessEqual(s['distance'][v], s['distance'][u] + w)
            finite = [s['distance'][v] for v in MAIN_NODES
                      if v not in s['settled'] and s['distance'][v] is not None]
            self.assertEqual(s['distance'][s['current']], min(finite))

    def test_finite_labels_always_have_a_real_path(self):
        weights = {(a, b): w for a, b, w in MAIN_EDGES}
        weights.update({(b, a): w for a, b, w in MAIN_EDGES})
        for s in dijkstra_states():
            for v, distance in s['distance'].items():
                path = recover_path(s, v)
                if distance is None:
                    self.assertIsNone(path)
                else:
                    self.assertEqual(sum(weights[a, b] for a, b in zip(path, path[1:])), distance)

    def test_directed_zero_weight_exercise_and_reverse_query(self):
        end = dijkstra_states(EXERCISE_NODES, EXERCISE_EDGES, 'P', directed=True)[-1]
        self.assertEqual(end['distance'], dict(P=0, Q=3, R=1, S=3))
        self.assertEqual(recover_path(end, 'S'), tuple('PRQS'))
        self.assertEqual([end['distance'][v] for v in end['order']], [0, 1, 3, 3])
        reverse = dijkstra_states(EXERCISE_NODES, EXERCISE_EDGES, 'S', directed=True)[-1]
        self.assertEqual(reverse['phase'], 'unreachable')
        self.assertIsNone(recover_path(reverse, 'P'))
        self.assertEqual(recover_path(reverse, 'S'), ('S',))
        self.assertIsNone(reverse['parent']['S'])
        self.assertEqual(reverse['distance']['S'], 0)

    def test_disconnected_vertices_are_never_confirmed(self):
        edges = tuple(e for e in MAIN_EDGES if e[:2] not in (('B', 'E'), ('D', 'E')))
        end = dijkstra_states(MAIN_NODES, edges)[-1]
        self.assertEqual(end['phase'], 'unreachable')
        self.assertNotIn('E', end['settled'])
        self.assertIsNone(end['distance']['E'])

    def test_equal_routes_record_one_acyclic_path(self):
        edges = (('A', 'B', 0), ('A', 'C', 1), ('B', 'C', 1))
        end = dijkstra_states('ABC', edges)[-1]
        self.assertEqual(end['distance'], dict(A=0, B=0, C=1))
        self.assertIn(recover_path(end, 'C'), (('A', 'C'), ('A', 'B', 'C')))
        self.assertEqual(recover_path(end, 'A'), ('A',))

    def test_floyd_restricted_stage_is_not_the_final_answer(self):
        stages = floyd_stages()
        before, after = stages[3], stages[4]
        self.assertEqual(before['allowed'], tuple('ABC'))
        self.assertEqual((before['distance'][0][4], before['distance'][0][3],
                          before['distance'][3][4]), (10, 4, 3))
        self.assertEqual(after['allowed'], tuple('ABCD'))
        self.assertEqual(after['distance'][0][4], 7)

    def test_floyd_ordering_sensitive_path(self):
        end = floyd_stages('0123', (('0', '2', 1), ('2', '3', 1), ('3', '1', 1)),
                           directed=True)[-1]
        self.assertEqual(end['distance'][0][1], 3)

    def test_small_graphs_against_independent_path_enumeration(self):
        rng = random.Random(14030)
        vertices = tuple('ABCD')
        for directed in (False, True):
            for _ in range(12):
                pairs = ((a, b) for i, a in enumerate(vertices) for j, b in enumerate(vertices)
                         if i != j and (directed or i < j))
                edges = tuple((a, b, rng.randrange(6)) for a, b in pairs if rng.random() < .45)
                all_pairs = floyd_stages(vertices, edges, directed=directed)[-1]['distance']
                for i, source in enumerate(vertices):
                    exact = exact_distances(vertices, edges, source, directed)
                    end = dijkstra_states(vertices, edges, source, directed=directed)[-1]
                    self.assertEqual(end['distance'], exact)
                    self.assertEqual(all_pairs[i], tuple(exact[v] for v in vertices))

    def test_unsupported_weights_and_graphs_are_rejected(self):
        for edges in ((('A', 'B', -1),), (('A', 'B', True),), (('A', 'B', 0.5),),
                      (('A', 'B', float('inf')),), (('A', 'Z', 1),),
                      (('A', 'A', 0),), (('A', 'B', 1), ('B', 'A', 2))):
            with self.assertRaises(ValueError):
                dijkstra_states('AB', edges)


@unittest.skipUnless(shutil.which('gcc'), 'gcc required for C/Python cross-check')
class ShortestPathCCrossCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        exe = Path(cls.tmp.name) / 'd014'
        subprocess.run(['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        str(ROOT / 'course/decks/d014-shortest-path/code/shortest_path_demo.c'),
                        '-o', str(exe)], check=True, capture_output=True, text=True)
        raw = subprocess.run([str(exe), '--json'], check=True, capture_output=True, text=True).stdout
        cls.cases = {c['case']: c for c in json.loads(raw)}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_classroom_cases_match_trace_paths_and_floyd(self):
        cases = {
            'main': (MAIN_NODES, MAIN_EDGES, 'A', False),
            'exercise': (EXERCISE_NODES, EXERCISE_EDGES, 'P', True),
            'reverse': (EXERCISE_NODES, EXERCISE_EDGES, 'S', True),
            'unreachable': (MAIN_NODES, tuple(e for e in MAIN_EDGES
                            if e[:2] not in (('B', 'E'), ('D', 'E'))), 'A', False),
            'zero_tie': ('ABC', (('A', 'B', 0), ('A', 'C', 1), ('B', 'C', 1)), 'A', False),
            'homework': (MAIN_NODES, tuple((a, b, 0 if (a, b) == ('C', 'D') else w)
                                          for a, b, w in MAIN_EDGES), 'A', False),
        }
        for name, (vertices, edges, source, directed) in cases.items():
            with self.subTest(case=name):
                vertices = tuple(vertices)
                end = dijkstra_states(vertices, edges, source, directed=directed)[-1]
                c = self.cases[name]
                self.assertEqual(c['distance'], [end['distance'][v] for v in vertices])
                self.assertEqual(c['order'], list(end['order']))
                self.assertEqual(c['settled'], [v in end['settled'] for v in vertices])
                expected = [recover_path(end, v) for v in vertices]
                self.assertEqual(c['paths'], [list(p) if p is not None else None for p in expected])
                self.assertEqual(c['floyd'], [list(row) for row in
                                 floyd_stages(vertices, edges, directed=directed)[-1]['distance']])
                self.assertEqual(c['distance'], list(exact_distances(vertices, edges, source, directed).values()))

    def test_negative_weight_example_is_rejected(self):
        self.assertTrue(self.cases['negative']['rejected'])


if __name__ == '__main__':
    unittest.main()
