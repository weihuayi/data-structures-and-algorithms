"""D013: minimum spanning trees and dynamic equivalence classes."""
DECK_ID = "D013"
TITLE = "最小生成树与并查集"
MATH = True

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from graph_diagram import graph, beside
from tree_trace import player as step_player
from mst_trace import (MAIN_NODES, MAIN_EDGES, MAIN_LABELS, MAIN_LABEL_POS,
                       TRIANGLE_NODES, TRIANGLE_EDGES, TRIANGLE_LABEL_POS, EXCHANGE_NODES, EXCHANGE_EDGES,
                       EXERCISE_NODES, EXERCISE_EDGES, prim_player, kruskal_player,
                       kruskal_states, dsu_diagram, path_compression_demo)


def answer(html, title='核对答案与理由'):
    return '<details><summary>' + title + '</summary>' + html + '</details>'


def main_graph(*, marked=(), candidate=(), rejected=(), states=None, edge_notes=None,
               edge_note_positions=None, regions=(), view_box=(0, 0, 520, 290),
               labels=None,
               caption='主例带权无向图：边权为建设成本。'):
    return graph(MAIN_NODES, [(a, b) for a, b, w in MAIN_EDGES],
                 labels=MAIN_LABELS if labels is None else labels,
                 label_positions=MAIN_LABEL_POS, marked=marked, candidate=candidate,
                 rejected=rejected, states=states, edge_notes=edge_notes,
                 edge_note_positions=edge_note_positions, caption=caption,
                 legend='', regions=regions, view_box=view_box)


def triangle_graph(*, marked=()):
    labels = {(a, b): w for a, b, w in TRIANGLE_EDGES}
    return graph(TRIANGLE_NODES, [(a, b) for a, b, w in TRIANGLE_EDGES], labels=labels,
                 label_positions=TRIANGLE_LABEL_POS, marked=marked,
                 caption='三角形：AB=10，AC=1，BC=1。')


def exchange_graph(*, marked=(), candidate=(), edge_notes=None, edge_note_positions=None, caption):
    labels = {(a, b): w for a, b, w in EXCHANGE_EDGES}
    return graph(EXCHANGE_NODES, [(a, b) for a, b, w in EXCHANGE_EDGES], labels=labels,
                 marked=marked, candidate=candidate, edge_notes=edge_notes,
                 edge_note_positions=edge_note_positions, caption=caption, legend='',
                 view_box=(40, 0, 330, 270),
                 regions=({'points': ((45, 5), (365, 5), (365, 115), (45, 115)),
                           'label': '已选顶点', 'label_position': (240, 30)},))


def relation_player(panels, label):
    return step_player(panels, label).replace('class="tree-player"',
                                            'class="tree-player relation-player"', 1)


def answer_workspace(diagram, prompt, solution, title='核对答案与理由'):
    return ('<div class="graph-layout answer-workspace">' + diagram +
            '<div><div class="answer-prompt">' + prompt + '</div>' +
            answer(solution, title) + '</div></div>')


def exercise_graph():
    labels = {(a, b): w for a, b, w in EXERCISE_EDGES}
    return graph(EXERCISE_NODES, [(a, b) for a, b, w in EXERCISE_EDGES], labels=labels,
                 caption='独立练习：P、Q、R、S；边权如下。', view_box=(35, 20, 380, 240))


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


def parent_row(head, parent):
    return ('<tr><th>' + head + '</th>' +
            ''.join('<td>' + parent[v] + '</td>' for v in sorted(parent)) + '</tr>')


_KRUSKAL = kruskal_states()
# Real snapshot: after AB, BC, CD were accepted and AC was checked and rejected.
_THREE = next(state for state in _KRUSKAL if state['decision'] == 'reject')
_DSU_DEMO = path_compression_demo()
_STAR_POS = {'A': (260, 45), 'B': (80, 140), 'C': (180, 140), 'D': (300, 140), 'E': (420, 140)}
_CHAIN_POS = {'A': (260, 40), 'B': (80, 125), 'C': (300, 125), 'D': (420, 200)}
_CUT_AB = {'points': ((20, 5), (330, 5), (330, 100), (20, 100)),
           'label': '已选顶点', 'label_position': (95, 30)}
_CUT_ABC = {'points': ((20, 5), (330, 5), (330, 100), (180, 270), (85, 265), (20, 100)),
            'label': '已选顶点', 'label_position': (95, 30)}


_OVERVIEW = ['本讲要解决哪四个问题？', r'''<table><thead><tr><th>部分</th><th>要解决的问题</th><th>页码</th><th>分钟</th></tr></thead><tbody>
<tr><td>第一部分</td><td>怎样定义连接全网的最低成本问题？</td><td>1–9</td><td>20</td></tr>
<tr><td>第二部分</td><td>怎样从一个顶点出发，逐步扩张连接区域？</td><td>10–15</td><td>17</td></tr>
<tr><td>第三部分</td><td>怎样按照边的成本顺序，逐步合并不同分组？</td><td>16–23</td><td>22</td></tr>
<tr><td>第四部分</td><td>怎样检查结果、分析计算代价并解决新问题？</td><td>24–33</td><td>26</td></tr>
</tbody></table>''', '课程路线']

_PART1 = part('第一部分：问题与数学依据',
              '从一棵搜索树开始，重新定义“连接全网”的优化目标。',
              '生成树、n−1 条边的边界、最小生成树性质与交换论证。',
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
 relation_player([
 beside(main_graph(marked=(('A', 'B'),), candidate=(('B', 'C'),), regions=(_CUT_AB,),
            states={'A': 'visited', 'B': 'visited'},
            edge_notes={('A', 'B'): 'F', ('B', 'C'): 'e'},
            edge_note_positions={('A', 'B'): (175, 80), ('B', 'C'): (231, 156)},
            caption='蓝色区域是已选顶点，橙虚线是当前候选边；红粗边已经接受。'),
        r'''<p>\(U=\{A,B\}\)，\(V-U=\{C,D,E\}\)。</p>
<p><strong>教材 MST 性质（概述）</strong>：在连通网中，将顶点分成非空的 \(U\) 与 \(V-U\)，连接两组的最小权值边必包含在某棵 MST 中。</p>
<table class="compact-table"><thead><tr><th>全部跨界边</th><th>权</th></tr></thead><tbody><tr><td>AC</td><td>4</td></tr><tr class="matrix-focus"><td>BC（最轻 e）</td><td>2</td></tr><tr><td>BD</td><td>5</td></tr></tbody></table>
<p class="compact-text">已选边集 \(F=\{AB\}\) 在 \(U\) 内。为什么接受 BC 时还能保留这些边？下一页解释。</p>'''),
 beside(main_graph(marked=(('A', 'B'), ('B', 'C')), candidate=(('C', 'D'),), regions=(_CUT_ABC,),
            states={'A': 'visited', 'B': 'visited', 'C': 'visited'},
            edge_notes={('A', 'B'): 'F′', ('B', 'C'): 'F′', ('C', 'D'): 'e′'},
            edge_note_positions={('A', 'B'): (175, 80), ('B', 'C'): (231, 156), ('C', 'D'): (257, 206)},
            caption='接受 BC 后，已选顶点增加 C；已选边为 AB、BC。'),
        r'''<p>\(U=\{A,B,C\}\)，\(V-U=\{D,E\}\)。</p>
<p>已选边 AB、BC 都在 \(U\) 内；重新比较连接两组的所有边。</p>
<table class="compact-table"><thead><tr><th>新的全部跨界边</th><th>权</th></tr></thead><tbody><tr><td>BD</td><td>5</td></tr><tr class="matrix-focus"><td>CD（最轻 e′）</td><td>3</td></tr><tr><td>CE</td><td>6</td></tr></tbody></table>
<p class="compact-text">CD 的权值最小，可按教材 MST 性质继续接入 D。每次扩大 \(U\) 后，都要重新比较。</p>''')
 ], '教材 MST 性质：连接两组顶点'),
 '第一部分 · 问题与数学依据']

_EXCHANGE = ['为什么这次局部选择不损失最优解？',
 relation_player([
 beside(exchange_graph(marked=(('A', 'B'), ('B', 'C')),
                edge_notes={('A', 'B'): 'F'},
                edge_note_positions={('A', 'B'): (145, 40)},
                caption='① 独立辅助例：AB=1、AC=2、BC=2；T={AB,BC}，总权 3。'),
        r'''<p><strong>不变量：</strong>存在某棵 MST T，包含已选边集合 \(F\)。</p>
<p>本例 \(U=\{A,B\}\)，\(V-U=\{C\}\)；已选边 \(F=\{AB\}\) 在 \(U\) 内，最轻连接边可取 e=AC。</p>
<p class="compact-text">一般地，若 e 已在 T 中，它已经与 \(F\) 共存。若 e 不在 T 中，尝试交换。</p>'''),
 beside(exchange_graph(marked=(('A', 'B'), ('B', 'C')), candidate=(('A', 'C'),),
                edge_notes={('A', 'B'): 'F', ('A', 'C'): 'e', ('B', 'C'): 'f'},
                edge_note_positions={('A', 'B'): (145, 40), ('A', 'C'): (163, 127), ('B', 'C'): (278, 125)},
                caption='② 加入 e=AC 形成唯一环；另一条连接两组的边是 f=BC。'),
        r'''<p><strong>为什么一定能找到 f？</strong></p>
<p>沿环从 \(U\) 走到 \(V-U\) 后必须跨回，因此还有另一条连接两组的边 f。</p>
<p><strong>为什么可以删 f？</strong><br>已选边都在各组内部，\(f\notin F\)；删 f 不会撤销已选边。</p>'''),
 beside(exchange_graph(marked=(('A', 'B'), ('A', 'C')),
                edge_notes={('A', 'B'): 'F'},
                edge_note_positions={('A', 'B'): (145, 40)},
                caption=r'③ T′={AB,AC} 包含 \(F\) 与 e；本例总权仍为 3。'),
        r'''<p><strong>交换后仍是生成树，且包含 \(F\cup\{e\}\)。</strong></p>
<p>e 是连接两组的最小权值边，所以 \(w(e)\leq w(f)\)。</p>
<p>\(w(T')=w(T)+w(e)-w(f)\leq w(T)\)。T 已最优，因此 T′ 也最优。</p>
<p class="compact-text"><strong>交换论证的收口：</strong>从 \(F=\varnothing\) 开始，每步保持可扩展性；当已选边连通全部顶点并组成一棵树时，它就是 MST。</p>''')
 ], '安全边交换论证'),
 '第一部分 · 问题与数学依据']

_PART2 = part('第二部分：怎样让已连接区域逐步扩大？',
              '从一个顶点出发，每次只接受连接当前区域与外部的一条边。',
              '先说明构造规则与辅助状态，再观察每一步怎样更新。',
              '第二部分 · 逐步扩大已连接区域')

_PRIM = ['普里姆算法：怎样逐步接入新顶点？',
 r'''<div class="quote compact-quote"><strong>普里姆算法（Prim's Algorithm）数学规则</strong><br>从任一顶点 \(u_0\) 开始，令 \(U=\{u_0\}\)、\(F=\varnothing\)。每次在 \(u\in U,\ v\in V-U\) 的边中取最轻边 \(e=(u,v)\)，接受 \(e\) 并把 \(v\) 加入 \(U\)，直到 \(U=V\)。</div>
<ol class="compact-list"><li>初始时，\(U\) 只含起点。</li><li>维护已纳入顶点集合 \(U\) 与已接受边集 \(F\)。</li><li>比较连接 \(U\) 与 \(V-U\) 的边，接受最轻边和外部顶点。</li></ol>
<p>已选边都在 \(U\) 内。用前面的交换理由，每步加入最轻连接边时仍可保留已选边，并包含于某棵 MST。</p>
<p class="small">前提：本页讨论连通图。选择的是连接 \(U\) 的一条边，不是离起点最近的顶点。</p>''',
 '第二部分 · 逐步扩大已连接区域']

_AUX = ['计算机执行 Prim，需要保存哪些辅助信息？',
 '<div class="graph-lesson">' + beside(
 main_graph(marked=(('A', 'B'),), candidate=(('B', 'C'),), states={'A': 'visited', 'B': 'visited'},
            caption=r'输入图不变；当前 \(U=\{A,B\}\)，已选边为 AB。C 的入口 AC:4 → BC:2。'),
 r'''<p><strong>每个外部点，只保留最便宜的一个入口。</strong></p>
<table class="compact-table"><thead><tr><th>\(v\in V-U\)</th><th>parent[v]</th><th>key[v]</th><th>has_key</th></tr></thead><tbody><tr class="matrix-focus"><td>C</td><td>B</td><td>2</td><td>1</td></tr><tr><td>D</td><td>B</td><td>5</td><td>1</td></tr><tr><td>E</td><td>—</td><td>—</td><td>0</td></tr></tbody></table>
<p class="compact-text">key[v] 是接入 \(U\) 的一条边权，<strong>不是从起点到 v 的路径长度</strong>。没有入口时，key 不取值。</p>''') +
 r'''<p class="compact-text">纳入 u 后，已有入口且 uv 存在时：\(\mathrm{key}_{新}[v]=\min(\mathrm{key}_{旧}[v],w(u,v))\)；更小时同时改 parent。首次出现入口直接赋值，无边则不更新。</p>
<p class="small">程序对应：used[v] 表示 \(v\in U\)，selected[] 保存 \(F\)；候选 parent 只记来源，顶点被接受后入口边才进入 \(F\)。输入图另用矩阵或邻接表保存。</p></div>''',
 '第二部分 · 逐步扩大已连接区域']

_PRIM_PLAYER = ['从 A 开始，观察顶点集合、候选入口与已选边',
 prim_player(),
 '第二部分 · 逐步扩大已连接区域']

_FROM_C = ['换一个起点，先补完两步',
 answer_workspace(main_graph(states={'C': 'current'}, caption='从 C 开始，图与边权不变；先独立预测，再展开核对。'),
        r'''<p>从 C 出发，独立预测：</p><ol class="compact-list"><li>第一条接受哪条边？纳入新顶点后，A 的候选入口如何更新？</li><li>第二条接受哪条边？最终总权改变吗？</li></ol>''',
        r'''<table class="compact-table"><tbody><tr><th>第一步</th><td>CB:2；A 的入口 CA:4 → BA:1</td></tr><tr><th>第二步</th><td>BA:1</td></tr><tr><th>继续</th><td>CD:3、CE:6；总权 12</td></tr></tbody></table><p class="compact-text">起点改变选择顺序；主例的 MST 唯一，总权不变。</p>'''),
 '第二部分 · 逐步扩大已连接区域']

_MSF = ['没有跨界候选，就把剩余点忽略吗？',
 beside(disconnected_graph(), r'''<p>删除 CE、DE 后，E 与 A–D 不连通。图中红边 AB、BC、CD 连接 A–D，E 单独构成一个分量。</p><p>此图不存在覆盖所有顶点的生成树。对每个连通分量分别求最小生成树，得到<strong>最小生成森林（Minimum Spanning Forest，MSF）</strong>。</p><p class="small">结果：2 个连通分量、3 条选边、总权 6；孤立顶点也是一棵树。</p>'''),
 '第二部分 · 逐步扩大已连接区域']

_PART3 = part('第三部分：怎样依次合并不同连通分组？',
              '从最便宜的边开始，判断两端是否已经连通。',
              '排序、接受/拒绝、动态分组，以及分组的内部表示与维护。',
              '第三部分 · 合并连通分组')

_KRUSKAL = ['克鲁斯卡尔算法（Kruskal\'s Algorithm）：按边的成本顺序合并分组',
 r'''<div class="quote compact-quote"><strong>算法规则（数学描述）</strong><br>把所有边按权值非递减排列；每个顶点自成一组。扫描边 (u,v)：不同组则接受并合并，同组则拒绝。边用完返回森林；接受 n−1 条边时已得到 MST，可提前停止。</div>
<p class="compact-text"><strong>无环：</strong>只合并不同分组。<strong>本讲演示与 C 程序：</strong>扫描全部边；MST 完成后，仅核对剩余边。</p>
<p class="compact-text"><strong>为何可以选：</strong>令 \(U\) 是包含 u 的当前分量，其余顶点为 \(V-U\)，已选边不连接这两组。更轻的连接边若已处理，原本应被接受，端点现在就不可能分属两组；早先拒绝的边也不会重新连接两组，因为分组只合并。</p>
<p class="compact-text">所以当前边是连接两组的最轻边，可用前面的 MST 性质与交换理由。平局按端点编号处理，只为输出可复现。</p>''',
 '第三部分 · 合并连通分组']

_KRUSKAL_PLAYER = ['从最便宜的边开始，观察分组怎样合并',
 kruskal_player(),
 '第三部分 · 合并连通分组']

_DSU = ['怎样高效维护不断合并的分组？',
 r'''<div class="quote compact-quote"><strong>课程补充模型（不是教材逐字定义）</strong><br><strong>并查集（Disjoint Set Union，DSU；又称 Union-Find）</strong>维护一族互不相交的动态集合：find(x) 返回 x 所属集合的代表，union(a,b) 合并两个不同集合。</div>
<p>它服务于 Kruskal 的两件事：判断候选边两端是否同组；接受边后把两组并成一组。</p>
<p>这里的分组由“当前已经接受的边”诱导，不是原输入图的全部连通关系。</p>
<p><strong>边界</strong>：DSU 只负责维护分组和判环，不能单独保证 MST 的全局最优；最优性还依赖按权扫描与教材 MST 性质。</p>''',
 '第三部分 · 合并连通分组']

_THREE_OBJECTS = ['选中的森林、当前分组与父指针：三者是什么关系？',
 '<div class="dsu-workspace"><div class="graph-pair">' +
 main_graph(marked=tuple(e[:2] for e in _THREE['selected_edges']),
            rejected=tuple(e[:2] for e in _THREE['rejected_edges']),
            view_box=(30, 10, 480, 270),
            caption=r'真实快照：已选边 \(F=\{AB,BC,CD\}\)；E 单独成树。') +
 dsu_diagram(_THREE['dsu_parent'], _STAR_POS,
             caption='同一快照的父指针：v→p[v]；A、E 各自为根。',
             root='A', view_box=(35, 5, 440, 210)) +
 '</div>' +
 '<table class="compact-table three-objects"><thead><tr><th>对象</th><th>当前值（真实快照）</th><th>回答什么</th></tr></thead><tbody>' +
 '<tr><td>已选边集合</td><td>' + edge_text(_THREE['selected_edges']) + '</td><td>哪些图边已被正式接受？</td></tr>' +
 '<tr><td>分组划分</td><td>' + group_text(_THREE['components']) + '</td><td>哪些顶点已被已选边连在一起？</td></tr>' +
 '<tr><td>DSU 父指针 p</td><td>B、C、D→A；A、E→自己</td><td>怎样编码“属于哪一组”？</td></tr>' +
 '</tbody></table>' +
 r'''<p class="compact-text">p[C]=A 对应已拒绝的 AC；p[D]=A 对应原图不存在的 AD。<strong>父指针不能直接当结果边输出。</strong></p></div>''',
 '第三部分 · 合并连通分组']

_COMPRESS = ['查代表时，怎样减少下一次的工作？',
 '<div class="dsu-workspace"><p class="small"><strong>独立辅助例（不是主例）</strong>：依次合并 AB、CD、BC，再查 find(D)。</p>' +
 '<div class="graph-pair">' +
 dsu_diagram(_DSU_DEMO['before']['parent'], _CHAIN_POS,
             caption='压缩前：p[D]=C，查找路径 D→C→A。', root='A', view_box=(35, 5, 440, 260)) +
 dsu_diagram(_DSU_DEMO['after']['parent'], _CHAIN_POS,
             caption='压缩后：p[D]=A；分组仍是 {A,B,C,D}。', root='A', view_box=(35, 5, 440, 260)) +
 '</div>' +
 '<div class="columns"><div><table class="compact-table"><thead><tr><th>p</th>' +
 ''.join('<th>' + v + '</th>' for v in sorted(_DSU_DEMO['before']['parent'])) +
 '</tr></thead><tbody>' +
 parent_row('压缩前', _DSU_DEMO['before']['parent']) +
 parent_row('压缩后', _DSU_DEMO['after']['parent']) +
 '</tbody></table></div><div>' +
 r'''<p class="small"><strong>路径压缩</strong>：find 把路径上的结点直接挂到根；集合成员关系不变，也不改变已选图边。</p>
<p class="small"><strong>按大小合并</strong>：把较小集合的根接到较大集合的根下；size 只在根上有效。</p>''' +
 '</div></div></div>',
 '第三部分 · 合并连通分组']

_DSU_CHECK = ['直接父结点不同，就一定不在同一组吗？',
 answer_workspace(
 dsu_diagram({'A': 'B', 'B': 'B', 'C': 'D', 'D': 'B'},
             {'B': (260, 40), 'A': (80, 125), 'D': (300, 125), 'C': (420, 200)},
             caption=r'查找前输入（独立例）：p[A]=B、p[B]=B、p[C]=D、p[D]=B；已选边集合 \(F\) 另存。',
             root='B', view_box=(35, 5, 440, 260)),
 r'''<p><strong>独立判断（2 分钟）</strong></p><ol class="compact-list"><li>A、C 的直接父结点不同，它们同组吗？写出代表。</li><li>执行 find(C) 后，哪个父指针改变？</li><li>集合划分和已选边集合 \(F\) 改变吗？</li></ol>''',
 r'''<p><strong>同组：</strong>A→B，C→D→B；代表都是 B。</p><p><strong>压缩：</strong>p[C] 从 D 改为 B，其余不变。</p><p><strong>不变：</strong>划分仍为 {A,B,C,D}，\(F\) 不变。判断同组要比较 find 的结果，不能只比较直接 parent。</p>'''),
 '第三部分 · 合并连通分组']

_FEASIBLE = ['不成环，为什么还不足以保证最优？',
 beside(triangle_graph(marked=(('A', 'B'), ('B', 'C'))),
        r'''<p>AB:10、AC:1、BC:1 中，先选 AB 再选 BC 也不成环，成本 11；但最小生成树是 AC、BC，成本 2。</p><ul><li>分组维护保证：已选结构保持森林。</li><li>排序与教材 MST 性质保证：接受的边仍可扩展到某个最优解。</li></ul>'''),
 '第三部分 · 合并连通分组']

_PART4 = part('第四部分：验证与应用',
              '把结构可行性、选择安全性与任务边界分开检查。',
              '等权与实现代价、C 状态、独立练习、MST 与最短路径。',
              '第四部分 · 验证与应用')

_TIE_LABELS = {**MAIN_LABELS, ('C', 'E'): 7}
_TIES = ['同样便宜的边，可以得到不同答案吗？',
 r'''<p class="compact-text"><strong>主例只改 CE：6 → 7</strong>，DE 仍为 7，其余边权不变。红粗边表示各方案选中的边。</p>''' +
 '<div class="graph-pair graph-comparison">' +
 main_graph(marked=(('A', 'B'), ('B', 'C'), ('C', 'D'), ('C', 'E')),
            labels=_TIE_LABELS,
            caption=r'方案一：AB、BC、CD、CE；总权 \(1+2+3+7=13\)。') +
 main_graph(marked=(('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')),
            labels=_TIE_LABELS,
            caption=r'方案二：AB、BC、CD、DE；总权 \(1+2+3+7=13\)。') +
 r'''</div><p class="compact-text">两棵树都覆盖全网且无环，总权同为 13。等权时最优边集可能不唯一；检查结构与总权，不能只比较边集。</p>''',
 '第四部分 · 验证与应用']

_COST = ['图的规模和已有表示如何影响选择？',
 r'''<p class="small">\(n=|V|\)，\(m=|E|\)；教材用 e 表示边数。下表比较<strong>已有相应输入表示</strong>上的算法阶段。</p>
<table><thead><tr><th>实现</th><th>主要工作</th><th>时间</th></tr></thead><tbody><tr><td>矩阵 Prim</td><td>每轮找最小入口、更新一行</td><td>\(O(n^2)\)</td></tr><tr><td>边表 Kruskal</td><td>排序 m 条边，再查代表与合并</td><td>\(O(n+m\log(m+1))\)</td></tr></tbody></table>
<p class="compact-text">稠密图已有矩阵时 Prim 自然；稀疏图已有边表时 Kruskal 自然。DSU 采用按大小合并与路径压缩，操作序列摊还高效，不等于每次 find 保证 O(1)。</p>
<p class="small">完整任务还需计输入准备和空间：演示 Graph 同时保存矩阵与边表；矩阵占用 O(n²) 空间，不能从 Kruskal 的时间表推成整个程序只用线性空间。</p>''',
 '第四部分 · 验证与应用']

_C_STATE = ['教材字段与课堂程序，怎样一一对应？',
 r'''<table class="implementation-map"><thead><tr><th>教材</th><th>课堂 C 程序</th><th>必须区分</th></tr></thead><tbody>
<tr><td>lowcost / adjvex</td><td>key / parent</td><td>入口边权与来源，不是路径距离</td></tr>
<tr><td>lowcost=0 表示已纳入</td><td>used[v]</td><td>零权边与已纳入标志分开</td></tr>
<tr><td>无边的存储约定</td><td>present / weight</td><td>权值 0 不能代替“无边”</td></tr>
<tr><td>Vexset[v] 分组编号</td><td>find(v) 返回代表</td><td>不同 parent 仍可能同组</td></tr>
</tbody></table>
<p class="compact-text">has_key 区分有无入口；结果森林另存。Prim 的 parent 是入口来源，DSU 的 parent 是集合父指针。</p>
<p class="small">阅读：find / unite → kruskal → prim。教材 Vexset 合并时改写全表，其代价不能套用当前 DSU 的摊还结论。</p>''',
 '第四部分 · 验证与应用']

_VERIFY = ['检查一棵结果树，哪些证据缺一不可？',
 r'''<p class="small"><strong>先预测：</strong>主例与 DE=0 的选边、总权；E 孤立时的结果类型。再从本 Deck 目录运行并核对。</p>
<table class="compact-table"><thead><tr><th>问题</th><th>检查方式</th></tr></thead><tbody><tr><td>边属于输入吗？</td><td>核对存在性与权值</td></tr><tr><td>覆盖且无环吗？</td><td>核对原图分量、重复合并、边数 n−分量数</td></tr><tr><td>总权正确吗？</td><td>重新求和</td></tr><tr><td>已经最优了吗？</td><td>安全选择依据；小图独立枚举</td></tr></tbody></table>
<pre class="run-command">gcc -std=c11 -Wall -Wextra code/mst_demo.c -o /tmp/d013
/tmp/d013</pre><p class="small">非连通返回 MSF；等权允许不同最优树。两算法总权相同仍不是独立最优性证明。</p>''',
 '第四部分 · 验证与应用']

_EXERCISE = ['新网络：你能说明每一次合并吗？',
 answer_workspace(exercise_graph(),
        r'''<p>四站点 P、Q、R、S；PQ=3、PR=1、QR=2、QS=4、RS=5。</p><div class="exercise-grid"><p>1. 按 Kruskal 扫描全部边。</p><p>2. 写接受/拒绝及原因。</p><p>3. 写接受后的分组。</p><p>4. 解释 PQ 为何被拒绝。</p><p>5. 任选接受边，说明依据。</p><p>6. 标完成时刻、算总权。</p></div>''',
        r'''<p class="small"><strong>过程</strong>：接受 PR1、QR2；PQ3 同组拒绝，此时 MST 未完成；接受 QS4 后 MST 已完成，总权 7。继续核对 RS5：同组拒绝。</p><p class="small"><strong>分组/依据</strong>：{P,R}→{P,Q,R}→{P,Q,R,S}；接受 QS 时 \(U=\{P,Q,R\}\)，\(V-U=\{S\}\)，连接两组的边有 QS4、RS5，QS 最轻。</p><p class="small">若采用提前终止，RS 是未处理，不是已拒绝。</p>''', '核对答案与理由（7+2 分钟）'),
 '第四部分 · 验证与应用']

_SHORTEST = ['总边权最小，两点间路径就最短吗？',
 beside(graph(TRIANGLE_NODES, [('A', 'B'), ('A', 'C'), ('B', 'C')],
              labels={('A', 'B'): 2, ('A', 'C'): 3, ('B', 'C'): 2},
              label_positions=TRIANGLE_LABEL_POS,
              marked=(('A', 'B'), ('B', 'C')), candidate=(('A', 'C'),),
              view_box=(40, 10, 330, 250), legend='',
              caption='红粗边：MST；橙虚线：原图中 A 到 C 的最短路径。'),
        r'''<p><strong>MST：</strong>选 AB、BC，所有已选边总权为 \(2+2=4\)。</p>
<p><strong>树上 A 到 C：</strong>走 A→B→C，路径权为 \(2+2=4\)。</p>
<p><strong>原图 A 到 C：</strong>直接走 AC，路径权为 \(3<4\)。</p>
<p class="small">最小生成树优化全部已选边的总权；最短路径优化从起点到目标的路径权。目标不同，树上路径未必最短。</p>'''),
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
    _DSU_CHECK,
    _FEASIBLE,
    _PART4,
    _TIES,
    _COST,
    _C_STATE,
    _VERIFY,
    _EXERCISE,
    _SHORTEST,
    _SUMMARY,
    _HOMEWORK,
    _NEXT,
]
