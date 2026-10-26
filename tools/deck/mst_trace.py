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
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.size = {v: 1 for v in vertices}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

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
        groups = {}
        for v in self.parent:
            groups.setdefault(self.find(v), []).append(v)
        return tuple(sorted(tuple(sorted(g)) for g in groups.values()))

    def parents(self):
        return {v: self.find(v) for v in self.parent}


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
        same = dsu.find(a) == dsu.find(b)
        add(f'检查第 {i + 1} 条边 {a}{b}={w}：两端当前是否同组？', i, e)
        if same:
            rejected.append(e)
            reason = '两端已在同一组；加入会成环，拒绝。'
            add(f'拒绝 {a}{b}={w}；{reason}', i, e, 'reject', reason)
        else:
            before = (dsu.find(a), dsu.find(b))
            dsu.union(a, b)
            selected.append(e)
            total += w
            reason = f'两端 {before[0]}、{before[1]} 不同组；接受并合并。'
            add(f'接受 {a}{b}={w}；{reason}', i, e, 'accept', reason)
    add(f'扫描结束：已选 {len(selected)} 条边，总权 {total}。')
    return states


def exercise_states():
    return kruskal_states(EXERCISE_EDGES, EXERCISE_NODES)


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
                 caption='红粗=已选；橙虚线=候选；灰虚线=拒绝；权值在边旁。',
                 legend='')


def _prim_content(state):
    selected = _edge_text(state['selected_edges'])
    key = _key_text(state['key'], state['parent'], state['has_key'],
                    set(state['selected_vertices']))
    total = state['total_weight']
    return ('<p class="trace-action">' + escape(state['action']) + '</p>' +
            '<p class="trace-detail"><strong>已纳入 S</strong>：' +
            escape('、'.join(state['selected_vertices'])) + '</p>' +
            '<p class="trace-detail"><strong>候选入口</strong>：' + escape(key) + '</p>' +
            '<p class="trace-detail"><strong>已选边</strong>：' + escape(selected) +
            '；<strong>总权</strong>：' + str(total) + '</p>' +
            '<p class="trace-legend">橙=当前顶点；红=已选边；橙虚线=候选边。key 是接入 S 的一条边权，不是路径距离。</p>')


def _kruskal_content(state):
    candidate = state.get('candidate_edge')
    decision = state.get('decision')
    dec = ''
    if decision == 'accept':
        dec = '<p class="trace-detail"><strong>决定</strong>：接受；' + escape(state['reason']) + '</p>'
    elif decision == 'reject':
        dec = '<p class="trace-detail"><strong>决定</strong>：拒绝；' + escape(state['reason']) + '</p>'
    comps = '；'.join('{' + ','.join(g) + '}' for g in state['components']) or '空'
    parents = ' '.join(f'{v}→{p}' for v, p in sorted(state['dsu_parent'].items()))
    return ('<p class="trace-action">' + escape(state['action']) + '</p>' + dec +
            '<p class="trace-detail"><strong>已选边</strong>：' + escape(_edge_text(state['selected_edges'])) +
            '；<strong>总权</strong>：' + str(state['total_weight']) + '</p>' +
            '<p class="trace-detail"><strong>当前分组</strong>：' + escape(comps) + '</p>' +
            '<p class="trace-detail"><strong>DSU parent</strong>：' + escape(parents) + '</p>' +
            '<p class="trace-legend">红=已选边；橙虚线=当前检查边；灰虚线=已拒绝边。分组与 parent 是两种表示。</p>')


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
    html = step_player(panels, 'Kruskal 与 DSU 推演')
    return html.replace('class="tree-player"', 'class="tree-player graph-player mst-player"', 1)
