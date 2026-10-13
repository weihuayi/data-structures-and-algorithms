"""D008: hierarchy as a computational object; traversal is deferred to D009."""
from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from tree_diagram import tree, beside, gallery

POINTS = [(300, 45), (160, 145), (440, 145), (90, 255), (230, 255), (370, 255), (510, 255)]
EDGES = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('B', 'E'), ('C', 'F'), ('C', 'G')]


def main_tree(indexed=False, positions=False, **kwargs):
    names = ['实验资料/', '模型/', '结果/', '网格.msh', '参数.json', '图像.png', '报告.pdf']
    nodes = {key: (*xy, key, (f'下标 {i}' if indexed else f'位置 {i}' if positions else name))
             for i, (key, xy, name) in enumerate(zip('ABCDEFG', POINTS, names))}
    return tree(nodes, EDGES, caption='实验资料树 · 上方是父结点，连线表示父子关系', level_start=0, **kwargs)


def expression(**kwargs):
    return tree({key: (*xy, label, '') for key, xy, label in zip('ABCDEFG', POINTS, ['×', '−', '+', 'a', 'b', 'c', 'd'])},
                EDGES, caption='表达式 \\((a-b)\\times(c+d)\\) · 左右位置不可混淆', level_start=0, **kwargs)


def shape(keys, caption):
    return tree({key: (*POINTS[i], key, '') for i, key in enumerate('ABCDEFG') if key in keys},
                [(a,b) for a,b in EDGES if a in keys and b in keys], caption=caption)


def single(right=False):
    return tree({'A': (300,45,'A',''), 'B': (440 if right else 160,190,'B','右孩子' if right else '左孩子'),
                 'N': (160 if right else 440,190,'NULL','左位置为空' if right else '右位置为空')},
                [('A','B'),('A','N')], caption='只有右孩子' if right else '只有左孩子', height=270)


def chain():
    return tree({key: (100+i*115,40+i*75,key,f'位置 {2**(i+1)-2}') for i,key in enumerate('ABCD')},
                [('A','B'),('B','C'),('C','D')], caption='右单链 · 每条连线通向右孩子', height=340)



def exhibition_tree():
    return tree({
        'A': (300, 35, 'A', '全馆'),
        'B': (160, 125, 'B', '陶瓷展区'),
        'C': (440, 125, 'C', '青铜展区'),
        'D': (160, 215, 'D', '展柜 01'),
        'E': (440, 215, 'E', '展柜 02'),
        'F': (90, 310, 'F', '青瓷碗'),
        'G': (230, 310, 'G', '白瓷瓶'),
        'H': (440, 310, 'H', '青铜鼎'),
    }, [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'E'),
        ('D', 'F'), ('D', 'G'), ('E', 'H')],
        caption='一种单一归属模型 · A–H 为唯一编号', width=640, height=370)

MATH = True
DECK_ID = 'D008'
TITLE = '树与二叉树：层次组织'


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>' + text + '</p></details>'


def code(text):
    return '<pre>' + escape(text) + '</pre>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>' + x + '</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + x + '</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table>'


def definition(text):
    return '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>' + text + '</div>'


SLIDES = [
['树与二叉树：层次组织', '<p class="lead">一个对象下面还有多个对象，关系怎样进入程序？</p><p>数据结构与算法 · D008</p><p class="small">教材接口：第 5 章 5.1、5.4；遍历在 D009 展开</p>', '课程名'],
['文件名都在，为什么还找不到文件？', '<div class="directory-context"><p>一次计算实验结束后，我们把模型文件、计算结果和实验报告整理进“实验资料”文件夹。现在要交给同学，让他能找到网格文件和结果图像。</p><div class="directory-compare"><section><h3>整理好的目录</h3><ul class="directory-tree"><li><span class="directory-folder">实验资料/</span><ul><li><span class="directory-folder">模型/</span><ul><li><span class="directory-file">网格.msh</span></li><li><span class="directory-file">参数.json</span></li></ul></li><li><span class="directory-folder">结果/</span><ul><li><span class="directory-file">图像.png</span></li><li><span class="directory-file">报告.pdf</span></li></ul></li></ul></li></ul></section><section><h3>只留下名称清单</h3><ul class="directory-flat"><li>实验资料</li><li>模型</li><li>网格.msh</li><li>参数.json</li><li>结果</li><li>图像.png</li><li>报告.pdf</li></ul></section></div><p>只看右侧，能确定“网格.msh”直接放在哪个文件夹里吗？<br>要恢复左侧的组织方式，除了名称，还必须记录什么？</p></div>'+note('需要记录每个文件或子目录直接属于哪个目录。左侧文件夹以文件夹标识和末尾斜线区分，文件以纸张标识区分。报告在结果目录下，与后续主例一致。这里只讨论无链接、单一归属的普通目录。清单可以保存路径或所属目录；不足的是只有名称，不是线性存储本身。'), '问题与对象'],
['怎样把目录中的包含关系记录下来？', beside(main_tree(), '<p>把每个文件或目录记为一个结点，<br>把直接包含关系记为一条边。</p><p>网格.msh（D）直接属于模型/（B），<br>模型/（B）直接属于实验资料/（A）。</p><p>沿 D、B、A，可以找回归属路径；<br>沿 A 向下，可以列出直接包含的目录。</p><p class="small">沿用前页目录；A–G 是唯一标识，名称是数据。图上左右排版不代表文件系统的左右位置。</p>'), '主案例'],
['怎样判断这些关系组成一棵树？', beside(main_tree(focus=('A','B','G')), '<p>① 唯一根：A 没有父结点。</p><p>② 其余结点各有一个父结点。</p><p>③ 沿父关系最终都能到达 A。</p><p>若再让 G 成为 B 的父结点，哪条条件被破坏？</p>') + note('B 已有父结点 A，再加 G 会破坏唯一父结点条件。仅有唯一根、其余单亲仍不够：A 独立为根而 B、C 互为父结点就是反例。'), '条件'],
['树为什么能递归定义？', beside(main_tree(regions=((45,105,235,225,'以 B 为根的子树'),(325,105,235,225,'以 C 为根的子树'))), definition('树是有限个结点的集合，可以为空；非空时有唯一根，其余结点分成若干互不相交的非空集合，每个集合又是一棵树，称为根的子树。') + '<p>去掉 A，两部分仍遵循同样规则。</p>') + note('对应教材 5.1，定义为概述。子树互不相交排除共享结点。一般树不限定两个孩子，本例左右排版不代表左、右位置语义。回收 D006：递归先是对象的定义。'), '教材定义'],
['谁是谁的父结点、孩子和兄弟？', beside(main_tree(focus=('B','D','E'), marked_edges=(('B','D'),('B','E'))), '<p>A 是根，没有父结点。</p><p><strong>D 的父结点是 B。</strong><br>B 的孩子是 D、E。<br>D 与 E 有同一个父结点，是兄弟。</p><p class="small">父结点（教材术语：双亲，parent）。<br>“双亲”在这里指一个父结点，不是两个。</p>'), '关系术语'],
['度和层次分别数什么？', beside(main_tree(focus=('B','D'), levels=True), '<p><strong>度数孩子：</strong>B 的度为 2；<br>树的度是各结点度的最大值，为 2。</p><p>叶子度为 0：D、E、F、G。<br>分支结点度大于 0：A、B、C。</p><p><strong>层次数位置：</strong>根在第 0 层，D 在第 2 层；结点深度等于层编号。</p>') + '<p class="small">本讲高度 height 按层数计：本例共 3 层，最大层编号为 2；空树高度为 0。A 到 D 的路径长为 2。</p>', '数量与位置'],
['同一棵树，可以怎样存？', beside(main_tree(indexed=True, focus=('B','D'), marked_edges=(('B','D'),)), table(['下标 \\(i\\)','0','1','2','3','4','5','6'], [['data','A','B','C','D','E','F','G'],['parent','−1','0','0','1','1','2','2'],['children','1,2','3,4','5,6','空','空','空','空']]) + '<p><code>parent[3] = 1</code><br>D 的父结点是 B；根用 −1 标记。</p><p>孩子表：<code>children[1] = {3,4}</code><br>B 的孩子是 D、E。</p>') + '<p class="small">双亲表示法记录“我属于谁”；孩子表记录“谁属于我”。数组相邻不等于父子相邻。</p>', '计算表示'],
['表示怎样改变操作的代价？', beside(main_tree(indexed=True, focus=('D','B','A'), marked_edges=(('B','D'),('A','B'))), table(['操作（已知结点标识）','双亲数组','孩子表'], [['找父结点','\\(O(1)\\)：读一个元素','\\(O(n)\\)：最坏扫描各表'],['列直接孩子','\\(O(n)\\)：扫描双亲数组','\\(O(k)\\)：读 \\(k\\) 个孩子'],['沿归属路径回到根','\\(O(h)\\)：逐层上行','需反查父结点或增存信息']]) + '<p class="small">孩子表无父指针，表头可直接定位；\\(n\\) 为结点数，\\(k\\) 为孩子数，\\(h\\) 为高度。按名字定位结点的代价另算。</p>' + note('回收 D003/D004：比较的是同一抽象关系上的具体操作。孩子表全扫描的总条目为 \\(n-1\\)，不是每个表都有 \\(n\\) 项。额外存双亲能加速上行，但修改时要保持两套信息一致。')), '表示与选择'],
['改一个父结点，为什么还可能出错？', beside(main_tree(indexed=True, focus=('B','D'), marked_edges=(('B','D'),)), '<p>若只改数组，把模型 B 的父结点设为网格 D：</p>' + code('parent[1] = 3;') + '<p>但 D 原本就在 B 的子树内。</p><p><code>parent[3] = 1</code><br><code>parent[1] = 3</code><br>沿 parent 反复走回原处，无法到根。</p>') + note('真实文件不能容纳子目录；这里暂只检查抽象父关系，说明下标合法仍可能成环。图保留修改前结构，右侧两项明确展示修改后成环。迁移前须排除新父结点在自己的子树内；同时保存孩子表时也要同步更新。下标合法不等于关系合法。'), '不变量回收'],
['算式里，两个孩子能交换吗？', beside(expression(focus=('B','D','E')), '<p>减号的左操作数是 a，<br>右操作数是 b。</p><p>交换后，\\(a-b\\) 变成 \\(b-a\\)。</p><p>除了父子关系，还必须保存<strong>左、右位置</strong>。</p>'), '第二案例'],
['二叉树只是“度不超过 2 的树”吗？', gallery(single(), single(True)) + definition('二叉树可以为空；非空时由根和互不相交的左子树、右子树组成，两棵子树本身也是二叉树。') + '<p>这是两种不同的二叉树。缺失的左、右位置也是结构信息。</p>', '教材定义'],
['左右位置怎样进入 C 结构？', beside(single(True), code('typedef struct Node {\n    char data;\n    struct Node *left;\n    struct Node *right;\n} Node;') + '<p>空树用 <code>NULL</code>；左孩子缺失用 <code>left == NULL</code>。<br>叶子要求左右指针<strong>都为空</strong>。</p>' + note('二叉链表是一种表示，不是二叉树的定义。约定每个非根结点只被一个父结点引用、无环且全部可从根到达。相同 data 不表示同一个结点。')), 'C 表示'],
['怎样在内存中接出这棵树？', beside(expression(focus=('E',)), code("Node a = {'a', NULL, NULL};\nNode b = {'b', NULL, NULL};\nNode minus = {'-', &a, &b};\nNode c = {'c', NULL, NULL};\nNode d = {'d', NULL, NULL};\nNode plus = {'+', &c, &d};\nNode root = {'*', &minus, &plus};") + '<p class="small">这些局部对象在当前函数返回前有效。指针记录关系，不要求结点地址相邻。</p>' + note('课堂代码在 main 内使用这些对象，不返回悬空指针，不涉及动态申请与释放。确认学生能指出 root.left->right 对应 b。')), '程序'],
['“满”和“完全”，从图上怎样判断？', gallery('<div>'+shape('ABCDEFG','满：每层都达到最多结点数')+'</div>', '<div>'+shape('ABCDEF','完全但不满：末层从左连续占据')+'</div>', '<div>'+shape('ABCFG','一般：左侧有空位，不完全')+'</div>') + '<p>满：高度 \\(h\\) 时有 \\(2^h-1\\) 个结点。<br>完全：恰好占据满二叉树按层从左到右编号的前 \\(n\\) 个位置。</p>' + note('所有满二叉树都是完全二叉树。右图每个分支都有两个孩子，但仍不满；本课“满”采用中文教材口径，不混用英文 full 的另一种常见定义。'), '形态与条件'],
['每一层最多多少结点？', beside(expression(levels=True), '<p>根在第 0 层；每个结点最多有两个孩子。</p>' + r'<p>第 \(i\) 层最多 \(2^i\) 个结点（\(i\geq0\)）。</p><p>共 \(h\) 层，编号 \(0\) 至 \(h-1\)，最多：</p><div>\[\sum_{j=0}^{h-1}2^j=2^h-1\]</div>' + '<p>非空二叉树：\\(\\lceil\\log_2(n+1)\\rceil\\le h\\le n\\)。<br>完全二叉树：\\(h=\\lfloor\\log_2 n\\rfloor+1\\)。</p>' + note('本讲 h 按层数计，非空树的最大层编号为 h−1。遇到教材从 1 编层时，先换算编号，不混用公式。上下界分别由尽量填满和单链达到。\\(n=1025\\) 时一般二叉树高度范围为 11 至 1025，完全二叉树高度为 11。式子描述形态，不证明一般二叉树查找为 \\(O(\\log n)\\)。')), '性质的理由'],
['叶子数为什么比双孩子结点多 1？', beside(expression(focus=('D','E','F','G')), '<p>非空二叉树中，\\(n_0\\)、\\(n_1\\)、\\(n_2\\) 分别计数度为 0、1、2 的结点。</p>' + r'<div>\[\begin{aligned}n &amp;= n_0+n_1+n_2\\n-1 &amp;= n_1+2n_2\\n_0 &amp;= n_2+1\end{aligned}\]</div>' + '<p>为什么边数是 \\(n-1\\)？每个非根结点恰好贡献一条入边。</p>' + note('空树不适用 \\(n_0=n_2+1\\)。一般非空树可推广为叶子数 \\(n_0=1+\\sum_{k\\ge1}(k-1)n_k\\)。重点让学生说明同一个量为何能用两种方式数，不把恒等式当成树合法性的充分条件。')), '性质的理由'],
['用编号代替指针，行不行？', beside(main_tree(positions=True), '<p>从 0 起按满二叉树的位置编号，缺失位置仍保留。</p><p>位置 \\(i\\) 的左孩子：\\(2i+1\\)<br>右孩子：\\(2i+2\\)<br>\\(i>0\\) 时父位置：\\(\\lfloor(i-1)/2\\rfloor\\)</p><p>完全二叉树恰好占据 \\(0,\\ldots,n-1\\)。</p>') + '<p class="small">这里为该形状指定左右位置。根的位置为 0。双亲数组下标标识结点，这里的位置还编码左右结构；访问前须检查位置是否存在。</p>', '顺序表示'],
['只有右孩子时，数组会怎样？', beside(chain(), table(['位置','0','1','2','3–5','6','7–13','14'], [['结点','A','空','B','空','C','空','D']]) + '<p>最大位置为 14，要分配 15 个槽位，<br>有效结点只有 4 个。</p><p>若紧凑装入 \\(0,\\ldots,3\\)，<br>\\(2i+1\\)、\\(2i+2\\) 就不再表示原来的孩子。</p>') + '<p class="small">高度 \\(h\\) 的右单链末位置为 \\(2^h-2\\)。空位必须显式标记，不能用某个合法数据值冒充。</p>', '表示的边界'],
['什么时候选数组，什么时候选链式？', table(['需求 / 形态','位置数组','二叉链表'], [['完全二叉树',' \\(n\\) 个连续有效位置；下标定位','可表示，但需两个孩子指针'],['稀疏或偏斜二叉树','可能浪费大量空位置','每个结点固定两个孩子指针'],['已知结点找父结点','可用下标公式','没有父指针时需另找']]) + '<p>空间、定位能力和修改需求共同决定选择。</p>' + note('不把“链式插删 \\(O(1)\\)”无条件搬过来，重接链接前可能要定位、检查约束。本课不讨论 BST 的有序性或堆序，它们是后续追加的性质。'), '判断与选择'],
['先预测：程序会报告什么？', '<p><a href="code/tree_demo.c">code/tree_demo.c</a> 对照三种小树：</p>' + table(['输入','结点数 \\(n\\)','叶子数','高度','最大位置'], [['表达式 \\((a-b)\\times(c+d)\\)','？','？','？','？'],['4 个结点的右单链','？','？','？','？'],['空树','？','？','？','？']]) + '<p class="small">先画图、填表，再编译运行。程序还会拒绝一个双亲成环的输入。</p>' + note('预测：表达式 7、4、3、6；右单链 4、1、4、14；空树前三项为 0，最大位置不存在（程序显示 none）。程序用递归核对统计量，递归展开与访问序在 D009 讲，本课不要求背统计函数。'), '预测'],
['改变输入后，哪些预测需要重做？', '<pre>gcc -std=c11 -Wall -Wextra code/tree_demo.c -o /tmp/d008-tree\n/tmp/d008-tree</pre><p>先预测 expression 与 experiment 的统计量。<br>只把 <code>experiment.right = NULL</code>，再运行并解释变化。</p><p class="small">只改 EXPERIMENT 区域；原例与边界断言继续保留。一次相符只核对当前输入。</p><details class="teacher-note"><summary>教学注记</summary><p>初始 experiment 与原树相同；删右子树后 \\(n=4\\)、叶子数为 2、高度为 3、最大位置为 4。实验结点单独保存根，改其链接不改变基准 root。仅修改 experiment 的左右链接，不能修改共享的子结点或造环。若预测错误，先区分对象变化、编号变化与计算错误。</p></details>', '运行检查'],
['把情境、关系和表示放在一起看', table(['情境','保留的关系 / 条件','C 表达'], [['实验资料归属','唯一父结点、归根可达','parent[i] 或孩子表'],['算术表达式','运算结合、左右操作数','data、left、right'],['完全二叉树位置','层序位置无空洞','数组下标 \\(0,\\ldots,n-1\\)'],['稀疏二叉树','左右缺失位置仍有意义','NULL 或显式占位']]) + '<p>逻辑关系由问题确定，物理存储有不同选择。</p>', '结构化收口'],
['展品、展柜与展出记录，谁是结点？', beside('<div class="tree-explain"><p>查询展品在哪里展出，列出各展区的展品。</p><p>先写：结点、关系是什么？<br>还缺什么约定？</p><details><summary>完成对象判断后，展开共同约定</summary><p>全馆—展区—展柜—展品；唯一编号、单一归属。画至少 6 个结点，比较双亲数组与孩子表查所属展柜的代价。允许多处展出时，模型哪里失效？</p></details><details class="teacher-note"><summary>教学注记</summary><p>2 分钟对象与假设、4 分钟画图和比较、2 分钟互评。先保留原始回答再展开约定。判据：明确实体或展出记录；父子合法；直接按编号访问的双亲数组找父为 \\(O(1)\\)，孩子表通常需反查；多归属须改模型或改为展出记录结点。只给约定后正确图属于有支架应用，不据此声称陌生迁移已达成。</p></details></div>', '<details><summary>完成画图后，展开树形示例</summary>' + exhibition_tree() + '</details>'), '独立学习证据'],
['课后：教材导航与本周作业', '<p><strong>教材导航</strong>：精读 5.1 与 5.4；5.2–5.3 的案例与编码内容在 D010 回收。</p><p><strong>A. 书本习题</strong>：第 5 章选择题 <strong>(2)(3)(4)(5)(8)</strong>。每题附一句“为什么选它”，计算题写出推导过程。</p><p><strong>B. 扩展作业</strong>：运行 <code>code/tree_demo.c</code>：预测原表达式树，再仅令 experiment.right=NULL，提交四项统计量的前后预测、实测与解释；说明主要查所属展柜时选择哪种表示及理由。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B 两部分，末尾附 3–5 行过程记录。<br>自学练习（不提交）：举出一个“最多两个孩子，却未定义左右位置”的层次对象。</p>', '课后衔接'],
['结点已经连好，怎样不重不漏地访问？', '<p>表达式树保留了运算的结合关系，实验资料树保留了归属关系。</p><p class="lead">但从根开始，先访问谁、后访问谁？</p><p>下一讲 D009：遍历与系统访问。<br>回到 D006 的递归、D005 的栈与队列。</p>', '留下问题'],
]
