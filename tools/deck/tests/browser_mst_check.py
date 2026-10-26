#!/usr/bin/env python3
"""Headless Chrome check for D013 Prim/Kruskal players. Not unittest-discovered."""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DECK = ROOT / 'course/decks/d013-mst-and-union-find'
INDEX = DECK / 'index.html'
CHROME = next((shutil.which(x) for x in ('google-chrome', 'chromium', 'chromium-browser')
               if shutil.which(x)), None)

SCRIPT = r'''
<script>
window.addEventListener("load", () => {
  function read(panels, label) {
    const active = panels.findIndex(p => !p.hidden);
    const p = panels[active];
    return {step: label.textContent, active,
      action: (p.querySelector('.trace-action') || {}).textContent || '',
      marked: p.querySelectorAll('.graph-edge.marked').length,
      candidate: p.querySelectorAll('.graph-edge.candidate').length,
      rejected: p.querySelectorAll('.graph-edge.rejected').length};
  }
  const out = {};
  for (const slide of [12, 18]) {
    const root = document.querySelector('#slide-' + slide + ' [data-tree-player]');
    const panels = [...root.querySelectorAll(':scope > .tree-step-panel')];
    const next = root.querySelector('[data-step="next"]');
    const prev = root.querySelector('[data-step="prev"]');
    const reset = root.querySelector('[data-step="reset"]');
    const label = root.querySelector('.tree-step');
    const steps = [read(panels, label)];
    const initialPrev = prev.disabled, initialNext = next.disabled;
    for (let i = 1; i < panels.length; i++) { next.click(); steps.push(read(panels, label)); }
    const endPrev = prev.disabled, endNext = next.disabled;
    prev.click();
    const afterPrev = read(panels, label);
    reset.click();
    out[slide] = {panels: panels.length, initialPrev, initialNext, endPrev, endNext,
                  steps, afterPrev, afterReset: read(panels, label)};
  }
  const pre = document.createElement('pre');
  pre.id = 'browser-check'; pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
</script>'''


def main():
    if not CHROME:
        raise SystemExit('Chrome/Chromium not found; browser check not executed')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        harness = DECK / f'.browser-mst-check-{os.getpid()}.html'
        try:
            harness.write_text(INDEX.read_text(encoding='utf-8').replace('</body>', SCRIPT + '</body>'),
                               encoding='utf-8')
            proc = subprocess.run(
                [CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                 f'--user-data-dir={td / "chrome"}', '--window-size=1280,720',
                 '--virtual-time-budget=5000', '--dump-dom', harness.as_uri() + '#slide-12'],
                capture_output=True, text=True, timeout=60)
            if proc.returncode:
                raise SystemExit(f'Chrome failed: {proc.returncode}\n{proc.stderr[-1000:]}')
            m = re.search(r'<pre id="browser-check">(.*?)</pre>', proc.stdout, re.S)
            if not m:
                raise SystemExit('browser harness did not produce #browser-check')
            data = json.loads(m.group(1))
        finally:
            harness.unlink(missing_ok=True)

    for slide, count in (('12', 9), ('18', 16)):
        result = data[slide]
        assert result['panels'] == count, (slide, result['panels'])
        assert [x['active'] for x in result['steps']] == list(range(count)), slide
        assert result['initialPrev'] and not result['initialNext'], slide
        assert not result['endPrev'] and result['endNext'], slide
        assert result['afterPrev']['active'] == count - 2, (slide, result['afterPrev'])
        assert result['afterReset']['active'] == 0, slide
        assert all(x['step'] == f'步骤 {i + 1} / {count}' for i, x in enumerate(result['steps'])), slide
    assert '总权 12' in data['12']['steps'][-1]['action']
    assert '总权 12' in data['18']['steps'][-1]['action']
    assert data['18']['steps'][7]['candidate'] == 1  # AC candidate in pre-decision state
    assert data['18']['steps'][8]['rejected'] == 1  # AC rejected
    print('browser-mst-check: PASS')
    print('Prim 9 states; Kruskal 16 states; prev/next/reset/boundary OK')
    print('Kruskal AC candidate/reject classes OK')


if __name__ == '__main__':
    main()
