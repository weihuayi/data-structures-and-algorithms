"""D013 Prim/Kruskal/DSU state semantics and controlled players."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mst_trace import (EXERCISE_EDGES, EXERCISE_NODES, MAIN_EDGES, MAIN_NODES, _DSU,
                       dsu_diagram, kruskal_player, kruskal_states, path_compression_demo,
                       prim_player, prim_states)


def norm(a, b, w):
    return (a, b, w) if a < b else (b, a, w)


def walk_root(parent, vertex):
    seen = set()
    while parent[vertex] != vertex:
        if vertex in seen:
            raise AssertionError('parent cycle')
        seen.add(vertex)
        vertex = parent[vertex]
    return vertex


def deep_dsu():
    """Legal non-flat state: unions AB, CD, then BC."""
    dsu = _DSU(('A', 'B', 'C', 'D'))
    for a, b in (('A', 'B'), ('C', 'D'), ('B', 'C')):
        dsu.union(a, b)
    return dsu


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

    def test_key_updates_record_old_and_new_entries_without_mutating_snapshots(self):
        states = prim_states()
        self.assertEqual(states[2]['key_changes'],
                         {'C': (('A', 4), ('B', 2)), 'D': (None, ('B', 5))})
        self.assertEqual(states[0]['key']['C'], 4)
        self.assertEqual(states[2]['key']['C'], 2)
        for pre, post in zip(states, states[1:]):
            for v, (old, new) in post['key_changes'].items():
                self.assertEqual(new, (post['parent'][v], post['key'][v]))
                if old:
                    self.assertEqual(old, (pre['parent'][v], pre['key'][v]))
                    self.assertLess(new[1], old[1])
                else:
                    self.assertFalse(pre['has_key'].get(v, False))
        self.assertEqual(states[3]['key_changes'], {})  # candidate step does not update

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
        # Completion by accepting an edge in the final component is still MSF.
        final = prim_states(edges=[('B', 'C', 0), ('D', 'E', 1)])[-1]
        self.assertEqual(final['components'], 3)
        self.assertEqual(final['total_weight'], 1)
        self.assertIn('MSF 完成', final['action'])

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
    def test_completion_is_marked_before_remaining_edges_are_checked(self):
        states = kruskal_states()
        complete = next(i for i, s in enumerate(states) if s['result_complete'])
        self.assertEqual(states[complete]['candidate_edge'], ('C', 'E', 6))
        self.assertEqual(states[complete]['decision'], 'accept')
        self.assertIn('端点 C、E', states[complete]['reason'])
        self.assertNotIn('端点 A、E', states[complete]['reason'])
        self.assertEqual(len(states[complete]['selected_edges']), len(MAIN_NODES) - 1)
        for state in states[complete:]:
            self.assertTrue(state['result_complete'])
            self.assertEqual(state['selected_edges'], states[complete]['selected_edges'])
            self.assertEqual(state['total_weight'], 12)
        self.assertEqual(states[complete + 1]['candidate_edge'], ('D', 'E', 7))
        disconnected = [e for e in MAIN_EDGES if 'E' not in e[:2]]
        forest = kruskal_states(disconnected)
        self.assertFalse(any(s['result_complete'] for s in forest))
        self.assertIn('MSF', forest[-1]['action'])
        self.assertEqual(len(forest[-1]['components']), 2)

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

    def test_dsu_parent_groups_match_components_by_parent_walk(self):
        for state in kruskal_states():
            parent = state['dsu_parent']
            roots = {v: walk_root(parent, v) for v in parent}
            covered = set()
            for group in state['components']:
                group_roots = {roots[v] for v in group}
                self.assertEqual(len(group_roots), 1)
                root = next(iter(group_roots))
                self.assertEqual({v for v in parent if roots[v] == root}, set(group))
                covered |= set(group)
            self.assertEqual(covered, set(MAIN_NODES))

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


class DSUSnapshotTests(unittest.TestCase):
    def test_parent_snapshot_is_raw_copy_without_compression(self):
        dsu = deep_dsu()
        expected = {'A': 'A', 'B': 'A', 'C': 'A', 'D': 'C'}
        self.assertEqual(dsu.parent, expected)
        snapshot = dsu.parents()
        self.assertEqual(dsu.parent, expected)
        self.assertEqual(snapshot, expected)
        self.assertEqual(snapshot['D'], 'C')
        self.assertIsNot(snapshot, dsu.parent)

    def test_components_snapshot_is_read_only(self):
        dsu = deep_dsu()
        before = dict(dsu.parent)
        self.assertEqual(dsu.components(), (('A', 'B', 'C', 'D'),))
        self.assertEqual(dsu.parent, before)
        self.assertEqual(dsu.parent['D'], 'C')
        dsu.components()
        self.assertEqual(dsu.parent, before)

    def test_find_compresses_and_preserves_partition(self):
        dsu = deep_dsu()
        groups = dsu.components()
        self.assertEqual(dsu.find('D'), 'A')
        self.assertEqual(dsu.parent['D'], 'A')
        self.assertEqual(dsu.components(), groups)
        self.assertEqual(dsu.parent['C'], 'A')

    def test_distinct_parent_structures_encode_same_partition(self):
        deep = deep_dsu()
        star = _DSU(('A', 'B', 'C', 'D'))
        star.parent.update({'B': 'A', 'C': 'A', 'D': 'A'})
        self.assertEqual(deep.components(), star.components())
        self.assertNotEqual(deep.parents(), star.parents())

    def test_path_compression_demo_snapshots(self):
        demo = path_compression_demo()
        self.assertEqual(demo['before']['parent']['D'], 'C')
        self.assertEqual(demo['after']['parent']['D'], 'A')
        self.assertEqual(demo['before']['parent']['C'], 'A')
        self.assertEqual(demo['before']['components'], demo['after']['components'])
        self.assertEqual(demo['before']['components'], (('A', 'B', 'C', 'D'),))
        self.assertEqual(demo['representative'], 'A')

    def test_dsu_diagram_draws_real_parent_links(self):
        parent = {'A': 'A', 'B': 'A', 'C': 'A', 'D': 'C'}
        positions = {'A': (260, 45), 'B': (80, 140), 'C': (260, 140), 'D': (430, 220)}
        html = dsu_diagram(parent, positions, caption='快照', root='A')
        self.assertIn('data-edge="D-C"', html)
        self.assertIn('data-edge="C-A"', html)
        self.assertIn('p[D]=C', html)
        self.assertNotIn('data-edge="D-A"', html)


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
                self.assertIn('已选边集合', html)
            else:
                self.assertIn('graph-edge marked', html)
            self.assertNotIn('seen', html)
            self.assertIn(r'\(F=\varnothing\)', html)
            self.assertIn(r'\(F=\{AB,BC,CD,CE\}\)', html)
            self.assertNotIn('已选森林 F', html)

    def test_kruskal_player_defers_internal_representation(self):
        html = kruskal_player()
        self.assertIn('当前分组', html)
        self.assertIn('已选边集合', html)
        self.assertIn('保留全部顶点，只看已选边', html)
        self.assertIn('每棵树对应一个分组', html)
        self.assertNotIn('DSU parent', html)
        self.assertNotIn('dsu_parent', html)
        self.assertNotIn('父指针', html)


if __name__ == '__main__':
    unittest.main()
