"""Three isolated D019 review pages using the actual course component API.

Not the course Deck's slides.py. Page order and section structure here are a subset
of the approved 33-page candidate storyboard, not a competing source of truth.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4] / 'tools' / 'deck'))
from components import CourseDeck, task_workspace, contract_checks

DECK_ID='D019-PROTO'
TITLE='D019｜插入、划分与排序机制 · 三页隔离原型'
MATH=False
COURSE=CourseDeck()  # Intentional three-page isolated subset, not a five-section full lesson.

COURSE.add('insertion-trace','保存待插入记录后，原来的记录怎样右移？',r'''
<div class="d019-preview">
  <p class="lead">已知前三条记录 <strong>2、4、7</strong> 有序。将下一条记录 <strong>3</strong> 插入适当位置。</p>
  <div class="d019-panel">
    <div class="d019-row"><strong id="ins-stage">状态 1/5</strong><span id="ins-held">临时变量：无</span></div>
    <div class="d019-array" style="--count:5" id="ins-array" aria-label="插入排序当前数组" aria-live="polite"></div>
    <div class="d019-narrative" id="ins-note" aria-live="polite"></div>
    <div class="d019-controls"><button id="ins-prev" type="button">上一步</button><button id="ins-next" type="button">下一步</button><button id="ins-reset" type="button">重置</button></div>
  </div>
  <p class="d019-note">□ 表示逻辑空位；当前数组与暂存记录共同保持记录身份。只有完成一轮插入后，才声明新的有序前缀。</p>
</div>
''',role='content',label='候选第08页 · 第二阶段：插入排序',goal='依据暂存和搬移状态解释单次插入，而不混淆外层不变量与临时状态',activity='教师手动分步、学生预测下一步')

partition_input=r'''
<div class="d019-panel">
  <div class="d019-row"><strong>初始输入（核对时持续可见）</strong><span>枢轴关键字：<strong>5</strong></span></div>
  <div class="d019-array d019-small-array" style="--count:9" id="partition-input" data-required-context="独立题初始数组"></div>
  <p class="d019-note" data-required-context="划分执行约定">首记录为枢轴；暂存枢轴；先从右往左、再从左往右交替扫描，移动记录填补空位；下标从 0 开始。</p>
</div>'''
partition_prompt=r'''
<div><strong>独立完成：</strong>写出第一次划分的数组和枢轴下标；说明为什么左右区域可分别递归排序。</div>
<label for="d019-student-input" class="d019-note">先在纸上或下方记录你的推演与依据，再展开核对。</label>
<textarea id="d019-student-input" class="d019-student" placeholder="我的预测、枢轴位置与推理依据……"></textarea>'''
partition_answer=r'''
<p><strong>枢轴最终下标：<span id="partition-index">—</span></strong></p>
<div id="partition-output" class="d019-array d019-small-array" style="--count:9" aria-label="完整划分结果"></div>
<p>枢轴左侧关键字均不大于 5，右侧均不小于 5，所以枢轴已处于合法的最终位置。左右内部仍未排序，但跨区域的大小关系已经成立。</p>'''
COURSE.add('partition-independent','换一个输入，你能独立完成第一次划分吗？',
    '<div class="d019-preview">'+task_workspace(partition_input,partition_prompt,partition_answer,title='核对答案与理由',layout='stacked')+'</div>',
    role='exercise',label='候选第23页 · 第四阶段：快速排序',goal='独立执行指定的双端划分并解释枢轴最终位置和左右子问题的独立性',activity='先独立预测，再展开答案核对')

COURSE.add('mechanism-map','它们都在排序，但各自已经保证了什么？',r'''
<div class="d019-preview">
  <p class="lead">不要只记操作步骤。先问：<strong>每一轮之后，究竟已经建立了什么性质？</strong></p>
  <div class="d019-compare">
    <article class="d019-card"><h3>直接插入排序</h3><div class="sequence">2　4　7 │ 3</div><strong>已处理前缀有序</strong><p>局部已排序，不意味着其中每条记录都到达最终位置。</p></article>
    <article class="d019-card"><h3>冒泡排序</h3><div class="sequence">2　4　1 │ 5</div><strong>已确定后缀就位</strong><p>从左向右相邻交换一趟，使未处理区域的最大记录到末端。</p></article>
    <article class="d019-card"><h3>快速排序</h3><div class="sequence">1,3,2 │ <i>4</i> │ 8,6,7</div><strong>枢轴位置与跨区域关系已确定</strong><p>左右子数组内部未排序，仍需各自递归处理。</p></article>
  </div>
  <div class="d019-chain"><span>执行操作</span> → <span>建立性质</span> → <span>说明为什么最终正确</span></div>
  <p class="d019-narrative">课堂追问：前缀已经有序的记录，与已经位于最终位置的记录，是同一回事吗？</p>
</div>
''',role='content',label='候选第29页 · 第五阶段：机制综合',goal='区分局部有序、最终就位和跨区域约束三种不同性质',activity='机制比较与独立解释')

SLIDES=COURSE.finalize()
assert all(check['status']=='pass' for check in contract_checks(COURSE,SLIDES)), contract_checks(COURSE,SLIDES)