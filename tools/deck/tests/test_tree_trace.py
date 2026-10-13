"""State invariants checked independently of the HTML presentation."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tree_trace import traversal_states, recovery_states


class TraceTests(unittest.TestCase):
    def setUp(self):
        self.children = {'A': ('B','C'), 'B': (None,'D'), 'C': ('E',None), 'D': (None,None), 'E': (None,None)}

    def test_main_outputs_and_visit_events(self):
        for mode, expected in [('pre','ABDCE'),('in','BDAEC'),('post','DBECA'),('stack','ABDCE'),('queue','ABCDE')]:
            states=traversal_states(self.children,'A',mode)
            self.assertEqual(''.join(states[-1]['output']),expected)
            previous=[]
            for s in states:
                self.assertEqual(len(s['visited']),len(set(s['visited'])))
                if s['output'] != previous:
                    self.assertTrue(s['action'].startswith('访问 '))
                    self.assertEqual(s['output'][:-1],previous)
                previous=s['output']
                for key in s['done']:
                    def descendants(k):
                        return [] if k is None else [k]+sum((descendants(c) for c in self.children[k]),[])
                    self.assertTrue(set(descendants(key)) <= set(s['visited']))
            self.assertEqual(states[-1]['pending'],[])

    def test_container_operations(self):
        for mode in ('stack','queue'):
            states=traversal_states(self.children,'A',mode)
            self.assertEqual(states[1]['pending'],['A'])
            pending=['A']
            for s in states[2:-1]:
                action=s['action']
                if '出栈' in action or '出队' in action:
                    expected=pending.pop() if mode=='stack' else pending.pop(0)
                    self.assertEqual(s['current'],expected)
                elif '入栈' in action or '入队' in action:
                    parent=s['current']; child=self.children[parent][1 if '右孩子' in action else 0]
                    pending.append(child)
                self.assertEqual(s['pending'],pending)

    def test_recovery_and_rejection(self):
        for pre,ino,links in [('ABDCE','BDAEC',[('A','B'),('B','D'),('A','C'),('C','E')]),('PQSRT','SQPRT',[('P','Q'),('Q','S'),('P','R'),('R','T')])]:
            states=recovery_states(pre,ino)
            self.assertEqual(states[0]['built'],[])
            self.assertEqual(states[-1]['links'],links)
            self.assertEqual(states[-1]['built'],list(pre))
            for a,b in zip(states,states[1:]):
                self.assertLessEqual(len(b['built'])-len(a['built']),1)
        for pre,ino in [('ABC','CAB'),('AA','AA'),('AB','A'),('AB','AC')]:
            with self.assertRaises(ValueError): recovery_states(pre,ino)

    def test_empty_and_one_sided_trees(self):
        for mode in ('pre','in','post','stack','queue'):
            self.assertEqual(traversal_states({},None,mode)[-1]['output'],[])
            self.assertEqual(traversal_states({'A':(None,None)},'A',mode)[-1]['output'],['A'])
        self.assertEqual(recovery_states('','')[-1]['built'],[])
        for children,ino in [({'A':('B',None),'B':(None,None)},'BA'),({'A':(None,'B'),'B':(None,None)},'AB')]:
            self.assertEqual(''.join(traversal_states(children,'A','in')[-1]['output']),ino)
            self.assertEqual(recovery_states('AB',ino)[-1]['links'],[('A','B')])

if __name__=='__main__': unittest.main()
