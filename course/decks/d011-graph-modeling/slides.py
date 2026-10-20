"""D011: model general relations; compare representations before traversal."""
from html import escape

DECK_ID = 'D011'
TITLE = '图：一般关系结构'
MATH = True

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools/deck'))
from graph_diagram import graph, beside


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>' + text + '</p></details>'


def code(text):
    return '<pre>' + escape(text) + '</pre>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>' + x + '</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + x + '</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table>'


def definition(text):
    return '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>' + text + '</div>'



NODES = {'A': (65, 60), 'B': (275, 60), 'C': (170, 205), 'D': (365, 205), 'E': (465, 60)}
ROADS = [('A','B'), ('A','C'), ('B','C'), ('C','D')]
TIMES = {('A','B'):4, ('A','C'):0, ('B','C'):2, ('C','D'):3, ('D','B'):1}


def roads(marked=(), edges=None):
    return graph(NODES, ROADS if edges is None else edges, caption='道路：AB、AC、BC、CD；E 孤立。虚线粗边为当前讨论关系。', marked=marked)


def times():
    return graph(NODES, list(TIMES), caption='独立的单向时间网；标数单位为分钟，位置不表示距离。', directed=True, labels=TIMES)


def matrix():
    return table(['','A','B','C','D','E'], [[u]+[('<span class="graph-mark">1</span>' if {u,v}=={'B','C'} else str(int((u,v) in ROADS or (v,u) in ROADS))) for v in NODES] for u in NODES])


def lists():
    return code('A: [B] → [C] → NULL\nB: [A] → [C]* → NULL\nC: [A] → [B]* → [D] → NULL\nD: [C] → NULL\nE: NULL')


def answer(text, title='核对答案与理由'):
    return '<details><summary>'+title+'</summary>'+text+'</details>'


SLIDES = [
['图：一般关系结构', '<p class="lead">当连接可以成环，也没有唯一的父结点，怎样组织计算？</p><p>数据结构与算法 · D011</p><p class="small">教材接口：6.1–6.3；6.4.1–6.4.2 的表示对照先行引入</p>', '第一节 · 从现实关系到图模型'],
['今天我们要解决哪四个问题？', '<table><thead><tr><th>节次</th><th>问题</th></tr></thead><tbody><tr><td>第一节</td><td>哪些现实关系需要图？</td></tr><tr><td>第二节</td><td>直接相邻与沿路可达有何不同？</td></tr><tr><td>第三节</td><td>同一张图怎样存入计算机？</td></tr><tr><td>第四节</td><td>操作与资源怎样决定表示选择？</td></tr></tbody></table>', '第一节 · 从现实关系到图模型'],
['第一节：为什么需要图？', '<p class="lead">从一张道路网开始，确定对象、关系和需要保留的信息。</p><p>先观察连接，再写数学对象。</p>', '第一节 · 从现实关系到图模型'],
['为什么不能把所有关系都组织成树？', beside(roads(), '<p>若每个站点只留一个父站点，哪些道路会丢失？</p><p>三角形 A—B—C—A 不能完整放进一棵树。</p><p>树是连通且无环的特殊无向图；选一棵树会舍去原图的部分关系。</p>'), '第一节 · 从现实关系到图模型'],
['哪些站点之间存在直接连接？', beside(roads(), '<p>道路清单：AB、AC、BC、CD，均可双向通行。</p><p>站点 E 尚无道路接入，但必须保留。</p><p>请逐条核对端点：A 与 D 直接相连吗？</p>'), '第一节 · 从现实关系到图模型'],
['如何从道路网络建立数学对象？', '<table><thead><tr><th>情境信息</th><th>计算对象</th><th>本讲约定</th></tr></thead><tbody><tr><td>站点 A–E</td><td>顶点（Vertex）集合 V(G)</td><td>标识互异，位置编号固定</td></tr><tr><td>两站之间直接相通</td><td>边（Edge）集合 E(G)</td><td>无自环，无重复边</td></tr><tr><td>行驶方向 / 时间</td><td>方向 / 边权</td><td>按任务需要明确加入</td></tr></tbody></table><p>V(G)={A,B,C,D,E}；E(G)={AB,AC,BC,CD}。</p><details class="teacher-note"><summary>教学注记</summary><p>站点名 E 与边集 E(G) 需区分，讲授时读作“站点 E”与“边集合”。公式中 G=(V,E) 沿教材标准记法，程序用 edges 避免混淆。现实道路可有平行路线，本讲简单图模型只保留每对地点最多一条关系。</p></details>', '第一节 · 从现实关系到图模型'],
['什么是图？', '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>图（Graph）\\(G=(V,E)\\) 由顶点的非空有限集合 V 和边的有限集合 E 构成。无向图的边表示无序顶点对；有向图的弧表示有序顶点对。</div><p>无向边 {A,B}={B,A}，只计一条边。<br>有向弧 ⟨A,B⟩ 与 ⟨B,A⟩ 是两个可能不同的关系。</p><p class="small">本讲采用简单图：无自环、无重边；允许边集为空。</p>', '第一节 · 从现实关系到图模型'],
['方向与权值改变了什么？', beside(times(), '<p>有向图（Directed Graph）：箭头保存允许通行的方向，反向弧不自动存在。</p><p>权值保存通行时间；带权图也称网。</p><p>A→C 的 0 是即时转接，仍有边。</p><p class="small">这是独立约定的五条弧，不能由道路图直接推出。</p>'), '第一节 · 从现实关系到图模型'],
['第二节：图中的关系意味着什么？', '<p class="lead">连接给出一步能去哪里；路径回答多步能否到达。</p><p>用路径、度数和反例检查我们对关系的理解。</p>', '第二节 · 理解图中的关系'],
['不直接相邻，是否仍然可以到达？', beside(roads(marked=[('A','C'),('C','D')]), '<p>A、D 不邻接，却可沿 A—C—D 到达。</p><p>站点 E 无法从其他顶点到达。</p>'+definition('无向图任意两顶点间都有路径时称连通；极大连通子图称连通分量。')+'<p class="small">本例分量：{A,B,C,D}、{E}；极大不是全图最大。</p>'), '第二节 · 理解图中的关系'],
['路径、路径长度与环怎样定义？', beside(roads(marked=[('A','B'),('B','C'),('A','C')]), definition('路径是相邻顶点连接成的序列；路径长度为经过的边或弧数。首尾相同的路径称回路或环。')+'<p>A—C—D：长度 2。A—B—C—A：环。</p><p class="small">简单路径不重复顶点；简单环除首尾外不重复顶点。</p>'), '第二节 · 理解图中的关系'],
['方向改变后，可达性会怎样变化？', beside(times(), '<p>A 能到 B，B 却不能回到 A。</p><p>A→C→D：2 条弧，总权值 3。<br>A→B→C→D：3 条弧，总权值 9。</p><p>边数与总权值是不同量。</p>')+note('强连通要求任意不同顶点间均有双向有向路径。本例强连通分量为 {A}、{B,C,D}、{E}，不展开算法。'), '第二节 · 理解图中的关系'],
['怎样通过度数检查图的关系？', '<table><thead><tr><th>图</th><th>顶点 A、B、C、D、E</th><th>总和</th></tr></thead><tbody><tr><td>无向主例的度</td><td>2、2、3、1、0</td><td>8=2×4</td></tr><tr><td>有向时间网的出度</td><td>2、1、1、1、0</td><td>5</td></tr><tr><td>有向时间网的入度</td><td>0、2、2、1、0</td><td>5</td></tr></tbody></table><p>\\(\\sum_v d(v)=2m\\)；\\(\\sum_v d^+(v)=\\sum_v d^-(v)=m\\)。<br>无向边为两个端点各贡献 1；有向弧贡献一次出度、一次入度。</p><details class="teacher-note"><summary>教学注记</summary><p>回收 D008 的双重计数。自环口径此处不展开，因为模型已排除自环。孤立顶点的度是 0，但它仍是顶点集合的一员。</p></details>', '第二节 · 理解图中的关系'],
['有 n−1 条边就一定是树吗？', '<table><thead><tr><th>对象（无向简单图语境）</th><th>连接条件</th><th>边数关系</th></tr></thead><tbody><tr><td>树</td><td>连通且无环</td><td>n 个顶点有 \\(n-1\\) 条边</td></tr><tr><td>森林</td><td>无环，可有多个分量</td><td>c 个分量时 m=n−c</td></tr><tr><td>一般图</td><td>可能有环，也可能不连通</td><td>只靠 m=\\(n-1\\) 不能判定是树</td></tr></tbody></table><p>主例 \\(n=5,m=4\\)，却有三角形 A—B—C—A 和孤立点 E。</p><details class="teacher-note"><summary>教学注记</summary><p>无向图的“根”可以为任务另选；图本身未必指定根。主例正好提供 \\(n-1\\) 条边但不是树的反例。</p></details>', '第二节 · 理解图中的关系'],
['第三节：计算机怎样保存一张图？', '<p class="lead">同一个逻辑图，能否用不同存储方式完成相同操作？</p><p>先列操作，再建立图、矩阵、链表与 C 字段的对应。</p>', '第三节 · 将图转换为计算表示'],
['为了使用图，需要哪些基本操作？', '<p>图与基本操作构成抽象数据类型（Abstract Data Type，ADT）。</p><table><thead><tr><th>需求</th><th>操作接口</th><th>应回答什么</th></tr></thead><tbody><tr><td>能否直接从 u 到 v</td><td>has_edge(u,v)</td><td>存在 / 不存在 / 顶点非法</td></tr><tr><td>从 u 可以直接去哪</td><td>neighbors(u)</td><td>所有邻接顶点及边权</td></tr><tr><td>一条道路关闭</td><td>remove_edge(u,v)</td><td>删除关系，保持表示一致</td></tr></tbody></table><p>接口描述图的行为。矩阵、链表只是实现这些操作的不同办法。</p><details class="teacher-note"><summary>教学注记</summary><p>教材 6.3 图的类型定义还有顶点增删等操作。本讲选固定顶点集合的局部接口；邻接不等于可达。完整 DFS/BFS 与邻接访问迭代在 D012 回收。</p></details>', '第三节 · 将图转换为计算表示'],
['怎样用矩阵保存图中的边？', beside(roads(marked=[('B','C')]), matrix())+'<p class="small">邻接矩阵（Adjacency Matrix）：行列顺序 A–E；1 有边、0 无边。粗虚线 BC ↔ 下划线两格 M[B][C]、M[C][B]。</p>', '第三节 · 将图转换为计算表示'],
['矩阵的哪些性质来自图的关系？', '<ul><li>无向图满足 M[u][v]=M[v][u]。</li><li>无自环，所以对角线全为 0。</li><li>无向主例共有 8 个 1，对应 4 条边。</li></ul><p>改为有向图后，行描述出边，列描述入边，矩阵不必对称。</p><details class="teacher-note"><summary>教学注记</summary><p>先让学生在第 17 页独立数一行、一列、所有非零项。不能把对称性推广到有向图，也不能把二值邻接矩阵的“非零个数”规则不加区分地用于允许零权边的权值矩阵。</p></details>', '第三节 · 将图转换为计算表示'],
['权值为 0，与不存在的边怎样区分？', beside(times(), table(['顶点对','present','weight'],[['A→C','true','0（即时转接）'],['A→E','false','不解释']])+code('bool present[MAX_V][MAX_V];\nint weight[MAX_V][MAX_V];'))+'<p class="small">教材以 ∞ 编码无边；本程序把存在性与权值分开。不能用 weight != 0 判断有边。</p>', '第三节 · 将图转换为计算表示'],
['怎样只保存实际存在的邻居？', beside(roads(marked=[('B','C')]), lists())+'<p class="small">邻接表（Adjacency List）：* 是 BC 的两份邻接项。→ 仅是 next 链接，不是道路；E 仍占一个表头。固定编号与编码后矩阵唯一，邻接表记录顺序可以改变。</p>', '第三节 · 将图转换为计算表示'],
['有向图的邻接表如何保存方向？', beside(times(), code('出邻接（邻居,权值）\nA: (B,4) → (C,0) → NULL\nB: (C,2) → NULL\nC: (D,3) → NULL\nD: (B,1) → NULL\nE: NULL'))+'<p class="small">每条弧只记在弧尾的出表；逆邻接表按弧头记入邻居，例如 B 的入邻居为 A、D。</p>', '第三节 · 将图转换为计算表示'],
['C 程序中的字段对应什么？', '<pre>typedef struct Arc {\n    int to, weight;\n    struct Arc *next;\n} Arc;\n\nArc *head[MAX_V]; // head[u] 指向 u 的出边表</pre><p>编号 A=0、B=1、C=2、D=3、E=4；C 表的 to 依次为 0、1、3。</p><p>回收 D004：next 表示下一个记录，不是道路。<br>顶点 E 即使没有边，也保留自己的表头位置。</p><details class="teacher-note"><summary>教学注记</summary><p>演示使用动态申请的边结点，结束时释放；构造失败释放已经申请的所有结点。按编号递增列邻居只是为了便于手工核对，查询仍按线性扫描实现。</p></details>', '第三节 · 将图转换为计算表示'],
['同一张图，你能构建两种表示吗？', '<p>4 分钟：无向图 V={X,Y,Z,W}，边 XY、YZ，W 孤立。行列顺序 X、Y、Z、W。</p>'+code('矩阵 Y 行：[ __, __, __, __ ]\n邻接表 X: __   Y: __   Z: __   W: __')+'<p>填写并解释：一条 YZ 边对应哪些矩阵位置、哪些邻接项？</p>'+answer('<p>Y 行：[1,0,1,0]；X:[Y]，Y:[X,Z]，Z:[Y]，W:空。YZ 对应 M[Y][Z]、M[Z][Y]，以及 Y 表的 Z 和 Z 表的 Y。</p>'), '第三节 · 将图转换为计算表示'],
['第四节：为什么需要选择表示？', '<p class="lead">逻辑关系相同，访问哪些存储位置却不同。</p><p>逐项观察查边、列邻居、删边，再结合规模与工作负载作判断。</p>', '第四节 · 操作、代价与表示选择'],
['判断指定边是否存在，两种表示各做什么？', beside(roads(marked=[('B','C')]), '<p>查 BC：矩阵直达 M[B][C]。</p>'+code('B 表： [A] → [C] → NULL\n         ①     ② 找到 C')+'<p>若查 BD，则读完 B 的两个记录仍未找到。</p>')+r'<p class="small">已知有效编号、表示已构造：矩阵 \(O(1)\)；链表最坏 \(O(1+d(u))\)，有向出表用 \(d^+(u)\)。名字查编号和构造成本另计。</p>', '第四节 · 操作、代价与表示选择'],
['枚举一个顶点的邻居，工作量为何不同？', beside(roads(marked=[('A','C'),('B','C'),('C','D')]), code('矩阵 C 行： [1][1][0][1][0]\n检查位置：   A  B  C  D  E\n邻接表 C： [A] → [B] → [D]\n访问条目：  ①     ②     ③'))+r'<p>矩阵扫描 5 格：\(\Theta(n)\)；邻接表访问 3 项：\(\Theta(1+d(C))\)。空表仍有常数开销。</p>', '第四节 · 操作、代价与表示选择'],
['图的规模怎样影响空间与表示选择？', r'<p>无自环、无重边：无向图最多 \(n(n-1)/2\) 条边；有向图最多 \(n(n-1)\) 条弧。</p>'+table(['按规模分配','普通矩阵','普通邻接表'],[[r'空间',r'\(\Theta(n^2)\)',r'\(\Theta(n+m)\)；无向有 2m 项'],['n=10000，m=30000','一亿个位置','一万表头 + 三万弧项 / 六万无向项']])+'<p class="small">少量边、主要枚举时通常倾向表；大量指定对查询时还要权衡矩阵内存、查询频率与常数。不是仅按稀疏/稠密决定。</p>'+note('顶点对计数：无向每对计一次，有向每对有两个方向。若每矩阵位置4字节，一亿位置约400 MB，不含顶点及辅助信息；演示 MAX_V=8 固定容量不做此规模实测。矩阵转表扫描 n² 格，与建好表示上的查询是不同成本。非连通图上界 (n−1)(n−2)/2；8 顶点最多21边，9 顶点可有28边，服务选择(5)。'), '第四节 · 操作、代价与表示选择'],
['删除一条无向边，必须维护什么？', beside(graph(NODES, [('A','B'),('A','C'),('C','D')], caption='删除 BC 后：AB、AC、CD；E 仍孤立。'), code('M[B][C]、M[C][B]：1 → 0\nB 表：[A,C] → [A]\nC 表：[A,B,D] → [A,D]'))+'<p class="small">删除一条边，同步维护两份记录。边数 4→3；度数 2、1、2、1、0，总和 6。</p>'+note('链表同时释放两个边结点。不存在的边不再次减数；非法顶点单独报告。矩阵保持对称，其他关系不变。E 仍孤立，全图仍不是树。'), '第四节 · 操作、代价与表示选择'],
['先预测，再运行 C 程序检查', '<p><a href="code/graph_demo.c">code/graph_demo.c</a> 使用无向主例与有向时间网。</p><ol><li>预测 C 的邻居、矩阵与邻接表各检查多少项。</li><li>预测删除 BC 后的边数、各顶点度数及总和。</li><li>检查时间网的 A→C、A→E：零权边与无边能否区分？</li></ol><details class="teacher-note"><summary>教学注记</summary><p>无向 C 的邻居 A、B、D，矩阵扫描5格、表扫描3项。删除 BC 后度数为2、1、2、1、0，总和6，边数3。时间网 A→C 存在且权0，A→E 不存在；入度和出度总和均5。</p></details>', '第四节 · 操作、代价与表示选择'],
['课程先修关系怎样建模？该选什么表示？', '<p>9 分钟：学校需要枚举“学完一门课可以直接衔接哪些课”。P 是 Q、R 的先修；Q、R 是 S 的先修。</p><p>独立 2 分钟：识别顶点，说明边方向与含义。</p><details><summary>独立判断后：共同约定与应用任务（5 分钟）</summary><p>约定先修→后续。画图写边集；构造出邻接表，按主要操作解释选择理由。</p></details><p>反馈 2 分钟：核对方向、遗漏及理由；提高追问：增加 S→P 后会怎样？</p>'+note('共同约定在独立判断后口头公布，不要求独立复现教师措辞。答案 V={P,Q,R,S}；弧 PQ、PR、QS、RS；出表 P:[Q,R], Q:[S], R:[S], S:空。列表按实际出邻居枚举，适合所给负载；小图本身不足以证明性能优越。提高：规模及频率变化须核对内存与度分布；SP 成环仍可用图表示，但所有课程必须先满足先修的安排不可执行。不要求全部表示或拓扑排序实现。'), '第四节 · 操作、代价与表示选择'],
['今天建立了怎样的计算能力链？', '<table><thead><tr><th>情境</th><th>关系建模</th><th>表示与条件</th></tr></thead><tbody><tr><td>双向道路</td><td>无向图，可有环、孤立点</td><td>矩阵对称；表中每边两份</td></tr><tr><td>单向时间网</td><td>有向带权图</td><td>存在性与权值分开，允许零权</td></tr><tr><td>课程先修</td><td>按先修→后续连弧</td><td>图可编码环；排课可行性另判断</td></tr></tbody></table><p>先确定对象、关系语义和操作需求，再选择矩阵或邻接表。</p>', '第四节 · 操作、代价与表示选择'],
['课后练习与教材导航', '<p><strong>教材导航</strong>：精读 6.1–6.3，对照阅读 6.4.1–6.4.2；邻接访问与遍历在 D012 回收。</p><p><strong>A. 书本习题</strong>：第 6 章选择题 <strong>(1)(2)(3)(5)</strong>。每题附理由，计数题写出假设和推导。</p><p><strong>B. 扩展作业</strong>：运行 <code>code/graph_demo.c</code>：预测主例 C 的邻居，再预测 homework 删除 AC 后的度数并核对；按第 27、30 页的规模和两种工作负载选择表示，写明代价及内存条件。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B，附 3–5 行过程记录。<br>自学（不提交）：为课程先修例画出邻接矩阵与邻接表，比较两种表示。</p>', '第四节 · 操作、代价与表示选择'],
['已经能找到邻居，怎样不重不漏地遍历？', '<p>从 A 出发，沿 A—B—C—A 走，可能反复回来。<br>即使这一部分都访问完，孤立的 E 仍没有被看到。</p><p class="lead">怎样既不重复，也不遗漏其他连通分量？</p><p>D012：图的遍历，回收栈、队列与访问标记。</p>', '第四节 · 操作、代价与表示选择'],
]
