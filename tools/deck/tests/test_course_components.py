"""Structural invariants, supported variation and deliberate broken inputs."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from components import CourseDeck, Section, contract_checks, task_workspace
from build import EXAMPLES, load_deck, render_document


def lesson(count=2):
    course = CourseDeck([Section(f's{i}', f'任务{i}', f'怎样完成任务{i}？', '解释一步。')
                         for i in range(count)])
    course.outline()
    for section in course.sections:
        course.start_section(section.id)
        course.add('work-' + section.id, '预测一步', '<p>必要输入</p>',
                   section=section.id, goal='解释本步输入与操作')
    course.finalize()
    return course


class CourseComponentTests(unittest.TestCase):
    def failures(self, course):
        return [c['check'] for c in contract_checks(course, course.slides) if c['status'] == 'fail']

    def test_variable_section_counts_and_ranges(self):
        for count in (1, 2, 5):
            c = lesson(count)
            self.assertEqual(self.failures(c), [])
            self.assertIn('<td>2–3</td>', c.slides[0][1])
        c.add('more-work', '进一步解释', '<p>输入</p>', section='s4', goal='解释边界')
        c.finalize()
        self.assertIn('<td>10–12</td>', c.slides[0][1])

    def test_single_task_has_no_required_outline(self):
        c = CourseDeck()
        c.add('task', '解释操作', '<p>输入与问题</p>', goal='预测一步')
        self.assertEqual(self.failures(c), [])

    def test_compact_navigation_needs_a_reason_once(self):
        c = lesson()
        c.slides.pop(0); c.pages.pop(0)
        self.assertIn('outline-presence', self.failures(c))
        c.navigation = 'compact'
        self.assertIn('navigation-adaptation', self.failures(c))
        c.navigation_reason = '本次专题沿同一张任务图连续展开，转换由口头提问承担。'
        self.assertEqual(self.failures(c), [])

    def test_duplicate_ids_and_missing_metadata_fail(self):
        c = lesson()
        c.pages[-1]['id'] = c.pages[-2]['id']
        self.assertIn('page-ids', self.failures(c))
        c.pages.pop()
        self.assertIn('page-metadata', self.failures(c))

    def test_navigation_cannot_drift_from_declarations(self):
        c = lesson()
        c.slides[0][1] = c.slides[0][1].replace('怎样完成任务0', '另一项任务')
        c.slides[1][0] = '第一部分：完全不同的任务'
        c.slides[2][2] = '错误的部分'
        failures = self.failures(c)
        self.assertIn('outline-content/outline', failures)
        self.assertIn('section-content/part-s0', failures)
        self.assertIn('section-label/work-s0', failures)

    def test_unknown_role_section_and_interleaving_fail(self):
        c = lesson()
        c.pages[2]['role'] = 'whatever'
        c.pages[-1]['section'] = 'unknown'
        self.assertIn('page-role/work-s0', self.failures(c))
        self.assertIn('page-section/work-s1', self.failures(c))
        c = lesson()
        c.pages[2]['section'] = 's1'
        self.assertIn('section-order/s1', self.failures(c))

    def test_exercise_requires_shared_workspace(self):
        c = CourseDeck()
        c.add('task', '预测', '<p>答案</p>', role='exercise', goal='预测一步')
        self.assertIn('exercise-input/task', self.failures(c))
        c.slides[0][1] = task_workspace('<p>输入</p>', '<p>问题</p>', '<p>答案</p>')
        self.assertEqual(self.failures(c), [])

    def test_closing_pages_need_no_artificial_section(self):
        c = lesson()
        c.add('homework', '课后练习', '<p>阅读与任务</p>', role='closing', goal='明确课后实践')
        self.assertEqual(self.failures(c), [])
        c.slides.insert(1, c.slides.pop()); c.pages.insert(1, c.pages.pop())
        self.assertIn('closing-position/homework', self.failures(c))

    def test_examples_build_with_stable_dom_roles(self):
        for name in ('patterns', 'single-task'):
            deck = load_deck(EXAMPLES / name)
            self.assertEqual(self.failures(deck.COURSE), [])
            html, _ = render_document(EXAMPLES / name)
            self.assertIn('data-page-id=', html)
            self.assertIn('components.css', html)
            self.assertIn('data-task-input', html)


if __name__ == '__main__':
    unittest.main()
