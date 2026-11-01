/* Known review workspaces; no blanket slide-level overflow exemption. */
const AREAS = '[data-course-component="task-workspace"],.answer-workspace,.tree-swap';
const OPEN = '[data-task-answer][open],.answer-workspace details:not(.teacher-note)[open],.tree-swap details:not(.teacher-note)[open]';

// Runs in the browser. Mark exceptional required subunits with
// data-required-context; ordinary semantic blocks are checked automatically.
function inspect(slide, {print = false} = {}) {
  const main = slide.closest('main');
  const roots = [...slide.querySelectorAll(
    '[data-task-input],[data-task-prompt],[data-required-context],.answer-prompt,' +
    '.answer-workspace>figure,.tree-preview:not([data-review-replaceable]),' +
    '.tree-layout:has(>.tree-explain .tree-swap)>:first-child,' +
    '.tree-explain:has(.tree-swap)>p')];
  if (!print) for (const detail of slide.querySelectorAll(
    '[data-task-answer][open],.answer-workspace details:not(.teacher-note)[open],.tree-swap details:not(.teacher-note)[open]'))
    roots.push(...[...detail.children].filter(n => n.tagName !== 'SUMMARY'));
  const units = new Set();
  for (const root of roots) {
    units.add(root);
    for (const n of root.querySelectorAll('p,li,pre,svg,figcaption,th,td,[data-required-context]')) units.add(n);
  }
  const visibleFailures = [], reachFailures = [];
  const positions = new Map();
  const label = n => (n.getAttribute('data-required-context') || n.getAttribute('data-task-input') ||
    n.getAttribute('data-task-prompt') || n.tagName) + ': ' + n.textContent.trim().replace(/\s+/g,' ').slice(0,65);
  function intentional(n) {
    if (n.closest('.katex-mathml')) return true;
    if (n.closest('[data-review-replaceable]') && !n.hasAttribute('data-required-context')) return true;
    if (n.closest('.tree-step-panel[hidden]')) return true; // step adapter owns inactive states
    if (n.closest('.teacher-note') && !n.hasAttribute('data-required-context')) return true;
    for (let a = n.parentElement; a && a !== slide; a = a.parentElement)
      if (a.tagName === 'DETAILS' && (!a.open || print) && !a.querySelector(':scope > summary')?.contains(n))
        return !n.hasAttribute('data-required-context');
    return false;
  }
  function visible(n) {
    const r = n.getBoundingClientRect();
    if (!r.width || !r.height) return false;
    for (let a = n; a && a !== main; a = a.parentElement) {
      const s = getComputedStyle(a);
      if (s.display === 'none' || s.visibility !== 'visible' || Number(s.opacity) === 0) return false;
    }
    return true;
  }
  function clipped(n) {
    const r = n.getBoundingClientRect();
    for (let a = n.parentElement; a && a !== main; a = a.parentElement) {
      const s = getComputedStyle(a), b = a.getBoundingClientRect();
      if (/hidden|clip/.test(s.overflowY) && (r.top < b.top-3 || r.bottom > b.bottom+3)) return true;
      if (/hidden|clip/.test(s.overflowX) && (r.left < b.left-3 || r.right > b.right+3)) return true;
    }
    return false;
  }
  let checked = 0;
  try {
    for (const n of units) {
      if (intentional(n) || (!n.textContent.trim() && !n.querySelector('svg,img') && n.tagName !== 'SVG')) continue;
      checked++;
      if (!visible(n)) { visibleFailures.push(label(n)); continue; }
      if (print) continue;
      if (n.scrollWidth > n.clientWidth+3) { reachFailures.push('horizontal overflow '+label(n)); continue; }
      if (clipped(n)) { reachFailures.push('clipped '+label(n)); continue; }
      if (main.scrollHeight > main.clientHeight+3 && !/auto|scroll/.test(getComputedStyle(main).overflowY)) {
        reachFailures.push('scroll disabled '+label(n)); continue;
      }
      for (let a = n; a && a !== document.body; a = a.parentElement)
        if (!positions.has(a)) positions.set(a,[a.scrollLeft,a.scrollTop]);
      n.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});
      const r = n.getBoundingClientRect(), m = main.getBoundingClientRect();
      const l = Math.max(0,m.left,r.left), t = Math.max(0,m.top,r.top);
      const right = Math.min(innerWidth,m.right,r.right), bottom = Math.min(innerHeight,m.bottom,r.bottom);
      if (right <= l || bottom <= t) { reachFailures.push('unreachable '+label(n)); continue; }
      const hit = document.elementFromPoint((l+right)/2,(t+bottom)/2);
      if (!hit || !(n === hit || n.contains(hit))) reachFailures.push('covered '+label(n));
    }
  } finally {
    for (const [n,[x,y]] of positions) n.scrollTo({left:x,top:y,behavior:'instant'});
  }
  return {checked,visibleFailures,reachFailures};
}

// Ignore position changes caused by the expanded answer pushing later material
// down. Unrelated blocks may not grow merely because an answer is open.
function outsideSizes(slide) {
  const areas = '[data-course-component="task-workspace"],.answer-workspace,.tree-swap,.teacher-note';
  return [...slide.querySelectorAll('div,p,table,figure,pre')].map((n,i) => {
    if (n.closest(areas) || n.querySelector(areas)) return null;
    const r = n.getBoundingClientRect();
    return {id:i,width:r.width,height:r.height};
  }).filter(Boolean);
}

module.exports = {AREAS,OPEN,inspect,outsideSizes};
