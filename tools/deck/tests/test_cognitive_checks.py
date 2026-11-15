"""D017 regressions and benign examples for cognition-aware structural checks."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from components import CourseDeck, task_workspace
from cognitive_checks import prediction_checks, storyboard_checks, initially_visible
from build import DECKS, load_deck


class CognitiveCheckTests(unittest.TestCase):
    def test_d017_authored_prediction_markers_do_not_leak(self):
        mod = load_deck(DECKS / 'd017-bst-avl')
        checks = prediction_checks(mod.COURSE, mod.SLIDES)
        self.assertEqual({c['check'] for c in checks},
                         {'prediction-outcomes/compare-path',
                          'prediction-outcomes/lr-single-fails',
                          'prediction-outcomes/update-array'})
        self.assertTrue(all(c['status'] == 'pass' for c in checks))

    def test_p1_regressions_detect_old_title_and_lead(self):
        course = CourseDeck()
        course.add('counts', '查找 55，为什么比较次数是 3 和 7？',
                   task_workspace('两棵树', '先预测比较次数', '结果分别为 3、7'),
                   role='exercise', goal='独立比较', withheld_results=('3 和 7',))
        course.add('rotate', '只做一次右旋会怎样？',
                   task_workspace('初始树', '判定单旋', '旋转后仍会失衡'),
                   role='exercise', goal='独立判断', withheld_results=('仍会失衡',))
        c = prediction_checks(course, course.slides)
        self.assertEqual([x['status'] for x in c], ['fail', 'pass'])
        course.slides[1][1] = course.slides[1][1].replace('判定单旋', '仍会失衡，请解释')
        self.assertEqual([x['status'] for x in prediction_checks(course, course.slides)],
                         ['fail', 'fail'])

    def test_closed_answer_is_not_visible_but_open_answer_and_summary_are(self):
        html = task_workspace('<p>原始数据 3,7</p>', '<p>请判断</p>',
                              '<p>最终结果是 3 和 7</p>')
        self.assertNotIn('最终结果', initially_visible(html))
        self.assertIn('原始数据', initially_visible(html))
        self.assertIn('最终结果', initially_visible(html.replace('<details ', '<details open ', 1)))
        self.assertIn('结果 3 和 7', initially_visible(
            html.replace('<summary>核对答案与理由</summary>', '<summary>结果 3 和 7</summary>')))

    def test_declared_results_only_on_exercises(self):
        c = CourseDeck()
        c.add('content', '讲解', '<p>例题</p>', goal='观察', withheld_results=('结果',))
        self.assertEqual(prediction_checks(c, c.slides)[0]['status'], 'fail')

    def test_optional_storyboard_checks_only_ids_and_order(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            course = CourseDeck()
            course.add('intro', '介绍', '<p>输入</p>', goal='建立问题')
            course.add('task', '提出问题', '<p>活动</p>', goal='探索')
            self.assertEqual(storyboard_checks(path, course), [])
            story = path/'storyboard.md'
            story.write_text('| ' + chr(96) + 'intro' + chr(96) + '／旧标题 | 入门 | 情境 | 接续 |\n'
                             '| ' + chr(96) + 'task' + chr(96) + '／候选问题 | 先修 | 活动 | 后继 |\n',
                             encoding='utf-8')
            good = storyboard_checks(path, course)
            self.assertTrue(all(c['status']=='pass' for c in good))
            story.write_text(story.read_text().replace('task', 'obsolete'),encoding='utf-8')
            self.assertTrue(any(c['status']=='fail' for c in storyboard_checks(path,course)))
            story.write_text('| ' + chr(96) + 'task' + chr(96) + '／问题 | ... |\n'
                             '| ' + chr(96) + 'intro' + chr(96) + '／介绍 | ... |\n',encoding='utf-8')
            reordered = storyboard_checks(path,course)
            self.assertEqual([c['status'] for c in reordered], ['pass','fail'])
            story.write_text('| ' + chr(96) + 'task' + chr(96) + '／问题 | ... |\n'
                             '| ' + chr(96) + 'task' + chr(96) + '／重复 | ... |\n',encoding='utf-8')
            self.assertEqual(storyboard_checks(path,course)[0]['status'],'fail')


if __name__ == '__main__':
    unittest.main()
