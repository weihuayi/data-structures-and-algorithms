"""Deterministic classroom traces; each snapshot separates control and output."""
from html import escape
from tree_diagram import beside


def traversal_states(children, root, mode='pre'):
    states, output, visited, done, frames = [], [], [], [], []

    def save(action, current=None, pending=None):
        states.append(dict(action=action, current=current, output=output.copy(),
                           visited=visited.copy(), done=done.copy(),
                           pending=list(pending if pending is not None else frames)))

    save('先预测下一步；只有执行 visit 才向输出追加标识。')
    if mode in ('stack', 'queue'):
        pending = [root] if root is not None else []
        save('根入栈。' if mode == 'stack' else '根入队。', pending=pending)
        while pending:
            key = pending.pop() if mode == 'stack' else pending.pop(0)
            save(f'{key} 出栈。' if mode == 'stack' else f'{key} 出队。', key, pending)
            output.append(key); visited.append(key)
            save(f'访问 {key}：输出追加 {key}。', key, pending)
            left, right = children[key]
            for child, side in ((right, '右'), (left, '左')) if mode == 'stack' else ((left, '左'), (right, '右')):
                if child is not None:
                    pending.append(child)
                    save(f'{key} 的{side}孩子 {child} 入' + ('栈。' if mode == 'stack' else '队。'), key, pending)
        save('待处理任务为空，遍历结束。', pending=[])
        return states

    if mode not in ('pre', 'in', 'post'):
        raise ValueError(mode)

    def walk(key):
        if key is None:
            save('进入空子树：直接返回，输出不变。', frames[-1].split('：')[0] if frames else None)
            return
        frames.append(f'{key}：刚进入')
        save(f'进入 {key}，建立调用帧；进入本身不输出。', key)
        left, right = children[key]
        for event in {'pre': 'NLR', 'in': 'LNR', 'post': 'LRN'}[mode]:
            if event == 'N':
                frames[-1] = f'{key}：执行 visit'
                output.append(key); visited.append(key)
                save(f'访问 {key}：输出追加 {key}。', key)
            else:
                child = left if event == 'L' else right
                side = '左' if event == 'L' else '右'
                frames[-1] = f'{key}：等待{side}子树返回'
                save(f'{key} 准备递归处理{side}子树。', key)
                walk(child)
                frames[-1] = f'{key}：{side}子树已返回'
                save(f'回到 {key} 的调用，{side}子树已完成；这次返回不输出。', key)
        done.append(key)
        frames.pop()
        save(f'以 {key} 为根的子树完成，退出该调用；输出不变。', key)

    walk(root)
    save('根调用结束，遍历完成。')
    return states


def recovery_states(pre, inorder):
    """Validate every split, emitting partial links before descending."""
    if len(pre) != len(inorder) or len(set(pre)) != len(pre) or set(pre) != set(inorder):
        raise ValueError('长度、互异标识或集合不符合条件')
    states, links, built = [], [], []
    states.append(dict(pre=list(pre), inorder=list(inorder), root=None, left=[], right=[],
                       links=[], built=[], action='只给出两条记录；树尚未恢复。'))

    def split(p, q, parent=None, side=None):
        if not p:
            states.append(dict(pre=[], inorder=[], root=None, left=[], right=[],
                               links=links.copy(), built=built.copy(), action=f'{parent} 的{side}子树为空，不接入结点。'))
            return
        key = p[0]
        if key not in q:
            raise ValueError('子问题不相容')
        k = q.index(key)
        if set(p[1:1+k]) != set(q[:k]) or set(p[1+k:]) != set(q[k+1:]):
            raise ValueError('子问题不相容')
        built.append(key)
        if parent is not None:
            links.append((parent, key))
        states.append(dict(pre=list(p), inorder=list(q), root=key, left=list(q[:k]), right=list(q[k+1:]),
                           links=links.copy(), built=built.copy(),
                           action=f'根为 {key}；中序左段有 {k} 项，先序根后取 {k} 项给左子树。'))
        split(p[1:1+k], q[:k], key, '左')
        split(p[1+k:], q[k+1:], key, '右')
    if pre:
        split(pre, inorder)
    states.append(dict(pre=list(pre), inorder=list(inorder), root=None, left=[], right=[],
                       links=links.copy(), built=built.copy(), action='恢复完成；重新生成先序、中序核对原记录。'))
    return states


def player(panels, label):
    return ('<div class="tree-player" data-tree-player aria-label="' + escape(label, quote=True) + '">'
            '<div class="toolbar"><button type="button" data-step="prev">上一步</button>'
            '<button type="button" data-step="next">下一步</button>'
            '<button type="button" data-step="reset">重置</button>'
            '<span class="tree-step" aria-live="polite"></span></div>' +
            ''.join('<div class="tree-step-panel"' + (' hidden' if i else '') + '>' + panel + '</div>'
                    for i, panel in enumerate(panels)) + '</div>')


def traversal_player(children, root, diagram, mode='pre', states=None):
    states = traversal_states(children, root, mode) if states is None else states
    label = '队头 → 队尾' if mode == 'queue' else '栈底 → 栈顶' if mode == 'stack' else '调用栈：栈底 → 栈顶'
    panels = []
    for s in states:
        pending = ''.join('<li>' + escape(x) + '</li>' for x in s['pending']) or '<li>空</li>'
        content = ('<p class="trace-action">' + escape(s['action']) + '</p><div class="trace-state"><strong>' + label +
                   '</strong><ol class="trace-pending">' + pending + '</ol></div>' +
                   '<p class="trace-output">已输出：<strong>' + (' '.join(s['output']) or '空') + '</strong></p>')
        legend = '<p class="trace-legend">橙框：当前处理　蓝底：已访问'
        if mode not in ('stack', 'queue'):
            legend += '　绿框：子树完成'
        legend += '</p>'
        panels.append(beside(diagram(s), content) + legend)
    return player(panels, '遍历分步推演')


def sequence(label, items, root=None, left=(), right=()):
    out = '<div class="trace-sequence"><strong>' + escape(label) + '</strong>'
    for key in items:
        cls = 'root' if key == root else 'left' if key in left else 'right' if key in right else ''
        out += f'<span class="seq-{cls}">{escape(key)}</span>'
    return out + ('<span>空</span>' if not items else '') + '</div>'
