import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dependencies import dependency_manifest
from impact import analyze


class DependencyTests(unittest.TestCase):
    def test_package_initializers_and_relative_imports_are_included(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name); deck=root/'lesson'; deck.mkdir()
            package=deck/'pkg'; package.mkdir()
            (deck/'slides.py').write_text('from pkg import engine\n')
            (package/'__init__.py').write_text('')
            (package/'engine.py').write_text('from . import data\n')
            (package/'data.py').write_text('WEIGHT=0\n')
            files=dependency_manifest(deck,document='',root=root)['files']
            self.assertTrue({'lesson/pkg/__init__.py','lesson/pkg/engine.py','lesson/pkg/data.py'} <= set(files))

    def test_shared_css_and_import_change_fingerprint_without_html_change(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); deck = root / 'course/decks/test'; deck.mkdir(parents=True)
            (deck / 'slides.py').write_text('from helper import DATA\n')
            helper = deck / 'helper.py'; helper.write_text('DATA=1\n')
            assets = root / 'assets'; assets.mkdir()
            css = assets / 'shared.css'; css.write_text('body{font-size:24px}')
            html = '<link rel="stylesheet" href="../../../assets/shared.css">'
            a = dependency_manifest(deck, document=html, root=root)
            css.write_text('body{font-size:2px}')
            b = dependency_manifest(deck, document=html, root=root)
            self.assertNotEqual(a['sha256'], b['sha256'])
            self.assertEqual(a['files']['course/decks/test/slides.py'], b['files']['course/decks/test/slides.py'])
            helper.write_text('DATA=2\n')
            c = dependency_manifest(deck, document=html, root=root)
            self.assertNotEqual(b['sha256'], c['sha256'])
            self.assertIn('course/decks/test/helper.py', c['files'])

    def test_css_fonts_missing_assets_and_explicit_dependencies(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name); deck=root/'lesson'; deck.mkdir()
            (deck/'slides.py').write_text('SLIDES=[]')
            (root/'font.woff2').write_bytes(b'font')
            (root/'style.css').write_text('@font-face{src:url(font.woff2)}')
            (root/'input.json').write_text(json.dumps({'weight':0}))
            result=dependency_manifest(deck,document='<link href="../style.css"><img src="missing.png">',
                                       extra=['input.json'],root=root)
            self.assertIn('font.woff2',result['files'])
            self.assertIn('input.json',result['files'])
            self.assertIn('lesson/missing.png',result['missing'])

    def test_components_do_not_force_legacy_migration(self):
        impact=analyze(['tools/deck/components.css'])
        self.assertIn('D014',impact['full'])
        self.assertNotIn('D013',impact['defaults'])
        global_change=analyze(['tools/deck/deck.css'])
        self.assertIn('D013',global_change['defaults'])
        self.assertIn('D014',global_change['full'])

    def test_local_revision_is_scoped_and_unknown_shared_changes_expand(self):
        impact=analyze(['course/decks/d014-shortest-path/README.md'])
        self.assertEqual(impact['full'],['D014'])
        self.assertEqual(impact['defaults'],[])
        expanded=analyze(['tools/deck/new-shared-module.py'])
        self.assertEqual(len(expanded['full'])+len(expanded['defaults']),14)


if __name__ == '__main__':
    unittest.main()
