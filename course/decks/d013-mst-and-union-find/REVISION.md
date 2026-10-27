# D013 定向修订与验证报告

对象：[D013 设计卡](README.md)、[slides.py](slides.py)、[index.html](index.html)、[C 演示](code/mst_demo.c)、[mst_trace.py](../../../tools/deck/mst_trace.py)、[图形组件](../../../tools/deck/graph_diagram.py)。
性质：在已确认 MST 数学主线上做定向修订；不重写全部知识内容，不修改 D011/D012 教学内容，不扩大为堆优化 Prim 或反 Ackermann 证明。

## 第一轮（2026-10-26）

第一轮完成：33 页四部分结构；Prim/Kruskal 受控播放器；A–E 主例与 P–S 独立练习；SVG 图示；C11 `CHECK` 宏替代有副作用的 `assert`；`mst_trace.py` 状态模型与测试；构建和 Chrome 检查。修订前 HEAD 为 `fc4d946e981f09d7d22f0fa000b6c9544f226740`，第一轮结果已包含在 HEAD `0f5c7dd` 中。第一轮遗留的知识顺序问题由本轮处理。

## 第二轮（2026-10-28）执行基线

- 仓库：`repos/weihuayi/data-structures-and-algorithms`；分支 `main`。
- 修订前 HEAD：`0f5c7ddcc53169d226f6f8784a41d7741b6ba83c`，与任务给定 SHA 一致；工作区干净，无用户未提交修改。
- `git ls-remote origin main` 与 `git ls-remote https://...` 均因本机 SSH 配置权限错误（`/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf`）失败；未 fetch/pull/push，不声称远程状态已改变。
- 教材：沿用第一轮已读取的 `repos/inbox/数据结构与算法/数据结构6.pdf` 口径；本轮未新增教材引用。
- 本轮未执行 Commit、Push、reset、clean。

## 1. R1–R8 修订结果

| 项 | 原问题 | 本轮修订 | 证据 |
|---|---|---|---|
| R1 | 封面引导句在 1280×720 出现“接？”孤行 | 副标题改为“每次选便宜的边，怎样保证总成本最小？”；不缩小全局字号 | 1280/1440 浏览器测量 `.lead` 只有 1 行；截图 |
| R2 | 大纲提前使用 Prim/Kruskal | 四部分改为学习问题：定义最低成本、逐步扩张、按成本合并分组、检查与代价；算法名留到各部分正式页 | 第 2 页无 MST/MSF/Prim/Kruskal/DSU/并查集；内容测试锁定 |
| R3 | 第 8 页先用 MST 缩写，未正式定义 | 第 6 页首次给出“最小生成树（Minimum Spanning Tree，MST）”及前提/候选解/目标；第 15 页定义“最小生成森林（Minimum Spanning Forest，MSF）”；Prim 11、Kruskal 17、DSU 19 首次出现均带全称 | 内容测试逐项检查首次定义页 |
| R4 | Prim 先看含 key/parent 的播放器，后解释状态 | 第 10 页只提“怎样扩大已连接区域”；第 11 页给 Prim 数学规则与安全边；第 12 页分“输入图—抽象状态—程序表示”三层，解释 S/F/key/parent/has_key/used/selected；第 13 页才播放 | 第 12 页无播放器，第 13 页有播放器；内容测试 |
| R5 | Kruskal 播放器先出现 DSU 父指针，之后才定义 DSU | 第 16 页提“合并不同分组”；第 17 页给排序/同组判断/接受拒绝；第 18 页只显示 F、分组、拒绝与总权，不显示父指针；第 19 页定义并查集；第 20 页并列三对象；第 21 页路径压缩 | 第 18 页文本无 DSU/父指针；第 20 页真实快照；内容测试 |
| R6 | 割页只标 S 与候选 BC，未显示 F | 第 8 页明确 F={AB}、S={A,B}、割尊重 F、全部跨界边 AC4/BC2/BD5、最轻 BC2；右图加入 BC 后 F′={AB,BC}、新割跨界 BD5/CD3/CE6、最轻 CD3 | 两幅静态图 + 边标记 F/e；截图 |
| R7 | 交换论证主图没有真正显示 T→T+e→T+e−f | 第 9 页改用独立等权三角形 AB=1、AC=2、BC=2；三阶段 T={AB,BC}、T+e 成环、T′={AB,AC}；标出 F/e/f；两棵树总权均为 3 | 三幅静态图；内容测试锁定权值与前提 |
| R8 | DSU 父指针缺少忠实静态图 | 第 20 页用真实快照（接受 AB/BC/CD、拒绝 AC）画已选森林、分组、父指针树；第 21 页用独立辅助例 AB/CD/BC 画压缩前后父指针树与数组；明确标注“不是主例” | `dsu_diagram()` 直接消费快照；截图；测试 |

## 2. 新旧页面对应

| 旧页 | 新页 | 变化 |
|---:|---:|---|
| 1 | 1 | 封面句式修复 |
| 2 | 2 | 大纲改为四个学习问题 |
| 3–5 | 3–5 | 保留；第 4 页补 DFS 全称 |
| 6 | 6 | 正式定义 MST（中/英/缩写、前提、候选解、目标） |
| 7–9 | 7–9 | 第 8 页补 F 与两阶段割；第 9 页换独立交换论证图 |
| 10 | 10 | 改为“怎样让已连接区域逐步扩大？” |
| 11 | 11 | Prim 机制页改为正式算法规则与安全边 |
| 12 | 13 | Prim 播放器后移，先建立辅助状态 |
| 13 | 12 | `key/parent/has_key` 并入三层辅助信息页 |
| 14–15 | 14–15 | 保留；第 15 页补 MSF 全称 |
| 16 | 16 | 改为“怎样依次合并不同连通分组？” |
| 17 | 17 | Kruskal 机制页改为正式算法规则 |
| 18 | 18 | 播放器保留；移除 DSU 父指针，只显示分组 |
| 19 | 19 | 并查集正式定义（中/英/缩写/别名、能力、边界） |
| 20 | 20 | 从“parent 是不是图边”扩为“森林/分组/父指针”三对象真实快照 |
| 21 | 21 | 路径压缩改为独立辅助例的压缩前/后静态对照 |
| 22–33 | 22–33 | 保留数学结论；第 26 页 C 状态字段与 Prim/DSU parent 语义更新 |

## 3. 概念首次引入位置

| 术语/对象 | 首次页 | 位置与说明 |
|---|---:|---|
| DFS | 4 | “深度优先搜索（DFS）”，回收 D012 |
| MST | 6 | “最小生成树（Minimum Spanning Tree，MST）”，数学对象，不绑定实现 |
| Prim / Prim's Algorithm | 11 | “普里姆算法（Prim's Algorithm）”，先规则后状态 |
| MSF | 15 | “最小生成森林（Minimum Spanning Forest，MSF）” |
| Kruskal / Kruskal's Algorithm | 17 | “克鲁斯卡尔算法（Kruskal's Algorithm）” |
| 并查集 / DSU / Union-Find | 19 | “并查集（Disjoint Set Union，DSU；又称 Union-Find）” |
| 父指针 | 20 | 第 18 页播放器不显示；第 20 页才作为学习对象 |
| `key/parent/has_key/used/selected` | 12 | 在抽象状态之后给程序字段，不先于 S/F |

## 4. Prim 的知识依赖调整

1. 第 10 页只问“怎样让已连接区域逐步扩大”，不出现 Prim、key、parent。
2. 第 11 页给出数学构造：S={s}、F=∅；取跨越 S 的最轻边；接受边与外部顶点；说明依赖安全边性质。
3. 第 12 页问“计算机要保存什么”，分三层：
   - 输入图 G=(V,E,w) 与邻接矩阵/邻接表：只描述连接，不保存执行进度；
   - 抽象状态：S、F、key[v]=min{w(u,v):u∈S 且 uv∈E}、parent[v]、has_key[v]；
   - 程序表示：used、key、parent、has_key、selected。
4. 第 13 页才观察播放器；每步显示 S、候选入口、F、总权。
5. 第 14 页从 C 起点预测，第 15 页处理非连通/MSF。
6. 明确 `key` 是接入边权，不是最短路径距离；`parent` 候选阶段不是已接受结果边。

## 5. Kruskal 与 DSU 的知识依赖调整

1. 第 16 页只提“按成本顺序合并不同分组”，不出现 Kruskal/DSU。
2. 第 17 页给排序、同组判断、接受并合并、终止与安全边依据。
3. 第 18 页播放器只显示候选边、已选森林 F、当前分组、接受/拒绝原因、总权；内部 DSU 状态保留在模型里，但不出现在教学视图。
4. 第 19 页由“怎样高效维护分组”引出并查集：find 代表、union 合并、服务判环、不能单独保证最优、分组来自已选边。
5. 第 20 页并列三种对象：已选森林 F、F 诱导的划分、DSU 父指针树；用真实快照说明 p[B]=A 恰好与 AB 重合、p[C]=A 对应已拒绝的 AC、p[D]=A 在原图中没有 AD。
6. 第 21 页用独立辅助例对照压缩前后父指针，强调集合成员关系不变、D→A 不是新增图边。
7. 第 22 页再回到“不成环不足以保证最优”，把可行性与最优性证据分开。

## 6. DSU 父指针快照问题的原因与修复

原实现：

```python
def parents(self):
    return {v: self.find(v) for v in self.parent}
```

`find()` 带路径压缩，因此 `parents()` 不是只读观察，而是会改写内部父指针；`components()` 也调用 `find()`，同样可能改变被观察对象。结果是把真实父指针错误地“拍平”为直接指向根，掩盖了深层结构。

修复：

- 新增只读 `root(x)`：沿父指针走到根，不压缩；
- `parents()` 改为 `dict(self.parent)`，复制真实父指针；
- `components()` 用 `root()` 分组，不改变内部状态；
- `find()` 保留路径压缩，作为算法操作；
- `kruskal_states()` 中同组判断只调用一次 `find(a), find(b)`，接受后 `union()` 的正常 `find()` 仍可压缩；快照在操作后复制；
- `path_compression_demo()` 用 AB、CD、BC 构造非扁平状态，先只读快照，再执行 `find(D)`，再快照；
- `dsu_diagram()` 直接消费传入的父指针映射，不调用 `find()`。

新增定向测试：

- 深层状态 `{A:A, B:A, C:A, D:C}` 的快照前后不变，`parents()['D']=='C'`；
- `components()` 重复调用不改变父指针，分组仍为 `{A,B,C,D}`；
- `find('D')` 压缩为 `p[D]=A`，分组不变；
- 不同父指针结构（星形/链形）编码同一划分；
- 路径压缩演示的前后快照与代表；
- 静态 DSU 图只画真实父指针（`D-C`、`C-A`，不画 `D-A`）；
- 每个 Kruskal 状态沿父指针递归求根，根集合与 `components()` 完全一致，不假定直接指向根；
- 播放器不显示 DSU 父指针。

## 7. 数学图示与数据一致性

- 主例：A–E；AB1、AC4、BC2、BD5、CD3、CE6、DE7；MST AB、BC、CD、CE，总权 12。
- Prim 从 A：AB、BC、CD、CE，总权 12；从 C：CB2、BA1、CD3、CE6，总权仍 12。
- Kruskal：AB、BC、CD 接受，AC、BD 拒绝，CE 接受，DE 拒绝；总权 12。
- 等权 CE/DE=7：总权 13，多解；DE=0：总权 6；删 CE/DE：MSF 2 分量总权 6；负权 AB=-2、BC=0：总权 -2。
- 第 8 页：F={AB}、S={A,B}；跨界 AC4、BC2、BD5；加入 BC 后 F′={AB,BC}、S′={A,B,C}；新跨界 BD5、CD3、CE6，最轻 CD3。
- 第 9 页：T={AB,BC}、F={AB}、e=AC、f=BC、T′={AB,AC}；三阶段总权均 3。
- 第 20 页：真实快照 F={AB,BC,CD}，AC 已拒绝，分组 `{A,B,C,D}`、`{E}`，父指针 `A→A、B→A、C→A、D→A、E→E`。
- 第 21 页：压缩前 `B→A、C→A、D→C`；压缩后 `D→A`；分组不变。
- 独立练习：PR1、QR2、PQ3（同组拒绝，发生在完成前）、QS4、RS5（拒绝），总权 7；选 QS 时割 S={P,Q,R} 的跨界边 QS4、RS5。
- 图中候选/拒绝/已选边、分组、父指针与状态数据同源；Prim `key` 是接入边权，不是源路径距离；DSU 父指针不是 MST 边。

## 8. 构建、测试与 C11

实际执行：

```bash
python3 tools/deck/build.py D013
python3 tools/deck/check.py D013 --static-only
python3 -m unittest discover -s tools/deck/tests -v
python3 tools/deck/tests/browser_mst_check.py
```

结果：

- 构建 33 页；`STATIC-ONLY-PASS`。
- 单元测试 **73 项通过**：D013 27 项（Prim 6、Kruskal 5、DSU 快照 6、播放器 2、页面内容 8）；其余 46 项（含新增的 `edge_notes` 回归）。
- `browser_mst_check.py` 在 1280×720、1440×900 两档检查：封面单行、33 页无纵向溢出、Prim 9 状态、Kruskal 16 状态、next/prev/reset/边界、Kruskal 候选/拒绝类；输出 `browser-mst-check: PASS`。
- C11 默认、`-DNDEBUG`、ASan/UBSan 编译运行通过；`All classroom checks passed.`；输出 base 12、ties 13、homework 6、isolated 6、negative -2。
- `check.py D013 --screenshots pages` 的完整浏览器段因本机未安装 `playwright` 返回 `INCOMPLETE`（`Cannot find module 'playwright'`）；静态段仍通过。未安装依赖、未绕过检查。
- 1280×720 全部 33 页截图；1440×900 抽查并逐页测量。截图临时位置：`/home/why/whyos/.tmp-d013/final/` 与 `.tmp-d013/after/`，不提交入库。
- 第 29 页答案展开后 1280×720、1440×900 纵向溢出均为 0。

## 9. 课堂时间

- 33 页：第一部分 19 分钟、第二部分 17、第三部分 22、第四部分 27，另 5 分钟机动，总计 90。
- 约 45 分钟断点在第 18 页 Kruskal 演示后：19+17+0.5+3+6=45.5，约 45。
- 第 29 页保留 7 分钟独立作答 + 2 分钟反馈；输入和图默认可见，答案默认隐藏。
- 可下沉：第 21 页路径压缩细节、第 26 页 C 字段、第 9 页完整交换论证口述；不先删独立活动。
- 新增内容没有增加页数：旧第 13 页（key/parent）合并进新第 12 页，旧第 12 页播放器后移为新第 13 页；第 11 页替换旧 Prim 机制页，页数仍为 33。

## 10. 修改文件

修改：

- `course/decks/d013-mst-and-union-find/slides.py`
- `course/decks/d013-mst-and-union-find/README.md`
- `course/decks/d013-mst-and-union-find/index.html`（由 `build.py` 生成）
- `course/decks/d013-mst-and-union-find/REVISION.md`
- `tools/deck/mst_trace.py`
- `tools/deck/graph_diagram.py`（`edge_notes` / `edge_note_positions`，默认行为不变）
- `tools/deck/deck.css`（D013 图示/状态层/紧凑布局）
- `tools/deck/README.md`
- `tools/deck/tests/test_mst_trace.py`
- `tools/deck/tests/test_graph_diagram.py`（`edge_notes` 回归）
- `tools/deck/tests/browser_mst_check.py`

新增：

- `tools/deck/tests/test_d013_slides.py`

未修改：C 程序、D011/D012 教学内容、Learning Progression、Matrix、Memo、课程治理资产、其他 Deck。

## 11. 残余风险与后续评审重点

- 教学效果、第 12 页 4 分钟是否足够、第 18 页 6 分钟是否超时，需真实课堂证据。
- 浏览器只覆盖 Chromium headless；Playwright 完整折叠/组合、打印/连续阅读、真实投影未执行。
- 第 21 页是独立辅助例，学生仍可能误认为主例执行状态；需口头强调。
- 第 12 页三层状态信息密度高；若课堂反馈过载，可把“程序表示”层下移为注记，但不改变抽象状态页的顺序。
- Prim/Kruskal 播放器是 D013 专用状态模型，不宣称任意图/堆优化/教材全表实现。
- 人工评审重点：候选/拒绝/已选三类边是否混淆；Prim `key` 与 BFS/Dijkstra 距离是否混读；Kruskal 播放器是否仍暗示父指针；第 20 页 p[D]=A 是否被误当图边 AD；第 9 页等权交换是否被误当“主例多解”。
