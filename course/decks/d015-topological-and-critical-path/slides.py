"""D015: dependency constraints, ordering, project time and activity float."""
from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]/'tools/deck'))
from components import CourseDeck, Section, task_workspace
from dependency_trace import (TASKS, AOV_NODES, AOV_EDGES, MAIN_ACTIVITIES, EVENTS,
    EXERCISE_ACTIVITIES, aov_view, completed_aov_view, aoe_view, table, task_table,
    topological_states, critical_path, topological_player, time_player)

DECK_ID = 'D015'
TITLE = '拓扑排序与关键路径：依赖关系怎样决定顺序与工期？'
MATH = True
COURSE = CourseDeck([
    Section('dependency', '把依赖关系说清楚', '哪些工作必须等待，哪些可以独立推进？',
            '从任务条件建立活动间的先后关系，明确有向环与当前模型的冲突。'),
    Section('order', '产生合法推进顺序', '为什么当前这个顶点可以排在下一位？',
            '剩余入度、候选与输出；分别解释安全选择和停滞判环。'),
    Section('earliest', '计算最早完工时间', '顺序合法之后，整个项目最早何时完成？',
            '对应活动与事件，按全部前置约束计算最早时间，解释最长链的作用。'),
    Section('critical', '时间余量与关键活动', '哪些活动可以适度延后，哪些会影响工期？',
            '反向汇总期限，计算活动余量；用变式与独立作答核对理解。'),
])


def add(pid, title, body, section=None, goal='', activity='讲述、观察与追问', role='content'):
    COURSE.add(pid, title, '<div class="dependency-lesson">'+body+'</div>',
               section=section, role=role, goal=goal, activity=activity)


def pair(left, right, cls=''):
    return '<div class="dag-two '+cls+'"><div>'+left+'</div><div>'+right+'</div></div>'


def code(text):
    return '<pre><code>'+escape(text)+'</code></pre>'


def definition(text, *, inline=False):
    label = '<strong>教材定义（概述）：</strong>' if inline else '<strong>教材定义（概述）</strong><br>'
    return '<div class="dag-definition">'+label+text+'</div>'


MAIN = critical_path()
EXERCISE = critical_path(range(4), EXERCISE_ACTIVITIES, source=2, sink=1)
B4 = tuple((a,u,v,4 if a=='B' else w) for a,u,v,w in MAIN_ACTIVITIES)
B3 = tuple((a,u,v,3 if a=='B' else w) for a,u,v,w in MAIN_ACTIVITIES)
TIED, FASTER = critical_path(activities=B4), critical_path(activities=B3)

# Opening and dependency semantics, pages 1–7.
add('cover', TITLE, pair(aov_view(),
    '<p class="lead">工作有先后依赖，<br>怎样安排顺序、判断工期？</p>'
    '<p>从小组完成一份数据分析报告开始。</p>'
    '<p class="dag-note">数据结构与算法 · 教材 6.6.3–6.6.4</p>'),
    goal='定位依赖、顺序和工期问题',role='cover')
COURSE.outline()
COURSE.start_section('dependency')

add('project', '六项工作，哪些必须等待？', pair(task_table(),
    '<p>项目目标：完成一次数据分析报告。</p>'
    '<p>D 需要程序和测试样例；F 需要预处理结果和通过测试的程序。</p>'
    '<p>先只看依赖，不考虑每项工作需要多久。</p>'
    '<p class="dag-note">程序输入约定已知，B 可以和 A 独立开始；表中依赖是本教学案例给定的条件。</p>'),
    'dependency','从任务表识别直接前置条件')

add('aov', '怎样把依赖画成 AOV 网？',
    task_workspace(definition('AOV 网（Activity on Vertex Network）以顶点表示活动，以有向弧表示先后依赖。',inline=True)+
        aov_view(caption='新增活动 G：必须等 C、E 完成才能开始。'),
        '<p>请补画依赖边；G 也必须等待 D 吗？</p>',
        completed_aov_view()+'<p class="dag-note">未给定 D→G，不能额外增加这项依赖。</p>'),
    'dependency','把活动和依赖对应为顶点与弧，避免添加多余约束','1 分钟独立补边与反馈',role='exercise')

add('legal-order', '合法顺序为什么可能不唯一？', pair(aov_view(),
    definition('拓扑排序（Topological Sorting）将全部顶点排成一个序列；每条弧的起点都排在终点之前。')+
    '<p>A B C E D F</p><p>B A E D C F</p>'
    '<p>这两种都满足所有依赖。</p><p class="dag-note">A 与 B 无先后约束；序列中排在前面，不等于现实中必须串行执行。</p>'),
    'dependency','区分必要先后、合法序列与实际串行执行')

add('cycle-model', '互相等待，与当前依赖模型冲突在哪里？',
    pair(aov_view(cycle=True, caption='在原依赖图中另加红弧 E→A，形成 A→E→A。'),
         '<p>A 必须等 E 完成才能开始；E 又必须等 A 完成。</p>'
         '<p>这种一次性、先完成再开始的依赖无法启动。</p>'
         '<p>无环的有向图称为有向无环图（Directed Acyclic Graph，DAG）。</p>'
         '<p class="dag-note">反馈与反复迭代需要另建模型，不由此断言现实中的环都不合理。</p>'),
    'dependency','解释有向环与当前一次性依赖模型的冲突')

# Topological ordering, pages 8–15.
COURSE.start_section('order')

add('ready', '哪些顶点可以排在下一位？', pair(aov_view(),
    '<p>选择当前没有未安排前驱的顶点。</p>'+
    table(('顶点',*AOV_NODES),[('初始入度',0,0,1,2,1,2)],'dag-state')+
    '<p>最初候选：A、B。</p><p><code>indegree[v]</code> 用于记录尚未解除的入边数量。</p>'
    '<p class="dag-note">这里生成排列；“排入序列”不表示现实工作已经做完。</p>'),
    'order','建立零入度候选与剩余依赖的含义')

add('release', '把 B 排入序列，D 就可以排下一位吗？',
    task_workspace(aov_view(marked=(('B','D'),))+
        '<p class="dag-note">输入弧：B→D；D 初始有 B、E 两个直接前驱。</p>',
        '<p>读取 B 的出邻接记录 D 后，D 的剩余入度怎样变化？应加入候选吗？</p>',
        '<p>D 的剩余入度：2→1。</p><p>E 还没有排入序列，因此 D 仍不能加入候选。</p>'
        '<p>不修改原图；只更新算法的辅助记录。</p>'),
    'order','将一条出邻接记录与入度减一、是否加入候选对应','独立预测与反馈',role='exercise')

add('topo-trace', '完整推进中，哪些记录在变化？', topological_player(),
    'order','区分排位、读取、解除依赖与本轮完成','分步演示，在 B→D 和首次产生新候选处停顿')

add('safe-choice', '为什么选择零入度顶点不会破坏顺序？', pair(aov_view(),
    '<p>轮次开始时，已输出顶点的出边都已处理。</p>'
    '<p>若某未输出顶点的剩余入度为 0，它的全部前驱都已在前面。</p>'
    '<p>把它放在下一位，不会把任何前驱放到它后面。</p>'
    '<p class="dag-note">栈或队列决定多个合法候选间的选择次序；合法性来自零入度条件。</p>'),
    'order','解释零入度选择的安全性及其轮次前提')

add('blocked', '没有候选，又没排完，为什么说明有环？',
    pair(aov_view(cycle=True,caption='新增 E→A 后，只能先输出 B；其他顶点均留在剩余子图中。'),
         '<p>剩余顶点都有剩余前驱。</p><p>沿前驱不断回溯，有限个顶点中必有重复，因此存在环。</p>'
         '<p>本例只有 A、E 在环上；C、D、F 是受阻的后续活动。</p>'
         '<p class="dag-note">判据：候选为空且输出数小于顶点数；不是“剩余顶点全部构成一个环”。</p>'),
    'order','由剩余子图解释判环，区分环成员与受阻后续')

add('check-order', '怎样核对别人给出的顺序？',
    task_workspace(aov_view()+'<p class="dag-note">序列① A B C E D F<br>序列② A B D E C F</p>',
        '<p>哪一个合法？请指出具体检查依据。</p>',
        '<p>① 合法；② 把 D 排在 E 前，违反 E→D。</p>'
        '<p>先查每个顶点恰好出现一次，再对每条弧检查起点位置小于终点位置。</p>'),
    'order','独立核对顶点完整性与逐边先后约束','2 分钟独立核对与反馈',role='exercise')

add('topo-code', '怎样把排位和更新写进程序？', pair(code('u = stack[--size];\nr->order[r->count++] = u;\nfor (e = g->head[u]; e != -1;\n     e = g->edge[e].next) {\n    v = g->edge[e].v;\n    if (--r->degree[v] == 0)\n        stack[size++] = v;\n}'),
    '<p><code>head/edge/next</code>：原图的出邻接表。</p><p><code>degree</code> 对应教材的 <code>indegree</code>；<code>stack</code> 保存候选。</p>'
    '<p><code>order</code>：已生成的排列。</p><p class="dag-note">C 演示关键语句；按编号初始化栈，按邻接记录顺序扫描，与教材算法 6.12 对应。</p>'),
    'order','对应输入、辅助状态与 C 的关键条件')

# Time meaning and earliest finish, pages 16–21.
COURSE.start_section('earliest')

add('order-time', '得到一个顺序，就知道何时完工了吗？', pair(task_table(durations=True),
    '<p>六项时长相加：16 小时。</p><p>但 A、B 可以并行，C、E 也可以在 A 完成后并行。</p>'
    '<p>怎样在满足全部依赖的同时尽早完成？</p>'
    '<p class="dag-note">时长固定且非负，工作可以并行，人员、设备不构成额外限制；教学数字不是真实工期估计。</p>'),
    'earliest','区分合法排列、串行总时长与并行工期')

add('aoe', '同一项目怎样表示成 AOE 网？',
    definition('AOE 网（Activity on Edge Network）以顶点表示事件、弧表示活动、权表示持续时间，是带权 DAG。',inline=True)+
    '<div class="dag-two dag-comparison">'+aov_view(caption='AOV：六个顶点分别是活动 A–F。')+
    aoe_view(caption='AOE：五个顶点分别是事件；A–F 标在活动弧上。')+'</div>'+
    '<p>事件 2：B、E 均完成；事件 3：C、D 均完成。事件本身不占时长。</p>',
    'earliest','明确 AOV 活动顶点与 AOE 事件、活动弧的对应')

add('max', '为什么要等待最晚完成的前置工作？',
    task_workspace(aoe_view(marked=((0,2),(1,2)))+'<p class="dag-note">事件 0 在时刻 0 发生；事件 1 在时刻 3 发生。</p>'+
        '<p class="dag-note">本次目标事件 v=2，前驱事件 u 为 0 或 1；连接它们的活动为 B、E，w(u,v) 表示活动时长。</p>',
        '<p>B 完成需到 0+5；E 完成需到 3+1。</p><p>事件 2 最早何时发生？能取较小值吗？</p>',
        r'<p>必须等 B、E 都完成。</p><p>\(ve(2)=\max\{5,4\}=5\)。</p>'
        '<p>取 4 时 B 还没有完成，D 的开始条件不成立。</p>'),
    'earliest','由全部前置条件推导最大值递推','独立预测与解释',role='exercise')

add('early-trace', '怎样按拓扑序计算最早时间？',
    time_player('forward')+
    r'<p class="dag-note">\(ve(v)=\max_{(u,v)}\{ve(u)+w(u,v)\}\)。u、v 是事件，w(u,v) 为活动时长；全部前驱传播后，ve(v) 才完整。</p>',
    'earliest','区分已收集约束的下界与已经完整的最早时间','正向分步演示，停顿比较两个前置约束')

add('longest', '为什么最长依赖链决定最早工期？', pair(aoe_view(marked=((0,2),(2,3),(3,4))),
    '<p>B→D→F 必须先后完成：5+3+2=<strong>10</strong>，任何安排都不能少于 10。</p>'+
    table(('活动','一种可行时间安排'),[('A、B','A：0–3；B：0–5'),('C、E','C：3–5；E：3–4'),('D','5–8'),('F','8–10')])+
    '<p class="dag-note">这个安排满足全部依赖并达到 10：下界能够达到，所以最早工期为 10。</p>'),
    'earliest','同时说明最长链的下界与最早安排的可达到性')

# Latest constraints, activity float, independent work, pages 22–31.
COURSE.start_section('critical')

add('min', '为了按时完工，事件 1 最迟何时发生？',
    task_workspace(aoe_view(marked=((1,2),(1,3)))+'<p class="dag-note">不延长 T=10：事件 2 最迟为 5，事件 3 最迟为 8。</p>',
        '<p>经过 E 要留 1 小时，经过 C 要留 2 小时。</p><p>事件 1 应取哪一个最迟期限？</p>',
        r'<p>两项后续要求都要满足。</p><p>\(vl(1)=\min\{5-1,8-2\}=4\)。</p>'
        '<p>若取 6，E 就不能在事件 2 的期限前完成。</p>'),
    'critical','由全部后继期限推导最小值递推','独立预测与反馈',role='exercise')

add('late-trace', '怎样按逆拓扑序完成反向计算？', time_player('backward')+
    r'<p class="dag-note">\(vl(t)=T=ve(t)\)；\(vl(u)=\min_{(u,v)}\{vl(v)-w(u,v)\}\)。编号不是逆拓扑序。</p>',
    'critical','从汇点沿逆拓扑序汇总后继约束','反向分步演示，在事件 1 的两个期限处停顿')

add('activity-time', '事件时间怎样变成活动的开始时间？',
    pair(aoe_view(values=MAIN['early'],marked=((1,3),)),
         r'<p>活动 C：事件 1→3，持续 2 小时。</p><p>\(ve(1)=3\)，\(vl(3)=8\)。</p>'
         r'<p>最早开始：\(e(C)=ve(1)=3\)。</p><p>最迟开始：\(l(C)=vl(3)-2=6\)。</p>'
         r'<p>时间余量：\(l(C)-e(C)=3\)。</p>'
         '<p class="dag-note">这里的余量是总时差，不能把各项余量视为独立额度。</p>'),
    'critical','对应事件最早/最迟时间与活动开始时间和总时差')

add('critical-path', '哪些活动组成关键路径？', pair(aoe_view(marked=((0,2),(2,3),(3,4)))+
    '<p>B→D→F：5+3+2=10。</p>'
    '<p class="dag-note">关键路径（Critical Path）从源到汇；依据活动的 l−e 判定，不只看端点。</p>',
    table(('活动','e','l','余量'),[(a,t['earliest'],t['latest'],t['slack']) for a,t in MAIN['activity_times'].items()])+
    '<p>余量为 0 的关键活动：B、D、F。</p>'),
    'critical','依据活动余量识别完整的源汇关键路径')

add('multiple', '继续缩短 B，工期一定继续缩短吗？',
    task_workspace(aoe_view(activities=B4)+'<p class="dag-note">只把活动 B 的时长从 5 小时改为 4 小时；其他活动不变。</p>',
        '<p>B 的持续时间为 4 小时，工期和关键路径是什么？</p><p>若再改为 3 小时，工期还会缩短 1 小时吗？</p>',
        '<p>B 持续 4 小时：T=9。<br>关键路径：B–D–F、A–E–D–F。</p>'
        '<p>B 持续 3 小时：T 仍为 9，由 A–E–D–F 约束。</p>'
        '<p>加快一条关键路径独有的活动，未必能缩短另一条关键路径；改变时长后重新计算。</p>'),
    'critical','用时长变化理解多关键路径及加速效果的条件','变式预测与反馈',role='exercise')

add('independent', '换一张编号不同的网，你能独立计算吗？',
    task_workspace(aoe_view(EXERCISE_ACTIVITIES,exercise=True)+
        '<p class="dag-note">固定非负时长；源事件 2 在时刻 0 开始，汇事件 1 表示全部活动完成；资源不额外限制并行。</p>',
        '<ol><li>写出拓扑序，计算全部 ve、vl。</li><li>求活动 c 的 e、l 和余量。</li>'
        '<li>指出工期与关键路径，解释一处 max 或 min 的依据。</li></ol>',
        '<p>拓扑序：2、0、3、1；T=6。</p>'+
        table(('事件',2,0,3,1),[('ve',0,2,3,6),('vl',0,2,4,6)],'dag-state')+
        r'<p>活动 c：\(e(c)=2\)，\(l(c)=4-1=3\)，余量 1。</p><p>关键路径：2→0→1，活动 a、d。</p>'),
    'critical','独立应用拓扑次序、两向约束和活动余量','8 分钟独立作答＋3 分钟反馈',role='exercise')

add('predict-run', '预测与程序结果不同，先检查什么？', pair('<p class="dag-note">在本讲目录中运行：</p>'+
    code('gcc -std=c11 -Wall -Wextra \\\n  code/dependency_demo.c -o /tmp/d015\n/tmp/d015 exercise\n/tmp/d015 topo --trace'),
    '<p>先保留自己的预测，再运行核对。</p><ol><li>活动还是事件？源汇是谁？</li>'
    '<li>是否按拓扑序和逆拓扑序处理？</li><li>入边约束取 max，出边期限取 min？</li>'
    '<li>是否把事件时间误当活动开始时间？</li></ol>'),
    'critical','用输入、处理次序和公式对象定位差异','预测后运行，与独立题反馈衔接')

add('resources', '如果全部工作只能由一个人完成呢？',
    task_workspace(task_table(durations=True)+'<p class="dag-note">新条件：所有工作由同一人串行完成，时长不变。</p>',
        '<p>10 小时还一定能达到吗？</p>',
        '<p>此时总工作量为 16 小时，按合法顺序串行执行可在 16 小时完成。</p>'
        '<p>依赖链的 10 小时仍是下界，但资源约束使它无法达到。</p>'
        '<p>本讲关键路径法计算没有包含这项新约束。</p>'),
    'critical','区分依赖约束下的最早工期与加入资源条件后的问题','短判断与边界解释',role='exercise')

add('cost', '几轮计算，为什么仍是线性工作量？',
    table(('阶段','在邻接表上完成的工作'),[
        ('拓扑排序','初始化全部入度；每个顶点进出候选一次，每条弧解除一次'),
        ('正向与反向','按两个方向各扫描全部顶点和全部活动'),
        ('活动判定','每条活动计算 e、l、余量，并判定是否关键')])+
    r'<p>总时间 \(O(n+m)\)；图存储 \(O(n+m)\)，辅助数组与栈 \(O(n)\)。</p>'
    '<p class="dag-note">n 为当前图的顶点数，m 为弧数。以上针对已校验邻接表上的算法；输入检查、追踪快照与输出另计。枚举全部关键路径可能有指数规模。</p>',
    'critical','从顶点、弧的处理次数解释总代价并限定输出范围')

# Closing pages 32–33.
add('homework', '课后怎样练习和核对？',
    '<p><strong>A · 教材：</strong>第 6 章选择题（15）、应用题（5），按图 6.38 完成工期、活动开始时间及关键活动计算。</p>'
    '<p><strong>B · 程序实践：</strong>只把主例 D 从 3 改为 2。先预测事件 2、3 的最早时间、工期和关键活动，再运行核对。</p>'+
    code('/tmp/d015 homework')+
    '<p class="dag-note">阅读 6.6.3–6.6.4、算法 6.12/6.13；保留过程、一次更新的解释及 3–5 行差异记录。按课程作业说明提交。</p>',
    goal='明确教材导航与先预测后运行的课后任务',role='closing')

add('recall-next', '依赖关系怎样支撑了计算与判断？',
    table(('问题','本讲依据'),[('能否排在下一位？','全部前驱已经排在前面'),
        ('最早何时发生？','满足全部前置活动完成时间，取 max'),
        ('最迟允许何时？','守住全部后继期限，取 min'),
        ('哪些活动关键？','相对于最早工期，活动总时差为 0')])+
    '<p>下一讲：已知关键字有序，怎样用它减少查找？</p>'
    '<p class="dag-note">本讲的依赖先后与关键字大小是不同的序；都要先说明关系，再判断它支持什么计算。</p>',
    goal='回收约束、计算次序与边界，衔接 D016',role='closing')

SLIDES = COURSE.finalize()
