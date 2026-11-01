"""Independent assertions on the final outline, separate from its renderer."""
from html.parser import HTMLParser


class Outlines(HTMLParser):
    def __init__(self):
        super().__init__()
        self.outlines = []
        self.stack = []
        self.current = None
        self.item = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('data-course-component') == 'outline':
            self.current = dict(tag=tag, items=[], depth=len(self.stack))
            self.outlines.append(self.current)
        if self.current is not None and tag == 'li':
            self.item = dict(id=attrs.get('data-section-id'), number=[], title=[], question=[], pages=[])
            self.current['items'].append(self.item)
        field = None
        classes = attrs.get('class', '').split()
        if 'course-outline-number' in classes: field = 'number'
        if 'course-outline-pages' in classes: field = 'pages'
        if self.item is not None and tag in {'strong', 'p'}:
            field = 'title' if tag == 'strong' else 'question'
        self.stack.append((tag, field))
        if self.item is not None and field:
            self.item[field].append('')

    def handle_data(self, data):
        if self.item is not None:
            field = next((field for _, field in reversed(self.stack) if field), None)
            if field and self.item[field]:
                self.item[field][-1] += data

    def handle_endtag(self, tag):
        if not any(t == tag for t, _ in self.stack): return
        while self.stack:
            closed, _ = self.stack.pop()
            if closed == tag: break
        if tag == 'li': self.item = None
        if self.current is not None and len(self.stack) <= self.current['depth']:
            self.current = None


def outline_checks(document, course):
    parser = Outlines(); parser.feed(document)
    expected_count = sum(p['role'] == 'outline' for p in course.pages)
    valid = len(parser.outlines) == expected_count
    checks = [dict(check='outline-navigation', status='pass' if valid else 'fail',
                   detail='Exactly one ordered navigation for each declared outline page')]
    for outline in parser.outlines:
        valid = (outline['tag'] == 'ol' and
                 [item['id'] for item in outline['items']] == [s.id for s in course.sections])
        checks.append(dict(check='outline-sections', status='pass' if valid else 'fail',
                           detail='Ordered navigation contains each declared section once, in order'))
        for i, (item, section) in enumerate(zip(outline['items'], course.sections), 1):
            pages = [j for j, p in enumerate(course.pages, 1) if p['section'] == section.id]
            span = ('—' if not pages else str(pages[0]) if len(pages) == 1
                    else str(pages[0]) + '–' + str(pages[-1]))
            expected = dict(number=[f'{i:02d}'], title=[section.title],
                            question=[section.question], pages=[span + ' 页'])
            valid = all([s.strip() for s in item[key]] == value for key, value in expected.items())
            checks.append(dict(check='outline-fields/' + section.id, status='pass' if valid else 'fail',
                               detail='One sequence number, theme, question and actual page range; no repeated label column'))
    return checks
