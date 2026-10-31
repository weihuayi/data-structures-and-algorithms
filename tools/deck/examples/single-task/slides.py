"""A short task needs no artificial outline or section boundary."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from components import CourseDeck, task_workspace

DECK_ID = 'single-task'
TITLE = '单任务组织样例'
COURSE = CourseDeck()
COURSE.add('one-step', '这个操作改变了什么？', task_workspace(
    '<p>数组 A = [3, 5]；操作为 A[0] = 7。</p>',
    '<p>写出操作后的数组，说明下标 0 的含义。</p>',
    '<p>A = [7, 5]；下标 0 指第一个位置。</p>'),
    role='exercise', label='独立练习', goal='独立解释一次按下标修改')
SLIDES = COURSE.finalize()
