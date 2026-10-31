"""Exercise the source checker with source-level contract failures."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
import check


class CourseCheckTests(unittest.TestCase):
    def test_design_card_region_is_derived_and_checking_is_read_only(self):
        with tempfile.TemporaryDirectory() as name:
            deck=Path(name)
            (deck/'slides.py').write_text("""from components import CourseDeck
DECK_ID='D999'
TITLE='Fixture'
COURSE=CourseDeck()
COURSE.add('item','Question','<p>Input</p>',goal='Explain the operation')
SLIDES=COURSE.finalize()
""")
            readme=deck/'README.md'
            readme.write_text('Manual design\n'+build.PLAN_START+'\n'+build.PLAN_END+'\nManual budget\n')
            build.render(deck)
            text=readme.read_text()
            self.assertIn('| 1 | item | Question |',text)
            self.assertTrue(text.endswith('Manual budget\n'))
            readme.write_text(text.replace('| Question |','| Stale title |'))
            stale=readme.read_text()
            result=check.check_source(deck)
            self.assertTrue(any(c['check']=='design-card-page-plan' and c['status']=='fail' for c in result['checks']))
            self.assertEqual(readme.read_text(),stale)

    def test_new_lesson_cannot_silently_opt_out(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); deck = root / 'd999-new'; deck.mkdir()
            (deck/'slides.py').write_text("DECK_ID='D999'\nTITLE='New'\nSLIDES=[['Task','<p>Input</p>','Task']]\n")
            build.render(deck)
            with patch.object(check, 'ROOT', root), patch.object(check, 'DECKS', root):
                result = check.check_source(deck)
            self.assertEqual(result['contract']['status'], 'required-but-missing')
            self.assertTrue(any(c['check']=='contract-adoption' and c['status']=='fail' for c in result['checks']))
            # Copying a legacy source and forgetting its identity cannot opt out.
            source=deck/'slides.py'
            source.write_text(source.read_text().replace("DECK_ID='D999'", "DECK_ID='D001'"))
            build.render(deck)
            with patch.object(check, 'ROOT', root), patch.object(check, 'DECKS', root):
                copied=check.check_source(deck)
            self.assertEqual(copied['contract']['status'],'required-but-missing')
            self.assertTrue(any(c['check']=='deck-identity' and c['status']=='fail' for c in copied['checks']))

    def test_source_nav_mismatch_fails_even_when_generated_html_matches(self):
        with tempfile.TemporaryDirectory() as name:
            deck = Path(name)
            (deck/'slides.py').write_text("""from components import CourseDeck, Section
DECK_ID='D999'
TITLE='Fixture'
COURSE=CourseDeck([Section('task','Task','Question?','Scope')])
COURSE.outline()
COURSE.start_section('task')
SLIDES=COURSE.finalize()
SLIDES[1][0]='Different topic'
""")
            build.render(deck)
            result=check.check_source(deck)
            self.assertEqual(result['checks'][0]['status'],'pass')
            self.assertTrue(any(c['check'].startswith('section-content/') and c['status']=='fail' for c in result['checks']))


if __name__=='__main__':
    unittest.main()
