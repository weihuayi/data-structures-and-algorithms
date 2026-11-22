"""Build a three-page prototype with the *repository* build renderer.

No permanent slides.py: the shim exists only inside this script's try/finally.
Run from anywhere: python3 course/decks/d019-insertion-and-exchange/prototypes/build_preview.py
"""
from pathlib import Path
import sys

here=Path(__file__).resolve().parent
root=here.parents[3]
sys.path.insert(0,str(root/'tools'/'deck'))
from build import render_document

shim=here/'slides.py'
if shim.exists():
    raise RuntimeError('Refusing to overwrite slides.py: prototype must not create a formal Deck')
try:
    shim.write_text('from preview_source import *\n',encoding='utf-8')
    document,count=render_document(here)
finally:
    shim.unlink(missing_ok=True)
assert count==3
# Append isolated assets after the shared renderer's official CSS/JS references.
document=document.replace('</head>','<link rel="stylesheet" href="preview.css"></head>',1)
document=document.replace('</body>','<script src="trace.js"></script><script src="preview.js"></script></body>',1)
(here/'index.html').write_text(document,encoding='utf-8')
print(f'Built isolated D019 prototype using CourseDeck + shared renderer: {count} pages')