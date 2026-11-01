# 课件构建与验证工具

本目录承载课程 HTML Deck 的共享构建与交互能力。具体教学内容由各 Deck 的 `slides.py` 维护。

当前共同约定见 [课程课件共性约定](../../docs/design/deck-contract.md)，实施与证据见 [实施计划](../../docs/design/deck-consistency-plan.md)。新任务从根及作用域 `AGENTS.md` → 共同约定 → 所需组件与本讲设计卡进入，历史课件是参考，不是自动生效的规范。规则入口与链接由 `instructions.py` 检查，并纳入依赖指纹与影响分析。

## 课程公共模式

`components.py` 提供 `CourseDeck`、`Section`、`task_workspace`；`components.css` 只在采用 `COURSE` 的课件加载，不改变旧课件的页面形式。调用公共模式即可获得导航与任务展开规则，部分数、案例、图示、证明及算法状态仍由本讲确定。

最小多部分课件：

```python
from components import CourseDeck, Section, task_workspace

DECK_ID = 'D015'  # 示例；实际使用对应资产身份
TITLE = '本讲主题'
COURSE = CourseDeck([
    Section('task', '明确任务', '需要解决什么？', '明确对象、输入和输出。'),
    Section('method', '组织计算', '怎样利用已有信息？', '解释操作、条件和检查。'),
])
COURSE.outline()
COURSE.start_section('task')
COURSE.add('input', '需要保留哪些信息？', '<p>具体输入及问题</p>',
           section='task', goal='识别完成任务所需的信息')
COURSE.start_section('method')
COURSE.add('predict', '下一步会发生什么？',
           task_workspace('<p>必要输入</p>', '<p>先预测</p>', '<p>答案及理由</p>'),
           section='method', role='exercise', goal='独立解释一次操作', activity='作答与反馈')
COURSE.add('after-class', '课后怎样核对？', '<p>教材导航及实践任务</p>',
           role='closing', label='课后衔接', goal='明确课后任务')
SLIDES = COURSE.finalize()
```

实际 `slides.py` 需按既有课件将 `tools/deck` 加入 Python 搜索路径，或通过仓库加载环境导入。可直接运行的 [多部分源码](examples/patterns/slides.py) 和 [单任务源码](examples/single-task/slides.py) 包含完整导入；D014 是课程接入实例。

- 页面 ID 使用稳定英文标识，不使用页码；`role` 为 `cover/outline/section/content/exercise/closing`。角色只声明职责，不能证明教学内容充分。
- 部分定义维护标题、问题、展开范围；大纲默认生成 `<ol>` 有序导航，按行展示序号、主题、问题及实际页码，页码由页面归属生成。`start_section` 与大纲共用定义，不手写复制导航 HTML。`navigation.py` 独立核对最终 HTML 的顺序、字段和页码；浏览器再检查 DOM 与可见性。
- 公共页头由 `headers.py` 与构建器组合：`section` 起始页只输出完整主标题，省略小号分节节点；普通页保留信息不同的上下文与本页标题。源码三元组中的分节标签保持完整，不用清空标签或 CSS 隐藏来去重。旧课件无需迁入 `COURSE` 也可受益于完全重复去重。
- 页头比较保留词间边界、数学符号及有意义的标点，只合并 ASCII 全半角、空白格式和已知章节前缀的分隔差异。静态检查读取实际 HTML，浏览器再检查 DOM；自动规则不识别所有同义冗余，仍需人工看组合后的页面。
- `CourseDeck()` 无部分时支持单任务课件，不强制大纲。多个部分默认有大纲；需紧凑组织时使用 `navigation='compact', navigation_reason='具体教学理由'`，记录一次即可。
- `task_workspace` 的 HTML 参数是可信仓库内容；不是外部 HTML 清洗器。输入置于折叠区之外，答案展开替换提问，打印恢复提问并隐藏答案。默认可见标题、图注及摘要是否泄漏答案需专业审阅。构造或转换任务默认提供完成产物并解释理由；题目特定结果由独立语义断言及内容审阅核对，不由任务区组件推断。
- `COURSE.page_plan()` 从相同注册信息生成逐页职责行；不要另行维护页码与标题副本。设计卡可用 `<!-- page-plan:start -->` 和 `<!-- page-plan:end -->` 包住派生表格，构建时同步该区域，检查器只读核对；区域外的教学设计、活动预算与证据仍人工维护。没有部分归属的课后/衔接页用 `closing`，位于部分内容之后。
- `SLIDES` 仍为三元组。`build.py` 给已接入页面附加稳定 ID、角色与部分属性，保留既有翻页接口。`legacy.json` 明确列出 D001–D013 的初始迁移范围，接入时应同时移除对应 ID；新课件缺少 `COURSE` 会失败。目录身份与 `DECK_ID` 必须对应，复制旧源或删除元数据不能静默退回旧模式。

```bash
python3 tools/deck/build.py patterns single-task
python3 tools/deck/check.py patterns single-task --static-only
python3 tools/deck/check.py patterns single-task --screenshots pages
```

样例服务作者，不登记为正式课程课件。单任务、不同部分数量、紧凑组织都有正例；错配导航、重复 ID、无归属页面、输入隐藏和失效按钮有失败夹具。共享组件的变更应同时审阅这些样例。

D015 使用 `dependency_trace.py` 的依赖状态与图视图，复用公共导航、任务区及播放器。拓扑输出表示排位，`read/release/boundary` 区分未更新和更新完成；时间传播区分待汇总值与确定值。适用范围是教学用简单依赖图和一源一汇、固定非负整数时长的 AOE DAG，不是通用资源排程 API。其状态、C 演示和独立路径枚举的交叉核对见 `tests/test_dependency_trace.py` 与 [D015 设计卡](../../course/decks/d015-topological-and-critical-path/README.md)。布局样式按 `.dependency-lesson` 限定，放在共享 `components.css`。

## 统一验证入口与影响范围

```bash
# 全课程静态与语义测试，以及已接入课件/样例的完整操作、旧课件默认页
python3 tools/deck/verify.py --all --output /tmp/course-review

# 依据与 main 的差异缩小浏览器回归；静态和语义检查仍覆盖全课程
python3 tools/deck/verify.py --base origin/main --output /tmp/course-change-review

# 不运行浏览器，状态明确为 static-only-pass
python3 tools/deck/verify.py --all --static-only

# 保留完整操作的展开/步骤截图，便于定向视觉自审
python3 tools/deck/verify.py --base origin/main --screenshots all --output /tmp/course-visual-review

# 只读查看影响对象与原因（包含未提交及未跟踪文件）
python3 tools/deck/impact.py --base origin/main
```

运行完整检查需 Python 3.12+、C11 编译器、Node 20+、Playwright、Chromium/Chrome 和中文字库。浏览器驱动由本目录 `package.json` 与 lock 文件固定，可用 `npm ci --prefix tools/deck --ignore-scripts` 安装；已有运行环境可继续用 `DECK_NODE`、`DECK_PLAYWRIGHT_MODULE`、`DECK_BROWSER_EXECUTABLE`，避免重复下载。安装浏览器可在本目录运行 `npx playwright install chromium`；Linux 安装 Noto CJK 等字体。检查命令本身不安装依赖。

`verify.py` 汇总静态、语义、检查器回归、完整操作和旧课件默认页日志及报告，输出目录必须新建。`scoped-pass` 只表示声明范围通过，不是所有旧交互都已验证。`--static-only`、`check.py --default-pages` 分别得到 `static-only-pass`、`default-pages-pass`，不得转述为完整通过。旧课件溢出会与明确基线在相同环境对照；仅页面 DOM 与溢出完全相同的布局失败可分类为既有发现，汇总为 `scoped-pass-with-legacy-findings`，原始报告仍保留失败。新/加重、内容变更、字体或资源失败继续阻断。失败返回 1，未完成返回 2；人工补查另留页 ID、尺寸、操作和发现，不改机器原始状态。

影响分析使用本地 Python 静态导入闭包、HTML/CSS 本地资源、课件代码及源码 `DEPENDENCIES` 列出的仓库相对路径。动态加载/数据依赖需显式补充；无法判断的共享代码变更保守扩大范围。全局 CSS/脚本与构建器影响旧课件，公共组件只影响采用者。报告保存依赖文件哈希、约定哈希与检查工具哈希；哈希能绑定版本，不能证明推导正确。

作用域 AGENTS、当前契约、修订指南、工具说明和本讲设计卡也进入依赖指纹。改变规范入口时，CI 和影响分析选择相关回归；当前规范文件变化保守覆盖全课程的相应检查，不强迫旧课件迁移。

### AI 交付审阅记录

机器验证报告的 `status` 保留原有范围含义，`deliveryStatus` 为 `pending-review`。它另存当前内容指纹、运行期间是否变化，以及机器日志、报告和截图的哈希。验证中源码变化会使本次运行不完整。

机器检查后，在最终页面进行实际的六方面内容与视觉自审，修订问题并复查；然后创建并填写记录：

```bash
python3 tools/deck/review.py init --verification /tmp/course-change-review/verification.json --review /tmp/course-ai-review.json
# 完成实际自审后填写 JSON：审阅者、六方面判断、页面与操作、证据、发现处置。
python3 tools/deck/review.py check --verification /tmp/course-change-review/verification.json --review /tmp/course-ai-review.json --output /tmp/course-review-closure.json
```

`dimensions` 的键为 `goals/continuity/organization/representation/interaction/verification`，对应契约六方面；每项记录 `reviewed` 或附理由的 `not-applicable`、判断说明和证据。`targets` 覆盖本次完整操作课件及样例，记录实际审阅的页面、状态和证据。证据使用验证输出中的相对路径，如 `full/report.json` 或具体截图。发现分 `blocking/advisory/legacy`；阻断项须为 `resolved`，所有发现记录具体位置、处置及复查证据。待填模板不能通过检查。

记录与结果保存在仓库外的验证工作目录，PR 和受控设计文档留下简洁的结论与运行定位。内容指纹覆盖受控及非忽略的新课程、工具、设计与 CI 文件，生成记录不参与自身指纹。改变源码、设计、规则或共享依赖后须重跑必要验证并更新记录；提交元数据变化本身不使相同内容失效。

`ready-for-teacher-review` 只表示记录完整、版本相符、机器范围完成且没有未决阻断声明。工具不证明判断正确，也不宣称教师已经审阅或课堂效果成立。缺失、过期或篡改的机器证据、未覆盖六方面、遗漏完整操作目标、未决阻断均使交付记录失败；静态检查不能独自闭合交付。

`.github/workflows/deck-check.yml` 在 PR、main 更新或手动触发时运行相同入口并保留报告。它提供检查结果；是否设为 main 必需检查由维护者在稳定运行后决定。本轮不修改仓库保护设置，也不新增审批人数。

字体检查用常用汉字的不同字形识别整组缺字方框，报告字体栈；不能保证所有字符、字体缩放或后排可读性。公共样例保留截图并进行 AI 视觉自审，教师审阅另留证据；尚未建立跨环境的逐像素截图基准，结构、操作和布局检查分别报告。

```bash
python3 tools/deck/build.py all
python3 tools/deck/build.py D001
```

`slides.py` 是课件主维护源，`index.html` 是受控派生产物。公开 Deck 不包含教师私有备注。教师运行资料应通过受限或本地工作空间维护，不写入公开 `slides.py` 或 `index.html`。

## 交互组件

`deck.js` 按 `data-*` 根元素接管页面内的交互演示，样式在 `deck.css`：

- `data-pair="brute|sorted"`：商品配对的分步扫描演示（D002）；
- `data-map` / `data-maze`：网格位置与迷宫寻路演示；
- `data-mem="insert|delete|access|expand|cache"`：连续内存条带演示——顺序表插入/删除搬运、地址直达与逐个扫描对照、扩容整体搬迁、缓存预取对照（D003）。
- `data-link="access|insert|delete"`：链表链式推演——沿 next 走访计数、插入改两个链接（含先改前驱的断链陷阱现场）、删除（含只改链接不 free 的内存泄漏对照）（D004）。
- `data-stack="brackets"`：括号匹配栈轨迹——左括号压栈、右括号弹栈核对，含匹配成功与遍历完栈非空两种对照情形（D005）。
- `data-queue="plain|circ"`：队列推演——顺序队列假满现场；N=5 循环队列 front/rear 轨迹（判满 → 出队 → rear 绕回 → 再次判满）（D005）。
- `data-recur="factorial"`：递归工作栈逐帧推演——factorial(4) 压帧五层、回退 1→1→2→6→24（D006）。
- `data-hanoi="disks"`：汉诺塔盘子移动推演——2 盘/3 盘可选，3 盘标注"整体法"三段结构（D006）。
- `data-match="bf|kmp"`：模式匹配轨迹——主串与模式网格对齐、逐次比较、失配标红、比较计数；BF 五趟浪费复现，KMP 可切 BF 对照（i 不回头 vs 回溯）（D007）。

嵌入方式：在 `slides.py` 的 `body_html` 中放置带 `data-*` 属性的根元素，内含 `.toolbar`（情形选择与上一步/下一步/重置）、演示区与 `.status` 状态栏。纯逻辑函数（trace）与 DOM 分离，经 `module.exports` 导出，可用 Node 直接断言。新增交互组件按同一模式加入共享层，不在单个 Deck 内私造。

源文件与生成页面可用下述只读检查核对；检查不会先重建并掩盖过期产物。

## 静态树图

`tree_diagram.py` 提供 `tree`（SVG 结点—边图）、`beside`（树与表示并排）、`gallery`（形态对照）。结点以稳定 ID 映射到坐标、标签和说明，边为父子 ID 对；支持结点与边高亮、层线及子树区域。结构边统一无箭头，SVG 含可访问标题，样式使用共享 `.tree-*` 类。D008 提供资料树与表达式树的用例。

## LaTeX 数学公式

课件在 `slides.py` 中设置 `MATH = True`，构建器才会加载本地 KaTeX 0.16.22 与 `math.js`；未启用的 Deck 不增加资源引用。行内公式用 `\(...\)`，独立公式用 `\[...\]`，多行推导可在独立公式中使用 `aligned` 环境。Python 字符串建议使用原始字符串，例如 `r'<p>\(n_0=n_2+1\)</p>'`，以免反斜杠被转义；HTML 内的 `&` 写作 `&amp;`。

正文、表格、折叠注记和图注均参与渲染；`pre`、`code`、SVG 标签及页面菜单保持字面内容。标题宜用自然语言，避免菜单显示公式源码。数学表达式不要包在代码标签中。KaTeX 资源和字体位于 `vendor/katex/`，来源与 MIT 许可随资源保留，离线可用；它支持常用 LaTeX 数学语法，并非完整 TeX 文档编译环境。

## 树的分步推演

`tree_trace.py` 生成确定性的遍历和恢复状态。递归状态区分进入、visit、返回、整棵子树完成，保存调用帧的执行位置；显式栈和队列分别记录容器、取出、访问及加入孩子的微步骤。`traversal_player` 将状态与树图、输出区组合，`recovery_states` 逐次校验分割并输出已确定的链接。适用输入为小规模、有限、无共享结点的合法二叉树；不作为任意指针图校验器。

`data-tree-player` 在 `deck.js` 中接管上一步、下一步和重置；每个播放器独立保存步号，不自动播放，隐藏状态不参与投影布局。`tree-swap` 在展开代码或镜像时让该内容替代预览图，避免上下堆叠；`tree-answer` 为折叠答案提供紧凑图示。D009 的独立恢复题使用同名 details，一次只展开一种提示或答案。

运行 `python3 -m unittest discover -s tools/deck/tests -v` 核对输出、容器操作、完成状态和恢复分割。浏览器还需验证逐步切换、重置、折叠、公式渲染及目标投影尺寸。打印保留当前可见状态，不展开全部隐藏步骤。

## 课件验证

修订方法见 [Deck 课件修订方法](../../docs/design/deck-revision-guide.md)。`check.py` 先在内存中生成期望 HTML，与现有 `index.html` 比较，不改写课件。注意：生成过程会执行本仓库的 `slides.py`，仅用于可信的仓库源文件。

```bash
# 仅检查源与生成物一致性；不代表浏览器验证通过
python3 tools/deck/check.py D008 D009 --static-only

# 完整检查；报告默认放入新建的临时目录
python3 tools/deck/check.py D008 D009

# 保留每页初始截图及失败截图；输出目录必须尚不存在
python3 tools/deck/check.py D008 D009 --output /tmp/deck-review-run --screenshots pages
```

依赖 Python 3、Node.js、Playwright 和已有的 Chromium/Chrome。工具不下载依赖或浏览器。Node 不在搜索路径时用 `--node` 指定；Playwright 不在 Node 模块搜索路径时用 `--playwright-module` 指定模块目录；使用现有浏览器时用 `--browser-executable` 指定可执行文件。对应环境变量为 `DECK_NODE`、`DECK_PLAYWRIGHT_MODULE`、`DECK_BROWSER_EXECUTABLE`。依赖缺失或浏览器不能启动会报告未完成，不会回退成通过。浏览器检查阻断 HTTP/HTTPS 请求，以检查本地资源的离线可用性。

| 检查项 | 当前自动覆盖 | 边界 |
| --- | --- | --- |
| 构建一致性 | 指定 Deck 的完整 HTML 字节比较、页数 | 不证明内容正确；不检查未选中的 Deck |
| 页头职责 | 直接页头 h2 唯一且非空、起始页无 kicker 节点、上下文与主标题不完全重复；默认页模式同样检查 | 不判断所有近义冗余；不检查教学展品内的标题 |
| 公式 | KaTeX 错误、未渲染的数学分隔符，包括折叠内容 | 排除代码、SVG 和菜单；不验证数学推导 |
| 投影 | 1280×720、1440×900 的主区域横纵溢出 | 不能替代人工判断可读性或检测所有局部遮挡 |
| 分步演示 | `data-tree-player` 全部步骤、末态、返回、重置与边界按钮 | 每播放器最多 500 状态；其他组件或隐藏播放器标记未覆盖 |
| 折叠 | 默认收起、逐一开关、展开布局、同名组切换互斥、至多六个无名独立折叠区的全部开关组合 | 嵌套或隐藏折叠、超过六个独立折叠区或混合命名组的组合展开标记未覆盖；教师注记展开允许纵向滚动 |
| 阅读与打印 | 连续阅读显示全部页；打印隐藏非当前步骤和教师注记正文 | 不是完整打印分页或移动端验证 |
| 资源 | 本地资源加载失败、JavaScript 运行错误 | 不验证所有超链接目标 |

报告 `report.json` 包含时间、源与 HTML 哈希、运行版本、覆盖范围、逐页检查与状态。浏览器失败项带页码、标题、尺寸、操作状态；`browser.log` 保留运行输出。`--screenshots failures|pages|all|none` 控制截图：默认保留布局失败或执行异常截图，`pages` 增加各页默认状态，`all` 记录每次布局检查；并非每项断言都有截图。截图与报告位于输出目录，不提交为受控课件源文件。

退出码：`0` 为所选模式通过（仅静态时状态明确为 `static-only-pass`）；`1` 为检查发现失败；`2` 为依赖不可用或存在未覆盖项等不完整情况。参数错误也返回 `2`，在创建报告前失败时只显示参数说明。未覆盖项应人工补查，说明页码、操作和结果；不能修改报告将未覆盖改成自动通过。

验证工具自身的回归检查：

```bash
python3 -m unittest discover -s tools/deck/tests -v
node --test tools/deck/tests/check_browser.test.cjs
```

第二条也需要上述 Playwright 与浏览器环境变量。它使用临时夹具验证正常页面、溢出、未渲染公式、失效按钮、未知交互与资源缺失，不修改真实课件。状态算法的语义由 Python 测试单独覆盖。新增组件时应补充状态逻辑测试与浏览器适配器；适配前保持未覆盖提示。


## 哈夫曼状态与边标签

`huffman_trace.py` 提供正整数权值、至少两个符号的课堂合并快照，以及在其生成的合法满分支二叉码树上按位译码的快照。选择按权值、再按编号；译码将移动、叶子输出、回根分开记录，末尾内部结点报告不完整。它复用 `tree_trace.player` 的手动控制，不自动播放。D010 的四符号案例使用该模块；它不是任意外部树的结构校验器，也不替代 C 示例的容量和溢出检查。

`tree_diagram.tree` 可通过 `edge_labels={(parent, child): label}` 给边标注 L/R 或 0/1；省略时保持原图。共享 `tree-spacious` 类为较深的快照树提供更多显示高度。相关语义测试纳入同一 Python 测试入口。

层线可通过 `level_start` 指定起始编号；默认值 1 保持既有调用，D008 显式使用 0。层编号不自动决定程序高度的计数口径，课件需分别说明。


`huffman_trace.selection_scan_states` 展示首轮合并之前两遍完整扫描已建记录的微步骤，累计查看次数（包括排除项）、分别保存当前记录和当前最小根，末态追加合成记录并更新双亲。它使用与 `merge_states` 相同的正整数且至少两符号的课堂输入范围，复用现有播放器；不模拟 C 容量、溢出检查或整个程序运行时间。共享 `.record-scan` 样式区分当前记录、最小权值与已合并记录。D010 第 20 页用这一过程引出各轮扫描成本。

## 静态一般图

`graph_diagram.graph` 接收顶点坐标、端点对及可选的方向、权值标签和讨论边标记，不假定树的单亲或无环结构。SVG 箭头止于顶点边界；红色粗实线与线宽共同标记当前关注的已有边；只有命中实际边时才显示图例。`states` 可把顶点标为 `unvisited`、`visited` 或 `current`，对应共享的灰/蓝/橙样式；`legend` 可改写红线图例，传入空串可抑制图例。状态语义必须同时由文字说明或表格承载，不能只靠颜色。无向边标记不区分端点顺序，有向弧标记严格区分方向。`node_details` 可在顶点下显示编号或度数，保留孤立顶点和零值标签。`beside` 将图与表示并置。共享样式为 `.graph-*`；案例数据留在 Deck。适用于无自环、端点坐标不同的小图；不提供自动布局、平行弧避让或任意交叉标签检测，须人工看图。语义测试纳入 Python unittest 入口。

`view_box=(x,y,width,height)` 可裁去与任务无关的空白；默认仍为 `(0,0,520,290)`。`regions` 是显式背景多边形序列，每项给出 `points`、`label`、`label_position`，在边与顶点之前绘制。D013 用它表示已选顶点集合 U；图形工具不自动推导或证明集合成员关系，须核对区域、顶点和跨界边。字号需乘以 SVG 实际缩放比例再判断，不能只读取 CSS 标称值。

## 图搜索状态播放器

`graph_trace.py` 提供 D012 无向主例（A–E，边 AB、AC、BC、CD）的确定性搜索状态：`dfs_states(order)` 与 `bfs_states(order)` 各 15 个快照，保存 `visited`、当前处理顶点 `processing`、刚检查邻居 `examined`、`(vertex,next)` 栈或队列、`parent`、`distance`、`tree_edges` 与输出。BFS 中 `processing` 是正在扫描邻接表的顶点，`examined` 是刚检查的邻居；新访问的邻居不再被误设为当前处理顶点。`dfs_player('recursive'|'stack')`、`bfs_player()` 复用 `tree_trace.player` 的 `data-tree-player` 上一步/下一步/重置控件；每个面板由图、容器、动作与输出组成；DFS 面板显示 parent，BFS 面板显示 parent 与 distance。无自动播放。

状态逻辑在 Python，DOM 只负责显示；`tests/test_graph_trace.py` 覆盖主例序列、parent/tree_edges/distance、BFS `processing/examined`、DFS 栈顶/返回、降序、游标推进、无重复访问、播放器控件与非法参数；`test_graph_forest.py` 覆盖全图搜索森林，`test_c_crosscheck.py` 对照 C 输出。浏览器可执行 `python3 tools/deck/tests/browser_player_check.py`（若本机有 Chrome）。边界：只覆盖该无向无权小图；不提供任意图、带权图、SCC 或扩展存储动画；不把“全部邻居一次入栈”的错误写法纳入播放器。无 JavaScript 时第一个状态仍静态可见。

## MST 状态播放器（D013）

`mst_trace.py` 提供 D013 主例的 `prim_states()`（9 状态：U（对应 selected_vertices）、selected_edges、key、parent、has_key、current_edge、components、总权）和 `kruskal_states()`（16 状态：排序边、当前边、接受/拒绝、selected/rejected、components、真实 DSU parent、总权）。`prim_player()`、`kruskal_player()` 复用 `tree_trace.player` 控件；图用红粗已接受、橙虚线当前检查、灰细虚线已拒绝，并注明虚线只表示处理状态。Prim 侧栏以 LaTeX 显示 U，另列候选入口与 F；Kruskal 侧栏只显示 F、当前分组、拒绝边与总权，不提前显示 DSU 父指针。

Prim 快照的 `key_changes` 保存外部点入口的旧值/新值，表格保留无入口行，候选检查步骤不产生更新。`input_row` 仅在纳入或重启顶点时保存对应的逻辑矩阵行，选择候选阶段为空；None 表示无边，零权保留。`input_row_html` 与 `edge_preparation_views` 从主例输入生成矩阵行、去重视图和同一边数组，后者用于 D013 第 19 页的两状态关系演示。Kruskal 的 `result_complete` 标识已连为一个分量：本讲和 C 使用全扫描变式，MST 完成后只核对剩余边。排序条突出当前扫描位置，完成状态与扫描末态分开解释；非连通末态标为 MSF。第 8–9 页的 MST 性质与交换也复用同一播放器，分别为 2/3 个状态，采用共享 `.relation-player` 大图布局。

共享 `.answer-workspace` 将输入图和提问/答案并置。原生 details 展开时只替换 `.answer-prompt`，图和权值保持可见，收起后恢复提问；D013 第 13、16、28、32、35、38 页用于预测与独立诊断，跨课程探索也复用答案替换行为。`.independent-network` 按任务语义设置独立练习图示尺寸，不依赖页号。目标投影尺寸须同时检查两种状态。打印仍显示提问，完整分页与静态步骤取舍需按使用场景人工核对。

`kruskal_states()` 内部的 `dsu_parent` 是真实父指针的只读复制：`parents()` 不再调用带路径压缩的 `find()`，`components()` 使用无副作用的 `root()`；真实 Kruskal 的 `find()` 仍会压缩，并作为算法操作记录在后续快照中。`tests/test_mst_trace.py` 覆盖候选连接已选与未选顶点、key/parent、接受/拒绝前后分组、递归父指针与分组一致性、路径压缩、等权/零权/负权、非连通 MSF 与练习；`tests/test_d013_slides.py` 校验术语首次定义页、Prim/Kruskal/DSU 的知识依赖与练习答案折叠。`browser_mst_check.py` 在 Chrome 下检查 9/16 状态、next/prev/reset/边界、封面单行与 41 页无纵向溢出。播放器仅覆盖 D013 数据，不扩展为任意图算法平台；无 JS 时首个状态静态可见。


## 最短路径状态与页面（D014）

`shortest_path_trace.py` 提供小型简单图、非负整数权的 Dijkstra 状态，以及 Floyd 按中间顶点阶段的矩阵快照。None 表示尚无路径标签，0 保留为有效边权；有向输入只沿箭头读取。Dijkstra 按输入编号打破距离并列，分别保存选择、确认、读取、比较、修改、一轮完成与停止。所有已确认出边均已处理的前提在下一轮选择前使用，中间快照另有阶段标识。

D014 复用现有 `graph_diagram.graph` 与 `tree_trace.player`，没有增加独立 DOM 播放器或全局 JavaScript 分支。共享 `.shortest-lesson` 样式按内容身份作用，前驱用蓝实线、当前输入边用红粗实线，并辅以文字与表格。学生答案展开时替换提问，图与条件仍在场；打印保留问题，隐藏答案及非当前播放器状态。

`tests/test_shortest_path_trace.py` 使用简单路径穷举作为独立小图参照，核对确认前提、实际路径、零权并列、有向反向不可达、负权拒绝与 Floyd 阶段含义；并编译 C11 课堂程序，对照路径、最终状态与各对距离。通用浏览器检查覆盖 D014 的 38 个播放器状态、返回、重置、答案折叠、公式和两种投影尺寸。算法测试及浏览器检查各有边界，不代表真实学习效果。

## 数组查找状态与页面（D016）

search_trace.py 提供顺序/折半状态、判定树深度、失败间隙、精确概率加权和静态分块过程；复用 tree_trace.player、tree_diagram.tree 及公共任务区，不增加独立 JavaScript 分支。状态区分 ready、compare、update、found、miss，输入保持不变；闭区间、0 起下标、任一匹配或 −1。分块另记索引比较和记录比较，selected 表示选定块，不等同尚未检查记录集合。

array_view 显示完整输入、下标、候选/排除/当前/命中；decision_view 从同一输入推导分析树，gap_view 显示失败类别。成功 ASL 的记录分布要求互异关键字；mean_cost 使用 Fraction 并检查非负概率及归一。图文、边界和代码的一致性仍须内容审阅。

Python 轨迹构建时检查数据，C 查询函数依赖已建立前提；CLI 的一次输入检查不计查询成本。C 演示限制 n≤256、保留轨迹，不作为通用查找库。独立线性参照、随机/边界输入、字面成本参照、分块非法成员及 C 对照见 tests/test_search_trace.py。样式限于 .search-lesson，公共变更覆盖采用者；教师审阅、真实课堂效果另行取证。
