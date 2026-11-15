"""Summaries locate new browser failures without erasing known historical ones."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify import diagnostic_summary


class DiagnosticSummaryTests(unittest.TestCase):
    def test_browser_failure_has_stable_page_location_and_screenshot(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            full=root/'adopted-full'; full.mkdir()
            (full/'browser-report.json').write_text(json.dumps({
                'status':'fail','checks':[
                    {'deck':'d017-bst-avl','page':9,'pageId':'bst-insert',
                     'viewport':'1280x720','state':'initial','check':'projection-layout',
                     'status':'fail','detail':'overflow x=0, y=42',
                     'screenshot':'d017-1280x720-p9.png'},
                    {'deck':'d017-bst-avl','page':14,'pageId':'two-builds',
                     'viewport':'1280x720','state':'initial','check':'projection-layout',
                     'status':'fail','detail':'overflow x=0, y=5'}
                ]
            }),encoding='utf-8')
            out=diagnostic_summary(root,[{'name':'adopted-full','returncode':1}])
            self.assertEqual(out['blockingCount'],2)
            self.assertEqual(out['historicalCount'],0)
            self.assertEqual(out['blocking'][0]['pageId'],'bst-insert')
            self.assertEqual(out['blocking'][0]['viewport'],'1280x720')
            self.assertEqual(out['blocking'][0]['evidence'],'adopted-full/d017-1280x720-p9.png')

    def test_historical_failure_is_kept_separate_and_raw_result_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); old=root/'legacy-defaults'; old.mkdir()
            (old/'browser-report.json').write_text(json.dumps({'checks':[
                {'deck':'d001-problem-representation','page':2,'pageId':None,
                 'viewport':'1280x720','state':'initial','check':'projection-layout',
                 'detail':'overflow y=89','status':'fail'}]}),encoding='utf-8')
            runs=[{'name':'legacy-defaults','returncode':1,
                   'classification':'existing-layout-findings; raw exit code preserved'}]
            out=diagnostic_summary(root,runs)
            self.assertEqual(out['historicalCount'],1)
            self.assertFalse(out['blocking'])
            self.assertEqual(runs[0]['returncode'],1)

    def test_missing_report_does_not_disappear_and_samples_are_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            out=diagnostic_summary(Path(folder),[{'name':'semantic','returncode':1}])
            self.assertEqual(out['blockingCount'],1)
            self.assertEqual(out['blocking'][0]['evidence'],'semantic.log')
            full=Path(folder)/'adopted-full';full.mkdir()
            (full/'browser-report.json').write_text(json.dumps({'checks':[
                {'status':'fail','check':'fake'} for _ in range(15)]}),encoding='utf-8')
            result=diagnostic_summary(Path(folder),[{'name':'adopted-full','returncode':1}],sample_limit=3)
            self.assertEqual(result['blockingCount'],15)
            self.assertEqual(len(result['blocking']),3)
            self.assertEqual(result['omitted'],12)


if __name__ == '__main__':
    unittest.main()
