# Harness | 课程 AI Skill 的确定性检查

本目录为课程仓库的 AI Skill 提供**只读、轻量、确定性**的结构检查，与 `tools/deck/` 的课件语义和浏览器验证保持独立。技能正文以 `skills/` 为唯一主源；`.agents/skills/` 只承载指向主源的发现适配链接。

## 运行

```bash
python3 tools/harness/check_skills.py
python3 -m unittest discover -s tools/harness/tests -v
```

`check_skills.py --root <repo-path>` 可检查指定仓库，错误时返回非零状态。无需额外 Python 依赖，不修改被检查文件。CI 通过 `.github/workflows/harness-check.yml` 在 PR 和主分支推送时运行；检查足够轻量，因此不使用路径过滤，以免误使必需检查挂起。

## 覆盖范围

- Skill `SKILL.md` 中简易 YAML frontmatter 的名称、描述、目录同名及索引入口；当前约定为单行标量 `name` 与 `description`。
- `.agents/skills/` 相对符号链接的目标正确、存在、不越界，并禁止复制为并列技能正文或留下无主入口。
- 根协作入口、技能目录、案例索引和技能正文中的**基本 Markdown 行内本地链接**是否指向仓库内实际文件或目录；案例 Markdown 文件应被案例索引引用。
- 使用正常与故障夹具检验缺失文件、错误元数据、无效链接及越界引用能够触发失败。

## 不验证的事项

本工具**不**验证 GitHub 外部链接是否可访问、Markdown 锚点、全部复杂 Markdown 语法、知识源内容是否真正支持主张、案例质量、学生学习效果、用户是否实际授权、Agent 是否正确调用 Skill，也不证明 Codex 的真实自动发现能力。这些需要按任务由 AI、工具或人另行核验；不要把静态检查通过当作这些结论的证据。
