# D019｜代表性页面共性组件适配审阅记录

## 审阅范围及状态

- 候选第08页 `insertion-trace`、第23页 `partition-independent`、第29页 `mechanism-map`，对应教师已确认的三个隔离视觉原型。
- 本轮将内容改为通过实际课程 `CourseDeck` / `task_workspace` 和公共构建器生成的隔离预览。没有创建正式 D019 `slides.py`，没有扩展到其余 30 页或修改全课程组件。
- 代码、任务、呈现与课堂效果使用不同证据；**正式共享 CSS/JS 环境的浏览器回归还需要在完整仓库及其依赖中执行**。

## 已执行核验

1. **专业数据**：执行 `node test_trace.cjs`，固定插入样例五状态和快速划分结果完全一致；另外 900 组确定性生成输入的排列保持、枢轴两侧关系、包含重复关键字时的记录身份，以及插入有序前缀检查通过。
2. **构建接口**：隔离预览 `preview_source.py` 按课程组件接口注册三页，独立题通过 `task_workspace` 生成；`build_preview.py` 调用共享 `render_document`，页面使用共享 CSS、JS 链接，并仅追加局部算法状态样式与脚本。
3. **离线浏览器抽查**：本地以真实 Chromium 通过 `page.set_content` 注入页面及其 CSS/JS 文本，在 1280×720、1440×900、2048×1107 检查三页默认态、插入分步、原始输入可见、native `<details>` 先隐藏后展开、答案下标 4、返回收起与导航，无脚本错误。注意：由于本环境限制访问 `file://` 和 `localhost`，这项检查采用**本地构建器及公共 API 的临时兼容镜像 CSS/JS**，并非仓库正式资源的完全等效浏览器证据。

## 需在完整仓库完成的回归

在仓库根目录执行：

```bash
python3 course/decks/d019-insertion-and-exchange/prototypes/build_preview.py
node course/decks/d019-insertion-and-exchange/prototypes/test_trace.cjs
node course/decks/d019-insertion-and-exchange/prototypes/check_preview.cjs
# 检查生成 HTML 是否与版本库一致
 git diff --exit-code -- course/decks/d019-insertion-and-exchange/prototypes/index.html
```

`check_preview.cjs` 使用仓库实际的 `deck.css`、`components.css`、`deck.js` 和三个原型资源，将其直接注入 Chromium DOM；避免本环境对本地 URL 的限制。应检查三个视口的默认页面溢出、原生任务区展开/收起、页面切换、学生预测保持及关键数组状态。须确保 `tools/deck/node_modules/playwright` 已按课程说明安装，或通过 `DECK_PLAYWRIGHT_MODULE` 指定。

## 教师审阅与后续边界

上一版三个视觉原型已得到教师确认。**本轮共享组件适配的实际浏览器显示属于新的工程版本，尚未获得新的教师视觉审阅**；不能以原型初版确认直接替代。

回归、教师审阅以及后续 33 页正式课件实现应分别记录。对原型的任何后续更改应重新核验源码、派生 HTML 以及受影响的交互状态。