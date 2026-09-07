# Deck Build Tool

本目录承载课程 HTML Deck 的共享构建与交互能力。具体教学内容由各 Deck 的 `slides.py` 维护。

```bash
python3 tools/deck/build.py all
python3 tools/deck/build.py D001
```

`slides.py` 是课件主维护源，`index.html` 是受控派生产物。公开 Deck 不包含教师私有备注。教师运行资料应通过受限或本地工作空间维护，不写入公开 `slides.py` 或 `index.html`。

接入 CI 后，应执行重新构建并检查 Git 工作区无差异，以验证源文件与提交的 HTML 一致。
