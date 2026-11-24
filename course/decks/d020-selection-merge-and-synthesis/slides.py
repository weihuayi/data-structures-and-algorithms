"""D020 official 34-page lesson, based on R1–R8 and QA-01–QA-08.

Single source of truth for page identities, sections, questions and lesson content.
Run: python3 tools/deck/build.py D020 (from repository root).
"""
from html import escape
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "deck"))
from components import CourseDeck, Section, task_workspace

DECK_ID = "D020"
TITLE = "排序：选择、堆、归并与条件化选择"
MATH = True
COURSE = CourseDeck([
    Section("selection", "选择与结构维护",
            "反复寻找最值，能否复用以前的比较结果？",
            "简单选择、树形选择和二叉堆的维护机制", "解释可复用信息与堆排序正确性"),
    Section("merge", "有序结果的组合",
            "两个子序列已有序，如何在线性时间中合并？",
            "稳定归并、输出不变量、递归组合及时间空间代价", "独立归并并说明递归输入前提"),
    Section("radix", "利用关键字数位",
            "不用通用两两比较，能否利用关键字的表示结构？",
            "多关键字、最低位优先、链式桶、稳定分配与收集", "解释桶内顺序及其正确性职责"),
    Section("choice", "计算代价与条件化选择",
            "数据条件变了，为什么合适的排序方法也会变？",
            "模型、时间空间、稳定性及输出需求", "依据约束比较方案而非只背复杂度表"),
])

def P(text):
    return "<p>" + text + "</p>"

def M(formula):
    return '<span class="d20-math">\\(' + escape(formula) + '\\)</span>'

def box(title, body, cls=""):
    return '<div class="d20-box '+cls+'"><h3>'+title+'</h3>'+body+'</div>'

def cols(*items):
    return '<div class="d20-columns">'+"".join(items)+"</div>"

def lead(text):
    return '<p class="d20-lead">'+text+"</p>"

def note(text):
    return '<p class="d20-note">'+text+"</p>"

def highlight(text):
    return '<div class="d20-highlight">'+text+"</div>"

def seq(values, ids=None, *, focus=(), fixed=(), active=None, label=None):
    """Record key and ID are separate; a boundary may distinguish heap/suffix."""
    if ids is not None and len(ids) != len(values):
        raise ValueError("Record identity count differs from key count")
    cells = []
    for i, val in enumerate(values):
        klass = "d20-cell"
        if i in focus:
            klass += " d20-focus"
        elif i in fixed or (active is not None and i >= active):
            klass += " d20-fixed"
        sub = ('<small>id='+escape(str(ids[i]))+'</small>' if ids is not None else "")
        cells.append('<div class="'+klass+'"><small class="d20-index">i='+str(i)+'</small>'
                     '<strong>'+escape(str(val))+'</strong>'+sub+'</div>')
    return ('<figure class="d20-sequence" aria-label="'+escape(label or "数组顺序状态", quote=True)+'">'
            '<div class="d20-cells" style="--n:'+str(len(values))+'">'+''.join(cells)+'</div>'
            '</figure>')

def tree(values, *, highlight_nodes=()):
    """Complete binary tree and level-order array share the same numeric input."""
    n=len(values)
    if not n:
        return '<div>空堆</div>'
    h=math.floor(math.log2(n))+1
    width=960
    height=80*h+22
    xy={}
    for i in range(n):
        d=math.floor(math.log2(i+1))
        p=i-(2**d-1)
        xy[i]=((p+0.5)*width/(2**d),43+80*d)
    shapes=[]
    for i in range(1,n):
        j=(i-1)//2
        x,y=xy[i]; xx,yy=xy[j]
        shapes.append(f'<path d="M{xx:.1f},{yy:.1f} L{x:.1f},{y:.1f}" class="d20-edge"/>')
    for i,v in enumerate(values):
        x,y=xy[i]
        klass="d20-node d20-marked" if i in highlight_nodes else "d20-node"
        shapes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="25" class="{klass}"/>')
        shapes.append(f'<text x="{x:.1f}" y="{y+7:.1f}" class="d20-node-key">{escape(str(v))}</text>')
        shapes.append(f'<text x="{x:.1f}" y="{y+52:.1f}" class="d20-node-index">i={i}</text>')
    return ('<svg class="d20-tree" viewBox="0 0 '+str(width)+' '+str(height)+'" role="img" '
            'aria-label="完全二叉树，圆内为关键字，下面为数组下标">'+''.join(shapes)+'</svg>')

def task(input_html, prompt_html, answer_html, *, title="展开核对答案与依据"):
    return '<div class="d20-task">'+task_workspace(
        input_html,prompt_html,answer_html,title=title,layout="stacked")+'</div>'

def add(pid, title, body, section=None, *, goal, activity="观察、解释与追问",
        role="content", withheld=()):
    COURSE.add(pid,title,'<div class="d20-lesson">'+body+'</div>',
               section=section,goal=goal,activity=activity,role=role,
               withheld_results=withheld)

def trace_view(name, initial_html, description):
    """Use CourseDeck's shared, checkable manual-step player for formal traces.

    Panels are present in source; lesson.js fills them with the pure trace
    snapshots. Shared deck.js owns prev/next/reset navigation; no competing
    D020-specific button controller is attached.
    """
    states = {"merge": 7, "radix": 12}[name]
    panels = ''.join(
        '<section class="tree-step-panel"' + (' hidden' if i else '') + '>'
        '<div class="d20-step-label">状态 ' + str(i+1) + '</div>'
        '<div class="d20-live">' + description + '</div></section>'
        for i in range(states)
    )
    return ('<div class="d20-necessary"><strong>固定输入（演示过程中持续保留）</strong>'
            +initial_html+'</div><div class="d20-viewer" id="'+name+'-viewer" data-tree-player>'
            +panels
            +'<div class="toolbar d20-buttons">'
            '<button type="button" data-step="prev" id="'+name+'-prev">上一步</button>'
            '<span class="tree-step" id="'+name+'-stage">步骤 1 / '+str(states)+'</span>'
            '<button type="button" data-step="next" id="'+name+'-next">下一步</button>'
            '<button type="button" data-step="reset" id="'+name+'-reset">重置</button>'
            '</div></div>')

# 01—03: prerequisite diagnosis; do not presume D019 was taught or mastered.
add("cover", "排序：怎样组织和利用已有信息？",
    '<link rel="stylesheet" href="lesson.css">'
    '<script defer src="prototypes/trace.js"></script><script defer src="lesson.js"></script>'
    +lead("相同的排序任务，为什么会产生不同的算法机制和计算代价？")
    +box("本讲的主问题",
         P("反复取最值，可以维护什么结构？两个子序列已有序，可以怎样直接利用？"
           "关键字具有数位结构时，又能利用哪些信息？")
         +P("在算法正确性、时间、空间和稳定性要求下，如何作出有条件的选择？"))
    +note("《数据结构与算法》 · D020 · 第 8 章 8.4–8.6 · 90 分钟"),
    goal="提出本讲以可复用信息设计排序算法的主问题", role="cover")
COURSE.outline(title="这节课通过哪些问题理解和选择排序算法？")
COURSE.start_section("selection")

add("sort-contract-recall", "排序结果有序，就一定满足要求吗？",
    task(
      box("已知输入：记录身份与关键字",seq([3,1,3,2],["甲","乙","丙","丁"])
          +P("输出要求：按关键字非递减，且每一条输入记录恰好保留一次。")),
      P("<strong>先判断：</strong>输出 A：1乙、2丁、3甲、3丙；输出 B：1乙、2丁、3丙、3甲。"
        "两者是否满足基本排序契约？哪一个保持稳定性？"),
      P("两个输出都满足<strong>有序、记录保持</strong>，均可终止；只有 A 保留相同关键字 3 的甲在丙前，因此 A 稳定。")
      +P("稳定性是附加要求，不是排序正确性的全部定义。"),
    ), "selection", goal="区分有序性、记录保持与稳定性的不同职责",
    role="exercise",activity="诊断 D019 先修理解，独立判断后核对")

# 03—16: selection, tournament tree and heap.
add("simple-selection", "为什么简单选择排序要反复扫描剩余元素？",
    box("在尚未排序部分反复找最小值",
        seq([4,1,3,2])+P("第一轮最小值 1 放到首位；之后仅在剩余三个元素中再找最小值。")
        +P("每轮已就位前缀增长，后缀仍可能无序。"))
    +cols(box("正确性不变量",P("前缀各记录已到最终位置，且不大于尚未处理的所有关键字。")),
          box("计算代价",P("对 n 条记录，比较次数 "+M(r"(n-1)+(n-2)+\cdots+1=\frac{n(n-1)}2")
                          +"，故为 "+M(r"\Theta(n^2)")+"。")))
    +note("简单选择交换最小值时可能颠倒相等关键字记录的先后：2甲、2乙、1丙 → 1丙、2乙、2甲。"),
    "selection",goal="解释简单选择反复扫描及其不稳定性、平方阶比较成本")
add("tournament-bridge", "树形选择能保存哪些比较结果？",
    task(
        cols(box("简单选择",P("每轮都在剩余序列重新寻找最值。")+seq([8,3,6,2])),
             box("树形选择（竞赛树）",P("比较 8 与 3 得 3，比较 6 与 2 得 2；再比较 3 与 2，根得到最小值 2。")
              +P("现在取出 2，把该叶子暂记为无效（比较时等价于 +∞）；其他叶子不变。需要重新计算哪些比较？"))),
        P("<strong>E1a 独立判断：</strong>如果最小值 2 已被取出，为什么不需要重新比较所有未变化的叶子对？"),
        P("原来 8 与 3 的比较仍有效，左支胜者仍是 3；右支改为 6 胜出，根再比较 3 与 6 得到 3。只需更新被替换叶子的胜者路径。")
        +P("树形选择的比较结果存储方式并不等同于二叉堆的父子堆序。"),
    ), "selection", goal="说明树形选择复用胜者路径的机制并区分堆",role="exercise",
    activity="E1a 独立比较结构信息")
add("heap-opportunity", "反复取最大值，能否维护一个合法结构？",
    lead("简单选择每轮把最小值放到左边；换一个方向，每轮把最大值放到右边，能否减少重复寻找？")
    +cols(box("仍然要完成的操作",P("找到当前最大值 → 放到未排序区最右端 → 继续处理其余记录。")),
          box("希望复用的信息",P("让最大值位于根，删除它后沿较短路径恢复关系，而不是重新扫描所有剩余记录。")))
    +highlight("最大堆将把这一想法实现为一种可维护的结构；接下来明确它必须满足什么性质。"),
    "selection",goal="由选择排序成本引出可维护的最值结构")
add("heap-contract", "什么样的完全二叉树才是最大堆？",
    cols(box("最大堆（max-heap）＝形状 + 父子堆序",
             tree([9,7,8,4,5,6,3])
             +P("形状：完全二叉树，末层从左至右连续填充。顺序：每个父结点关键字不小于孩子。")),
         box("只满足形状还不够",
             seq([2,5,7,3,4,6,8])
             +P("虽然可以按层序存入完全二叉树，根 2 小于孩子 5 和 7，因此不是最大堆。")
             +P("堆序只约束父子，不直接规定同层与左右子树之间的全局顺序。")))
    +highlight("沿根到任意结点逐层比较，能推出最大堆的根是整个结构的最大元素。"),
    "selection",goal="区分完全二叉树形状与局部堆序，并由传递性推出根为最大值")
add("heap-array", "完全二叉树为什么便于数组顺序存储？",
    box("同一堆：树图与从 0 开始的层序数组",
        tree([9,7,8,4,5,6,3])+seq([9,7,8,4,5,6,3]))
    +highlight("父结点 i 的左孩子下标 "+M(r"2i+1")+"，右孩子下标 "+M(r"2i+2")
               +"；孩子下标必须小于有效长度 heapSize。")
    +note("heapSize 是当前有效堆前缀的长度，初始为 n，堆排序每轮缩小 1。"
          "从 0 起下标，非根结点 i 的堆序条件为 "
          +M(r"A[\lfloor(i-1)/2\rfloor]\ge A[i]")+"；例如 i=2 的孩子下标为 5、6。"),
    "selection",goal="建立树形与数组下标的一一对应及边界检查")
add("heap-vs-bst", "最大堆为什么不能像 BST 那样定向查找？",
    cols(box("回顾二叉搜索树（BST）",P("BST 的左／右子树有整体的关键字顺序约束，比较目标与根即可排除一侧。")),
         box("最大堆",tree([9,7,8,4,5,6,3])
             +P("只知每个父结点不小于孩子，不知左、右子树中的目标关键字分布。")))
    +highlight("堆保证取得最值；不能仅因目标比根小，就决定只往左子树或右子树查找。"),
    "selection",goal="借 D017 的 BST 顺序性质排除堆查找方向误解")
add("sift-down", "一个根结点偏小，怎样沿路径恢复堆序？",
    cols(box("调整前：两侧孩子子树已经是堆",
             tree([4,9,8,7,5,6,3],highlight_nodes=[0])+seq([4,9,8,7,5,6,3])),
         box("调整后：新根恢复最大堆",
             tree([9,7,8,4,5,6,3])+seq([9,7,8,4,5,6,3])))
    +highlight("向下调整（siftDown）：与较大的孩子比较；只有当前结点更小时才交换，"
               "可能违反堆序的位置沿一条路径向下移动。")
    +note("本例 4 先与 9 交换，再与 7 交换；前提是两个孩子子树原本均为堆。"
          "完全二叉树高度为 Θ(log n)，单次下沉最坏 O(log n)。"),
    "selection",goal="在两个孩子子树已成堆的前提下推导向下调整")
add("sift-counterexample", "从根下沉一次，就能整理任意无序数组吗？",
    task(
        box("反例：孩子子树并未先成为最大堆",
            seq([2,5,7,3,4,6,8])+P("只从根执行一次向下调整 siftDown(0,n)，不执行自底向上建堆。")),
        P("<strong>先推演：</strong>按“交换较大孩子”规则下沉后，整个数组是不是合法最大堆？请指出仍违反堆序的一条边。"),
        seq([7,5,8,3,4,6,2],focus=[0,2])
        +P("不是。根 7 小于右孩子 8；原右子树本身并不是堆。局部调整必须满足两个孩子子树已成堆的前置条件。"),
    ), "selection", goal="借错误根下沉反例明确 siftDown 的前置条件",role="exercise",
    activity="独立诊断失败条件并核对")
add("build-heap", "为什么自底向上建堆从最后一个非叶结点开始？",
    box("主例：由任意输入构造合法最大堆",
        seq([5,3,8,2,7,1,6])
        +P("自底向上建堆（buildHeap）：最后非叶结点 "
           +M(r"\lfloor n/2\rfloor-1=2")+"；按 i=2、1、0 调用 siftDown。")
        +P("i=2 不交换；i=1 后为 [5,7,8,2,3,1,6]；i=0 下沉完成：")
        +seq([8,7,6,2,3,1,5]))
    +highlight("叶子结点天然为堆；逆序处理保证每次 siftDown 时两个孩子子树已成堆。")
    +note("自底向上建堆整体是 Θ(n)：靠近叶子的结点多、所需下沉距离短；不同于逐个插入的建堆代价。"),
    "selection",goal="由已成堆的小子树递推构造整个堆，区分单次与总工作量")
add("heap-independent", "换一个数组，你能独立完成建堆和一次提取吗？",
    task(
        box("P1：新数组；规定从 i=2、1、0 依次下沉",seq([4,1,7,3,6,2,5])
            +P("按 0 起下标执行自底向上建堆，再交换根与最后元素，缩小有效堆并修复。")),
        P("<strong>先独立推演：</strong>写出建堆结果、提取最大值后的有效堆前缀与已排序后缀，并解释修复依据。"),
        box("建堆过程",P("i=2：不变；i=1：[4,6,7,3,1,2,5]；i=0：完成建堆。")
            +seq([7,6,5,3,1,2,4]))
        +box("提取最大值 7 并修复",P("先交换根与末尾，再令 heapSize=6，下沉修复：")
            +seq([6,4,5,3,1,2,7],active=6))
        +P("当前有效堆前缀是 [6,4,5,3,1,2]，最终就位后缀为 [7]。如果只要求“任意合法最大堆”，答案未必唯一；此题规定了算法过程。"),
    ), "selection",goal="在不同输入上独立完成建堆与一次堆顶提取",role="exercise",
    activity="P1 独立预测，再展开全部状态")
add("heapsort-boundary", "取走堆顶之后，哪一部分保持什么性质？",
    task(
       box("有效堆与最终就位区域",seq([6,4,5,3,1,2,7],active=6)
           +P("已提取最大值 7；原始数组长度 n=7，当前 heapSize=6。")),
       P("<strong>E1b 独立解释：</strong>左边六个元素必须满足什么？右边一个元素为什么不需要再参与比较？多次提取后哪个部分扩大？"),
       P("左边 [0,heapSize) 仍是最大堆；右侧 [heapSize,n) 为已经按升序确定最终位置的后缀。每轮先选剩余最大值，再恢复有效堆性质。")
       +P("建堆 Θ(n)，反复 n−1 轮最坏 O(log n) 调整；迭代数组实现总最坏 Θ(n log n)、额外工作空间 O(1)。"),
    ), "selection",goal="独立解释堆前缀和已排序后缀的两个保持性质",role="exercise",activity="E1b 不变量判断")
add("heap-checkpoint", "为什么这次局部修复能够保证整个堆正确？",
    task(
        box("堆调整的必要前提",seq([4,9,8,7,5,6,3])
            +P("当前根可能违反堆序，但左右孩子子树各自是最大堆。")),
        P("<strong>判断：</strong>为什么先比较两个孩子？如果先交换较小孩子会怎样？最坏需要调整多少层？"),
        P("必须选较大孩子，使交换后新父结点不小于两个孩子。潜在违反关系只随原根下移；调整最多经过 O(log n) 层。")
        +P("关键依据：调整前两侧子树已是堆；每次交换仅把可能的违例沿当前路径下移。"),
    ), "selection",goal="判断堆局部调整的前置条件、交换方向和代价",role="exercise",
    activity="阶段检查，必要时补救")

# 17—23: merge and recursion.
COURSE.start_section("merge")
add("merge-opportunity", "两个输入已有序，为什么不必重新排序？",
    cols(box("左有序输入 L",seq([2,5,8])),
         box("右有序输入 R",seq([1,6,7])))
    +highlight("有序归并（merge）：每侧未处理首元素都是该侧剩余的最小值；"
               "只比较两个首元素，就能取出全部剩余记录中的一个最小值。"),
    "merge",goal="识别有序输入的信息价值并建立线性归并的前提")
add("merge-trace", "两个有序序列如何逐步合成完整结果？",
    trace_view("merge",'<div class="d20-compact-input">'
               '<div><strong>固定输入 L（原左半段）</strong>'+seq([2,5,8],["a","b","c"])+'</div>'
               '<div><strong>固定输入 R（原右半段）</strong>'+seq([1,6,7],["d","e","f"])+'</div></div>',
               "当前候选、指针位置及输出前缀同步呈现。")
    +note("只比较两侧首候选；某一侧耗尽后追加另一侧剩余部分。"),
    "merge",goal="通过连续状态解释线性归并与输出前缀",activity="逐步预测和核对")
add("stable-merge-independent", "相等关键字的记录，应当先从哪边取？",
    task(
        cols(box("原记录的左半段 L",seq([2,5,8],["甲","乙","戊"])),
             box("原记录的右半段 R",seq([2,6,7],["丙","丁","己"]))),
        P("<strong>P2 独立任务：</strong>归并两段分别已排序的记录；关键字都为 2 时如何选择？请写出完整身份顺序，并解释为何这样稳定。"),
        box("稳定归并后的完整输出",
            seq([2,2,5,6,7,8],["甲","丙","乙","丁","己","戊"]))
        +P("左半段来自原序列的较早连续位置，遇到相等关键字先取左方的 2甲，保留其早于 2丙 的原始先后。"),
    ), "merge",goal="独立归并含相同关键字的完整记录并解释稳定性",role="exercise",
    activity="P2 独立判断与完整结果核对")
add("merge-invariant", "为什么每次选择不会遗漏更小的元素？",
    cols(box("初始化",P("输出 B 为空；两个输入 L/R 均有序，位置 i=j=0。")),
         box("每次保持",P("两侧都未耗尽时取较小的首候选（相等先取左侧）；"
                          "若某侧耗尽，直接追加另一侧剩余有序部分。")))
    +highlight("循环不变量：输出 B 是已取记录构成的有序前缀；其元素来自两侧输入且不遗漏，"
               "每次追加的都是当前剩余记录的最小关键字。")
    +note("终止时两侧元素均已取出，故全部记录有序且无遗漏；这一论证不由动画流畅性代替。"),
    "merge",goal="用初始化、保持与终止解释归并操作的正确性")
add("merge-recursion", "递归为什么能保证每次 Merge 的输入已排序？",
    task(
       box("从局部归并到完整排序",seq([4,1,3,2])
           +P("归并排序（merge sort）：先拆成 [4,1] 与 [3,2]，分别递归排序到单元素，"
              "再将已排序子序列归并。")),
       P("<strong>E2 独立判断：</strong>为什么不能直接把任意两段无序序列交给 Merge？递归排序究竟为最终合并建立了哪个前提？"),
       P("基本情形：长度 0/1 天然有序；归纳步骤：左右各自递归排序得到 [1,4] 和 [2,3]，它们都满足 Merge 的有序输入前提，再合并为 [1,2,3,4]。")
       +P("回顾 D019：快速排序先划分（Partition）再递归；归并排序先递归排好左右子序列，"
          "再用归并（Merge）形成整体有序。"),
    ), "merge",goal="独立解释递归排序怎样建立 Merge 的有序输入前提",role="exercise",
    activity="E2 递归与组合的正确性条件")
add("merge-cost", "归并排序的对数层级与线性工作怎样相乘？",
    cols(box("每一层的工作量",P("两个有序序列合并，每条记录最多被本层写入一次，总代价 "+M(r"\Theta(n)")+"。")),
         box("递归深度",P("每层问题约减半，层数约 "+M(r"\log_2 n")+"。")))
    +highlight("标准数组实现时间 "+M(r"\Theta(n\log n)")+"；通过额外数组缓冲归并，辅助空间 "+M(r"O(n)")+"。")
    +note("与堆排序具有相同最坏时间阶，但原地性和稳定性条件不同；不能把递归分治四字当作复杂度证明。"),
    "merge",goal="由线性归并和递归层数解释时间及标准数组空间")

# 24—29: radix and FIFO-linked buckets.
COURSE.start_section("radix")
add("radix-opportunity", "整数关键字有数位结构，能否直接分桶？",
    cols(box("输入条件：可以读取关键字的数位",
             P("本讲只考虑非负整数。十进制基数 b=10，每一位的取值 0–9，"
               "可作为桶下标；位数不足时左侧补零。")),
         box("新机制：基数排序（radix sort）",
             P("最低有效位优先（LSD）先按个位、再按十位等逐轮分配与收集；"
               "不是每轮重新做通用关键字比较。")))
    +highlight("下一步先观察怎样分桶，再回答：为什么每个桶里的记录顺序不能随意改变？"),
    "radix",goal="由关键字的可分解表示引出基数排序和 LSD 数位次序")
add("radix-buckets", "从个位到十位，分配与收集怎样推进？",
    box("示范输入，按个位分配到十个桶",seq([21,13,12,22])
        +P("个位为 1 的桶：21；个位为 2 的桶：12 → 22；个位为 3 的桶：13。其余桶为空。"))
    +cols(box("第一轮：个位",seq([21,12,22,13])+P("按桶号从小到大，桶内从头到尾收集。")),
         box("第二轮：十位",seq([12,13,21,22])+P("相同十位记录保留上一轮已经建立的个位顺序。")))
    +highlight("每轮仅按当前数位分组；同一桶内按进入顺序收集（先进先出），"
               "让上一轮已经建立的低位顺序不被破坏。"),
    "radix",goal="手工追踪 LSD 两轮数位分配和稳定收集")
add("radix-linked-trace", "链式桶怎样保持每一条记录的先后顺序？",
    trace_view("radix",'<div class="d20-compact-input"><div><strong>固定输入（带记录身份）</strong>'
               +seq([21,13,12,22],["A","B","C","D"])+'</div></div>',
               "十个桶初始为空；分配时追加到桶尾，按桶号从桶头顺序收集。")
    +note("链式桶的 head/tail/next：回顾单链表，next 指向后一条记录；head 指向桶首，tail 指向桶尾；"
          "新增记录接在 tail.next 后，按桶号依次从 head 顺序收集，保持先进先出。"),
    "radix",goal="认识 head/tail/next 与稳定分配、收集之间的语义关系",activity="动态预测桶内链接顺序")
add("radix-independent", "新输入的一轮分配和收集，你能独立完成吗？",
    task(
       box("P3：整数关键字及记录身份",seq([42,11,32,21],["甲","乙","丙","丁"])
           +P("以十进制个位数为本轮排序键，桶内必须保持记录先后。")),
       P("<strong>独立填写：</strong>桶 1 和桶 2 内分别是什么链接次序？按桶号收集后的完整记录序列是什么？"),
       P("桶 1：11乙 → 21丁；桶 2：42甲 → 32丙。按桶号收集得到：")
       +seq([11,21,42,32],["乙","丁","甲","丙"])
       +P("一轮个位排序后并非已经全局有序。下一页讨论：之后处理更高位时，为什么必须保持桶内原来的顺序？"),
    ), "radix",goal="独立完成新的数位输入的一轮稳定桶分配／收集",role="exercise",
    activity="P3 先预测桶内链接，再核对最终记录")
add("radix-stability", "为什么不能随意改变同桶记录的顺序？",
    task(
        box("已建立的低位顺序",
            P("个位处理后，21 和 22 的顺序为 21→22；二者十位都为 2。"
              "现在进入十位桶，假设改为从桶头插入、逆序收集。")),
        P("<strong>快速独立判断：</strong>十位桶会变成 21→22 还是 22→21？"
          "为什么这样的收集方式不能保证 LSD 的最终排序正确？"),
        P("逆序得到 22→21，而实际 21<22。十位相同时必须保留已经按个位建立的次序；"
          "因此要稳定分配，按进入顺序从桶头到桶尾收集。"),
    )
    +note("若关键字有 d 位、每位基数为 b，桶访问及记录移动均为常数成本，"
          "LSD 时间为 "+M(r"O(d(n+b))")+"；不能无条件称为 O(n)。"),
    "radix",goal="独立用十位桶倒序反例解释 FIFO 对 LSD 正确性的必要性",role="exercise",
    activity="判断后展开反例答案")

# 30—34: comparison and authentic choice.
COURSE.start_section("choice")
add("comparison-model", "排序复杂度结论为什么必须带上计算条件？",
    task(
        cols(box("两种已学计算机制",
                 P("堆与归并主要依据关键字大小比较组织排序；"
                   "LSD 在受约束的整数键上使用数位和桶下标。")),
             box("两条待判断主张",
                 P("A：“堆排序必然需要一个长度为 n 的辅助数组。”")
                 +P("B：“所有排序都具有 "+M(r"\Omega(n\log n)")+" 的最坏时间下界。”"))),
        P("<strong>E3 独立诊断：</strong>两条主张能否无条件成立？"
          "分别指出对算法实现、允许操作或关键字条件的隐藏要求。"),
        P("A 不成立：迭代数组堆排序原地交换，可仅需 "+M(r"O(1)")+" 辅助工作空间。")
        +P("B 不成立：通用比较决策树的 "+M(r"\Omega(n\log n)")+
           " 下界针对互异关键字的最坏比较次数；"
           "LSD 等算法利用了数位信息，不能把该结论推广到全部排序计算模型。")
        +P("把“关键字比较次数”直接等同于所有实现的真实运行时间，也是不成立的。"),
    ), "choice",goal="诊断算法工作空间与比较决策树下界的成立条件",role="exercise",
    activity="E3 先判断条件，再核对模型")
add("choice-independent", "数据条件变化后，怎样有依据地选择排序机制？",
    task(
        box("P4：一百万条带记录身份的数据；场景条件逐步改变",
            P("A：非负整数关键字 0–100，要求稳定，允许 "+M(r"O(n)")+" 额外空间。")
            +P("B：关键字变成任意可比较类型，仍要求稳定、允许 "+M(r"O(n)")+" 空间。")
            +'<details class="d20-extension"><summary>拓展 C · Top-k（完成 A/B 后按需展开）</summary>'
            +P("C（拓展）：仅取前 k 大（"+M(r"2\le k\ll n")+"），无需整体排序；"
               "此情境不要求稳定，遇到边界处相同关键字可任选满足大小的 k 条记录。"
               "提示：最小堆是最大堆的对偶，父结点不大于孩子，根为堆内最小值。")
            +'</details>'),
        P("<strong>P4 课堂最低证据（A、B 必答）：</strong>用已学的归并、堆或 LSD，"
          "分别选择可行方法，并比较至少两种方法的关键前提。"
          "<strong>C 为时间允许时的迁移挑战</strong>：由已给出的最小堆对偶推导 Top-k 维护。"
          "每一项写清数据约束与适用条件。"),
        P("A：将 0–100 补成三位十进制整数，稳定 LSD 可逐位分桶，"
          "b=10、d=3，时间 "+M(r"O(3(n+10))")+"；标准稳定归并也可用。")
        +P("B：通用稳定数组归并排序适用于任意可比较键，"
           "最坏时间 "+M(r"\Theta(n\log n)")+"、辅助空间 "+M(r"O(n)")+
           "；不宜按整个巨大键域直接分配桶。")
        +P("候选并不唯一；必须结合键的表示、稳定性、内存与输出需求说明适用条件。")
        +'<details class="d20-extension"><summary>拓展 C · 核对 Top-k 参考方案</summary>'
        +P("C：维护容量 k 的最小堆，堆根是已保留的前 k 大记录中的最小关键字；"
           "后续记录只有更大时才替换根并下沉，最坏 "+M(r"O(n\log k)")+
           " 时间、"+M(r"O(k)")+" 额外空间（这里 k≥2）。")
        +'</details>',
    ), "choice",goal="基于已学机制与给定提示，在条件变化时独立选择可行算法",role="exercise",
    activity="P4 已学机制迁移与对偶推导")
add("mechanism-synthesis", "不同排序算法究竟复用了哪一种信息？",
    '<div class="d20-compare">'
    +box("简单／树形／堆选择",P("简单选择取最小值放左侧；竞赛树复用胜者路径；最大堆取最大值放右侧。"))
    +box("归并排序",P("两个已排序输入 → 只比较两侧首候选 → 合成更长有序序列。"))
    +box("基数排序",P("关键字有限数位 → 逐轮稳定分配 → 保留先前低位次序。"))
    +'</div>'
    +highlight("算法并非只看名字和复杂度表：明确计算对象，维护可利用的信息，证明保持性质，再判断代价与条件。"),
    "choice",goal="综合三类信息组织机制与其正确性、代价边界")
add("homework-bridge", "课后作业：怎样独立预测、运行和解释？",
    '<div class="d20-homework">'
    +P("<strong>A · 教材作业（必做）</strong>：第 8 章选择题 <strong>(8)(11)(13)</strong>；"
       "应用题 <strong>(1)⑧ 二路归并</strong>。选择题写出一句依据，推演题保留必要中间状态。")
    +P("<strong>B · C11 程序实践（必做）</strong>：先独立预测<strong>新输入 [3,8,1,6,2,7,4]</strong>"
       " 自底向上建堆及第一次提取最大值后的堆前缀、有序后缀；"
       "再用 C11 程序核对，解释向下调整的前置条件及预测与实测是否一致。")
    +'<pre class="d20-code"><code>gcc -std=c11 -Wall -Wextra -Werror -pedantic code/sorting_d020_demo.c -o d020_demo\n./d020_demo heap 3 8 1 6 2 7 4\n./d020_demo --self-test</code></pre>'
    +P("程序可复制到个人电脑运行，不要求在 Git 仓库内运行或向公共仓库 push。")
    +'<p class="d20-homework-note">A/B 均必做；选做不提交：选择题 (10)(12)(14)(15)、'
     '应用题 (1)⑥⑦、应用题 (2) 链式基数排序完整三轮。按课程作业规范提交飞书文档，'
     '附 3–5 行真实过程记录；若与 D019 同周收取，须核对累计负担。</p>'
    +'</div>',
    goal="发布 A/B 可执行作业、输入与提交边界",role="closing",
    activity="说明正式课堂任务与本地运行条件")

SLIDES=COURSE.finalize()
assert len(SLIDES)==34, (len(SLIDES), [p["id"] for p in COURSE.pages])
PAGE_IDS=[p["id"] for p in COURSE.pages]
