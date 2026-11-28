# D021｜合并后质量压力测试记录

基线：`3e545c7c7b9416a872eb4a7c713459f3a65faa20`（PR #69 合并版）。目标是课件可供教师可靠审阅，不将固定课时或页数作为认知设计硬指标，也不宣布课堂学习效果。

## 标准与流程

| ID | 标准 | 验证路径 |
| --- | --- | --- |
| QA01 | 目标与职责：校园讨论先于抽象和发布，D021 不代做题 | 逐页源审阅、末页顺序断言 |
| QA02 | 真实性：观察、假设、构造数据、真实成果分开 | 逐页源审阅、教师公开素材边界 |
| QA03 | 完整性：现实需求、对象、关系、输入输出与条件连续 | 主例逐页核对 |
| QA04 | 接续：旧知入口、先修条件、术语和关键问题 | Storyboard、README 派生表、专业审阅 |
| QA05 | 专业正确性：题面、边界、算法、代价、独立答案 | 独立参考结果、C11 测试、故障夹具 |
| QA06 | 视觉：D018–D020 首末页语言、等高并列块、投影可读 | 1280×720/1440×900 默认及展开态截图；人工视觉审阅 |
| QA07 | 交互：任务上下文保持、答案默认隐藏、导航与打印 | 公共 checker 全操作 |
| QA08 | 期末发布：唯一主源、三题任选一、个人报告、无阶段提交 | 末页及作业检查 |
| QA09 | 工程：构建一致、稳定 ID、链接、依赖 | 正式 build.py 后 git diff、check.py |
| QA10 | 回归：原始失败、修订版本与证据对应 | 定向 CI + 全课程现有 CI，人工 review.py 闭环 |

## 已发现并修订（源码层）

| 位置 | 问题 | 修订与复查要求 |
| --- | --- | --- |
| cover / final-practice-release | 首末页视觉语法与 D019/D020 不一致 | 局部样式继承相同配色与结构，真实渲染待检查 |
| open-discussion / timetable-impact / traffic | 开放讨论线索较泛，缺少明确观察对象 | 独立观察—自愿交流—证据追问；构造时间轴，不虚构实际课表 |
| research-connection | 学生页面混入后台教师指令 | 学生可见具体研究问题与证据；教师提醒置于默认折叠注记 |
| not-start-code / information / abstraction / define-task | 输入语义不连续、关系与操作混列、完整性条件不够明确 | 同一座位主例；区分对象、属性、关系、操作；同一时刻完整唯一记录 |
| multiple-tasks | 最短时间任务缺少固定非负权条件 | 补充模型条件，不把最少边数与最小权混同 |
| practice-a/b/c | B 的图示布局与 A/C 不对等 | 三题同结构，不在课堂给正式数据答案 |
| assignment A/B/C | A 未写单日不重叠等假设；B 原始 0→5 目标与边数缺失；C 同时到达编号语义不明确 | 补全原设计条件与明确输出，不增加任务范围 |
| reference A/C | C11 qsort 标准不保证 O(n log n)；字符串比较 R10 与 R2 错序；C 结果数组固定容量 | 直接插入排序，说明最坏复杂度；按数值编号比较，逐行输出，新增同到达时间边界 |
| practice-process / final-practice-release | 过程与任务入口层级较弱 | 六步视觉路径、在线可读主源优先、仓库内链接保留 |

## 验证边界

基线 CI 的 D020 专项日志（run 46156081778）已确认 D020 源测试 29 项通过、全课程作业检查 21 讲通过；D020 存在投影溢出。更早 main run 46137291629 已记录 D017、D020 溢出及旧课件历史布局问题。这些不是 D021 新增问题，不改写原始失败。当前环境无法直接克隆 GitHub，实际正式构建、C 编译执行、浏览器状态及截图审阅以本轮 CI 结果为准；在取得对应版本证据前不宣布通过。定向 CI 通过也不替代全课程检查、教师审阅或真实课堂反馈。

正式验收命令：

```sh
python3 tools/deck/build.py D021
git diff --exit-code -- course/decks/d021-campus-computing-practice/index.html course/decks/d021-campus-computing-practice/README.md
python3 -m unittest discover -s course/decks/d021-campus-computing-practice/tests -v
python3 tools/deck/check_homework.py
python3 tools/deck/check.py D021 --screenshots all --output /tmp/d021-quality
python3 tools/deck/verify.py --base origin/main --output /tmp/d021-full-review
```

最后一项需按实际基线 SHA 调整。完成真实视觉自审后使用现有 review.py 记录，未完成不得填写通过。无受限校园素材及学生记录入库。期末任务发布时间、提交方式和总评权重不擅自修改。
