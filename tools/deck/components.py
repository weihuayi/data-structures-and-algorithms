"""Small course patterns. Teaching content stays in each lesson's slides.py.

SLIDES remains a list of [title, html, label] triples. Metadata is registered at
the same call site; navigation is derived from sections and actual page order.
"""
from dataclasses import dataclass
from html import escape
import re

CONTRACT_VERSION = 1
ROLES = {'cover', 'outline', 'section', 'content', 'exercise', 'closing'}
ID = re.compile(r'^[a-z][a-z0-9_-]*$')


def number(n):
    digits = '零一二三四五六七八九'
    if 0 < n < 10:
        return digits[n]
    if 10 <= n < 100:
        tens, ones = divmod(n, 10)
        return (digits[tens] if tens > 1 else '') + '十' + (digits[ones] if ones else '')
    return str(n)


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    question: str
    scope: str
    goal: str = ''


def section_html(section):
    return ('<div class="course-section" data-course-component="section" '
            'data-section-id="' + escape(section.id, quote=True) + '">'
            '<p class="lead">' + escape(section.question) + '</p>'
            '<p class="course-section-scope">' + escape(section.scope) + '</p></div>')


def task_workspace(input_html, prompt_html, answer_html, *, title='核对答案与理由'):
    """Keep required input visible while replacing a prompt with its answer.

    HTML arguments are trusted repository content, not sanitized user input.
    The browser checker verifies the visibility contract, not answer correctness.
    """
    return ('<div class="course-workspace" data-course-component="task-workspace">'
            '<div class="course-input" data-task-input>' + input_html + '</div>'
            '<div class="course-task"><div class="course-prompt" data-task-prompt>' +
            prompt_html + '</div><details class="course-answer" data-task-answer>'
            '<summary>' + escape(title) + '</summary><div class="course-solution">' +
            answer_html + '</div></details></div></div>')


class CourseDeck:
    """Optional authoring layer; legacy lessons need no migration to build.

    No sections is a supported single-task lesson. With two or more sections,
    an outline is the default. A compact adaptation records its teaching reason
    once here, without weakening input, state or build requirements.
    """
    version = CONTRACT_VERSION

    def __init__(self, sections=(), *, navigation='standard', navigation_reason=''):
        self.sections = tuple(sections)
        self.navigation = navigation
        self.navigation_reason = navigation_reason
        self.slides = []
        self.pages = []

    def label(self, section_id):
        for index, section in enumerate(self.sections, 1):
            if section.id == section_id:
                return f'第{number(index)}部分 · {section.title}'
        raise ValueError(f'Unknown section: {section_id}')

    def add(self, page_id, title, body, *, section=None, role='content', label='',
            goal='', activity='讲述、观察与追问'):
        self.slides.append([title, body, self.label(section) if section else label])
        self.pages.append(dict(id=page_id, role=role, section=section,
                               goal=goal, activity=activity))

    def outline(self, page_id='outline', title='本讲要解决哪些问题？'):
        self.add(page_id, title, '', role='outline', label='课程路线',
                 goal='看清各部分的问题与承接关系')

    def start_section(self, section_id, *, page_id=None):
        section = next(s for s in self.sections if s.id == section_id)
        index = self.sections.index(section) + 1
        self.add(page_id or 'part-' + section_id,
                 f'第{number(index)}部分：{section.title}', section_html(section),
                 section=section_id, role='section', goal=section.goal or section.scope,
                 activity='小节转折')

    def outline_html(self):
        rows = []
        for index, section in enumerate(self.sections, 1):
            positions = [i for i, page in enumerate(self.pages, 1)
                         if page['section'] == section.id]
            span = (str(positions[0]) if len(positions) == 1 else
                    f'{positions[0]}–{positions[-1]}') if positions else '—'
            rows.append('<li data-section-id="' + escape(section.id, quote=True) + '">'
                        '<span class="course-outline-number" aria-hidden="true">' +
                        f'{index:02d}' + '</span><div class="course-outline-topic">'
                        '<strong>' + escape(section.title) + '</strong>'
                        '<p>' + escape(section.question) + '</p></div>'
                        '<span class="course-outline-pages" aria-label="页码">' +
                        span + ' 页</span></li>')
        density = ' course-outline-dense' if len(self.sections) > 4 else ''
        return ('<ol class="course-outline' + density + '" data-course-component="outline" role="list">' +
                ''.join(rows) + '</ol>')

    def finalize(self):
        for slide, page in zip(self.slides, self.pages):
            if page['role'] == 'outline':
                slide[1] = self.outline_html()
        return self.slides

    def page_plan(self):
        return [(i, slide[0], page['goal'], page['activity'])
                for i, (slide, page) in enumerate(zip(self.slides, self.pages), 1)]

    def page_plan_markdown(self):
        def cell(value):
            return str(value).replace('|', '\\|').replace('\n', ' ')
        rows = ['| 页 | 页面标识 | 标题 | 认知责任与目标 | 主要活动 |',
                '| ---: | --- | --- | --- | --- |']
        for index, (slide, page) in enumerate(zip(self.slides, self.pages), 1):
            rows.append('| ' + ' | '.join(cell(x) for x in
                        (index, page['id'], slide[0], page['goal'], page['activity'])) + ' |')
        return '\n'.join(rows)


def contract_checks(course, slides):
    """Check declared structure. Does not assess the teaching quality of text."""
    checks = []

    def add(name, ok, detail):
        checks.append(dict(check=name, status='pass' if ok else 'fail', detail=detail))

    add('contract-version', course.version == CONTRACT_VERSION,
        f'version={course.version}; supported={CONTRACT_VERSION}')
    if len(course.pages) != len(slides):
        add('page-metadata', False, 'Register every page with CourseDeck.add; metadata and SLIDES differ in length')
        return checks
    page_ids = [p.get('id') for p in course.pages]
    section_ids = [s.id for s in course.sections]
    add('page-ids', all(isinstance(x, str) and ID.fullmatch(x) for x in page_ids)
        and len(set(page_ids)) == len(page_ids), 'Stable page IDs must be unique lowercase identifiers')
    add('section-ids', all(ID.fullmatch(s.id) and s.title.strip() and s.question.strip()
                           and s.scope.strip() for s in course.sections)
        and len(set(section_ids)) == len(section_ids), 'Sections need unique IDs, a title, a question and a scope')
    add('navigation-adaptation', course.navigation == 'standard' or
        (course.navigation == 'compact' and bool(course.navigation_reason.strip())),
        'Use standard navigation, or record a teaching reason for compact navigation')
    outline_positions = [i for i, p in enumerate(course.pages) if p.get('role') == 'outline']
    required_outline = len(course.sections) >= 2 and course.navigation == 'standard'
    add('outline-presence', len(outline_positions) <= 1 and
        (not required_outline or len(outline_positions) == 1) and
        (not outline_positions or bool(course.sections)),
        'Multi-section standard lessons need one outline; single-task lessons may omit navigation')
    starts = []
    for section in course.sections:
        members = [i for i, p in enumerate(course.pages) if p.get('section') == section.id]
        section_starts = [i for i in members if course.pages[i].get('role') == 'section']
        valid = bool(members) and section_starts == members[:1] and members == list(range(members[0], members[-1] + 1))
        add('section-order/' + section.id, valid,
            'Each declared section starts once, before its content, and occupies a contiguous range')
        if section_starts:
            starts.append(section_starts[0])
    add('section-declaration-order', starts == sorted(starts), 'Page order must match the declared section order')
    for index, (slide, page) in enumerate(zip(slides, course.pages), 1):
        key = str(page.get('id', index))
        role, section = page.get('role'), page.get('section')
        add('page-role/' + key, role in ROLES and bool(str(page.get('goal', '')).strip()),
            f'page={index}; role={role}; declare a supported role and cognitive responsibility')
        valid_section = section in section_ids if section else not (course.sections and role in {'content', 'exercise', 'section'})
        add('page-section/' + key, valid_section,
            f'page={index}; content in a sectioned lesson must belong to a declared section')
        if section in section_ids:
            add('section-label/' + key, slide[2] == course.label(section),
                f'page={index}; derive the label from CourseDeck.label rather than copying it')
        if role == 'outline':
            add('outline-content/' + key, slide[1] == course.outline_html(),
                'Generate the outline from the section declaration and actual page positions')
        if role == 'section' and section in section_ids:
            s = course.sections[section_ids.index(section)]
            title = f'第{number(section_ids.index(section) + 1)}部分：{s.title}'
            add('section-content/' + key, slide[0] == title and slide[1] == section_html(s),
                'Use start_section so its title, question and scope share the course pattern')
        if role in {'cover', 'outline'}:
            add('navigation-position/' + key, section is None and (not starts or index - 1 < min(starts)),
                'Cover and outline precede the section content')
        if role == 'closing' and section is None:
            members = [i for i, p in enumerate(course.pages) if p.get('section') in section_ids]
            add('closing-position/' + key, not members or index - 1 > max(members),
                'Unsectioned closing pages follow the declared sections')
        if role == 'exercise':
            add('exercise-input/' + key, 'data-course-component="task-workspace"' in slide[1]
                and 'data-task-input' in slide[1] and 'data-task-prompt' in slide[1]
                and 'data-task-answer' in slide[1],
                'Use task_workspace to separate required input, prompt and answer; review meaning manually')
    return checks
