#!/usr/bin/env python3
"""Check student-facing homework contract, not instructional quality."""
from html import unescape
from pathlib import Path
import re
import sys

from build import DECKS, ROOT, load_deck

LABEL = re.compile(r"<strong[^>]*>(.*?)</strong>", re.DOTALL)
SOURCE = re.compile(r"code/([A-Za-z0-9_-]+\.c)")


def is_homework_title(title):
    return "课后" in title and any(word in title for word in ("作业", "练习", "教材", "核对"))


def labels(body):
    result = set()
    for match in LABEL.finditer(body):
        plain = unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        if re.match(r"(?:正式作业\s*)?A(?:[.·:：\s　]|$)", plain):
            result.add("A")
        if re.match(r"(?:正式作业\s*)?B(?:[.·:：\s　]|$)", plain):
            result.add("B")
    return result


def check_page(deck, title, body):
    """Check reliable surface invariants; cannot assess task validity."""
    errors = []
    identifier = deck.name.split("-", 1)[0].upper()
    present = labels(body)
    for key in ("A", "B"):
        if key not in present:
            errors.append(f"{identifier}: missing formal {key} assignment label")
    if not re.search(r"选择题|应用题|简述题|算法设计题", body):
        errors.append(f"{identifier}: no concrete textbook exercise type")
    if "过程记录" not in body:
        errors.append(f"{identifier}: no student-facing process record reminder")
    if not any(text in body for text in ("homework-guide.md", "作业规范", "课程作业说明")):
        errors.append(f"{identifier}: no shared homework guide reference")
    if not ("提交" in body or "作业规范" in body):
        errors.append(f"{identifier}: no submission instruction")
    if "如另行布置为正式作业" in body or "不自动成为新正式 Assignment" in body:
        errors.append(f"{identifier}: formal homework demoted to a conditional task")
    if re.search(r"在(?:课程)?仓库(?:中|内)?(?:执行|运行)", body):
        errors.append(f"{identifier}: repository execution incorrectly required")
    for name in sorted(set(SOURCE.findall(body))):
        if not (deck / "code" / name).is_file():
            errors.append(f"{identifier}: missing referenced code/{name}")
    if not SOURCE.search(body):
        errors.append(f"{identifier}: B practice has no identifiable C source")
    if re.search(r"/tmp/d0\d+", body) and not any(s in body for s in ("本地", "个人电脑", "Linux")):
        errors.append(f"{identifier}: /tmp execution without local-environment explanation")
    return errors


def check_all(decks=DECKS):
    errors, count = [], 0
    for deck in sorted(decks.iterdir()):
        if not (deck / "slides.py").is_file():
            continue
        count += 1
        try:
            model = load_deck(deck)
            pages = [(title, body) for title, body, _ in model.SLIDES
                     if is_homework_title(title)]
        except Exception as exc:
            errors.append(f"{deck.name}: cannot load slides: {exc}")
            continue
        if len(pages) != 1:
            errors.append(f"{deck.name}: expected one homework page, got {len(pages)}")
            continue
        errors.extend(check_page(deck, *pages[0]))
    return count, errors


def main():
    count, errors = check_all()
    if errors:
        for error in errors:
            print("FAIL:", error)
        print(f"homework-check: FAIL ({len(errors)} issues in {count} decks)")
        return 1
    print(f"homework-check: PASS ({count} Deck homework pages; structural scope only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
