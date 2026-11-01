"""D016: key lookup, sound elimination, cost models and method choice."""
from fractions import Fraction
from html import escape
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]/'tools/deck'))
from components import CourseDeck, Section, task_workspace
from search_trace import (KEYS, BLOCKS, UNIFORM, HOT_FIRST, array_view, search_states,
    search_player, successful_costs, mean_cost, decision_view, decision_model, gap_view,
    index_view, block_player, block_states)

DECK_ID = 'D016'
TITLE = '查找：有序信息怎样减少比较？'
MATH = True
COURSE = CourseDeck([
    Section('task', '明确查找任务', '拿到编号，究竟要找到什么？',
            '区分记录、关键字和下标，建立顺序查找的成功与失败基线。'),
    Section('order', '利用有序信息', '凭什么可以排除半边？',
            '解释候选区间、更新依据和终止条件，再对应到 C 程序。'),
    Section('cost', '计算查找代价', '比较少了多少，结论依赖什么条件？',
            '从具体路径进入判定树和 ASL，区分概率、平均与最坏代价。'),
    Section('blocks', '用索引缩小范围', '块内没有排好序，还能先缩小范围吗？',
            '检查块间范围，建立索引，再完成块内扫描。'),
    Section('choice', '结合需求选择', '什么时候值得先组织数据再查找？',
            '结合准备、访问与更新维护，给出有依据的方法选择。'),
])


def add(pid, title, body, section=None, goal='', activity='讲述、观察与追问', role='content'):
    COURSE.add(pid, title, '<div class="search-lesson">'+body+'</div>', section=section,
               role=role, goal=goal, activity=activity)


def table(headers, rows):
    return '<table class="search-table"><thead><tr>'+''.join('<th>'+escape(str(x))+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'


def definition(text):
    return '<div class="search-definition"><strong>教材定义（概述）：</strong>'+text+'</div>'


def code(text, small=False):
    return '<pre'+(' class="search-code-small"' if small else '')+'><code>'+escape(text)+'</code></pre>'


def pair(left, right):
    return '<div class="search-pair"><div>'+left+'</div><div>'+right+'</div></div>'


BINARY_COSTS = successful_costs()
SEQ_COSTS = successful_costs(mode='sequential')
MEAN_BINARY = mean_cost(BINARY_COSTS, UNIFORM)
MEAN_SEQ = mean_cost(SEQ_COSTS, UNIFORM)
HOT_SEQ = mean_cost(SEQ_COSTS, HOT_FIRST)
HOT_BINARY = mean_cost(BINARY_COSTS, HOT_FIRST)
GAP_COSTS = tuple(decision_model()['gaps'][i] for i in range(len(KEYS)+1))
GAP_MEAN = mean_cost(GAP_COSTS, (Fraction(1,len(GAP_COSTS)),)*len(GAP_COSTS))
INDEPENDENT = (8,19,31,47)

# Opening and lookup contract.
add('cover', TITLE,
    '<p class="lead">给定一个编号，<br>怎样找到记录，或确认不存在？</p>'+
    array_view(caption='本讲沿用同一组商品编号；图中只展示记录的关键字。')+
    '<p class="search-note">数据结构与算法 · 教材 7.1–7.2</p>',
    goal='定位按关键字查找与有序信息的关系',role='cover')
COURSE.outline()
COURSE.start_section('task')
add('record-key-index', '编号 27，和下标 27，是一回事吗？',
    definition('查找表是同一类型记录的集合；关键字是记录中用于标识记录的某个数据项的值。按给定值确定关键字相等的记录，称为查找。')+
    array_view()+
    table(('对象','本例含义'), [('关键字 27','商品编号；记录还可含名称、库存等字段'),
                            ('数组下标 3','记录在当前数组中的位置；A[3].key=27')])+
    '<p class="search-note">主例编号互异，作为主关键字。命中返回下标，失败返回 −1；返回 0 表示命中首项。</p>',
    'task','区分查找表、记录、关键字与当前存储位置')
add('sequential-hit', '逐个比较，怎样找到编号 27？',
    search_player(27,mode='sequential')+
    '<p class="search-note">顺序查找（Sequential Search）：从一端逐个比较。本讲从前向后；教材示例从后向前，两者都需说明方向。</p>',
    'task','从顺序查找轨迹建立比较计数与命中输出','先预测次数，再分步核对')
add('sequential-miss', '没有编号 65，怎样才足以确认？',
    task_workspace(array_view(caption='目标为 65；本基线只作相等判断，不利用有序性提前停止。'),
        '<p>需要比较多少个记录？应返回哪个值？为什么还不能只看几个记录就结束？</p>',
        array_view(low=len(KEYS),high=len(KEYS)-1,checked=range(len(KEYS)),
                   caption='所有 11 个记录均已比较，没有命中。')+
        '<p>比较 11 个关键字，返回 −1。该顺序查找规则已排除全部记录。</p>'),
    'task','区分顺序查找失败证据与一次不相等','独立作答与反馈',role='exercise')
add('access-versus-lookup', '数组访问快，查找就一定快吗？',
    table(('已知什么','要做什么','本讲代价'),[
        ('下标 i','读取 A[i]','数组随机访问 O(1)'),
        ('关键字 key','确定匹配位置或不存在','顺序基线最多检查 n 个记录')])+
    '<p>“顺序存储”表示连续布局，不表示已经按关键字排好序。</p>'
    '<p>“顺序查找”描述检查方式；它也能用于链表。</p>'
    '<p class="search-note">回收 D003、D004：表示决定访问机制；先说明任务，再讨论代价。</p>',
    'task','区分存储方式、访问操作与关键字查找')

# Order, proof obligations and C.
COURSE.start_section('order')
add('eliminate-half', '与 36 比较后，哪些位置不必再查？',
    task_workspace(array_view(current=5,caption='目标 27；按编号递增。当前中点下标 5，关键字 36。'),
        '<p>请写出剩余下标范围，并解释被排除的位置为什么都不可能命中。</p>',
        array_view(low=0,high=4,caption='新的候选为 [0,4]；中点及其右侧全部排除。')+
        '<p>对 i≥5，A[i]≥36&gt;27，所以这批记录均不可能命中。</p>'),
    'order','用同一关键字的有序性证明成批排除','独立预测边界与理由',role='exercise')
add('binary-hit', '折半查找 27，候选怎样逐步缩小？',
    search_player(27)+
    '<p class="search-note">折半查找（Binary Search）：在有序数组中比较中点，保留仍可能命中的一侧；本讲两端均包含。</p>',
    'order','对应中点比较、候选更新和命中返回','在每次更新前停顿预测')
add('binary-miss', '折半查找 65，失败证据在哪里？',
    search_player(65)+
    '<p class="search-note">失败时 low=9、high=8；这是空区间，不读取 A[low] 或 A[high] 来“再确认”。</p>',
    'order','将区间为空与查找失败对应','分步核对，比较与上一页的停止原因')
add('invariant-progress', '为什么不会漏查，也不会停住？',
    pair('<h3>保留可能命中的记录</h3>'
         '<p>若目标存在，仍在当前候选区间。</p>'
         '<p>每次根据有序性，只排除已经确定不可能命中的位置。</p>',
         '<h3>未命中时继续推进</h3>'
         '<p>已经比较且不相等的中点也要排除。</p>'
         '<p>区间长度严格减小；命中或区间为空时结束。</p>')+
    '<p class="search-note">初始覆盖全表；更新保持候选不漏；终止时由相等或空区间给出结果。两项理由分别承担结果正确与能够结束。</p>',
    'order','区分候选不漏与严格推进，解释算法整体依据')
source=(Path(__file__).parent/'code/search_demo.c').read_text()
core=source.split('static int binary_find',1)[1].split('static int block_find',1)[0]
core='int binary_find'+core.replace(', Trace *t','')
core=re.sub(r'^\s*probe\(t,low,high,mid,a\[mid\]\);\n','',core,flags=re.M)
add('binary-code', '区间规则怎样进入 C 程序？',
    code(core.strip())+
    '<p class="search-note">核心代码省略轨迹记录。键数组 a[i] 对应记录 A[i].key，一般记录还需保持其他字段对应。前提：n≥0、存储有效且按同一关键字非递减；查询不现场排序。</p>',
    'order','将区间约定、返回契约与实际 C 条件和更新对应','对照规则阅读代码')
add('boundary-task', '只剩最后一个候选，还要比较吗？',
    '<div class="search-compact-task">'+task_workspace(array_view((5,16),caption='目标 16；初始 low=0、high=1，向下取中点。'),
        '<p>第一次未命中后，若写 low=mid，会发生什么？正确更新后只剩一个候选，循环应继续吗？</p>',
        array_view((5,16),low=1,high=1,current=1,found=1,caption='low=1、high=1，仍比较 A[1]=16。')+
        '<p>low=mid 会保持原区间；正确为 low=mid+1。闭区间在 low=high 时仍有一个候选，故使用 low≤high。</p>')+'</div>',
    'order','用两元素反例检验推进与闭区间边界','独立诊断错误更新',role='exercise')
add('wrong-field', '按价格排好序，能按编号折半吗？',
    task_workspace(table(('下标','编号','价格'),[(0,30,10),(1,10,20),(2,20,30)]),
        '<p>按编号查找 30。价格递增，是否足以支持本讲折半规则？请说明一次错误排除。</p>',
        '<p>不满足前提。中点编号 10 小于 30，会使算法排除左侧，而编号 30 恰好在左侧。</p>'
        '<p>必须按查找关键字的同一比较规则有序；不能用另一字段的顺序作依据。</p>'),
    'order','识别有序性必须对应查找关键字','独立判断前提',role='exercise')

# Cost model and conditional averages.
COURSE.start_section('cost')
add('all-query-costs', '一次命中用了三次，其他查询呢？',
    table(('关键字',*KEYS), [('顺序',*SEQ_COSTS),('折半',*BINARY_COSTS)])+
    '<p>查 5：顺序 1 次，折半 3 次；查 36：顺序 6 次，折半 1 次。</p>'
    '<p class="search-note">统一计数：比较过几个记录的关键字。一次中点判定计 1 个；C 中的 ==、&lt; 等条件测试次数和实测时间另计。</p>',
    'cost','从不同查询的实际比较次数建立评价问题')
add('decision-tree', '判定树怎样把不同路径画出来？',
    decision_view()+
    '<p class="search-note">本表比较 1、2、3、4 次的记录分别有 1、2、4、4 个。先看实际路径，再汇总。</p>',
    'cost','把数组查找路径与判定树层数对应','指出 27、71 的路径并数比较')
add('success-asl', '怎样从不同查询得到平均代价？',
    definition('平均查找长度（Average Search Length，ASL）是比较关键字个数的期望。教材首先定义成功时的 ASL；此时概率在成功记录之间归一。')+
    r'<p class="search-formula">\(ASL_{\mathrm{succ}}=\sum_{i=0}^{n-1}p_i c_i,\qquad \sum_i p_i=1\)</p>'+
    r'<p class="search-note">\(p_i\)：成功时查第 \(i\) 项的概率；\(c_i\)：命中它所比较的关键字个数。<br>'
    r'例：\(i=3\) 对应关键字 27；等概率时 \(p_3=1/11\)，顺序 \(c_3=4\)、折半 \(c_3=3\)。</p>'+
    table(('本例假设','顺序查找','折半查找'),[
        ('成功查询，11 个记录等概率',str(MEAN_SEQ),str(MEAN_BINARY))])+
    r'<p class="search-formula">折半：\(\dfrac{1+2\times2+3\times4+4\times4}{11}=3\)</p>'
    r'<p class="search-note">平均 3 次不表示每次 3 次，也不表示最坏 3 次。顺序成功均值为 \((n+1)/2=6\)。</p>',
    'cost','解释 ASL 的计数、权重及成功条件','先根据树汇总，再形成公式')
add('failure-asl', '失败代价，能从成功平均直接得到吗？',
    gap_view()+
    '<p class="search-note">上表列出 12 个失败间隙；本主例每个间隙都有可取的整数。各间隙是否等概率，需另外给定。</p>'+
    r'<p>若题设给出失败间隙等概率：\(ASL_{\mathrm{fail}}=(4\times3+8\times4)/12=11/3\)。</p>'
    '<p class="search-note">查 65 的 3 次是单次结果。实际查询混合成功和失败时，还要按它们的发生比例加权。</p>',
    'cost','区分一次失败、失败间隙分布与条件平均')
add('query-frequency', '查询频率变了，平均代价会变吗？',
    table(('成功查询分布','顺序 ASL','折半 ASL'),[
        ('11 个关键字等概率',str(MEAN_SEQ),str(MEAN_BINARY)),
        ('查 5 的概率 0.8；其余各 0.02',str(float(HOT_SEQ)),str(HOT_BINARY))])+
    '<p>数组和算法都没变，需求分布变了。</p>'
    '<p>平均收益要说明“哪些查询更常发生”。</p>'
    '<p class="search-note">此例折半均值恰好仍为 3；一般情况下它也会随分布变化。这里比较关键字个数，不据此宣称实测更快。</p>',
    'cost','用非均匀查询反例检验固定平均结论','先预测，再核对权重')
add('growth', '表长增加，代价怎样增长？',
    table(('方法','最坏比较关键字数','这里的条件'),[
        ('顺序基线','n','不利用有序性提前停止'),
        ('数组折半',r'\(\lfloor\log_2 n\rfloor+1\)（n≥1）','按关键字有序，且能 O(1) 访问中点')])+
    '<p>本例 n=11：折半最坏为 4，成功 ASL 为 3，含义不同。</p>'
    '<p>折半每轮把候选规模约减半，时间为 O(log n)；空表不比较。</p>'
    '<p class="search-note">特殊长度的 ASL 闭式公式保留其前提，不用于任意表长。链表节点走访成本需另计。</p>',
    'cost','区分具体代价、最坏上界与增长阶')
add('cost-task', '换一张表，你能独立分析吗？',
    '<div class="search-compact-task">'+task_workspace(array_view(INDEPENDENT,caption='按关键字递增；四个记录在成功查询中等概率；闭区间、向下取中点。'),
        '<p>画出判定树，求顺序和折半的成功 ASL。若没有给出概率，还能得到唯一均值吗？</p>',
        '<div class="search-answer-tree">'+decision_view(INDEPENDENT,caption='层数从 1 开始，表示成功比较次数。')+'</div>'+
        r'<p>折半比较次数为 2、1、2、3，均值 2；顺序均值 2.5。未给概率时，可写 \(\sum p_i c_i\)，不能指定唯一均值。</p>')+'</div>',
    'cost','在新输入上产出判定树与有条件的平均计算','独立画图与计算',role='exercise')

# Partial order by blocks.
COURSE.start_section('blocks')
add('block-input', '块内无序，哪些信息仍可用于排除？',
    definition('分块查找（Blocking Search，又称索引顺序查找）先定位块，再在块内顺序查找。索引记录块的最大关键字及起始位置。')+
    index_view()+array_view(sum(BLOCKS,()),caption='B1 为下标 0–2，B2 为 3–5，B3 为 6–10；仍是原来 11 个记录。')+
    r'<p class="search-note">本讲互异关键字满足 \(\max(B_i)<\min(B_{i+1})\)；块内无需有序。块末由下一起点或表长确定。</p>',
    'blocks','明确块间范围、块内排列和索引的不同职责')
add('block-trace', '查 30：索引和块内扫描怎样分工？',
    block_player(30),
    'blocks','从索引定位到块内扫描，区分两段比较计数','遇到块内 36 时停顿，预测能否提前结束')
add('block-miss', '查 28：什么时候才足以判定失败？',
    task_workspace(array_view(sum(BLOCKS,()),caption='查找 28；索引（最大值，起点）：(20,0)、(36,3)、(71,6)；总长 11。'),
        '<p>定位哪个块？需要检查哪些位置？看到第一个记录大于 28，可以停止吗？</p>',
        array_view(sum(BLOCKS,()),low=3,high=5,checked=(3,4,5),caption='蓝底标出已经完整检查的 B2：36、27、30。')+
        '<p>索引比较 2 次，块内比较 3 次，返回 −1。块内无序，看到 36&gt;28 不能停止；块末以后不再扫描。</p>'),
    'blocks','解释块内失败证据及块边界','独立定位与核对',role='exercise')
add('block-condition', '最大值递增，就一定分块正确吗？',
    task_workspace(table(('待核对块','记录','最大值'),[('B1','5、30',30),('B2','16、36',36)]),
        '<p>索引最大值递增。查 16 时会选哪个块？这能保证不漏查吗？</p>',
        array_view((5,30,16,36),found=2,caption='16 实际在 B2；第一次索引定位却会选 B1。')+
        '<p>最大值递增不足以保证块间范围有序。本例 30&gt;16，块成员范围交错，不能使用该定位规则。</p>'),
    'blocks','用非法分块反例检验结构条件','独立诊断并解释反例',role='exercise')

# Complete cost and choice.
COURSE.start_section('choice')
add('preparation-cost', '准备工作的代价，何时能摊回？',
    '<p>只比较关键字比较次数。题设：准备耗费 60 次比较；每次成功查询等概率，顺序均值 6、折半均值 3。</p>'+
    table(('查询次数 q','顺序：6q','准备后折半：60+3q'),[(1,6,63),(20,120,120),(100,600,360)])+
    '<p>在这个模型中，q&gt;20 才获得比较次数收益。</p>'
    '<p class="search-note">60 是题设，不是排序实测。记录移动、空间与实际时间另作评估；排序实现留到 D019–D020。</p>',
    'choice','用统一计数口径评价准备成本与多次查询','判断盈亏条件')
add('whole-cost', '仅比较次数，够不够决定方案？',
    table(('需求与表示','还要核对什么'),[
        ('现有有序数组，多次查询','中点随机访问、查询分布与返回要求'),
        ('未组织数据，查询很少','准备工作是否值得；顺序查找可作基线'),
        ('有序链表','比较虽可减少，走访中点的代价仍要计算'),
        ('有序数组频繁插入删除','记录移动、有序性维护及额外空间')])+
    '<p class="search-note">分块更新还取决于实际存储、容量和索引维护；块内无序不自动带来 O(1) 更新。</p>',
    'choice','将比较收益放回表示、维护与需求的整体成本')
add('choice-task', '面对一个新需求，怎样给出选择？',
    task_workspace('<p>20 万条记录已按编号存于数组；查询持续发生，近期没有增删。</p>'
                   '<p class="search-note">目标是返回任一匹配位置或不存在；查询频率分布未给定。</p>',
        '<p>给出方法、成立条件、代价依据，以及一个可能使你改选的变化。可以直接给出唯一 ASL 吗？</p>',
        '<p>可选择数组折半：已有顺序，无需为本次查询再排序；迭代只维护边界。</p>'
        '<p>按最坏比较次数评估，每次至多 18 次；未给查询概率，不能指定唯一 ASL。</p>'
        '<p>若持续大量插入删除，应重新评估移动与维护成本，并比较后续树表、散列等结构。</p>'),
    'choice','在陌生规模上作出有前提、有代价依据的选择','独立决策与同伴解释',role='exercise')

add('summary', '怎样把查找方法连成一条判断链？',
    table(('判断','本讲形成的依据'),[
        ('找什么？','给定关键字，返回位置或确认不存在'),
        ('为什么能排除？','已有有序信息；候选不漏且持续缩小'),
        ('少比较多少？','按实际路径、成功/失败与概率计算'),
        ('何时值得采用？','结合准备、访问、更新维护与空间')])+
    '<p>回收 D002 的信息利用、D003 的数组访问和 D010 的加权路径思想。</p>'
    '<p class="search-note">下一讲：数据持续变化，怎样用树维护查找所需的顺序？</p>',
    goal='回收查找契约、正确性、评价与选择，并衔接 D017',role='closing')
add('after-class', '课后怎样核对预测与运行？',
    code('gcc -std=c11 -Wall -Wextra \\\n  course/decks/d016-search-order-and-asl/code/search_demo.c -o /tmp/d016\n/tmp/d016 last\n/tmp/d016 profile --json',small=True)+
    '<p><strong>A · 教材：</strong>精读 7.1–7.2、算法 7.1–7.3，核对下标、返回值与 ASL 假设。</p>'
    '<p><strong>B · 实践：</strong>先预测查 71 再运行；另拟 4–7 个互异关键字，画判定树并算等概率成功 ASL；核对分块查 28 的失败依据。</p>'
    '<p class="search-note">保留手工过程、程序输出和 3–5 行差异解释，按课程作业说明提交。</p>',
    goal='明确教材导航与先预测后运行的课后任务',role='closing')

SLIDES = COURSE.finalize()
