"""Accessible static general graphs; coordinates carry no metric meaning."""
from html import escape
from math import hypot


VALID_NODE_STATES = {'unseen', 'seen', 'current'}


def graph(nodes, edges, *, caption, directed=False, marked=(), labels=None,
          node_details=None, states=None, legend=None):
    """nodes maps IDs to (x,y); edges are endpoint pairs, labels map pairs to text.

    Thick red solid edges mark existing relationships under discussion. Directed edges
    end at the vertex boundary; no parent/child or tree assumption is made.
    Optional states map vertices to unseen/seen/current; optional legend overrides
    the red-edge legend and may be empty to suppress it.
    """
    out = [f'<figure class="graph-figure"><svg viewBox="0 0 520 290" role="img" aria-label="{escape(caption, quote=True)}"><title>{escape(caption)}</title>']
    states = states or {}
    for key, state in states.items():
        if key not in nodes:
            raise ValueError('State key must be a vertex')
        if state not in VALID_NODE_STATES:
            raise ValueError('Node state must be unseen, seen, or current')
    marked = set(marked)
    has_marked_edge = False
    for a, b in edges:
        x, y = nodes[a]
        xx, yy = nodes[b]
        distance = hypot(xx-x, yy-y)
        if distance == 0:
            raise ValueError('Distinct endpoint coordinates required')
        ux, uy = (xx-x)/distance, (yy-y)/distance
        sx, sy, tx, ty = x+24*ux, y+24*uy, xx-24*ux, yy-24*uy
        is_marked = (a, b) in marked or (not directed and (b, a) in marked)
        has_marked_edge |= is_marked
        cls = 'graph-edge marked' if is_marked else 'graph-edge'
        out.append(f'<g data-edge="{escape(a)}-{escape(b)}"><path class="{cls}" d="M {sx} {sy} L {tx} {ty}"/>')
        if directed:
            arrow_cls = 'graph-arrow marked' if is_marked else 'graph-arrow'
            out.append(f'<path class="{arrow_cls}" d="M {tx-12*ux+6*uy} {ty-12*uy-6*ux} L {tx} {ty} L {tx-12*ux-6*uy} {ty-12*uy+6*ux}"/>')
        if labels and (a, b) in labels:
            out.append(f'<text class="graph-label" x="{(x+xx)/2-14*uy}" y="{(y+yy)/2+14*ux}">{escape(str(labels[a,b]))}</text>')
        out.append('</g>')
    for key, (x, y) in nodes.items():
        state = states.get(key)
        cls = 'graph-node' + (f' graph-node-{state}' if state else '')
        state_attr = f' data-state="{state}"' if state else ''
        out.append(f'<g class="{cls}" data-vertex="{escape(key)}"{state_attr}><circle cx="{x}" cy="{y}" r="24"/><text x="{x}" y="{y+8}">{escape(key)}</text></g>')
        if node_details and key in node_details:
            out.append(f'<text class="graph-detail" x="{x}" y="{y+50}">{escape(str(node_details[key]))}</text>')
    legend_html = ''
    if has_marked_edge and legend != '':
        legend_text = '红色粗实线：关注的已有边。' if legend is None else legend
        if legend_text:
            legend_html = f' <span class="graph-legend">{escape(legend_text)}</span>'
    return ''.join(out) + f'</svg><figcaption>{escape(caption)}{legend_html}</figcaption></figure>'


def beside(diagram, content):
    return '<div class="graph-layout">' + diagram + '<div>' + content + '</div></div>'
