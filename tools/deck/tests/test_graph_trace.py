"""Graph-search state semantics independent of the DOM."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graph_trace import ADJ, EDGES, bfs_player, bfs_states, dfs_player, dfs_states


class GraphTraceTests(unittest.TestCase):
    def test_adjacency_is_consistent_with_the_main_graph(self):
        self.assertEqual(ADJ['A'], ['B', 'C'])
        self.assertEqual(ADJ['B'], ['A', 'C'])
        self.assertEqual(ADJ['C'], ['A', 'B', 'D'])
        self.assertEqual(ADJ['D'], ['C'])
        self.assertEqual(ADJ['E'], [])
        for vertex, neighbors in ADJ.items():
            for neighbor in neighbors:
                self.assertIn((vertex, neighbor), EDGES + [(b, a) for a, b in EDGES])

    def test_dfs_visit_order_parent_and_tree_edges(self):
        final = dfs_states()[-1]
        self.assertEqual(final['output'], ('A', 'B', 'C', 'D'))
        self.assertEqual(final['parent'], {'A': None, 'B': 'A', 'C': 'B', 'D': 'C'})
        self.assertEqual(final['tree_edges'], (('A', 'B'), ('B', 'C'), ('C', 'D')))
        self.assertEqual(final['distance'], {'A': 0, 'B': 1, 'C': 2, 'D': 3})

    def test_dfs_descending_order_changes_sequence_but_not_reachability(self):
        final = dfs_states(order='desc')[-1]
        self.assertEqual(final['output'], ('A', 'C', 'D', 'B'))
        self.assertEqual(final['parent'], {'A': None, 'B': 'C', 'C': 'A', 'D': 'C'})
        self.assertEqual(set(final['visited']), {'A', 'B', 'C', 'D'})

    def test_dfs_cursor_advances_after_skipping_a_visited_neighbor(self):
        states = dfs_states()
        target = next(s for s in states if s['action'].startswith('B 检查位置 0 的 A'))
        top = target['stack'][-1]
        self.assertEqual(top, {'vertex': 'B', 'next': 1})
        self.assertEqual(target['current'], 'B')
        self.assertNotIn('E', target['visited'])

    def test_dfs_current_matches_stack_top_and_return_restores_parent(self):
        states = dfs_states()
        for state in states:
            expected = state['stack'][-1]['vertex'] if state['stack'] else None
            self.assertEqual(state['current'], expected)
        back = next(s for s in states if s['action'].startswith('C 的邻接项已全部检查，弹出帧；回到 B'))
        self.assertEqual(back['current'], 'B')
        self.assertEqual(back['stack'][-1], {'vertex': 'B', 'next': 2})

    def test_every_dfs_frame_cursor_is_monotonic(self):
        states = dfs_states()
        last = {}
        for state in states:
            for frame in state['stack']:
                vertex, pos = frame['vertex'], frame['next']
                self.assertGreaterEqual(pos, last.get(vertex, 0))
                last[vertex] = pos
                self.assertLessEqual(pos, len(ADJ[vertex]))

    def test_bfs_first_visit_marks_and_enqueues(self):
        states = bfs_states()
        after_a = next(s for s in states if '检查位置 1 的 C' in s['action'])
        self.assertEqual(after_a['queue'], ('B', 'C'))
        self.assertEqual(after_a['processing'], 'A')
        self.assertEqual(after_a['examined'], 'C')
        self.assertEqual(after_a['current'], 'A')
        self.assertEqual(after_a['output'], ('A', 'B', 'C'))
        self.assertEqual(after_a['distance'], {'A': 0, 'B': 1, 'C': 1})
        final = states[-1]
        self.assertEqual(final['output'], ('A', 'B', 'C', 'D'))
        self.assertEqual(final['parent'], {'A': None, 'B': 'A', 'C': 'A', 'D': 'C'})
        self.assertEqual(final['distance'], {'A': 0, 'B': 1, 'C': 1, 'D': 2})
        self.assertEqual(final['tree_edges'], (('A', 'B'), ('A', 'C'), ('C', 'D')))

    def test_bfs_processing_vertex_and_examined_neighbor_are_distinct(self):
        states = bfs_states()
        a_b = next(s for s in states if '正在处理 A，检查位置 0 的 B' in s['action'])
        self.assertEqual((a_b['processing'], a_b['examined'], a_b['current']), ('A', 'B', 'A'))
        a_c = next(s for s in states if '正在处理 A，检查位置 1 的 C' in s['action'])
        self.assertEqual((a_c['processing'], a_c['examined'], a_c['current']), ('A', 'C', 'A'))
        b_dequeue = next(s for s in states if s['action'].startswith('B 出队'))
        self.assertEqual((b_dequeue['processing'], b_dequeue['examined']), ('B', None))
        self.assertEqual(b_dequeue['queue'], ('C',))
        b_c = next(s for s in states if '正在处理 B，检查位置 1 的 C' in s['action'])
        self.assertEqual((b_c['processing'], b_c['examined']), ('B', 'C'))
        self.assertEqual(b_c['queue'], ('C',))
        c_dequeue = next(s for s in states if s['action'].startswith('C 出队'))
        self.assertEqual(c_dequeue['processing'], 'C')
        self.assertEqual(c_dequeue['queue'], ())

    def test_bfs_descending_order_changes_sequence_not_distance(self):
        final = bfs_states(order='desc')[-1]
        self.assertEqual(final['output'], ('A', 'C', 'B', 'D'))
        self.assertEqual(final['distance'], {'A': 0, 'B': 1, 'C': 1, 'D': 2})
        self.assertEqual(set(final['visited']), {'A', 'B', 'C', 'D'})

    def test_bfs_invariants_hold_in_every_state(self):
        for state in bfs_states():
            self.assertEqual(state['output'], state['visited'])
            self.assertEqual(len(state['visited']), len(set(state['visited'])))
            self.assertTrue(set(state['queue']) <= set(state['visited']))
            for vertex in state['visited']:
                self.assertIn(vertex, state['parent'])
                if state['parent'][vertex] is None:
                    self.assertEqual(state['distance'][vertex], 0)
                else:
                    self.assertEqual(state['distance'][vertex],
                                     state['distance'][state['parent'][vertex]] + 1)

    def test_tree_edges_agree_with_parent_in_every_state(self):
        for states in (dfs_states(), bfs_states(), dfs_states(order='desc'), bfs_states(order='desc')):
            for state in states:
                for source, child in state['tree_edges']:
                    self.assertEqual(state['parent'][child], source)

    def test_no_vertex_is_visited_twice(self):
        for states in (dfs_states(), bfs_states(), dfs_states(order='desc'), bfs_states(order='desc')):
            previous = ()
            for state in states:
                self.assertGreaterEqual(len(state['visited']), len(previous))
                self.assertEqual(len(state['visited']), len(set(state['visited'])))
                previous = state['visited']

    def test_players_have_manual_controls_and_all_states(self):
        for html, label in ((dfs_player('recursive'), 'DFS'), (dfs_player('stack'), 'DFS'), (bfs_player(), 'BFS')):
            self.assertIn('data-tree-player', html)
            self.assertIn('上一步', html)
            self.assertIn('下一步', html)
            self.assertIn('重置', html)
            self.assertEqual(html.count('tree-step-panel'), 15)
            self.assertIn('graph-node-current', html)
            self.assertNotIn('seen', html)
        self.assertIn('graph-node-examined', bfs_player())

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            dfs_states(start='Z')
        with self.assertRaises(ValueError):
            bfs_states(order='up')
        with self.assertRaises(ValueError):
            dfs_player(mode='queue')
