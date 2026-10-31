from pathlib import Path
import argparse
import html
import importlib.util
import os
import sys
from headers import render_header

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
DECKS = ROOT / "course" / "decks"
EXAMPLES = Path(__file__).resolve().parent / 'examples'
PLAN_START = '<!-- page-plan:start -->'
PLAN_END = '<!-- page-plan:end -->'


def load_deck(deck_dir: Path):
    spec = importlib.util.spec_from_file_location(f"deck_{deck_dir.name}", deck_dir / "slides.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Deck source: {deck_dir / 'slides.py'}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render_document(deck_dir: Path):
    """Return the controlled derivative without changing the working tree."""
    mod = load_deck(deck_dir)
    assets = Path(os.path.relpath(ROOT / 'tools' / 'deck', deck_dir)).as_posix()
    blocks = []
    course = getattr(mod, 'COURSE', None)
    for i, (name, body, part) in enumerate(mod.SLIDES, 1):
        metadata = ''
        role = None
        if course is not None and i <= len(course.pages):
            page = course.pages[i - 1]
            role = page['role']
            metadata = ''.join(f' data-{key}="{html.escape(str(value), quote=True)}"'
                               for key, value in (('page-id', page['id']), ('role', page['role']),
                                                  ('section-id', page['section'])) if value is not None)
        blocks.append(
            f'<section class="slide" id="slide-{i}" data-title="{html.escape(name, quote=True)}"{metadata}>'
            f'<div class="slide-inner">{render_header(name, part, role=role)}{body}'
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
    math_assets = ''
    if getattr(mod, "MATH", False):
        math_assets = (
            f'<link rel="stylesheet" href="{assets}/vendor/katex/katex.min.css">'
            f'<script defer src="{assets}/vendor/katex/katex.min.js"></script>'
            f'<script defer src="{assets}/vendor/katex/contrib/auto-render.min.js"></script>'
            f'<script defer src="{assets}/math.js"></script>'
        )
    component_assets = f'<link rel="stylesheet" href="{assets}/components.css">' if course is not None else ''
    doc = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{html.escape(mod.DECK_ID)}｜{html.escape(mod.TITLE)}</title>'
        f'{math_assets}<link rel="stylesheet" href="{assets}/deck.css">'
        f'{component_assets}</head>'
        f'<body class="deck">{nav}<noscript>请启用浏览器 JavaScript 以使用翻页与演示功能。</noscript>'
        f'<main>{"".join(blocks)}</main>{foot}<script src="{assets}/deck.js"></script></body></html>'
    )
    return doc, len(mod.SLIDES)


def render(deck_dir: Path):
    doc, count = render_document(deck_dir)
    (deck_dir / "index.html").write_text(doc, encoding="utf-8")
    readme = deck_dir / 'README.md'
    if readme.exists() and PLAN_START in readme.read_text(encoding='utf-8'):
        text = readme.read_text(encoding='utf-8')
        if text.count(PLAN_START) != 1 or text.count(PLAN_END) != 1:
            raise ValueError('Design-card page-plan markers must occur exactly once')
        course = load_deck(deck_dir).COURSE
        before, rest = text.split(PLAN_START)
        _, after = rest.split(PLAN_END)
        readme.write_text(before + PLAN_START + '\n' + course.page_plan_markdown() + '\n' + PLAN_END + after,
                          encoding='utf-8')
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("deck", nargs="*", help="D001 / d001-problem-representation / all")
    args = parser.parse_args()

    dirs = [p for p in DECKS.iterdir() if p.is_dir() and (p / "slides.py").exists()]
    wanted = args.deck or ["all"]
    if "all" not in [x.lower() for x in wanted]:
        keys = {x.lower() for x in wanted}
        dirs += [p for p in EXAMPLES.iterdir() if p.is_dir() and (p / 'slides.py').exists()] if EXAMPLES.exists() else []
        dirs = [p for p in dirs if p.name.lower() in keys or p.name.split("-", 1)[0].lower() in keys]
    if not dirs:
        raise SystemExit("No matching Deck.")

    for deck_dir in sorted(dirs):
        count = render(deck_dir)
        print(f"Built {deck_dir.name}: {count} slides -> {deck_dir / 'index.html'}")


if __name__ == "__main__":
    main()
