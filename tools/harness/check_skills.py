#!/usr/bin/env python3
"""Deterministic repository Skill structure and local-link checks (read-only)."""

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")


def local_targets(path, root, errors):
    """Resolve simple Markdown inline links, ignoring external URLs and fragments.

    This intentionally checks path integrity, not whether a cited source supports
    a claim or whether fragment anchors exist.
    """
    links = set()
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"unreadable Markdown: {path.relative_to(root)}: {exc}")
        return links
    for match in MARKDOWN_LINK.finditer(content):
        parts = match.group(1).strip().split()
        if not parts:
            errors.append(f"empty local link: {path.relative_to(root)}")
            continue
        raw = parts[0].strip("<>")
        uri = urlsplit(raw)
        if uri.scheme or uri.netloc or not uri.path:
            continue
        try:
            candidate = (path.parent / unquote(uri.path)).resolve(strict=True)
        except (OSError, RuntimeError):
            errors.append(f"broken local link: {path.relative_to(root)} -> {raw}")
            continue
        if not candidate.is_relative_to(root):
            errors.append(f"out-of-repository link: {path.relative_to(root)} -> {raw}")
            continue
        links.add(candidate)
    return links


def skill_metadata(path, slug, errors):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        errors.append(f"unreadable Skill: {slug}: {exc}")
        return
    if not lines or lines[0] != "---":
        errors.append(f"missing YAML frontmatter: {slug}")
        return
    try:
        close = lines.index("---", 1)
    except ValueError:
        errors.append(f"unclosed YAML frontmatter: {slug}")
        return
    metadata = {}
    for line in lines[1:close]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-zA-Z][\w-]*):\s*(.+)", line)
        if not match:
            errors.append(f"unsupported frontmatter field: {slug}: {line}")
            continue
        key, value = match.groups()
        if key in metadata:
            errors.append(f"duplicate frontmatter field: {slug}: {key}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        metadata[key] = value
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not SLUG.fullmatch(name) or len(name) > 64 or name != slug:
        errors.append(f"invalid Skill name/directory: {slug}: {name!r}")
    if not description or description in ("|", ">", "|-", ">-") or len(description) > 1024:
        errors.append(f"invalid Skill description: {slug}")


def check_repository(root):
    root = Path(root).resolve(strict=True)
    errors = []
    skill_root = root / "skills"
    adapter_root = root / ".agents" / "skills"
    case_root = root / "kb" / "design_cases"
    required = [root / "AGENTS.md", skill_root / "README.md",
                root / "kb" / "README.md", case_root / "README.md"]
    for file in required:
        if not file.is_file():
            errors.append(f"missing entry: {file.relative_to(root)}")
    if not skill_root.is_dir():
        errors.append("missing skills directory")
        return errors
    skill_dirs = sorted(p for p in skill_root.iterdir() if p.is_dir() and not p.is_symlink())
    if not skill_dirs:
        errors.append("no skills in skills/")
    if not adapter_root.is_dir():
        errors.append("missing .agents/skills discovery directory")
    index_targets = local_targets(skill_root / "README.md", root, errors) if (skill_root / "README.md").is_file() else set()
    for directory in skill_dirs:
        slug = directory.name
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md: {slug}")
            continue
        skill_metadata(skill_file, slug, errors)
        if skill_file.resolve() not in index_targets:
            errors.append(f"unindexed Skill: {slug}")
        local_targets(skill_file, root, errors)
        alias = adapter_root / slug
        if not alias.is_symlink():
            errors.append(f"missing or non-symlink discovery adapter: {slug}")
            continue
        target_text = alias.readlink()
        if target_text.is_absolute():
            errors.append(f"absolute discovery link (not portable): {slug}")
        try:
            target = alias.resolve(strict=True)
        except (OSError, RuntimeError):
            errors.append(f"broken or cyclic discovery adapter: {slug}")
            continue
        if not target.is_relative_to(root) or target != directory.resolve():
            errors.append(f"wrong or escaping discovery target: {slug}")
    if adapter_root.is_dir():
        known = {p.name for p in skill_dirs}
        for alias in sorted(adapter_root.iterdir()):
            if alias.name not in known:
                errors.append(f"orphan discovery adapter: {alias.name}")
    for file in required:
        if file.is_file() and file != skill_root / "README.md":
            local_targets(file, root, errors)
    if case_root.is_dir() and (case_root / "README.md").is_file():
        cases = {p.resolve() for p in case_root.glob("*.md") if p.name != "README.md"}
        indexed = local_targets(case_root / "README.md", root, [])
        for case in sorted(cases - indexed):
            errors.append(f"unindexed design case: {case.name}")
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root (default: script's repository)")
    args = parser.parse_args()
    try:
        errors = check_repository(args.root)
    except (OSError, RuntimeError) as exc:
        print(f"skill-check: failed to inspect repository: {exc}")
        return 2
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"skill-check: FAIL ({len(errors)} issue(s))")
        return 1
    print("skill-check: PASS (metadata, discovery links, indices, local references)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
