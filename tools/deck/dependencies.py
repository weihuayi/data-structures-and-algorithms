"""Conservative local dependency fingerprints; no code is rewritten."""
import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from build import ROOT, render_document


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'img', 'source', 'video', 'audio', 'iframe', 'link'}:
            for key in ('src', 'href', 'poster'):
                if attrs.get(key):
                    self.urls.append(attrs[key])


def local_resource(base, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (base / unquote(parsed.path)).resolve()


def python_imports(path, deck, root):
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except (OSError, SyntaxError, UnicodeError):
        return []
    result = []
    for node in ast.walk(tree):
        modules = []
        level = 0
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            modules = ([module] if module else []) + [
                '.'.join(x for x in (module, alias.name) if x)
                for alias in node.names if alias.name != '*']
            level = node.level
        for module in modules:
            bases = [path.parent, deck, root / 'tools/deck', root]
            if level:
                bases = [path.parents[level - 1]]
            for base in bases:
                target = base.joinpath(*module.split('.'))
                candidates = [target.with_suffix('.py'), target / '__init__.py'] if module else []
                match = next((p.resolve() for p in candidates if p.is_file()), None)
                if match is not None:
                    result.append(match)
                    for prefix in range(1, len(module.split('.'))):
                        init = base.joinpath(*module.split('.')[:prefix]) / '__init__.py'
                        if init.is_file():
                            result.append(init.resolve())
                    break
    return result


def dependency_manifest(deck, *, document=None, extra=(), root=ROOT):
    """Static local imports + HTML/CSS resources + code + explicit extra files.

    Dynamic or data dependencies not discoverable from these forms must be
    declared as repository-relative DEPENDENCIES in slides.py. Runtime network
    resources remain the browser checker's responsibility.
    """
    root, deck = root.resolve(), deck.resolve()
    if document is None:
        document, _ = render_document(deck)
    parser = Resources(); parser.feed(document)
    queue = [deck / 'slides.py', Path(__file__).with_name('build.py')]
    queue += [p for url in parser.urls if (p := local_resource(deck, url)) is not None]
    queue += [(root / p).resolve() for p in extra]
    queue += [p for p in (deck / 'code').rglob('*') if p.is_file()] if (deck / 'code').exists() else []
    files, missing, outside, seen = {}, [], [], set()
    while queue:
        path = queue.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        try:
            key = path.relative_to(root).as_posix()
        except ValueError:
            outside.append(str(path))
            continue
        if not path.is_file():
            missing.append(key)
            continue
        data = path.read_bytes()
        files[key] = hashlib.sha256(data).hexdigest()
        if path.suffix == '.py':
            queue.extend(python_imports(path, deck, root))
        if path.suffix == '.css':
            text = data.decode('utf-8')
            urls = re.findall(r'''url\(\s*['"]?([^)'"\s]+)''', text)
            urls += re.findall(r'''@import\s+['"]([^'"]+)''', text)
            queue.extend(p for url in urls if (p := local_resource(path.parent, url)) is not None)
    files = dict(sorted(files.items()))
    return dict(sha256=hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
                files=files, missing=sorted(missing), outside=sorted(outside),
                scope='Static local Python imports, local HTML/CSS resources, lesson code and declared DEPENDENCIES')
