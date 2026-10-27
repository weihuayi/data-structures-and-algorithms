"""D013: minimum spanning trees and dynamic equivalence classes."""
DECK_ID = "D013"
TITLE = "最小生成树与并查集"
MATH = True

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from graph_diagram import graph, beside
from mst_trace import (MAIN_NODES, MAIN_EDGES, MAIN_LABELS, MAIN_LABEL_POS,
                       TRIANGLE_NODES, TRIANGLE_EDGES, TRIANGLE_LABEL_POS, EXCHANGE_NODES, EXCHANGE_EDGES,
                       EXERCISE_NODES, EXERCISE_EDGES, prim_player, kruskal_player,
                       kruskal_states, dsu_diagram, path_compression_demo)


def answer(html, title='核对答案与理由'):
    return '<details><summary>' + title + '</summary>' + html + '</details>'


def main_graph(*, marked=(), candidate=(), rejected=(), states=None, edge_notes=None,
               edge_note_positions=None, caption='主例带权无向图：边权为建设成本。'):
    return graph(MAIN_NODES, [(a, b) for a, b, w in MAIN_EDGES], labels=MAIN_LABELS,
                 label_positions=MAIN_LABEL_POS, marked=marked, candidate=candidate,
                 rejected=rejected, states=states, edge_notes=edge_notes,
                 edge_note_positions=edge_note_positions, caption=caption,
                 legend='')


def triangle_graph(*, marked=()):
    labels = {(a, b): w for a, b, w in TRIANGLE_EDGES}
    return graph(TRIANGLE_NODES, [(a, b) for a, b, w in TRIANGLE_EDGES], labels=labels,
                 label_positions=TRIANGLE_LABEL_POS, marked=marked,
                 caption='三角形：AB=10，AC=1，BC=1。')


def exchange_graph(*, marked=(), candidate=(), edge_notes=None, edge_note_positions=None, caption):
    labels = {(a, b): w for a, b, w in EXCHANGE_EDGES}
    return graph(EXCHANGE_NODES, [(a, b) for a, b, w in EXCHANGE_EDGES], labels=labels,
                 marked=marked, candidate=candidate, edge_notes=edge_notes,
                 edge_note_positions=edge_note_positions, caption=caption, legend='')


def exercise_graph():
    labels = {(a, b): w for a, b, w in EXERCISE_EDGES}
    return graph(EXERCISE_NODES, [(a, b) for a, b, w in EXERCISE_EDGES], labels=labels,
                 caption='独立练习：P、Q、R、S；边权如下。')


def disconnected_graph():
    edges = [(a, b, w) for a, b, w in MAIN_EDGES if (a, b) not in {('C', 'E'), ('D', 'E')}]
    labels = {(a, b): w for a, b, w in edges}
    return graph(MAIN_NODES, [(a, b) for a, b, w in edges], labels=labels,
                 label_positions=MAIN_LABEL_POS, marked=(('A', 'B'), ('B', 'C'), ('C', 'D')),
                 caption='非连通变式：删除 CE 和 DE；红色 AB、BC、CD 是 A–D 的最小生成树，E 孤立。', legend='')


def part(title, lead, detail, label):
    return [title, '<p class="lead">' + lead + '</p><p>' + detail + '</p>', label]


def edge_text(edges):
    return '、'.join(f'{a}{b}:{w}' for a, b, w in edges) or '无'


def group_text(components):
    return '、'.join('{' + ','.join(group) + '}' for group in components) or '空'


def parent_text(parent):
    return '、'.join(f'{v}→{p}' for v, p in sorted(parent.items()))


def parent_row(head, parent):
    return ('<tr><th>' + head + '</th>' +
            ''.join('<td>' + parent[v] + '</td>' for v in sorted(parent)) + '</tr>')


_KRUSKAL = kruskal_states()
# Real snapshot: after AB, BC, CD were accepted and AC was checked and rejected.
_THREE = next(state for state in _KRUSKAL if state['decision'] == 'reject')
_DSU_DEMO = path_compression_demo()
_STAR_POS = {'A': (260, 45), 'B': (80, 140), 'C': (180, 140), 'D': (300, 140), 'E': (420, 140)}
_CHAIN_POS = {'A': (260, 45), 'B': (80, 145), 'C': (260, 145), 'D': (430, 220)}


_OVERVIEW = ['本讲要解决哪四个问题？', r'''<table><thead><tr><th>部分</th><th>要解决的问题</th><th>页码</th><th>分钟</th></tr></thead><tbody>
<tr><td>第一部分</td><td>怎样定义连接全网的最低成本问题？</td><td>3–9</td><td>19</td></tr>
<tr><td>第二部分</td><td>怎样从一个顶点出发，逐步扩张连接区域？</td><td>10–15</td><td>17</td></tr>
<tr><td>第三部分</td><td>怎样按照边的成本顺序，逐步合并不同分组？</td><td>16–22</td><td>22</td></tr>
<tr><td>第四部分</td><td>怎样检查结果、分析计算代价并解决新问题？</td><td>23–33</td><td>27</td></tr>
</tbody></table>''', '课程路线']

_PART1 = part('第一部分：问题与数学依据',
              '从一棵搜索树开始，重新定义“连接全网”的优化目标。',
              '生成树、n−1 条边的边界、割与交换论证。',
              '第一部分 · 问题与数学依据')

_SEARCH = ['搜索树为什么可能多花钱？',
 beside(triangle_graph(marked=(('A', 'B'), ('B', 'C'))),
        r'''<p>按编号从 A 做深度优先搜索（DFS）：选 AB、BC（红粗），总成本 <strong>11</strong>。</p><p>另一棵连接树 AC、BC 的总成本为 <strong>2</strong>。</p><p>搜索树保证覆盖可达点，没有按建设总成本选边。</p>'''),
 '第一部分 · 问题与数学依据']

_MAIN = ['五个站点都接通，哪些信息必须保留？',
 beside(main_graph(),
        r'''<p>顶点 A–E；每条边表示可建设的双向线路，边权为建设成本。</p><p><strong>目标</strong>：选择线路，使五个站点互通，并使总成本最小。</p><p class="small">先保留全部候选边；选多少条、选哪几条，是本讲要回答的问题。</p>'''),
 '第一部分 · 问题与数学依据']

_MST = ['怎样把“连接全网”写成一个最小化问题？',
 r'''<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>连通无向图的生成树：包含全部顶点的连通无环子图。最小生成树在所有生成树中使边权之和最小。</div>
<p><strong>最小生成树（Minimum Spanning Tree，MST）</strong>：给定连通无向带权图 \(G=(V,E,w)\)，在全部生成树 \(T\subseteq E\) 中，使总边权 \(w(T)=\sum_{e\in T}w(e)\) 最小。</p>
<table class="compact-table"><tbody>
<tr><th>成立前提</th><td>图连通、无向；每条边有可比较的权值。</td></tr>
<tr><th>候选解</th><td>包含全部顶点的生成树（\(n-1\) 条边、连通、无环）。</td></tr>
<tr><th>优化目标</th><td>最小化总边权；不是最小化某条路径的长度。</td></tr>
</tbody></table>
<p>当边权表示非负建设成本时，删除环上的一条边仍保持连通，且成本不增加，因此可将最低成本连接问题限制在生成树中。</p>''',
 '第一部分 · 问题与数学依据']

_N1 = ['选了 n−1 条边，就一定完成了吗？',
 beside(main_graph(marked=(('A', 'B'), ('A', 'C'), ('B', 'C'), ('D', 'E')),
                    caption='选中 AB、AC、BC、DE：4 条边，但分量是 {A,B,C} 与 {D,E}。'),
        r'''<p>五个顶点选了 4 条边，却仍有两个分量。</p><ul><li>中间状态：已选边应组成森林。</li><li>完成条件：全部顶点连通，且无环。</li><li>对 n 个顶点的森林：边数 = n − 分量数。</li></ul>'''),
 '第一部分 · 问题与数学依据']

_CUT = ['跨过一条分界，哪条边可以安全选？',
 '<div class="graph-pair tight">' +
 main_graph(marked=(('A', 'B'),), candidate=(('B', 'C'),),
            states={'A': 'visited', 'B': 'visited'},
            edge_notes={('A', 'B'): 'F', ('B', 'C'): 'e'},
            edge_note_positions={('A', 'B'): (175, 80), ('B', 'C'): (231, 156)},
            caption='F={AB}（红粗）；S={A,B}（蓝）；跨界 AC4、BC2、BD5；最轻 e=BC2。') +
 main_graph(marked=(('A', 'B'), ('B', 'C')), candidate=(('C', 'D'),),
            states={'A': 'visited', 'B': 'visited', 'C': 'visited'},
            edge_notes={('A', 'B'): 'F′', ('B', 'C'): 'F′', ('C', 'D'): 'e′'},
            edge_note_positions={('A', 'B'): (175, 80), ('B', 'C'): (231, 156), ('C', 'D'): (257, 206)},
            caption='加入 BC 后：F′={AB,BC}，S′={A,B,C}；跨界 BD5、CD3、CE6；最轻 e′=CD3。') +
 '</div>' +
 r'''<p><strong>割</strong>：把顶点分成 S 与 V∖S，只考虑跨过这条分界的边（虚线只表示处理状态，边都在输入图中）。<strong>割尊重 F</strong>：没有 F 中的边跨过它。</p>
<p>左图 F={AB}，S={A,B}：AB 在 S 内部，故割尊重 F；全部跨界边为 AC=4、BC=2、BD=5，最轻 e=BC=2。</p>
<p class="compact-text">若 F 可扩展成某棵 MST 且割尊重 F，加入 e 后 F∪{e} 仍可扩展。右图加入 BC 后，新割仍尊重 F′，最轻边界变为 CD=3。</p>''',
 '第一部分 · 问题与数学依据']

_EXCHANGE = ['为什么这次局部选择不损失最优解？',
 '<p class="small"><strong>独立辅助例（不是 A–E 主图）</strong>：三角形 AB=1、AC=2、BC=2；已选 F={AB}，割为 {A,B}｜{C}；令 e=AC、f=BC。</p><div class="graph-stages">' +
 exchange_graph(marked=(('A', 'B'), ('B', 'C')),
                edge_notes={('A', 'B'): 'F'},
                edge_note_positions={('A', 'B'): (205, 38)},
                caption='① 原树 T={AB,BC}，总权 3；保留 F={AB}。') +
 exchange_graph(marked=(('A', 'B'), ('B', 'C')), candidate=(('A', 'C'),),
                edge_notes={('A', 'B'): 'F', ('A', 'C'): 'e', ('B', 'C'): 'f'},
                edge_note_positions={('A', 'B'): (205, 38), ('A', 'C'): (163, 127), ('B', 'C'): (278, 125)},
                caption='② 加入 e=AC 形成环；f=BC 跨割且不属于 F。') +
 exchange_graph(marked=(('A', 'B'), ('A', 'C')),
                edge_notes={('A', 'B'): 'F'},
                edge_note_positions={('A', 'B'): (205, 38)},
                caption='③ 移去 f=BC，得到 T′={AB,AC}，总权仍为 3。') +
 '</div>' +
 r'''<ol class="compact-list"><li><strong>① 原树：</strong>\(T=\{AB,BC\}\) 是最小生成树，包含必须保留的 \(F=\{AB\}\)。</li><li><strong>② 加边：</strong>跨割最轻边 \(e=AC\) 不在 T 中，加入它形成三角环；环上的 \(f=BC\) 跨割且不属于 F。</li><li><strong>③ 换边：</strong>用 e 代替 f，得到 \(T'=\{AB,AC\}\)，仍是包含 F 的生成树。</li></ol>
<p class="compact-text">这里 \(w(e)=w(f)=2\)，两棵树的总权同为 3。一般情形下 \(w(e)\leq w(f)\)，交换不会增加总权，因此保留最优性。</p>''',
 '第一部分 · 问题与数学依据']

_PART2 = part('第二部分：怎样让已连接区域逐步扩大？',
              '从一个顶点出发，每次只接受连接当前区域与外部的一条边。',
              '先说明构造规则与辅助状态，再观察每一步怎样更新。',
              '第二部分 · 逐步扩大已连接区域')

_PRIM = ['普里姆算法（Prim\'s Algorithm）：每次接受最轻的跨界边',
 r'''<div class="quote compact-quote"><strong>算法规则（数学描述）</strong><br>从任一顶点 s 开始，令 S={s}、F=∅；当 S≠V 时，取跨越 S 与 V∖S 的最轻边 e=(u,v)，令 F←F∪{e}、S←S∪{v}。</div>
<ol class="compact-list"><li>从一个顶点开始，S 最初只含该顶点。</li><li>维护当前已纳入顶点集合 S 与已接受边集 F。</li><li>在跨越 S 边界的边中，选择权值最小的一条。</li><li>接受该边和外部顶点；重复直到 S=V。</li></ol>
<p>Prim 构造的 F 是一棵生成树。它的正确性依赖<strong>安全边性质</strong>：当前割尊重 F，最轻跨界边可以加入某个 MST。</p>
<p class="small">前提：本页讨论连通图。选择的是“连接 S 的一条边”，不是“离起点最近的顶点”。</p>''',
 '第二部分 · 逐步扩大已连接区域']

_AUX = ['计算机执行 Prim，需要保存哪些辅助信息？',
 r'''<p class="small">计算任务：反复找出“S 与外部之间最轻的边”。要执行它，程序必须分清三类不同对象。</p>
<div class="state-layers">
<div><h3>一、输入图</h3><p>G=(V,E,w)，以及它的表示：邻接矩阵或邻接表。</p><p>回答“哪些顶点之间有边、权是多少”；不保存算法执行到哪一步。</p></div>
<div><h3>二、抽象状态</h3><p>S⊆V：已纳入顶点；F⊆E：已接受边。</p><p>对 v∉S：key[v]=min{w(u,v):u∈S 且 uv∈E}；parent[v] 记录取到最小值的 u；has_key[v] 表示候选是否存在。</p></div>
<div><h3>三、程序表示</h3><p><code>used[v]</code> ↔ v∈S；<code>key[v]</code>、<code>parent[v]</code>、<code>has_key[v]</code> 三个数组；<code>selected[]</code> 保存 F 的边。</p></div>
</div>
<p class="small"><strong>主例 S={A,B} 时</strong>：used[A]=used[B]=1；key[C]=2、parent[C]=B；key[D]=5、parent[D]=B；has_key[E]=0；F={AB:1}。</p>
<p><strong>key[v] 是“接进 S 的一条边权”，不是从起点到 v 的路径长度。</strong>parent[v] 在候选阶段只是入口来源；v 被接受后，对应的边才进入 F。</p>''',
 '第二部分 · 逐步扩大已连接区域']

_PRIM_PLAYER = ['从 A 开始，观察 S、候选入口与已选边 F 怎样变化',
 prim_player(),
 '第二部分 · 逐步扩大已连接区域']

_FROM_C = ['换一个起点，先补完两步',
 beside(main_graph(states={'C': 'current'}, caption='从 C 开始的 Prim 练习：C 为起点，边权与主例相同。'),
        r'''<p>从 C 出发，观察原图并独立预测：</p><ol class="compact-list"><li>第一条接受哪条边？纳入新顶点后，A 的候选入口如何更新？</li><li>第二条接受哪条边？最终总权改变吗？</li></ol><p class="small">先作答，再展开核对答案。</p>''') +
 answer(r'''<p><strong>第一步：</strong>选择 CB:2，纳入 B 后 A 的入口从 CA:4 更新为 BA:1。</p><p><strong>第二步：</strong>选择 BA:1；继续选择 CD:3、CE:6，总权为 12。</p><p class="small">改变起点可以改变选择顺序，但不改变主例唯一的 MST。</p>'''),
 '第二部分 · 逐步扩大已连接区域']

_MSF = ['没有跨界候选，就把剩余点忽略吗？',
 beside(disconnected_graph(), r'''<p>删除 CE、DE 后，E 与 A–D 不连通。图中红边 AB、BC、CD 连接 A–D，E 单独构成一个分量。</p><p>此图不存在覆盖所有顶点的生成树。对每个连通分量分别求最小生成树，得到<strong>最小生成森林（Minimum Spanning Forest，MSF）</strong>。</p><p class="small">结果：2 个连通分量、3 条选边、总权 6；孤立顶点也是一棵树。</p>'''),
 '第二部分 · 逐步扩大已连接区域']

_PART3 = part('第三部分：怎样依次合并不同连通分组？',
              '从最便宜的边开始，每次判断两个端点是否已经连在一起。',
              '排序、接受/拒绝、动态分组，以及分组的内部表示与维护。',
              '第三部分 · 合并连通分组')

_KRUSKAL = ['克鲁斯卡尔算法（Kruskal\'s Algorithm）：按边的成本顺序合并分组',
 r'''<div class="quote compact-quote"><strong>算法规则（数学描述）</strong><br>把 E 按权值非递减排列；每个顶点起初自成一个分组。依次取边 (u,v)：若 u、v 在不同分组，接受该边并合并两组；若在同一分组，拒绝。接受 n−1 条边或边用完时停止。</div>
<ol class="compact-list"><li><strong>排序</strong>：先处理便宜边；平局按端点编号只为输出可复现。</li><li><strong>判断同组</strong>：两端同组时，接受会形成环，拒绝。</li><li><strong>接受并合并</strong>：当前边连接两个不同分组，是该割最轻候选。</li><li><strong>终止</strong>：接受 n−1 条边即连通；否则返回森林。</li></ol>
<p>正确性仍靠安全边性质：更轻的跨界边会更早处理并合并两组；故当前边对该割最轻，可加入某个 MST。</p>''',
 '第三部分 · 合并连通分组']

_KRUSKAL_PLAYER = ['从最便宜的边开始，观察分组怎样合并',
 kruskal_player(),
 '第三部分 · 合并连通分组']

_DSU = ['怎样高效维护不断合并的分组？',
 r'''<div class="quote compact-quote"><strong>课程补充模型（不是教材逐字定义）</strong><br><strong>并查集（Disjoint Set Union，DSU；又称 Union-Find）</strong>维护一族互不相交的动态集合：find(x) 返回 x 所属集合的代表，union(a,b) 合并两个不同集合。</div>
<p>它服务于 Kruskal 的两件事：判断候选边两端是否同组；接受边后把两组并成一组。</p>
<p>这里的分组由“当前已经接受的边”诱导，不是原输入图的全部连通关系。</p>
<p><strong>边界</strong>：DSU 只负责维护分组和判环，不能单独保证 MST 的全局最优；最优性还依赖按权扫描与割性质。</p>''',
 '第三部分 · 合并连通分组']

_THREE_OBJECTS = ['选中的森林、当前分组与父指针：三者是什么关系？',
 '<div class="graph-pair tight">' +
 main_graph(marked=tuple(e[:2] for e in _THREE['selected_edges']),
            rejected=tuple(e[:2] for e in _THREE['rejected_edges']),
            caption='真实快照：F={AB,BC,CD}（红粗）；AC 已拒绝（灰细虚线）；E 未接入。') +
 dsu_diagram(_THREE['dsu_parent'], _STAR_POS,
             caption='同一快照的父指针树：箭头 v→p[v]；根 p[A]=A。',
             root=next(v for v, p in _THREE['dsu_parent'].items() if v == p)) +
 '</div>' +
 '<table class="compact-table three-objects"><thead><tr><th>对象</th><th>当前值（真实快照）</th><th>回答什么</th></tr></thead><tbody>' +
 '<tr><td>已选森林 F</td><td>' + edge_text(_THREE['selected_edges']) + '</td><td>哪些图边已被正式接受？</td></tr>' +
 '<tr><td>分组划分</td><td>' + group_text(_THREE['components']) + '</td><td>哪些顶点已被已选边连在一起？</td></tr>' +
 '<tr><td>DSU 父指针 p（v→p[v]）</td><td>' + parent_text(_THREE['dsu_parent']) + '</td><td>程序怎样编码“属于哪一组”？</td></tr>' +
 '</tbody></table>' +
 r'''<p>父指针只编码分组归属，不能直接当结果边输出。</p>''',
 '第三部分 · 合并连通分组']

_COMPRESS = ['查代表时，怎样减少下一次的工作？',
 '<p class="small"><strong>独立辅助例（不是主例）</strong>：四个对象 A–D，依次合并 AB、CD、BC；此时 p[D]=C，查 find(D) 得到 D→C→A。</p>' +
 '<div class="graph-pair tight">' +
 dsu_diagram(_DSU_DEMO['before']['parent'], _CHAIN_POS,
             caption='压缩前：p[D]=C，D 到根要经过 C；分组仍是 {A,B,C,D}。', root='A') +
 dsu_diagram(_DSU_DEMO['after']['parent'], _CHAIN_POS,
             caption='执行 find(D) 后：p[D]=A；分组没有改变。', root='A') +
 '</div>' +
 '<div class="columns"><div><table class="compact-table three-objects dense-table"><thead><tr><th>p</th>' +
 ''.join('<th>' + v + '</th>' for v in sorted(_DSU_DEMO['before']['parent'])) +
 '</tr></thead><tbody>' +
 parent_row('压缩前', _DSU_DEMO['before']['parent']) +
 parent_row('压缩后', _DSU_DEMO['after']['parent']) +
 '</tbody></table></div><div>' +
 r'''<p class="small"><strong>路径压缩</strong>：find 把路径上的结点直接挂到根；集合成员关系不变，也不改变已选图边。</p>
<p class="small"><strong>按大小合并</strong>：把较小集合的根接到较大集合的根下；size 只在根上有效。</p>''' +
 '</div></div>',
 '第三部分 · 合并连通分组']

_FEASIBLE = ['不成环，为什么还不足以保证最优？',
 beside(triangle_graph(marked=(('A', 'B'), ('B', 'C'))),
        r'''<p>AB:10、AC:1、BC:1 中，先选 AB 再选 BC 也不成环，成本 11；但最小生成树是 AC、BC，成本 2。</p><ul><li>分组维护保证：已选结构保持森林。</li><li>排序与割性质保证：接受的边仍可扩展到某个最优解。</li></ul>'''),
 '第三部分 · 合并连通分组']

_PART4 = part('第四部分：验证与应用',
              '把结构可行性、选择安全性与任务边界分开检查。',
              '等权与实现代价、C 状态、独立练习、MST 与最短路径。',
              '第四部分 · 验证与应用')

_TIES = ['同样便宜的边，可以得到不同答案吗？',
 r'''<pre>把主例 CE 改成 7，DE 仍为 7
共同选边：AB:1、BC:2、CD:3
最后可选 CE:7，也可选 DE:7</pre><p>两棵树总成本都为 13。<br>应检查结构与总权，不能只比较边集是否逐字相同。</p>''',
 '第四部分 · 验证与应用']

_COST = ['图的规模和已有表示如何影响选择？',
 r'''<table><thead><tr><th>实现</th><th>主要工作</th><th>时间</th></tr></thead><tbody><tr><td>矩阵 Prim</td><td>每轮找最小入口、更新一行</td><td>\(O(n^2)\)</td></tr><tr><td>边表 Kruskal</td><td>排序 m 条边，再查代表与合并</td><td>\(O(n+m\log(m+1))\)</td></tr></tbody></table><p class="small">稠密图已有矩阵时 Prim 自然；稀疏图已有边表时 Kruskal 自然。构造与排序成本也要计入。</p>''',
 '第四部分 · 验证与应用']

_C_STATE = ['代码里哪些状态承担哪些责任？',
 r'''<pre>bool present[CAP][CAP];  /* 输入：边是否存在 */
int  weight[CAP][CAP];   /* 输入：边权，可为 0 */
bool used[CAP];          /* Prim：S 的成员 */
int  key[CAP], parent[CAP];  /* Prim：接入边权 / 候选入口 */
bool has_key[CAP];       /* Prim：入口是否存在 */
DSU  dsu;                /* Kruskal：parent/size */
Edge selected[CAP-1];    /* 结果：正式接受的边 */</pre>
<p>阅读顺序：find / unite → kruskal → prim。先看状态含义，再看更新语句。</p>
<p class="small">Prim 的 parent[] 是入口边来源；DSU 的 parent[] 是集合父指针。同名不同义，不能混用。</p>''',
 '第四部分 · 验证与应用']

_RUN = ['先预测，再比较两种构造',
 r'''<p>记录主例选边、总成本，以及 E 孤立后的结果类型。<br>再预测零权边 DE 会改变哪些选择。</p><pre>gcc -std=c11 -Wall -Wextra code/mst_demo.c -o /tmp/d013
/tmp/d013</pre><p class="small">对照 Prim 与 Kruskal；相同总权是一项检查，还不是最优性的独立证明。</p>''',
 '第四部分 · 验证与应用']

_VERIFY = ['检查一棵结果树，哪些证据缺一不可？',
 r'''<table><thead><tr><th>问题</th><th>检查方式</th></tr></thead><tbody><tr><td>边真在输入图中吗？</td><td>核对存在性与权值</td></tr><tr><td>覆盖且无环吗？</td><td>连通分组、重复合并、n−1 条</td></tr><tr><td>总权计算正确吗？</td><td>重新求和</td></tr><tr><td>已经最优了吗？</td><td>安全选择理由；小图可枚举全部候选树</td></tr></tbody></table><p>非连通输入应报告森林；等权输入允许不同最优树。</p>''',
 '第四部分 · 验证与应用']

_EXERCISE = ['新网络：你能说明每一次合并吗？',
 beside(exercise_graph(),
        r'''<p>四站点 P、Q、R、S；PQ=3、PR=1、QR=2、QS=4、RS=5。</p><div class="exercise-grid"><p>1. 按 Kruskal 构造 MST。</p><p>2. 写接受/拒绝边及原因。</p><p>3. 写接受后的分组。</p><p>4. 解释 PQ 为何被拒绝。</p><p>5. 任选接受，说明割安全。</p><p>6. 计算总权。</p></div>''') +
 answer(r'''<p class="small"><strong>顺序/过程</strong>：PR1、QR2、PQ3（此时 MST 未完成，PQ 同组拒绝）、QS4、RS5（拒绝）；总权 7。</p><p class="small"><strong>分组/割</strong>：{P,R}→{P,Q,R}→{P,Q,R,S}；选 QS 时 S={P,Q,R}，跨界 QS4、RS5，QS 最轻。</p>''', '核对答案与理由（7+2 分钟）'),
 '第四部分 · 验证与应用']

_SHORTEST = ['全网最便宜，就能让每次出行都最快吗？',
 r'''<pre>三角形：AB=2，BC=2，AC=3
MST 选 AB、BC，总和4
树上 A→C 成本4，原图直达 AC 成本3</pre><p>最小生成树优化所有已选边的总权。<br>最短路径优化一个源到目标的路径权。</p>''',
 '第四部分 · 验证与应用']

_SUMMARY = ['把选择、约束和维护机制放在一起',
 r'''<table><thead><tr><th>算法/结构</th><th>维护什么</th><th>为何有用</th></tr></thead><tbody><tr><td>Prim</td><td>已连接区域与最便宜入口</td><td>最轻跨界边逐步扩展</td></tr><tr><td>Kruskal</td><td>按权排序、当前连通分组</td><td>以安全边合并森林</td></tr><tr><td>并查集</td><td>同属一个集合的关系</td><td>快速判断合并还是成环</td></tr></tbody></table><p>能连接、不会成环、成本最优，是三个需要分别解释的判断。</p>''',
 '第四部分 · 验证与应用']

_HOMEWORK = ['课后：教材导航与正式作业',
 r'''<p><strong>教材导航</strong>：精读 6.6.1；对照阅读本讲并查集代码。</p><p><strong>A. 书本习题</strong>：第 6 章选择题 <strong>(7)</strong>、应用题 <strong>(2)③</strong>。写选择理由、选边过程和总权。</p><p><strong>B. 程序实践</strong>：把主例 DE 权值由 7 改为 0，先预测两算法的选边和总权，运行 homework 输出核对；写出 Kruskal 每次合并后的分组。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B 与 3–5 行过程记录。<br>应用题 (2)①②可画作解题草稿，本次正式提交范围为③。</p>''',
 '第四部分 · 验证与应用']

_NEXT = ['下一讲：从一个起点出发，距离如何更新？',
 r'''<p>Prim 的 key[v] 是接入当前区域的一条边。<br>若任务变成“从 A 到 v 的最少总代价”，状态应保存什么？</p><p class="lead">D014：最短路径。</p>''',
 '第四部分 · 验证与应用']


SLIDES = [
    ['最小生成树与并查集',
     '<p class="lead">每次选便宜的边，怎样保证总成本最小？</p><p>数据结构与算法 · D013</p><p class="small">承接 D012；教材 6.6.1</p>',
     '课程名'],
    _OVERVIEW,
    _PART1,
    _SEARCH,
    _MAIN,
    _MST,
    _N1,
    _CUT,
    _EXCHANGE,
    _PART2,
    _PRIM,
    _AUX,
    _PRIM_PLAYER,
    _FROM_C,
    _MSF,
    _PART3,
    _KRUSKAL,
    _KRUSKAL_PLAYER,
    _DSU,
    _THREE_OBJECTS,
    _COMPRESS,
    _FEASIBLE,
    _PART4,
    _TIES,
    _COST,
    _C_STATE,
    _RUN,
    _VERIFY,
    _EXERCISE,
    _SHORTEST,
    _SUMMARY,
    _HOMEWORK,
    _NEXT,
]
