"""Static, accessible SVG tree diagrams for HTML decks (no browser dependency)."""
from html import escape


def tree(nodes, edges, *, caption, focus=(), marked_edges=(), levels=False,
         regions=(), width=600, height=340, visited=(), completed=(), edge_labels=None, level_start=1):
    """nodes: id -> (x, y, label, detail); edges are unarrowed parent-child pairs."""
    out = [f'<figure class="tree-figure"><svg class="tree-diagram" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(caption, quote=True)}"><title>{escape(caption)}</title>']
    for x, y, w, h, label in regions:
        out.append(f'<rect class="tree-region" x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/><text class="tree-detail" x="{x+w/2}" y="{y+h-12}">{escape(label)}</text>')
    if levels:
        for i, y in enumerate(sorted({v[1] for v in nodes.values()}), level_start):
            out.append(f'<line class="tree-level" x1="12" y1="{y}" x2="{width-12}" y2="{y}"/><text class="tree-detail" x="45" y="{y-26}">第 {i} 层</text>')
    for a, b in edges:
        x1, y1 = nodes[a][:2]
        x2, y2 = nodes[b][:2]
        cls = 'tree-edge focus' if (a, b) in marked_edges else 'tree-edge'
        out.append(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    for (a, b), label in (edge_labels or {}).items():
        x1, y1 = nodes[a][:2]
        x2, y2 = nodes[b][:2]
        out.append(f'<text class="tree-edge-label" x="{(x1+x2)/2+12}" y="{(y1+y2)/2}">{escape(str(label))}</text>')
    for key, (x, y, label, detail) in nodes.items():
        cls = 'tree-node focus' if key in focus else 'tree-node'
        if key in visited:
            cls += ' visited'
        if key in completed:
            cls += ' completed'
        if label == 'NULL':
            cls += ' vacant'
        out.append(f'<g class="{cls}"><rect x="{x-34}" y="{y-23}" width="68" height="46" rx="13"/><text x="{x}" y="{y+8}">{escape(label)}</text></g>')
        if detail:
            out.append(f'<text class="tree-detail" x="{x}" y="{y+47}">{escape(detail)}</text>')
    out.append(f'</svg><figcaption>{escape(caption)}</figcaption></figure>')
    return ''.join(out)


def beside(diagram, content):
    return '<div class="tree-layout">' + diagram + '<div class="tree-explain">' + content + '</div></div>'


def gallery(*items):
    return '<div class="tree-gallery">' + ''.join(items) + '</div>'
