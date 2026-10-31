"""D015: independent path oracle, precedence equivalence, trace and C checks."""
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/deck'))
from dependency_trace import (TASKS, AOV_NODES, AOV_EDGES, MAIN_ACTIVITIES,
    EXERCISE_ACTIVITIES, topological_states, critical_path)


def all_paths(vertices, activities, source, sink):
    """Only bounded test inputs: enumerate routes independently of recurrence."""
    def walk(u, names, length):
        if u == sink: return [(names, length)]
        return [item for a, x, v, w in activities if x == u
                for item in walk(v, names + (a,), length + w)]
    return walk(source, (), 0)


class DependencyTests(unittest.TestCase):
    def test_microstates_count_unreleased_arcs_and_keep_input(self):
        original = tuple(AOV_EDGES)
        for s in topological_states():
            for v in AOV_NODES:
                self.assertEqual(s['degree'][v], sum(b == v and (a,b) not in s['removed'] for a,b in AOV_EDGES))
            self.assertEqual(len(s['ready']), len(set(s['ready'])))
            self.assertEqual(set(s['ready']), {v for v in AOV_NODES if v not in s['order'] and s['degree'][v] == 0})
            for u,v in s['removed']: self.assertIn(u, s['order'])
            if s['phase'] in {'init','boundary','done'}:
                for v in AOV_NODES:
                    self.assertEqual(s['degree'][v], sum(b == v and a not in s['order'] for a,b in AOV_EDGES))
        self.assertEqual(AOV_EDGES, original)
        read_b = next(s for s in topological_states() if s['phase']=='read' and s['edge']==('B','D'))
        released = next(s for s in topological_states() if s['phase']=='release' and s['edge']==('B','D'))
        self.assertEqual((read_b['degree']['D'],released['degree']['D']), (2,1))
        self.assertNotIn('D',released['ready'])

    def test_valid_orders_and_isolated_vertices(self):
        for strategy in ('stack','queue'):
            s=topological_states(tuple(AOV_NODES)+('G',),AOV_EDGES,strategy=strategy)[-1]
            self.assertEqual(s['phase'],'done');self.assertEqual(len(s['order']),7)
            for u,v in AOV_EDGES:self.assertLess(s['order'].index(u),s['order'].index(v))
        self.assertEqual(topological_states()[-1]['order'],tuple('BAEDCF'))

    def test_remaining_vertices_are_not_all_cycle_members(self):
        end=topological_states(AOV_NODES,AOV_EDGES+(('E','A'),))[-1]
        self.assertEqual(end['phase'],'blocked');self.assertEqual(end['order'],('B',))
        self.assertEqual(set(AOV_NODES)-set(end['order']),set('ACDEF'))
        self.assertEqual(topological_states(('X',),(('X','X'),))[-1]['phase'],'blocked')

    def test_aov_aoe_have_identical_activity_precedence(self):
        def reaches(start,target,arcs):
            todo=[start];seen=set()
            while todo:
                u=todo.pop()
                if u==target:return True
                if u not in seen:seen.add(u);todo.extend(v for a,v in arcs if a==u)
            return False
        arcs=[(u,v) for a,u,v,w in MAIN_ACTIVITIES]
        for a,u,v,w in MAIN_ACTIVITIES:
            for b,x,y,z in MAIN_ACTIVITIES:
                if a!=b:self.assertEqual(reaches(a,b,AOV_EDGES),reaches(v,x,arcs),(a,b))

    def test_main_times_and_event_activity_distinction(self):
        r=critical_path()
        self.assertEqual(list(r['early'].values()),[0,3,5,8,10])
        self.assertEqual(list(r['late'].values()),[0,4,5,8,10])
        self.assertEqual(r['critical'],('B','D','F'));self.assertEqual(r['one_path'],('B','D','F'))
        self.assertEqual({a:t['slack'] for a,t in r['activity_times'].items()},dict(A=1,B=0,C=3,D=0,E=1,F=0))

    def test_multiple_paths_and_acceleration(self):
        for w,total,critical in [(5,10,{'B','D','F'}),(4,9,{'A','B','D','E','F'}),(3,9,{'A','D','E','F'})]:
            acts=tuple((a,u,v,w if a=='B' else d) for a,u,v,d in MAIN_ACTIVITIES)
            r=critical_path(activities=acts)
            self.assertEqual(r['T'],total);self.assertEqual(set(r['critical']),critical)
            paths=all_paths(range(5),acts,0,4)
            self.assertEqual(max(d for p,d in paths),total)
            self.assertEqual(set(a for p,d in paths if d==total for a in p),critical)

    def test_critical_endpoints_do_not_make_an_edge_critical(self):
        r=critical_path(activities=MAIN_ACTIVITIES+(('X',0,3,1),))
        for v in (0,3):self.assertEqual(r['early'][v],r['late'][v])
        self.assertEqual(r['activity_times']['X']['slack'],7)

    def test_shared_float_and_zero_duration(self):
        for aw,ew,total in [(4,1,10),(3,2,10),(4,2,11)]:
            acts=tuple((a,u,v,aw if a=='A' else ew if a=='E' else w) for a,u,v,w in MAIN_ACTIVITIES)
            self.assertEqual(critical_path(activities=acts)['T'],total)
        self.assertEqual(critical_path((3,1,2),(('dummy',3,1,0),('a',1,2,2)),source=3,sink=2)['T'],2)

    def test_renumbered_exercise_and_forward_backward_states(self):
        r=critical_path(range(4),EXERCISE_ACTIVITIES,source=2,sink=1)
        self.assertEqual(r['order'],(2,0,3,1));self.assertEqual(r['T'],6)
        self.assertEqual(r['critical'],('a','d'))
        exact=critical_path()
        self.assertEqual(exact['forward'][0]['final'],(0,))
        self.assertEqual(exact['backward'][0]['final'],(4,))
        for s in exact['forward']:
            for v in s['final']:self.assertEqual(s['values'][v],exact['early'][v])
            for v,value in s['values'].items():
                if value is not None:self.assertLessEqual(value,exact['early'][v])
        for s in exact['backward']:
            for v in s['final']:self.assertEqual(s['values'][v],exact['late'][v])
            for v,value in s['values'].items():
                if value is not None:self.assertGreaterEqual(value,exact['late'][v])

    def test_reject_invalid_project_models(self):
        bad=[(('a',0,1,-1),),(('a',0,1,True),),(('a',0,1,1.5),),
             (('a',0,1,1),('b',1,0,1)),(('a',0,1,1),('b',0,1,2))]
        for acts in bad:
            with self.assertRaises(ValueError):critical_path((0,1),acts,source=0,sink=1)
        with self.assertRaises(ValueError):critical_path(range(3),(('a',0,1,1),),source=0,sink=1)

    def test_random_dags_against_path_oracle_and_late_suffixes(self):
        rng=random.Random(1501)
        for _ in range(18):
            n=6;labels=list(range(n));rng.shuffle(labels)
            pairs={(i,i+1) for i in range(n-1)}
            pairs|={(i,j) for i in range(n) for j in range(i+2,n) if rng.random()<.3}
            acts=tuple((str(k),labels[i],labels[j],rng.randrange(5)) for k,(i,j) in enumerate(sorted(pairs)))
            r=critical_path(range(n),acts,source=labels[0],sink=labels[-1])
            paths=all_paths(range(n),acts,labels[0],labels[-1]);total=max(d for p,d in paths)
            self.assertEqual(r['T'],total)
            self.assertEqual(set(r['critical']),{a for p,d in paths if d==total for a in p})
            for v in range(n):
                self.assertEqual(r['early'][v],max(d for p,d in all_paths(range(n),acts,labels[0],v)))
                self.assertEqual(r['late'][v],total-max(d for p,d in all_paths(range(n),acts,v,labels[-1])))


@unittest.skipUnless(shutil.which('gcc'),'C11 compiler required')
class DependencyCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.binary=Path(cls.temp.name)/'d015'
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(ROOT/'course/decks/d015-topological-and-critical-path/code/dependency_demo.c'),'-o',str(cls.binary)],check=True,capture_output=True)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_c_builtin_cases_and_topological_cycle(self):
        cases={'main':MAIN_ACTIVITIES,'exercise':EXERCISE_ACTIVITIES,
               'homework':tuple((a,u,v,2 if a=='D' else w) for a,u,v,w in MAIN_ACTIVITIES),
               'tied':tuple((a,u,v,4 if a=='B' else w) for a,u,v,w in MAIN_ACTIVITIES),
               'faster':tuple((a,u,v,3 if a=='B' else w) for a,u,v,w in MAIN_ACTIVITIES),
               'shared':tuple((a,u,v,4 if a=='A' else 2 if a=='E' else w) for a,u,v,w in MAIN_ACTIVITIES),
               'endpoint':MAIN_ACTIVITIES+(('X',0,3,1),)}
        for name,acts in cases.items():
            n,s,t=(4,2,1) if name=='exercise' else (5,0,4)
            r=critical_path(range(n),acts,source=s,sink=t)
            c=json.loads(subprocess.check_output([str(self.binary),name,'--json']))
            self.assertEqual(c['T'],r['T']);self.assertEqual(c['early'],list(r['early'].values()));self.assertEqual(c['late'],list(r['late'].values()))
            self.assertEqual(c['slack'],[r['activity_times'][a]['slack'] for a,u,v,w in acts])
            self.assertEqual(c['critical'],[int(a in r['critical']) for a,u,v,w in acts])
            self.assertEqual(tuple(acts[i][0] for i in c['onePath']),r['one_path'])
        topo=json.loads(subprocess.check_output([str(self.binary),'topo','--json']))
        self.assertEqual(topo['order'],[1,0,4,3,2,5])
        cycle=subprocess.run([str(self.binary),'cycle','--json'],capture_output=True,text=True)
        self.assertEqual(cycle.returncode,2);self.assertEqual(json.loads(cycle.stdout)['order'],[1])

    def test_c_stdin_renumbered_zero_and_invalid_inputs(self):
        rng=random.Random(1502)
        for _ in range(8):
            labels=list(range(5));rng.shuffle(labels)
            acts=tuple((str(i),labels[u],labels[v],rng.randrange(5)) for i,(u,v) in enumerate([(0,1),(0,2),(1,2),(1,3),(2,3),(3,4)]))
            r=critical_path(range(5),acts,source=labels[0],sink=labels[-1])
            data=f'5 6 {labels[0]} {labels[-1]}\n'+''.join(f'{u} {v} {w}\n' for a,u,v,w in acts)
            c=json.loads(subprocess.check_output([str(self.binary),'--stdin','--json'],input=data.encode()))
            self.assertEqual(c['T'],r['T']);self.assertEqual(c['late'],list(r['late'].values()))
        for data in ['2 1 0 1\n0 1 -1\n','2 2 0 1\n0 1 1\n1 0 1\n','3 1 0 1\n0 1 1\n']:
            c=subprocess.run([str(self.binary),'--stdin','--json'],input=data,text=True,capture_output=True)
            self.assertEqual(c.returncode,2);self.assertFalse(json.loads(c.stdout)['valid'])
