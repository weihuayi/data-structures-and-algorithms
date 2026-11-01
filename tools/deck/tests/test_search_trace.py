"""D016: independent lookup oracle, state invariants, cost assumptions and C."""
from bisect import bisect_left
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/deck'))
from search_trace import (KEYS, BLOCKS, MISS_KEYS, UNIFORM, HOT_FIRST, search_states,
    successful_costs, mean_cost, decision_model, block_model, block_states,
    array_view, decision_view, gap_view, snapshot)
from build import DECKS, render_document, load_deck


def lookup(values, key):
    """A linear independent correctness oracle; duplicate results may differ."""
    return next((i for i,x in enumerate(values) if x==key), -1)


class SearchTests(unittest.TestCase):
    def test_all_small_boundaries_and_duplicate_results_against_oracle(self):
        rng=random.Random(1601)
        for n in range(20):
            values=tuple(sorted(rng.randrange(-8,18) for _ in range(n)))
            for key in range(-10,21):
                for mode in ('binary','sequential'):
                    states=search_states(values,key,mode=mode)
                    result=states[-1]['result'];expected=lookup(values,key)
                    self.assertEqual(result==-1,expected==-1)
                    if result!=-1:self.assertEqual(values[result],key)
                    self.assertEqual(states[-1]['probes'],sum(s['phase']=='compare' for s in states))
                    for s in states:
                        self.assertEqual(s['values'],values)
                        self.assertEqual(len(s['checked']),s['probes'])
                        self.assertEqual(len(set(s['checked'])),s['probes'])
                        self.assertTrue(0<=s['low']<=n and -1<=s['high']<max(n,1))
                        if s['phase']=='compare':
                            self.assertTrue(s['low']<=s['mid']<=s['high'])
                        if s['result'] is None and expected!=-1:
                            self.assertTrue(any(values[i]==key for i in range(s['low'],s['high']+1)))
                    for prior,current in zip(states,states[1:]):
                        if current['phase']=='update':
                            self.assertLess(current['high']-current['low'],prior['high']-prior['low'])
        self.assertEqual(search_states((),27)[-1]['probes'],0)
        self.assertEqual(search_states((27,),27)[-1]['result'],0)
        self.assertEqual(search_states((5,16),16)[-1]['probes'],2)

    def test_main_paths_have_exact_closed_interval_semantics(self):
        for key,path,result in [(27,[36,20,27],3),(65,[36,60,67],-1),(71,[36,60,67,71],10)]:
            states=search_states(key=key)
            self.assertEqual([KEYS[s['mid']] for s in states if s['phase']=='compare'],path)
            self.assertEqual(states[-1]['result'],result)
        end=search_states(key=65)[-1]
        self.assertEqual((end['low'],end['high'],end['mid']),(9,8,None))
        for key in KEYS:
            self.assertEqual(search_states(key=key,mode='sequential')[-1]['probes'],KEYS.index(key)+1)

    def test_wrong_field_and_bad_types_rejected_by_trace_construction(self):
        for values,key,mode in [((30,10,20),30,'binary'),((True,),1,'binary'),
                                ((1,),1.5,'binary'),((1,),1,'unknown')]:
            with self.assertRaises(ValueError):search_states(values,key,mode=mode)

    def test_decision_tree_is_independent_depth_profile_and_ordered(self):
        for values in [(),(8,19,31,47),KEYS]:
            m=decision_model(values)
            self.assertEqual(set(m['nodes']),set(range(len(values))))
            self.assertEqual(set(m['gaps']),set(range(len(values)+1)))
            for i,k in enumerate(values):
                self.assertEqual(m['nodes'][i]['depth'],search_states(values,k)[-1]['probes'])
            for parent,child in m['edges']:
                self.assertEqual(m['nodes'][child]['depth'],m['nodes'][parent]['depth']+1)
        self.assertEqual(successful_costs(),(3,4,2,3,4,1,3,4,2,3,4))
        self.assertEqual(successful_costs((8,19,31,47)),(2,1,2,3))
        self.assertIn('data-cost="0"',gap_view(()))

    def test_success_failure_and_weighted_models_are_separate(self):
        self.assertEqual(mean_cost(successful_costs(),UNIFORM),3)
        self.assertEqual(mean_cost(successful_costs(mode='sequential'),UNIFORM),6)
        self.assertEqual(mean_cost(successful_costs(mode='sequential'),HOT_FIRST),Fraction(21,10))
        self.assertEqual(mean_cost(successful_costs(),HOT_FIRST),3)
        costs=tuple(search_states(key=k)[-1]['probes'] for k in MISS_KEYS)
        self.assertEqual(costs,(3,4,4,3,4,4,3,4,4,3,4,4))
        self.assertEqual(mean_cost(costs,(Fraction(1,12),)*12),Fraction(11,3))
        for k,cost in zip(MISS_KEYS,costs):
            self.assertEqual(decision_model()['gaps'][bisect_left(KEYS,k)],cost)
        for costs,p in [((1,2),(Fraction(1,3),)*2),((1,2),(-1,2)),((-1,),(1,)),((),())]:
            with self.assertRaises(ValueError):mean_cost(costs,p)
        with self.assertRaises(ValueError):successful_costs((5,5))

    def test_static_block_lookup_and_two_costs(self):
        m=block_model()
        self.assertEqual(m['starts'],(0,3,6));self.assertEqual(m['maxima'],(20,36,71))
        self.assertEqual(sorted(m['values']),list(KEYS))
        for key in range(0,76):
            end=block_states(key=key)[-1]
            self.assertEqual(end['result'],lookup(m['values'],key))
            self.assertEqual(end['record_probes'],len(end['checked']))
            if end['selected'] is not None:
                b=end['selected'];self.assertTrue(all(m['starts'][b]<=i<m['starts'][b]+len(BLOCKS[b]) for i in end['checked']))
        end=block_states(key=30)[-1]
        self.assertEqual((end['result'],end['selected'],end['index_probes'],end['record_probes']),(5,1,2,3))
        end=block_states(key=28)[-1]
        self.assertEqual((end['result'],end['checked']),(-1,(3,4,5)))
        end=block_states(key=72)[-1];self.assertEqual((end['record_probes'],end['result']),(0,-1))

    def test_sorted_maxima_do_not_replace_block_range_invariant(self):
        for blocks in [(),((),),((5,30),(16,36)),((5,5),),((5,16),(16,30))]:
            with self.assertRaises(ValueError):block_model(blocks)

    def test_snapshot_does_not_erase_zero_result_or_read_empty_candidate(self):
        hit=snapshot(search_states((27,),27)[-1])
        self.assertIn('data-search-result="0"',hit)
        self.assertIn('返回 0：命中',hit)
        empty=snapshot(search_states((),27)[-1])
        self.assertIn('data-size="0"',empty)
        self.assertIn('data-search-mid="None"',empty)


class TreeKeys(HTMLParser):
    def __init__(self):
        super().__init__();self.svg=0;self.in_text=False;self.texts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='svg':self.svg+=1
        if tag=='text' and self.svg:self.in_text=True
    def handle_endtag(self,tag):
        if tag=='svg':self.svg-=1
        if tag=='text':self.in_text=False
    def handle_data(self,data):
        if self.in_text:self.texts.append(data.strip())


class TreeStructure(HTMLParser):
    """Read actual SVG geometry into labelled topology, not just word presence."""
    def __init__(self):
        super().__init__();self.node=None;self.nodes={};self.lines=[];self.in_text=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='g' and 'tree-node' in a.get('class','').split():self.node={}
        if self.node is not None and tag=='rect':
            self.node['center']=(float(a['x'])+float(a['width'])/2,float(a['y'])+float(a['height'])/2)
        if self.node is not None and tag=='text':self.in_text=True
        if tag=='line' and 'tree-edge' in a.get('class','').split():
            self.lines.append(((float(a['x1']),float(a['y1'])),(float(a['x2']),float(a['y2']))))
    def handle_data(self,data):
        if self.node is not None and self.in_text:self.node['label']=data.strip()
    def handle_endtag(self,tag):
        if tag=='text':self.in_text=False
        if tag=='g' and self.node is not None:
            self.nodes[self.node['center']]=self.node['label'];self.node=None
    def topology(self):
        edges=set()
        for a,b in self.lines:
            if a not in self.nodes or b not in self.nodes:return None
            if a[1]>b[1]:a,b=b,a
            edges.add((self.nodes[a],self.nodes[b]))
        return set(self.nodes.values()),edges


class SlideTests(unittest.TestCase):
    def test_five_sections_and_independent_answer_contains_new_tree(self):
        deck=DECKS/'d016-search-order-and-asl'
        mod=load_deck(deck);html,_=render_document(deck)
        self.assertEqual(len(mod.COURSE.sections),5)
        page=html.split('data-page-id="cost-task"',1)[1].split('</section>',1)[0]
        initial,answer=page.split('data-task-answer',1)
        self.assertNotIn('<svg',initial)
        parser=TreeKeys();parser.feed(answer)
        for key in ('8','19','31','47'):self.assertIn(key,parser.texts)
        actual=TreeStructure();actual.feed(answer)
        expected=({'8','19','31','47'},{('19','8'),('19','31'),('31','47')})
        self.assertEqual(actual.topology(),expected)
        # Missing edge and wrong node fixtures must not pass the same criterion.
        for bad in [re.sub(r'<line class="tree-edge[^\"]*"[^>]*/>','',answer,count=1),
                    answer.replace('>47</text>','>31</text>')]:
            broken=TreeStructure();broken.feed(bad)
            self.assertNotEqual(broken.topology(),expected)
        self.assertIn('2.5',answer)
        self.assertTrue(mod.COURSE.pages[-1]['role']=='closing')

    def test_trace_and_profile_dom_bind_counts_to_rendered_data(self):
        html,_=render_document(DECKS/'d016-search-order-and-asl')
        self.assertIn('data-search-low="9" data-search-high="8"',html.replace('data-search-phase="miss" ',''))
        self.assertIn('data-search-result="0"',snapshot(search_states((27,),27)[-1]))
        self.assertEqual(gap_view().count('data-gap='),12)
        self.assertEqual(array_view().count('data-index='),22)


@unittest.skipUnless(shutil.which('gcc'),'C11 compiler required')
class CTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.binary=Path(cls.temp.name)/'d016'
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',
                        str(DECKS/'d016-search-order-and-asl/code/search_demo.c'),'-o',str(cls.binary)],check=True,capture_output=True)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_main_c_and_python_comparison_states_match(self):
        for case,values,key,mode in [('binary27',KEYS,27,'binary'),('binary65',KEYS,65,'binary'),
                ('seq27',KEYS,27,'sequential'),('seq65',KEYS,65,'sequential'),
                ('empty',(),27,'binary'),('single',(27,),27,'binary'),('pair',(5,16),16,'binary'),
                ('last',KEYS,71,'binary'),('duplicate',(5,16,16,16,30),16,'binary')]:
            c=json.loads(subprocess.check_output([str(self.binary),case,'--json']))
            states=search_states(values,key,mode=mode)
            self.assertEqual((c['result'],c['probes']),(states[-1]['result'],states[-1]['probes']))
            expected=[dict(low=s['low'],high=s['high'],mid=s['mid'],value=values[s['mid']]) for s in states if s['phase']=='compare']
            self.assertEqual(c['trace'],expected)

    def test_c_profile_is_cross_checked_against_literal_reference(self):
        c=json.loads(subprocess.check_output([str(self.binary),'profile','--json']))
        self.assertEqual(c['binary'],[3,4,2,3,4,1,3,4,2,3,4])
        self.assertEqual(c['sequential'],list(range(1,12)))
        self.assertEqual(c['failure'],[3,4,4,3,4,4,3,4,4,3,4,4])

    def test_c_stdin_random_inputs_against_independent_linear_oracle(self):
        rng=random.Random(1602)
        for _ in range(48):
            values=sorted(rng.randrange(-30,31) for _ in range(rng.randrange(17)))
            key=rng.randrange(-35,36)
            data=f'{len(values)} {key}\n'+' '.join(map(str,values))+'\n'
            c=json.loads(subprocess.check_output([str(self.binary),'--stdin','--json'],input=data.encode()))
            expected=lookup(values,key)
            self.assertEqual(c['result']==-1,expected==-1)
            if c['result']!=-1:self.assertEqual(values[c['result']],key)

    def test_c_block_lookup_boundaries_and_separate_index_record_cost(self):
        for key in list(KEYS)+list(MISS_KEYS):
            c=json.loads(subprocess.check_output([str(self.binary),'block',str(key),'--json']))
            end=block_states(key=key)[-1]
            self.assertEqual((c['result'],c['probes'],c['indexProbes'],c['selectedBlock']),
                             (end['result'],end['record_probes'],end['index_probes'],end['selected'] if end['selected'] is not None else -1))

    def test_c_cli_invalid_inputs_are_not_counted_as_queries(self):
        for data in ['-1 0\n','257 0\n','2 5\n30 10\n','1 0\nx\n','1 99999999999999999999\n5\n']:
            c=subprocess.run([str(self.binary),'--stdin','--json'],input=data,capture_output=True,text=True)
            self.assertEqual(c.returncode,2)
            self.assertFalse(json.loads(c.stdout)['valid'])


if __name__=='__main__':unittest.main()
