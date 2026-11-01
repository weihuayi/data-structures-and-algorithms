"""D016 bounded classroom search traces and views.

Cost is records whose keys were examined, not C relational operators.
Trace construction validates inputs once; C query routines require preconditions.
All algorithm states preserve the input. Main ASL profiles use distinct keys.
"""
from fractions import Fraction
from html import escape
from numbers import Integral
from tree_diagram import tree
from tree_trace import player

KEYS = (5, 16, 20, 27, 30, 36, 44, 55, 60, 67, 71)
BLOCKS = ((16, 5, 20), (36, 27, 30), (44, 71, 55, 67, 60))
MISS_KEYS = (4, 10, 18, 23, 28, 33, 40, 49, 57, 63, 69, 72)
UNIFORM = (Fraction(1, 11),) * 11
HOT_FIRST = (Fraction(4, 5),) + (Fraction(1, 50),) * 10


def integers(values):
    values = tuple(values)
    if any(not isinstance(v, Integral) or isinstance(v, bool) for v in values):
        raise ValueError('Integer keys required')
    return values


def search_states(values=KEYS, key=27, *, mode='binary'):
    values = integers(values)
    integers((key,))
    if mode not in {'binary', 'sequential'}:
        raise ValueError('Unknown search mode')
    if mode == 'binary' and any(a > b for a, b in zip(values, values[1:])):
        raise ValueError('Binary input must be nondecreasing')
    lo, hi, probes, checked = 0, len(values)-1, 0, ()
    states = []

    def emit(phase, action, mid=None, result=None):
        states.append(dict(values=values, key=key, mode=mode, low=lo, high=hi,
                           mid=mid, probes=probes, checked=checked,
                           result=result, phase=phase, action=action))
    emit('ready', '给定关键字 '+str(key)+'；尚未比较记录。')
    while lo <= hi:
        mid = lo + (hi-lo)//2 if mode == 'binary' else lo
        probes += 1
        checked += (mid,)
        emit('compare', f'比较 A[{mid}]={values[mid]} 与 {key}；本次计 1 个关键字。', mid)
        if values[mid] == key:
            emit('found', f'关键字相等，命中下标 {mid}。', mid, mid)
            return states
        if mode == 'sequential':
            lo = mid+1
            action = f'A[{mid}] 不等于 {key}，继续检查下一个记录。'
        elif values[mid] < key:
            old = lo
            lo = mid+1
            action = f'{values[mid]}<{key}，下标 {old}–{mid} 均不可能命中；low={lo}。'
        else:
            old = hi
            hi = mid-1
            action = f'{values[mid]}>{key}，下标 {mid}–{old} 均不可能命中；high={hi}。'
        emit('update', action)
    emit('miss', '候选区间为空，确认不存在，返回 −1。', result=-1)
    return states


def mean_cost(costs, probabilities):
    costs, probabilities = tuple(costs), tuple(Fraction(p) for p in probabilities)
    if any(not isinstance(c, Integral) or isinstance(c, bool) or c < 0 for c in costs):
        raise ValueError('Nonnegative integer costs required')
    if not costs or len(costs) != len(probabilities) or any(p < 0 for p in probabilities) or sum(probabilities) != 1:
        raise ValueError('One nonnegative probability per outcome; sum must be 1')
    return sum(c*p for c, p in zip(costs, probabilities))


def successful_costs(values=KEYS, *, mode='binary'):
    values = integers(values)
    if not values or len(set(values)) != len(values):
        raise ValueError('Per-record success profile needs nonempty distinct keys')
    return tuple(search_states(values, k, mode=mode)[-1]['probes'] for k in values)


def decision_model(values=KEYS):
    values = integers(values)
    if any(a >= b for a, b in zip(values, values[1:])):
        raise ValueError('Decision profile requires strictly increasing keys')
    nodes, edges, gaps = {}, [], {}

    def visit(lo, hi, depth, parent=None):
        if lo > hi:
            gaps[lo] = depth-1
            return
        mid = lo+(hi-lo)//2
        nodes[mid] = dict(key=values[mid], depth=depth, low=lo, high=hi)
        if parent is not None:
            edges.append((parent, mid))
        visit(lo, mid-1, depth+1, mid)
        visit(mid+1, hi, depth+1, mid)
    visit(0, len(values)-1, 1)
    return dict(nodes=nodes, edges=edges, gaps=gaps)


def array_view(values=KEYS, *, low=None, high=None, current=None, found=None,
               checked=(), caption='数组中显示关键字；下标从 0 开始。'):
    values = tuple(values)
    if not values:
        return '<div class="search-empty" data-search-array data-size="0">空表：没有可读取的数组元素。</div>'
    states = []
    for i in range(len(values)):
        cls = []
        if low is not None:
            cls.append('candidate' if low <= i <= high else 'excluded')
        if i in checked:
            cls.append('checked')
        if i == current:
            cls.append('current')
        if i == found:
            cls.append('found')
        states.append(' '.join(cls))
    row = lambda tag, data: ''.join(
        f'<{tag} data-index="{i}" class="{states[i]}">{escape(str(value))}</{tag}>'
        for i, value in enumerate(data))
    return ('<figure class="search-array-figure"><table class="search-array" data-search-array '
            f'data-size="{len(values)}"><tbody><tr><th scope="row">下标</th>'+row('th', range(len(values)))+
            '</tr><tr><th scope="row">关键字</th>'+row('td', values)+'</tr></tbody></table>'
            '<figcaption>'+escape(caption)+'</figcaption></figure>')


def snapshot(s):
    result = '尚未返回' if s['result'] is None else (
        '返回 −1：不存在' if s['result'] == -1 else f"返回 {s['result']}：命中")
    attrs = ' '.join(f'data-search-{k}="{escape(str(s[k]), quote=True)}"'
                     for k in ('phase', 'low', 'high', 'mid', 'probes', 'result'))
    interval = '空' if s['low'] > s['high'] else f"[{s['low']}, {s['high']}]"
    return (f'<div class="search-snapshot" {attrs}>'+
            array_view(s['values'], low=s['low'], high=s['high'], current=s['mid'],
                       found=s['result'] if s['phase']=='found' else None, checked=s['checked'])+
            '<p class="search-action">'+escape(s['action'])+'</p>'+
            '<div class="search-counters">'+
            f'<span>候选区间：{interval}</span><span>low={s["low"]}，high={s["high"]}</span>'+
            f'<span>已比较关键字：{s["probes"]} 个</span><span>{result}</span></div>'+
            '<p class="search-note">蓝底：候选；灰底：排除；橙框：当前比较；绿框：命中。含义同时由区间、动作和结果说明。</p></div>')


def search_player(key, *, values=KEYS, mode='binary'):
    states = search_states(values, key, mode=mode)
    return '<div class="search-player">'+player([snapshot(s) for s in states],
        ('折半' if mode=='binary' else '顺序')+f'查找 {key} 的过程')+'</div>'


def decision_view(values=KEYS, *, caption=None):
    values = tuple(values)
    model = decision_model(values)
    width = max(550, 160+84*max(1, len(values)))
    nodes = {str(i): (130+84*i, 40+70*(s['depth']-1), str(s['key']), '')
             for i, s in model['nodes'].items()}
    height = 70*max((s['depth'] for s in model['nodes'].values()), default=1)+20
    return '<div class="search-decision">'+tree(nodes, [(str(a),str(b)) for a,b in model['edges']],
        caption=caption or '结点标关键字；层数从 1 开始，等于成功查找所比较的关键字个数。判定树用于分析，不另建树来执行本数组查找。',
        levels=True, width=width, height=height)+'</div>'


def gap_view(values=KEYS):
    values = tuple(values)
    if not values:
        return '<div class="search-gaps"><div data-gap="0" data-cost="0"><strong>任意关键字</strong><span>空表：比较 0 次</span></div></div>'
    model = decision_model(values)
    out = []
    for i in range(len(values)+1):
        label = f'k<{values[0]}' if i==0 else f'k>{values[-1]}' if i==len(values) else f'{values[i-1]}<k<{values[i]}'
        out.append(f'<div data-gap="{i}" data-cost="{model["gaps"][i]}"><strong>{escape(label)}</strong>'
                   f'<span>比较 {model["gaps"][i]} 次</span></div>')
    return '<div class="search-gaps">'+''.join(out)+'</div>'


def block_model(blocks=BLOCKS):
    blocks = tuple(integers(b) for b in blocks)
    if not blocks or any(not b for b in blocks):
        raise ValueError('Nonempty blocks required')
    if any(len(set(b)) != len(b) for b in blocks) or any(
            max(a) >= min(b) for a,b in zip(blocks, blocks[1:])):
        raise ValueError('Distinct keys and max(previous)<min(next) required')
    starts, total = [], 0
    for block in blocks:
        starts.append(total); total += len(block)
    return dict(blocks=blocks, values=sum(blocks, ()), starts=tuple(starts),
                maxima=tuple(max(b) for b in blocks))


def index_view(blocks=BLOCKS, *, current=None, selected=None):
    m = block_model(blocks)
    rows = []
    for i, (maximum, start) in enumerate(zip(m['maxima'], m['starts'])):
        cls = 'current' if current==i else 'found' if selected==i else ''
        rows.append(f'<tr data-block="{i}" class="{cls}"><th scope="row">B{i+1}</th><td>{maximum}</td><td>{start}</td><td>{start+len(m["blocks"][i])-1}</td></tr>')
    return ('<table class="search-index"><thead><tr><th>块名</th><th>最大关键字</th><th>起始下标</th><th>结束下标</th></tr></thead><tbody>'+
            ''.join(rows)+'</tbody></table>')


def block_states(blocks=BLOCKS, key=30):
    m = block_model(blocks); integers((key,))
    states = []
    ip, rp, chosen, current, checked = 0, 0, None, None, ()

    def emit(phase, action, result=None, index=None):
        states.append(dict(model=m, key=key, phase=phase, action=action, result=result,
                           index_probes=ip, record_probes=rp, selected=chosen,
                           current=current, checked=checked, index=index))
    emit('ready', f'查找 {key}：先确定所在块，再检查块内记录。')
    for i, maximum in enumerate(m['maxima']):
        ip += 1
        emit('index', f'比较 {key} 与 B{i+1} 的最大关键字 {maximum}。', index=i)
        if key <= maximum:
            chosen = i
            emit('select', f'这是第一个最大关键字不小于 {key} 的块；若目标存在，就在 B{i+1}。')
            start = m['starts'][i]
            for j, value in enumerate(m['blocks'][i], start):
                current = j; rp += 1; checked += (j,)
                emit('compare', f'比较 A[{j}]={value}；块内无序，不根据大小提前停止。')
                if value == key:
                    emit('found', f'命中 A[{j}]，返回整表下标 {j}。', j)
                    return states
            current = None
            emit('miss', '本块全部检查仍未命中；其他块已由块间范围排除，返回 −1。', -1)
            return states
    emit('miss', '目标大于全部索引最大值，无需检查块内记录，返回 −1。', -1)
    return states


def block_snapshot(s):
    m = s['model']; chosen = s['selected']
    low = m['starts'][chosen] if chosen is not None else None
    high = low+len(m['blocks'][chosen])-1 if low is not None else None
    result = '尚未返回' if s['result'] is None else f'返回 {s["result"]}'
    attrs = ' '.join(f'data-block-{k}="{s[k]}"' for k in ('phase','selected','index_probes','record_probes','result'))
    return (f'<div class="search-block-snapshot" {attrs}>'+
            '<div class="search-block-head">'+index_view(m['blocks'], current=s['index'], selected=chosen)+
            '<p class="search-note">先找第一个最大关键字 ≥ 目标的索引项。<br>块名 B1–B3；记录下标从 0 开始。</p></div>'+
            array_view(m['values'], low=low, high=high, current=s['current'],
                       found=s['result'] if s['phase']=='found' else None, checked=s['checked'],
                       caption='原表完整保留；蓝底为选定块，橙框为当前记录，绿框为命中。')+
            '<p class="search-action">'+escape(s['action'])+'</p>'+
            f'<p class="search-note">索引比较 {s["index_probes"]} 次；记录比较 {s["record_probes"]} 次；{result}。</p></div>')


def block_player(key=30):
    return '<div class="search-player">'+player([block_snapshot(s) for s in block_states(key=key)],
                                               f'分块查找 {key}')+'</div>'
