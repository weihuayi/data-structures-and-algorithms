# 数据结构与算法 | AGENTS | 仓库级协作约定

本文件定义 AI 助手在本仓库开展工作时应遵循的仓库级规则，重点是 `course/` 下 Deck 课件的生产流程与治理边界。它继承用户级全局约定，不重复定义通用 AI 协作底线。

## 一、仓库对象定位

本仓库同时承载课程教学、学生学习实践与真实项目开发，三条主要入口：

- `course/`：正式课程教学资产及允许公开的课程开设信息；
- `submissions/`：适合公开 PR 的学生作业提交；
- `src/`、`tests/`、`docs/`、`examples/` 等：项目实践工程目录。

默认只处理任务明确涉及的入口；跨入口修改先说明原因。

## 二、Deck 对象模型

Deck（`course/decks/dNNN-slug/`）是为真实课堂组织的一条相对完整的教学叙事，是课件的主要维护对象。

- Deck ID（如 D001）表示稳定资产身份，不等同于教学周次、课次或 45 分钟课时；
- 不按 Week 组织目录，不通过移动或重命名 Deck 表达教学进度；某学期实际推进位置记录在 `course/offerings/<offering>/`；
- 一个完整 Deck 的标准组成（四件套）：
  - `README.md`：设计卡（本质关系与接口方向）、教学目标、主要问题、案例、维护关系与课堂时间预算（分钟分配、断点、可砍页）；
  - `slides.py`：幻灯片主维护源，`SLIDES` 为 `[标题, body_html, 分节标签]` 三元组列表；
  - `index.html`：由构建工具生成的受控派生产物，不作为并列主源手工编辑；
  - `code/`：与该 Deck 强绑定的 C 课堂演示代码（C11，`gcc -std=c11 -Wall -Wextra` 可编译运行）。

学生课后材料以 slides（含可点开的教师注记）为主；不再维护独立的 handout 讲义（避免互动答案泄漏与双轨维护漂移）。

## 三、新 Deck 生产流程

当前共性以 [课程课件共性约定](docs/design/deck-contract.md) 为入口，分为必须满足、默认采用、按需选择；不要从某份旧课件复制出新的全局要求。先读本讲设计卡及所需公共模式说明，不依赖此前聊天记忆。

1. 在 `course/decks/` 下新建 `dNNN-slug/` 目录，NNN 接续现有编号，slug 用英文短横线命名；
2. 编写 `slides.py`：新课件使用 `tools/deck/components.py` 的公共模式与结构信息；保留三元组接口，旧课件可渐进接入，部分数与页数由认知任务决定；
3. 执行构建生成 `index.html`（见第四节），核对生成页数与源一致；
4. 补齐 `README.md`（含课堂时间预算），按需添加 `code/` 演示代码；
5. 在 `course/decks/README.md` 表格中登记，并更新建议顺序；
6. 如某一学期已开始使用，在 `course/offerings/<offering>/schedule.md` 记录实际推进。

## 四、构建与验证

```bash
python3 tools/deck/build.py all      # 构建全部 Deck
python3 tools/deck/build.py D001     # 构建指定 Deck（支持 Deck ID 或目录名）
```

- 构建工具与共享样式、交互组件位于 `tools/deck/`（`build.py`、`deck.css`、`deck.js`）；新增样式或交互组件加入共享层，不在单个 Deck 内私造；
- 修改 `slides.py`、共享 CSS/JS 后必须重新构建，提交前确认 `index.html` 与源同步（可用 `python3 tools/deck/check.py D008 --static-only` 只读核对，Deck ID 按实际对象替换）；
- 改动页面布局、公式或交互后，按 [验证工具说明](tools/deck/README.md#课件验证)检查目标投影尺寸、受影响步骤及折叠状态；自动检查未覆盖的交互或组合展开须人工补查并记录，不把构建通过或未覆盖当作完整验证通过；
- 演示代码修改后必须重新编译运行验证，遵循"先预测、再运行、再检查"的教学口径。

## 五、内容体例约定

- 叙事方式：案例驱动的问题链，而非教材章节式罗列；标题首先帮助学习者定位当前认知任务或理解焦点，有助于认知推进时优先用问题形式，不要求每页都提出问题；按分节标签组织叙事线；Deck 之间显式衔接（前一 Deck 留下问题，后一 Deck 回到问题）；
- 概念引入依据当前学习任务明确必要的认知依赖，组织问题、对象、信息、操作、表示、算法、成立条件、代价及验证之间实际需要建立的关系；关键前提应先于依赖它的结论，不要求所有概念执行同一条完整链条；教材术语准确对应，教材定义用「教材定义」引用块明确锚定，与案例解释分开呈现；
- 需要比较或映射对象时，用对照表支持结构化理解（如情境 ↔ 数学 ↔ C 表达、跨案例对比、教材概念 ↔ 课堂案例映射），不作为每页或每个 Deck 的固定形式；
- 课后练习放在 Deck 末尾"课后衔接"页；只有任务边界已确认的练习才进入 `course/assignments/` 成为正式 Assignment；
- 教师注记层：理念层与现场展开脚本以 `<details class="teacher-note">` 直接嵌入所在页 `body_html`，投影默认收起、打印保持收起，样式在共享层 `tools/deck/deck.css`；注记是可公开的教学注释——不出现可识别的学生个体，不引用考勤与表现性信息；教师私有备注不入库；
- WhyOS 的[课程工程 Memo](https://github.com/weihuayi/whyos/blob/develop/kb/structured_understanding_memos/courses/why_course_engineering_structured_understanding_memo.md)与[数据结构与算法 Memo](https://github.com/weihuayi/whyos/blob/develop/kb/structured_understanding_memos/courses/why_data_structures_and_algorithms_structured_understanding_memo.md)分别维护 Why 对课程工程、课程及领域结构的长期理解；[高质量幻灯片表达 Memo](https://github.com/weihuayi/whyos/blob/develop/kb/structured_understanding_memos/expression_and_communication/why_high_quality_slide_based_communication_structured_understanding_memo.md)提供制作与评审的认知输入。个人 Memo 不自动构成本仓库强制规则，教学表达需面向学习者转换。
- 本仓库 [Learning Progression](course/data_structures_algorithms_learning_progression.md)维护学习者认知演化的候选设计基线，不是更高优先级的正式治理依据；[Matrix](course/data_structures_algorithms_D001_D020_learning_progression_matrix.md)维护 Deck 与认知主线、最低学习证据及资产状态的映射。
- 具体 Deck 由 [Registry](course/decks/README.md)定位，`README.md` 维护当前设计与教学组织，`slides.py` 维护教学表达；相应 [Offering](course/offerings/2026-fall/schedule.md)记录某学期已经发生的课堂运行。设计、资产形成和运行记录均不能替代学生学习证据或能力达成判断。

具体修订方法、例证和适用边界见 [Deck 课件修订方法](docs/design/deck-revision-guide.md)。修订时遵循以下触发式约束：

- 当问题依赖结构关系或状态变化时，在任务所在处提供必要图示或状态；文字已足以完成任务时不强制加图或动画。
- 当对象在情境、数学表示、存储或程序之间转换时，明确对应关系与条件；修改编号、符号或例子后，核对关联图表、公式、代码和答案。
- 当页面要求学生独立预测或求解时，保留必要输入，按教学需要折叠提示与答案；不把解题必需信息一并隐藏。
- 当使用分步演示时，明确当前操作、工作状态、输出与完成标记的语义，并验证中间状态、返回和重置；静态概念页不因此承担交互要求。

## 六、公开性边界

本仓库为公开仓库。以下内容不得入库：

- 学生身份、成绩、课程群二维码等受限信息；
- 教师私有备注、运行资料（通过受限或本地工作空间维护，不写入公开 `slides.py` 或 `index.html`）。

## 七、Git 约定

- 主分支为 `main`；未经明确要求不执行 Commit、Push 等状态变更；
- 提交前检查最终 diff 只包含任务相关修改，且 `index.html` 等派生产物与源同步。
