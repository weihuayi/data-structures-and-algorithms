import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from legacy_baseline import compare


def finding(**changes):
    c=dict(deck='d001-fixture',viewport='1280x720',page=2,title='Question',state='initial',
           check='projection-layout',status='fail',pageFingerprint='same-page',detail='overflow x=0, y=20')
    c.update(changes)
    return c


class LegacyComparisonTests(unittest.TestCase):
    def test_identical_findings_are_preserved_as_failures(self):
        current={'checks':[finding()]}; original=copy.deepcopy(current)
        result=compare(current,{'checks':[finding()]})
        self.assertEqual(result['status'],'existing-findings')
        self.assertEqual(result['existing'][0]['status'],'fail')
        self.assertEqual(current,original)

    def test_changed_page_or_geometry_blocks(self):
        for change in ({'pageFingerprint':'changed'}, {'detail':'overflow x=0, y=21'}, {'page':3}):
            result=compare({'checks':[finding(**change)]},{'checks':[finding()]})
            self.assertEqual(result['status'],'regressions')

    def test_resource_font_and_missing_fingerprint_cannot_be_grandfathered(self):
        for change in ({'check':'runtime-and-resources'}, {'check':'cjk-glyphs'}, {'pageFingerprint':None}, {'status':'uncovered'}):
            c=finding(**change)
            self.assertEqual(compare({'checks':[c]},{'checks':[c]})['status'],'regressions')

    def test_fixed_findings_do_not_count_as_current_failures(self):
        self.assertEqual(compare({'checks':[finding(status='pass')]},{'checks':[finding()]})['status'],'pass')


if __name__=='__main__':
    unittest.main()
