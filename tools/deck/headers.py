"""Page-frame responsibilities and conservative, exact header comparison."""
from html import escape
from html.parser import HTMLParser
import re

PREFIX = re.compile(r'^(第[0-9零〇一二三四五六七八九十百两]+(?:部分|节|章)|补充)\s*[·:]\s*')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class PlainText(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.parts = []; self.feed(html)

    def handle_data(self, data):
        self.parts.append(data)


def header_key(text):
    """Fold ASCII fullwidth/space and known section-prefix separators only.

    Preserve word boundaries, operators, other punctuation, case and mathematical
    alphabets: x-y != xy, A B != AB, and double-struck R != R.
    """
    text = ''.join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E
                   else ' ' if c == '\u3000' else c for c in text)
    text = ' '.join(text.split())
    return PREFIX.sub(lambda match: match[1] + ':', text, count=1)


def same_header(label, title):
    left, right = header_key(label), header_key(title)
    return bool(left) and left == right


def render_header(title, context, *, role=None):
    """Keep full context in source metadata; render it only when informative."""
    title_text = ''.join(PlainText(title).parts)
    show_context = role != 'section' and context.strip() and not same_header(context, title_text)
    kicker = '<p class="kicker">' + escape(context) + '</p>' if show_context else ''
    return kicker + '<h2>' + title + '</h2>'


class PageHeaders(HTMLParser):
    """Read only direct page-frame headings, not headings in teaching exhibits."""
    def __init__(self, document):
        super().__init__(); self.pages = []; self.stack = []; self.page = None
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); classes = attrs.get('class', '').split()
        if tag == 'section' and 'slide' in classes:
            self.page = dict(page=len(self.pages) + 1, pageId=attrs.get('data-page-id'),
                             role=attrs.get('data-role'), titles=[], kickers=[])
            self.pages.append(self.page)
            self.stack = []
        node = dict(tag=tag, root=tag == 'section' and 'slide' in classes,
                    inner=tag == 'div' and 'slide-inner' in classes and bool(self.stack)
                    and self.stack[-1].get('root', False))
        if self.page is not None and self.stack and self.stack[-1]['inner']:
            field = 'titles' if tag == 'h2' else 'kickers' if tag == 'p' and 'kicker' in classes else None
            if field:
                self.page[field].append('')
                node['capture'] = (self.page, field, len(self.page[field]) - 1)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                del self.stack[index:]
                break
        if tag == 'section':
            self.page = None

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        for node in reversed(self.stack):
            if 'capture' in node:
                page, field, index = node['capture']
                page[field][index] += data
                break


def header_checks(document):
    checks = []
    for page in PageHeaders(document).pages:
        titles, kickers = page['titles'], page['kickers']
        key = page['pageId'] or str(page['page'])
        structure = len(titles) == 1 and bool(titles[0].strip()) and len(kickers) <= 1 and all(k.strip() for k in kickers)
        if page['role'] == 'section':
            structure = structure and not kickers
        common = {k: page[k] for k in ('page', 'pageId', 'role')}
        checks.append(dict(**common, check='heading-structure/' + key,
                           status='pass' if structure else 'fail',
                           detail='Use one frame h2; section starts omit the kicker node, including hidden/empty copies'))
        duplicate = any(same_header(k, title) for k in kickers for title in titles)
        checks.append(dict(**common, check='header-redundancy/' + key,
                           status='fail' if duplicate else 'pass',
                           detail='Context and main heading must not repeat the same text; preserve context metadata and fix the common frame renderer'))
    return checks
