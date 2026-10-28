"""Accessible static general graphs; coordinates carry no metric meaning."""
from html import escape
from math import hypot, isfinite


VALID_NODE_STATES = {'unvisited', 'visited', 'current', 'examined'}


def graph(nodes, edges, *, caption, directed=False, marked=(), labels=None,
          node_details=None, states=None, legend=None, candidate=(), rejected=(),
          label_positions=None, edge_notes=None, edge_note_positions=None,
          view_box=(0, 0, 520, 290), regions=()):
    """nodes maps IDs to (x,y); edges are endpoint pairs, labels map pairs to text.

    Thick red solid edges mark existing relationships under discussion. Directed edges
    end at the vertex boundary; no parent/child or tree assumption is made.
    Optional states map vertices to unvisited/visited/current; optional legend overrides
    the red-edge legend and may be empty to suppress it.
    view_box may crop unused space. regions are explicit background polygons with
    points, label and label_position; their geometry is supplied by the lesson.
    """
    if (len(view_box) != 4 or not all(isfinite(x) for x in view_box)
            or view_box[2] <= 0 or view_box[3] <= 0):
        raise ValueError('view_box must have finite coordinates and positive dimensions')
    box = ' '.join(str(x) for x in view_box)
    out = [f'<figure class="graph-figure"><svg viewBox="{box}" role="img" aria-label="{escape(caption, quote=True)}"><title>{escape(caption)}</title>']
    for region in regions:
        points = region['points']
        lx, ly = region['label_position']
        if (len(points) < 3 or not all(isfinite(v) for point in points for v in point)
                or not isfinite(lx) or not isfinite(ly)):
            raise ValueError('A region needs at least three finite points and a finite label position')
        coords = ' '.join(f'{x},{y}' for x, y in points)
        out.append(f'<g class="graph-region"><polygon points="{coords}"/>'
                   f'<text x="{lx}" y="{ly}">{escape(region["label"])}</text></g>')
    states = states or {}
    for key, state in states.items():
        if key not in nodes:
            raise ValueError('State key must be a vertex')
        if state not in VALID_NODE_STATES:
            raise ValueError('Node state must be unvisited, visited, current, or examined')
    marked = set(marked)
    candidate = set(candidate)
    rejected = set(rejected)
    has_highlight = False
    for a, b in edges:
        x, y = nodes[a]
        xx, yy = nodes[b]
        distance = hypot(xx-x, yy-y)
        if distance == 0:
            raise ValueError('Distinct endpoint coordinates required')
        ux, uy = (xx-x)/distance, (yy-y)/distance
        sx, sy, tx, ty = x+24*ux, y+24*uy, xx-24*ux, yy-24*uy
        is_marked = (a, b) in marked or (not directed and (b, a) in marked)
        is_candidate = (a, b) in candidate or (not directed and (b, a) in candidate)
        is_rejected = (a, b) in rejected or (not directed and (b, a) in rejected)
        has_highlight |= is_marked or is_candidate or is_rejected
        cls = 'graph-edge'
        if is_marked: cls += ' marked'
        if is_candidate: cls += ' candidate'
        if is_rejected: cls += ' rejected'
        out.append(f'<g data-edge="{escape(a)}-{escape(b)}"><path class="{cls}" d="M {sx} {sy} L {tx} {ty}"/>')
        if directed:
            arrow_cls = 'graph-arrow marked' if is_marked else 'graph-arrow'
            out.append(f'<path class="{arrow_cls}" d="M {tx-12*ux+6*uy} {ty-12*uy-6*ux} L {tx} {ty} L {tx-12*ux-6*uy} {ty-12*uy+6*ux}"/>')
        if labels and (a, b) in labels:
            if label_positions and (a, b) in label_positions:
                lx, ly = label_positions[(a, b)]
            else:
                lx, ly = (x+xx)/2-14*uy, (y+yy)/2+14*ux
            out.append(f'<text class="graph-label" x="{lx}" y="{ly}">{escape(str(labels[a,b]))}</text>')
        if edge_notes and (a, b) in edge_notes:
            if edge_note_positions and (a, b) in edge_note_positions:
                nx, ny = edge_note_positions[(a, b)]
            else:
                # Default: near the source end, clear of a midpoint weight label.
                nx = x + 0.14*(xx-x) + 22*uy
                ny = y + 0.14*(yy-y) - 22*ux
            out.append(f'<text class="graph-edge-note" x="{nx}" y="{ny}">{escape(str(edge_notes[a,b]))}</text>')
        out.append('</g>')
    for key, (x, y) in nodes.items():
        state = states.get(key)
        cls = 'graph-node' + (f' graph-node-{state}' if state else '')
        state_attr = f' data-state="{state}"' if state else ''
        out.append(f'<g class="{cls}" data-vertex="{escape(key)}"{state_attr}><circle cx="{x}" cy="{y}" r="24"/><text x="{x}" y="{y+8}">{escape(key)}</text></g>')
        if node_details and key in node_details:
            out.append(f'<text class="graph-detail" x="{x}" y="{y+50}">{escape(str(node_details[key]))}</text>')
    legend_html = ''
    if has_highlight and legend != '':
        legend_text = '红色粗实线：关注的已有边。' if legend is None else legend
        if legend_text:
            legend_html = f' <span class="graph-legend">{escape(legend_text)}</span>'
    return ''.join(out) + f'</svg><figcaption>{escape(caption)}{legend_html}</figcaption></figure>'


def beside(diagram, content):
    return '<div class="graph-layout">' + diagram + '<div>' + content + '</div></div>'
