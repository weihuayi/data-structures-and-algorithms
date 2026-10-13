"""D010: preserving hierarchy through representation; optimizing weighted paths."""
from html import escape
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from tree_diagram import tree, beside, gallery
from tree_trace import player
from huffman_trace import merge_states, decode_states

DECK_ID = 'D010'
TITLE = '树和森林与哈夫曼'
MATH = True


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>' + text + '</p></details>'


def code(text):
    return '<pre>' + escape(text) + '</pre>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>' + x + '</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + x + '</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table>'


def definition(text):
    return '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>' + text + '</div>'



def fold(title, body):
    return '<details><summary>'+title+'</summary>'+body+'</details>'


def forest(binary=False):
    if binary:
        points={'A':(300,35),'B':(180,130),'G':(490,130),'E':(80,230),'C':(280,230),'H':(440,230),'F':(150,330),'D':(350,330)}
        edges=[('A','B'),('A','G'),('B','E'),('B','C'),('G','H'),('E','F'),('C','D')]
        labels=dict(zip(edges,['L','R','L','R','L','R','R']))
    else:
        points={'A':(240,35),'B':(120,160),'C':(270,160),'D':(370,160),'E':(60,300),'F':(180,300),'G':(500,35),'H':(500,160)}
        edges=[('A','B'),('A','C'),('A','D'),('B','E'),('B','F'),('G','H')]
        labels={}
    return tree({k:(*v,k,'') for k,v in points.items()},edges,caption='L：第一个孩子；R：下一个兄弟（根也沿 R 串接）' if binary else '根次序 A、G；孩子次序从左到右',height=380,edge_labels=labels)


MERGES=merge_states([8,4,2,2])
NODES=MERGES[-1]['nodes']
ROOT=MERGES[-1]['roots'][0]


def huff_diagram(nodes=NODES, roots=None, selected=(), edge=None, symbols='ABCD'):
    roots=[ROOT] if roots is None else roots
    points={}; edges=[]; labels={}; cursor=0
    def place(k,depth):
        nonlocal cursor
        n=nodes[k]
        if n['left'] is None:
            x=70+cursor*140; cursor+=1
        else:
            left=place(n['left'],depth+1); right=place(n['right'],depth+1); x=(left+right)/2
            for child,bit in [(n['left'],'0'),(n['right'],'1')]:
                edges.append((k,child)); labels[(k,child)]=bit
        label=symbols[k] if n['symbol'] else str(n['weight'])
        points[k]=(x,35+depth*95,label,str(n['weight']) if n['symbol'] else '')
        return x
    for k in roots: place(k,0)
    return tree(points,edges,caption='叶子下方为权值；内部结点为子树权值和；边标 0 / 1',height=380,
                focus=selected,marked_edges=[edge] if edge else [],edge_labels=labels)


def merge_player():
    panels=[]
    for state in MERGES:
        roots='、'.join((state['nodes'][k]['symbol'] or '新树')+str(state['nodes'][k]['weight']) for k in state['roots'])
        body='<p class="trace-action">'+state['action']+'</p><p>待选根：'+roots+'</p><p>累计合并代价：'+str(state['cost'])+'</p><p class="small">橙色标出本步选择或生成的根；并列按结点编号选择。</p>'
        panels.append(beside(huff_diagram(state['nodes'],state['roots'],state['selected']),body))
    return player(panels,'哈夫曼逐轮合并').replace('class="tree-player"', 'class="tree-player tree-spacious"')


def decode_player():
    bits='010110111'; panels=[]
    for state in decode_states(NODES,ROOT,bits):
        i=state['read']
        body='<p>已读 <code>'+bits[:i]+'</code> ｜ 待读 <code>'+bits[i:]+'</code></p><p class="trace-action">'+state['action']+'</p><p>已输出：<strong>'+(state['output'] or '空')+'</strong></p><p class="small">橙色为当前结点；到叶子才输出，然后回根。</p>'
        panels.append(beside(huff_diagram(selected=[state['current']],edge=state['edge']),body))
    return player(panels,'按位译码').replace('class="tree-player"', 'class="tree-player tree-spacious"')


SLIDES = [
['树和森林与哈夫曼', '<p class="lead">树的表示可以转换，树的形状也可以优化。</p><p>数据结构与算法 · D010</p><p class="small">教材接口：5.6–5.7；回收 5.2–5.3 的编码案例</p>', '课程名'],
['给定的树之外，还能设计什么？', '<p>D009 解决了：在给定结构上安排访问顺序。</p><ol><li>一个结点有多个孩子，怎样只用两个链接保存关系？</li><li>有些叶子使用得更频繁，怎样让总代价更低？</li></ol><p>前一个问题先保留关系，后一个问题允许改变树形。</p>', '回收留问'],
['两份独立的资料目录，怎样作为一个对象？', beside(forest(), definition(r'森林是 \(m\)（\(m\geq0\)）棵互不相交的树的集合。')+'<p>A、G 为两份项目目录；B 为模型，C 为结果，D 为报告；E、F 是 B 下的网格与参数，H 为 G 下的数据。</p><p class="small">固定根与孩子的次序，结点标识互异。</p>'), '对象与关系'],
['双亲、孩子、兄弟：保存哪一条关系？', table(['表示','每个结点记录什么','直接支持的操作'], [['双亲表示','一个父结点编号','找父结点'],['孩子表示','直接孩子的列表','依次列出孩子'],['孩子兄弟表示','第一个孩子、下一个兄弟','进入孩子层、沿同层继续']]) + '<p>回收 D008：一个逻辑对象可以有多种表示。<br>兄弟次序先约定，才谈具体转换结果。</p>' + note('对应 5.6.1。若原树无序，先选择孩子顺序；所得二叉形态不必唯一。这里不把排列选择误认为改变父子归属。'), '表示选择'],
['两个链接怎样容纳任意多个孩子？', code('typedef struct CSNode {\n    char id;\n    struct CSNode *first_child;\n    struct CSNode *next_sibling;\n} CSNode;') + '<p>A 的第一个孩子是 B；B 的下一个兄弟是 C，C 的下一个兄弟是 D。</p><p>列出 A 的孩子：从 B 开始，沿兄弟链接依次走到 C、D。</p>', 'C 表示'],
['同一批结点，两种链接含义', gallery(forest(),forest(True))+'<p class="small">C 的原父结点是谁？沿右链 B、C、D 还原 A 的孩子。</p>'+note('C 的原父为 A，不是 B；G 是另一个根。L / R 是存储链接语义，不把 R 当作原对象的父子关系。'), '转换规则'],
['怎样把二叉链接读回森林？', beside(forest(True),'<ol><li>沿根的右链分出 A、G。</li><li>左链接给出第一个孩子。</li><li>沿该孩子的右链找其余孩子，逐层重复。</li></ol>')+note('A 的孩子为 B、C、D；B 的孩子为 E、F；G 的孩子为 H。孩子链与根链必须无环、不共享结点。'), '反向检查'],
['原树的后根遍历，对应二叉树的什么顺序？', table(['原森林（按根与孩子次序）','二叉表示','本例序列'], [['先序：根，再各孩子子树','先序 NLR','A B E F C D G H'],['后序：各孩子子树，再根','中序 LNR','E F B C D A H G']]) + '<p>左边编码“孩子”，右边编码“后续兄弟”。<br>原树的后根顺序，不能直接照搬成二叉后序。</p>' + note('对应 5.6.3。森林先序为各树先根序串接；这里的森林后序按各树后根序串接，教材也常称森林中序。请学生以原关系定义为准核对。二叉中序先处理孩子链、再根、再后续兄弟，恰好符合这一顺序。'), '回收遍历'],
['先预测：转换后哪些量会变？', beside(forest(True),'<p>预测 A 的孩子数、两条遍历序列和空右链接数，再运行 <a href="code/forest_demo.c">森林程序</a>核对。</p><p class="small">程序用下标代替指针：A 对应 0，<code>first[0]=1</code> 指向 B，<code>next[1]=2</code> 从 B 指向 C；<code>-1</code> 为空。</p>')+note(r'A 有 3 个孩子；先序 ABEFCDGH，后序 EFBCDAHG（回收前页结果）。空右链接为 D、F、G、H，共 4 个。非空森林有 \(q\) 个非叶结点时，孩子链末尾各贡献一个，根链末尾再贡献一个，共 \(q+1\)。空森林另算。'), '预测与检查'],
['四种消息都用两位编码，够好吗？', '<p>假设一批 16 条状态消息只有四种类型：</p>' + table(['符号','A','B','C','D'], [['出现次数','8','4','2','2'],['等长编码','00','01','10','11']]) + '<p>消息内容占 \\(16\\times2=32\\) bit。<br>频繁出现的 A，能不能比其他消息更短？</p><p class="small">教学构造数据；暂只比较编码后的消息内容，不计码表和文件头。</p>', '代价问题'],
['码字变短以后，怎样知道在哪里断开？', code('若 A=0，B=01，C=1\n收到 01：可能是 B，也可能是 A C') + '<p>仅让每个符号的码字不同，还不够。</p>' + definition('前缀编码：任何一个字符的编码都不是另一个字符编码的前缀。') + '<p class="small">它允许从左向右即时确定码字边界。前缀条件是唯一译码的充分条件，并非必要条件。</p>', '编码条件'],
['把符号放在叶子上，能保证什么？', beside(huff_diagram(),'<p>从根到叶子的边标组成码字：<br>A：<code>0</code>，B：<code>10</code><br>C：<code>110</code>，D：<code>111</code></p><p>叶子不是其他叶子的祖先，因此码字互不为前缀。</p>')+note('先展示可行编码树；能译码不直接证明最优。内部结点不放符号。'), '编码树'],
['怎样把“短一些”写成可比较的目标？', definition('带权路径长度是叶子权值与根到叶子路径长度的乘积之和；使给定叶子权值的 WPL 最小的二叉树称为哈夫曼树。')+r'<p>\[\operatorname{WPL}=\sum_{i=1}^{n}w_i\ell_i=8\times1+4\times2+2\times3+2\times3=28\]</p><p>\[\bar\ell=\frac{\operatorname{WPL}}{\sum_{i=1}^{n}w_i}=\frac{28}{16}=1.75\quad\text{bit/符号}\]</p><p class="small">\(\ell_i\) 数边，根深度为 0，与 D008 从 0 开始的层编号一致。内部权值不直接计入求和。</p>', '目标函数'],
['同样四个符号，树形改变了多少代价？', table(['方案','A、B、C、D 的码长','加权总位数'], [['等长编码','2、2、2、2','32'],['第 12 页的树','1、2、3、3','28'],['把 A 与 D 的位置交换','3、2、3、1','40']]) + '<p>树形和符号位置共同影响代价。<br>若权值大却放得深，频繁操作就会反复付出长路径的成本。</p>' + note('交换变化量为 \\((8-2)(3-1)=12\\)，\\(28+12=40\\)。树高低不是唯一优化目标；本例较高的树反而比等长树的 WPL 更低。'), '比较与判断'],
['怎样一步步构造低代价的树？', merge_player()+note(r'本讲取正权值、\(n\geq2\) 个符号。每轮从全部待选根中取两个最小者，合并后放回，直至一棵；共 \(n-1\) 轮。并列先取结点编号较小者放左侧只是复现约定，不是最优性的必要条件。'), '哈夫曼算法'],
['合成项放回后，下一轮选谁？', '<p>回看第 15 页主例，再补全 A6、B3、C2、D1。</p>'+table(['轮次','选中的两棵树','新根权值'],[['1','D1 与 C2',r'\(1+2=3\)'],['2','____ 与 ____','____'],['3','____ 与 ____','____']])+'<p>第一轮后待选：B3、新树3、A6。<br>为什么新树必须参与下一轮比较？</p>'+note(r'补全为 \(3+3=6\)、\(6+6=12\)，\(\operatorname{WPL}=3+6+12=21\)。合成项代表一组符号，必须重新参与最小选择；不要求每轮重新排序全部对象。第 24 页再独立构造。'), '示例与补全'],
['为什么合并权值之和恰好等于 WPL？', beside(huff_diagram(),r'<p>合并 C、D：两片叶子各加深一层，增量 \(2+2=4\)。</p><p>再接入 B：增量 \(4+2+2=8\)。</p><p>最后接入 A：增量 \(8+4+2+2=16\)。</p><p>\(\operatorname{WPL}=4+8+16=28\)</p>')+note('每片叶子的权值被累计的次数等于深度。合并和恒等式不限于最小合并，两种计算相等本身不能证明最优。'), '代价核对'],
['为什么先合并最小两项是安全的？', '<ul><li>可以选取一棵最优树，使两个最小权值处在最深的一对兄弟叶子上。</li><li>把这对兄弟收缩成权值之和，得到更小的同类问题。</li><li>较小问题的最优树展开这对叶子，就给出原问题的最优树。</li></ul><p>安全选择加上规模缩小，让局部选择可以持续进行。</p>' + note('理由展开：正权下可去掉只有一个孩子的内部结点而降低 WPL，因此只需考虑每个内部结点有两个孩子的树。取最深兄弟叶子，把最小两权交换到那里不会增加代价，因为把小权移深、大权移浅的变化量 \\(\\leq0\\)。收缩后若还能改进，展开即改进原树，矛盾。展开多付的固定量为两权之和。这是证明提纲，不以一个例子代替普遍理由。'), '成立理由'],
['合成结点怎样存进 C 数组？', '<div class="tree-swap"><div class="tree-preview">'+code('typedef struct {\n    unsigned long long weight;\n    int parent, left, right;\n} HNode;\n// 0 .. n-1 为叶子；-1 表示空链接')+'</div>'+fold('展开第一轮合并的数组记录',table(['下标','weight','parent','left / right'],[['2（C）','2','4','-1 / -1'],['3（D）','2','4','-1 / -1'],['4（新根）','4','-1','2 / 3']]))+'</div>'+r'<p>每轮选两个无父结点的最小根，再新建父结点。<br>\(n\) 个叶子、\(n-1\) 个内部结点，共 \(2n-1\) 个结点。</p>'+note('数组下标是记录编号，不是完全二叉树层序位置。两个孩子不表示每层填满；生成码字时沿 parent 回溯，再反转。'), '计算表示'],
['树最优了，实现就一定快吗？', table(['工作','本演示实现','代价（n 个符号）'], [['每轮选两个最小根','扫描尚未被合并的根','单轮 \\(O(n)\\)，构树 \\(O(n^2)\\)'],['从叶子生成码字','沿父链接回溯再反转','总计 \\(O(\\sum_i\\ell_i)\\)，最坏 \\(O(n^2)\\)'],['译码','逐位沿树走，到叶子回根','\\(O(L)\\)，\\(L\\) 为输入位数']]) + '<p>最优 WPL 描述编码目标；构造算法的运行成本是另一件事。</p>' + note('若用最小优先队列，构树可做到 \\(O(n\\log n)\\)，堆的机制留待 D020。存树 \\(O(n)\\)，若保存所有码字，最坏需要 \\(O(n^2)\\) 字符。本课固定容量仅服务小规模演示。'), '算法代价'],
['收到 010110111，怎样还原消息？', decode_player()+note('完整切分为 0 / 10 / 110 / 111，输出 ABCD。输入 11 结束于内部结点，末尾码字不完整。前缀编码不自动检测所有传输错误，也不等于纠错。'), '译码与边界'],
['先预测：两组频率还会得到相同收益吗？', '<p><a href="code/huffman_demo.c">code/huffman_demo.c</a> 对照两组权值：</p>' + table(['输入','合并权值之和','WPL','等长位数'], [['8、4、2、2','？','？','32'],['4、4、4、4','？','？','32']]) + '<p>先预测，再运行：比较码长与总代价，并检查 <code>ABCD</code> 编码后能否还原。</p>' + note('第一组 28、28、32，平均码长 1.75；第二组 32、32、32，平均码长 2。并列权可有不同合法码字，比较 WPL、前缀性和往返结果，不能只比较某一串 0/1。两例码表见程序输出。'), '预测与运行'],
['少了 4 bit，就一定让文件更小吗？', '<p>本例内容从 32 bit 降到 28 bit，节省 \\(12.5\\%\\)。</p><ul><li>解码端还需要知道码表或树。</li><li>文件可能包含长度、头部和字节对齐填充。</li><li>短消息的额外开销可能超过节省量。</li></ul><p class="small">哈夫曼在给定权值的二元逐符号前缀编码中最优，不表示对所有压缩方法或完整文件都最优。</p>' + note('码表需与当前编码一致。单符号字母表的结构深度是 0，本演示约定码字为 0，于是线上码长为 1，另行处理。零频符号本演示拒绝，可在建模时移出字母表。'), '适用边界'],
['换一组频率，你能独立优化结构吗？', code('四种事件 P、Q、R、S 的次数为：5、2、1、1') + '<ol><li>手工完成每轮最小合并，画出编码树。</li><li>给出码字、WPL 与平均码长。</li><li>与每个符号 2 bit 的方案比较，并说明优化的量。</li></ol>' + note('保留 7 分钟独立作答、2 分钟核对。合并权值 2、4、9，\\(\\operatorname{WPL}=15\\)，平均 \\(15/9=5/3\\)；等长为 18。一个可行码表 P=1、Q=00、R=010、S=011。并列情况下允许其他最优结果，判定须包含前缀性、每轮选择和代价，不要求码字逐字相同。'), '独立构造'],
['两种“改变树”，分别保持什么、改变什么？', table(['操作','必须保持','改变 / 目标'], [['树或森林转孩子兄弟表示','原结点、父子归属、约定次序','链接含义与存储方式'],['按频率构造哈夫曼树','符号、权值、前缀编码条件','树形与码长，使 WPL 最小'],['根据码树译码','码表一致、码字边界有效','位串恢复为符号串']]) + '<p>先明确对象和条件，再决定哪些结构可以改变。</p>', '结构化收口'],
['课后：教材导航与本周作业', '<p><strong>教材导航</strong>：精读 5.6–5.7，回看 5.2–5.3 的编码案例。</p><p><strong>A. 书本习题</strong>：第 5 章选择题 <strong>(1)(9)(11)(14)</strong>、应用题 <strong>(2)③、(3)</strong>。选择题附理由；应用题给出转换、构造与计算过程。</p><p><strong>B. 扩展作业</strong>：对新权值 A7、B3、C2、D1，先提交合并过程、码表、WPL、平均码长与等长比较；运行 <code>code/huffman_demo.c</code> 核对 homework 输出及 ABCD 往返译码。码字不同须解释是否仍最优。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B，附 3–5 行过程记录。<br>自学练习（不提交）：选择题 (6)、应用题 (4)；应 (2)③ 可先借助 D009 的恢复方法画出题设二叉树。</p>', '课后衔接'],
['一个对象可以同时连接多个对象，树还够用吗？', '<p>树与森林保留了单一归属的层次关系。<br>编码树则用路径表达符号，按代价优化树形。</p><p class="lead">道路之间可以成环，一个地点也可能连接多个方向，该怎样表示？</p><p>D011：图与一般关系结构。</p>', '留下问题'],
]
