# D020｜三页隔离教学原型

> **状态**：基于 D020 R1–R8 的设计验证候选，仅覆盖 Storyboard 的 10–11、18、24–25 页的典型问题，不是完整 D020 Deck、不替代正式 `slides.py`，未被纳入 [课程 Deck 注册表](../../README.md)。

## 一、真实入口与覆盖

直接打开 [index.html](index.html)，或从仓库根目录启动 `python3 -m http.server 8765` 后访问 `/course/decks/d020-selection-merge-and-synthesis/prototypes/index.html`。浏览器需要能加载同目录的 `preview.css`、`trace.js` 和 `preview.js`；没有在线字体、网络或构建器运行时依赖。

三页分别用于验证：
- **堆与局部修复**：真实动态建堆与一次提取轨迹、有效堆前缀和排序后缀分界；根下沉错误反例明确标记为非法。P1 独立输入与完整核对默认折叠。
- **稳定归并**：左右原始记录身份（甲／丙等）始终可见；P2 学生先在文本框写预测；答案默认隐藏，展开后可以逐步核对，原题与作答不消失。
- **链式基数的桶顺序**：0–9 号桶、按数位分配到桶尾和从桶头收集的规则可见；隔离原型给出教材十条输入的三轮验证结果，答案默认折叠；QA 后课堂 P3 改为四条新记录的一轮独立分配／收集。当前隔离原型以 JS 数组明确表示各桶的**链结次序**，并非完整 C11 链式结点实现。

`trace.js` 是无 DOM 的纯计算源；`preview.js` 仅将其状态渲染到 HTML。把状态计算与展示分离，避免用视觉正确替代专业正确性。输入均使用记录 `{key,id}`；有相等关键字时保留 ID。

## 二、运行验证

在仓库根目录：

```bash
node course/decks/d020-selection-merge-and-synthesis/prototypes/test_trace.cjs
# 浏览器检查需要 tools/deck/node_modules/playwright 及其 Chromium：
node course/decks/d020-selection-merge-and-synthesis/prototypes/check_preview.cjs
```

`test_trace.cjs` 覆盖：固定建堆与提取、从根直接下沉的非法反例、960 组确定性生成的堆输入，稳定归并的相等关键字与记录身份，教材十个基数关键字的三轮结果和 140 组确定性生成的基数排序。这个测试范围只支持所检验的状态正确性。

`check_preview.cjs` 在 1280×720、1440×900、2048×1107 下检查页面切换、默认答案折叠、步进／重置、输入保留、学生作答不丢失、桶数及页面脚本异常，并检查横向文档溢出；只报告纵向总高度，不将允许滚动的隔离预览冒称正式投影无溢出。正式 Deck 还须使用 `CourseDeck/Section/task_workspace` 和共享浏览器检查。

## 三、没有覆盖的职责

- 尚未制作 34 页正式 `slides.py`、生成 Deck 完整 `index.html` 或正式 C11 示例。
- 尚未让本原型通过 `tools/deck` 的共享播放器、组件、KaTeX、打印与作业全量验收。
- 尚未获得教师真实投影审阅、真实 90 分钟排练或任何学生达成证据。
- 不修改 D019、D017/D018、共享 CSS/JS 或课程作业制度；原型只用于下一步判断公共组件是否需要局部适配。

详见 [REVIEW.md](REVIEW.md) 的时间模型、未决风险和验证边界。
