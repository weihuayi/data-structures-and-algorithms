"""Deterministic Prim/Kruskal states for D013; DOM rendering is kept separate."""
from html import escape

from graph_diagram import graph
from tree_trace import player as step_player

MAIN_NODES = {'A': (60, 60), 'B': (290, 55), 'C': (130, 215),
              'D': (385, 245), 'E': (480, 65)}
MAIN_EDGES = [('A', 'B', 1), ('A', 'C', 4), ('B', 'C', 2),
              ('B', 'D', 5), ('C', 'D', 3), ('C', 'E', 6), ('D', 'E', 7)]
MAIN_LABELS = {(a, b): w for a, b, w in MAIN_EDGES}
MAIN_LABEL_POS = {('A', 'B'): (175, 42), ('A', 'C'): (78, 140), ('B', 'C'): (235, 128), ('B', 'D'): (350, 180), ('C', 'D'): (250, 238), ('C', 'E'): (315, 120), ('D', 'E'): (445, 145)}
TRIANGLE_NODES = {'A': (90, 65), 'B': (320, 60), 'C': (205, 220)}
TRIANGLE_EDGES = [('A', 'B', 10), ('A', 'C', 1), ('B', 'C', 1)]
TRIANGLE_LABEL_POS = {('A', 'B'): (205, 35), ('A', 'C'): (120, 150), ('B', 'C'): (290, 150)}
# Independent equal-weight triangle for the exchange argument (not the main case).
EXCHANGE_NODES = {'A': (90, 65), 'B': (320, 60), 'C': (205, 220)}
EXCHANGE_EDGES = [('A', 'B', 1), ('A', 'C', 2), ('B', 'C', 2)]
EXERCISE_NODES = {'P': (80, 65), 'Q': (280, 55), 'R': (170, 210), 'S': (380, 190)}
EXERCISE_EDGES = [('P', 'Q', 3), ('P', 'R', 1), ('Q', 'R', 2),
                  ('Q', 'S', 4), ('R', 'S', 5)]


def _adj(edges, nodes=MAIN_NODES):
    out = {v: [] for v in nodes}
    for a, b, w in edges:
        out[a].append((b, w))
        out[b].append((a, w))
    for v in out:
        out[v].sort(key=lambda item: (item[1], item[0]))
    return out


def _edge(a, b, w):
    return (a, b, w) if a < b else (b, a, w)


def _key_text(key, parent, has_key, selected):
    parts = []
    for v in sorted(key):
        if v in selected or not has_key.get(v):
            continue
        parts.append(f'{v}←{parent[v]}:{key[v]}')
    return '，'.join(parts) or '无'


def _edge_text(edges):
    return '、'.join(f'{a}{b}:{w}' for a, b, w in edges) or '无'


def prim_states(start='A', edges=MAIN_EDGES, nodes=MAIN_NODES):
    if start not in nodes:
        raise ValueError('start must be a vertex')
    adj = _adj(edges, nodes)
    component_roots = [start]
    selected_vertices = {start}
    selected, key, parent, has_key = [], {}, {}, {}
    total, states = 0, []

    def update(u):
        for v, w in adj[u]:
            if v in selected_vertices:
                continue
            if not has_key.get(v) or w < key[v]:
                has_key[v], key[v], parent[v] = True, w, u

    update(start)

    def add(action, current_edge=None, current_vertex=None):
        states.append({
            'selected_vertices': tuple(sorted(selected_vertices)),
            'selected_edges': tuple(selected),
            'key': dict(key), 'parent': dict(parent), 'has_key': dict(has_key),
            'current_edge': current_edge, 'current_vertex': current_vertex,
            'total_weight': total, 'components': len(component_roots), 'action': action,
        })

    add(f'准备：S={{{start}}}；先预测最轻跨界边。', current_vertex=start)
    while len(selected_vertices) < len(nodes):
        candidates = [(key[v], v, parent[v]) for v in key
                      if v not in selected_vertices and has_key.get(v)]
        if not candidates:
            root = min((v for v in nodes if v not in selected_vertices), key=lambda v: str(v))
            component_roots.append(root)
            selected_vertices.add(root)
            update(root)
            if len(selected_vertices) == len(nodes):
                action = (f'重启新分量 {root}（第 {len(component_roots)} 个分量）；'
                          f'已覆盖全部顶点，MSF 完成，总权 {total}。')
            else:
                action = f'没有跨界候选：当前分量结束；重启新分量 {root}（第 {len(component_roots)} 个分量）。'
            add(action, current_vertex=root)
            continue
        w, v, u = min(candidates, key=lambda x: (x[0], x[1]))
        e = _edge(u, v, w)
        add(f'当前最轻跨界边：{u}{v}={w}；候选入口 {v}←{u}。', current_edge=e)
        selected_vertices.add(v)
        selected.append(e)
        total += w
        for vertex in (v,):
            key.pop(vertex, None)
            parent.pop(vertex, None)
            has_key.pop(vertex, None)
        update(v)
        if len(selected_vertices) == len(nodes):
            action = f'接受 {u}{v}={w}；S 覆盖全部顶点，MST 完成，总权 {total}。'
        else:
            action = f'接受 {u}{v}={w}；更新外部顶点的 key/parent；总权 {total}。'
        add(action, current_vertex=v)
    return states


class _DSU:
    """Kruskal's dynamic partition.

    ``find`` is an algorithm operation and may compress paths.  ``root`` is a
    read-only query used by snapshots: it must never change the internal
    parent pointers while a teacher or a player is inspecting them.
    """

    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.size = {v: 1 for v in vertices}

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != x:
            parent = self.parent[x]
            self.parent[x] = root
            x = parent
        return root

    def root(self, x):
        """Read-only representative lookup; no path compression."""
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True

    def components(self):
        """Read-only partition snapshot derived from the real parent pointers."""
        groups = {}
        for v in self.parent:
            groups.setdefault(self.root(v), []).append(v)
        return tuple(sorted(tuple(sorted(g)) for g in groups.values()))

    def parents(self):
        """Copy the real parent pointers; never rewrite them through find()."""
        return dict(self.parent)


def kruskal_states(edges=MAIN_EDGES, nodes=MAIN_NODES):
    sorted_edges = tuple(sorted((_edge(a, b, w) for a, b, w in edges),
                                key=lambda e: (e[2], e[0], e[1])))
    dsu = _DSU(nodes)
    selected, rejected, total, states = [], [], 0, []

    def add(action, index=None, candidate=None, decision=None, reason=''):
        states.append({
            'sorted_edges': sorted_edges, 'current_index': index,
            'candidate_edge': candidate, 'selected_edges': tuple(selected),
            'rejected_edges': tuple(rejected), 'components': dsu.components(),
            'dsu_parent': dsu.parents(), 'decision': decision, 'reason': reason,
            'total_weight': total, 'action': action,
        })

    add('准备：边按 (权值, 端点) 排序；每个顶点独立成组。', index=None)
    for i, e in enumerate(sorted_edges):
        a, b, w = e
        # The check is an algorithm operation: a real find() may compress paths.
        ra, rb = dsu.find(a), dsu.find(b)
        same = ra == rb
        add(f'检查第 {i + 1} 条边 {a}{b}={w}：两端当前是否同组？', i, e)
        if same:
            rejected.append(e)
            reason = '两端已在同一组；加入会成环，拒绝。'
            add(f'拒绝 {a}{b}={w}；{reason}', i, e, 'reject', reason)
        else:
            dsu.union(a, b)
            selected.append(e)
            total += w
            reason = f'两端 {ra}、{rb} 不同组；接受并合并。'
            add(f'接受 {a}{b}={w}；{reason}', i, e, 'accept', reason)
    add(f'扫描结束：已选 {len(selected)} 条边，总权 {total}。')
    return states


def exercise_states():
    return kruskal_states(EXERCISE_EDGES, EXERCISE_NODES)


def path_compression_demo():
    """Independent auxiliary example: unions AB, CD, BC, then find(D).

    Returns the real parent snapshots before/after the query, plus the
    read-only partition that must stay unchanged.
    """
    dsu = _DSU(('A', 'B', 'C', 'D'))
    for a, b in (('A', 'B'), ('C', 'D'), ('B', 'C')):
        dsu.union(a, b)
    before = {'parent': dsu.parents(), 'components': dsu.components()}
    representative = dsu.find('D')
    after = {'parent': dsu.parents(), 'components': dsu.components()}
    return {'query': 'D', 'before': before, 'after': after,
            'representative': representative}


def _graph(state, nodes, edges, labels, prim=False):
    selected = state['selected_edges']
    current = state.get('current_edge')
    if current is None and state.get('decision') is None:
        current = state.get('candidate_edge')
    candidates = () if current is None else (current[:2],)
    rejected = tuple(e[:2] for e in state.get('rejected_edges', ()))
    states = {}
    if prim:
        for v in state['selected_vertices']:
            states[v] = 'visited'
        if state.get('current_vertex'):
            states[state['current_vertex']] = 'current'
    positions = MAIN_LABEL_POS if nodes is MAIN_NODES else None
    return graph(nodes, [(a, b) for a, b, w in edges], labels=labels, marked=tuple(e[:2] for e in selected),
                 candidate=candidates, rejected=rejected, states=states, label_positions=positions,
                 caption='红粗=已接受；橙虚线=正在检查；灰细虚线=已拒绝。虚线只表示处理状态，每条边都来自输入图。',
                 legend='')


def dsu_diagram(parent, positions, *, caption, root=None):
    """Static DSU parent-pointer forest; every arrow points to p[v].

    The diagram is data-driven: it draws exactly the supplied parent mapping and
    never calls find(), so a saved snapshot cannot be silently flattened.
    """
    if set(parent) - set(positions):
        raise ValueError('every DSU vertex needs a position')
    edges = [(v, p) for v, p in sorted(parent.items()) if v != p]
    details = {v: f'p[{v}]={p}' for v, p in parent.items() if v != p}
    states = {root: 'visited'} if root in parent else None
    return graph(positions, edges, directed=True, caption=caption,
                 node_details=details, states=states, legend='')


def _prim_content(state):
    selected = _edge_text(state['selected_edges'])
    key = _key_text(state['key'], state['parent'], state['has_key'],
                    set(state['selected_vertices']))
    total = state['total_weight']
    return ('<p class="trace-action">' + escape(state['action']) + '</p>' +
            '<p class="trace-detail"><strong>已纳入 S</strong>：' +
            escape('、'.join(state['selected_vertices'])) + '</p>' +
            '<p class="trace-detail"><strong>候选入口</strong>：' + escape(key) +
            '（没有入口的顶点不显示）</p>' +
            '<p class="trace-detail"><strong>已选边 F</strong>：' + escape(selected) +
            '；<strong>总权</strong>：' + str(total) + '</p>' +
            '<p class="trace-legend">橙=当前顶点；红粗=已接受边；橙虚线=当前候选。key 是接入 S 的一条边权，不是路径距离。</p>')


def _kruskal_content(state):
    candidate = state.get('candidate_edge')
    decision = state.get('decision')
    dec = ''
    if decision == 'accept':
        dec = '<p class="trace-detail"><strong>决定</strong>：接受；' + escape(state['reason']) + '</p>'
    elif decision == 'reject':
        dec = '<p class="trace-detail"><strong>决定</strong>：拒绝；' + escape(state['reason']) + '</p>'
    comps = '；'.join('{' + ','.join(g) + '}' for g in state['components']) or '空'
    return ('<p class="trace-action">' + escape(state['action']) + '</p>' + dec +
            '<p class="trace-detail"><strong>已选森林 F</strong>：' + escape(_edge_text(state['selected_edges'])) +
            '；<strong>总权</strong>：' + str(state['total_weight']) + '</p>' +
            '<p class="trace-detail"><strong>当前分组</strong>：' + escape(comps) +
            '；<strong>已拒绝</strong>：' + escape(_edge_text(state['rejected_edges'])) + '</p>' +
            '<p class="trace-legend">红粗=已接受；橙虚线=正在检查；灰细虚线=已拒绝。分组是已选边诱导的划分；'
            '内部表示留到第 20 页再读。</p>')


def prim_player():
    panels = []
    for state in prim_states():
        panels.append('<div class="graph-layout graph-player-layout">' +
                      _graph(state, MAIN_NODES, MAIN_EDGES, MAIN_LABELS, prim=True) +
                      '<div>' + _prim_content(state) + '</div></div>')
    html = step_player(panels, 'Prim 最小生成树推演')
    return html.replace('class="tree-player"', 'class="tree-player graph-player mst-player"', 1)


def kruskal_player():
    panels = []
    for state in kruskal_states():
        panels.append('<div class="graph-layout graph-player-layout">' +
                      _graph(state, MAIN_NODES, MAIN_EDGES, MAIN_LABELS) +
                      '<div>' + _kruskal_content(state) + '</div></div>')
    html = step_player(panels, 'Kruskal 分组合并推演')
    return html.replace('class="tree-player"', 'class="tree-player graph-player mst-player"', 1)
