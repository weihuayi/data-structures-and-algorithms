# D013 定向修订与验证报告

日期：2026-10-26。对象：[D013 设计卡](README.md)、[slides.py](slides.py)、[index.html](index.html)、[C 演示](code/mst_demo.c)、[mst_trace.py](../../../tools/deck/mst_trace.py)、[图形组件](../../../tools/deck/graph_diagram.py)。
性质：在已确认 MST 数学主线上做定向修订；不重写全部知识内容，不修改 D011/D012 教学内容，不扩大为堆优化 Prim 或反 Ackermann 证明。

## 1. 执行基线

- 仓库：`repos/weihuayi/data-structures-and-algorithms`；分支 `main`。
- 修订前 HEAD：`fc4d946e981f09d7d22f0fa000b6c9544f226740`（与任务给定 SHA 一致）。
- 修订前工作区无 D013 未提交改动；本报告列出本轮产生的改动。
- `git ls-remote origin HEAD` 因本机 SSH 配置权限错误失败；未 fetch/pull/push，不声称远程状态已改变。
- 教材：实际读取 `repos/inbox/数据结构与算法/数据结构6.pdf`；核对 6.1.2、6.6.1、MST 性质、算法 6.8、表 6.1。教材图未复制。

## 2. 原问题与修订措施

| 原问题 | 修订 |
|---|---|
| 主图与三角形反例为 ASCII，边权与边对应不清晰 | 新增 SVG 带权主图、DFS 三角反例、n−1 反例、割、交换论证、独立练习图；边权使用手动标签位置，避免 5/6 重叠 |
| 28 页缺少独立大纲与四部分标题，课堂路线不清 | 增加大纲页和四个小节标题页；形成 33 页，四部分时间 19+17+22+27 分钟，另 5 分钟机动 |
| Prim 只有完整状态表，不能逐步控制 | 新增 `prim_states()` 9 个真实状态和 Prim 播放器：S、selected_edges、key、parent、has_key、current_edge、total、components；先候选后接受 |
| Kruskal 只有结果表，分组与 DSU parent 混在一起 | 新增 `kruskal_states()` 16 个真实状态和 Kruskal 播放器：排序边、当前边、接受/拒绝、分组、DSU parent、总权；候选/拒绝/已选三类边独立标记 |
| 原独立练习 P–S 为 PQ4、QS1，答案为总权4 | 按任务改为 PQ3、PR1、QR2、QS4、RS5；接受 PR1、QR2，拒绝 PQ3（MST 未完成），接受 QS4，拒绝 RS5，总权 7 |
| `checks()` 依赖 `assert(build(...))` 等有副作用断言 | C 改为 `CHECK` 宏，构建/合并等副作用不依赖 assert；默认与 `-DNDEBUG` 均执行 |
| 教材 `closedge/Vexset` 与程序 `key/parent/DSU` 容易混淆 | README、第 13、19–21、25 页及教师注记说明字段对应与成本差异；不把 Vexset 判错，不把 DSU 摊还界等同全表重编号 |

## 3. 数学与数据一致性

- 主例：A–E；AB1、AC4、BC2、BD5、CD3、CE6、DE7；MST AB、BC、CD、CE，总权 12。
- Prim 从 A：AB、BC、CD、CE，总权 12；从 C：CB2、BA1、CD3、CE6，总权仍 12。
- Kruskal：AB、BC、CD 接受，AC、BD 拒绝，CE 接受，DE 拒绝；总权 12。
- 等权 CE/DE=7：总权 13，多解；DE=0：总权 6；删 CE/DE：MSF 2 分量总权 6；负权 AB=-2、BC=0：总权 -2。
- 独立练习：PR1、QR2、PQ3（同组拒绝，发生在完成前）、QS4、RS5（拒绝），总权 7；选 QS 时割 S={P,Q,R} 的跨界边 QS4、RS5。
- 图中候选/拒绝/已选边、分组、DSU parent 与状态数据同源；Prim `key` 是接入边权，不是源路径距离；DSU parent 不是 MST 边。

## 4. 状态模型与测试

- [mst_trace.py](../../../tools/deck/mst_trace.py)：主例/练习数据、Prim/Kruskal 状态、播放器。
- [test_mst_trace.py](../../../tools/deck/tests/test_mst_trace.py)：13 项，覆盖 Prim 候选跨割与 key/parent、接受后总权、从 C、非连通重启、等权/零权/负权；Kruskal 排序、接受/拒绝前后分组、选中/拒绝边、DSU parent 与分组对应、练习；播放器 9/16 状态和控制。
- 完整 `python3 -m unittest discover -s tools/deck/tests`：**58 项通过**（D012 既有 45 + D013 13）。
- [browser_mst_check.py](../../../tools/deck/tests/browser_mst_check.py)：Chrome headless 检查 Prim 9 状态、Kruskal 16 状态、next/prev/reset/边界、Kruskal 候选/拒绝 CSS 类；结果 `browser-mst-check: PASS`。

## 5. C11 验证

```bash
gcc -std=c11 -Wall -Wextra -Werror course/decks/d013-mst-and-union-find/code/mst_demo.c -o /tmp/d013
/tmp/d013
gcc -std=c11 -DNDEBUG -Wall -Wextra -Werror ... -o /tmp/d013-nd
/tmp/d013-nd
gcc -std=c11 -Wall -Wextra -fsanitize=address,undefined -fno-sanitize-recover=all ... -o /tmp/d013-san
/tmp/d013-san
```

三组均通过，`All classroom checks passed.`；输出覆盖 base/ties/homework DE=0/isolated E/negative and zero，总权分别为 12/13/6/6/-2。`checks()` 的构建和合并副作用不再依赖 `assert`。

## 6. 构建与浏览器/视觉

- `python3 tools/deck/build.py D013`：33 页；`check.py D013 --static-only`：`STATIC-ONLY-PASS`。
- Chrome headless：1280×720 全部 33 页截图；1440×900 抽查主图、割/交换、Prim/Kruskal 玩家、独立练习、作业等关键页。
- 已检查 1280×720 第 5、8、12、18、29 页与 1440×900 主图/玩家；第 29 页答案默认折叠，展开后 1280×720 完整可见。截图临时位置：`/home/why/whyos/.tmp-d013-current2/`（1280 全 33 页）、`/home/why/whyos/.tmp-d013-1440/`（1440 抽查）；不提交入库。
- 未执行：Playwright 完整回归、打印/连续阅读下的全部折叠行为、真实教室投影；未重跑旧版 4,165 图穷举测试。

## 7. 课堂时间与学习活动

- 33 页：第一部分 19 分钟、第二部分 17、第三部分 22、第四部分 27，另 5 分钟机动，总计 90。
- 约 45 分钟断点在第 18 页 Kruskal 推演后。
- 第 29 页保留 7 分钟独立作答 + 2 分钟反馈；输入和图默认可见，答案默认隐藏。
- 可下沉：第 21 页路径压缩代码、第 26 页 C 字段、第 9 页完整交换论证口述；不先删独立活动。

## 8. 文件与 Git

修改：`README.md`、`slides.py`、`index.html`、`code/mst_demo.c`、`tools/deck/graph_diagram.py`、`tools/deck/deck.css`、`tools/deck/README.md`。
新增：`tools/deck/mst_trace.py`、`tools/deck/tests/test_mst_trace.py`、`tools/deck/tests/browser_mst_check.py`、本报告。

未 Commit、未 Push；等待用户检查与授权。未修改 D011/D012 教学内容、学习主线、Matrix、Memo 或课程治理资产。

## 9. 残余风险与后续评审重点

- 教学效果、7 分钟是否足够、第 18 页 6 分钟推演是否超时，需真实课堂证据。
- 浏览器只覆盖 Chromium headless；未验证打印、连续阅读、无 JS 的所有折叠组合。
- Prim/Kruskal 播放器是 D013 专用状态模型，不宣称任意图/堆优化/教材全表实现。
- 人工评审重点：候选/拒绝/已选三类边是否混淆；Prim `key` 与 BFS/Dijkstra 距离是否混读；Kruskal DSU parent 是否被误当结果边；第 29 页 PQ 拒绝是否发生在完成前。
