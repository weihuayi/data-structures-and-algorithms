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


IDS = {name: i for i, name in enumerate(NODES)}


def roads(marked=(), edges=None, *, numbered=False, degrees=False, caption=None):
    edges = ROADS if edges is None else edges
    details = {v: str(IDS[v]) for v in NODES} if numbered else None
    if degrees:
        details = {v: f'度 {sum(v in edge for edge in edges)}' for v in NODES}
    return graph(NODES, edges, caption=caption or ('道路主图。' if marked else '无向道路主例；E 孤立。'),
                 marked=marked, node_details=details)


def times(*, numbered=False):
    return graph(NODES, list(TIMES), caption='单向时间网：弧权以分钟计；位置不表示距离。',
                 directed=True, labels=TIMES,
                 node_details={v: str(IDS[v]) for v in NODES} if numbered else None)


def numbering():
    return '<div class="graph-index">' + table(['站点', *NODES], [['编号', *map(str, IDS.values())]]) + '</div>'


def matrix():
    return '<div class="graph-index">' + table(['行 / 列', *[f'{i}({v})' for v, i in IDS.items()]],
                 [[f'{IDS[u]}({u})'] + [
                     '<span class="graph-mark">1</span>' if {u,v} == {'B','C'}
                     else str(int((u,v) in ROADS or (v,u) in ROADS)) for v in NODES]
                  for u in NODES]) + '</div>'


def lists():
    return code('head[0](A): 1(B) → 2(C) → NULL\nhead[1](B): 0(A) → 2(C)* → NULL\nhead[2](C): 0(A) → 1(B)* → 3(D) → NULL\nhead[3](D): 2(C) → NULL\nhead[4](E): NULL')


def answer(text, title='核对答案与理由'):
    return '<details><summary>'+title+'</summary>'+text+'</details>'


SLIDES = [
['图：一般关系结构', '<p class="lead">有环、没有唯一的父结点，怎样组织计算？</p><p>数据结构与算法 · D011</p><p class="small">教材接口：6.1–6.3；6.4.1–6.4.2 的表示对照先行引入</p>', '第一节 · 从现实关系到图模型'],
['今天我们要解决哪四个问题？', '<table><thead><tr><th>节次</th><th>问题</th></tr></thead><tbody><tr><td>第一节</td><td>哪些现实关系需要图？</td></tr><tr><td>第二节</td><td>直接相邻与沿路可达有何不同？</td></tr><tr><td>第三节</td><td>同一张图怎样存入计算机？</td></tr><tr><td>第四节</td><td>操作与资源怎样决定表示选择？</td></tr></tbody></table>', '第一节 · 从现实关系到图模型'],
['第一节：为什么需要图？', '<p class="lead">从道路网络出发，理解对象与关系。</p><p>先观察连接，再建立数学模型。</p>', '第一节 · 从现实关系到图模型'],
['为什么不能把所有关系都组织成树？', beside(roads(), '<p>A—B—C—A 有环；站点 E 没有道路接入。</p><p>在 {A,B,C,D} 内可舍去环上的一条边，保留一棵树。</p><p>仅删边无法接入 E，全图仍不连通。<br>因此不存在覆盖五个顶点的生成树。</p>'), '第一节 · 从现实关系到图模型'],
['哪些站点之间存在直接连接？', beside(roads(), '<p>道路清单：AB、AC、BC、CD，均可双向通行。</p><p>站点 E 尚无道路接入，但必须保留。</p><p>请逐条核对端点：A 与 D 直接相连吗？</p>'), '第一节 · 从现实关系到图模型'],
['如何从道路网络建立数学对象？', '<table><thead><tr><th>情境信息</th><th>计算对象</th><th>本讲约定</th></tr></thead><tbody><tr><td>站点 A–E</td><td>顶点（Vertex）集合 V(G)</td><td>标识互异，位置编号固定</td></tr><tr><td>两站之间直接相通</td><td>边（Edge）集合 E(G)</td><td>无自环，无重复边</td></tr><tr><td>行驶方向 / 时间</td><td>方向 / 边权</td><td>按任务需要明确加入</td></tr></tbody></table><p>V(G)={A,B,C,D,E}；E(G)={AB,AC,BC,CD}。</p><details class="teacher-note"><summary>教学注记</summary><p>站点名 E 与边集 E(G) 需区分，讲授时读作“站点 E”与“边集合”。公式中 G=(V,E) 沿教材标准记法，程序用 edges 避免混淆。现实道路可有平行路线，本讲简单图模型只保留每对地点最多一条关系。</p></details>', '第一节 · 从现实关系到图模型'],
['什么是图？', '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>图（Graph）\\(G=(V,E)\\) 由顶点的非空有限集合 V 和边的有限集合 E 构成。无向图的边表示无序顶点对；有向图的弧表示有序顶点对。</div><p>无向边 {A,B}={B,A}，只计一条边。<br>有向弧 ⟨A,B⟩ 与 ⟨B,A⟩ 是两个可能不同的关系。</p><p class="small">本讲采用简单图：无自环、无重边；允许边集为空。</p>', '第一节 · 从现实关系到图模型'],
['方向与权值改变了什么？', beside(times(), '<p>有向图（Directed Graph）：箭头保存允许通行的方向，反向弧不自动存在。</p><p>权值保存通行时间；带权图也称网。</p><p>A→C 的 0 是即时转接，仍有边。</p><p class="small">这是独立约定的五条弧，不能由道路图直接推出。</p>'), '第一节 · 从现实关系到图模型'],
['第二节：图中的关系意味着什么？', '<p class="lead">连接给出一步能去哪里；路径回答多步能否到达。</p><p>用路径、度数和反例检查我们对关系的理解。</p>', '第二节 · 理解图中的关系'],
['不直接相邻，是否仍然可以到达？', beside(roads(marked=[('A','C'),('C','D')]), '<p>A、D 不邻接，却可沿 A—C—D 到达。</p>'+definition('无向图任意两顶点间都有路径时称连通；极大连通子图称连通分量（Connected Component）。')+'<p>{A,B,C,D}、{E} 各是一个连通分量。</p><p class="small">前者内部连通，无法再加入 E 保持连通；“极大”不是顶点最多。</p>'), '第二节 · 理解图中的关系'],
['路径、路径长度与环怎样定义？', beside(roads(marked=[('A','B'),('B','C'),('A','C')]), definition('路径是相邻顶点连接成的序列；路径长度为经过的边或弧数。首尾相同的路径称回路或环。')+'<p>A—C—D：长度 2。A—B—C—A：环。</p><p class="small">简单路径不重复顶点；简单环除首尾外不重复顶点。</p>'), '第二节 · 理解图中的关系'],
['方向改变后，可达性会怎样变化？', beside(times(), '<p>A 能到 B，B 却不能回到 A。</p><p>A→C→D：2 条弧，总权值 3。<br>A→B→C→D：3 条弧，总权值 9。</p><p>边数与总权值是不同量。</p>')+note(r'强连通要求任意不同顶点间均有双向有向路径。本例强连通分量（Strongly Connected Component）为 {A}、{B,C,D}、{E}，不展开算法。对当前可见时间网逐弧计数：出度 2、1、1、1、0；入度 0、2、2、1、0，各和为5。用 m 表示弧数，则 \(\sum_v d^+(v)=\sum_v d^-(v)=m\)，每弧贡献一次出度和一次入度。'), '第二节 · 理解图中的关系'],
['怎样通过度数检查图的关系？', beside(roads(marked=[('B','C')], degrees=True), r'<p>\(n=|V(G)|\)：顶点数。<br>\(m=|E(G)|\)：边数；有向图按弧数计。</p><p>\(d(v)\) 是与顶点 v 关联的边数。</p><p>BC 为 B、C 各贡献 1；每条无向边均有两个端点。</p><p>\(2+2+3+1+0=8=2m\)<br>故 \(\sum_v d(v)=2m\)。</p>')+note('当前简单无向图 n=5、m=4，E 的度为0。教材用 e 表示边数，本讲统一用 m；有向图的出度、入度及弧数在第12页时间网注记中对照。'), '第二节 · 理解图中的关系'],
['有 n−1 条边就一定是树吗？', beside(roads(marked=[('A','B'),('B','C'),('A','C')]), r'<p>主例 \(n=5,m=4=n-1\)。<br>它有环及孤立顶点 E，不是树。</p><p>树是连通且无环的无向图。<br>\(m=n-1\) 是必要条件，单独不是充分条件。</p>')+r'<p class="small">仅对无向森林：\(m=n-c\)，其中 c 是连通分量个数。该公式不能直接套用于左图的含环一般图。</p>', '第二节 · 理解图中的关系'],
['第三节：计算机怎样保存一张图？', '<p class="lead">同一个逻辑图，能否用不同存储方式完成相同操作？</p><p>先列操作，再建立图、矩阵、链表与 C 字段的对应。</p>', '第三节 · 将图转换为计算表示'],
['为了使用图，需要哪些基本操作？', '<p>图与基本操作构成抽象数据类型（Abstract Data Type，ADT）。</p><table><thead><tr><th>需求</th><th>操作接口</th><th>应回答什么</th></tr></thead><tbody><tr><td>能否直接从 u 到 v</td><td>has_edge(u,v)</td><td>存在 / 不存在 / 顶点非法</td></tr><tr><td>从 u 可以直接去哪</td><td>neighbors(u)</td><td>所有邻接顶点及边权</td></tr><tr><td>一条道路关闭</td><td>remove_edge(u,v)</td><td>删除关系，保持表示一致</td></tr></tbody></table><p>接口描述图的行为。矩阵、链表只是实现这些操作的不同办法。</p><details class="teacher-note"><summary>教学注记</summary><p>教材 6.3 图的类型定义还有顶点增删等操作。本讲选固定顶点集合的局部接口；邻接不等于可达。完整 DFS/BFS 与邻接访问迭代在 D012 回收。</p></details>', '第三节 · 将图转换为计算表示'],
['怎样用矩阵保存图中的边？', beside(roads(marked=[('B','C')], numbered=True), numbering()+matrix())+'<p class="small">邻接矩阵（Adjacency Matrix）：A–E 是名称，0–4 是数组下标，编号不改变关系。BC → 1—2 → M[1][2]=M[2][1]=1。</p>', '第三节 · 将图转换为计算表示'],
['矩阵的哪些性质来自图的关系？', beside(roads(marked=[('B','C')], numbered=True), matrix())+'<p class="small">无向边对应对称两格：M[1][2]=M[2][1]；无自环 ⇒ 对角线全 0；4 条边 ⇒ 8 个值为 1 的单元。有向矩阵不必对称。</p>', '第三节 · 将图转换为计算表示'],
['权值为 0，与不存在的边怎样区分？', beside(times(numbered=True), table(['顶点对 / 编号','present','weight'],[['A→C / 0→2','true','0'],['A→E / 0→4','false','不解释']])+code('present[0][2] = true;\nweight[0][2] = 0;'))+'<p class="small">教材以 ∞ 编码无边；本程序将存在性与权值分开。A→C 权0仍有边，A→E 无边；不能用 weight != 0 判断有边。</p>', '第三节 · 将图转换为计算表示'],
['怎样只保存实际存在的邻居？', beside(roads(marked=[('B','C')], numbered=True), lists())+'<p class="small">邻接表（Adjacency List）：head[1] 对应 B；整数为编号，字母为辅助名。<br>* 是 BC 的两份记录；→ 是 next 存储链接，不是图中的边。</p>', '第三节 · 将图转换为计算表示'],
['有向图的邻接表如何保存方向？', beside(times(numbered=True), code('出邻接：(to, weight)\nhead[0](A): (1,4) → (2,0) → NULL\nhead[1](B): (2,2) → NULL\nhead[2](C): (3,3) → NULL\nhead[3](D): (1,1) → NULL\nhead[4](E): NULL'))+'<p class="small">每条弧仅记在弧尾的出表；逆邻接表按弧头记入邻居，例如编号1(B)的入邻居是0(A)、3(D)。→ 是存储链接。</p>'+note('孤立点 E 仍有 head[4]=NULL。固定编号和编码约定后矩阵唯一；邻接表记录次序可变，不改变逻辑邻接关系。'), '第三节 · 将图转换为计算表示'],
['C 程序中的字段对应什么？', beside(code('typedef struct Arc {\n    int to, weight;\n    struct Arc *next;\n} Arc;\nArc *head[MAX_V];'), table(['字段','对应对象'],[['head[u]','编号 u 顶点的首个边记录'],['Arc.to','邻接顶点的整数编号'],['Arc.next','下一个边记录的地址'],['Arc.weight','本条逻辑边的权值']]))+'<p class="small">A=0、B=1、C=2、D=3、E=4；head[2] 的 to 依次为 0、1、3；head[4]=NULL。to 标识邻居，next 组织记录，职责不同。</p>'+note('边结点动态申请，构造失败清理已建记录，使用后释放。按编号升序只是本程序的记录次序约定。'), '第三节 · 将图转换为计算表示'],
['同一张图，你能构建两种表示吗？', '<p>4 分钟：无向图 V={X,Y,Z,W}，边 XY、YZ，W 孤立。独立编号 X=0、Y=1、Z=2、W=3。</p>'+code('矩阵第1行(Y)：[ __, __, __, __ ]\nhead[0](X): __   head[1](Y): __\nhead[2](Z): __   head[3](W): __')+'<p>填写并解释：一条 YZ 边对应哪些矩阵位置、哪些邻接项？</p>'+answer('<p>第1行：[1,0,1,0]；head[0]:[1]，head[1]:[0,2]，head[2]:[1]，head[3]:空。YZ 对应 M[1][2]、M[2][1]，以及表头1中的2和表头2中的1。</p>'), '第三节 · 将图转换为计算表示'],
['第四节：为什么需要选择表示？', '<p class="lead">逻辑关系相同，访问哪些存储位置却不同。</p><p>逐项观察查边、列邻居、删边，再结合规模与工作负载作判断。</p>', '第四节 · 操作、代价与表示选择'],
['判断指定边是否存在，两种表示各做什么？', beside(roads(marked=[('B','C')], numbered=True), '<p>查 BC（1—2）：矩阵直达 M[1][2]。</p>'+code('head[1](B)：0(A) → 2(C) → NULL\n            ①      ② 找到 to=2')+'<p>查 BD（1—3）：读完这两项，仍未找到 to=3。</p>')+r'<p class="small">有效编号、表示已构造：矩阵 \(O(1)\)；链表最坏 \(O(1+d(u))\)，有向出表用出度 \(d^+(u)\)。名字查编号和构造成本另计。</p>', '第四节 · 操作、代价与表示选择'],
['枚举一个顶点的邻居，工作量为何不同？', beside(roads(marked=[('A','C'),('B','C'),('C','D')], numbered=True), code('矩阵第2行(C)：[1][1][0][1][0]\n列编号：       0  1  2  3  4\nhead[2]：0(A) → 1(B) → 3(D)\n访问条目： ①      ②      ③'))+r'<p class="small">枚举 C（编号2）：矩阵扫描第2行的5格，\(\Theta(n)\)；链表访问3项，\(\Theta(1+d(C))\)。空表仍有常数开销。</p>', '第四节 · 操作、代价与表示选择'],
['图的规模怎样影响空间与表示选择？', r'<p>无自环、无重边：无向图最多 \(n(n-1)/2\) 条边；有向图最多 \(n(n-1)\) 条弧。</p>'+table(['按规模分配','普通矩阵','普通邻接表'],[[r'空间',r'\(\Theta(n^2)\)',r'\(\Theta(n+m)\)；无向有 2m 项'],['n=10000，m=30000','一亿个位置','一万表头 + 三万弧项 / 六万无向项']])+'<p class="small">少量边、主要枚举时通常倾向表；大量指定对查询时还要权衡矩阵内存、查询频率与常数。不是仅按稀疏/稠密决定。</p>'+note('顶点对计数：无向每对计一次，有向每对有两个方向。若每矩阵位置4字节，一亿位置约400 MB，不含顶点及辅助信息；演示 MAX_V=8 固定容量不做此规模实测。矩阵转表扫描 n² 格，与建好表示上的查询是不同成本。非连通图上界 (n−1)(n−2)/2；8 顶点最多21边，9 顶点可有28边，服务选择(5)。'), '第四节 · 操作、代价与表示选择'],
['删除一条无向边，必须维护什么？', '<div class="graph-pair">'+roads(marked=[('B','C')], numbered=True, caption='删除前：m=4。')+roads(edges=[('A','B'),('A','C'),('C','D')], numbered=True, caption='删除 BC 后：m=3；其余边及 E 不变。')+'</div>'+'<pre class="graph-change">M[1][2]、M[2][1]：1 → 0；head[1]：[0,2] → [0]；head[2]：[0,1,3] → [0,3]</pre>'+'<p class="small">一条逻辑边删除 ⇒ 两份邻接记录更新；度数 2,2,3,1,0 → 2,1,2,1,0，度数和 8→6。</p>'+note('无向边的两个边结点均释放；重复删除不再次减数，非法编号另报。矩阵保持对称；E 仍孤立，全图仍不是树。'), '第四节 · 操作、代价与表示选择'],
['先预测，再运行 C 程序检查', beside(roads(numbered=True), '<ol><li>预测 C（编号2）的邻居及两种表示的扫描数。</li><li>预测删除 BC（1—2）后的边数和各顶点度数。</li><li>运行 <a href="code/graph_demo.c">C 演示程序</a>，核对并解释差异。</li></ol>')+'<p class="small">时间网数据：A→B:4、A→C:0、B→C:2、C→D:3、D→B:1。另预测 A→C 与 A→E 的查询结果。</p>'+note('先记录预测再运行。无向邻居 A、B、D（0、1、3），矩阵5格、表3项；删 BC 后 m=3，度数2、1、2、1、0。时间网 present[0][2]为真且weight[0][2]=0，present[0][4]为假；两种入出度和各5。'), '第四节 · 操作、代价与表示选择'],
['课程先修关系怎样建模？该选什么表示？', '<p>9 分钟：学校需要枚举“学完一门课可以直接衔接哪些课”。P 是 Q、R 的先修；Q、R 是 S 的先修。</p><p>独立 2 分钟：识别顶点，说明边方向与含义。</p><details><summary>独立判断后：共同约定与应用任务（5 分钟）</summary><p>约定先修→后续。画图写边集；构造出邻接表，按主要操作解释选择理由。</p></details><p>反馈 2 分钟：核对方向、遗漏及理由；提高追问：增加 S→P 后会怎样？</p>'+note('共同约定在独立判断后口头公布，不要求独立复现教师措辞。答案 V={P,Q,R,S}；弧 PQ、PR、QS、RS；出表 P:[Q,R], Q:[S], R:[S], S:空。列表按实际出邻居枚举，适合所给负载；小图本身不足以证明性能优越。提高：规模及频率变化须核对内存与度分布；SP 成环仍可用图表示，但所有课程必须先满足先修的安排不可执行。不要求全部表示或拓扑排序实现。'), '第四节 · 操作、代价与表示选择'],
['今天建立了怎样的计算能力链？', '<table><thead><tr><th>情境</th><th>关系建模</th><th>表示与条件</th></tr></thead><tbody><tr><td>双向道路</td><td>无向图，可有环、孤立点</td><td>矩阵对称；表中每边两份</td></tr><tr><td>单向时间网</td><td>有向带权图</td><td>存在性与权值分开，允许零权</td></tr><tr><td>课程先修</td><td>按先修→后续连弧</td><td>图可编码环；排课可行性另判断</td></tr></tbody></table><p>先确定对象、关系语义和操作需求，再选择矩阵或邻接表。</p>', '第四节 · 操作、代价与表示选择'],
['课后练习与教材导航', '<p><strong>教材导航</strong>：精读 6.1–6.3，对照阅读 6.4.1–6.4.2；邻接访问与遍历在 D012 回收。</p><p><strong>A. 书本习题</strong>：第 6 章选择题 <strong>(1)(2)(3)(5)</strong>。每题附理由，计数题写出假设和推导。</p><p><strong>B. 扩展作业</strong>：运行 <code>code/graph_demo.c</code>：预测主例 C 的邻居，再预测 homework 删除 AC 后的度数并核对；按第 27、30 页的规模和两种工作负载选择表示，写明代价及内存条件。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B，附 3–5 行过程记录。<br>自学（不提交）：为课程先修例画出邻接矩阵与邻接表，比较两种表示。</p>', '第四节 · 操作、代价与表示选择'],
['已经能找到邻居，怎样不重不漏地遍历？', '<p>从 A 出发，沿 A—B—C—A 走，可能反复回来。<br>即使这一部分都访问完，孤立的 E 仍没有被看到。</p><p class="lead">怎样既不重复，也不遗漏其他连通分量？</p><p>D012：图的遍历，回收栈、队列与访问标记。</p>', '第四节 · 操作、代价与表示选择'],
]
