"""D015 dependency semantics and views; input graphs never change during traces.

Topological output is an ordering operation, not a real task completion event.
Remaining indegree counts unreleased input arcs in every microstate; its simpler
interpretation as incoming arcs from un-emitted vertices applies at boundaries.
CPM assumes a single-source/sink DAG with nonnegative fixed integer durations.
"""
from collections import deque
from html import escape
from numbers import Integral
import re

from graph_diagram import graph
from tree_trace import player


TASKS = (
    ('A', '整理原始数据', (), 3, 0, 1),
    ('B', '编写分析程序', (), 5, 0, 2),
    ('C', '预处理数据', ('A',), 2, 1, 3),
    ('D', '测试分析程序', ('B', 'E'), 3, 2, 3),
    ('E', '准备测试样例', ('A',), 1, 1, 2),
    ('F', '运行分析并生成报告', ('C', 'D'), 2, 3, 4),
)
AOV_NODES = {'A': (50, 55), 'B': (50, 235), 'C': (300, 55),
             'D': (355, 235), 'E': (175, 150), 'F': (520, 145)}
AOV_EDGES = tuple((p, task[0]) for task in TASKS for p in task[2])
MAIN_ACTIVITIES = tuple((a, u, v, w) for a, _, _, w, u, v in TASKS)
AOE_NODES = {0: (45, 175), 1: (190, 65), 2: (325, 185),
             3: (470, 65), 4: (590, 175)}
EVENTS = ('项目开始', '数据已整理', '程序与样例就绪', '分析条件齐备', '报告完成')
AOE_LABELS = {(0, 1): (105, 94), (0, 2): (175, 208), (1, 2): (237, 148),
              (1, 3): (330, 43), (2, 3): (415, 137), (3, 4): (550, 101)}
EXERCISE_NODES = {2: (45, 145), 0: (245, 55), 3: (245, 235), 1: (455, 145)}
EXERCISE_ACTIVITIES = (('a', 2, 0, 2), ('b', 2, 3, 3), ('c', 0, 3, 1),
                       ('d', 0, 1, 4), ('e', 3, 1, 2))
EXERCISE_LABELS = {(2, 0): (135, 83), (2, 3): (135, 215), (0, 3): (213, 150),
                   (0, 1): (359, 83), (3, 1): (359, 215)}


def _graph_input(vertices, arcs):
    vertices, arcs = tuple(vertices), tuple(arcs)
    if not vertices or len(set(vertices)) != len(vertices):
        raise ValueError('Vertices must be nonempty and unique')
    adjacency = {u: [] for u in vertices}
    seen = set()
    for u, v in arcs:
        if u not in adjacency or v not in adjacency or (u, v) in seen:
            raise ValueError('Arcs need known endpoints and must be distinct')
        seen.add((u, v)); adjacency[u].append(v)
    return vertices, arcs, adjacency


def topological_states(vertices=AOV_NODES, arcs=AOV_EDGES, *, strategy='stack'):
    vertices, arcs, adjacency = _graph_input(vertices, arcs)
    if strategy not in {'stack', 'queue'}:
        raise ValueError('Choose stack or queue')
    degree = dict.fromkeys(vertices, 0)
    for u, v in arcs: degree[v] += 1
    ready = deque(v for v in vertices if degree[v] == 0)
    order, completed, removed, states = [], [], [], []

    def save(phase, action, current=None, edge=None):
        states.append(dict(phase=phase, action=action, current=current, edge=edge,
                           degree=degree.copy(), ready=tuple(ready), order=tuple(order),
                           completed=tuple(completed), removed=tuple(removed)))

    save('init', '由全部输入弧计算入度，把所有零入度顶点放入候选。')
    while ready:
        u = ready.pop() if strategy == 'stack' else ready.popleft()
        order.append(u)
        save('output', f'将 {u} 排入序列；接着处理它的出边。这不表示现实活动已经完成。', u)
        for v in adjacency[u]:
            save('read', f'读取输入弧 {u}→{v}；当前剩余入度为 {degree[v]}，尚未执行减法。', u, (u, v))
            old = degree[v]; degree[v] -= 1; removed.append((u, v))
            if degree[v] == 0:
                ready.append(v)
            suffix = '，加入候选' if degree[v] == 0 else '，仍不能加入候选'
            save('release', f'解除 {u}→{v} 这一项依赖：{v} 的剩余入度 {old}→{degree[v]}' + suffix + '。', u, (u, v))
        completed.append(u)
        save('boundary', f'{u} 的出边全部处理完。本轮结束，可以选择下一位。', u)
    complete = len(order) == len(vertices)
    save('done' if complete else 'blocked', '全部顶点已排入序列。' if complete else
         '候选为空但尚有顶点未输出：剩余子图中存在环；并非每个剩余顶点都在环上。')
    return states


def critical_path(vertices=AOE_NODES, activities=MAIN_ACTIVITIES, *, source=0, sink=4):
    vertices, activities = tuple(vertices), tuple(activities)
    vertices, arcs, adjacency = _graph_input(vertices, ((u, v) for a, u, v, w in activities))
    if len({a for a, u, v, w in activities}) != len(activities):
        raise ValueError('Activity IDs must be unique')
    if any(isinstance(w, bool) or not isinstance(w, Integral) or w < 0 for a, u, v, w in activities):
        raise ValueError('Durations must be nonnegative integers')
    if source not in vertices or sink not in vertices:
        raise ValueError('Explicit source and sink must be vertices')
    topo = topological_states(vertices, arcs)[-1]
    if topo['phase'] != 'done':
        raise ValueError('CPM needs a DAG')
    incoming = dict.fromkeys(vertices, 0)
    for u, v in arcs: incoming[v] += 1
    if [v for v in vertices if incoming[v] == 0] != [source] or [v for v in vertices if not adjacency[v]] != [sink]:
        raise ValueError('Use one declared source/sink and a complete project network')
    order = topo['order']
    outgoing = {u: [] for u in vertices}
    for a, u, v, w in activities: outgoing[u].append((a, v, w))
    early = dict.fromkeys(vertices); early[source] = 0
    forward, final = [], [source]

    def snapshot(target, phase, action, values, final, current=None, edge=None):
        target.append(dict(phase=phase, action=action, values=values.copy(),
                           final=tuple(final), current=current, edge=edge))

    snapshot(forward, 'init', f'源事件 {source} 的最早时间为 0，其余尚未汇总。', early, final)
    for u in order:
        if u not in final: final.append(u)
        snapshot(forward, 'enter', f'全部前驱已传播到事件 {u}；ve[{u}]={early[u]} 已确定。', early, final, u)
        for a, v, w in outgoing[u]:
            candidate = early[u] + w; old = early[v]
            early[v] = candidate if old is None else max(old, candidate)
            snapshot(forward, 'update', f'活动 {a}：{early[u]}+{w}={candidate}；ve[{v}] 从 {fmt(old)} 更新为 {early[v]}。', early, final, u, (u, v))
        snapshot(forward, 'boundary', f'事件 {u} 的全部出边已传播。未标“确定”的值仍是已收集约束的下界。', early, final, u)
    snapshot(forward, 'done', f'正向计算完成；最早工期 T={early[sink]}。', early, final)
    late = dict.fromkeys(vertices); late[sink] = early[sink]
    backward, final = [], [sink]
    snapshot(backward, 'init', f'不延长最早工期：vl[{sink}]=T={early[sink]}。其余尚未汇总。', late, final)
    for u in reversed(order):
        snapshot(backward, 'enter', f'处理事件 {u}：逐项读取已经确定的后继期限。', late, final, u)
        for a, v, w in outgoing[u]:
            candidate = late[v] - w; old = late[u]
            late[u] = candidate if old is None else min(old, candidate)
            snapshot(backward, 'update', f'活动 {a}：后继期限 {late[v]}−时长 {w}={candidate}；vl[{u}] 从 {fmt(old)} 更新为 {late[u]}。', late, final, u, (u, v))
        if u not in final: final.append(u)
        snapshot(backward, 'boundary', f'事件 {u} 的全部后继约束已汇总；vl[{u}]={late[u]} 已确定。', late, final, u)
    snapshot(backward, 'done', '反向计算完成；接着计算每项活动的开始时间和余量。', late, final)
    activity_times = {a: dict(earliest=early[u], latest=late[v] - w,
                              slack=late[v] - w - early[u]) for a, u, v, w in activities}
    critical = tuple(a for a, u, v, w in activities if activity_times[a]['slack'] == 0)
    critical_set = set(critical)
    # Return one representative path only; all critical paths can be exponential.
    path, u = [], source
    while u != sink:
        a, v, w = next(edge for edge in outgoing[u] if edge[0] in critical_set)
        path.append(a); u = v
    return dict(order=order, early=early, late=late, T=early[sink],
                activity_times=activity_times, critical=critical, one_path=tuple(path),
                forward=forward, backward=backward)


def fmt(value):
    return '—' if value is None else str(value)


def aov_view(*, marked=(), states=None, cycle=False, caption='活动 A–F；箭头表示先完成、后开始的依赖。'):
    arcs = AOV_EDGES + ((('E', 'A'),) if cycle else ())
    result = graph(AOV_NODES, arcs, directed=True, marked=marked, states=states,
                 node_details={a: f'编号 {i}' for i, a in enumerate(AOV_NODES)},
                 caption=caption, view_box=(0, 0, 575, 300))
    if cycle:
        # Route the added reverse dependency clear of the original A->E arc.
        result = re.sub(r'<g data-edge="E-A">.*?</g>',
            '<g data-edge="E-A"><path class="graph-edge marked" d="M 175 126 Q 165 -25 74 55"/>'
            '<path class="graph-arrow marked" d="M 86 53 L 74 55 L 79 43"/></g>', result)
    return result


def completed_aov_view():
    """D015 construction answer; retain all input nodes/arcs and add only C/E→G."""
    added = (('C', 'G'), ('E', 'G'))
    return graph({**AOV_NODES, 'G': (335, 135)}, AOV_EDGES + added,
                 directed=True, marked=added,
                 caption='补充后的 AOV 网。',
                 legend='红色粗实线：新增 ' + '、'.join(a+'→'+b for a, b in added) + '。',
                 view_box=(0, 15, 575, 260))


def aoe_view(activities=MAIN_ACTIVITIES, *, exercise=False, marked=(), values=None, kind='ve', caption=None):
    nodes = EXERCISE_NODES if exercise else AOE_NODES
    positions = EXERCISE_LABELS if exercise else AOE_LABELS
    labels = {(str(u), str(v)): f'{a} · {w}' for a, u, v, w in activities}
    return graph({str(v): p for v, p in nodes.items()},
                 [(str(u), str(v)) for a, u, v, w in activities], directed=True,
                 marked=[(str(u), str(v)) for u, v in marked], labels=labels,
                 label_positions={(str(u), str(v)): p for (u, v), p in positions.items()},
                 node_details={str(v): f'{kind}={fmt(values[v])}' for v in nodes} if values else None,
                 caption=caption or ('源事件 2，汇事件 1；a–e 为活动，数字为时长。' if exercise else
                                     '顶点 0–4 是事件；A–F 是活动，数字为时长（小时）。'),
                 view_box=(0, 0, 500, 300) if exercise else (0, 0, 635, 270))


def table(headers, rows, cls=''):
    cell = lambda x: escape(str(x))
    return '<table class="dag-table ' + cls + '"><thead><tr>' + ''.join('<th>' + cell(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + cell(v) + '</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table>'


def task_table(*, durations=False):
    headers = ('活动', '工作内容', '直接前置') + (('小时',) if durations else ())
    return table(headers, [(a, name, '、'.join(pred) or '无') + ((w,) if durations else ())
                           for a, name, pred, w, u, v in TASKS])


def topological_player():
    panels = []
    for s in topological_states():
        state = {a: 'visited' for a in s['order']}
        if s['current'] is not None: state[s['current']] = 'current'
        diagram = aov_view(marked=(s['edge'],) if s['edge'] else (), states=state,
                           caption='原图保持不变；蓝底已排入序列，橙圈为当前处理顶点。')
        info = '<p class="dag-action">' + escape(s['action']) + '</p>'
        info += table(('顶点', *AOV_NODES), [('剩余入度', *(s['degree'][v] for v in AOV_NODES))], 'dag-state')
        info += '<p>栈（左底右顶）：<strong>' + (' '.join(s['ready']) or '空') + '</strong></p>'
        info += '<p>输出序列：<strong>' + (' '.join(s['order']) or '空') + '</strong></p>'
        info += '<p class="dag-note">已完成出边更新：' + ('、'.join(s['completed']) or '无') + '</p>'
        panels.append('<div class="dag-two">' + diagram + '<div>' + info + '</div></div>')
    return player(panels, '拓扑排序：排位与解除依赖').replace('class="tree-player"', 'class="tree-player dag-player"', 1)


def time_player(direction):
    result = critical_path(); kind = 've' if direction == 'forward' else 'vl'
    panels = []
    for s in result[direction]:
        diagram = aoe_view(values=s['values'], kind=kind, marked=(s['edge'],) if s['edge'] else ())
        info = '<p class="dag-action">' + escape(s['action']) + '</p>'
        info += table(('事件', *AOE_NODES), [(kind, *(fmt(s['values'][v]) for v in AOE_NODES)),
                       ('状态', *('确定' if v in s['final'] else '待汇总' for v in AOE_NODES))], 'dag-state')
        info += '<p class="dag-note">处理次序：' + ' → '.join(map(str, result['order'] if direction == 'forward' else result['order'][::-1])) + '</p>'
        info += '<p class="dag-note">红粗弧：当前读取的活动；“—”表示尚未汇总，不表示 0。</p>'
        panels.append('<div class="dag-two">' + diagram + '<div>' + info + '</div></div>')
    return player(panels, '最早时间的正向传播' if direction == 'forward' else '最迟时间的反向约束').replace('class="tree-player"', 'class="tree-player dag-player"', 1)
