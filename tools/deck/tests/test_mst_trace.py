"""D013 Prim/Kruskal/DSU state semantics and controlled players."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mst_trace import (EXERCISE_EDGES, EXERCISE_NODES, MAIN_EDGES, MAIN_NODES,
                       kruskal_player, kruskal_states, prim_player, prim_states)


def norm(a, b, w):
    return (a, b, w) if a < b else (b, a, w)


class PrimTests(unittest.TestCase):
    def test_main_prim_state_and_total(self):
        states = prim_states()
        final = states[-1]
        self.assertEqual(final['total_weight'], 12)
        self.assertEqual(final['components'], 1)
        self.assertEqual(set(final['selected_edges']),
                         {('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 3), ('C', 'E', 6)})
        self.assertEqual(final['selected_vertices'], ('A', 'B', 'C', 'D', 'E'))
        self.assertEqual(len(states), 9)

    def test_each_candidate_is_lightest_crossing_edge(self):
        for state in prim_states():
            edge = state['current_edge']
            if edge is None:
                continue
            a, b, w = edge
            self.assertIn(a, state['selected_vertices'])
            self.assertNotIn(b, state['selected_vertices'])
            self.assertTrue(state['has_key'][b])
            self.assertEqual(state['key'][b], w)
            self.assertEqual(state['parent'][b], a)
            self.assertNotIn(edge, state['selected_edges'])
            for v in state['key']:
                if v not in state['selected_vertices']:
                    self.assertLessEqual(w, state['key'][v])

    def test_accept_updates_region_and_total_without_cycles(self):
        for state in prim_states():
            self.assertEqual(len(state['selected_edges']),
                             len(state['selected_vertices']) - state['components'])
            for a, b, w in state['selected_edges']:
                self.assertIn((a, b, w), [norm(*e) for e in MAIN_EDGES])

    def test_prim_from_c_changes_order_not_total(self):
        states = prim_states(start='C')
        self.assertEqual(states[-1]['total_weight'], 12)
        self.assertEqual(states[-1]['selected_edges'][0], ('B', 'C', 2))
        self.assertEqual(states[-1]['selected_edges'][1], ('A', 'B', 1))

    def test_prim_restarts_on_disconnected_graph(self):
        edges = [e for e in MAIN_EDGES if e[:2] not in {('C', 'E'), ('D', 'E')}]
        final = prim_states(edges=edges)[-1]
        self.assertEqual(final['total_weight'], 6)
        self.assertEqual(final['components'], 2)
        self.assertEqual(len(final['selected_edges']), 3)
        self.assertIn('E', final['selected_vertices'])
        self.assertEqual(final['selected_edges'][-1], ('C', 'D', 3))

    def test_tie_zero_and_negative_variants(self):
        ties = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 5),
                ('C', 'D', 3), ('C', 'E', 7), ('D', 'E', 7)]
        self.assertEqual(prim_states(edges=ties)[-1]['total_weight'], 13)
        zero = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 5),
                ('C', 'D', 3), ('C', 'E', 6), ('D', 'E', 0)]
        self.assertEqual(prim_states(edges=zero)[-1]['total_weight'], 6)
        neg = [('A', 'B', -2), ('B', 'C', 0), ('A', 'C', 5)]
        n = {'A': MAIN_NODES['A'], 'B': MAIN_NODES['B'], 'C': MAIN_NODES['C']}
        self.assertEqual(prim_states(edges=neg, nodes=n)[-1]['total_weight'], -2)


class KruskalTests(unittest.TestCase):
    def test_sorted_order_and_final_result(self):
        states = kruskal_states()
        self.assertEqual(states[0]['sorted_edges'][:3],
                         (('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 3)))
        final = states[-1]
        self.assertEqual(final['total_weight'], 12)
        self.assertEqual(set(final['selected_edges']),
                         {('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 3), ('C', 'E', 6)})
        self.assertEqual(set(final['rejected_edges']),
                         {('A', 'C', 4), ('B', 'D', 5), ('D', 'E', 7)})
        self.assertEqual(final['components'], (('A', 'B', 'C', 'D', 'E'),))

    def test_accept_reject_relations_and_components(self):
        states = kruskal_states()
        pairs = [(states[i], states[i + 1]) for i in range(len(states) - 1)
                 if states[i]['decision'] is None and states[i]['candidate_edge']]
        self.assertEqual(len(pairs), 7)
        for pre, post in pairs:
            a, b, w = pre['candidate_edge']
            same = any(a in group and b in group for group in pre['components'])
            if post['decision'] == 'accept':
                self.assertFalse(same)
                self.assertIn((a, b, w), post['selected_edges'])
                self.assertEqual(post['total_weight'], pre['total_weight'] + w)
            else:
                self.assertTrue(same)
                self.assertEqual(post['selected_edges'], pre['selected_edges'])
                self.assertEqual(post['total_weight'], pre['total_weight'])
            self.assertIn((a, b, w), post['rejected_edges'] + post['selected_edges'])

    def test_dsu_parent_groups_match_components(self):
        for state in kruskal_states():
            for group in state['components']:
                roots = {state['dsu_parent'][v] for v in group}
                self.assertEqual(len(roots), 1)
            self.assertEqual(set().union(*map(set, state['components'])),
                             set(MAIN_NODES))

    def test_dsu_groups_and_path_compression_do_not_change_partition(self):
        states = kruskal_states()
        before = states[-1]['components']
        after = states[-1]['dsu_parent']
        self.assertEqual({v for v in after}, set(MAIN_NODES))
        self.assertEqual(before, (('A', 'B', 'C', 'D', 'E'),))

    def test_kruskal_tie_zero_negative_variants(self):
        ties = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 5),
                ('C', 'D', 3), ('C', 'E', 7), ('D', 'E', 7)]
        self.assertEqual(kruskal_states(ties)[-1]['total_weight'], 13)
        zero = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2), ('B', 'D', 5),
                ('C', 'D', 3), ('C', 'E', 6), ('D', 'E', 0)]
        z = kruskal_states(zero)[-1]
        self.assertEqual(z['total_weight'], 6)
        self.assertIn(('D', 'E', 0), z['selected_edges'])
        neg = [('A', 'B', -2), ('B', 'C', 0), ('A', 'C', 5)]
        n = {'A': MAIN_NODES['A'], 'B': MAIN_NODES['B'], 'C': MAIN_NODES['C']}
        self.assertEqual(kruskal_states(neg, n)[-1]['total_weight'], -2)

    def test_exercise_accepts_pr_qr_qs_rejects_pq_rs(self):
        final = kruskal_states(EXERCISE_EDGES, EXERCISE_NODES)[-1]
        self.assertEqual(final['total_weight'], 7)
        self.assertEqual(set(final['selected_edges']),
                         {('P', 'R', 1), ('Q', 'R', 2), ('Q', 'S', 4)})
        self.assertEqual(set(final['rejected_edges']), {('P', 'Q', 3), ('R', 'S', 5)})
        self.assertIn(('P', 'Q', 3), final['rejected_edges'])
        self.assertEqual(final['components'], (('P', 'Q', 'R', 'S'),))


class PlayerTests(unittest.TestCase):
    def test_players_have_controls_and_all_states(self):
        for html, panels in ((prim_player(), 9), (kruskal_player(), 16)):
            self.assertIn('data-tree-player', html)
            self.assertIn('上一步', html)
            self.assertIn('下一步', html)
            self.assertIn('重置', html)
            self.assertEqual(html.count('tree-step-panel'), panels)
            if panels == 9:
                self.assertIn('graph-node-current', html)
            else:
                self.assertIn('graph-edge marked', html)
            self.assertNotIn('seen', html)


if __name__ == '__main__':
    unittest.main()
