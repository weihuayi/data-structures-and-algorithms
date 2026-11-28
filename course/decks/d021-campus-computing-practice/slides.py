"""D021：正式教学页面主源。通过 tools/deck/build.py D021 生成 HTML。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "deck"))
from components import CourseDeck, Section, task_workspace

DECK_ID = "D021"
TITLE = "从校园生活到计算问题"
MATH = True
DEPENDENCIES = ["course/assignments/campus-computing-practice/README.md"]
COURSE = CourseDeck([
    Section("learning", "知识学习与现实问题", "学过算法，怎样才能用它理解和解决问题？", "回顾学习经验，辨认知识、理解与独立应用的区别。", "建立从知识学习走向现实实践的动机"),
    Section("campus", "观察与理解湘潭大学校园", "我们每天生活的校园，有哪些现象和需求值得研究？", "从学生真实体验出发，讨论教学、空间、交通、服务及资源之间的联系。", "发现问题，区分观察、推断和待验证解释"),
    Section("model", "从现实问题到计算问题", "一个真实问题怎样变成边界明确的计算任务？", "识别对象、信息、关系、假设、输入、输出与目标。", "在具体情境中建立计算抽象意识"),
    Section("knowledge", "重新认识数据结构与算法", "已经学过的知识怎样共同支持一次计算？", "回顾表示、操作、算法、正确性、代价和验证的关系。", "回收课程主线，形成后续复习导航"),
    Section("practice", "期末综合计算实践", "从校园问题中可以提取哪些适合自己尝试的任务？", "认识三个候选题目及其边界，在授课结束时统一发布。", "理解期末个人实践的目的及共同要求"),
])

COURSE.add("cover", "从校园生活到计算问题",
    "<p class=\"lead\">我们怎样发现身边值得研究的问题，并让数据结构与算法发挥作用？</p><div class=\"quote\">观察现实 → 理解问题 → 计算抽象 → 调用已有知识</div><p class=\"small\">D021 · 数据结构与算法 · 综合复习与计算实践导入</p>",
    role="cover", label="课程导入", goal="从理论知识学习转向真实问题认识", activity="观察、思考与追问")

COURSE.outline(title="今天我们将怎样重新认识数据结构与算法？")
COURSE.start_section("learning")
COURSE.add("knowledge-vs-ability", "学过一种算法，就意味着会解决问题吗？",
    "<div class=\"columns\"><div class=\"panel\"><h3>教材中的任务</h3><p>给出一个图，要求完成 BFS。</p><p>问题和输入已经定义好了。</p></div><div class=\"panel\"><h3>现实中的任务</h3><p>某处道路施工后，学生怎样到教室？</p><p>先判断需要什么信息、求什么结果。</p></div></div><div class=\"quote\">会执行算法与会提出并解决计算问题，是不同层次的能力。</div>",
    section="learning", role="content", goal="区分知识记忆、算法执行和独立问题解决", activity="先独立回忆自己遇到的困难，再听同学回答")

COURSE.add("learning-purpose", "学习怎样帮助我们认识和改善生活？",
    "<p class=\"lead\">你所学的知识，能不能帮助你理解一个以前不理解的现象？</p><div class=\"columns\"><div class=\"panel\"><h3>适应环境</h3><p>认识已有规则，学会使用已有工具。</p></div><div class=\"panel\"><h3>改善环境</h3><p>观察、提出问题、分析原因、探索改变的可能性。</p></div></div><p>不必现在就有答案。先从自己真正关心的问题开始。</p>",
    section="learning", role="content", goal="把学习能力与现实认识建立联系", activity="教师追问学生已有体验，不要求表态")

COURSE.start_section("campus")
COURSE.add("daily-activities", "我们每天在校园中经历哪些活动？",
    "<table><thead><tr><th scope=\"col\">活动</th><th scope=\"col\">可以观察什么</th></tr></thead><tbody><tr><td>上课、换教室</td><td>时间、地点、课间移动</td></tr><tr><td>就餐、取快递</td><td>到达、等待、服务</td></tr><tr><td>自习、运动</td><td>空间、开放时间、占用情况</td></tr></tbody></table><p class=\"small\">这些只是观察入口。你还经历过什么活动？</p>",
    section="campus", role="content", goal="从真实活动而不是预设技术分类开始", activity="学生回忆自己的一天，补充活动")

COURSE.add("open-discussion", "你遇到过哪些值得改善的校园问题？",
    "<p class=\"lead\">先独立想一个实际经历，再向全班介绍。</p><ul><li>发生了什么？在什么地点、什么时段？</li><li>谁受到了影响？你观察到了哪些事实？</li><li>哪些判断只是自己的猜测？</li></ul><p class=\"small\">不要求分组或提交材料；不公开个人身份、课表隐私或他人评价。</p>",
    section="campus", role="content", goal="自主提出真实问题并区分事实与猜测", activity="教师留白；先听学生，不预先给三个题目")

COURSE.add("timetable-impact", "一份课表会怎样影响学生的学习与生活？",
    "<div class=\"columns\"><div class=\"panel\"><h3>教学安排</h3><p>课程在什么时候、什么地点发生？</p><p>同一个人或班级的活动怎样衔接？</p></div><div class=\"panel\"><h3>学生体验</h3><p>能否及时到达？是否需要跨教学区移动？</p><p>课间是否还有休息时间？</p></div></div><div class=\"quote\">想一想：两份课表的课程完全相同，安排顺序不同，体验会一样吗？</div>",
    section="campus", role="content", goal="发现活动次序和空间移动之间的联系", activity="请学生结合自己的经历说明，不展示含身份的课表")

COURSE.add("campus-space", "我们怎样认识校园中的空间与道路？",
    "<div class=\"columns\"><div class=\"panel\"><h3>几何信息</h3><p>地点在哪里？道路有多长？</p></div><div class=\"panel\"><h3>拓扑与语义信息</h3><p>哪些地点直接连通？道路是否双向、是否开放？</p></div></div><div class=\"quote\">地图上的两个点很近，就一定能够直接到达吗？</div>",
    section="campus", role="content", goal="区分空间几何、连接关系与通行规则", activity="结合实际熟悉地点讨论；有经授权地图可现场展示")

COURSE.add("traffic", "为什么有些道路在特定时段会拥堵？",
    "<p>先描述现象：时段、地点、人员与车辆。</p><div class=\"columns\"><div class=\"panel\"><h3>可能的原因</h3><p>活动集中结束；道路容量有限；不同出行方式相互影响。</p></div><div class=\"panel\"><h3>还需要的证据</h3><p>不同时间的流量、出行起终点、道路条件与通行时间。</p></div></div><p class=\"small\">以上原因是待检验的解释，不是对湘潭大学实际交通状态的已验证结论。</p>",
    section="campus", role="content", goal="从观察现象走向提出可检验解释", activity="学生提出假设，教师追问如何验证")

COURSE.add("service-wait", "为什么有些校园服务需要长时间等待？",
    "<div class=\"columns\"><div class=\"panel\"><h3>请求一侧</h3><p>什么时候到达？有多少请求？每个请求需要怎样的服务？</p></div><div class=\"panel\"><h3>服务一侧</h3><p>有几个窗口？每次服务需要多久？按什么规则处理？</p></div></div><div class=\"quote\">等待时间与到达、服务能力及处理规则都可能有关。</div>",
    section="campus", role="content", goal="识别服务过程中的对象、事件与资源限制", activity="从食堂、快递等学生实际体验比较")

COURSE.add("resource-use", "校园中还有哪些资源可以更好地利用？",
    "<ul><li>教室、自习座位、实验室与体育场地。</li><li>什么时候有人需要？什么时候有空余？</li><li>不同人的需求冲突时，怎样作出合理安排？</li></ul><p class=\"small\">学生可以提出其他问题；有些问题需要管理、制度或沟通，并不一定适合用计算解决。</p>",
    section="campus", role="content", goal="扩大问题视野并明确计算不是唯一手段", activity="全班开放讨论，可跳转前面场景")

COURSE.add("campus-relations", "这些看似不同的问题之间有什么联系？",
    "<svg viewBox=\"0 0 960 300\" role=\"img\" aria-label=\"活动安排和路网分别形成出行需求和路径条件，共同影响交通运行\" style=\"width:100%;max-height:300px\"><defs><marker id=\"c-arrow\" markerWidth=\"7\" markerHeight=\"7\" refX=\"6\" refY=\"3.5\" orient=\"auto\"><path d=\"M0 0 L7 3.5 L0 7 Z\" fill=\"#536779\"/></marker></defs><rect x=\"35\" y=\"12\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"220\" y=\"52.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">教学与活动安排</text><rect x=\"555\" y=\"12\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"740\" y=\"52.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">校园空间与路网</text><rect x=\"35\" y=\"110\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"220\" y=\"150.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">出行需求</text><rect x=\"555\" y=\"110\" width=\"370\" height=\"65\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"740\" y=\"150.5\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">路径与通行条件</text><rect x=\"295\" y=\"225\" width=\"370\" height=\"60\" rx=\"9\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"480\" y=\"263\" font-size=\"26\" text-anchor=\"middle\" fill=\"#152943\">交通运行</text><path d=\"M220 77 V110\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/><path d=\"M740 77 V110\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/><path d=\"M220 175 V198 H390 V225\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/><path d=\"M740 175 V198 H570 V225\" fill=\"none\" stroke=\"#536779\" stroke-width=\"3\" marker-end=\"url(#c-arrow)\"/></svg><p>交通运行的观察结果，可以反过来支持课表安排、道路管理等方案的改进。</p><p class=\"small\">概念关系示意；不是完整智慧校园模型，也不是实际交通数据。</p>",
    section="campus", role="content", goal="认识校园运行中的部分承重关系", activity="学生解释一条关联，提出可能缺失的因素")

COURSE.add("research-connection", "我们正在尝试怎样认识和解决这些问题？",
    "<div class=\"columns\"><div class=\"panel\"><h3>从实际活动出发</h3><p>排课、校园空间表示、道路通行与交通分析等问题，可以相互连接。</p></div><div class=\"panel\"><h3>从问题到研究</h3><p>获取数据 → 建立模型 → 设计计算方法 → 检查结果 → 支持实际判断。</p></div></div><p class=\"small\">教师可结合算海当前的实际工作介绍已有成果、正在验证的能力和尚待解决的问题；不将研究计划当作已验证的成果。</p>",
    section="campus", role="content", goal="把学生生活与真实科研工程认识连接", activity="教师展示经确认可公开的真实素材（如有），区分事实与设想")

COURSE.start_section("model")
COURSE.add("not-start-code", "发现问题之后，为什么不能立即开始编程？",
    "<div class=\"columns\"><div class=\"panel\"><h3>现实需求</h3><p>例如：希望自习空间得到更合理的利用。</p><p>它涉及不同时间、地点、规则和需求。</p></div><div class=\"panel\"><h3>计算问题</h3><p>例如：给定某时段的座位总数与占用记录，统计可用座位数量。</p><p>先确定输入、输出和条件。</p></div></div><div class=\"quote\">程序是对计算问题的实现，不是现实问题本身。</div>",
    section="model", role="content", goal="区分现实需求与定义好的计算任务", activity="学生指出哪些现实信息尚未进入模型")

COURSE.add("information", "要研究一个问题，需要哪些信息？",
    "<table><thead><tr><th scope=\"col\">计算对象</th><th scope=\"col\">属性或状态</th><th scope=\"col\">关系或操作</th></tr></thead><tbody><tr><td>自习座位</td><td>编号、是否占用</td><td>属于哪个区域、查询</td></tr><tr><td>教学活动</td><td>开始、结束、地点</td><td>同一人活动的先后</td></tr><tr><td>道路</td><td>端点、通行条件</td><td>直接连接、路径搜索</td></tr></tbody></table><p class=\"small\">同一现实对象在不同任务中需要保留的信息不一定相同。</p>",
    section="model", role="content", goal="区分对象、属性、状态和关系", activity="指出不必要或尚缺失的信息")

COURSE.add("abstraction", "怎样从真实对象中提取计算对象？",
    "<div class=\"columns\"><div class=\"panel\"><h3>真实座位</h3><p>位置、材质、光照、附近插座、占用状态等。</p></div><div class=\"panel\"><h3>当前计算对象</h3><p>如果只统计可用座位，可以保留编号、区域与占用状态。</p></div></div><div class=\"quote\">计算抽象：根据任务保留必要信息，明确暂不考虑的因素。</div>",
    section="model", role="content", goal="理解抽象由目标决定而不是任意丢弃信息", activity="追问：如果希望推荐有插座的座位，模型需要改变什么？")

COURSE.add("define-task", "怎样明确一个计算问题的输入和输出？",
    task_workspace("<table><thead><tr><th scope=\"col\">座位编号</th><th scope=\"col\">区域</th><th scope=\"col\">占用状态</th></tr></thead><tbody><tr><td>S1</td><td>甲</td><td>空闲</td></tr><tr><td>S2</td><td>甲</td><td>占用</td></tr><tr><td>S3</td><td>乙</td><td>空闲</td></tr></tbody></table><p class=\"small\">教学构造数据。假设三条记录完整，状态只有空闲或占用。</p>", "<p><strong>独立思考：</strong>若目标是统计甲区可用座位数量，需要哪些字段？应该输出什么？</p>", "<p>输入：座位所属区域与占用状态；编号用于区分记录。</p><p>输出：甲区可用座位数为 1。该结果只对应给定时刻和完整记录。</p>", layout="stacked"),
    section="model", role="exercise", goal="在新任务中明确输入、输出与前置条件", activity="纸笔独立判断后展开核对，不提交", withheld_results=["甲区可用座位数为 1"])

COURSE.add("multiple-tasks", "同一个现实问题可以产生哪些计算任务？",
    "<table><thead><tr><th scope=\"col\">校园出行不便</th><th scope=\"col\">不同计算目标</th></tr></thead><tbody><tr><td>道路是否连通？</td><td>判断可达性</td></tr><tr><td>希望少经过道路</td><td>最少边数路径</td></tr><tr><td>希望尽快到达</td><td>给定通行时间的最小权路径</td></tr><tr><td>想了解拥堵原因</td><td>分析出行需求与交通运行数据</td></tr></tbody></table><div class=\"quote\">同一现实问题，可以因目标和假设不同而形成不同计算问题。</div>",
    section="model", role="content", goal="认识目标改变会改变模型与算法", activity="追问哪些任务需要更多数据")

COURSE.start_section("knowledge")
COURSE.add("representation-recall", "我们怎样组织和表示计算对象？",
    "<table><thead><tr><th scope=\"col\">组织或表示</th><th scope=\"col\">已有课程中的知识</th></tr></thead><tbody><tr><td>对象、属性、顺序与存储</td><td><a href=\"../d001-problem-representation/index.html\">D001</a>–<a href=\"../d004-linked-list/index.html\">D004</a>：抽象、顺序表、链表</td></tr><tr><td>字符串与层次关系</td><td><a href=\"../d007-string-pattern-matching/index.html\">D007</a>–<a href=\"../d010-forest-and-huffman/index.html\">D010</a>：串、树、森林</td></tr><tr><td>一般关系</td><td><a href=\"../d011-graph-modeling/index.html\">D011</a>：图与存储表示</td></tr></tbody></table><p class=\"small\">抽象对象不等于具体表示；应根据必要操作选择实现。</p>",
    section="knowledge", role="content", goal="回收对象、表示与抽象的课程主干", activity="学生解释为什么同一图可用矩阵或邻接表")

COURSE.add("mechanism-recall", "怎样利用已有信息组织计算过程？",
    "<table><thead><tr><th scope=\"col\">要完成的工作</th><th scope=\"col\">已有课程中的知识</th></tr></thead><tbody><tr><td>组织待处理任务</td><td><a href=\"../d005-stack-and-queue/index.html\">D005</a>–<a href=\"../d006-stack-and-recursion/index.html\">D006</a>：栈、队列、递归</td></tr><tr><td>访问、连接、路径与依赖</td><td><a href=\"../d012-graph-traversal/index.html\">D012</a>–<a href=\"../d015-topological-and-critical-path/index.html\">D015</a>：图遍历、最小生成树、最短路径、拓扑排序与关键路径</td></tr><tr><td>查找与建立顺序</td><td><a href=\"../d016-search-order-and-asl/index.html\">D016</a>–<a href=\"../d020-selection-merge-and-synthesis/index.html\">D020</a>：查找、树表、散列、排序</td></tr></tbody></table><p class=\"small\">算法主动利用表示和计算过程中获得的信息，而不只是机械执行步骤。</p>",
    section="knowledge", role="content", goal="回收主要算法机制并认识跨知识联系", activity="学生任选熟悉算法说明利用了什么信息")

COURSE.add("verify-choice", "为什么结果、正确性和计算代价都需要关心？",
    task_workspace("<p>某程序对一个小输入得到正确结果；另一个程序对同一输入也得到正确结果。</p>", "<p><strong>独立判断：</strong>能否仅凭这一次运行认定两个算法对所有合法输入都正确？能否据此判断哪一个更适合大规模输入？</p>", "<p>不能。需要解释算法的成立条件及保持性质，构造其他测试；比较代价还需说明输入规模、操作和成本模型。</p>", layout="stacked"),
    section="knowledge", role="exercise", goal="区分样例通过、正确性论证和复杂度判断", activity="独立判断后核对，回收先预测再运行再检查")

COURSE.start_section("practice")
COURSE.add("practice-a", "题目 A｜校园课表合理性分析",
    "<div class=\"columns\"><div class=\"panel\"><h3>现实背景</h3><p>相邻教学活动可能发生在不同地点。</p></div><div class=\"panel\"><h3>计算任务</h3><p>给定某人或同班学生一天的无重叠课表和地点间预计移动时间，检查相邻课程是否留足移动时间。</p></div></div><p class=\"small\">知识入口：记录、顺序表、排序、扫描。它不是自动排课系统；正式数据与要求见最终发布页。</p>",
    section="practice", role="content", goal="认识课表检查的目标、对象和边界", activity="理解题意，不展示参考程序或正式答案")

COURSE.add("practice-b", "题目 B｜校园道路网络与路径分析",
    "<div class=\"columns\"><div class=\"panel\"><h3>教学示意</h3><svg viewBox=\"0 0 470 200\" role=\"img\" aria-label=\"抽象道路示意，A、B、C、D 由道路连接，不表示真实校园\" style=\"width:100%;max-height:220px\"><g stroke=\"#536779\" stroke-width=\"3\"><path d=\"M60 100 L200 40 L400 100 L200 160 Z M200 40 L200 160\" fill=\"none\"/></g><circle cx=\"60\" cy=\"100\" r=\"22\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"60\" y=\"107\" text-anchor=\"middle\" font-size=\"24\" fill=\"#152943\">A</text><circle cx=\"200\" cy=\"40\" r=\"22\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"200\" y=\"47\" text-anchor=\"middle\" font-size=\"24\" fill=\"#152943\">B</text><circle cx=\"400\" cy=\"100\" r=\"22\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"400\" y=\"107\" text-anchor=\"middle\" font-size=\"24\" fill=\"#152943\">D</text><circle cx=\"200\" cy=\"160\" r=\"22\" fill=\"#eef4f9\" stroke=\"#005a9c\" stroke-width=\"2\"/><text x=\"200\" y=\"167\" text-anchor=\"middle\" font-size=\"24\" fill=\"#152943\">C</text></svg><p class=\"small\">抽象图，不是正式题目路网。</p></div><div class=\"panel\"><h3>计算任务</h3><p>给定无向道路网络，判断两地点是否连通，寻找经过道路数量最少的路径，分析关闭道路后的变化。</p></div></div><p class=\"small\">知识入口：图表示、队列、BFS。最少边数不等于实际最短距离。</p>",
    section="practice", role="content", goal="认识无权图搜索的任务与边界", activity="学生说明顶点、边可能表示什么")

COURSE.add("practice-c", "题目 C｜校园服务请求与等待时间分析",
    "<div class=\"columns\"><div class=\"panel\"><h3>现实背景</h3><p>请求陆续到达一个服务窗口，可能需要等待。</p></div><div class=\"panel\"><h3>计算任务</h3><p>给定请求到达时间和服务时长，按约定 FIFO 规则模拟服务并计算等待时间。</p></div></div><p class=\"small\">知识入口：记录、排序、队列语义、状态更新。FIFO 是处理规则，不要求必须用显式队列。</p>",
    section="practice", role="content", goal="认识请求、事件和状态更新的计算任务", activity="讨论模型不考虑哪些现实因素")

COURSE.add("practice-process", "怎样完整地经历一次计算实践？",
    "<p class=\"lead\">问题理解 → 对象与表示 → 算法 → C11 程序</p><p class=\"lead\">预测与测试 → 结果解释 → 学习反思</p><p>允许借助 AI、教材和同学交流；先自己尝试，实际运行、核对并解释。</p><p class=\"small\">D022 将使用不同的教学输入示范完整过程，不提前代做期末题目。</p>",
    section="practice", role="content", goal="建立完整实践路径与独立判断责任", activity="教师说明后续学习如何支持自主推进")

COURSE.add("practice-reflection", "三个题目不同，怎样判断自己的学习有了进展？",
    "<div class=\"columns\"><div class=\"panel\"><h3>不只看最终结果</h3><p>能否说清计算目标、数据结构、算法依据和计算代价？</p></div><div class=\"panel\"><h3>也看理解与验证</h3><p>能否独立预测、运行程序、检查变化和边界，并解释局限？</p></div></div><div class=\"quote\">课件和 AI 都可以提供帮助，但理解、判断与验证需要自己参与。</div>",
    section="practice", role="content", goal="建立共同评价认识，避免以报告形式替代理解", activity="提出一个自己还想弄清楚的问题，不要求提交")

COURSE.add("final-practice-release", "课后作业：期末综合计算实践大作业",
    "<p class=\"lead\"><a href=\"../../assignments/campus-computing-practice/README.md\">阅读三个正式题目、统一报告要求和评价标准</a></p><p>三个题目任选其一，独立完成。期末只提交一份个人报告，完整 C11 源码放在报告附录。</p><p>不要求立即选题、提交初步方案或阶段成果；本讲不另设 A/B 课后作业。</p><p class=\"small\">在个人电脑运行；先预测、再运行、再解释，附 3–5 行过程记录。通过飞书提交，截止日期和入口以教师、助教通知为准。</p><p class=\"small\"><a href=\"https://github.com/weihuayi/data-structures-and-algorithms/blob/main/course/assignments/campus-computing-practice/README.md\">在线正式任务入口</a> · <a href=\"../../assignments/homework-guide.md\">作业共同规范</a></p>",
    role="closing", label="期末任务发布", goal="在授课结束时正式发布期末个人实践并明确唯一任务主源", activity="说明任务边界；允许按自己的节奏推进")

SLIDES = COURSE.finalize()
PAGE_IDS = [page["id"] for page in COURSE.pages]
assert len(SLIDES) == 32
