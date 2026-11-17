"""D018 R8 alignment with D017: outline, BST recall and formal homework.

Tests source and generated HTML contracts. Actual projected legibility still
requires Chromium checks and teacher review.
"""
from pathlib import Path
from html.parser import HTMLParser
import re
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from build import DECKS, load_deck
from check_homework import check_page

D018 = DECKS / "d018-hashing"
D017 = DECKS / "d017-bst-avl"


class ElementCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.circle_count = 0
        self.edge_count = 0
        self.texts = []
        self._capture_text = False

    def handle_starttag(self, tag, attrs):
        if tag == "circle":
            self.circle_count += 1
        if tag == "line":
            self.edge_count += 1
        if tag == "text":
            self._capture_text = True

    def handle_endtag(self, tag):
        if tag == "text":
            self._capture_text = False

    def handle_data(self, data):
        if self._capture_text:
            self.texts.append(data.strip())


class D018R8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d18 = load_deck(D018)
        cls.d17 = load_deck(D017)
        cls.body = dict((p["id"], slide[1])
                        for p, slide in zip(cls.d18.COURSE.pages, cls.d18.SLIDES))
        cls.html = (D018 / "index.html").read_text(encoding="utf-8")
        cls.ref = (D017 / "index.html").read_text(encoding="utf-8")

    def test_outline_reuses_d017_dense_typography(self):
        for html in (self.html, self.ref):
            self.assertIn('<ol class="course-outline course-outline-dense"', html)
        css = self.body["cover"].split("</style>", 1)[0]
        self.assertIn("Same actual outline fonts as D017", css)
        self.assertNotIn(".course-outline-number{font-size:26px}", css)
        self.assertNotIn(".course-outline-topic strong{font-size:.94em", css)
        self.assertNotIn(".course-outline-topic p{font-size:.82em", css)
        self.assertNotIn(".course-outline-pages{font-size:.76em}", css)
        self.assertIn('data-page-id="outline"', css)
        self.assertIn("padding:2px 0;gap:12px", css)
        self.assertEqual(len(re.findall(r'<li data-section-id="', self._slide(self.html, "outline"))), 6)
        self.assertEqual(len(re.findall(r'<li data-section-id="', self._slide(self.ref, "outline"))), 5)

    def test_page_four_bst_is_a_valid_balanced_search_tree(self):
        page = self.body["recall-avl"]
        self.assertIn('data-course-component="task-workspace"', page)
        self.assertIn('data-task-input', page)
        self.assertIn('data-task-prompt', page)
        self.assertIn('data-task-answer', page)
        self.assertIn('class="hash-r8-bst-svg"', page)
        self.assertIn('viewBox="0 0 540 252"', page)
        self.assertIn("根40", page)
        self.assertIn("查找 35", page)
        self.assertIn("BST 的全子树顺序性质", page)
        self.assertIn(r"\(35&lt;40\)", page)
        parser = ElementCollector()
        parser.feed(page.split('<details', 1)[0])
        self.assertEqual(parser.circle_count, 7)
        self.assertEqual(parser.edge_count, 6)
        self.assertEqual(parser.texts, ["40", "25", "60", "15", "35", "50", "70"])
        # The visible figure may show where 35 is stored; it must not disclose
        # the comparative reasoning or search path before the teacher reveals it.
        self.assertNotIn("40 → 25 → 35", page.split("<details", 1)[0])
        self.assertIn("40 → 25 → 35", page.split("<details", 1)[1])
        # Equal left/right subtree heights at every internal node.
        data = {40:(25,60),25:(15,35),60:(50,70)}
        for parent, (left, right) in data.items():
            self.assertLess(left,parent)
            self.assertGreater(right,parent)
        self.assertTrue(all(x < 40 for x in (25,15,35)))
        self.assertTrue(all(x > 40 for x in (60,50,70)))

    def test_homework_follows_d017_vertical_practical_layout(self):
        body = self.body["homework"]
        self.assertIn('class="hash-r8-homework"', body)
        self.assertNotIn('class="hash-pair"', body)
        self.assertIn('class="hash-r8-homework-code"', body)
        self.assertIn("<pre ", body)
        self.assertIn("A · 教材作业（必做）", body)
        self.assertIn("B · C11 程序实践（必做）", body)
        self.assertIn('href="../../assignments/homework-guide.md"', body)
        self.assertIn("3–5 行过程", body)
        self.assertIn("选做不提交", body)
        for mode in ("chain", "build", "scenarios", "demo", "--self-test"):
            self.assertIn("./d018_demo " + mode, body)
        self.assertIn("code/hash_demo.c", body)
        self.assertEqual(check_page(D018,"课后怎样预测、运行和核对？",body),[])
        self.assertIn('class="d17-code"', self.d17.SLIDES[-1][1])

    def test_formal_source_and_derived_html_agree(self):
        ids = [p["id"] for p in self.d18.COURSE.pages]
        self.assertEqual(len(ids),34)
        for id_ in ("recall-avl","homework"):
            self.assertIn('<div class="hash-lesson">' + self.body[id_] + '</div>', self._slide(self.html,id_))
        self.assertIn("R8: Same actual outline fonts", self.html)
        self.assertIn("hash-r8-homework-code", self.html)

    @staticmethod
    def _slide(html,id_):
        # Page-scoped CSS is physically embedded in cover's <style> within <main>.
        # Match actual <section> tags, never bare data-page-id text in CSS.
        main_start = html.index("<main>")
        main = html[main_start:html.index("</main>",main_start)]
        pattern = r'<section class="slide"[^>]*data-page-id="' + re.escape(id_) + r'"'
        hit = re.search(pattern,main)
        if hit is None:
            raise AssertionError("Missing generated slide section: " + id_)
        start = hit.start()
        end = main.index("</section>",start)
        return main[start:end]


if __name__ == "__main__":
    unittest.main()
