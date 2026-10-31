"""Author-facing, executable examples; not a scheduled course lesson."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from components import CourseDeck, Section, task_workspace

DECK_ID = 'patterns'
TITLE = '课程公共模式样例'
COURSE = CourseDeck([
    Section('task', '明确任务', '当前要求解决什么问题？', '说明对象、输入与输出。'),
    Section('representation', '选择表示', '需要保留哪些关系？', '对应情境、数学对象与存储记录。'),
    Section('operation', '组织操作', '怎样利用已有信息推进？', '解释一步操作的依据和结果。'),
    Section('check', '检查结果', '怎样判断结果是否成立？', '比较预测、运行与条件。'),
    Section('transfer', '尝试变化', '条件改变后，哪些判断仍成立？', '用变化检验适用边界。'),
])
COURSE.outline()
for section in COURSE.sections:
    COURSE.start_section(section.id)
COURSE.add('practice', '先预测，再核对', task_workspace(
    '<p>输入序列：2，4，6。</p>',
    '<p>在每项都乘以 2 后，写出新序列并说明规则。</p>',
    '<p>4，8，12。每个输出都来自对应输入项。</p>'),
    section='transfer', role='exercise', goal='检查必要输入在答案展开后仍可读取')
SLIDES = COURSE.finalize()
