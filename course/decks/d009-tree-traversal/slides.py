"""D009: visible traversal state and reconstruction, built from shared components."""
from html import escape
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from tree_diagram import tree, beside, gallery
from tree_trace import traversal_states, traversal_player, recovery_states, player, sequence

DECK_ID = 'D009'
TITLE = '二叉树的遍历'
MATH = True

CHILDREN = {'A': ('B','C'), 'B': (None,'D'), 'C': ('E',None), 'D': (None,None), 'E': (None,None)}
POINTS = {'A': (300,45), 'B': (150,140), 'C': (450,140), 'D': (225,250), 'E': (375,250)}
EDGES = [(p,c) for p,cs in CHILDREN.items() for c in cs if c]


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>'+text+'</p></details>'


def fold(title, body):
    return '<details><summary>'+title+'</summary>'+body+'</details>'


def answer_fold(title, body):
    return fold(title, body).replace('<details>', '<details name="d009-recovery-answer">', 1)


def code(text):
    return '<pre>'+escape(text)+'</pre>'


def table(headers, rows):
    return '<table><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'


def main_tree(state=None, mirror=False, regions=False, levels=False, values=None):
    state = state or {}
    nodes = {k: ((600-x if mirror else x), y, k, (values or {}).get(k,'')) for k,(x,y) in POINTS.items()}
    return tree(nodes, EDGES, caption='主例：B 只有右孩子 D；C 只有左孩子 E' if not mirror else '镜像：B 只有左孩子 D；C 只有右孩子 E',
                focus=(state['current'],) if state.get('current') else (), visited=state.get('visited',()), completed=state.get('done',()), levels=levels, level_start=0,
                regions=((65,100,210,230,'L：整棵左子树'),(325,100,210,230,'R：整棵右子树')) if regions else ())


def expression():
    positions=[(300,45),(150,140),(450,140),(75,250),(225,250),(375,250),(525,250)]
    return tree({k:(*xy,label,'') for k,xy,label in zip('ABCDEFG',positions,['×','−','+','a','b','c','d'])},
                [('A','B'),('A','C'),('B','D'),('B','E'),('C','F'),('C','G')],caption=r'表达式 \((a-b)\times(c+d)\)')


def single(right=False):
    return tree({'A':(300,45,'A',''),'B':(450 if right else 150,180,'B',''), 'N':(150 if right else 450,180,'NULL','空位置')},
                [('A','B'),('A','N')],caption='只有右孩子' if right else '只有左孩子',height=265)


def trace(mode='pre', states=None):
    diagram = (lambda state: main_tree(state, levels=True)) if mode == 'queue' else main_tree
    return traversal_player(CHILDREN,'A',diagram,mode,states)


def returning():
    states=traversal_states(CHILDREN,'A')
    start=next(i for i,s in enumerate(states) if s['action'].startswith('访问 D'))
    stop=next(i for i,s in enumerate(states) if s['action'].startswith('进入 C'))
    return trace(states=states[start:stop+1])


def recovery(pre='ABDCE', inorder='BDAEC', first=False):
    positions=POINTS if pre[0]=='A' else {'P':(300,45),'Q':(150,140),'R':(450,140),'S':(75,250),'T':(525,250)}
    states=recovery_states(pre,inorder)
    if first: states=states[:2]
    panels=[]
    for s in states:
        diagram=tree({k:(*positions[k],k,'') for k in s['built']},s['links'],caption='当前已确定的结点和链接；空白处尚待恢复',focus=(s['root'],) if s['root'] else ())
        content=sequence('先序',s['pre'],s['root'],s['left'],s['right'])+sequence('中序',s['inorder'],s['root'],s['left'],s['right'])
        content+='<p class="trace-action">'+s['action']+'</p><p class="small">橙：根；绿：左子树片段；蓝：右子树片段。</p>'
        panels.append(beside(diagram,content))
    return player(panels,'由先序和中序恢复树')


def exercise_tree():
    return tree({'P':(300,45,'P',''),'Q':(150,140,'Q',''),'R':(450,140,'R',''),'S':(75,250,'S',''),'T':(525,250,'T','')},
                [('P','Q'),('P','R'),('Q','S'),('R','T')],caption='P 左 Q、右 R；Q 仅左 S；R 仅右 T')


def prediction_tree():
    return tree({'U':(300,45,'U',''),'V':(150,140,'V',''),'W':(450,140,'W',''),
                 'X':(75,250,'X',''),'Y':(225,250,'Y','')},
                [('U','V'),('U','W'),('V','X'),('V','Y')],
                caption='U 左 V、右 W；V 左 X、右 Y；W、X、Y 为叶子')


SLIDES = [
['二叉树的遍历', '<p class="lead">怎样不重不漏地访问整棵树？</p><p>数据结构与算法 · D009</p><p class="small">承接 D008；教材 5.5.1</p>', '课程名'],
['树已经连好了，怎样处理所有结点？', beside(main_tree(),'<p>打印所有结点。</p><p>寻找值为 x 的结点。</p><p>统计叶子结点。</p><p><strong>怎样保证所有结点都得到处理，<br>而且没有遗漏和重复？</strong></p>')+note('先让学生提出从根沿链接处理的办法。搜索也可能提前命中；此处先考虑未找到时怎样检查整棵树。'), '遍历需求'],
['什么叫遍历？什么叫访问？', beside(main_tree({'current':'A','visited':['A']}),'<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>遍历：按确定规则，使每个结点被访问一次且仅一次。</div><p><code>visit(p)</code> 可执行输出、计数、判断、修改数据或局部计算。</p><p><strong>进入：</strong>开始处理子树。<br><strong>访问：</strong>执行指定操作，本例输出标识。<br><strong>返回：</strong>继续未完成的调用，不自动输出。</p><p>图中 A 已访问，但它的子树尚未完成。</p>')+note('进入 ≠ 访问 ≠ 返回。前提为有限合法二叉树，无环、无共享结点；访问操作会结束，且不破坏遍历所依赖的链接。定义是概述，不冒充教材逐字原文。'), '操作语义'],
['每个结点都访问一次，顺序就唯一吗？', beside(main_tree(),'<p>A B D C E<br>B D A E C<br>D B E C A<br>A B C D E</p><p>哪一个才是正确的？</p>'+fold('讨论后，展开结论','<p>不同的系统访问规则可以产生不同顺序。<br>需要先说明规则，再检查是否符合任务。</p>'))+note('这些记录来自后面将建立的四种规则。此处不要求学生提前知道术语，也不把任意排列当作某种已定义遍历的结果。'), '顺序问题'],
['遍历一棵非空二叉树，有哪三件事？', beside(main_tree(regions=True),'<p><strong>N：</strong>访问根 A。</p><p><strong>L：</strong>遍历以 B 为根的整棵左子树。</p><p><strong>R：</strong>遍历以 C 为根的整棵右子树。</p><p>L ≠ 左孩子；R ≠ 右孩子。<br>处理 L 要覆盖 B、D，处理 R 要覆盖 C、E。</p>'), 'N / L / R'],
['先、中、后，说的是谁的先、中、后？', beside(main_tree(regions=True),table(['名称','访问次序'],[['先序','<strong>N</strong> L R'],['中序','L <strong>N</strong> R'],['后序','L R <strong>N</strong>']])+'<p><strong>说的是根 N 相对于左右子树的访问时机。</strong></p><p>固定左子树先于右子树；<br>每棵子树重复同一规则，空树直接返回。</p>'), '访问时机'],
['三个名字，为什么只需要一副递归骨架？', beside(code('void traverse(const Node *p)\n{\n    if (p == NULL) return;\n    /* position 1 */\n    traverse(p->left);\n    /* position 2 */\n    traverse(p->right);\n    /* position 3 */\n}'),'<p>选择一个位置插入 <code>visit(p);</code>：</p>'+table(['位置','得到的遍历'],[['1','先序 NLR'],['2','中序 LNR'],['3','后序 LRN']])+'<p>递归结构相同，根的访问时机不同。</p>')+note('这是一份待填的骨架，不是已完成的输出程序。三处只选一处。课堂程序 depth_first 用 order 选择 PRE、IN、POST，并额外检查输出容量与失败返回。'), '递归骨架'],
['先序：为什么先访问根？', trace()+note('按 NLR，先执行 visit，再处理左右子树。先预测再点下一步，完整输出 A B D C E。停在首次访问 A、访问 D、完成 B，区分当前处理、已访问、子树完成。'), '先序示范'],
['中序：为什么不是“从左往右读图”？', trace('in')+note('按 LNR，B 左子树为空，先访问 B，再遍历右子树 D；左子树整体完成后才访问 A。完整输出 B D A E C。结点画在屏幕什么横坐标不定义算法，中序由递归规则决定。'), '中序推演'],
['后序：为什么根最后？', trace('post')+note('按 LRN，子树先完成，再访问根。A 必须等 B、C 两棵子树都完成，完整输出 D B E C A。访问最后一个结点与退出根调用仍是不同事件。'), '后序推演'],
['换一棵树，你还能独立写出来吗？', beside('<div>'+prediction_tree()+note('固定左子树先于右子树，保留原始答案。本题使用 U–Y 的另一形状，避免提前暴露第 22 页恢复题。核对时要求解释一处子树内部次序。')+'</div>','<div class="tree-answer"><p>先序 ______<br>中序 ______<br>后序 ______</p><p class="small">左先于右；作答 4 分钟，核对 2 分钟。</p>'+answer_fold('需要时，展开提示','<p>把以 V 为根的整棵子树看作 L。<br>子树内部重复相同规则。</p>')+answer_fold('作答后，展开核对','<p>先序 U V X Y W<br>中序 X V Y U W<br>后序 X Y V W U</p>')+'</div>'), '独立三序'],
['为什么递归天然适合二叉树？', beside(main_tree(regions=True),table(['对象的结构','程序的工作'],[['根','visit(p)'],['左二叉树','traverse(p->left)'],['右二叉树','traverse(p->right)'],['空树','直接返回']])+'<p>子树仍是二叉树，<br>所以同一过程可以继续处理子树。</p><p>对象的递归结构对应算法的递归结构。</p>')+note('回收 D008 的二叉树定义、D006 的递归。表格是对应关系，不规定执行次序；N 放在哪里由当前遍历规则决定。'), '结构与算法'],
['为什么不会重复、不会遗漏，而且一定结束？', beside(main_tree(regions=True),r'<p>前提：有限合法二叉树，无环、无共享结点。</p><p>结点集合 \(T=\{root\}\cup L\cup R\)，三部分互不重叠。</p><p><strong>不漏：</strong>根与两棵子树覆盖整棵树。<br><strong>不重：</strong>子树各正确遍历一次，根访问一次。</p><p><strong>终止：</strong>每次进入更小的子树，最终遇到空树并返回。</p>')+note('按结构归纳：空树不访问结点，结论成立；假设更小的左右子树各正确遍历一次，则合并根一次成立。visit 必须终止且不破坏链接。有环可能不终止，共享结点可能重复；图的访问标记留到 D012。'), '正确性'],
['递归返回以后，程序为什么知道下一步？', returning()+note('调用栈保存当前调用和返回后继续执行的位置。D 返回 B，B 结束后返回 A，A 才继续右子树 C；返回 A 不再次输出 A。只回收 D006，不重讲递归或栈。重置回到访问 D 的观察点。'), '调用与返回'],
['如果要求先处理浅层结点呢？', beside(main_tree(levels=True),'<p>第 0 层：A<br>第 1 层：B C<br>第 2 层：D E</p><p>访问 B 后，下一个应该是 D，还是 C？</p>'+fold('讨论后，展开层序要求','<p>先浅后深、同层从左到右：<br>下一位是 C，完整顺序 A B C D E。</p>')+'<p class="small">根深度为 0，深度等于层编号。<br>本树高度按层数计为 3；空树高度为 0。</p>'), '层序需求'],
['队列为什么自然产生层序？', trace('queue')+note('FIFO：新发现的深一层结点排到当前层尚未处理的结点后面。根入队 [A]；访问 A 并加入孩子后 [B,C]；处理 B 后 [C,D]；处理 C 后 [D,E]。固定左孩子先入队。队列可同时包含相邻两层，层编号非递减。'), '队列推演'],
['四种遍历怎样放在一张认知地图里？', table(['推进方式','访问规则','本讲实现'],[['沿子树深入','先序 NLR／中序 LNR／后序 LRN','递归，选择 visit 的位置'],['按层推进','层序：先浅后深，同层从左到右','FIFO 队列，左孩子先入队']])+'<p>先序、中序、后序属于树上的深度优先方式；<br>层序属于广度优先方式。</p><p class="small">一般图的 DFS/BFS 及其辅助状态在 D012 展开。</p>'+note('这里建立术语接口，不提前讲 frontier、seen、parent 的一般机制。也不能把深度优先仅等同于先序，或把三序看作三个无关算法。'), '遍历地图'],
['同一棵表达式树，为什么需要不同顺序？', beside(expression(),table(['顺序','逐结点输出'],[['先序','× − a b + c d'],['中序','a − b × c + d'],['后序','a b − c d + ×']])+r'<p>普通中序只给出中缀次序，丢失结合关系。<br>完整结构需括号：\(((a-b)\times(c+d))\)。</p><p>求根上的乘法前，先求左右子表达式。<br>任务决定哪些信息需要先就绪。</p>')+note('括号是在进入、离开时附加的输出，不是重复访问结点。前缀、后缀解释依赖已知运算符元数；求值要使用子树结果，不等同于单纯打印后序序列。'), '任务应用'],
['遍历不只是打印结点', beside('<div class="tree-explain">'+table(['任务','操作或结果使用'],[['打印','输出当前标识'],['统计 / 搜索','count++ 或判断'],['统计叶子','左右为空时计数'],['高度 / 求值','汇总子树返回值']])+'<p>遍历提供计算顺序；任务决定操作时机，以及是否使用子树返回值。</p></div>','<p><strong>子树返回结果，不等同于 visit(p)。</strong></p>'+fold('课后阅读：叶子数汇总',code('size_t leaves(const Node *p) {\n    if (!p) return 0;\n    if (!p->left && !p->right)\n        return 1;\n    return leaves(p->left)\n         + leaves(p->right);\n}')))+note('叶子统计既可通过局部判断计数，也可递归汇总，不能因为“统计”就断言必须后序。搜索若提前成功可停止，但完整遍历的代价结论不自动描述提前退出路径。'), '操作迁移'],
['只有一条遍历序列，能把树恢复出来吗？', gallery(single(),single(True))+'<p>两棵树先序均 A B、后序均 B A，却没有保留 B 的左右位置。<br>缺失位置也是结构信息，普通序列可能丢失它。</p>'+note('即使先序加后序也一般不足以唯一确定二叉树。若先序记录全部空子树标记，信息量改变，可以唯一恢复。'), '信息与恢复'],
['先序 + 中序为什么能够恢复？', '<p><strong>成立条件：结点标识互异，并且先序与中序相容。</strong></p>'+recovery()+note('先序首项定根，在中序唯一定位根；中序划分左右，再按左段长度切分先序，递归重复。每次分割都必须相容：先序 ABC、中序 CAB 虽总集合相同，左子树却分别要求 B 与 C，因而不能恢复。互异保证每轮根位置唯一，相容保证所有子问题存在，递归确定唯一树。'), '恢复机制'],
['换一组序列，你能独立恢复吗？', beside('<div>'+sequence('先序',list('PQSRT'))+sequence('中序',list('SQPRT'))+'<p>画树，保留至少两次切分。</p><p>写出后序与层序，<br>再重新生成输入序列核对。</p><p class="small">独立 6 分钟，核对 2 分钟。</p>'+note('只写正确图不够，要展示切分。是否使用提示应区分记录；不给动画时仍能独立恢复才是这里的证据。')+'</div>','<div class="tree-answer">'+answer_fold('需要时，展开第一步提示','<p>根 P；中序左段 S Q，右段 R T。<br>先序根后两项 Q S 属于左子树。</p>')+answer_fold('完成作答后，展开答案树',exercise_tree())+answer_fold('展开切分与序列核对','<p>Q：左 S，右空；R：左空，右 T。<br>后序 S Q T R P；层序 P Q R S T。<br>重新生成：先序 P Q S R T；中序 S Q P R T。</p>')+'</div>'), '独立学习证据'],
['一次遍历需要多少代价？', beside(main_tree(levels=True),table(['完整遍历','时间','活跃辅助空间'],[['递归三序',r'\(\Theta(n)\)',r'\(O(h)\) 调用栈'],['层序',r'\(\Theta(n)\)',r'\(O(w)\) 队列']])+r'<p>前提：每个结点执行一次 \(O(1)\) 局部工作。</p><p>\(n\) 为结点数；\(h\) 为层数；\(w\) 为最大层宽。<br>本树 \(n=5,h=3,w=2\)。</p><p>空间来自同时保存的尚未完成状态。</p>')+note(r'按非空树讨论渐近上界；空树只有常数开销。队列可能混合相邻两层，占用不一定恰等于 w，但至多 O(w)。输出若另存需 O(n)，不计入这里的辅助空间；演示预分配 CAP 不等于活跃状态。恢复采用分段线性找根，最坏 O(n²)，不套用本页遍历代价。'), '代价'],
['今天真正建立了什么？', table(['问题','已经建立的关系'],[['为什么需要规则','树结构不替任务规定唯一线性访问顺序'],['怎样安排访问','N / L / R；根的时机决定先、中、后序'],['怎样实现并说明成立','递归结构；根与左右子树不重叠，规模递减'],['怎样按层处理','FIFO 队列让浅层在前'],['怎样选择与反推','任务决定顺序；互异且相容的先序、中序可恢复树']])+'<p class="lead">理解和设计访问顺序，才能解释遍历序列。</p>', '结构化收口'],
['课后：正式作业与扩展自学', '<p><strong>教材导航</strong>：精读 5.5.1，比较递归与非递归遍历；阅读 5.5.2，区分孩子指针和线索。</p><p><strong>正式作业 A · 书本习题</strong>：第 5 章选择题 <strong>(7)(10)</strong>、应用题 <strong>(1)</strong>、算法设计题 <strong>(1)(3)</strong>。选择题附理由；应用题与算法题写出思路和完整过程。</p><p><strong>正式作业 B · 程序实践</strong>：运行 <code>code/traversal_demo.c</code>：先预测主例先序；再将 B 的唯一孩子 D 从右移到左，预测变式的中序、后序和层序，核对 variant 输出；解释求表达式值为何要等子树结果。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B 两部分，末尾附 3–5 行过程记录。<br>扩展自学（不提交）：显式栈先序、中序/后序非递归、更多恢复组合；应用题 (2)①；线索化 5.5.2：选择题 (12)(13)、应用题 (2)②。</p>', '课后衔接'],
['访问顺序会设计了，结构本身还能改变吗？', '<p>遍历是在既定树结构上设计访问顺序。</p><p class="lead">如果改变树的结构本身，<br>能不能让整个计算代价更低？</p><p>当不同叶子的使用频率不同，怎样选择树形？<br>D010：树和森林的表示转换与哈夫曼树。</p>', '留下问题'],
]
