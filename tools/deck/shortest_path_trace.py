"""Nonnegative-integer shortest-path states and HTML views for classroom graphs.

Computation is separate from rendering. None denotes an unknown/unreachable label;
zero is a valid weight. Selection, confirmation and edge relaxation are distinct
snapshots. The invariant about scanning all settled vertices applies at the start
of selection, not halfway through a round.
"""
from html import escape
from numbers import Integral

from graph_diagram import graph
from tree_trace import player


MAIN_NODES = {'A': (50, 145), 'B': (205, 65), 'C': (205, 230),
              'D': (380, 230), 'E': (465, 65)}
MAIN_EDGES = (('A', 'B', 3), ('A', 'C', 2), ('B', 'C', 2),
              ('B', 'D', 1), ('C', 'D', 5), ('B', 'E', 7), ('D', 'E', 3))
MAIN_LABEL_POS = {('A', 'B'): (116, 87), ('A', 'C'): (116, 209),
                  ('B', 'C'): (180, 153), ('B', 'D'): (306, 132),
                  ('C', 'D'): (293, 259), ('B', 'E'): (335, 43),
                  ('D', 'E'): (450, 157)}
EXERCISE_NODES = {'P': (55, 145), 'Q': (270, 65),
                  'R': (270, 230), 'S': (475, 145)}
EXERCISE_EDGES = (('P', 'Q', 4), ('P', 'R', 1), ('R', 'Q', 2),
                  ('Q', 'S', 0), ('R', 'S', 6))
EXERCISE_LABEL_POS = {('P', 'Q'): (155, 88), ('P', 'R'): (155, 211),
                      ('R', 'Q'): (245, 154), ('Q', 'S'): (380, 90),
                      ('R', 'S'): (380, 211)}


def _input(vertices, edges, directed):
    vertices, edges = tuple(vertices), tuple(edges)
    if not vertices or len(set(vertices)) != len(vertices):
        raise ValueError('Vertices must be nonempty and distinct')
    adjacency = {v: {} for v in vertices}
    for a, b, weight in edges:
        if a not in adjacency or b not in adjacency or a == b:
            raise ValueError('Edges need distinct known endpoints')
        if isinstance(weight, bool) or not isinstance(weight, Integral) or weight < 0:
            raise ValueError('Classroom traces require nonnegative integer weights')
        if b in adjacency[a]:
            raise ValueError('Parallel or duplicate edges are outside this lesson')
        adjacency[a][b] = int(weight)
        if not directed:
            adjacency[b][a] = int(weight)
    return vertices, adjacency


def dijkstra_states(vertices=MAIN_NODES, edges=MAIN_EDGES, source='A', *, directed=False):
    vertices, adjacency = _input(vertices, edges, directed)
    if source not in adjacency:
        raise ValueError('Unknown source')
    distance = dict.fromkeys(vertices)
    parent = dict.fromkeys(vertices)
    settled, order, states = set(), [], []
    distance[source] = 0

    def save(phase, action, current=None, edge=None, candidate=None):
        states.append(dict(phase=phase, action=action, current=current, edge=edge,
                           candidate=candidate, distance=distance.copy(),
                           parent=parent.copy(), settled=tuple(v for v in vertices if v in settled),
                           order=tuple(order), source=source))

    save('init', f'初始化：{source} 的距离为 0，其余尚未找到路径；前驱为空。')
    while len(settled) < len(vertices):
        finite = [v for v in vertices if v not in settled and distance[v] is not None]
        if not finite:
            save('unreachable', '没有有限的未确认候选。剩余顶点从源点不可达，停止。')
            return states
        # min preserves the input numbering when finite labels tie.
        u = min(finite, key=distance.__getitem__)
        save('select', f'选取 {u}：它的暂定距离 {distance[u]} 在未确认顶点中最小。', u)
        settled.add(u)
        order.append(u)
        save('confirm', f'确认 {u} 的最短距离为 {distance[u]}；接着枚举它的邻居。', u)
        for v in vertices:
            if v not in adjacency[u]:
                continue
            weight = adjacency[u][v]
            if v in settled:
                save('skip', f'读取 {u}→{v}，权 {weight}。{v} 已确认，本轮跳过。', u, (u, v))
                continue
            candidate = distance[u] + weight
            old = distance[v]
            save('compare', f'读取 {u}→{v}：新候选 {distance[u]}+{weight}={candidate}，'
                 f'与原距离 {fmt(old)} 比较。', u, (u, v), candidate)
            if old is None or candidate < old:
                distance[v], parent[v] = candidate, u
                save('update', f'更新 {v}：{fmt(old)} 改为 {candidate}，前驱改为 {u}。',
                     u, (u, v), candidate)
            else:
                save('keep', f'保留 {v}：候选 {candidate} 没有严格小于 {fmt(old)}，前驱不变。',
                     u, (u, v), candidate)
        save('round-end', f'{u} 的邻居更新完成，开始下一轮选择。', u)
    save('done', '所有顶点均已确认，单源计算完成。')
    return states


def recover_path(state, target):
    """Return one path, or None; the source itself is reachable without a parent."""
    if target not in state['distance']:
        raise ValueError('Unknown target')
    if state['distance'][target] is None:
        return None
    path, seen, u = [], set(), target
    while u is not None:
        if u in seen:
            raise ValueError('Cyclic predecessor record')
        seen.add(u)
        path.append(u)
        if u == state['source']:
            return tuple(reversed(path))
        u = state['parent'][u]
    raise ValueError('Finite label has no predecessor path to the source')


def floyd_stages(vertices=MAIN_NODES, edges=MAIN_EDGES, *, directed=False):
    """Snapshots after allowing each successive intermediate vertex (k outermost)."""
    vertices, adjacency = _input(vertices, edges, directed)
    d = [[0 if a == b else adjacency[a].get(b) for b in vertices] for a in vertices]
    states = [dict(allowed=(), distance=tuple(tuple(row) for row in d))]
    for k, vertex in enumerate(vertices):
        for i in range(len(vertices)):
            for j in range(len(vertices)):
                if d[i][k] is None or d[k][j] is None:
                    continue
                candidate = d[i][k] + d[k][j]
                if d[i][j] is None or candidate < d[i][j]:
                    d[i][j] = candidate
        states.append(dict(allowed=vertices[:k + 1],
                           distance=tuple(tuple(row) for row in d)))
    return states


def fmt(value):
    return '∞' if value is None else str(value)


def state_table(state, vertices=MAIN_NODES):
    rows = []
    for i, v in enumerate(vertices):
        confirmed = v in state['settled']
        status = '已确认' if confirmed else '不可达' if state['phase'] == 'unreachable' else '待定'
        cls = ' class="sp-confirmed"' if confirmed else ''
        rows.append(f'<tr{cls}><th>{escape(v)} ({i})</th><td>{fmt(state["distance"][v])}</td>'
                    f'<td>{escape(state["parent"][v] or "—")}</td><td>{status}</td></tr>')
    return ('<table class="sp-state"><thead><tr><th>顶点 (编号)</th><th>dist</th>'
            '<th>parent</th><th>状态</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')


def graph_view(nodes=MAIN_NODES, edges=MAIN_EDGES, *, directed=False,
               caption='带权无向主例；边权表示固定通行时间。', marked=(), states=None,
               regions=(), legend='', notes=None, details=None):
    return graph(nodes, [(a, b) for a, b, _ in edges], directed=directed,
                 labels={(a, b): w for a, b, w in edges},
                 label_positions=MAIN_LABEL_POS if nodes is MAIN_NODES else EXERCISE_LABEL_POS,
                 marked=marked, states=states, caption=caption, legend=legend,
                 regions=regions, edge_notes=notes, node_details=details, view_box=(0, 10, 520, 285))


def dijkstra_player():
    panels = []
    for state in dijkstra_states():
        node_states = {v: 'visited' if v in state['settled'] else 'unvisited' for v in MAIN_NODES}
        if state['current']:
            node_states[state['current']] = 'current'
        edge = state['edge']
        diagram = graph_view(states=node_states, marked=(edge,) if edge else (),
                             caption='蓝底：已确认；橙圈：当前处理。确认状态同时见右表。')
        for a, b in ((p, v) for v, p in state['parent'].items() if p is not None):
            for x, y in ((a, b), (b, a)):
                token = f'data-edge="{x}-{y}"><path class="graph-edge'
                diagram = diagram.replace(token, token + ' sp-predecessor')
        completed = ', '.join(state['order']) or '空'
        info = f'<p class="sp-action">{escape(state["action"])}</p>' + state_table(state)
        if edge:
            a, b = edge
            weight = next(w for x, y, w in MAIN_EDGES if {x, y} == {a, b})
            current_input = f'{a}→{b}，权 {weight}'
        else:
            current_input = '尚未读取新边'
        info += f'<p class="sp-meta">确认：{escape(completed)}　输入：{current_input}</p>'
        panels.append('<div class="sp-two">' + diagram + '<div>' + info + '</div></div>' +
                      '<p class="sp-legend">蓝色实线：当前前驱；红色粗实线：当前读取的边。原图保持不变。</p>')
    return player(panels, 'Dijkstra：选择、确认、读取与更新').replace(
        'class="tree-player"', 'class="tree-player sp-player"', 1)
