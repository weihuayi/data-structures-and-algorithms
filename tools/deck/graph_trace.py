"""Deterministic graph-search states for the D012 player.

The module owns state transitions only; it does not know about the DOM.  Every
snapshot is derived from the same adjacency lists and the same first-visit rule
as code/traversal_demo.c.  The player uses the shared tree-player controls and
is therefore keyboard-operable and testable without a browser.
"""
from html import escape

from graph_diagram import graph
from tree_trace import player as step_player

NODES = {
    'A': (65, 60), 'B': (275, 60), 'C': (170, 205),
    'D': (365, 205), 'E': (465, 60),
}
EDGES = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D')]
ADJ = {
    'A': ['B', 'C'],
    'B': ['A', 'C'],
    'C': ['A', 'B', 'D'],
    'D': ['C'],
    'E': [],
}
INDEX = {v: i for i, v in enumerate(NODES)}


def _neighbors(vertex, order):
    if order == 'asc':
        return list(ADJ[vertex])
    if order == 'desc':
        return list(reversed(ADJ[vertex]))
    raise ValueError("order must be 'asc' or 'desc'")


def _copy_stack(stack):
    return tuple({'vertex': f['vertex'], 'next': f['next']} for f in stack)


def _state(states, action, *, visited, current, stack, queue, parent, distance,
           tree_edges, output, processing=None, examined=None):
    states.append({
        'action': action,
        'visited': tuple(visited),
        'current': current,
        'processing': processing,
        'examined': examined,
        'stack': _copy_stack(stack),
        'queue': tuple(queue),
        'parent': dict(parent),
        'distance': dict(distance),
        'tree_edges': tuple(tree_edges),
        'output': tuple(output),
    })


def dfs_states(start='A', order='asc'):
    """Depth-first snapshots: call stack, cursor, output and tree edges.

    The same state machine models recursion and an explicit frame stack; only
    the label and cursor explanation differ in the rendered player.
    """
    if start not in ADJ:
        raise ValueError('start must be a vertex')
    visited, parent, distance, tree_edges = [], {}, {}, []
    stack, output, states = [], [], []

    def visit(vertex, source):
        visited.append(vertex)
        parent[vertex] = source
        distance[vertex] = 0 if source is None else distance[source] + 1
        output.append(vertex)
        if source is not None:
            tree_edges.append((source, vertex))

    _state(states, '准备：从 A 出发。先预测第一步；此时 visited 全为假。',
           visited=visited, current=None, stack=stack, queue=(), parent=parent,
           distance=distance, tree_edges=tree_edges, output=output)
    visit(start, None)
    stack.append({'vertex': start, 'next': 0})
    _state(states, f'访问 {start}：visited[{start}]=true，parent=-1，输出 {start}；压入帧 ({start},0)。',
           visited=visited, current=start, stack=stack, queue=(), parent=parent,
           distance=distance, tree_edges=tree_edges, output=output)
    while stack:
        frame = stack[-1]
        vertex, pos = frame['vertex'], frame['next']
        neighbors = _neighbors(vertex, order)
        if pos >= len(neighbors):
            stack.pop()
            current = stack[-1]['vertex'] if stack else None
            _state(states, f'{vertex} 的邻接项已全部检查，弹出帧；' +
                   (f'回到 {current} 的调用。' if current else '栈空，搜索结束。'),
                   visited=visited, current=current, stack=stack, queue=(), parent=parent,
                   distance=distance, tree_edges=tree_edges, output=output)
            continue
        neighbor = neighbors[pos]
        frame['next'] = pos + 1
        if neighbor in visited:
            _state(states, f'{vertex} 检查位置 {pos} 的 {neighbor}：已访问，跳过；游标 {pos}→{pos+1}。',
                   visited=visited, current=vertex, stack=stack, queue=(), parent=parent,
                   distance=distance, tree_edges=tree_edges, output=output)
        else:
            visit(neighbor, vertex)
            stack.append({'vertex': neighbor, 'next': 0})
            _state(states, f'{vertex} 检查位置 {pos} 的 {neighbor}：未访问；访问 {neighbor}，输出 {neighbor}，压入 ({neighbor},0)。',
                   visited=visited, current=neighbor, stack=stack, queue=(), parent=parent,
                   distance=distance, tree_edges=tree_edges, output=output)
    _state(states, '栈空：从 A 可达的搜索结束；E 没有被访问。',
           visited=visited, current=None, stack=stack, queue=(), parent=parent,
           distance=distance, tree_edges=tree_edges, output=output)
    return states


def bfs_states(start='A', order='asc'):
    """Breadth-first snapshots: queue, visit time and distance."""
    if start not in ADJ:
        raise ValueError('start must be a vertex')
    visited, parent, distance, tree_edges = [], {}, {}, []
    queue, output, states = [], [], []

    def visit(vertex, source):
        visited.append(vertex)
        parent[vertex] = source
        distance[vertex] = 0 if source is None else distance[source] + 1
        output.append(vertex)
        if source is not None:
            tree_edges.append((source, vertex))

    _state(states, '准备：从 A 出发。BFS 用队头出队、队尾入队；先预测第一步。',
           visited=visited, current=None, stack=(), queue=queue, parent=parent,
           distance=distance, tree_edges=tree_edges, output=output)
    visit(start, None)
    queue.append(start)
    _state(states, f'访问 {start}：visited[{start}]=true，distance[{start}]=0，输出 {start}；{start} 入队。',
           visited=visited, current=start, stack=(), queue=queue, parent=parent,
           distance=distance, tree_edges=tree_edges, output=output)
    while queue:
        vertex = queue.pop(0)
        _state(states, f'{vertex} 出队；正在处理 {vertex} 的邻接表。',
               visited=visited, current=vertex, stack=(), queue=queue, parent=parent,
               distance=distance, tree_edges=tree_edges, output=output,
               processing=vertex, examined=None)
        for pos, neighbor in enumerate(_neighbors(vertex, order)):
            if neighbor in visited:
                _state(states, f'正在处理 {vertex}，检查位置 {pos} 的 {neighbor}：已访问，跳过。',
                       visited=visited, current=vertex, stack=(), queue=queue, parent=parent,
                       distance=distance, tree_edges=tree_edges, output=output,
                       processing=vertex, examined=neighbor)
            else:
                visit(neighbor, vertex)
                queue.append(neighbor)
                _state(states, f'正在处理 {vertex}，检查位置 {pos} 的 {neighbor}：未访问；访问 {neighbor}，distance={distance[neighbor]}，入队。',
                       visited=visited, current=vertex, stack=(), queue=queue, parent=parent,
                       distance=distance, tree_edges=tree_edges, output=output,
                       processing=vertex, examined=neighbor)
    _state(states, '队列空：BFS 结束；E 没有被访问。',
           visited=visited, current=None, stack=(), queue=queue, parent=parent,
           distance=distance, tree_edges=tree_edges, output=output)
    return states


def _diagram(state, label, show_examined=False):
    processing = state.get('processing') or state['current']
    examined = state.get('examined') if show_examined else None
    states = {}
    for vertex in NODES:
        if vertex == processing:
            states[vertex] = 'current'
        elif vertex == examined:
            states[vertex] = 'examined'
        elif vertex in state['visited']:
            states[vertex] = 'visited'
        else:
            states[vertex] = 'unvisited'
    return graph(NODES, EDGES, caption=label, marked=state['tree_edges'],
                 states=states, legend='')


def _parent_line(state):
    parts = []
    for vertex in NODES:
        value = state['parent'].get(vertex)
        parts.append(f'{vertex}:{value if value is not None else "-1"}')
    return 'parent（-1=根或未访问）：' + ' '.join(parts)


def _content(state, mode, show_cursor):
    action = '<p class="trace-action">' + escape(state['action']) + '</p>'
    process = ''
    if mode == 'bfs' and state.get('processing'):
        process = '<p class="trace-detail">正在处理：<strong>' + escape(state['processing']) + '</strong>'
        if state.get('examined'):
            process += '；刚检查：<strong>' + escape(state['examined']) + '</strong>'
        process += '。</p>'
    if mode == 'bfs':
        pending = ' '.join(state['queue']) or '空'
        container = ('<div class="trace-state"><strong>队头 → 队尾</strong>：' +
                     escape(pending) + '</div>')
    else:
        frames = state['stack']
        shown = ' '.join(f'{f["vertex"]}:{f["next"]}' for f in frames) or '空'
        label = '显式帧栈（底→顶）' if mode == 'stack' else '调用栈（底→顶）'
        container = '<div class="trace-state"><strong>' + label + '</strong>：' + escape(shown) + '</div>'
    output = '<p class="trace-output">已输出：<strong>' + (' '.join(state['output']) or '空') + '</strong></p>'
    detail = ''
    if show_cursor and state['stack']:
        frame = state['stack'][-1]
        vertex, pos = frame['vertex'], frame['next']
        items = ' '.join(f'{i}→{w}' for i, w in enumerate(ADJ[vertex]))
        detail = ('<p class="trace-detail">当前帧 <strong>' + escape(vertex) + ':' + str(pos) +
                  '</strong>；' + escape(vertex) + ' 的邻接表：' + escape(items) +
                  '。next 是下一项待检查的位置，不是顶点编号。</p>')
    distance = ''
    if mode == 'bfs':
        values = ' '.join(f'{v}:{state["distance"][v]}' for v in state['visited']) or '未开始'
        distance = '<p class="trace-detail">distance：' + escape(values) + '（从 A 的最少边数）。</p>'
    return action + process + container + output + detail + distance + '<p class="trace-detail">' + escape(_parent_line(state)) + '</p>'


def _legend(mode):
    if mode == 'bfs':
        return ('<p class="trace-legend">橙实线=正在处理；橙虚线=刚检查；蓝底=已访问；灰=未访问；红线=搜索树边。'
                'BFS 中 distance 为最少边数。</p>')
    return '<p class="trace-legend">橙=当前帧；蓝底=已访问；灰=未访问；红线=搜索树边。</p>'


def dfs_player(mode='recursive', order='asc'):
    """Return a manual DFS player. mode is 'recursive' or 'stack'."""
    if mode not in ('recursive', 'stack'):
        raise ValueError("mode must be 'recursive' or 'stack'")
    states = dfs_states(order=order)
    panels = []
    for i, state in enumerate(states):
        body = ('<div class="graph-layout graph-player-layout">' +
                _diagram(state, 'DFS 递归' if mode == 'recursive' else 'DFS 显式栈', False) +
                '<div>' + _content(state, mode, mode == 'stack') + '</div></div>' +
                _legend(mode))
        panels.append(body)
    html = step_player(panels, 'DFS 递归深入与回溯' if mode == 'recursive' else 'DFS 显式帧栈推演')
    return html.replace('class="tree-player"', 'class="tree-player graph-player"', 1)


def bfs_player(order='asc'):
    states = bfs_states(order=order)
    panels = []
    for i, state in enumerate(states):
        body = ('<div class="graph-layout graph-player-layout">' +
                _diagram(state, 'BFS 队列', True) +
                '<div>' + _content(state, 'bfs', False) + '</div></div>' +
                _legend('bfs'))
        panels.append(body)
    html = step_player(panels, 'BFS 队列与逐层扩展')
    return html.replace('class="tree-player"', 'class="tree-player graph-player"', 1)
