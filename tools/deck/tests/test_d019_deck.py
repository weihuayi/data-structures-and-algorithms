"""D019 independent C11 and formal teaching-source regression tests."""
import re
from html.parser import HTMLParser
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

class MathematicalMarkupAudit(HTMLParser):
    """Report obvious unrendered mathematics outside prose code and array slots.

    This is deliberately narrow: typography beyond the patterns remains a
    professional review responsibility, not a complete formal parser.
    """
    suspect=re.compile(r'(?:[OΩΘ]\s*\(|\d+_[a-zA-Z]|\b(?:n|i)\s*[-−]\s*\d)')
    def __init__(self):
        super().__init__();self.stack=[];self.suspects=[]
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def handle_starttag(self,tag,attrs):
        if tag in self.VOID:return
        attrs=dict(attrs); classes=set(attrs.get('class','').split())
        inherited=self.stack[-1] if self.stack else False
        excluded=inherited or tag in ('code','pre','script','style') or bool(classes.intersection({'math','d19-cell','d19-cells'}))
        self.stack.append(excluded)
    def handle_endtag(self,tag):
        if self.stack:self.stack.pop()
    def handle_startendtag(self,tag,attrs):
        # Void nodes are not on the HTMLParser nesting stack.
        pass
    def handle_data(self,data):
        if self.stack and self.stack[-1]:return
        found=self.suspect.search(data)
        if found:self.suspects.append(data.strip())

class D019ContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=load_deck(DECK)
        cls.ids=[p['id'] for p in cls.m.COURSE.pages]
        cls.bodies={p['id']:s[1] for p,s in zip(cls.m.COURSE.pages,cls.m.SLIDES)}

    def test_34_stable_pages_and_five_sections(self):
        self.assertEqual(len(self.m.SLIDES),34)
        self.assertEqual(len(self.m.COURSE.sections),5)
        self.assertEqual(len(set(self.ids)),34)
        self.assertEqual(self.ids[7],'insertion-trace')
        self.assertEqual(self.ids[23],'partition-independent')
        self.assertEqual(self.ids[29],'mechanism-map')
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
        tasks=[slide for page,slide in zip(self.m.COURSE.pages,self.m.SLIDES) if page['id']=='homework']
        self.assertEqual(len(tasks),1)
        body=tasks[0][1]
        for item in ('A ·','B ·','(1)(3)(6)(7)','code/sorting_demo.c','过程记录','课程作业规范','选做','<pre', './d019_demo insert'):
            self.assertIn(item,body)
        self.assertIn('无需在 Git 仓库中运行',self.bodies['code-bridge'])

    def test_math_complexity_symbols_and_algorithm_introduction(self):
        cost=self.bodies['insertion-cost']
        for token in (r'\(O(f(n))\)',r'\(\Omega(f(n))\)',r'\(\Theta(f(n))\)'):
            self.assertIn(token,cost)
        self.assertIn('恰好为 0',cost)
        shell=self.bodies['shell-gaps']
        for token in ('希尔排序（Shellsort）', '下标相差', 'g=2', '2\\rightarrow1'):
            self.assertIn(token,shell)
        self.assertIn('shell-stability',self.ids)
        self.assertIn('A组',self.bodies['shell-gaps'])
        self.assertIn('B组',self.bodies['shell-gaps'])
        self.assertIn('for="d19-student-answer"',self.bodies['partition-independent'])
        self.assertIn('typedef struct { int key; int id; } Record;',self.bodies['code-bridge'])
        self.assertNotIn('Record{key,id}',self.bodies['code-bridge'])
        self.assertIn('快速排序（Quicksort）',self.bodies['partition-idea'])
        self.assertIn('直接插入排序（Insertion Sort）',self.bodies['sorted-prefix'])
        self.assertNotIn('已经完成',self.bodies['partition-idea'])

    def test_no_obvious_math_in_raw_prose(self):
        for pid,body in self.bodies.items():
            with self.subTest(page=pid):
                auditor=MathematicalMarkupAudit();auditor.feed(body)
                self.assertEqual(auditor.suspects,[])

    def test_insertion_example_revisions_are_cross_page(self):
        for pid in ('sorted-prefix','insertion-trace','insertion-invariant','bubble-boundary'):
            self.assertIn('2</strong>',self.bodies[pid])
            self.assertIn('6</strong>',self.bodies[pid])
            self.assertIn('7</strong>',self.bodies[pid])
            self.assertIn('5</strong>',self.bodies[pid])
        self.assertNotIn('r3',self.bodies['insertion-trace'])
        # F1: didactic counterexample must separate sorted prefix from sorted whole input.
        body=self.bodies['insertion-invariant']
        self.assertIn('末尾的',body)
        self.assertIn('整体仍无序',body)
        self.assertIn('1</strong>',body)
        self.assertIn('1</strong>',self.bodies['bubble-boundary'])
        self.assertIn('\\([1_{\\mathrm b}',self.bodies['stability-task'])
        self.assertIn('\\(n-1\\)',self.bodies['bubble-stop-task'])

    def test_r3_classroom_partition_semantics_and_course_frame(self):
        # Classroom feedback: avoid mistaking a one-time direction order for the cycle.
        self.assertEqual(self.m.SLIDES[0][2], '课程导入')
        self.assertEqual(self.m.SLIDES[-1][2], '')
        self.assertIn('d19-cover-line', self.bodies['cover'])
        self.assertIn('d19-cover-note', self.bodies['cover'])
        self.assertNotIn('从已知走向新问题', self.bodies['cover'])
        self.assertIn('课后怎样预测、运行和核对？', self.m.SLIDES[-1][0])
        css=(DECK/'lesson.css').read_text()
        self.assertIn('d19-cover-line',css)
        self.assertIn('background:#f0f6fb;color:#193f60',css)
        self.assertIn('d19-homework',self.bodies['homework'])
        for pid in ('pivot-hole','partition-trace','partition-independent'):
            self.assertNotIn('先从右向左、再从左向右扫描',self.bodies[pid])
            self.assertNotIn('先从右向左寻找小于枢轴的关键字，再从左向右',self.bodies[pid])
        self.assertIn('空位在哪一端',self.bodies['pivot-hole'])
        self.assertIn('从另一端',self.bodies['pivot-hole'])
        self.assertIn('两端',self.bodies['partition-trace'])
        self.assertIn('id="quick-next-scan"',self.bodies['partition-trace'])
        self.assertIn('初始',self.bodies['partition-independent'])
        self.assertIn('当前空位',self.bodies['partition-independent'])
        self.assertIn('扫描跳过',self.bodies['partition-invariant'])
        self.assertIn('关键字比较次数一般不等于',self.bodies['insertion-cost'])
        js=(DECK/'lesson.js').read_text()
        for marker in ('low = high','空位在 low','空位在 high','i===state.low',"prefix==='quick'"):
            self.assertIn(marker,js)
        self.assertIn('已于 2026-11-23 用于真实课堂',(DECK/'README.md').read_text())

    def test_generated_html_matches_renderer(self):
        expected,count=render_document(DECK)
        self.assertEqual(count,34)
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

    def test_c11_revised_insertion_main_example(self):
        output=self.run_demo('insert',2,6,7,5,1)
        steps=[line for line in output.splitlines() if line.startswith('after insertion')]
        self.assertEqual(parse_records(steps[-1]),[(1,4),(2,0),(5,3),(6,1),(7,2)])

    def test_shell_gap_states_match_both_lesson_examples(self):
        actual=self.run_demo('shell',7,4,6,3,5)
        self.assertIn('after gap 2',actual)
        self.assertIn('after gap 1',actual)
        steps=[line for line in actual.splitlines() if line.startswith('after gap ')]
        self.assertEqual([k for k,i in parse_records(steps[0])],[5,3,6,4,7])
        self.assertEqual([k for k,i in parse_records(steps[1])],[3,4,5,6,7])
        duplicate=self.run_demo('shell',2,2,1)
        self.assertEqual(parse_records(next(line for line in duplicate.splitlines() if line.startswith('after gap 2'))),
                         [(1,2),(2,1),(2,0)])

    def test_partition_example_and_new_input(self):
        out=self.run_demo('partition',4,7,2,8,3,6,1)
        self.assertIn('pivot index = 3',out)
        self.assertEqual(parse_records(next(x for x in out.splitlines() if x.startswith('after Partition'))),
                         [(1,6),(3,4),(2,2),(4,0),(8,3),(6,5),(7,1)])
        out=self.run_demo('partition',5,9,3,8,2,7,4,6,1)
        self.assertIn('pivot index = 4',out)
        self.assertEqual([k for k,i in parse_records(next(x for x in out.splitlines() if x.startswith('after Partition')))],
                         [1,4,3,2,5,7,8,6,9])

    def test_c11_partition_frames_match_js_pointer_checkpoints(self):
        """Actual C11 checkpoint logs and JS display frames must mean the same instant."""
        import json
        js=str(DECK/'prototypes/trace.js')
        samples=[(4,7,2,8,3,6,1),(5,9,3,8,2,7,4,6,1),
                 (2,2,1),(4,4,4,4),(3,), (0,-1,4,-2,6)]
        for seq in samples:
            with self.subTest(input=seq):
                c=self.run_demo('partition',*seq)
                ctrace=[]
                for line in c.splitlines():
                    m=re.fullmatch(r'TRACE (hold|right|left|done) low=(\d+) high=(\d+) hole=(-?\d+)',line)
                    if m:ctrace.append((m[1],int(m[2]),int(m[3]),int(m[4])))
                cmd=['node','-e',"const t=require(process.argv[1]);const a=process.argv.slice(2).map(Number);console.log(JSON.stringify(t.partitionTrace(a).frames.map(x=>[x.name,x.low,x.high,x.hole])))",js,*map(str,seq)]
                j=subprocess.run(cmd,text=True,capture_output=True,timeout=10)
                self.assertEqual(j.returncode,0,msg=j.stderr)
                jtrace=[]
                for name,low,high,hole in json.loads(j.stdout):
                    typ=('hold' if name=='暂存枢轴' else 'done' if name=='枢轴归位'
                         else 'right' if '从右' in name else 'left')
                    jtrace.append((typ,low,high,hole))
                self.assertEqual(ctrace,jtrace)

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
