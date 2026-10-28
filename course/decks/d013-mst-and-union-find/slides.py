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
                       prim_states, kruskal_states, dsu_diagram, path_compression_demo,
                       input_row_html, matrix_row, edge_preparation_views)


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


def answer_workspace(diagram, prompt, solution, title='核对答案与理由', class_name=''):
    return ('<div class="graph-layout answer-workspace ' + class_name + '">' + diagram +
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
_PRIM_A = prim_states()[0]
_STAR_POS = {'A': (260, 45), 'B': (80, 140), 'C': (180, 140), 'D': (300, 140), 'E': (420, 140)}
_CHAIN_POS = {'A': (260, 40), 'B': (80, 125), 'C': (300, 125), 'D': (420, 200)}
_CUT_AB = {'points': ((20, 5), (330, 5), (330, 100), (20, 100)),
           'label': '已选顶点', 'label_position': (95, 30)}
_CUT_ABC = {'points': ((20, 5), (330, 5), (330, 100), (180, 270), (85, 265), (20, 100)),
            'label': '已选顶点', 'label_position': (95, 30)}


_OVERVIEW = ['本讲要解决哪四个问题？', r'''<table><thead><tr><th>部分</th><th>要解决的问题</th><th>页码</th><th>分钟</th></tr></thead><tbody>
<tr><td>第一部分</td><td>怎样定义连接全网的最低成本问题？</td><td>1–9</td><td>20</td></tr>
<tr><td>第二部分</td><td>怎样从存储信息出发，逐步扩大连接区域？</td><td>10–17</td><td>17</td></tr>
<tr><td>第三部分</td><td>怎样组织边，并维护不断合并的分组？</td><td>18–29</td><td>25</td></tr>
<tr><td>第四部分</td><td>怎样检查代价、联系其他课程并判断适用性？</td><td>30–41</td><td>23</td></tr>
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

_PART2 = ['输入图、工作状态与结果分别保存什么？',
 r'''<p class="compact-text">回到 D011 的图 ADT 与 D012 的访问标记：保存关系与记录计算进度，职责不同。</p>
<table><thead><tr><th>职责</th><th>要回答什么</th><th>本讲中的表示</th></tr></thead><tbody>
<tr><td>输入图</td><td>哪些边存在，权值多少？</td><td>矩阵、邻接表或完整边数组</td></tr>
<tr><td>工作状态</td><td>当前已知什么，下一步怎样决定？</td><td>纳入标记、候选入口、分组</td></tr>
<tr><td>结果</td><td>哪些边已正式接受？</td><td>已选边集合 \(F\) 与总权</td></tr>
</tbody></table><p class="compact-text">同一输入图可以支持不同算法；算法还需组织自己的工作状态。</p>''',
 '第二部分 · 逐步扩大已连接区域']

_PRIM = ['普里姆算法：怎样逐步接入新顶点？',
 r'''<div class="quote compact-quote"><strong>普里姆算法（Prim's Algorithm）数学规则</strong><br>从任一顶点 \(u_0\) 开始，令 \(U=\{u_0\}\)、\(F=\varnothing\)。每次在 \(u\in U,\ v\in V-U\) 的边中取最轻边 \(e=(u,v)\)，接受 \(e\) 并把 \(v\) 加入 \(U\)，直到 \(U=V\)。</div>
<ol class="compact-list"><li>初始时，\(U\) 只含起点。</li><li>维护已纳入顶点集合 \(U\) 与已接受边集 \(F\)。</li><li>比较连接 \(U\) 与 \(V-U\) 的边，接受最轻边和外部顶点。</li></ol>
<p>已选边都在 \(U\) 内。用前面的交换理由，每步加入最轻连接边时仍可保留已选边，并包含于某棵 MST。</p>
<p class="small">前提：本页讨论连通图。选择的是连接 \(U\) 的一条边，不是离起点最近的顶点。</p>''',
 '第二部分 · 逐步扩大已连接区域']

_ENTRY_MOTIVE = ['已有的最佳入口，还要每次重找吗？',
 beside(main_graph(states={'A': 'visited'}, candidate=(('A', 'B'),),
                   caption='当前只纳入 A；候选入口来自 A 的邻接信息。'),
        '<p>朴素做法：每次重新比较已纳入区域与外部之间的所有边。</p>' +
        '<table class="compact-table"><thead><tr><th>外部点</th><th>当前最佳入口</th></tr></thead><tbody>' +
        ''.join('<tr><td>' + v + '</td><td>' +
                (f'{_PRIM_A["parent"][v]}{v}:{_PRIM_A["key"][v]}' if v in _PRIM_A['key'] else '无入口') +
                '</td></tr>' for v in MAIN_NODES if v != 'A') +
        r'''</tbody></table><p>纳入 B 后，C 的旧最佳入口 AC=4 不必丢弃：只需与新边 BC=2 比较。</p>
<p class="small">保存每个外部点的最好入口，可以复用此前的比较结果。</p>'''),
 '第二部分 · 逐步扩大已连接区域']

_INPUT_UPDATE = ['接入 B 后，怎样从存储记录更新候选？',
 answer_workspace(
 '<div><h3>矩阵 B 行（列 A–E）</h3>' + input_row_html('B') +
 r'''<p class="small">— 表示无边，存在性由 present 判定；零权边仍然存在。</p>
<h3>B 的全部邻接项</h3><p>''' + '、'.join(f'{v}:{w}' for v, w in matrix_row('B') if w is not None) + r'''</p>
<p class="compact-text">已接受 AB，\(U=\{A,B\}\)。本轮跳过已纳入点 A、B。</p></div>''',
 r'''<p><strong>独立预测（1 分钟）</strong></p><table class="compact-table"><thead><tr><th>外部点</th><th>更新前入口</th></tr></thead><tbody><tr><td>C</td><td>AC:4</td></tr><tr><td>D</td><td>无入口</td></tr><tr><td>E</td><td>无入口</td></tr></tbody></table>
<p>补全三个新入口，并说明每次改变或不变的依据。矩阵与邻接表分别检查多少位置或邻接项？</p>''',
 r'''<table class="compact-table"><thead><tr><th>顶点</th><th>旧 → 新</th><th>依据</th></tr></thead><tbody><tr><td>C</td><td>AC:4 → BC:2</td><td>新边更轻</td></tr><tr><td>D</td><td>无 → BD:5</td><td>首次有入口</td></tr><tr><td>E</td><td>无 → 无</td><td>没有 BE</td></tr></tbody></table>
<p>矩阵循环检查 5 个顶点位置；邻接表枚举 3 项。已纳入点先跳过，不把它们重新接入。</p>''',
 class_name='source-workspace'),
 '第二部分 · 逐步扩大已连接区域']

_AUX = ['计算机执行 Prim，需要保存哪些辅助信息？',
 '<div class="graph-lesson">' + beside(
 main_graph(marked=(('A', 'B'),), candidate=(('B', 'C'),), states={'A': 'visited', 'B': 'visited'},
            caption=r'输入图不变；当前 \(U=\{A,B\}\)，已选边为 AB。C 的入口 AC:4 → BC:2。'),
 r'''<p><strong>每个外部点，只保留最便宜的一个入口。</strong></p>
<table class="compact-table"><thead><tr><th>\(v\in V-U\)</th><th>parent[v]</th><th>key[v]</th><th>has_key</th></tr></thead><tbody><tr class="matrix-focus"><td>C</td><td>B</td><td>2</td><td>1</td></tr><tr><td>D</td><td>B</td><td>5</td><td>1</td></tr><tr><td>E</td><td>—</td><td>—</td><td>0</td></tr></tbody></table>
<p class="compact-text">key[v] 是接入 \(U\) 的一条边权，<strong>不是从起点到 v 的路径长度</strong>。没有入口时，key 不取值。</p>''') +
 r'''<p class="compact-text">纳入 u 后，已有入口且 uv 存在时：\(\mathrm{key}_{新}[v]=\min(\mathrm{key}_{旧}[v],w(u,v))\)；更小时同时改 parent。首次出现入口直接赋值，无边则不更新。</p>
<p class="small">教材 lowcost/adjvex 对应 key/parent；used[v] 表示 \(v\in U\)，has_key 区分有无入口。候选 parent 只记来源；接受顶点时入口边才进入 \(F\)。</p></div>''',
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

_PART3 = ['换一种组织：怎样从全部边中依次选择？',
 r'''<p>前一种方法按新接入的顶点读取邻接信息。现在改为先整理全部边，再按成本依次判断。</p>
<table><thead><tr><th>已有输入</th><th>需要的操作</th><th>准备得到什么</th></tr></thead><tbody>
<tr><td>邻接矩阵</td><td>枚举存在的无向边</td><td rowspan="2">每条边只保留一次的边数组</td></tr>
<tr><td>邻接表</td><td>枚举并去掉双份记录</td></tr>
</tbody></table><p>图的存储不变，访问次序可以重组。得到边数组后再按权排序。</p>''',
 '第三部分 · 合并连通分组']

_EDGE_PREP = ['同一张图，怎样提取出同一份边数组？',
 relation_player(edge_preparation_views(), '矩阵与邻接表提取无向边') +
 r'''<p class="compact-text">条件：无向简单图，邻接表每边两份对称记录。字母按 A–E 编号；排序后的副本用于扫描，不改变输入图。</p>''',
 '第三部分 · 合并连通分组']

_KRUSKAL = ['克鲁斯卡尔算法：按边的成本顺序合并分组',
 r'''<div class="quote compact-quote"><strong>克鲁斯卡尔算法（Kruskal's Algorithm）数学规则</strong><br>把所有边按权值非递减排列；每个顶点自成一组。扫描边 (u,v)：不同组则接受并合并，同组则拒绝。边用完返回森林；接受 n−1 条边时已得到 MST，可提前停止。</div>
<p class="compact-text"><strong>无环：</strong>只合并不同分组。<strong>本讲演示与 C 程序：</strong>扫描全部边；MST 完成后，仅核对剩余边。</p>
<p class="compact-text"><strong>为何可以选：</strong>令 \(U\) 是包含 u 的当前分量，其余顶点为 \(V-U\)，已选边不连接这两组。更轻的连接边若已处理，原本应被接受，端点现在就不可能分属两组；早先拒绝的边也不会重新连接两组，因为分组只合并。</p>
<p class="compact-text">所以当前边是连接两组的最轻边，可用前面的 MST 性质与交换理由。平局按端点编号处理，只为输出可复现。</p>''',
 '第三部分 · 合并连通分组']

_KRUSKAL_PLAYER = ['从最便宜的边开始，观察分组怎样合并',
 kruskal_player(),
 '第三部分 · 合并连通分组']

_CONNECTIVITY = ['能否用已学的搜索，判断下一条边会不会成环？',
 beside(graph(MAIN_NODES, [('A', 'B'), ('B', 'C'), ('C', 'D'), ('A', 'C')],
              marked=(('A', 'B'), ('B', 'C'), ('C', 'D')), candidate=(('A', 'C'),),
              caption=r'红边是当前 \(F=\{AB,BC,CD\}\)；橙虚线 AC 尚未接受；E 单独一组。', legend=''),
        r'''<p>只沿当前已选边做 DFS/BFS，可以找到 A—B—C。加入 AC 会闭环，因此拒绝。</p>
<p><strong>查的是当前选边中的路径。</strong>不能用原输入图的连通性，也不能只查有无直接边。</p>
<p>搜索能够完成判断。但下一条边到来，还要从头搜索吗？</p>
<p class="small">分组只合并、不拆分；能否保存已经得到的连通信息？</p>'''),
 '第三部分 · 合并连通分组']

_GROUP_IDS = ['把已经知道的连通分组保存下来',
 r'''<p>教材 Vexset 保存所属组的编号。回看接受 CD 的一步：把 ABC 与 D 合并。</p>
<table><thead><tr><th>Vexset</th><th>A(0)</th><th>B(1)</th><th>C(2)</th><th>D(3)</th><th>E(4)</th></tr></thead><tbody>
<tr><th>合并前</th><td>0</td><td>0</td><td>0</td><td>3</td><td>4</td></tr>
<tr><th>合并后</th><td>0</td><td>0</td><td>0</td><td class="matrix-focus">0</td><td>4</td></tr></tbody></table>
<p>查询：比较两个编号。合并：扫描全表，把编号 3 改为 0。</p>
<p><strong>问题转移了：</strong>不用每次重新搜索，但合并两大组时，是否必须逐个改写成员？</p>
<p class="small">本页数字是分组编号，不是父结点。教材 6.6.1，算法 6.9。</p>''',
 '第三部分 · 合并连通分组']

_DSU = ['怎样高效维护不断合并的分组？',
 r'''<div class="quote compact-quote"><strong>课程补充模型（不是教材逐字定义）</strong><br><strong>并查集（Disjoint Set Union，DSU；又称 Union-Find）</strong>维护一族互不相交的动态集合：find(x) 返回 x 所属集合的代表，union(a,b) 合并两个不同集合。</div>
<table class="compact-table"><thead><tr><th>同一组操作</th><th>分组编号实现</th><th>父指针实现</th></tr></thead><tbody><tr><td>find / 判断同组</td><td>读取编号</td><td>沿父指针找到根</td></tr><tr><td>union / 合并</td><td>全表改号</td><td>找到两根后连接根</td></tr></tbody></table>
<p>分组编号和父指针，是同一 ADT 的不同表示。回收 D004：先明确操作，再比较实现。</p>
<p>这里的分组由“当前已经接受的边”诱导，不是原输入图的全部连通关系。</p>
<p><strong>边界</strong>：DSU 不能单独保证 MST 的全局最优；还需按权扫描与教材 MST 性质。</p>''',
 '第三部分 · 合并连通分组']

_ROOT_MERGE = ['合并两组，能否只修改代表之间的连接？',
 '<div class="dsu-workspace"><p class="small">独立辅助例：先合并 AB、CD，再处理 union(B,C)。</p><div class="graph-pair">' +
 dsu_diagram(_DSU_DEMO['before_union']['parent'], _CHAIN_POS,
             caption='合并前：find(B)=A，find(C)=C；两组各有自己的根。',
             view_box=(35, 5, 440, 260)) +
 dsu_diagram(_DSU_DEMO['before']['parent'], _CHAIN_POS,
             caption='合并后：只令 p[C]=A；D 仍指向 C，find(D) 也能到 A。',
             root='A', view_box=(35, 5, 440, 260)) +
 r'''</div><p class="compact-text">连接的是两组的根，不能只把 B 随意接到 C。成员不必逐个改号；代价转为沿父指针找根。</p>
<p class="compact-text">任意连接可能形成长链。按大小合并，把小树的根接到大树的根下；相同大小时本例选 A。</p></div>''',
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

_COST = ['算法代价来自哪些读取、查询与更新？',
 r'''<p class="small">\(n=|V|\)，\(m=|E|\)；教材用 e 表示边数。先计已有表示上的算法阶段。</p>
<table class="compact-table"><thead><tr><th>实现</th><th>主要工作</th><th>时间</th></tr></thead><tbody>
<tr><td>矩阵 Prim</td><td>n 轮：线性选最小＋扫描一行</td><td>\(O(n^2)\)</td></tr>
<tr><td>Kruskal＋全表改号</td><td>排序；至多 n−1 次全表合并</td><td>\(O(n^2+m\log(m+1))\)</td></tr>
<tr><td>Kruskal＋优化父指针</td><td>排序；按大小合并＋路径压缩</td><td>\(O(n+m\log(m+1))\)</td></tr>
</tbody></table>
<p class="compact-text">查询与维护要一起计。父指针的高效性依赖实现及操作序列，不是每次 find 保证 O(1)。</p>
<p class="small">完整任务还要计输入准备和空间。当前 C 同时保存矩阵与边数组，矩阵占用 O(n²) 空间；不能由 Kruskal 的扫描代价推出整个程序只用线性空间。</p>''',
 '第四部分 · 验证与应用']

_COST_CHECK = ['换成邻接表，就一定能更快地选出下一项吗？',
 answer_workspace(
 r'''<div><h3>同一份输入，改变邻居访问方式</h3><table class="compact-table"><thead><tr><th>工作</th><th>矩阵</th><th>邻接表</th></tr></thead><tbody><tr><td>枚举 u 的邻居</td><td>扫描一行</td><td>只访问邻接项</td></tr><tr><td>找最小候选</td><td>扫描候选数组</td><td>仍扫描候选数组</td></tr></tbody></table><p class="small">题设保留线性选最小，没有加入其他优先级结构。</p></div>''',
 r'''<p><strong>独立判断（1 分钟）</strong></p><p>某实现只把矩阵换成邻接表，每轮仍扫描所有候选找最小值。</p><p>它是否自然变成 \(O(m\log n)\)？指出减少的工作和仍然存在的工作。</p>''',
 r'''<p>没有。全部邻居更新可按邻接项进行，总量 \(O(n+m)\)；但 n 轮线性选最小，仍有 \(O(n^2)\) 工作。</p><p>合计 \(O(n^2+m)\)，在简单图中仍为平方量级。后续优先队列要解决的是高效取最小与更新候选。</p>'''),
 '第四部分 · 验证与应用']

_C_STATE = ['教材字段与课堂程序，怎样一一对应？',
 r'''<table class="implementation-map"><thead><tr><th>教材</th><th>课堂 C 程序</th><th>必须区分</th></tr></thead><tbody>
<tr><td>lowcost / adjvex</td><td>key / parent</td><td>入口边权与来源，不是路径距离</td></tr>
<tr><td>lowcost=0 表示已纳入</td><td>used[v]</td><td>零权边与已纳入标志分开</td></tr>
<tr><td>无边的存储约定</td><td>present / weight</td><td>权值 0 不能代替“无边”</td></tr>
<tr><td>Vexset[v] 分组编号</td><td>find(v) 返回代表</td><td>不同 parent 仍可能同组</td></tr>
</tbody></table>
<p class="compact-text">has_key 区分有无入口；结果森林另存。Prim 的 parent 是入口来源，DSU 的 parent 是集合父指针。</p>
<p class="small">课后对照阅读：find / unite → kruskal → prim。当前 Graph 同时保存矩阵和边数组，尚未实现邻接链表；两算法不与两种存储一一绑定。</p>''',
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
        r'''<p class="small"><strong>过程</strong>：接受 PR1、QR2；PQ3 同组拒绝，此时 MST 未完成；接受 QS4 后 MST 已完成，总权 7。继续核对 RS5：同组拒绝。</p><p class="small"><strong>分组/依据</strong>：{P,R}→{P,Q,R}→{P,Q,R,S}；接受 QS 时 \(U=\{P,Q,R\}\)，\(V-U=\{S\}\)，连接两组的边有 QS4、RS5，QS 最轻。</p><p class="small">若采用提前终止，RS 是未处理，不是已拒绝。</p>''', '核对答案与理由（7+2 分钟）', class_name='independent-network'),
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

_SPARSE_LINK = ['按实际需要的项访问，怎样联系数值计算？',
 '<div class="answer-workspace course-link"><div class="answer-prompt">' +
 r'''<p class="compact-text">独立数值例：矩阵的 B 行为下表。计算这一行与向量的内积，需要哪些信息？</p>
<table><thead><tr><th>列</th><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr></thead><tbody><tr><th>系数</th><td>2</td><td>0</td><td>−1</td><td>0</td><td>3</td></tr></tbody></table>
<p>按行只保存有贡献的项：(A,2)、(C,−1)、(E,3)。</p>
<p>\(y_B=2x_A-x_C+3x_E\)。邻接表也按顶点组织要访问的记录。</p>
<p class="compact-text"><strong>共同机制：</strong>用结构减少无关位置的存储和扫描。<strong>语义差异：</strong>零系数可省略而不改变线性算子；图的零权边仍须保留连接关系。</p></div>''' +
 answer(beside(graph(TRIANGLE_NODES, [('A', 'B'), ('B', 'C'), ('A', 'C')],
                     view_box=(40, 10, 330, 250),
                     caption='独立三角形：边的参考方向仅用于构造列向量。'),
 r'''<p>若已学线性相关，取顶点对应的标准基向量，定义 \(b_{AB}=e_B-e_A\)、\(b_{BC}=e_C-e_B\)、\(b_{AC}=e_C-e_A\)。</p>
<p>\(b_{AB}+b_{BC}=b_{AC}\)。闭环的三条边对应线性相关的列；无环边集对应这些关联矩阵列的线性无关。</p>
<p class="small">这里是顶点—边关联矩阵，区别于邻接矩阵。参考方向不改变无向图。可对照<a href="https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/resources/lecture-12-graphs-networks-incidence-matrices/">MIT 线性代数专题</a>阅读。</p>'''),
 '课后探索：环与线性相关（先修：线性相关）') + '</div>',
 '第四部分 · 验证与应用']

_MODEL_LIMIT = ['若一条线路故障后仍须连通，目标要怎样改变？',
 answer_workspace(
 graph(MAIN_NODES, [('A', 'B'), ('B', 'C'), ('C', 'D'), ('C', 'E')],
       labels={e[:2]: e[2] for e in MAIN_EDGES}, label_positions=MAIN_LABEL_POS,
       marked=(('A', 'B'), ('B', 'C'), ('C', 'D')), rejected=(('C', 'E'),),
       caption='原 MST 的 CE 线路故障（灰虚线）；只剩红色 AB、BC、CD，E 断开。', legend=''),
 r'''<p>最低建设成本的树没有冗余连接。现在新增要求：任意一条线路故障后，所有站点仍须互通。</p><p>仅把原 MST 算得更快，能满足新要求吗？需要重新考虑哪些约束？</p>''',
 r'''<p>不能。树上任意一条边删除都会断开。抗故障要求需要冗余线路，必须重新定义可行方案与成本目标。</p>
<p><strong>先判断目标和条件，再选择方法。</strong>数学最优依赖给定模型，不能直接代替真实用途判断。</p>
<p class="small">课后选做（不新增正式提交）：先记录自己的预测，再让程序或 AI 给出候选网络，核对输入、连通、总权与最优依据；增加故障要求后重新判断。</p>''', '核对模型边界与实践方法'),
 '第四部分 · 验证与应用']

_SUMMARY = ['把选择、约束和维护机制放在一起',
 r'''<table><thead><tr><th>对象/方法</th><th>利用什么</th><th>支持什么判断</th></tr></thead><tbody><tr><td>图的表示</td><td>输入关系与访问机制</td><td>怎样获得邻居或全部边</td></tr><tr><td>Prim</td><td>保存最佳入口，比较新邻边</td><td>怎样安全扩大已接入区域</td></tr><tr><td>Kruskal</td><td>按权组织边，维护当前分组</td><td>何时接受或拒绝候选边</td></tr><tr><td>并查集</td><td>分组编号或父指针</td><td>怎样查询并维护同组关系</td></tr></tbody></table><p>表示服务于操作；保存有用信息减少重复工作。能连接、不会成环、成本最优与用途适合，仍须分别检查。</p>''',
 '第四部分 · 验证与应用']

_HOMEWORK = ['课后：教材导航与正式作业',
 r'''<p><strong>教材导航</strong>：精读 6.6.1；对照阅读本讲并查集代码。</p><p><strong>A. 书本习题</strong>：第 6 章选择题 <strong>(7)</strong>、应用题 <strong>(2)③</strong>。写选择理由、选边过程和总权。</p><p><strong>B. 程序实践</strong>：把主例 DE 权值由 7 改为 0，先预测两算法的选边和总权，运行 homework 输出核对；写出 Kruskal 每次合并后的分组。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B 与 3–5 行过程记录。<br>应用题 (2)①②可画作解题草稿，本次正式提交范围为③。</p>''',
 '第四部分 · 验证与应用']

_NEXT = ['下一讲：从一个起点出发，距离如何更新？',
 r'''<p>Prim 的 key[v] 是接入当前区域的一条边。<br>若任务变成“从 A 到 v 的最少总代价”，状态应保存什么？</p><p class="lead">D014：最短路径。</p><p class="small">另一个留下的问题：候选很多时，怎样高效取最小并更新优先级？后续优先队列继续回答。</p>''',
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
    _ENTRY_MOTIVE,
    _INPUT_UPDATE,
    _AUX,
    _PRIM_PLAYER,
    _FROM_C,
    _MSF,
    _PART3,
    _EDGE_PREP,
    _KRUSKAL,
    _KRUSKAL_PLAYER,
    _CONNECTIVITY,
    _GROUP_IDS,
    _DSU,
    _ROOT_MERGE,
    _THREE_OBJECTS,
    _COMPRESS,
    _DSU_CHECK,
    _FEASIBLE,
    _TIES,
    _COST,
    _COST_CHECK,
    _C_STATE,
    _VERIFY,
    _EXERCISE,
    _SHORTEST,
    _SPARSE_LINK,
    _MODEL_LIMIT,
    _SUMMARY,
    _HOMEWORK,
    _NEXT,
]
