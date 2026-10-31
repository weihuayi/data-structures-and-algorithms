"""Inspect complete rendered page frames, independently of component strings."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import DECKS, EXAMPLES, load_deck, render_document
from headers import header_checks


class Text(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.text = ''; self.feed(html)

    def handle_data(self, data):
        self.text += data


def frames(html):
    result = []
    for section in html.split('<section class="slide"')[1:]:
        header = section.split('</h2>', 1)[0]
        title = Text(header.split('<h2>', 1)[1]).text
        kickers = [Text(s).text for s in re.findall(r'<p class="kicker">(.*?)</p>', header)]
        result.append(dict(title=title, kickers=kickers, section='data-role="section"' in header))
    return result


class HeadingPresentationTests(unittest.TestCase):
    def render_legacy(self, title, label):
        with tempfile.TemporaryDirectory() as folder:
            deck = Path(folder)
            (deck/'slides.py').write_text("DECK_ID='D999'\nTITLE='Fixture'\nSLIDES=" +
                                         repr([[title, '<p>Input</p>', label]]) + '\n')
            return frames(render_document(deck)[0])[0]

    def test_d014_section_frames_have_one_heading_without_kicker(self):
        deck = DECKS/'d014-shortest-path'
        course = load_deck(deck).COURSE
        rendered = frames(render_document(deck)[0])
        for page, slide, frame in zip(course.pages, course.slides, rendered):
            if page['role'] == 'section':
                with self.subTest(page=page['id']):
                    self.assertEqual(frame['kickers'], [])
                    self.assertEqual(frame['title'], slide[0])
                    self.assertTrue(slide[2], 'Context metadata remains available')

    def test_public_pattern_section_frames_do_not_repeat_context(self):
        for frame in frames(render_document(EXAMPLES/'patterns')[0]):
            if frame['section']:
                with self.subTest(title=frame['title']):
                    self.assertEqual(frame['kickers'], [])

    def test_legacy_prefix_separator_and_width_variants_are_collapsed(self):
        for title, label in [('第一部分：任务', '第一部分 · 任务'),
                             ('补充：扩展存储', '补充 · 扩展存储'),
                             ('第１节：任务', '第1节 · 任务')]:
            with self.subTest(title=title):
                self.assertEqual(self.render_legacy(title, label)['kickers'], [])

    def test_distinct_context_and_local_question_remain_visible(self):
        frame = self.render_legacy('怎样更新最短距离？', '第二部分 · 最短路径')
        self.assertEqual(frame['kickers'], ['第二部分 · 最短路径'])
        self.assertEqual(frame['title'], '怎样更新最短距离？')

    def test_meaningful_punctuation_symbols_and_word_spaces_are_preserved(self):
        for title, label in [('xy', 'x-y'), ('ab', 'a/b'), ('R', 'ℝ'),
                             ('AB', 'A B'), ('选择条件一', '选择（条件一）')]:
            with self.subTest(title=title, label=label):
                self.assertEqual(self.render_legacy(title, label)['kickers'], [label])

    def test_html_audit_rejects_hidden_and_empty_frame_copies(self):
        for kicker in ['<p class="kicker" style="display:none">第一部分 · 任务</p>',
                       '<p class="kicker"></p>']:
            document = ('<section class="slide" data-role="section" data-page-id="part-task">'
                        '<div class="slide-inner">' + kicker + '<h2>第一部分：任务</h2></div></section>')
            failures = [c for c in header_checks(document) if c['status'] == 'fail']
            self.assertTrue(any(c['check']=='heading-structure/part-task' for c in failures))
        self.assertTrue(any(c['check']=='header-redundancy/part-task' for c in header_checks(
            '<section class="slide" data-page-id="part-task"><div class="slide-inner">'
            '<p class="kicker">第一部分 · 任务</p><h2>第一部分：任务</h2></div></section>') if c['status']=='fail'))

    def test_html_audit_keeps_exhibit_headings_out_of_page_frame(self):
        document = ('<section class="slide"><div class="slide-inner"><p class="kicker">第一部分 · 图</p>'
                    '<h2>怎样更新距离？</h2><div class="slide-inner"><h2>图的说明</h2><p class="kicker">图的说明</p></div>'
                    '</div></section>')
        self.assertTrue(all(c['status']=='pass' for c in header_checks(document)))


if __name__ == '__main__':
    unittest.main()
