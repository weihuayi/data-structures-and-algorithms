"""D021：正式教学页面主源。通过 tools/deck/build.py D021 生成 HTML。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "deck"))
from components import CourseDeck, Section, task_workspace

DECK_ID = "D021"
TITLE = "从校园生活到计算问题"
MATH = False
DEPENDENCIES = ["course/assignments/campus-computing-practice/README.md"]
COURSE = CourseDeck([
    Section("learning", "知识学习与现实问题", "学过算法，怎样才能用它理解和解决问题？", "回顾学习经验，辨认知识、理解与独立应用的区别。", "建立从知识学习走向现实实践的动机"),
    Section("campus", "观察与理解湘潭大学校园", "我们每天生活的校园，有哪些现象和需求值得研究？", "从学生真实体验出发，讨论教学、空间、交通、服务及资源之间的联系。", "发现问题，区分观察、推断和待验证解释"),
    Section("model", "从现实问题到计算问题", "一个真实问题怎样变成边界明确的计算任务？", "识别对象、信息、关系、假设、输入、输出与目标。", "在具体情境中建立计算抽象意识"),
    Section("knowledge", "重新认识数据结构与算法", "已经学过的知识怎样共同支持一次计算？", "回顾表示、操作、算法、正确性、代价和验证的关系。", "回收课程主线，形成后续复习导航"),
    Section("practice", "期末综合计算实践", "从校园问题中可以提取哪些适合自己尝试的任务？", "了解三个期末实践题目及其边界，在授课结束时统一发布。", "理解期末个人实践的目的及共同要求"),
])

COURSE.add("cover", "从校园生活到计算问题",
    "<link rel=\"stylesheet\" href=\"lesson.css\"><div class=\"d21-cover\"><p class=\"d21-cover-lead\">我们怎样发现身边值得研究的问题，并让数据结构与算法发挥作用？</p><div class=\"d21-cover-line\"><strong class=\"d21-cover-label\">核心主线</strong><div class=\"d21-cover-sequence\">观察现实 → 理解问题 → 计算抽象 → 调用已有知识</div></div><p class=\"d21-cover-note\">D021 · 数据结构与算法 · 综合复习与计算实践导入</p></div>",
    role="cover", label="课程导入", goal="从理论知识学习转向真实问题认识", activity="观察、思考与追问")

COURSE.outline(title="今天我们将怎样重新认识数据结构与算法？")
COURSE.start_section("learning")
COURSE.add("knowledge-vs-ability", "学过一种算法，就意味着会解决问题吗？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>教材中的任务</h3><p>给出一个图，要求完成 BFS。</p><p>问题和输入已经定义好了。</p></div><div class=\"panel\"><h3>现实中的任务</h3><p>某处道路施工后，学生怎样到教室？</p><p>先判断需要什么信息、求什么结果。</p></div></div><div class=\"quote\">会执行算法与会提出并解决计算问题，是不同层次的能力。</div>",
    section="learning", role="content", goal="区分知识记忆、算法执行和独立问题解决", activity="先独立回忆自己遇到的困难，再听同学回答")

COURSE.add("learning-purpose", "学习怎样帮助我们认识和改善生活？",
    "<p class=\"lead\">所学知识能否帮助我们理解以前不理解的现象？</p><div class=\"columns d21-columns\"><div class=\"panel\"><h3>适应环境</h3><p>认识已有规则，学会使用已有工具。</p></div><div class=\"panel\"><h3>改善环境</h3><p>观察、提出问题、分析原因、探索改变的可能性。</p></div></div><p>不必现在就有答案。先从自己真正关心的问题开始。</p>",
    section="learning", role="content", goal="把学习能力与现实认识建立联系", activity="教师追问学生已有体验，不要求表态")

COURSE.start_section("campus")
COURSE.add("daily-activities", "我们每天在校园中经历哪些活动？",
    "<table><thead><tr><th scope=\"col\">活动</th><th scope=\"col\">观察线索</th></tr></thead><tbody><tr><td>上课、换教室</td><td>何时、何地？怎样到达下一处？</td></tr><tr><td>就餐、取快递</td><td>什么时候到达？等待多久？</td></tr><tr><td>自习、运动</td><td>空间何时开放、何时空闲？</td></tr></tbody></table><p class=\"small\">你还经历过哪些活动？这些活动之间会不会相互影响？</p>",
    section="campus", role="content", goal="从真实活动而不是预设技术分类开始", activity="学生回忆自己的一天，补充活动")

COURSE.add("open-discussion", "你遇到过哪些值得改善的校园问题？",
    "<p class=\"lead\">从自己在湘潭大学的真实经历出发，提出一个值得进一步理解的问题。</p><div class=\"columns d21-columns\"><div class=\"panel\"><h3>先描述</h3><p>发生了什么？在何处、何时？谁受到影响？</p></div><div class=\"panel\"><h3>再追问</h3><p>你亲眼观察到了什么？哪些只是推测？还需要知道什么？</p></div></div><p class=\"small\">先独立思考，再自愿交流；不分组、不提交，不公开个人信息。</p>",
    section="campus", role="content", goal="自主提出真实问题并区分事实与猜测", activity="教师留白；先听学生，不预先给三个题目")

COURSE.add("timetable-impact", "一份课表会怎样影响学生的学习与生活？",
    "<figure class=\"d21-figure\"><svg viewBox=\"0 0 930 210\" role=\"img\" aria-label=\"教学构造时间轴：同一学生上午先在甲楼上课，再在乙楼上课，两活动间存在移动时间窗口\"><g fill=\"#eef4f9\" stroke=\"#246c9d\" stroke-width=\"2\"><rect x=\"30\" y=\"45\" width=\"275\" height=\"92\" rx=\"8\"/><rect x=\"625\" y=\"45\" width=\"275\" height=\"92\" rx=\"8\"/></g><g font-size=\"27\" fill=\"#152943\" text-anchor=\"middle\"><text x=\"167.5\" y=\"82\">第一门课 · 甲楼</text><text x=\"167.5\" y=\"115\">08:00—09:40</text><text x=\"762.5\" y=\"82\">第二门课 · 乙楼</text><text x=\"762.5\" y=\"115\">10:00—11:40</text><text x=\"465\" y=\"70\">课间活动</text><text x=\"465\" y=\"105\">移动、休息</text></g><path d=\"M315 150 H615\" stroke=\"#d94d16\" stroke-width=\"4\"/><path d=\"M315 140 V160 M615 140 V160\" stroke=\"#d94d16\" stroke-width=\"4\"/><text x=\"465\" y=\"190\" text-anchor=\"middle\" font-size=\"25\" fill=\"#152943\">可用时间窗口</text></svg><figcaption>教学构造情境，不代表实际课表；图中时间段宽度不按比例。</figcaption></figure><p>如果下一门课改在同一栋楼，课间体验会怎样变化？要判断是否来得及，还缺少什么信息？</p>",
    section="campus", role="content", goal="发现活动次序和空间移动之间的联系", activity="请学生结合自己的经历说明，不展示含身份的课表")

COURSE.add("campus-space", "我们怎样认识校园中的空间与道路？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>几何信息</h3><p>地点在哪里？两点直线距离是多少？道路实际有多长？</p></div><div class=\"panel\"><h3>连接与通行信息</h3><p>哪些地点直接连通？道路是否双向、开放？能否通行？</p></div></div><div class=\"quote\">地图上很近的两个点，可能被围栏、建筑或道路规则隔开。</div>",
    section="campus", role="content", goal="区分空间几何、连接关系与通行规则", activity="结合实际熟悉地点讨论；有经授权地图可现场展示")

COURSE.add("traffic", "为什么有些道路在特定时段会拥堵？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>先观察</h3><p>在哪个地点、哪个时段拥堵？是行人、车辆还是两者相互影响？</p></div><div class=\"panel\"><h3>再检验解释</h3><p>活动集中结束？道路容量不足？需要按时段记录流量、出行需求与通行时间。</p></div></div><p class=\"small\">这里列的是待检验的解释。不能只凭某一次体验认定拥堵原因。</p>",
    section="campus", role="content", goal="从观察现象走向提出可检验解释", activity="学生提出假设，教师追问如何验证")

COURSE.add("service-wait", "为什么有些校园服务需要长时间等待？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>请求一侧</h3><p>什么时候到达？有多少请求？每个请求需要怎样的服务？</p></div><div class=\"panel\"><h3>服务一侧</h3><p>有几个窗口？每次服务需要多久？按什么规则处理？</p></div></div><div class=\"quote\">等待时间与到达、服务能力及处理规则都可能有关。</div>",
    section="campus", role="content", goal="识别服务过程中的对象、事件与资源限制", activity="从食堂、快递等学生实际体验比较")

COURSE.add("resource-use", "校园中还有哪些资源可以更好地利用？",
    "<ul><li>教室、自习座位、实验室与体育场地。</li><li>什么时候有人需要？什么时候有空余？</li><li>不同人的需求冲突时，怎样作出合理安排？</li></ul><p class=\"small\">学生可以提出其他问题；有些问题需要管理、制度或沟通，并不一定适合用计算解决。</p>",
    section="campus", role="content", goal="扩大问题视野并明确计算不是唯一手段", activity="全班开放讨论，可跳转前面场景")

COURSE.add("campus-relations", "这些看似不同的问题之间有什么联系？",
    "<svg viewBox=\"0 0 960 300\" role=\"img\" aria-label=\"活动安排和路网分别形成出行需求和路径条件，共同影响交通运行\" style=\"width:100%;max-height:300px\"><defs><marker id=\"c-arrow\" markerWidth=\"7\" markerHeight=\"7\" refX=\"6\" refY=\"3.5\" orient=\"auto\"><path d=\"M0 0 L7 3.5 L0 7 Z\" fill=\"#536779\"/></marker></defs><rect x=\"35\" y=\"12\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"220\" y=\"52.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">教学与活动安排</text><rect x=\"555\" y=\"12\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"740\" y=\"52.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">校园空间与路网</text><rect x=\"35\" y=\"110\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"220\" y=\"150.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">出行需求</text><rect x=\"555\" y=\"110\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"740\" y=\"150.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">路径与通行条件</text><rect x=\"295\" y=\"225\" width=\"370\" height=\"60\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"480\" y=\"263\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">交通运行</text><path d=\"M220 77 V110\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/><path d=\"M740 77 V110\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/><path d=\"M220 175 V198 H390 V225\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/><path d=\"M740 175 V198 H570 V225\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/></svg><p>交通运行的观察结果，可以反过来支持课表安排、道路管理等方案的改进。</p><p class=\"small\">概念关系示意；不是完整智慧校园模型，也不是实际交通数据。</p>",
    section="campus", role="content", goal="认识校园运行中的部分承重关系", activity="学生解释一条关联，提出可能缺失的因素")

COURSE.add("research-connection", "校园中的问题怎样成为真实研究任务？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>真实研究中的问题</h3><p>排课怎样影响出行需求？校园地图怎样保存通行关系？怎样评价不同改进方案？</p></div><div class=\"panel\"><h3>需要形成的证据</h3><p>可靠的活动数据、空间与道路数据、实际运行观察，以及可核验的计算结果。</p></div></div><div class=\"quote\">从现实问题出发，用数据和计算帮助理解，再回到现实中检验。</div><details class=\"teacher-note\"><summary>教师讨论提示</summary><p>结合算海已核实且可公开的校园地图、排课研发或交通分析材料说明实际进展；区分已经完成、正在验证和尚未完成的工作。暂无可核验公开素材时，以现场讨论为主，不展示虚构成果。</p></details>",
    section="campus", role="content", goal="把学生生活与真实科研工程认识连接", activity="教师展示经确认可公开的真实素材（如有），区分事实与设想")

COURSE.start_section("model")
COURSE.add("not-start-code", "发现问题之后，为什么不能立即开始编程？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>现实需求</h3><p>希望自习空间得到更合理的利用。</p><p>涉及空间、时段、需求及使用规则。</p></div><div class=\"panel\"><h3>一个可计算的子问题</h3><p>给定某一时刻完整的座位记录，统计甲区的空闲座位数。</p><p>先明确输入、输出和条件。</p></div></div><div class=\"quote\">程序实现的是已经定义的计算任务，不是直接实现所有现实需求。</div>",
    section="model", role="content", goal="区分现实需求与定义好的计算任务", activity="学生指出哪些现实信息尚未进入模型")

COURSE.add("information", "要研究一个问题，需要哪些信息？",
    "<table><thead><tr><th scope=\"col\">对象</th><th scope=\"col\">属性或状态</th><th scope=\"col\">对象之间的关系</th></tr></thead><tbody><tr><td>座位</td><td>编号、占用状态</td><td>座位属于某区域</td></tr><tr><td>教学活动</td><td>开始、结束时间</td><td>活动发生在某地点；活动先后</td></tr><tr><td>道路</td><td>长度、通行状态</td><td>道路连接两个地点</td></tr></tbody></table><p class=\"small\">查询、排序、搜索是对这些信息进行的操作，不是对象之间的关系。</p>",
    section="model", role="content", goal="区分对象、属性、状态和关系", activity="指出不必要或尚缺失的信息")

COURSE.add("abstraction", "怎样从真实对象中提取计算对象？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>现实中的座位</h3><p>位置、材质、光照、附近插座、占用状态等。</p></div><div class=\"panel\"><h3>当前计算模型</h3><p>统计某区域空闲座位：保留座位编号、区域与占用状态。</p></div></div><div class=\"quote\">计算抽象：按目标保留必要信息，并明确忽略哪些因素。</div><p class=\"small\">如果改为推荐有插座的座位，当前模型还够用吗？</p>",
    section="model", role="content", goal="理解抽象由目标决定而不是任意丢弃信息", activity="追问：如果希望推荐有插座的座位，模型需要改变什么？")

COURSE.add("define-task", "怎样明确一个计算问题的输入和输出？",
    task_workspace("<table><thead><tr><th scope=\"col\">座位编号</th><th scope=\"col\">区域</th><th scope=\"col\">占用状态</th></tr></thead><tbody><tr><td>S1</td><td>甲</td><td>空闲</td></tr><tr><td>S2</td><td>甲</td><td>占用</td></tr><tr><td>S3</td><td>乙</td><td>空闲</td></tr></tbody></table><p class=\"small\">教学构造数据。同一时刻的完整记录，编号唯一，状态只有空闲或占用。</p>", "<p><strong>独立思考：</strong>若目标是统计甲区可用座位数量，需要哪些字段？应该输出什么？</p>", "<p>输入：每个座位的区域与占用状态，以及目标区域甲；唯一编号用于区分座位。</p><p>输出：甲区可用座位数为 1。该结果只对应给定时刻和完整记录。</p>", layout="stacked"),
    section="model", role="exercise", goal="在新任务中明确输入、输出与前置条件", activity="纸笔独立判断后展开核对，不提交", withheld_results=["甲区可用座位数为 1"])

COURSE.add("multiple-tasks", "同一个现实问题可以产生哪些计算任务？",
    "<table><thead><tr><th scope=\"col\">现实问题：出行不便</th><th scope=\"col\">可选择的计算目标</th></tr></thead><tbody><tr><td>有没有通路？</td><td>可达性判断</td></tr><tr><td>希望少经过道路</td><td>最少边数路径</td></tr><tr><td>希望尽快到达</td><td>在固定非负通行时间模型下求最小权路径</td></tr><tr><td>想理解拥堵原因</td><td>出行需求与运行数据分析</td></tr></tbody></table><p class=\"small\">目标、数据和假设不同，模型与计算方法也可能不同。</p>",
    section="model", role="content", goal="认识目标改变会改变模型与算法", activity="追问哪些任务需要更多数据")

COURSE.start_section("knowledge")
COURSE.add("representation-recall", "我们怎样组织和表示计算对象？",
    "<table><thead><tr><th scope=\"col\">对象或关系</th><th scope=\"col\">课程知识入口</th></tr></thead><tbody><tr><td>记录与线性关系</td><td><a href=\"../d001-problem-representation/index.html\">D001</a>–<a href=\"../d004-linked-list/index.html\">D004</a>：对象、顺序表、链表</td></tr><tr><td>字符串与层次</td><td><a href=\"../d007-string-pattern-matching/index.html\">D007</a>–<a href=\"../d010-forest-and-huffman/index.html\">D010</a>：串、树、森林</td></tr><tr><td>一般关系</td><td><a href=\"../d011-graph-modeling/index.html\">D011</a>：图、邻接矩阵、邻接表</td></tr></tbody></table><p class=\"small\">同一个抽象对象可以有多种表示；选择依据是任务需要哪些操作。</p>",
    section="knowledge", role="content", goal="回收对象、表示与抽象的课程主干", activity="学生解释为什么同一图可用矩阵或邻接表")

COURSE.add("mechanism-recall", "怎样利用已有信息组织计算过程？",
    "<table><thead><tr><th scope=\"col\">计算需求</th><th scope=\"col\">课程知识入口</th></tr></thead><tbody><tr><td>组织待处理工作</td><td><a href=\"../d005-stack-and-queue/index.html\">D005</a>–<a href=\"../d006-stack-and-recursion/index.html\">D006</a>：栈、队列、递归</td></tr><tr><td>访问、连接、路径与依赖</td><td><a href=\"../d012-graph-traversal/index.html\">D012</a>–<a href=\"../d015-topological-and-critical-path/index.html\">D015</a>：遍历、生成树、最短路径、拓扑与关键路径</td></tr><tr><td>查找与建立顺序</td><td><a href=\"../d016-search-order-and-asl/index.html\">D016</a>–<a href=\"../d020-selection-merge-and-synthesis/index.html\">D020</a>：查找、树表、散列、排序</td></tr></tbody></table><p class=\"small\">追问：你熟悉的一种算法利用了什么已有信息？</p>",
    section="knowledge", role="content", goal="回收主要算法机制并认识跨知识联系", activity="学生任选熟悉算法说明利用了什么信息")

COURSE.add("verify-choice", "为什么结果、正确性和计算代价都需要关心？",
    task_workspace("<p>某程序对一个小输入得到正确结果；另一个程序对同一输入也得到正确结果。</p>", "<p><strong>独立判断：</strong>能否仅凭这一次运行认定两个算法对所有合法输入都正确？能否据此判断哪一个更适合大规模输入？</p>", "<p>不能。样例通过不证明一般正确性；还需说明成立条件和算法依据，并设计边界测试。比较代价需说明输入规模、操作和成本模型。</p>", layout="stacked"),
    section="knowledge", role="exercise", goal="区分样例通过、正确性论证和复杂度判断", activity="独立判断后核对，回收先预测再运行再检查")

COURSE.start_section("practice")
COURSE.add("practice-a", "题目 A｜校园课表合理性分析",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>现实背景</h3><p>相邻教学活动可能发生在不同地点，课间移动时间可能不足。</p></div><div class=\"panel\"><h3>计算任务</h3><p>给定某位学生或同班学生一天内不重叠的课表与预计移动时间，检查相邻课程间隔是否足够。</p></div></div><p class=\"d21-task-note\"><strong>知识入口：</strong>记录、顺序表、排序与扫描。</p><p class=\"d21-task-note\"><strong>模型边界：</strong>课表检查不等于自动排课。</p>",
    section="practice", role="content", goal="认识课表检查的目标、对象和边界", activity="理解题意，不展示参考程序或正式答案")

COURSE.add("practice-b", "题目 B｜校园道路网络与路径分析",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>现实背景</h3><p>施工或其他通行条件变化，可能改变校园中的出行路线。</p></div><div class=\"panel\"><h3>计算任务</h3><p>给定无向道路网络，判断地点间可达性，求最少边数路径并比较道路关闭前后的结果。</p></div></div><p class=\"d21-task-note\"><strong>知识入口：</strong>图、队列、广度优先搜索（BFS）。</p><p class=\"d21-task-note\"><strong>模型边界：</strong>最少边数不等于实际最短距离。</p>",
    section="practice", role="content", goal="认识无权图搜索的任务与边界", activity="学生说明顶点、边可能表示什么")

COURSE.add("practice-c", "题目 C｜校园服务请求与等待时间分析",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>现实背景</h3><p>服务请求陆续到达一个窗口，服务时间和处理规则可能影响等待。</p></div><div class=\"panel\"><h3>计算任务</h3><p>给定到达时间和服务时长，按先到先服务（FIFO）规则模拟处理，计算等待时间。</p></div></div><p class=\"d21-task-note\"><strong>知识入口：</strong>记录、排序、队列语义、状态更新。</p><p class=\"d21-task-note\"><strong>模型边界：</strong>FIFO 是规则，不强制使用显式队列。</p>",
    section="practice", role="content", goal="认识请求、事件和状态更新的计算任务", activity="讨论模型不考虑哪些现实因素")

COURSE.add("practice-process", "怎样完整地经历一次计算实践？",
    "<div class=\"d21-flow\" role=\"group\" aria-label=\"完整计算实践路径\"><div class=\"d21-flow-node\"><span>1</span><strong>问题理解</strong></div><div class=\"d21-flow-node\"><span>2</span><strong>对象与表示</strong></div><div class=\"d21-flow-node\"><span>3</span><strong>算法设计</strong></div><div class=\"d21-flow-node\"><span>4</span><strong>C11 程序</strong></div><div class=\"d21-flow-node\"><span>5</span><strong>预测与验证</strong></div><div class=\"d21-flow-node\"><span>6</span><strong>结果与反思</strong></div></div><p>可以借助 AI、教材和同学交流；先自己尝试，实际运行、核对并解释。</p><p class=\"small\">下一讲将使用独立教学案例示范从计算问题到可验证程序。</p>",
    section="practice", role="content", goal="建立完整实践路径与独立判断责任", activity="教师说明后续学习如何支持自主推进")

COURSE.add("practice-reflection", "三个题目不同，怎样判断自己的学习有了进展？",
    "<div class=\"columns d21-columns\"><div class=\"panel\"><h3>不只看最终结果</h3><p>能否说清计算目标、数据结构、算法依据和计算代价？</p></div><div class=\"panel\"><h3>也看理解与验证</h3><p>能否独立预测、运行程序、检查变化和边界，并解释局限？</p></div></div><div class=\"quote\">课件和 AI 都可以提供帮助，但理解、判断与验证需要自己参与。</div>",
    section="practice", role="content", goal="建立共同评价认识，避免以报告形式替代理解", activity="提出一个自己还想弄清楚的问题，不要求提交")

COURSE.add("final-practice-release", "课后作业：期末综合计算实践大作业",
    "<div class=\"d21-release\"><div class=\"d21-cover-line\"><strong class=\"d21-cover-label\">正式任务入口</strong><div class=\"d21-cover-sequence\"><a href=\"https://github.com/weihuayi/data-structures-and-algorithms/blob/main/course/assignments/campus-computing-practice/README.md\">阅读三个正式题目、报告要求及评价标准（在线）</a></div></div><p><strong>三个题目任选其一，独立完成。</strong>期末提交一份个人报告，完整 C11 源码放在报告附录。</p><p>不要求立即选题、提交初步方案或阶段成果；本讲不另设 A/B 课后作业。</p><p class=\"small\">在个人电脑运行；先预测、再运行、再解释，附 3–5 行过程记录。通过飞书提交，截止日期与入口以教师、助教通知为准。</p><p class=\"small\"><a href=\"../../assignments/campus-computing-practice/README.md\">仓库内正式任务文件</a> · <a href=\"../../assignments/homework-guide.md\">作业共同规范</a></p></div>",
    role="closing", label="期末任务发布", goal="在授课结束时正式发布期末个人实践并明确唯一任务主源", activity="说明任务边界；允许按自己的节奏推进")

SLIDES = COURSE.finalize()
PAGE_IDS = [page["id"] for page in COURSE.pages]
assert len(SLIDES) == 32
