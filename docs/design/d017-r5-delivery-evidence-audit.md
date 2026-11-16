# D017｜R5 交付验证证据复核（PR-A）

> **性质**：2026-11-16 的事后审计；仅记录实际取得的公开 GitHub Actions 工作流状态、Job 步骤和日志摘录。原始日志与截图由对应 Actions run 和 artifact 维护；本文件不替代原始证据，不声称重跑历史环境，也不证明教师审阅或学生学习效果。
>
> **范围**：D017 的 PR #30、#38、#39、#40 最终 PR head SHA 对应的课程检查工作流；Harness 工作流单独记录。数据为审计时可读取的 GitHub 历史记录，并非每个 PR 的全部提交或全部人工审阅事件。

## 一、可追溯的版本及机器结果

| PR / 版本 | 课程检查 run（最终 head SHA） | 机器结果与范围 | 原始证据 |
| --- | --- | --- | --- |
| [#30](https://github.com/weihuayi/data-structures-and-algorithms/pull/30) / `9be97f5a646d` | [43667300825](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43667300825) | **failure**；static、homework、semantic、checker-regression、legacy-review-context、legacy-baseline 返回0；adopted-full 与 legacy-defaults 返回1；本次未逐项核实全部失败页面 | [artifact 14142946050](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43667300825/artifacts/14142946050) |
| [#38](https://github.com/weihuayi/data-structures-and-algorithms/pull/38) / `21eb3645357a` | [43769361240](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43769361240) | **failure**；adopted-full 返回1；报告摘要列出5个 D017 在1280×720下的纵向溢出，以及旧课件布局问题 | [artifact 14183342917](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43769361240/artifacts/14183342917) |
| [#39](https://github.com/weihuayi/data-structures-and-algorithms/pull/39) / `3bc732e3507f` | [43771179491](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43771179491) | **failure**；同样列出5个 D017 1280×720纵向溢出；不因该 PR 修复了对比度就声称整讲布局通过 | [artifact 14183699134](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43771179491/artifacts/14183699134) |
| [#40](https://github.com/weihuayi/data-structures-and-algorithms/pull/40) / `37cc447c3018` | [43774607405](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43774607405) | **success**；static、homework、semantic、checker-regression、adopted-full、legacy-review-context、legacy-baseline 返回0；legacy-defaults 返回1，但最终分类为 `scoped-pass-with-legacy-findings` | [artifact 14186070982](https://github.com/weihuayi/data-structures-and-algorithms/actions/runs/43774607405/artifacts/14186070982) |

四个版本的 `Course AI harness checks` 工作流均显示 success；其作用是检查协作工程入口/Skill 等结构约束，并不等于课件内容或浏览器验证已通过。

## 二、已从原始 Job 日志定位的 D017 失效

PR #38 与 #39 的课程检查 Job 日志，在 `adopted-full` 阶段列出下列 D017 1280×720 默认投影纵向溢出（以日志报告值为准）：

| 稳定页面 ID | 纵向溢出 |
| --- | ---: |
| `bst-insert` | 71 px |
| `bst-delete-cases` | 37 px |
| `build-shape-chain` | 43 px |
| `compare-path` | 75 px |
| `avl-definition` | 23 px |

两个版本另有 D001、D002 的 `legacy-defaults` 布局发现；日志中列出的旧页溢出不能当作 D017 的新缺陷。PR #40 的 `adopted-full` 返回0，但保留旧课件基线分类，说明**最终合格状态与曾经失败的历史版本不能互相替代**。

前述证据只覆盖最终 PR head SHA 上的有关工作流。尚未复核全部截图、原始 `verification.json` 内所有检查项目、审阅记录或相关 PR 的每次提交，不推断其余检查都曾通过。

## 三、问题机制及证据边界

1. **代码对比度**：PR #39 已通过源码和差异记录定位 `pre` 浅色前景与 D017 代码区浅色背景的继承冲突，并新增课件专用颜色对比度回归。此前构建及部分浏览器检查未阻断此问题的精确原因，需要结合当时的检查范围和页面证据分析；不简单归结为“没有运行浏览器”。
2. **认知前置、删除状态与数学表达**：PR #40 修订专业表达，并添加特定页面的静态/语义断言。测试通过不证明学生实际理解。
3. **布局**：PR #38/#39 明确出现 D017 的新增布局失败；PR #40 最终 `adopted-full` 成功，不能据此宣称后排投影可读性已被教师确认。
4. **README 状态漂移**：PR #38 已增加 C11 `avl27` 模式，但 README 的一处描述仍称未实现；同一文件还保留“下一阶段制作五页原型”的旧计划。本次 PR-A 按当前程序/历史 PR 修正叙述，不修改 C11 或课堂任务。

## 四、对 Q1–Q3 的阶段性回答

- **Q1（此前未发现的原因）**：已取得可核对的检查阶段与实际失败记录，不能再概括为“CI 全部通过”；但对比度漏检、专业语义漏检的具体执行/审阅机制尚未完整还原。保留未决。
- **Q2（问题是否得到修复）**：PR #39/#40 建立针对已知缺陷的局部回归，PR #40 最终课程验证为 success；公共视觉检查的漏报/误报与跨课件泛化尚未验证。
- **Q3（教学效果）**：尚无 D017 的本轮学生作答、课堂节奏、后排投影可读性和迁移能力实测证据。所有机器检查结论均不能替代这些证据。

## 五、后续处置建议（不等于已执行）

- T3：先完成 D017 描述事实的局部一致性修复，不自动生成所有 README 文本；仅针对稳定、可判定的接口事实考虑回归。
- T4：先以正常/低对比/继承冲突/复杂背景等夹具验证浏览器计算样式检测的价值；未验证前不声称通用可读性保障。
- T5：对历史缺陷开展定向 AI 审阅对照，明确目标、发现、误报与审阅成本；不要仅增加新的强制栏目。
- T6：依据现有 `impact.py` 与 `verify.py` 按影响范围回归，保留原始失败与覆盖边界。

**维护边界**：本文件是一次具有固定来源的历史证据摘要。课程源码、PR、Actions run 与生成报告仍为原始事实来源，不另建竞争性的测试报告主源。
