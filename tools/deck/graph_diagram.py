"""Accessible static general graphs; coordinates carry no metric meaning."""
from html import escape
from math import hypot


def graph(nodes, edges, *, caption, directed=False, marked=(), labels=None,
          node_details=None):
    """nodes maps IDs to (x,y); edges are endpoint pairs, labels map pairs to text.

    Thick red solid edges mark existing relationships under discussion. Directed edges
    end at the vertex boundary; no parent/child or tree assumption is made.
    """
    out = [f'<figure class="graph-figure"><svg viewBox="0 0 520 290" role="img" aria-label="{escape(caption, quote=True)}"><title>{escape(caption)}</title>']
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
        out.append(f'<g class="graph-node" data-vertex="{escape(key)}"><circle cx="{x}" cy="{y}" r="24"/><text x="{x}" y="{y+8}">{escape(key)}</text></g>')
        if node_details and key in node_details:
            out.append(f'<text class="graph-detail" x="{x}" y="{y+50}">{escape(str(node_details[key]))}</text>')
    legend = ' <span class="graph-legend">红色粗实线：关注的已有边。</span>' if has_marked_edge else ''
    return ''.join(out) + f'</svg><figcaption>{escape(caption)}{legend}</figcaption></figure>'


def beside(diagram, content):
    return '<div class="graph-layout">' + diagram + '<div>' + content + '</div></div>'
