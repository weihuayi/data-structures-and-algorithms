from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from huffman_trace import merge_states, decode_states, selection_scan_states

class HuffmanTraceTests(unittest.TestCase):
    def test_record_scans_count_exclusion_and_preserve_snapshots(self):
        states = selection_scan_states([8, 4, 2, 2])
        self.assertEqual(len(states), 11)
        viewed = [s for s in states if s['scan'] and s['current'] is not None]
        self.assertEqual([s['current'] for s in viewed], list(range(4)) * 2)
        self.assertEqual([s['inspections'] for s in viewed], list(range(1, 9)))
        self.assertEqual([s['best'] for s in viewed], [0, 1, 2, 2, 0, 1, 1, 3])
        excluded = viewed[6]
        self.assertEqual((excluded['exclude'], excluded['current']), (2, 2))
        self.assertEqual(excluded['records'][2]['parent'], None)
        final = states[-1]
        self.assertEqual(final['selected'], [2, 3])
        self.assertEqual(final['inspections'], 8)
        self.assertEqual([r['parent'] for r in final['records']], [None, None, 4, 4, None])
        self.assertEqual(final['records'][4], dict(symbol='CD', weight=4, parent=None))
        self.assertEqual(len(states[0]['records']), 4)
        self.assertTrue(all(r['parent'] is None for r in states[0]['records']))

    def test_record_scan_ties_and_invalid_input(self):
        for weights in ([1, 1], [4, 4, 4, 4], [6, 3, 2, 1]):
            end = selection_scan_states(weights)[-1]
            self.assertEqual(end['selected'], sorted(range(len(weights)), key=lambda i: (weights[i], i))[:2])
            self.assertEqual(end['inspections'], 2 * len(weights))
        for weights in ([], [1], [1, 0], [1, -1], [1, 2.5]):
            with self.assertRaises(ValueError):
                selection_scan_states(weights)

    def test_merges_preserve_subtrees_and_choose_smallest_roots(self):
        for weights,total in [([8,4,2,2],28),([6,3,2,1],21),([5,2,1,1],15),([7,3,2,1],22)]:
            states=merge_states(weights)
            self.assertEqual(states[-1]['cost'],total)
            for i in (1,3,5):
                before,after=states[i:i+2]
                a,b=before['selected']
                self.assertEqual([a,b],sorted(before['roots'],key=lambda k:(before['nodes'][k]['weight'],k))[:2])
                new=after['selected'][0]
                self.assertEqual((after['nodes'][new]['left'],after['nodes'][new]['right']),(a,b))
                self.assertEqual(set(after['roots']),(set(before['roots'])-{a,b})|{new})
                self.assertEqual(after['cost']-before['cost'],after['nodes'][new]['weight'])

    def test_decode_output_only_at_leaves_and_return_to_root(self):
        end=merge_states([8,4,2,2])[-1]; nodes=end['nodes']; root=end['roots'][0]
        states=decode_states(nodes,root,'010110111')
        self.assertEqual(states[-1]['output'],'ABCD')
        self.assertEqual(states[-1]['current'],root)
        changes=[]
        for a,b in zip(states,states[1:]):
            if a['output']!=b['output']:
                self.assertTrue(nodes[b['current']]['symbol'])
                self.assertEqual(a['read'],b['read'])
                changes.append(b['read'])
        self.assertEqual(changes,[1,3,6,9])
        bad=decode_states(nodes,root,'11')[-1]
        self.assertEqual(bad['output'],'')
        self.assertNotEqual(bad['current'],root)
        self.assertIn('不完整',bad['action'])
        with self.assertRaises(ValueError): decode_states(nodes,root,'2')
        for weights in ([],[1],[1,0]):
            with self.assertRaises(ValueError): merge_states(weights)
