# D012 第四轮定向返修与验收报告

日期：2026-10-26。对象：[D012 设计卡](../../course/decks/d012-graph-traversal/README.md)、[slides.py](../../course/decks/d012-graph-traversal/slides.py)、[index.html](../../course/decks/d012-graph-traversal/index.html)、[graph_trace.py](../../tools/deck/graph_trace.py)、[graph_diagram.py](../../tools/deck/graph_diagram.py)、[浏览器检查脚本](../../tools/deck/tests/browser_player_check.py)。
性质：定向返修与工程验收；不重做 34 页结构，不改正式作业。

## A. 执行基线

- 仓库：`repos/weihuayi/data-structures-and-algorithms`；分支 `main`。
- 本地修订前 HEAD：`a381a7c17a925c31475434fc293699aa5ded604c`，与任务给定第三轮 HEAD 一致。
- 修订前工作区干净，没有覆盖其他未提交工作。
- `git ls-remote origin HEAD` 因本机 SSH 配置权限错误（`/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf`）失败；未执行 fetch/pull/push，不声称远程状态已改变。本地 HEAD 与任务给定 `a381a7c…` 一致。
- 依据：当前 `slides.py`、`graph_trace.py`、`graph_diagram.py`、`deck.js`、`deck.css`、现有测试、D012 README、第三轮报告、教材第 6 章 6.4–6.5。

## B. 修订完成表

| 编号 | 修订事项 | 实际修改 | 验收证据 | 状态 |
|---|---|---|---|---|
| **P0-1** | 第 25 页搜索森林纠错 | 改为真实全图遍历：A,B 顺序为 `{A}`、`{B}`（2 棵）；B,A 顺序为 `{B,A}`（1 棵）。明确 visited 只初始化一次、不同根不重置；森林树不共享顶点；一棵树可含多个 SCC；SCC 始终 `{A}`、`{B}` | 第 25 页截图 1280/1440；`test_graph_forest.py` 5 项通过 | 完成 |
| **P1-1** | BFS 当前处理顶点 | `_state` 增加 `processing` 与 `examined`；BFS 访问邻居时 `current=processing`，新邻居只作为 `examined`；图新增 examined 虚线状态；动作文字与状态行直接写“正在处理 A，检查 C” | 第 17 页步骤 5/15：A 实线、C 虚线、队列 B C；步骤 6 才 B 出队；14 项 graph_trace 测试 | 完成 |
| **P1-2** | 第 7 页表示对照 | 主图 + C 矩阵行 `A1 B1 C0 D1 E0` + C 邻接表 `0→A、1→B、2→D` 同屏；保留 5 格/3 项结论；删除会超出固定页高的完整矩阵展开，聚焦直接对照 | 第 7 页 1280/1440 截图；`matrix_row('C')` 与 `ADJ['C']` 同源 | 完成 |
| **P2-1** | 第 31–32 页链接表示 | 保留字段表；补充链记号：`P.firstout→a1→a2`、`S.firstin→a3→a4`；`A.firstedge→e1→e2`、`B.firstedge→e1→e3`、`C.firstedge→e2→e3`。未新增 SVG，避免挤压既有密表 | 第 31、32 页 1280/1440 截图；字段关系人工核对 | 完成（文本链记号，无新动画） |
| **P1-3** | 状态与算法测试 | `test_graph_trace.py` 增至 14 项；新增 `test_graph_forest.py` 5 项；新增 `test_c_crosscheck.py` 5 项；`test_graph_diagram.py` 覆盖 examined 状态 | `unittest` 45 项通过；C/Python 交叉核对通过 | 完成 |
| **P1-4** | 浏览器回归 | 新增可重复运行 `browser_player_check.py`；Chrome headless 遍历第 12、14、17 页全部 15 状态，检查边界按钮、上一步/重置、BFS 步骤 5/6；检查第 7、13、25、31、32 页与答案/注记 | `browser-player-check: PASS`；1280/1440 截图；未运行 Playwright | 部分完成（无 Playwright/打印/真实课堂） |

### 第 13 页答案折叠（本轮补充）

- 第 13 页新增学生可展开的“核对答案与理由”，默认收起；内容为 `A C D B`、下一位 D、再下一位 B、降序枚举理由（C 的 D/B/A，A 已访问，D 返回后 B）与树边 `AC`、`CD`、`CB`。
- 教师注记不再承载答案，只保留“2 分钟补全；先写 D、B，再展开核对”的课堂提示。
- 为容纳折叠答案，将原独立顶点映射表压缩为一行 `A=0、B=1、C=2、D=3、E=4`；邻接表行内仍显示 A(0)、B(1)、C(2)、D(3)。34 页结构未变。
- 1280×720 默认状态显示折叠条与教师注记；展开答案完整可见；1440×900 同步检查。

### 第 16 页教材定义视觉（本轮补充）

- 第 16 页“教材定义（概述）”由 `<p class="small">` 灰色脚注改为 `definition-box` 说明块：浅底、完整细边框、20px，与第 13 页“核对答案与理由”折叠框的边框语言一致。
- 第 13 页没有教材定义块（其新增块是折叠答案）；此处按第 13 页同类说明框统一，同时保留第 16 页教师注记。34 页结构未变。
- 1280×720 与 1440×900 默认状态检查；教师注记可见，无溢出。

### 第 17 页播放器字号与第 19 页引用（本轮补充）

- 第 17 页通过 `#slide-17` 作用域放大右侧：动作 21px、队列 20px、输出 20px、辅助说明 18px；第 12、14 页播放器保持原字号。1280×720 与 1440×900 检查，队列/输出/注记未溢出。
- 第 19 页删除“第 8 页不变量”引用（原引用页号错误且不必要）；“不重复”直接写“首次访问即标记；只安排未访问顶点”，不依赖跨页引用。
- 第 12、14 页 DFS 播放器不再展示/注明 `distance`：前面只引入 visited/parent，DFS 不需要该数组；第 23 页改为“DFS 树深”与 BFS 最少边数比较。BFS 的 `distance` 从第 16 页伪代码引入，第 17 页继续使用。
- 34 页结构、正式作业和其他页面未变。

## C. P0 正确状态

有向图 \(V=\{A,B\}\)、\(E=\{(B,A)\}\)：

| 外层顺序 | 实际过程 | 搜索森林 | 树数 |
|---|---|---|---:|
| A,B | 访问 A；再以 B 为根，B→A 发现 A 已访问，B 单独成树 | `{A}`、`{B}` | 2 |
| B,A | 从 B 访问 B、A；外层扫描 A 时跳过 | `{B,A}` | 1 |

`visited` 在整个全图遍历中只初始化一次，不同根之间不重置。两棵树不共享顶点；`{B,A}` 这棵树包含 SCC `{B}` 与 `{A}`，所以树数不是 SCC 数。两种顺序下 SCC 都是 `{A}`、`{B}`。

## D. BFS 状态语义

`graph_trace` 的 BFS 状态现在区分：

- `processing`：正在扫描邻接表的顶点；
- `examined`：当前检查的邻居；
- `visited`：已首次访问的顶点；
- `queue`：等待出队的顶点；
- `parent`、`distance`、`output`：首次访问来源、最少边数、输出序列。

A 检查 C 并入队时，`processing='A'`、`examined='C'`、`current='A'`；C 已 visited 且队列为 `B C`，图上的 A 是实线、C 是虚线，树边 A–C 为红色。B 出队后 `processing='B'`；B 检查已访问 C 时不重复入队；C 出队后才扫描 C 的邻接表。

DFS 检查：递归与显式帧的 `current` 始终是栈顶帧顶点；跳过已访问邻居仍推进游标；返回后恢复到父帧的正确 `next`。新增断言覆盖 `current == stack[-1].vertex` 和 C 返回 B 时 `B:next=2`。

## E. 教学检查

- 第 7 页教师可直接指着 C 行和 C 邻接表说明“矩阵 5 格 vs 表 3 项”，无需翻回第 6 页。
- 第 17 页步骤 5 可以直接指出“A 正在处理，C 刚被访问入队”，不会把 C 误认为已开始扫描；步骤 6 才看到 B 出队。
- 第 25 页可用 A,B / B,A 两种外层顺序解释“visited 不重置”，并区分搜索森林树数与 SCC。
- 第 31–32 页链记号把 firstout/firstin、firstedge 和共享弧/边记录显式化；没有新增动画，不增加课堂操作负担。
- 未声称真实课堂学习效果提高；上述是材料与演示层面的改进。

## F. 验证报告

执行：

```bash
python3 tools/deck/build.py D012
python3 tools/deck/check.py D012 --static-only
python3 tools/deck/check.py D011 --static-only
python3 -m unittest discover -s tools/deck/tests -v
python3 tools/deck/tests/browser_player_check.py
gcc -std=c11 -Wall -Wextra -fsanitize=undefined \
    -fno-sanitize-recover=all course/decks/d012-graph-traversal/code/traversal_demo.c \
    -o /tmp/d012 && /tmp/d012
```

结果：

- D012：34 页，`STATIC-ONLY-PASS`；D011：`STATIC-ONLY-PASS`（共享 graph_diagram/deck.css 未破坏默认图）。
- unittest：**45 项通过**（含 graph_trace 14、graph_forest 5、C/Python 交叉 5、graph_diagram examined）。
- 浏览器：`browser-player-check: PASS`；三播放器各 15 状态、边界按钮、重置、BFS 步骤 5/6 通过。
- 视觉：1280×720 与 1440×900 检查第 7、12、13、14、16、17、19、21、22、25、28、31、32 页；第 13、21、28 页答案展开、第 7 页教师注记展开在 1280×720 完整可见；第 16 页定义说明块在 1280/1440 可见。
- 未执行：Playwright 完整浏览器回归；打印/连续阅读下的折叠行为；真实教室投影、课堂用时和学习效果；第 31–32 页仍无动画。
- 截图/浏览器结果保存在本地临时目录，未全部提交入库；可复现命令和 `browser_player_check.py` 已入库。

## G. 关键文件与 Git

修改：

- `course/decks/d012-graph-traversal/slides.py`：第 7、17、25、31、32 页内容；第 28 页已在上一轮完成，本轮未改。
- `course/decks/d012-graph-traversal/index.html`：重新生成 34 页。
- `course/decks/d012-graph-traversal/README.md`：第四轮说明、测试计数、验证记录。
- `tools/deck/graph_trace.py`：BFS processing/examined、图例/动作。
- `tools/deck/graph_diagram.py`：examined 状态。
- `tools/deck/deck.css`：examined 虚线样式、森林表宽。
- `tools/deck/tests/test_graph_trace.py`：BFS/DFS 断言。
- `tools/deck/tests/test_graph_diagram.py`：examined 断言。
- `tools/deck/README.md`：状态语义与浏览器脚本说明。
- `docs/design/d012-review.md`：补第四轮报告链接。
- 新增 `tools/deck/tests/test_graph_forest.py`、`test_c_crosscheck.py`、`browser_player_check.py`。
- 新增本报告。

未 Commit、未 Push；工作区状态以最终 `git status` 为准。没有修改 `traversal_demo.c` 和正式作业范围。

## H. 遗留

- 真实课堂用时、学生产出和 7 分钟独立任务是否充分，需要教师后续观察。
- 浏览器检查只覆盖 Chromium headless；未运行 Playwright、打印、连续阅读和真实投影。
- 第 31–32 页采用文本链记号而未新增 SVG/动画；若课堂需要更直观，可在不增加页数的前提下另做局部结构图。
- 第 7 页完整矩阵未在同一页展开（固定页高会裁切）；C 行与 C 邻接表已满足本页对照目标。
