# Deck Build Tool

本目录承载课程 HTML Deck 的共享构建与交互能力。具体教学内容由各 Deck 的 `slides.py` 维护。

```bash
python3 tools/deck/build.py all
python3 tools/deck/build.py D001
```

`slides.py` 是课件主维护源，`index.html` 是受控派生产物。公开 Deck 不包含教师私有备注。教师运行资料应通过受限或本地工作空间维护，不写入公开 `slides.py` 或 `index.html`。

## 交互组件

`deck.js` 按 `data-*` 根元素接管页面内的交互演示，样式在 `deck.css`：

- `data-pair="brute|sorted"`：商品配对的分步扫描演示（D002）；
- `data-map` / `data-maze`：网格位置与迷宫寻路演示；
- `data-mem="insert|delete|access|expand|cache"`：连续内存条带演示——顺序表插入/删除搬运、地址直达与逐个扫描对照、扩容整体搬迁、缓存预取对照（D003）。
- `data-link="access|insert|delete"`：链表链式推演——沿 next 走访计数、插入改两个链接（含先改前驱的断链陷阱现场）、删除（含只改链接不 free 的内存泄漏对照）（D004）。
- `data-stack="brackets"`：括号匹配栈轨迹——左括号压栈、右括号弹栈核对，含匹配成功与遍历完栈非空两种对照情形（D005）。
- `data-queue="plain|circ"`：队列推演——顺序队列假满现场；N=5 循环队列 front/rear 轨迹（判满 → 出队 → rear 绕回 → 再次判满）（D005）。

嵌入方式：在 `slides.py` 的 `body_html` 中放置带 `data-*` 属性的根元素，内含 `.toolbar`（情形选择与上一步/下一步/重置）、演示区与 `.status` 状态栏。纯逻辑函数（trace）与 DOM 分离，经 `module.exports` 导出，可用 Node 直接断言。新增交互组件按同一模式加入共享层，不在单个 Deck 内私造。

接入 CI 后，应执行重新构建并检查 Git 工作区无差异，以验证源文件与提交的 HTML 一致。
