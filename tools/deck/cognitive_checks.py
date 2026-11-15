"""Opt-in prediction concealment and optional Storyboard identity checks.

Only authored, exact result fragments and stable IDs are mechanically checked.
No semantic equivalence or learning outcomes are inferred by these checks.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unicodedata


def _plain(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()


# HTML inline formatting does not introduce a visual word boundary. Only tags
# normally creating separate blocks/lines should split neighboring text fragments.
# SVG <text> elements are individually positioned labels, unlike inline <tspan>.
TEXT_BOUNDARIES = {
    'address', 'article', 'aside', 'blockquote', 'br', 'dd', 'details', 'div',
    'dl', 'dt', 'fieldset', 'figcaption', 'figure', 'footer', 'form',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'li', 'main', 'nav',
    'ol', 'p', 'pre', 'section', 'summary', 'svg', 'table', 'tbody',
    'td', 'tfoot', 'th', 'thead', 'tr', 'ul', 'text',
}


class _InitiallyVisibleText(HTMLParser):
    """Static default-visible text; preserve continuity through inline markup."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.details = []
        self.skip = 0
        self.parts = []

    def _visible(self):
        return not self.skip and all(x['open'] or x['summary'] for x in self.details)

    def _boundary(self, tag):
        if tag in TEXT_BOUNDARIES and self._visible():
            self.parts.append(' ')

    def handle_starttag(self, tag, attrs):
        # A closed <details> is not visible except for its <summary>.
        # Separate adjacent visible text even when its contents are concealed.
        self._boundary(tag)
        if tag in {'script', 'style'}:
            self.skip += 1
        if tag == 'details':
            self.details.append({'open': 'open' in dict(attrs), 'summary': False})
        elif tag == 'summary' and self.details:
            self.details[-1]['summary'] = True

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.skip = max(0, self.skip - 1)
        if tag == 'summary' and self.details:
            self.details[-1]['summary'] = False
        elif tag == 'details' and self.details:
            self.details.pop()
        self._boundary(tag)

    def handle_data(self, data):
        if self._visible():
            self.parts.append(data)


def initially_visible(html):
    parser = _InitiallyVisibleText()
    parser.feed(html)
    return _plain(''.join(parser.parts))


def prediction_checks(course, slides):
    """Fail only explicit per-exercise withheld results that appear before disclosure."""
    results = []
    for page, slide in zip(course.pages, slides):
        key = page.get('id')
        snippets = page.get('withheld_results', ())
        if snippets in (None, (), []):
            continue
        valid = (page.get('role') == 'exercise' and isinstance(snippets, (list, tuple)) and
                 bool(snippets) and all(isinstance(s, str) and _plain(s) for s in snippets))
        if not valid:
            results.append(dict(check='prediction-outcomes/' + str(key), status='fail',
                                detail='Use nonempty result fragments on an exercise page only'))
            continue
        visible = _plain(slide[0] + ' ' + initially_visible(slide[1]))
        leaks = [s for s in snippets if _plain(s) in visible]
        results.append(dict(check='prediction-outcomes/' + str(key),
                            status='fail' if leaks else 'pass', pageId=key,
                            detail=('Declared outcome is default-visible: ' + repr(leaks) if leaks
                                    else 'Declared prediction outcomes remain outside the initial visible state')))
    return results


# D017 table convention: one stable identifier at the start of each authored row.
# No title equality or exact narrative prose comparison.
STORYBOARD_ROW = re.compile(r'^\|\s*\x60([a-z][a-z0-9_-]*)\x60\s*／', re.MULTILINE)


def storyboard_checks(deck, course):
    path = Path(deck) / 'storyboard.md'
    if not path.is_file():
        return []  # Storyboard is optional; do not migrate older decks.
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        return [dict(check='storyboard-page-ids', status='fail', detail=str(exc))]
    declared = STORYBOARD_ROW.findall(text)
    current = [p.get('id') for p in course.pages]
    unique = bool(declared) and len(declared) == len(set(declared))
    missing = [x for x in current if x not in declared]
    extra = [x for x in declared if x not in current]
    good = unique and not missing and not extra
    return [
        dict(check='storyboard-page-ids', status='pass' if good else 'fail',
             detail=('Storyboard stable IDs match the implemented pages' if good else
                     f'Duplicate/empty IDs={not unique}; missing={missing}; obsolete={extra}; '
                     'use table rows beginning with a backticked ID and ／')),
        dict(check='storyboard-page-order', status='pass' if good and declared == current else 'fail',
             detail=('Storyboard and implemented page order agree' if good and declared == current else
                     'Page order differs; update the authored Storyboard after reviewing cognitive transitions'))
    ]
