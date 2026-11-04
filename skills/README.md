# Skills | 课程 AI 协作技能

本目录维护课程级可复用的 AI Skill。课件、工程实现和事实记录仍由 `course/`、`docs/`、`tools/`、相关 PR/课堂来源分别负责；技能文件不是自动化服务或对教学效果的证明。

| 技能 | 启用情境 | 唯一主源 |
| --- | --- | --- |
| **dsa-design-case-curation** | 从真实课件评审、课堂反馈、讨论及历史修订中发现、重构、评审或经授权入库表达设计案例 | [`dsa-design-case-curation/SKILL.md`](dsa-design-case-curation/SKILL.md) |

## 调用示例

- **发现**：“用 `dsa-design-case-curation` 检查 D015 真实修订，先提出表达设计案例候选及必要来源，不写仓库。”
- **重构**：“按 `dsa-design-case-curation` 将 D010 的指定问题重构为真实设计案例草稿，标明证据与未知项。”
- **入库**：“用 `dsa-design-case-curation` 将已确认的案例入库 `kb/design_cases/`，经临时分支提交 PR，不合并。”

## 主维护与执行器发现

`skills/dsa-design-case-curation/SKILL.md` 是**唯一正文主源**；`kb/design_cases/` 维护案例实例。

对于从 `.agents/skills/` 发现仓库级技能的 Codex，可将 `.agents/skills/dsa-design-case-curation` 设为指向主源目录的**相对符号链接**，避免维护第二份技能文件。符号链接存在不等于执行器已识别或正确使用：自动发现和实际调用还须在相应 Codex 版本及工作目录下验证。其它执行器按自身发现规则显式加载主源。

当前版本为课程试点，后续是否增加脚本、模板、检查器或更多案例，由真实复用和失败反馈决定。
