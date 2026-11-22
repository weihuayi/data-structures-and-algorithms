"""D019 independent C11 and formal teaching-source regression tests."""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
DECK=ROOT/'course/decks/d019-insertion-and-exchange'
sys.path.insert(0,str(ROOT/'tools/deck'))
from build import load_deck,render_document
from components import contract_checks
from cognitive_checks import storyboard_checks


def parse_records(line):
    return [(int(k),int(i)) for k,i in re.findall(r'(-?\d+)_([0-9]+)',line)]

class D019ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=load_deck(DECK)
        cls.ids=[p['id'] for p in cls.m.COURSE.pages]
        cls.bodies={p['id']:s[1] for p,s in zip(cls.m.COURSE.pages,cls.m.SLIDES)}

    def test_33_stable_pages_and_five_sections(self):
        self.assertEqual(len(self.m.SLIDES),33)
        self.assertEqual(len(self.m.COURSE.sections),5)
        self.assertEqual(len(set(self.ids)),33)
        self.assertEqual(self.ids[7],'insertion-trace')
        self.assertEqual(self.ids[22],'partition-independent')
        self.assertEqual(self.ids[28],'mechanism-map')
        self.assertEqual(self.ids[-1],'homework')

    def test_common_contract_and_storyboard(self):
        failures=[x for x in contract_checks(self.m.COURSE,self.m.SLIDES) if x['status']!='pass']
        failures+= [x for x in storyboard_checks(DECK,self.m.COURSE) if x['status']!='pass']
        self.assertEqual(failures,[])

    def test_dynamic_trace_assets_and_roles(self):
        self.assertIn('prototypes/trace.js',self.bodies['cover'])
        self.assertIn('lesson.js',self.bodies['cover'])
        for pid in ('stability-task','insertion-independent','bubble-stop-task','partition-independent','cost-diagnosis'):
            body=self.bodies[pid]
            self.assertIn('data-course-component="task-workspace"',body)
            for field in ('data-task-input','data-task-prompt','data-task-answer'):
                self.assertIn(field,body)
        for text in ('id="ins-prev"','id="ins-next"','id="ins-reset"'):
            self.assertIn(text,self.bodies['insertion-trace'])
        for text in ('id="quick-prev"','id="quick-next"','id="quick-reset"'):
            self.assertIn(text,self.bodies['partition-trace'])

    def test_official_homework_is_single_source(self):
        tasks=[s for s in self.m.SLIDES if '课后作业' in s[0]]
        self.assertEqual(len(tasks),1)
        body=tasks[0][1]
        for item in ('A ·','B ·','(1)(3)(6)(7)','code/sorting_demo.c','过程记录','作业说明','选做'):
            self.assertIn(item,body)
        self.assertIn('无需在 Git 仓库中运行',self.bodies['code-bridge'])

    def test_generated_html_matches_renderer(self):
        expected,count=render_document(DECK)
        self.assertEqual(count,33)
        self.assertEqual((DECK/'index.html').read_text(encoding='utf-8'),expected)

class D019C11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='d019-c11-')
        cls.exe=str(Path(cls.tmp.name)/'sorting_demo')
        completed=subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',str(DECK/'code/sorting_demo.c'),'-o',cls.exe],capture_output=True,text=True)
        if completed.returncode:
            raise AssertionError('C11 compilation failed:\n'+completed.stderr)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def run_demo(self,*args):
        p=subprocess.run([self.exe,*map(str,args)],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,msg=p.stderr)
        return p.stdout

    def test_independent_generated_inputs(self):
        self.assertIn('PASS --self-test: 1200 inputs x 5 sorting methods',self.run_demo('--self-test'))

    def test_insertion_full_states_and_stability(self):
        output=self.run_demo('insert',5,2,4,2,3)
        states=[line for line in output.splitlines() if line.startswith('after insertion')]
        self.assertEqual(len(states),4)
        self.assertEqual(parse_records(states[-1]),[(2,1),(2,3),(3,4),(4,2),(5,0)])
        self.assertEqual(parse_records(states[0]),[(2,1),(5,0),(4,2),(2,3),(3,4)])

    def test_partition_example_and_new_input(self):
        out=self.run_demo('partition',4,7,2,8,3,6,1)
        self.assertIn('pivot index = 3',out)
        self.assertEqual(parse_records(next(x for x in out.splitlines() if x.startswith('after Partition'))),
                         [(1,6),(3,4),(2,2),(4,0),(8,3),(6,5),(7,1)])
        out=self.run_demo('partition',5,9,3,8,2,7,4,6,1)
        self.assertIn('pivot index = 4',out)
        self.assertEqual([k for k,i in parse_records(next(x for x in out.splitlines() if x.startswith('after Partition')))],
                         [1,4,3,2,5,7,8,6,9])

    def test_other_algorithms_and_duplicate_keys(self):
        for method in ('insert','binary','shell','bubble','quick'):
            with self.subTest(method=method):
                out=self.run_demo(method,3,-1,2,3,-1,0)
                last=[x for x in out.splitlines() if x.startswith('after ')][-1]
                actual=parse_records(last)
                self.assertEqual([k for k,i in actual],[-1,-1,0,2,3,3])
                self.assertEqual(sorted(i for k,i in actual),list(range(6)))

    def test_empty_and_invalid_arguments(self):
        for method in ('insert','quick','bubble'):
            p=subprocess.run([self.exe,method],capture_output=True,text=True)
            self.assertEqual(p.returncode,0)
        for seq in [('partition','nope'),('insert','not-an-integer'),('unknown',)]:
            p=subprocess.run([self.exe,*seq],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)

if __name__=='__main__':unittest.main()
