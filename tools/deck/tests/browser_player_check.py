#!/usr/bin/env python3
"""Headless Chrome check for the three D012 graph players.

This is not part of unittest discovery because it needs a browser.  Run:
    python3 tools/deck/tests/browser_player_check.py
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / 'course/decks/d012-graph-traversal/index.html'
CHROME = next((shutil.which(x) for x in ('google-chrome', 'chromium', 'chromium-browser')
               if shutil.which(x)), None)

SCRIPT = r'''
<script>
window.addEventListener("load", () => {
  function read(panels, label) {
    const active = panels.findIndex(p => !p.hidden);
    const p = panels[active];
    const g = p.querySelector('.graph-node-current');
    const e = p.querySelector('.graph-node-examined');
    return {step: label.textContent, active,
      current: g ? g.getAttribute('data-vertex') : null,
      examined: e ? e.getAttribute('data-vertex') : null,
      action: (p.querySelector('.trace-action') || {}).textContent || '',
      queue: (p.querySelector('.trace-state') || {}).textContent || ''};
  }
  const out = {};
  for (const slide of [12, 14, 17]) {
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


def run():
    if not CHROME:
        raise SystemExit('Chrome/Chromium not found; browser check not executed')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        harness = INDEX.parent / f'.browser-player-check-{os.getpid()}.html'
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

    for slide, result in data.items():
        assert result['panels'] == 15, (slide, result['panels'])
        assert [x['active'] for x in result['steps']] == list(range(15)), (slide, [x['active'] for x in result['steps']])
        assert result['initialPrev'] and not result['initialNext'], slide
        assert not result['endPrev'] and result['endNext'], slide
        assert result['afterPrev']['active'] == 13, (slide, result['afterPrev'])
        assert result['afterReset']['active'] == 0, slide
        assert all(x['step'] == f'步骤 {i + 1} / 15' for i, x in enumerate(result['steps'])), slide

    s5, s6 = data['17']['steps'][4], data['17']['steps'][5]
    assert (s5['current'], s5['examined']) == ('A', 'C'), s5
    assert 'B C' in s5['queue'], s5
    assert (s6['current'], s6['examined']) == ('B', None), s6
    assert 'C' in s6['queue'], s6
    print('browser-player-check: PASS')
    print('slides 12/14/17: 15 states, next/prev/reset/boundary OK')
    print('BFS step 5=', s5['current'], s5['examined'], s5['queue'], '| step 6=',
          s6['current'], s6['examined'], s6['queue'])


if __name__ == '__main__':
    run()
