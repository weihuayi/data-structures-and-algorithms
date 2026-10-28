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
      text: p.textContent,
      marked: p.querySelectorAll('.graph-edge.marked').length,
      candidate: p.querySelectorAll('.graph-edge.candidate').length,
      rejected: p.querySelectorAll('.graph-edge.rejected').length};
  }
  const out = {};
  for (const [name, labelText] of [["prim", "Prim 最小生成树推演"], ["kruskal", "Kruskal 分组合并推演"]]) {
    const root = document.querySelector(`[data-tree-player][aria-label="${labelText}"]`);
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
    out[name] = {panels: panels.length, initialPrev, initialNext, endPrev, endNext,
                  steps, afterPrev, afterReset: read(panels, label)};
  }
  const select = document.querySelector('#slide-select');
  const slides = [...document.querySelectorAll('.slide')];
  const cover = document.querySelector('#slide-1 .lead');
  out.coverLines = cover.getClientRects().length;
  out.overflow = [];
  for (let i = 0; i < slides.length; i++) {
    select.value = String(i); select.dispatchEvent(new Event('change'));
    const main = document.querySelector('main');
    const gap = main.scrollHeight - main.clientHeight;
    if (gap > 3) out.overflow.push({page: i + 1, gap});
  }
  const pre = document.createElement('pre');
  pre.id = 'browser-check'; pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
});
</script>'''


def main():
    if not CHROME:
        raise SystemExit('Chrome/Chromium not found; browser check not executed')
    results = {}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        harness = DECK / f'.browser-mst-check-{os.getpid()}.html'
        try:
            harness.write_text(INDEX.read_text(encoding='utf-8').replace('</body>', SCRIPT + '</body>'),
                               encoding='utf-8')
            # Chrome's --dump-dom inner height is ~143px smaller than --window-size.
            for size, label in (('1280,863', '1280x720'), ('1440,1043', '1440x900')):
                proc = subprocess.run(
                    [CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                     f'--user-data-dir={td / ("chrome-" + label.replace("x", "-"))}', f'--window-size={size}',
                     '--virtual-time-budget=5000', '--dump-dom', harness.as_uri() + '#slide-1'],
                    capture_output=True, text=True, timeout=60)
                if proc.returncode:
                    raise SystemExit(f'Chrome failed: {proc.returncode}\n{proc.stderr[-1000:]}')
                m = re.search(r'<pre id="browser-check">(.*?)</pre>', proc.stdout, re.S)
                if not m:
                    raise SystemExit('browser harness did not produce #browser-check')
                results[label] = json.loads(m.group(1))
        finally:
            harness.unlink(missing_ok=True)

    for label, data in results.items():
        for slide, count in (('prim', 9), ('kruskal', 16)):
            result = data[slide]
            assert result['panels'] == count, (label, slide, result['panels'])
            assert [x['active'] for x in result['steps']] == list(range(count)), (label, slide)
            assert result['initialPrev'] and not result['initialNext'], (label, slide)
            assert not result['endPrev'] and result['endNext'], (label, slide)
            assert result['afterPrev']['active'] == count - 2, (label, slide, result['afterPrev'])
            assert result['afterReset']['active'] == 0, (label, slide)
            assert all(x['step'] == f'步骤 {i + 1} / {count}' for i, x in enumerate(result['steps'])), (label, slide)
        assert data['coverLines'] == 1, (label, data['coverLines'])
        assert data['overflow'] == [], (label, data['overflow'])
        assert '父指针' not in data['kruskal']['steps'][0]['text'], label
        assert 'DSU' not in data['kruskal']['steps'][0]['text'], label
        assert '已选边集合' in data['prim']['steps'][0]['text'], label
        assert '总权 12' in data['prim']['steps'][-1]['action'], label
        assert '总权 12' in data['kruskal']['steps'][-1]['action'], label
        assert data['kruskal']['steps'][7]['candidate'] == 1, (label, 'AC candidate')
        assert data['kruskal']['steps'][8]['rejected'] == 1, (label, 'AC rejected')
    print('browser-mst-check: PASS')
    print('1280x720, 1440x900: cover single line; 41 pages no vertical overflow')
    print('Prim 9 states; Kruskal 16 states; prev/next/reset/boundary OK')
    print('Kruskal AC candidate/reject classes OK')


if __name__ == '__main__':
    main()
