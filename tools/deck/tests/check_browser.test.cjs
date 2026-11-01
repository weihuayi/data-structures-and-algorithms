/* Requires an existing Playwright/Chromium installation, like check.py. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {run, headerKey} = require('../check-browser.cjs');
const root = path.resolve(__dirname, '..');
const asset = name => pathToFileURL(path.join(root, name)).href;
function fixture(body, after = '') {
  return `<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="${asset('deck.css')}">
  <body class="deck"><header><select id="slide-select"></select><button id="read">Read</button></header>
  <main><section class="slide"><div class="slide-inner"><h2>Fixture</h2>${body}</div></section></main>
  <footer><button id="prev">Prev</button><span id="page"></span><button id="next">Next</button><div id="progress"></div></footer>
  <script src="${asset('deck.js')}"></script>${after}</body>`;
}
const player = `<div class="tree-player" data-tree-player><div class="toolbar"><button data-step="prev">Back</button><button data-step="next">Forward</button><button data-step="reset">Reset</button><span class="tree-step"></span></div><div class="tree-step-panel">One</div><div class="tree-step-panel" hidden>Two</div><div class="tree-step-panel" hidden>Three</div></div>`;
const task = `<link rel="stylesheet" href="${asset('components.css')}"><div class="course-workspace" data-course-component="task-workspace"><div data-task-input>Required input</div><div class="course-task"><div class="course-prompt" data-task-prompt>Predict</div><details class="course-answer" data-task-answer><summary>Answer</summary><div>Result</div></details></div></div>`;
const outline = `<ol class="course-outline" data-course-component="outline"><li data-section-id="one"><span class="course-outline-number">01</span><div class="course-outline-topic"><strong>主题</strong><p>核心问题？</p></div><span class="course-outline-pages">2–3 页</span></li></ol>`;
test('header comparison preserves symbols, punctuation and word boundaries', () => {
  assert.equal(headerKey('第１节 · 任务'),headerKey('第1节：任务'));
  for(const [a,b] of [['x-y','xy'],['a/b','ab'],['ℝ','R'],['A B','AB'],['选择（条件一）','选择条件一']])
    assert.notEqual(headerKey(a),headerKey(b));
});
test('browser checker distinguishes good pages, failures and uncovered interactions', async () => {
  const output = fs.mkdtempSync(path.join(os.tmpdir(), 'deck-check-test-'));
  try {
    const cases = [
      ['good', fixture(player + '<details><summary>Answer</summary><p>Result</p></details><details class="teacher-note"><summary>Note</summary><p>Explanation</p></details><code>\\(literal\\)</code>'), 'pass', null],
      ['overflow', fixture('<div style="height:1500px">Tall</div>'), 'fail', 'projection-layout'],
      ['math', fixture('<p>\\(x+1\\)</p>'), 'fail', 'math-rendering'],
      ['button', fixture(player, `<script>document.querySelector('[data-step="next"]').onclick=e=>e.stopPropagation();</script>`), 'fail', 'step-state'],
      ['combination', fixture('<div class="columns"><details><summary>A</summary><p>A</p></details><details><summary>B</summary><p>B</p></details></div>'), 'pass', null],
      ['unknown', fixture('<button>New component</button>'), 'incomplete', 'interaction-coverage'],
      ['resource', fixture('<img src="missing-image.png">'), 'fail', 'runtime-and-resources'],
      ['task', fixture(`<link rel="stylesheet" href="${asset('components.css')}">${task}`), 'pass', null],
      ['hidden-prompt', fixture(`${task}<style>.course-workspace:has(details[open]) [data-task-prompt]{display:none}</style>`), 'fail', 'task-prompt-visible'],
      ['hidden-condition', fixture(task.replace('Required input', '<p>Input</p><p data-required-context="condition">Nonnegative weights</p>')+'<style>.course-workspace:has(details[open]) [data-required-context]{display:none}</style>'), 'fail', 'review-context-visible'],
      ['hidden-code', fixture(task.replace('Required input', '<pre data-required-context="code">dist[v] = candidate;</pre>')+'<style>.course-workspace:has(details[open]) pre{display:none}</style>'), 'fail', 'review-context-visible'],
      ['clipped-context', fixture(task.replace('Required input', '<div style="height:15px;overflow:hidden"><p data-required-context="condition">Required condition</p></div>')), 'fail', 'review-context-reachable'],
      ['covered-context', fixture(task.replace('Required input', '<div style="position:relative"><p data-required-context="condition">Required condition</p><div style="position:absolute;inset:0;background:white;z-index:2"></div></div>')), 'fail', 'review-context-reachable'],
      ['review-scroll', fixture(task.replace('<div>Result</div>', '<div>'+Array.from({length:14},(_,i)=>`<p>Reason ${i+1}</p>`).join('')+'</div>')), 'pass', null],
      ['anonymous-scroll', fixture('<details><summary>Unclassified</summary><div style="height:1500px">Tall</div></details>'), 'fail', 'projection-layout'],
      ['closed-task-overflow', fixture(task.replace('Required input', '<div style="height:1500px">Tall</div>')), 'fail', 'projection-layout'],
      ['unrelated-open-overflow', fixture(task+'<div class="unrelated">Other content</div><style>.slide:has(details[open]) .unrelated{height:1500px}</style>'), 'fail', 'review-scroll-boundary'],
      ['horizontal-review', fixture(task.replace('<div>Result</div>', '<div style="width:3000px">Too wide</div>')), 'fail', 'projection-layout'],
      ['horizontal-code-scroll', fixture(task.replace('Required input', '<pre style="max-width:200px">'+('code '.repeat(100))+'</pre>')), 'fail', 'review-context-reachable'],
      ['legacy-prompt', fixture('<div class="answer-workspace"><p data-required-context="input">Graph</p><div><div class="answer-prompt">Original question</div><details><summary>Check</summary><p>Reason</p></details></div></div>'), 'pass', null],
      ['safe-replacement', fixture('<div class="tree-swap"><p data-required-context="question">Compare the same input.</p><div class="tree-preview" data-review-replaceable="The full process retains this input">Compact process</div><details><summary>Full process</summary><p>Same input and complete process</p></details></div>'), 'pass', null],
      ['empty-replacement', fixture('<div class="tree-swap"><div class="tree-preview" data-review-replaceable="">Question</div><details><summary>Full process</summary><p>Result</p></details></div>'), 'fail', 'review-replacement-declaration'],
      ['required-replacement', fixture('<div class="tree-swap"><div class="tree-preview" data-review-replaceable="Wrong exemption"><p data-required-context="question">Question</p></div><details><summary>Full process</summary><p>Result</p></details></div>'), 'fail', 'review-replacement-declaration'],
      ['outline', fixture(`<link rel="stylesheet" href="${asset('components.css')}">${outline}`), 'pass', null],
      ['outline-drift', fixture(outline.replace('>01</span>', '>02</span>')), 'fail', 'outline-navigation'],
      ['outline-hidden-topic', fixture(outline+'<style>.course-outline-topic{display:none}</style>'), 'fail', 'outline-fields-visible'],
      ['hidden-input', fixture(`<link rel="stylesheet" href="${asset('components.css')}">${task}<style>.course-workspace:has(details[open]) [data-task-input]{display:none}</style>`), 'fail', 'task-input-visible'],
      ['missing-cjk-glyphs', fixture('<p>数据结构</p>', '<script>HTMLCanvasElement.prototype.toDataURL=()=>"same-tofu";</script>'), 'fail', 'cjk-glyphs'],
      ['header-copy', fixture('<p>Input</p>').replace('<h2>Fixture</h2>', '<p class="kicker">第一部分 · 任务</p><h2>第一部分：任务</h2>'), 'fail', 'header-redundancy'],
      ['hidden-section-kicker', fixture('<p>Input</p>').replace('class="slide"', 'class="slide" data-role="section"').replace('<h2>Fixture</h2>', '<p class="kicker" style="display:none">Context</p><h2>Fixture</h2>'), 'fail', 'heading-structure'],
      ['distinct-header', fixture('<p>Input</p>').replace('<h2>Fixture</h2>', '<p class="kicker">第二部分 · 最短路径</p><h2>怎样更新最短距离？</h2>'), 'pass', null],
      ['runtime-header-copy', fixture('<p>Input</p>', '<script>document.querySelector(".slide-inner").insertAdjacentHTML("afterbegin",\'<p class="kicker">Fixture</p>\');</script>'), 'fail', 'header-redundancy'],
    ];
    for (const [id, html, status, check] of cases) {
      const file = path.join(output, id + '.html'); fs.writeFileSync(file, html);
      const result = await run({decks: [{id, url: pathToFileURL(file).href, slides: 1}], viewports: [[1280,720]], output, screenshots: 'none', playwrightModule: process.env.DECK_PLAYWRIGHT_MODULE, executablePath: process.env.DECK_BROWSER_EXECUTABLE});
      assert.equal(result.status, status, `${id}: ${JSON.stringify(result)}`);
      if (check) assert.ok(result.checks.some(c => c.check === check && c.status !== 'pass' && c.page === (check === 'cjk-glyphs' ? 0 : 1)), id);
    }
    const file = path.join(output, 'defaults.html'); fs.writeFileSync(file, fixture('<button>Unadapted interaction</button>'));
    const defaults = await run({decks:[{id:'defaults',url:pathToFileURL(file).href,slides:1}],viewports:[[1280,720]],output,screenshots:'none',scope:'default-pages',playwrightModule:process.env.DECK_PLAYWRIGHT_MODULE,executablePath:process.env.DECK_BROWSER_EXECUTABLE});
    assert.equal(defaults.status, 'pass');
    assert.equal(defaults.scope, 'default-pages');
    assert.ok(!defaults.checks.some(c => c.check === 'step-state' || c.check === 'interaction-coverage' || c.check === 'reading-mode'));
    const legacy = path.join(output, 'legacy-review.html');
    fs.writeFileSync(legacy, fixture('<button>Outside targeted scope</button><div class="tree-layout"><div class="tree-swap"><div class="tree-preview" data-review-replaceable="The complete process retains the compact input">Compact input</div><details><summary>Full process</summary>'+player+'</details></div><div class="tree-explain"><p data-required-context="question">Original question</p><div class="tree-swap"><div class="tree-preview">Comparison task</div><details><summary>Check</summary><p>Reason</p></details></div></div></div>'));
    const review = await run({decks:[{id:'legacy-review',url:pathToFileURL(legacy).href,slides:1}],viewports:[[1280,720]],output,screenshots:'none',scope:'review-context',playwrightModule:process.env.DECK_PLAYWRIGHT_MODULE,executablePath:process.env.DECK_BROWSER_EXECUTABLE});
    assert.equal(review.status, 'pass');
    assert.equal(review.scope, 'review-context');
    assert.ok(review.checks.some(c => c.check === 'review-context-reachable' && c.state.startsWith('disclosure-')));
    assert.ok(!review.checks.some(c => ['step-state','interaction-coverage','reading-mode'].includes(c.check)));
    const emptyReview = await run({decks:[{id:'no-review',url:pathToFileURL(file).href,slides:1}],viewports:[[1280,720]],output,screenshots:'none',scope:'review-context',playwrightModule:process.env.DECK_PLAYWRIGHT_MODULE,executablePath:process.env.DECK_BROWSER_EXECUTABLE});
    assert.equal(emptyReview.status,'fail');
    assert.ok(emptyReview.checks.some(c => c.check === 'review-workspace-coverage' && c.status === 'fail'));
  } finally { fs.rmSync(output, {recursive:true, force:true}); }
});
