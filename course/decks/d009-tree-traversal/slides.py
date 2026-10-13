"""D009: visible traversal state and reconstruction, built from shared components."""
from html import escape
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from tree_diagram import tree, beside, gallery
from tree_trace import traversal_states, traversal_player, recovery_states, player, sequence

DECK_ID = 'D009'
TITLE = '遍历：系统访问的设计'
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
                focus=(state['current'],) if state.get('current') else (), visited=state.get('visited',()), completed=state.get('done',()), levels=levels,
                regions=((65,100,210,230,'L：整棵左子树'),(325,100,210,230,'R：整棵右子树')) if regions else ())


def expression():
    positions=[(300,45),(150,140),(450,140),(75,250),(225,250),(375,250),(525,250)]
    return tree({k:(*xy,label,'') for k,xy,label in zip('ABCDEFG',positions,['×','−','+','a','b','c','d'])},
                [('A','B'),('A','C'),('B','D'),('B','E'),('C','F'),('C','G')],caption=r'表达式 \((a-b)\times(c+d)\)')


def single(right=False):
    return tree({'A':(300,45,'A',''),'B':(450 if right else 150,180,'B',''), 'N':(150 if right else 450,180,'NULL','空位置')},
                [('A','B'),('A','N')],caption='只有右孩子' if right else '只有左孩子',height=265)


def trace(mode='pre', states=None):
    return traversal_player(CHILDREN,'A',main_tree,mode,states)


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


def threaded():
    diagram=main_tree({'current':'D'})
    # Separate, explicitly labelled directed thread; structural edges remain plain.
    overlay='<path class="trace-thread" d="M 249 250 C 270 310 560 310 570 200 C 590 90 450 15 334 40"/><path class="trace-thread" d="M 334 40 L 353 39 M 334 40 L 344 24"/><text class="tree-detail" x="450" y="335">D 的中序后继线索：指向 A</text>'
    return diagram.replace('</svg>',overlay+'</svg>')

SLIDES = [
['遍历：系统访问的设计', '<p class="lead">结构已经连好，下一步该访问谁？</p><p>数据结构与算法 · D009</p><p class="small">承接 D008；教材 5.5.1，5.5.2 线索化自学引导</p>', '课程名'],
['同一棵表达式树，为什么需要不同顺序？', beside(expression(),'<p>写出算式时，运算符放在哪里？</p><p>计算根上的乘法前，<br>必须先得到哪两个结果？</p>')+note('先用 1 分钟让学生说出根运算依赖两个子表达式结果，再引入后序术语。表达式只使用二元运算符。'), '回到问题'],
['进入、访问、返回，是同一件事吗？', beside(main_tree({'current':'A','visited':['A']}),'<p><strong>进入：</strong>开始处理这棵子树。</p><p><strong>访问：</strong>执行 <code>visit(p)</code>，本例输出标识。</p><p><strong>返回：</strong>回到尚未完成的调用；不自动输出。</p><p>先序刚访问 A：已输出 A，<br>但 A 的两棵子树还没有完成。</p>')+'<details class="teacher-note"><summary>教材定义与条件（概述）</summary><div class="quote compact-quote"><strong>教材定义（概述）</strong><br>遍历使每个结点被访问一次且仅一次。</div><p>前提为有限合法二叉树，无环、无共享结点。本讲先固定访问为输出标识。</p></details>', '操作语义'],
['一棵非空树里，有哪三件事要做？', beside(main_tree(regions=True),'<p>N：访问根 A。</p><p>L：遍历以 B 为根的<strong>整棵</strong>子树。<br>R：遍历以 C 为根的<strong>整棵</strong>子树。</p><p>固定左先于右：<br>先序 NLR；中序 LNR；后序 LRN。</p><p>每棵子树重复同一规则；空树返回。</p>'), '算法设计'],
['先序怎样一步步得到输出？', trace()+note('先预测动作再点下一步。橙框标当前控制位置，蓝底表示已访问，绿框表示整棵子树完成；这些状态不能互相替代。可重点停在首次访问 A、访问 D、完成 B 三处。'), '先序示范'],
['完成 D 后，怎样继续到 C？', returning()+note('调用帧含结点及执行位置。D 返回 B，B 结束后返回 A，A 才继续右子树 C；返回 A 不再次输出 A。重置回到访问 D 的观察点。'), '调用与返回'],
['只改变访问时机，输出怎样变化？', beside('<div class="tree-swap"><div class="tree-preview">'+main_tree()+'</div>'+fold('展开中序 C 模板',code('void inorder(const Node *p) {\n    if (p == NULL) return;\n    inorder(p->left);\n    visit(p);\n    inorder(p->right);\n}'))+'</div>','<p>中序补全：B 的左侧为空，先输出 B；完成 D 后输出 ____；C 子树输出 ____。</p><p>中序：左子树、visit、右子树。</p><p>再独立写后序，解释 A 为什么最后。</p>'+fold('完成预测后，展开三序核对','<p>先序：A B D C E<br>中序：B D A E C<br>后序：D B E C A</p>'))+note('先中序补全，再后序独立留痕。各递归函数调用自身；程序以 order 参数合并访问时机。'), '补全与独立推演'],
['为什么不会重复，也不会漏？', beside(main_tree(regions=True),'<p>根、左子树、右子树互不重叠，合起来就是整棵树。</p><p>两棵更小的子树各正确遍历一次，再访问根一次，就不重不漏。</p><p>递归进入更小子树，最终到空树并返回。</p>')+note('按结构归纳。共享孩子会重复访问，环可能导致不终止；合法树条件不可省略。这里不增加图的 visited 标记，留到 D012。'), '正确性'],
['表达式树的三种输出有什么用途？', beside(expression(),table(['顺序','逐结点输出'],[['先序','× − a b + c d'],['中序','a − b × c + d'],['后序','a b − c d + ×']])+r'<p>直接中序输出丢失原结合关系。<br>补全括号：\(((a-b)\times(c+d))\)。</p><p>求乘法结果前，先算两个子表达式。</p>')+note('表中是输出标记序列，不是把后缀写作代数乘法。前缀、后缀的解释依赖运算符元数；括号是在进入、离开时附加的输出，不是重复访问结点。后缀求值先弹右操作数，再弹左操作数。'), '回到案例'],
['不用调用栈，待做的任务放在哪里？', beside(main_tree(),code('根入栈\n只要栈不空：\n    弹出 p，访问 p\n    非空右孩子入栈\n    非空左孩子入栈')+'<p>栈中只存待处理子树的根。<br>后进先出：要先处理左边，就先压右边。</p>')+note('此显式栈不保存递归程序的返回位置，不能与调用帧混为一谈。这里只实现先序，中序、后序需要安排不同访问时机。'), '显式栈'],
['栈里的 C 为什么要等一等？', trace('stack')+note('右先压、左后压。可停在访问 B 后、D 入栈前后：当前结点的待发现孩子与栈中任务一起构成待做工作，不能在任意微步骤都说栈已经覆盖全部未访问结点。改为左先压则输出 A C E B D。'), '栈的推演'],
['要按层展示，该换什么纪律？', beside(main_tree(levels=True),code('根入队\n只要队列不空：\n    出队 p，访问 p\n    非空左孩子入队\n    非空右孩子入队')+'<p>先进先出：C 比 D 更早入队，<br>所以先处理 C，再处理 D。</p>')+note('固定同层从左到右。层序是广度优先；先序、中序、后序都是深度优先方式，不能把深度优先仅等同于先序。'), '层序'],
['队列怎样保证浅层在前？', trace('queue')+note('新孩子排队尾，层次非递减。同层按父结点处理顺序和左先右后排列。队列可同时包含相邻两层；合法树中每个非根结点只由唯一父结点发现一次。'), '队列的推演'],
['同一棵树，下一项工作为什么不同？', beside(main_tree({'visited':['A','B']}),'<p>处理完 A、B，并加入其孩子后：</p>'+table(['机制','待处理状态','下一项'],[['栈底到栈顶','C　D','D'],['队头到队尾','C　D','C']])+'<p>先序：A B D C E<br>层序：A B C D E</p><p>树没变，下一项工作的取出规则变了。</p>')+note('这一刻两种容器看起来都是 C D，但取出的端不同。中序、后序还需安排根的访问时机，不能靠把栈换成队列得到。'), '机制收口'],
['访问次数相同，辅助空间也相同吗？', '<div class="trace-compact">'+gallery(tree({'A':(130,35,'A',''),'B':(240,110,'B',''),'C':(350,185,'C',''),'D':(460,260,'D','')},[('A','B'),('B','C'),('C','D')],caption=r'单链：\(h=4\)，\(w=1\)'),main_tree(levels=True))+table(['方式','时间（单次访问常数代价）','活跃辅助空间'],[['递归三序',r'\(\Theta(n)\)',r'\(O(h)\) 调用栈'],['显式栈先序',r'\(\Theta(n)\)',r'\(O(h)\) 待处理根'],['层序',r'\(\Theta(n)\)',r'\(O(w)\) 队列']])+'</div>'+note(r'\(h\) 为层数，\(w\) 为最大层宽。显式先序栈在单链上可只有一项，\(O(h)\) 是上界；队列会混合相邻两层，容量不一定恰等于 \(w\)。输出另需 \(O(n)\) 空间，演示预分配 CAP 不等于活跃状态。'), '代价'],
['叶子数怎样从子树汇总回来？', beside(main_tree(values={'D':'返回 1','E':'返回 1','B':'返回 1','C':'返回 1','A':'返回 2'}),r'<p>空树返回 0；叶子返回 1。</p><p>B：\(0+1=1\)，C：\(1+0=1\)。<br>A 汇总：\(1+1=2\)。</p>'+code('if (!p) return 0;\nif (!p->left && !p->right) return 1;\nreturn leaves(p->left)\n     + leaves(p->right);'))+note(r'这是后序式结果汇总，不只是把打印换成计数。B、C 虽然各有一个空孩子，却不是叶子。复杂度 \(\Theta(n)\)，递归辅助空间 \(O(h)\)。'), '操作迁移'],
['先预测，再运行四种遍历', beside('<div class="tree-swap"><div class="tree-preview">'+main_tree()+'</div>'+fold('完成预测后，展开镜像与结果','<div class="tree-answer">'+main_tree(mirror=True)+'</div><p>镜像先序：A C E B D。<br>原树：先序 ABDCE，中序 BDAEC；后序 DBECA，层序 ABCDE，叶子数 2。</p>')+'</div>','<p>先写四种遍历和叶子数。<br>显式栈先序是否与递归一致？</p><p>若整棵树镜像，先序怎样变化？</p><p><a href="code/traversal_demo.c">打开 C 演示程序</a></p>'+fold('展开编译与运行命令',code('gcc -std=c11 -Wall -Wextra code/traversal_demo.c -o /tmp/d009\n/tmp/d009')))+note('先保留预测再运行；镜像两次应还原。程序也检查边界与恢复失败。'), '预测与运行'],
['只有访问记录，能画回原树吗？', gallery(single(),single(True))+'<p>两棵树先序都是 A B，后序都是 B A。<br>记录没有说明：B 究竟占左位置，还是右位置？</p>'+note('普通序列不含空标记；先序加后序一般不足以唯一确定二叉树。若先序记录全部空子树标记，信息量改变，可以唯一恢复。'), '信息与恢复'],
['先序定根，中序怎样划分左右？', recovery(first=True)+note('只展示第一刀，先让学生继续。中序确定左子树大小，再据此切分先序；两条序列的切分位置并不相同。'), '恢复机制'],
['重复切分，链接怎样逐步长出来？', recovery()+note(r'逐步确定 A、B、D、C、E，同时展示空片段。完成后重新生成输入序列。分段线性找根的实现最坏为 \(O(n^2)\)，本课不要求现场写恢复代码。'), '恢复推演'],
['集合相同，为什么仍可能无法恢复？', beside(tree({'A':(300,45,'A','根'),'C':(150,190,'C','中序要求左子树含 C'),'B':(450,190,'B','中序要求右子树含 B')},[('A','C'),('A','B')],caption='仅按中序画出的候选分区，尚未满足先序'),sequence('先序',list('ABC'),'A',['B'],['C'])+sequence('中序',list('CAB'),'A',['C'],['B'])+'<p>左子树只有 1 个结点：<br>中序要求 C，先序切出的却是 B。</p><p>长度、总集合相同仍不够，<br>每轮分割都必须相容。</p>')+note('图为冲突候选，不是恢复结果。标识互异才能唯一定位根；互异且相容的先序加中序唯一确定树。后序加中序同理以末项定根。重复数据值可另设互异 ID。'), '条件与正确性'],
['不看示范，能恢复另一棵树吗？', beside('<div>'+sequence('先序',list('PQSRT'))+sequence('中序',list('SQPRT'))+'<p>画树，保留至少两次切分。</p><p>写出后序与层序，<br>再重新生成输入序列核对。</p><p class="small">独立 6 分钟，核对 2 分钟。</p>'+note('只写正确图不够，要展示切分。是否使用提示应区分记录；不给动画时仍能独立恢复才是这里的证据。')+'</div>','<div class="tree-answer">'+answer_fold('需要时，展开第一步提示','<p>根 P；中序左段 S Q，右段 R T。<br>先序根后两项 Q S 属于左子树。</p>')+answer_fold('完成作答后，展开答案树',exercise_tree())+answer_fold('展开切分与序列核对','<p>Q：左 S，右空；R：左空，右 T。<br>后序 S Q T R P；层序 P Q R S T。<br>重新生成：先序 P Q S R T；中序 S Q P R T。</p>')+'</div>'), '独立学习证据'],
['经常找中序下一位，可以多存什么？', beside(threaded(),'<p>中序：B D A E C。<br>D 的下一位是 A，但 D 没有孩子指向 A。</p><p>把原本空的右指针域用作后继线索，并用标志区分孩子与线索。</p><p class="small">实线：孩子关系。<br>虚线箭头：中序后继线索。</p>')+note('教材 5.5.2 自学引导。这里只画 D 的一条后继线索，不是完整线索树；线索不都指向父结点。误当孩子递归可能成环。构造、遍历细节课后读，考试范围以正式通知为准。'), '线索化引导'],
['把任务、顺序和机制放在一起看',table(['任务','顺序或条件','机制'],[['父项先于子项输出','先序','递归或显式栈'],['子表达式结果先就绪','后序式汇总','子树返回结果'],['按浅到深展示','层序','FIFO 队列'],['从记录恢复树','互异且相容的先序、中序','定根、分割、递归核对']])+'<p>选择顺序前，先问任务需要哪些信息先就绪。</p>','结构化收口'],
['课后：教材导航与本周作业', '<p><strong>教材导航</strong>：精读 5.5.1，比较递归与非递归遍历；阅读 5.5.2，区分孩子指针和线索。</p><p><strong>A. 书本习题</strong>：第 5 章选择题 <strong>(7)(10)</strong>、应用题 <strong>(1)</strong>、算法设计题 <strong>(1)(3)</strong>。选择题附理由；应用题与算法题写出思路和完整过程。</p><p><strong>B. 扩展作业</strong>：运行 <code>code/traversal_demo.c</code>：先预测主例先序；再将 B 的唯一孩子 D 从右移到左，预测变式的中序、后序和层序，核对 variant 输出；解释求表达式值为何要等子树结果。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B 两部分，末尾附 3–5 行过程记录。<br>自学练习（不提交）：应用题 (2)①；线索化：选择题 (12)(13)、应用题 (2)②。</p>', '课后衔接'],
['访问顺序会设计了，结构本身还能改变吗？', '<p>本讲在给定树上组织访问。<br>下一步：一个结点有很多孩子时，怎样继续使用二叉链接？</p><p class="lead">如果不同叶子被使用的频率不同，树的形状会改变总代价吗？</p><p>D010：树和森林的表示转换与哈夫曼树。</p>', '留下问题'],
]
