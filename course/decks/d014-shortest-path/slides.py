"""D014: a learning path from feasible routes to justified shortest distances."""
from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from graph_diagram import graph
from components import CourseDeck, Section, task_workspace
from shortest_path_trace import (
    MAIN_NODES, MAIN_EDGES, EXERCISE_NODES, EXERCISE_EDGES,
    graph_view, dijkstra_states, dijkstra_player, state_table, floyd_stages, fmt,
)

DECK_ID = 'D014'
TITLE = '最短路径：距离怎样更新，何时确定？'
MATH = True
COURSE = CourseDeck([
    Section('task', '我们要求哪一种最短？',
            '少走边、少花建设成本、少花通行时间，目标相同吗？',
            '先明确任务，再判断已有方法能够保证什么。', '从已有图算法进入优化目标辨析'),
    Section('distance', '距离的改进与确认',
            '一次更新为什么有用？一次确认为什么可靠？',
            '先比较具体路径，再建立选择规则及其成立依据。', '辨认改进与确认两项任务'),
    Section('execution', '执行、代价与检查',
            '输入怎样进入程序，代价从哪里来，怎样判断结果？',
            '从存储记录到独立作答，再用运行与依据检查。', '转向实现、代价与独立检验'),
    Section('all-pairs', '任意两点之间的距离',
            '每一对顶点都要查询，怎样组织计算？',
            '用允许的中间顶点集合解释阶段更新及方法选择。', '由查询范围变化引出全源计算'),
])
P1, P2, P3, P4 = [COURSE.label(section.id) for section in COURSE.sections]


def add(page_id, title, body, part, goal, activity='讲述、观察与追问', *, role='content'):
    section = next((s.id for s in COURSE.sections if COURSE.label(s.id) == part), None)
    COURSE.add(page_id, title, '<div class="shortest-lesson">' + body + '</div>',
               section=section, role=role, label=part, goal=goal, activity=activity)


def pair(left, right, cls=''):
    return '<div class="sp-two ' + cls + '">' + left + '<div>' + right + '</div></div>'


def solution(html, title='核对答案与理由'):
    return '<details><summary>' + title + '</summary>' + html + '</details>'


def workspace(diagram, question, answer, title='核对答案与理由', *, layout='columns'):
    return task_workspace(diagram, question, answer, title=title, layout=layout)


def main(**kwargs):
    return graph_view(**kwargs)


def exercise(**kwargs):
    return graph_view(EXERCISE_NODES, EXERCISE_EDGES, directed=True,
                      caption='独立练习有向图；弧上的数字为权值。', **kwargs)


def matrix(distance, labels=MAIN_NODES):
    labels = tuple(labels)
    rows = ['<tr><th></th>' + ''.join('<th>' + x + '</th>' for x in labels) + '</tr>']
    for label, row in zip(labels, distance):
        rows.append('<tr><th>' + label + '</th>' +
                    ''.join('<td>' + fmt(x) + '</td>' for x in row) + '</tr>')
    return '<table class="sp-matrix">' + ''.join(rows) + '</table>'


TRACE = dijkstra_states()
AFTER_A = next(s for s in TRACE if s['phase'] == 'round-end' and s['current'] == 'A')
AFTER_C = next(s for s in TRACE if s['phase'] == 'round-end' and s['current'] == 'C')
AFTER_B = next(s for s in TRACE if s['phase'] == 'round-end' and s['current'] == 'B')
FLOYD = floyd_stages()


def distance_value(state, vertex):
    """Render classroom vertex indexing from the actual algorithm snapshot."""
    value = state['distance'][vertex]
    tex = r'\infty' if value is None else str(value)
    return ('<span data-distance-vertex="' + escape(vertex, quote=True) +
            '" data-distance-value="' + fmt(value) + '">' +
            r'\(\mathrm{dist}[' + escape(vertex) + ']=' + tex + r'\)</span>')

# 1–7: task meaning and the status of route information.
add('cover', TITLE,
    pair(main(marked=(('A', 'B'), ('B', 'D'), ('D', 'E'))),
         '<p class="lead">找到一条路线以后，<br>怎样知道还有没有更短的？</p>'
         '<p>固定起点 A，比较从 A 出发的累计通行时间。</p>'
         '<p class="small">数据结构与算法 · 教材 6.6.2<br>本讲采用固定、可相加的边权模型。</p>', 'sp-cover'),
    '最短路径', '定位源点、路径代价与距离确认问题', role='cover')

COURSE.outline(title='本讲要解决哪些问题？')

COURSE.start_section('task')

add('bfs-cost', '少走几条边，就一定更快吗？',
    workspace(main(marked=(('A', 'B'), ('B', 'E'))),
              '<p>从 A 到 E：</p><p><strong>路线一：</strong>A→B→E，两条边。</p>'
              '<p><strong>路线二：</strong>A→B→D→E，三条边。</p>'
              '<p>分别计算通行时间，再判断广度优先搜索（BFS）保证哪一种“最短”。</p>',
              '<p>A→B→E：3+7=<strong>10</strong>。</p>'
              '<p>A→B→D→E：3+1+3=<strong>7</strong>。</p>'
              '<p>BFS 保证最少边数。每边代价相同且非负时，它也能保证最小累计代价。</p>'),
    P1, '区分最少边数与最小路径权', '短预测与反馈')

add('mst-cost', '连接总成本最低，出行路线就最短吗？',
    pair(main(marked=(('A', 'C'), ('B', 'C'), ('B', 'D'), ('D', 'E')),
              caption='红粗边是一棵 MST：AC、CB、BD、DE，总边权为 8。'),
         r'''<p>这棵 MST 上，A 到 B 的路径：</p>
<p>\(A\to C\to B\)，路径权为 \(2+2=4\)。</p>
<p>原图中直接走 AB，路径权为 \(3\)。</p>
<table class="sp-table"><tbody><tr><th>MST</th><td>最小化全部选中边的总权</td></tr>
<tr><th>最短路径</th><td>最小化源点到目标的路径权</td></tr></tbody></table>'''),
    P1, '解释最小生成树与最短路径的优化目标差异')

add('single-source', '从一个起点出发，我们究竟要求什么？',
    r'''<div class="sp-definition"><strong>教材定义（概述）</strong><br>
给定带权图及源点，求源点到其他各顶点的最短路径。带权路径的长度用沿途边权之和度量。</div>
<div class="sp-two sp-text-pair"><div><p>输入：\(G=(V,E,w)\)，源点 \(s\)。</p>
<p>路径 \(P\) 的代价：\(\ell(P)=\sum_{e\in P}w(e)\)。</p>
<p>最短距离：\(\delta(s,v)=\min_{P:s\leadsto v}\ell(P)\)。</p></div>
<div><p>输出：每个顶点的最短距离，及一条对应路径。</p>
<p>源点到自身：距离 \(0\)。</p><p>没有到达路径：距离记为 \(\infty\)。</p></div></div>
<p class="sp-small">本讲重点：有限图、固定非负边权。无向边可按两个方向读取；有向边按箭头读取。</p>''',
    P1, '明确单源最短路径的输入、输出与约定')

add('tentative', '找到一条路线后，哪些事情还没有确定？',
    workspace(main(marked=(('A', 'C'), ('C', 'D'))),
              '<p>已经找到 A→C→D，长度为 <strong>7</strong>。</p>'
              '<p>这条记录说明：</p><ul><li>A 能够到达 D。</li>'
              '<li>到 D 的最短距离至多为 7。</li></ul><p>能够直接断定最短距离就是 7 吗？</p>',
              '<p>当前只确认了这条路线存在。</p>'
              '<p>还需要比较其他可能的路线；到 D 的距离仍然可以改进。</p>'),
    P1, '把有限暂定距离理解为有路径支持的上界', '解释已有信息与未决信息')

# 8–20: local route comparisons, then a justified complete algorithm.
COURSE.start_section('distance')

add('improve', '找到更好的路线，怎样修改已有记录？',
    workspace(main(marked=(('A', 'B'), ('B', 'D'))),
              '<p>原记录：A→C→D，长度 7，D 的前驱为 C。</p>'
              '<p>新路线：A→B→D，长度 3+1。</p>'
              '<p>距离和前驱分别要怎样修改？</p>'
              '<p class="sp-small">这里先作局部路径比较，完整执行顺序稍后建立。</p>',
              '<p>到 D 的距离：<strong>7 → 4</strong>。</p>'
              '<p>D 的前驱：<strong>C → B</strong>。</p>'
              '<p>保留更短路线的长度，同时保存它的最后一步来源。</p>'),
    P2, '理解距离和前驱必须随路径改进同步变化', '局部预测与反馈')

add('relax', '一条输入记录怎样产生新的候选？',
    pair(main(marked=(('B', 'D'),)),
         r'''<table class="sp-table"><tbody>
<tr><th>已有路径信息</th><td>到 B 的路线长 \(\mathrm{dist}[u]=3\)</td></tr>
<tr><th>读取的图记录</th><td>边 BD 存在，权为 \(w(u,v)=1\)</td></tr>
<tr><th>新候选路径</th><td>经 B 到 D，长度 \(3+1=4\)</td></tr>
<tr><th>与旧值比较</th><td>旧记录 \(\mathrm{dist}[v]=7\)；\(4&lt;7\)，接受候选</td></tr></tbody></table>
<p><strong>松弛（Relaxation）</strong>：用一条新候选路径尝试改进距离。</p>
<p class="sp-small">u 是本次延伸的出发顶点，v 是待改进顶点；本例 \(u=B,v=D\)。dist[v] 保存当前找到的最好距离。</p>
<p class="sp-formula">\(\mathrm{dist}[v]\gets\min\{\mathrm{dist}[v],\mathrm{dist}[u]+w(u,v)\}\)</p>
<p class="sp-small">u 是新候选路径的前驱；仅在接受更短候选后，才写入 parent[v]=u。</p>'''),
    P2, '把输入边、已有距离与松弛公式逐项对应')

add('state-fields', '图、距离、前驱和确认状态各保存什么？',
    pair(main(),
         r'''<p class="sp-small">顶点编号：A=0，B=1，C=2，D=3，E=4。</p>
<table class="sp-table"><tbody>
<tr><th>原图</th><td>边的存在性、方向与权值</td></tr>
<tr><th>dist[v]</th><td>当前找到的最好路径的长度</td></tr>
<tr><th>parent[v]</th><td>该路径上 v 的直接前驱</td></tr>
<tr><th>settled[v]</th><td>最短距离是否已经确认</td></tr></tbody></table>
<p class="sp-small">dist[v] 是当前记录，真正最短距离记为 \(\delta(s,v)\)；确认后两者相等。
dist[D] 是课堂按顶点名索引的记法；C 中 D 编号为 3，对应 dist[3]。</p>'''),
    P2, '区分输入图、暂定路径信息与确认状态')

add('choose', '从 A 出发，下一步怎样选择？',
    workspace(main(states={'A': 'visited'}),
              '<p>A 到自身的距离为 0。读取 A 的邻居后：</p>' +
              state_table(AFTER_A) +
              '<p>B 与 C 都已找到路线，下一步先处理谁？为什么仍需要解释“可以确认”？</p>',
              '<p>未确认顶点中，C 的暂定距离 <strong>2</strong> 最小。</p>'
              '<p>暂定最小只是选择规则；需要证明其他绕行路线不会更短。</p>'
              '<p>源点距离 0 提供起点，下面解释怎样从已确认信息继续推进。</p>'),
    P2, '从合法初始状态提出最小候选选择与确认问题', '短预测与解释')

_REGION = {'points': ((18, 25), (247, 25), (247, 280), (18, 280)),
           'label': '已确认集合 S', 'label_position': (132, 27)}
add('first-exit', '一条更短的路线，必须先经过哪里？',
    pair(main(marked=(('A', 'B'), ('B', 'E'), ('D', 'E')),
              states={'A': 'visited', 'B': 'visited', 'C': 'visited'},
              details={'A':'s','B':'x ∈ S','E':'y ∉ S','D':'u ∉ S'},
              regions=(_REGION,),
              caption='图中 s=A、u=D；示意路线的首次出界边为 B→E，即 x=B、y=E。'),
         r'''<p>在一般的一轮选择前，设集合 \(S\) 中的距离已正确确认，且邻居已完成更新。</p>
<p>沿任意一条从源点到外部顶点的路线，找：</p>
<p><strong>第一个未确认顶点 \(y\)</strong>，及它之前的顶点 \(x\in S\)。</p>
<p>处理 \(x\) 时，边 \(x\to y\) 已经参与更新。</p>
<p class="sp-small">x、y 由所讨论的路线决定；首次出界就到终点时，也可以 y=u。</p>'''),
    P2, '定位确认论证中的首次出界顶点及已发生的更新')

add('confirmation-proof', '为什么边权非负，就能够确认当前最小者？',
    r'''<div class="sp-proof"><p>选最小有限候选 \(u\)（图中 D）。假设从 \(s\) 到 \(u\) 的路径 \(P\) 满足 \(\ell(P)&lt;\mathrm{dist}[u]\)。</p>''' +
    pair(main(marked=(('A', 'B'), ('B', 'E'), ('D', 'E')),
              states={'A': 'visited', 'B': 'visited', 'C': 'visited'}, regions=(_REGION,),
              details={'A':'s','B':'x ∈ S','E':'y ∉ S','D':'u ∉ S'},
              caption='S={A,B,C}，dist[D]=' + fmt(AFTER_B['distance']['D']) + '。红路线长 13，只示意出界；不是假设中更短的路径 P。'),
         r'''<table class="sp-table"><tbody>
<tr><th>已更新</th><td>\(\mathrm{dist}[y]\leq\ell(P_{s\leadsto y})\)<br><span class="sp-small">dist[x] 已正确，且处理过边 x→y。</span></td></tr>
<tr><th>非负权</th><td>\(\ell(P_{s\leadsto y})\leq\ell(P)\)<br><span class="sp-small">后续边权非负。</span></td></tr>
<tr><th>矛盾</th><td>\(\mathrm{dist}[y]&lt;\mathrm{dist}[u]\)<br><span class="sp-small">选择规则却给出 dist[u]≤dist[y]。</span></td></tr>
</tbody></table>''') +
    '<p><strong>因此可以确认 u。</strong> 哪一步用到了非负权？权为 0 时仍成立吗？</p></div>',
    P2, '说明确认理由，并指出非负权进入论证的位置', '图示论证与学生复述')

_NEG_NODES = {'s': (60, 145), 'p': (440, 65), 'q': (440, 230)}
_NEG = graph(_NEG_NODES, [('s', 'p'), ('s', 'q'), ('q', 'p')], directed=True,
             labels={('s', 'p'): 2, ('s', 'q'): 5, ('q', 'p'): -4},
             label_positions={('s', 'p'): (250, 89), ('s', 'q'): (250, 211), ('q', 'p'): (412, 151)},
             caption='独立有向反例：没有环；q→p 的权为 −4。', view_box=(0, 20, 520, 260))
add('negative', '出现负权边后，哪里会失效？',
    workspace(_NEG,
              r'<p>从 s 出发，先得到 \(\mathrm{dist}[p]=2\)、\(\mathrm{dist}[q]=5\)。</p>'
              r'<p>若先把 \(\mathrm{dist}[p]=2\) 当成最短距离确认，会遗漏什么？</p>'
              '<p>请指出上一页论证中失去保证的那一步。</p>',
              '<p>s→q→p 的长度为 <strong>5−4=1</strong>。</p>'
              '<p>到 q 的前缀长 5，整条路径反而只长 1。</p>'
              '<p>延长路径可能降低代价，原来的确认依据失去保证。</p>'),
    P2, '用无负环的小反例识别 Dijkstra 的条件边界', '反例预测')

add('algorithm', '怎样把这些判断组织成完整算法？',
    r'''<div class="sp-code-pair"><pre><code>dist[s] = 0，其余为 ∞；parent 为空
所有顶点初始未确认
重复：
    选取暂定距离最小的未确认顶点 u
    若不存在有限候选，停止
    确认 u
    对 u 的每个未确认邻居 v：
        若经 u 的路径严格更短：
            更新 dist[v] 和 parent[v]</code></pre>
<div><p><strong>迪杰斯特拉算法（Dijkstra）</strong></p>
<p>选择规则由当前距离给出。</p><p>确认理由依赖非负权。</p>
<p>邻居更新为下一轮积累信息。</p>
<p class="sp-small">源点距离 0 是起点。教材把确认源点及其初次邻居更新并入初始化，后续过程相同。</p></div></div>''',
    P2, '把局部操作、确认依据与完整控制流程连接起来')

add('trace', '从初始化开始，每一轮发生什么？',
    dijkstra_player(),
    P2, '区分选取、确认、读取、比较、修改与一轮完成', '按关键状态停顿的完整推演')

add('early-stop', '已经找到到 E 的路线，能够提前结束吗？',
    workspace(main(marked=(('A', 'B'), ('B', 'E')),
                   states={'A': 'visited', 'B': 'visited', 'C': 'visited'}),
              '<p>刚完成 B 的更新：' + distance_value(AFTER_B,'D') + '，' + distance_value(AFTER_B,'E') + '；均未确认。</p>'
              '<p>只查询 A 到 E，能否现在返回 10？</p>'
              '<p>下一步处理 D 后，E 会怎样变化？</p>',
              r'<p>经 D 的新候选为 4+3=7，更新 \(\mathrm{dist}[E]\gets7\)，parent[E]=D。</p>'
              '<p>单目标查询可以在<strong>目标距离被确认时</strong>停止。</p>'
              '<p>首次找到到目标的路线，还可能继续改进。</p>'),
    P2, '区分首次发现与单目标查询的安全停止时机', '局部预测')

add('recover', '距离已经得到，路线怎样找回来？',
    workspace(main(marked=(('A', 'B'), ('B', 'D'), ('D', 'E'))),
              '<p>最终前驱：parent[E]=D，parent[D]=B，parent[B]=A。</p>'
              '<p>从 E 开始追溯，再把记录反向排列。</p>'
              '<p>若目标就是 A，或目标不可达，分别怎样处理？</p>',
              '<p>E←D←B←A，恢复为 <strong>A→B→D→E</strong>，权和 7。</p>'
              '<p>A 到自身：路径 [A]、距离 0，即使 A 没有前驱。</p>'
              '<p>先检查距离是否有限；不可达时不沿前驱恢复。</p>'),
    P2, '恢复一条路径并区分源点无前驱与不可达')

_DISCONNECTED = tuple(e for e in MAIN_EDGES if e[:2] not in (('B', 'E'), ('D', 'E')))
add('unreachable', '没有有限候选时，剩余顶点怎么办？',
    pair(graph_view(edges=_DISCONNECTED,
                    states={'A': 'visited', 'B': 'visited', 'C': 'visited', 'D': 'visited', 'E': 'unvisited'},
                    caption='删除 BE、DE 后，E 成为孤立顶点。'),
         r'''<p>A、C、B、D 依次确认，E 的距离始终为 \(\infty\)。</p>
<p><strong>没有有限的未确认候选，计算停止。</strong></p>
<p>此时可以判断 E 从 A 不可达。</p>
<p class="sp-small">过程中的 ∞ 表示尚未找到路径。正确停止后，剩余 ∞ 才表示不可达；E 不加入已确认集合。</p>'''),
    P2, '解释不可达的判断依据及停止状态')

# 21–27: implementation, work, and independent evidence.
COURSE.start_section('execution')

_B_INPUT = r'''<p><strong>输入矩阵 B 行</strong>（列 A–E）</p>
<table class="sp-table sp-input-row"><tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr>
<tr><td>3</td><td>—</td><td>2</td><td>1</td><td>7</td></tr></table>
<p><strong>B 的邻接项：</strong>A:3，C:2，D:1，E:7。</p>
<p class="sp-small">— 表示无边；零权边仍需保留。主例没有自环。</p>'''
add('input-row', '确认 B 后，怎样从存储记录更新距离？',
    workspace('<div class="sp-storage-input">' + pair(main(states={'A': 'visited', 'B': 'current', 'C': 'visited'}),
              '<div data-required-context="B 行输入">' + _B_INPUT + '</div>' +
              '<p class="sp-small" data-required-context="更新前状态">更新前：' + distance_value(AFTER_C,'B') + '，' +
              distance_value(AFTER_C,'D') + '，' + distance_value(AFTER_C,'E') + '。A、B、C 已确认。</p>') + '</div>',
              '<p>补出 D、E 的新距离及前驱，并比较两种表示的枚举工作。</p>',
              '<p>' + distance_value(AFTER_B,'D') + r'：\(\min(7,3+1)=4\)，parent[D]=B。</p>'
              '<p>' + distance_value(AFTER_B,'E') + r'：\(\min(\infty,3+7)=10\)，parent[E]=B。</p>'
              '<p>矩阵检查 5 个位置；邻接表枚举 4 项。A、C 已确认，跳过更新。</p>',layout='stacked'),
    P3, '从真实输入记录独立解释一次更新及枚举代价', '独立补全与反馈')

add('cost', '算法的工作量主要花在哪里？',
    r'''<p class="sp-small">\(n=|V|\)，\(m=|E|\)；本讲采用线性扫描选最小候选。</p>
<table class="sp-table"><thead><tr><th>工作或存储</th><th>邻接矩阵</th><th>邻接表</th></tr></thead><tbody>
<tr><th>各轮选最小</th><td>\(O(n^2)\)</td><td>\(O(n^2)\)</td></tr>
<tr><th>各轮枚举输入</th><td>\(O(n^2)\)</td><td>\(O(n+m)\)</td></tr>
<tr><th>输入图空间</th><td>\(O(n^2)\)</td><td>\(O(n+m)\)</td></tr>
<tr><th>辅助数组空间</th><td>\(O(n)\)</td><td>\(O(n)\)</td></tr></tbody></table>
<p>邻接表减少部分扫描，线性选最小仍需平方量级的最坏工作。</p>
<p class="sp-small">单目标提前停止可以减少实际工作，最坏仍可能处理全部可达顶点。高效取最小留给后续优先队列。</p>''',
    P3, '从实际访问与选择推导代价，区分输入与辅助空间')

add('c-code', '怎样把选取、更新和停止写进程序？',
    workspace(r'''<pre data-required-context="待对照代码"><code>if (u == -1) break;          // 没有有限候选
settled[u] = true;
for (int v = 0; v &lt; n; ++v) {
    if (!present[u][v] || settled[v]) continue;
    long long candidate = dist[u] + w[u][v];
    if (candidate &lt; dist[v]) {
        dist[v] = candidate; parent[v] = u;
    }
}</code></pre><p class="sp-small">u、v 是整数编号；顶点 D 对应 dist[3]。present 区分无边与零权边；程序先校验非负权和整数范围。</p>''',
              '<p>对照教材：距离、前驱和确认信息，分别由哪个字段保存？</p>',
              r'''<table class="sp-table"><thead><tr><th>教材字段</th><th>课堂字段</th><th>含义</th></tr></thead><tbody>
<tr><td>D[v]</td><td>dist[v]</td><td>当前找到的最好路径长度</td></tr>
<tr><td>Path[v]</td><td>parent[v]</td><td>直接前驱</td></tr>
<tr><td>S[v]</td><td>settled[v]</td><td>是否已确认</td></tr></tbody></table>
<p>\(v\in S\iff\mathrm{settled}[v]=\mathrm{true}\)。教材数组 D 与顶点名 D 各有其含义。</p>
<p class="sp-small"><a href="code/shortest_path_demo.c">完整 C11 演示源码</a>：主例、零权、不可达、有向练习及负权拒绝。</p>''',
              title='展开教材字段与课堂字段对照',layout='stacked'),
    P3, '解释关键 C 条件及字段映射，保护零权和停止语义')

add('independent', '换一张有向图，你能独立完成吗？',
    workspace(exercise(),
              '<p><strong>独立作答 7 分钟，随后反馈 3 分钟。</strong></p>'
              '<ol><li>以 P 为源点。处理 R 后，写 Q、S 的距离和前驱。</li>'
              '<li>继续计算，恢复 P 到 S 的路径；用一句话解释为何可确认 Q。</li>'
              '<li>从 S 出发能否到达 P？依据箭头说明。</li></ol>'
              '<p class="sp-small">保留预测过程，再展开答案。编号 P=0，Q=1，R=2，S=3。</p>',
              r'<p>处理 R 后：\(\mathrm{dist}[Q]=3\)，parent[Q]=R；\(\mathrm{dist}[S]=7\)，parent[S]=R。</p>'
              r'<p>随后确认 Q 的距离 3，经零权 Q→S 更新 \(\mathrm{dist}[S]=3\)、parent[S]=Q；确认距离可以相等。</p>'
              '<p>最终 P→R→Q→S，权和 <strong>3</strong>。</p>'
              '<p>Q 为当前最小未确认候选，且边权非负。S 没有出边，所以不能到达 P。</p>'),
    P3, '检验有向读取、零权、确认、路径恢复与反向不可达', '7 分钟独立作答＋3 分钟反馈', role='exercise')

add('predict-run', '预测与运行不一致时，先检查什么？',
    r'''<p>先保留独立题的纸面状态，再进入本讲目录，编译运行并逐项核对。</p>
<pre class="sp-command"><code>gcc -std=c11 -Wall -Wextra -Werror \
  code/shortest_path_demo.c -o /tmp/d014
/tmp/d014 --trace exercise
/tmp/d014 reverse</code></pre>
<table class="sp-table"><thead><tr><th>观察到的差异</th><th>优先检查</th></tr></thead><tbody>
<tr><td>到 Q 仍为 4</td><td>是否允许改进已找到的路线？</td></tr>
<tr><td>到 S 为 7</td><td>零权边是否保留？是否首次发现就停止？</td></tr>
<tr><td>认为 S 能到 P</td><td>是否把箭头当成双向关系？</td></tr></tbody></table>
<p class="sp-small">相同的错误结果可能有不同原因，需要查看状态与执行过程。</p>''',
    P3, '用输入、状态和过程诊断差异', '预测后运行与针对性反馈')

add('optimality', '路径合法、权和正确，已经说明什么？',
    workspace(exercise(marked=(('P', 'Q'), ('Q', 'S'))),
              '<p>路线 P→Q→S 合法，权和为 4+0=4。</p>'
              '<p>这两项检查是否足以认定最短？请给出进一步依据。</p>',
              '<p>另一条路线 P→R→Q→S 的权和为 1+2+0=<strong>3</strong>。</p>'
              '<p>合法性与权和检查支持“这条路径存在且代价为 4”。</p>'
              '<p>最优性还需要确认论证，或其他能够排除更短路线的依据。</p>'),
    P3, '区分路径可行性、数值核对与最优性依据', '反例判断')

# 28–36: all-pairs distances, a restricted intermediate set, and selection.
COURSE.start_section('all-pairs')

add('matrix', '从一个距离数组到一个距离矩阵，增加了什么？',
    pair(main(),
         '<p>可以分别以各顶点为源点，重复执行 Dijkstra。</p>'
         '<p>用距离矩阵 D[i,j] 保存各顶点对的信息。</p>' +
         matrix(FLOYD[0]['distance']) +
         '<p class="sp-small">初始化：对角线为 0；直接边用边权；其他位置为 ∞。零权边仍写 0。</p>'),
    P4, '理解顶点对状态与距离矩阵初始化')

add('stage', '“允许经过顶点 k”究竟是什么意思？',
    workspace(main(marked=(('A', 'B'), ('B', 'E')),
                   states={'A': 'visited', 'B': 'visited', 'C': 'visited'}),
              '<p><strong>允许的中间顶点：</strong>{A,B,C}。</p>'
              '<p>此时 D[A,E]=10。</p>'
              '<p>已知最终最短距离是 7，现在填 10 是否出错？为什么？</p>',
              '<p>A→B→E 长 10，中间顶点 B 已允许。</p>'
              '<p>长度 7 的 A→B→D→E 需要中间顶点 D，此阶段尚未允许。</p>'
              '<p>当前保存的是<strong>受允许集合限制的最优结果</strong>。</p>'),
    P4, '区分 Floyd 阶段最优与最终全局最优', '阶段语义判断')

add('floyd-update', '允许经过 D，A 到 E 怎样更新？',
    workspace(main(marked=(('A', 'B'), ('B', 'D'), ('D', 'E'))),
              r'''<p>原允许集合：{A,B,C}。</p>
<table class="sp-table"><tbody><tr><th>D[A,E]</th><td>10</td></tr>
<tr><th>D[A,D]</th><td>4</td></tr><tr><th>D[D,E]</th><td>3</td></tr></tbody></table>
<p>现在允许 D 作为中间顶点。请计算新值，并指出两段路径。</p>''',
              r'''<p>两段是 A→B→D 和 D→E。</p>
<p>\(D_{\rm 新}[A,E]=\min\{10,4+3\}=7\)。</p>
<p>允许集合扩大为 {A,B,C,D}。同一阶段要检查所有顶点对。</p>'''),
    P4, '将阶段条件、子路径与局部更新对应', '局部预测与反馈')

add('floyd-loops', '为什么先固定 k，再检查所有顶点对？',
    r'''<p><strong>弗洛伊德算法（Floyd）</strong>：逐步扩大允许的中间顶点集合。</p>
<pre><code>for k = 0, ..., n-1:           // 本阶段新增允许的中间点
    for i = 0, ..., n-1:
        for j = 0, ..., n-1:
            若两段路径都存在：
                D[i,j] = min(D[i,j], D[i,k] + D[k,j])</code></pre>
<p>k 是阶段变量；i、j 枚举该阶段的全部端点对。</p>
<p class="sp-formula">\(n\) 个阶段，每阶段 \(n^2\) 对：时间 \(O(n^3)\)，距离矩阵空间 \(O(n^2)\)。</p>
<p class="sp-small">本讲沿用非负权范围。完整矩阵推演及各对路径的恢复留作教材阅读。</p>''',
    P4, '从阶段含义解释循环组织及基本代价')

add('method-choice', '面对具体查询，怎样选择计算方式？',
    r'''<table class="sp-table"><thead><tr><th>任务与条件</th><th>可考虑的方法</th><th>需要判断什么</th></tr></thead><tbody>
<tr><td>无权图，求最少边数</td><td>BFS</td><td>FIFO 层次是否对应目标代价？</td></tr>
<tr><td>非负权，固定一个源点</td><td>Dijkstra</td><td>距离确认条件与选最小的实现</td></tr>
<tr><td>非负权，需大量顶点对结果</td><td>Floyd 或重复单源计算</td><td>图规模、查询范围、表示与存储</td></tr>
</tbody></table>
<p>采用本讲的朴素实现，重复 n 次 Dijkstra 与 Floyd 的最坏时间都为 \(O(n^3)\)。</p>
<p class="sp-small">真实导航若加入时变耗时、订单分配或时间窗，应先重新判断模型和任务。</p>''',
    P4, '依据查询、条件与计算约束选择方法')

add('recall', '路径信息怎样支撑计算与判断？',
    r'''<table class="sp-table"><thead><tr><th>需要回答的问题</th><th>本讲建立的联系</th></tr></thead><tbody>
<tr><th>现在知道什么？</th><td>实际找到的路径，支持暂定距离</td></tr>
<tr><th>新信息怎样利用？</th><td>读取边、拼接路径、比较并更新</td></tr>
<tr><th>什么时候可以确定？</th><td>最小候选与非负权共同支持确认</td></tr>
<tr><th>结果怎样解释？</th><td>前驱恢复路径，检查合法性、权和及最优依据</td></tr></tbody></table>
<p>请从主例任选一次更新，用这四个问题把它解释完整。</p>''',
    P4, '用一次具体操作回收信息、机制、条件与检查', '口头解释与收束')

add('homework', '课后怎样练习和核对？',
    r'''<p><strong>A　教材练习</strong></p>
<p>阅读 6.6.2；完成第 6 章应用题（4）：按图 6.37，从 a 出发填写表 6.10，保留距离、前驱或路径及确认集合。</p>
<p><strong>B　程序实践</strong></p>
<p>主例只将 CD 从 5 改为 0。先预测到 D、E 的距离与路径，再运行 <code>/tmp/d014 homework</code>，写出一处更新和一处确认的依据。</p>
<p class="sp-small">题图以教材为准。提交 A、B 与 3–5 行过程记录，遵循
<a href="../../assignments/homework-guide.md">课程作业说明</a>。</p>''',
    '课后衔接', '明确教材导航与先预测后核对的课后实践', role='closing')

_NEXT = graph({'A': (70, 70), 'B': (70, 225), 'C': (285, 145), 'D': (470, 145)},
              [('A', 'C'), ('B', 'C'), ('C', 'D')], directed=True,
              caption='依赖关系示例：A、B 完成后才能做 C，C 完成后才能做 D。',
              view_box=(0, 15, 520, 285))
add('next', '有向关系还可以约束什么？',
    pair(_NEXT, '<p>道路箭头表示允许通行的方向。</p>'
         '<p>任务箭头也可以表示“必须先完成”的依赖。</p>'
         '<p class="lead">哪些执行顺序合法？<br>若出现有向环，会怎样？</p>'
         '<p class="sp-small">下一讲 D015：拓扑排序与关键路径。</p>'),
    '下一讲', '从道路关系转向依赖关系与调度问题', role='closing')

# Derived navigation and design-card rows share the page registration above.
SLIDES = COURSE.finalize()
PAGE_PLAN = COURSE.page_plan()
