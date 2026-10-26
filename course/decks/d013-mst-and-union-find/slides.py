"""D013: minimum spanning trees and dynamic equivalence classes."""
DECK_ID = "D013"
TITLE = "最小生成树与并查集"

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from graph_diagram import graph, beside
from mst_trace import (MAIN_NODES, MAIN_EDGES, MAIN_LABELS, MAIN_LABEL_POS, TRIANGLE_NODES,
                       TRIANGLE_EDGES, EXERCISE_NODES, EXERCISE_EDGES,
                       prim_player, kruskal_player)


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>' + text + '</p></details>'


def answer(html, title='核对答案与理由'):
    return '<details><summary>' + title + '</summary>' + html + '</details>'


def main_graph(*, marked=(), candidate=(), rejected=(), states=None, caption='主例带权无向图：边权为建设成本。'):
    return graph(MAIN_NODES, [(a, b) for a, b, w in MAIN_EDGES], labels=MAIN_LABELS, label_positions=MAIN_LABEL_POS, marked=marked,
                 candidate=candidate, rejected=rejected, states=states, caption=caption,
                 legend='')


def triangle_graph(*, marked=()):
    labels = {(a, b): w for a, b, w in TRIANGLE_EDGES}
    return graph(TRIANGLE_NODES, [(a, b) for a, b, w in TRIANGLE_EDGES], labels=labels, marked=marked,
                 caption='三角形：AB=10，AC=1，BC=1。')


def exercise_graph():
    labels = {(a, b): w for a, b, w in EXERCISE_EDGES}
    return graph(EXERCISE_NODES, [(a, b) for a, b, w in EXERCISE_EDGES], labels=labels,
                 caption='独立练习：P、Q、R、S；边权如下。')


def part(title, lead, detail, label):
    return [title, '<p class="lead">' + lead + '</p><p>' + detail + '</p>', label]


_LEGACY_SLIDES = [
['最小生成树与并查集', '<p class="lead">每次选一条便宜的边，怎样保证最后仍能得到最优连接？</p><p>数据结构与算法 · D013</p><p class="small">承接 D012；教材 6.6.1</p>', '课程名'],
['搜索树为什么可能多花钱？', '<pre>三角形：AB=10，AC=1，BC=1\n从 A 按编号做 DFS：选 AB、BC，总成本 11\n另一棵连接树：选 AC、BC，总成本 2</pre><p>先用 1 分钟解释：DFS 保证什么，没有保证什么？</p><details class="teacher-note"><summary>教学注记</summary><p>回收 D012：搜索树记录首次到达，保证覆盖可达点；没有按建设总成本选边。最少边数路径、搜索树、最小生成树是不同任务。</p></details>', '回收留问'],
['五个站点都接通，哪些信息必须保留？', '<pre>A ——1—— B\n \\4    /2 \\5\n    C ——3—— D\n     \\6   /7\n        E</pre><p>每条边表示可建设的双向线路，权为建设成本。<br>选择线路，使五个站点互通，并使总成本最小。</p><details class="teacher-note"><summary>教学注记</summary><p>完整边集 AB1、AC4、BC2、BD5、CD3、CE6、DE7。主例成本非负，不考虑容灾、容量、时延和既有必选边；这些要求改变后须重新建模。不要根据图中线条长短推断权值。</p></details>', '问题与对象'],
['为什么把候选解限定为生成树？', '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>连通无向图的生成树：包含全部顶点的连通无环子图。最小生成树在所有生成树中使边权之和最小。</div><p>本例非负建设成本下，环上删一条边仍连通，成本不会增加；可把最优连接约束到树。</p><details class="teacher-note"><summary>教学注记</summary><p>算法允许负权，但“从任意网络删环不增成本”的建模论证只对非负权成立；有负权时本讲仍以生成树为候选解，不声称等价于不限制边数的最低成本连通子图。定义按仓库教材记录概述，不作逐字引文。</p></details>', '模型与条件'],
['选了 n−1 条边，就一定完成了吗？', '<p>五个顶点：在 A、B、C 上选三角环，再选 DE。<br>边数为 4，却仍有两个分量。</p><ul><li>中间状态：已选边应组成森林。</li><li>完成条件：全部顶点连通，且无环。</li><li>对 n 个顶点的森林：边数 = n − 分量数。</li></ul><details class="teacher-note"><summary>教学注记</summary><p>区分结构可行与权值最优。保持无环再选到 n−1 条，才能推出连通。维护等价类正是后续并查集的任务。</p></details>', '结构不变量'],
['跨过一条分界，哪条边可以安全选？', '<pre>S={A,B}       其余={C,D,E}\n跨界边：AC=4，BC=2，BD=5\n最轻跨界边：BC=2</pre><p>若已选边可扩展成最优树，且没有跨越这条分界，加入最轻跨界边后，仍可扩展成最优树。</p><details class="teacher-note"><summary>教学注记</summary><p>割是顶点的非空真子集 S 与补集的划分。前提：已选边 F 可扩展成某棵 MST，且割尊重 F（无 F 边跨割）。安全不等于每棵 MST 都必须含该边；等权时可能有多解。</p></details>', '安全选择'],
['为什么这次局部选择不损失最优解？', '<ol><li>取一棵包含已选边的最优树 T；若已有最轻跨界边 e，无需改变。</li><li>否则加入 e 形成环；环上还有一条跨界边 f，且 f 不在已选边中。</li><li>用 e 换掉 f：仍是生成树，成本不增加，已选边全部保留。</li></ol><details class="teacher-note"><summary>教学注记</summary><p>因为 e 跨割最轻，w(e)≤w(f)。替换后不可能比最优 T 更便宜，故仍最优。这是交换论证；不是“每次最小所以整体最小”。先在前页割上用手指追出跨界路径，再读三步理由。</p></details>', '正确性'],
['Prim：让一片已连接区域逐步长大', '<pre>S 从一个顶点开始\n重复：\n    选 S 与外部之间最轻的边 (u,v)\n    加入该边，并把 v 纳入 S\n直到全部顶点已纳入</pre><p>每次加一个新顶点，树结构保持；跨界最轻支持安全选择。</p><details class="teacher-note"><summary>教学注记</summary><p>本页先讨论连通图。它不是“选离起点最近的顶点”；比较的是连接 S 的一条边。Prim 内部的选择规则无需边权非负。</p></details>', 'Prim 机制'],
['从 A 开始，最便宜的入口如何更新？', '<table><thead><tr><th>已纳入 S</th><th>各外部顶点的最便宜入口</th><th>本轮加入</th></tr></thead><tbody><tr><td>{A}</td><td>B←A:1，C←A:4；D/E 未知</td><td>AB:1</td></tr><tr><td>{A,B}</td><td>C←B:2，D←B:5；E 未知</td><td>BC:2</td></tr><tr><td>{A,B,C}</td><td>D←C:3，E←C:6</td><td>CD:3</td></tr><tr><td>{A,B,C,D}</td><td>E←C:6（经 D 为 7）</td><td>CE:6</td></tr></tbody></table><p>选边总和 1+2+3+6=12。</p><details class="teacher-note"><summary>教学注记</summary><p>展示一次完整示例。让学生解释 C 的入口为何从 A 改成 B，E 为何不随最近加入的 D 改变。初始没有入口必须与权值 0 区分。</p></details>', '完整推演'],
['key[v] 保存的是边权，还是路径长度？', '<pre>key[v] = min { w(u,v) : u 已在 S，且边存在 }\n纳入 u 后，对外部邻居 v：\n    若 w(u,v) &lt; key[v]：\n        key[v] = w(u,v)\n        parent[v] = u</pre><p>没有入口时另记“未知”；不要用 0 表示无边。</p><details class="teacher-note"><summary>教学注记</summary><p>代码用 has_key 与 present。key 不累加源到 u 的距离；parent 在这里记录当前候选连接边，纳入顶点后才成为结果树边。D014 将对比距离松弛。</p></details>', '信息与实现'],
['换一个起点，先补完两步', '<pre>Prim 从 C 开始：\nA:4，B:2，D:3，E:6\n第 1 条选 ____；纳入后 A 的入口变成 ____\n第 2 条选 ____；最终总成本是否改变？</pre><p>先补全，再解释每一步对应哪一条分界。</p><details class="teacher-note"><summary>教学注记</summary><p>2 分钟作答，1 分钟核对：CB2；A←B:1；BA1；之后 CD3、CE6，总和12。权值互异，MST 唯一，起点只改变选边次序。一般等权图中边集可能不同，但最优总权相同。</p></details>', '支架练习'],
['没有跨界候选，就把剩余点忽略吗？', '<p>删除 CE、DE 后，E 成为孤立点。<br>Prim 覆盖 A–D 后，没有边能把 E 接进来。</p><p>此图不存在覆盖全部顶点的生成树。<br>可以重新起一棵树，返回最小生成森林，并报告非连通。</p><details class="teacher-note"><summary>教学注记</summary><p>本程序显式报告 MSF 与 components，不把部分结果称 MST。孤立点也是一棵树。课堂主要讲连通条件，扩展实现另计每个分量起点。</p></details>', '失败条件'],
['Kruskal：从便宜的边开始合并分组', '<pre>所有边按权值非递减排列\n每个顶点起初独立成组\n依次取边 (u,v)：\n    若 u、v 不同组：选边并合并两组\n    若同组：跳过，它会形成环</pre><p>从多棵小树逐渐合成大树，直到连通或边已用完。</p><details class="teacher-note"><summary>教学注记</summary><p>必须先说明非递减排序与同组判断，不能只说“选最小边”。连通图选足 n−1 条可提前停止；本演示扫完边表以统一返回森林。</p></details>', 'Kruskal 机制'],
['哪两条候选边会因成环被跳过？', '<table><thead><tr><th>边（排序后）</th><th>两端当前关系</th><th>动作</th></tr></thead><tbody><tr><td>AB:1</td><td>分属 {A}、{B}</td><td>选，合成 {A,B}</td></tr><tr><td>BC:2</td><td>{A,B} 与 {C}</td><td>选，合成 {A,B,C}</td></tr><tr><td>CD:3</td><td>{A,B,C} 与 {D}</td><td>选，合成 {A,B,C,D}</td></tr><tr><td>AC:4、BD:5</td><td>两端已在同一组</td><td>跳过</td></tr><tr><td>CE:6</td><td>{A,B,C,D} 与 {E}</td><td>选，总和 12</td></tr></tbody></table><details class="teacher-note"><summary>教学注记</summary><p>DE:7 此后也在同组；若已选 n−1 条可以停止。请学生说出 AC 被跳过的路径依据 A—B—C，而非只背“有环”。</p></details>', '完整推演'],
['并查集保存的是哪些等价关系？', '<div class="quote compact-quote"><strong>模型约定（课程补充）</strong><br>本讲的并查集模型：把对象划分为互不相交的集合，支持查找所属集合的代表和合并两个集合。</div><p>u ~ v ⇔ 在当前已选边中，u 与 v 连通。<br>find(u)==find(v) 判断同组；union 合并两组。</p><details class="teacher-note"><summary>教学注记</summary><p>并查集的说明是本课补充模型，不声称教材 6.6.1 中有同名逐字定义。连通关系满足自反、对称、传递。原图连通不代表“当前已选边”已经连接全部顶点。</p></details>', '动态等价关系'],
['代表树的 parent 是原图中的边吗？', '<pre>并查集可表示为：A 是根，B→A，C→A，D→C\nfind(D)：D→C→A，代表为 A\n选中的图边却可能是：AB、BC、CD</pre><p>并查集父指针编码集合归属；不能拿它直接输出最小生成树。</p><details class="teacher-note"><summary>教学注记</summary><p>DSU forest 与 MST forest 是不同对象。根选择可因合并策略不同而改变，分组语义不变；结果图边需单独保存。当前例子用有效父指针状态解释，不要求与主例实现的每一步数组完全相同。</p></details>', '对象与表示'],
['怎样减少下一次查代表的工作？', '<pre>find(x):\n    若 parent[x] != x：\n        parent[x] = find(parent[x])\n    返回 parent[x]</pre><p>路径压缩：D→C→A 可改成 D→A，所属集合不变。<br>按大小合并：让较小集合的根接到较大集合根下。</p><details class="teacher-note"><summary>教学注记</summary><p>只合并根，不把任意结点挂接造成分组断裂。size 仅在根上有效。路径压缩改变辅助表示，不改变已选图边，也不会给原图凭空加 AD。摊还复杂度仅作注记，不推导反 Ackermann 函数。</p></details>', '表示维护'],
['不成环，为什么还不足以保证最优？', '<p>AB:10、AC:1、BC:1 中，先选 AB 再选 BC 也不成环，但成本不是最小。</p><ul><li>并查集保证：已选结构保持森林。</li><li>排序与割性质保证：接受的边仍可扩展到某个最优解。</li></ul><details class="teacher-note"><summary>教学注记</summary><p>对 Kruskal 当前分量取割。之前更轻的边要么已选并属于分量内部，要么因同组跳过后仍在某个分量内部；因此当前连接不同分量的边在该割上最轻。将可行性与最优性证据分开问。</p></details>', '全局性质'],
['同样便宜的边，可以得到不同答案吗？', '<pre>把主例 CE 改成 7，DE 仍为 7\n共同选边：AB:1、BC:2、CD:3\n最后可选 CE:7，也可选 DE:7</pre><p>两棵树总成本都为 13。<br>应检查结构与总权，不能只比较边集是否逐字相同。</p><details class="teacher-note"><summary>教学注记</summary><p>不同权值是唯一性的充分条件，存在等权不必然多解；本例确有两解。实现按权、端点编号确定平局，仅为输出可复现，不是正确性的必要条件。</p></details>', '等权与验证'],
['图的规模和已有表示如何影响选择？', '<table><thead><tr><th>实现</th><th>主要工作</th><th>时间</th></tr></thead><tbody><tr><td>矩阵 Prim</td><td>每轮找最小入口、更新一行</td><td>Θ(n²)</td></tr><tr><td>边表 Kruskal</td><td>排序 m 条边，再查代表与合并</td><td>O(n + m log(m+1))</td></tr></tbody></table><p class="small">稠密图已有矩阵时 Prim 自然；稀疏图已有边表时 Kruskal 自然。构造与排序成本也要计入。</p><details class="teacher-note"><summary>教学注记</summary><p>Kruskal 此界含按大小合并的最坏 O(log n) 查找，可对简单图相关边端点规模给出排序主导的整体界；通常连通图写 O(m log m)。并查集按大小+路径压缩的操作序列摊还近似常数 O(α(n))，不把单次 find 说成保证 O(1)。本演示归并排序 O(m log m)、辅助 O(m)，DSU O(n)；矩阵 Prim 除输入和结果外 O(n)。堆优化 Prim 留作后续联系，不在本讲展开。</p></details>', '代价与选择'],
['代码里哪些状态承担哪些责任？', '<pre>bool present[CAP][CAP];  /* 是否有边 */\nint weight[CAP][CAP];    /* 边权，可为 0 */\nint parent[CAP];         /* DSU 根或父结点 */\nsize_t size[CAP];        /* DSU 根的集合大小 */\nEdge selected[CAP-1];    /* 另存真正选中的图边 */</pre><p>阅读顺序：find / unite → kruskal → prim。<br>先看状态含义，再看更新语句。</p><details class="teacher-note"><summary>教学注记</summary><p>概念字段对照，完整结构名称见 code/mst_demo.c。Prim 也有独立 parent 数组，语义是入口边，不能与 DSU parent 混用。构图校验、排序实现和测试不逐行讲。</p></details>', 'C 表示'],
['先预测，再比较两种构造', '<p>记录主例选边、总成本，以及 E 孤立后的结果类型。<br>再预测零权边 DE 会改变哪些选择。</p><pre>gcc -std=c11 -Wall -Wextra code/mst_demo.c -o /tmp/d013\n/tmp/d013</pre><p class="small">对照 Prim 与 Kruskal；相同总权是一项检查，还不是最优性的独立证明。</p><details class="teacher-note"><summary>教学注记</summary><p>输出 base、ties、homework DE=0、isolated E、negative and zero。保留运行前预测。最后一组用于核对 MST 算法接受负权，不将物理建设成本强行解释为负数。</p></details>', '预测与运行'],
['检查一棵结果树，哪些证据缺一不可？', '<table><thead><tr><th>问题</th><th>检查方式</th></tr></thead><tbody><tr><td>边真在输入图中吗？</td><td>核对存在性与权值</td></tr><tr><td>覆盖且无环吗？</td><td>连通分组、重复合并、n−1 条</td></tr><tr><td>总权计算正确吗？</td><td>重新求和</td></tr><tr><td>已经最优了吗？</td><td>安全选择理由；小图可枚举全部候选树</td></tr></tbody></table><p>非连通输入应报告森林；等权输入允许不同最优树。</p><details class="teacher-note"><summary>教学注记</summary><p>程序 verify 只检查结构、覆盖原图分量与成本一致性，不冒称最优性证明。独立枚举测试另行验证小图最优值。</p></details>', '验证边界'],
['新网络：你能说明每一次合并吗？', '<pre>四站点 P、Q、R、S\nPQ=4，PR=1，QR=2，QS=1，RS=5</pre><ol><li>独立构造最小生成树并计算总成本。</li><li>写出每次选边后的分组；解释跳过一条边的理由。</li><li>任选一次选择，指出支持它的分界与最轻跨界边。</li></ol><details class="teacher-note"><summary>教学注记</summary><p>7 分钟独立作答、2 分钟反馈。PR1、QS1、QR2，总成本4；分组 {P,R}/{Q,S} 再合并。PQ、RS 成环，至少解释其中一条；QR 是两组之间最轻边（其他跨界 PQ4、RS5）。不要求平局顺序一致。只报总成本不能认定理解维护的性质。</p></details>', '独立学习证据'],
['全网最便宜，就能让每次出行都最快吗？', '<pre>三角形：AB=2，BC=2，AC=3\nMST 选 AB、BC，总和4\n树上 A→C 成本4，原图直达 AC 成本3</pre><p>最小生成树优化所有已选边的总权。<br>最短路径优化一个源到目标的路径权。</p><details class="teacher-note"><summary>教学注记</summary><p>此处权值抽象为代价，若物理任务分别是建设成本与行驶时间，需另行定义权值信息，不能混用。D014 会重新确定源点、距离状态与算法条件。</p></details>', '任务边界'],
['把选择、约束和维护机制放在一起', '<table><thead><tr><th>算法/结构</th><th>维护什么</th><th>为何有用</th></tr></thead><tbody><tr><td>Prim</td><td>已连接区域与最便宜入口</td><td>最轻跨界边逐步扩展</td></tr><tr><td>Kruskal</td><td>按权排序、当前连通分组</td><td>以安全边合并森林</td></tr><tr><td>并查集</td><td>同属一个集合的关系</td><td>快速判断合并还是成环</td></tr></tbody></table><p>能连接、不会成环、成本最优，是三个需要分别解释的判断。</p>', '结构化收口'],
['课后：教材导航与正式作业', '<p><strong>教材导航</strong>：精读 6.6.1；对照阅读本讲并查集代码。</p><p><strong>A. 书本习题</strong>：第 6 章选择题 <strong>(7)</strong>、应用题 <strong>(2)③</strong>。写选择理由、选边过程和总权。</p><p><strong>B. 程序实践</strong>：把主例 DE 权值由 7 改为 0，先预测两算法的选边和总权，运行 homework 输出核对；写出 Kruskal 每次合并后的分组。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B 与 3–5 行过程记录。<br>应用题 (2)①②可画作解题草稿，本次正式提交范围为③。</p><details class="teacher-note"><summary>教学注记</summary><p>A 直接采用仓库 D013 清单，原教材图以教材为准；不声称 D012 已正式布置应用题 (2)①②。B 的 DE0、AB1、BC2、CD3，总和6；Prim 从 A 顺序 AB、BC、CD、DE，Kruskal 顺序 DE、AB、BC、CD。两者顺序可不同，结果合法且最优即可。</p></details>', '课后衔接'],
['下一讲：从一个起点出发，距离如何更新？', '<p>Prim 的 key[v] 是接入当前区域的一条边。<br>若任务变成“从 A 到 v 的最少总代价”，状态应保存什么？</p><p class="lead">D014：最短路径。</p><details class="teacher-note"><summary>教学注记</summary><p>不要预先把 Prim 的更新式当作 Dijkstra；后者涉及源路径累计值和权值条件。让学生先说出“到 u 的已有距离加上 u→v 边权”，为下一讲保留问题。</p></details>', '留下问题'],
]


_OUTLINE = ['本讲要解决哪四个问题？', r'''<table><thead><tr><th>部分</th><th>要解决的问题</th><th>页码</th><th>分钟</th></tr></thead><tbody>
<tr><td>第一部分</td><td>网络建设目标、生成树、割与安全选择</td><td>3–9</td><td>19</td></tr>
<tr><td>第二部分</td><td>Prim 的已连接区域与最便宜入口</td><td>10–15</td><td>17</td></tr>
<tr><td>第三部分</td><td>Kruskal、动态分组与并查集</td><td>16–22</td><td>22</td></tr>
<tr><td>第四部分</td><td>等权、代价、实现、验证与独立任务</td><td>23–33</td><td>27</td></tr>
</tbody></table><p><strong>约 45 分钟断点</strong>：第 18 页 Kruskal 推演后。</p>''', '课程路线']

_PART1 = part('第一部分：问题与数学依据', '从一棵搜索树开始，重新定义“连接全网”的优化目标。', '生成树、n−1 条边的边界、割与交换论证。', '第一部分 · 问题与数学依据')
_PART2 = part('第二部分：Prim', '让一片已连接区域逐步长大。', '状态语义、最轻跨界边、key 与候选 parent、非连通重启。', '第二部分 · Prim')
_PART3 = part('第三部分：Kruskal 与并查集', '从便宜边开始合并，维护动态分组。', '排序、接受/拒绝、DSU 父指针与路径压缩。', '第三部分 · Kruskal 与 DSU')
_PART4 = part('第四部分：验证与应用', '把结构可行性、选择安全性与任务边界分开检查。', '等权与实现代价、C 状态、独立练习、MST 与最短路径。', '第四部分 · 验证与应用')

_SEARCH = ['搜索树为什么可能多花钱？',
 beside(triangle_graph(marked=(('A', 'B'), ('B', 'C'))),
        r'''<p>按编号从 A 做 DFS：选 AB、BC（红粗），总成本 <strong>11</strong>。</p><p>另一棵连接树 AC、BC 的总成本为 <strong>2</strong>。</p><p>搜索树保证覆盖可达点，没有按建设总成本选边。</p>''') +
 note('回收 D012：搜索树记录首次到达，保证覆盖可达点；没有按建设总成本选边。最少边数路径、搜索树、最小生成树是不同任务。'),
 '第一部分 · 问题与数学依据']

_MAIN = ['五个站点都接通，哪些信息必须保留？',
 beside(main_graph(), r'''<p>顶点 A–E；每条边表示可建设的双向线路，边权为建设成本。</p><p><strong>目标</strong>：选择线路，使五个站点互通，并使总成本最小。</p><p class="small">先保留全部候选边；选多少条、选哪几条，是本讲要回答的问题。</p>''') +
 note('完整边集 AB1、AC4、BC2、BD5、CD3、CE6、DE7。主例成本非负，不考虑容灾、容量、时延和既有必选边；这些要求改变后须重新建模。不要根据图中线条长短推断权值。'),
 '第一部分 · 问题与数学依据']

_N1 = ['选了 n−1 条边，就一定完成了吗？',
 beside(main_graph(marked=(('A', 'B'), ('A', 'C'), ('B', 'C'), ('D', 'E')),
                    caption='选中 AB、AC、BC、DE：4 条边，但 A–C 与 D–E 两个分量。'),
        r'''<p>五个顶点选了 4 条边，却仍有两个分量。</p><ul><li>中间状态：已选边应组成森林。</li><li>完成条件：全部顶点连通，且无环。</li><li>对 n 个顶点的森林：边数 = n − 分量数。</li></ul>''') +
 note('区分结构可行与权值最优。保持无环再选到 n−1 条，才能推出连通。维护等价类正是后续并查集的任务。'),
 '第一部分 · 问题与数学依据']

_CUT = ['跨过一条分界，哪条边可以安全选？',
 beside(main_graph(candidate=(('B', 'C'),), states={'A': 'visited', 'B': 'visited'},
                    caption='S={A,B}（蓝）；跨界 AC4、BC2、BD5；最轻 BC=2（橙虚线）。'),
        r'''<p><strong>割</strong>：把顶点分成 S 与补集两部分，只考虑跨过这条分界的边。</p><p>S={A,B}，其余={C,D,E}；跨界边 AC=4、BC=2、BD=5，最轻是 <strong>BC=2</strong>。</p><p>若已选边 F 可扩展成某棵 MST，且没有 F 边跨割，加入最轻跨界边后仍可扩展成某棵 MST。</p>''') +
 note('割是顶点的非空真子集 S 与补集的划分。前提：已选边 F 可扩展成某棵 MST，且割尊重 F（无 F 边跨割）。安全不等于每棵 MST 都必须含该边；等权时可能有多解。'),
 '第一部分 · 问题与数学依据']

_EXCHANGE = ['为什么这次局部选择不损失最优解？',
 beside(main_graph(candidate=(('B', 'C'),), states={'A': 'visited', 'B': 'visited'},
                    caption='e=BC 是当前割上最轻跨界边；用交换论证保留已有选择。'),
        r'''<ol><li>取一棵包含已选边的最优树 T；若已有最轻跨界边 e，无需改变。</li><li>否则加入 e 形成环；环上还有一条跨界边 f，且 f 不在已选边 F 中。</li><li>用 e 换掉 f：仍是生成树，成本不增加，F 全部保留。</li></ol><p>因为 e 跨割最轻，w(e)≤w(f)；替换后不可能比最优 T 更便宜。</p>''') +
 note('这是交换论证；不是“每次最小所以整体最小”。先在前页割上用手指追出跨界路径，再读三步理由。'),
 '第一部分 · 问题与数学依据']

_PRIM_PLAYER = ['从 A 开始，Prim 的每一步怎样变化？',
 prim_player(), '第二部分 · Prim']

_KRUSKAL_PLAYER = ['Kruskal：当前边、分组与 DSU 父指针',
 kruskal_player(), '第三部分 · Kruskal 与 DSU']

_EXERCISE = ['新网络：你能说明每一次合并吗？',
 beside(exercise_graph(), r'''<p>四站点 P、Q、R、S；PQ=3、PR=1、QR=2、QS=4、RS=5。</p><div class="exercise-grid"><p>1. 按 Kruskal 构造 MST。</p><p>2. 写接受/拒绝边及原因。</p><p>3. 写接受后的分组。</p><p>4. 解释 PQ 为何被拒绝。</p><p>5. 任选接受，说明割安全。</p><p>6. 计算总权。</p></div>''' +
 answer(r'''<p class="small"><strong>顺序/过程</strong>：PR1、QR2、PQ3（此时 MST 未完成，PQ 同组拒绝）、QS4、RS5（拒绝）；总权 7。</p><p class="small"><strong>分组/割</strong>：{P,R}→{P,Q,R}→{P,Q,R,S}；选 QS 时 S={P,Q,R}，跨界 QS4、RS5，QS 最轻。</p>''', '核对答案与理由（7+2 分钟）')),
 '第四部分 · 验证与应用']

SLIDES = [
    _LEGACY_SLIDES[0],
    _OUTLINE,
    _PART1,
    _SEARCH,
    _MAIN,
    _LEGACY_SLIDES[3],
    _N1,
    _CUT,
    _EXCHANGE,
    _PART2,
    _LEGACY_SLIDES[7],
    _PRIM_PLAYER,
    _LEGACY_SLIDES[9],
    _LEGACY_SLIDES[10],
    _LEGACY_SLIDES[11],
    _PART3,
    _LEGACY_SLIDES[12],
    _KRUSKAL_PLAYER,
    _LEGACY_SLIDES[14],
    _LEGACY_SLIDES[15],
    _LEGACY_SLIDES[16],
    _LEGACY_SLIDES[17],
    _PART4,
    _LEGACY_SLIDES[18],
    _LEGACY_SLIDES[19],
    _LEGACY_SLIDES[20],
    _LEGACY_SLIDES[21],
    _LEGACY_SLIDES[22],
    _EXERCISE,
    _LEGACY_SLIDES[24],
    _LEGACY_SLIDES[25],
    _LEGACY_SLIDES[26],
    _LEGACY_SLIDES[27],
]


for _i in range(3, 9):
    SLIDES[_i][2] = '第一部分 · 问题与数学依据'
for _i in range(10, 15):
    SLIDES[_i][2] = '第二部分 · Prim'
for _i in range(16, 22):
    SLIDES[_i][2] = '第三部分 · Kruskal 与 DSU'
for _i in range(23, 33):
    SLIDES[_i][2] = '第四部分 · 验证与应用'
