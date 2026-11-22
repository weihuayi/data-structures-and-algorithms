# D019｜三页隔离视觉原型（候选 08 / 23 / 29）

> 状态：已获教师对第一版独立视觉原型的审阅确认；本目录为**仓库公共组件适配与回归验证阶段**的候选实现，不是完整 D019 Deck，也不是课堂学习结果。

本目录检验三类关键页面：08 `insertion-trace`（保留记录身份和逻辑空位的状态轨迹）、23 `partition-independent`（先独立作答、后核对且原题持续可见）、29 `mechanism-map`（局部有序／已就位／跨区域约束三类性质）。候选页码对应已确认的 33 页 Storyboard；本隔离预览的实际页码是 1–3，不能把它登记为正式 33 页课件。

## 构建方式与主源边界

- `preview_source.py`：唯一的预览教学内容源；直接调用现行 `CourseDeck` 和 `task_workspace`，而不是手写其标记。
- `build_preview.py`：调用仓库 `tools/deck/build.py` 的 `render_document`、`headers.py` 和实际公共 CSS/JS；仅在构建过程中临时创建本目录 `slides.py` 兼容入口，`finally` 删除。绝不创建正式 `course/decks/d019-insertion-and-exchange/slides.py`。
- `index.html`：从预览源派生，禁止直接手改；共用样式由相对链接 `../../../../tools/deck/deck.css` 与 `components.css` 加载。
- `preview.css`：只用于本原型的算法特有状态、对象布局及字号；不修改全课程组件样式。
- `trace.js`：确定性算法状态生成，完整记录含身份、关键字、临时变量和空位；`preview.js` 负责呈现与按钮。

在仓库根目录运行：

```bash
python3 course/decks/d019-insertion-and-exchange/prototypes/build_preview.py
node course/decks/d019-insertion-and-exchange/prototypes/test_trace.cjs
```

然后在 Chromium/Chrome 打开 `course/decks/d019-insertion-and-exchange/prototypes/index.html`。如需测试资源路径，可从仓库根目录启动 `python3 -m http.server 8765`，浏览器访问对应路径。

## 专业与交互检查

- **插入**：待插入记录先暂存，空位随记录右移不断转移；中间状态应保持记录身份的多重集，只有完成一轮才声明新前缀有序。
- **划分**：首元素为枢轴，先右后左交替扫描；划分后左侧关键字不大于枢轴、右侧不小于枢轴；区域内部仍可能无序。重复关键字也必须符合此一般后置条件。
- **独立任务**：第 23 页采用真正的 `task_workspace`，其 `<details>` 默认收起。答案展开时题目、执行约定、原始输入与学生已填写内容仍然可见和可读。
- **机制比较**：区分“前缀已排序但可移动”“后缀最终就位”“枢轴位置已确定”，不重复 D020 的全算法比较表。

Node 测试包含两条固定输入、900 组确定性生成输入，以及包含重复关键字的排列保持、不变量和记录身份检查。浏览器验收还需检查 1280×720、1440×900、2048×1107 的默认／答案展开状态、分步按钮、页面切换和显示可达性。

## 阶段限制

本目录不是正式 Deck 主源，不代表 D019 全讲已经完成，也不应加入课程 Deck 注册表或更新实际授课记录。后续教师审阅通过后，按完整 Storyboard 在正式 `slides.py` 中重新登记全部页面，再删除或保留本原型为有来源的设计案例，**不得形成两个竞争性的课程主源**。