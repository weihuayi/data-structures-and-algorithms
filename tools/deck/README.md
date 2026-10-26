# Deck Build Tool

本目录承载课程 HTML Deck 的共享构建与交互能力。具体教学内容由各 Deck 的 `slides.py` 维护。

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

## 图搜索状态播放器

`graph_trace.py` 提供 D012 无向主例（A–E，边 AB、AC、BC、CD）的确定性搜索状态：`dfs_states(order)` 与 `bfs_states(order)` 各 15 个快照，保存 `visited`、当前处理顶点 `processing`、刚检查邻居 `examined`、`(vertex,next)` 栈或队列、`parent`、`distance`、`tree_edges` 与输出。BFS 中 `processing` 是正在扫描邻接表的顶点，`examined` 是刚检查的邻居；新访问的邻居不再被误设为当前处理顶点。`dfs_player('recursive'|'stack')`、`bfs_player()` 复用 `tree_trace.player` 的 `data-tree-player` 上一步/下一步/重置控件；每个面板由图、容器、动作与输出组成；DFS 面板显示 parent，BFS 面板显示 parent 与 distance。无自动播放。

状态逻辑在 Python，DOM 只负责显示；`tests/test_graph_trace.py` 覆盖主例序列、parent/tree_edges/distance、BFS `processing/examined`、DFS 栈顶/返回、降序、游标推进、无重复访问、播放器控件与非法参数；`test_graph_forest.py` 覆盖全图搜索森林，`test_c_crosscheck.py` 对照 C 输出。浏览器可执行 `python3 tools/deck/tests/browser_player_check.py`（若本机有 Chrome）。边界：只覆盖该无向无权小图；不提供任意图、带权图、SCC 或扩展存储动画；不把“全部邻居一次入栈”的错误写法纳入播放器。无 JavaScript 时第一个状态仍静态可见。
