"""Independent regression for full-graph search forests and SCC boundaries."""
import unittest
from collections import deque

# B -> A.  A is a sink, B is a source.
ADJ = {'A': (), 'B': ('A',)}
ARCS = {('B', 'A')}


def full_traverse(order, method):
    """One visited set for the whole outer scan; never reset between roots."""
    visited, roots, trees, parent, tree_edges, visits = set(), [], [], {}, [], []

    def mark(vertex, source):
        visited.add(vertex)
        visits.append(vertex)
        parent[vertex] = source
        if source is not None:
            tree_edges.append((source, vertex))

    for root in order:
        if root in visited:
            continue
        roots.append(root)
        tree = []
        mark(root, None)
        if method == 'dfs':
            def walk(vertex):
                tree.append(vertex)
                for neighbor in ADJ[vertex]:
                    if neighbor not in visited:
                        mark(neighbor, vertex)
                        walk(neighbor)
            walk(root)
        elif method == 'bfs':
            queue = deque([root])
            while queue:
                vertex = queue.popleft()
                tree.append(vertex)
                for neighbor in ADJ[vertex]:
                    if neighbor not in visited:
                        mark(neighbor, vertex)
                        queue.append(neighbor)
        else:
            raise ValueError(method)
        trees.append(set(tree))
    return {'visited': visited, 'roots': roots, 'trees': trees,
            'parent': parent, 'tree_edges': tree_edges, 'visits': visits}


def reachable(start):
    seen, stack = {start}, [start]
    while stack:
        vertex = stack.pop()
        for neighbor in ADJ[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen


def sccs():
    nodes = tuple(ADJ)
    return {frozenset(v for v in nodes if v in reachable(u) and u in reachable(v))
            for u in nodes}


class FullForestTests(unittest.TestCase):
    def check_forest(self, result, roots, trees):
        self.assertEqual(result['roots'], roots)
        self.assertEqual(result['trees'], trees)
        self.assertEqual(result['visited'], {'A', 'B'})
        self.assertEqual(sorted(result['visits']), ['A', 'B'])
        self.assertEqual(len(result['visits']), 2)
        self.assertEqual(len(result['tree_edges']), 2 - len(roots))
        self.assertTrue(all(edge in ARCS for edge in result['tree_edges']))
        self.assertTrue(all(not (a & b) for i, a in enumerate(trees) for b in trees[i + 1:]))
        self.assertEqual(set().union(*trees), {'A', 'B'})

    def test_outer_order_a_then_b_resets_nothing(self):
        for method in ('dfs', 'bfs'):
            result = full_traverse(('A', 'B'), method)
            self.check_forest(result, ['A', 'B'], [{'A'}, {'B'}])
            self.assertEqual(result['parent'], {'A': None, 'B': None})
            self.assertEqual(result['tree_edges'], [])

    def test_outer_order_b_then_a_forms_one_tree(self):
        for method in ('dfs', 'bfs'):
            result = full_traverse(('B', 'A'), method)
            self.check_forest(result, ['B'], [{'B', 'A'}])
            self.assertEqual(result['parent'], {'A': 'B', 'B': None})
            self.assertEqual(result['tree_edges'], [('B', 'A')])

    def test_parent_arcs_exist_and_forest_has_no_cycle(self):
        for order in (('A', 'B'), ('B', 'A')):
            result = full_traverse(order, 'bfs')
            for vertex, source in result['parent'].items():
                if source is not None:
                    self.assertIn((source, vertex), ARCS)
                seen, cursor = set(), vertex
                while cursor is not None:
                    self.assertNotIn(cursor, seen)
                    seen.add(cursor)
                    cursor = result['parent'].get(cursor)

    def test_scc_result_is_independent_of_outer_order(self):
        expected = {frozenset({'A'}), frozenset({'B'})}
        self.assertEqual(sccs(), expected)
        for order in (('A', 'B'), ('B', 'A')):
            self.assertEqual(sccs(), expected)

    def test_every_vertex_is_visited_exactly_once_per_full_traverse(self):
        for order in (('A', 'B'), ('B', 'A')):
            for method in ('dfs', 'bfs'):
                result = full_traverse(order, method)
                self.assertEqual(len(result['visits']), len(set(result['visits'])))
                self.assertEqual(set(result['visits']), {'A', 'B'})


if __name__ == '__main__':
    unittest.main()
