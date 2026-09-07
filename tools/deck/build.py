from pathlib import Path
import argparse
import html
import importlib.util
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
DECKS = ROOT / "course" / "decks"
CSS_REL = "../../../tools/deck/deck.css"
JS_REL = "../../../tools/deck/deck.js"


def load_deck(deck_dir: Path):
    spec = importlib.util.spec_from_file_location(f"deck_{deck_dir.name}", deck_dir / "slides.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Deck source: {deck_dir / 'slides.py'}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render(deck_dir: Path):
    mod = load_deck(deck_dir)
    blocks = []
    for i, (name, body, part) in enumerate(mod.SLIDES, 1):
        blocks.append(
            f'<section class="slide" id="slide-{i}" data-title="{html.escape(name, quote=True)}">'
            f'<div class="slide-inner"><p class="kicker">{html.escape(part)}</p><h2>{name}</h2>{body}'
            f'</div></section>'
        )
    nav = (
        f'<header><span class="brand">数据结构与算法 · {html.escape(mod.DECK_ID)}</span>'
        '<nav aria-label="课件工具"><select id="slide-select" aria-label="跳转页面"></select>'
        '<button id="read">连续阅读</button></nav></header>'
    )
    foot = (
        '<footer><span>← → 翻页 · 菜单跳页 · F11 可全屏</span>'
        '<div><button id="prev">上一页</button> <span id="page" aria-live="polite"></span> '
        '<button id="next">下一页</button></div><div id="progress" class="progress"></div></footer>'
    )
    doc = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{html.escape(mod.DECK_ID)}｜{html.escape(mod.TITLE)}</title>'
        f'<link rel="stylesheet" href="{CSS_REL}"></head>'
        f'<body class="deck">{nav}<noscript>请启用浏览器 JavaScript 以使用翻页与演示功能。</noscript>'
        f'<main>{"".join(blocks)}</main>{foot}<script src="{JS_REL}"></script></body></html>'
    )
    (deck_dir / "index.html").write_text(doc, encoding="utf-8")
    return len(mod.SLIDES)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("deck", nargs="*", help="D001 / d001-problem-representation / all")
    args = parser.parse_args()

    dirs = [p for p in DECKS.iterdir() if p.is_dir() and (p / "slides.py").exists()]
    wanted = args.deck or ["all"]
    if "all" not in [x.lower() for x in wanted]:
        keys = {x.lower() for x in wanted}
        dirs = [p for p in dirs if p.name.lower() in keys or p.name.split("-", 1)[0].lower() in keys]
    if not dirs:
        raise SystemExit("No matching Deck.")

    for deck_dir in sorted(dirs):
        count = render(deck_dir)
        print(f"Built {deck_dir.name}: {count} slides -> {deck_dir / 'index.html'}")


if __name__ == "__main__":
    main()
