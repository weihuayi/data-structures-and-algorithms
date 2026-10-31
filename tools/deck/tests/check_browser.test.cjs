/* Requires an existing Playwright/Chromium installation, like check.py. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {run} = require('../check-browser.cjs');
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
const task = `<div class="course-workspace" data-course-component="task-workspace"><div data-task-input>Required input</div><div class="course-task"><div class="course-prompt" data-task-prompt>Predict</div><details class="course-answer" data-task-answer><summary>Answer</summary><div>Result</div></details></div></div>`;
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
      ['hidden-input', fixture(`<link rel="stylesheet" href="${asset('components.css')}">${task}<style>.course-workspace:has(details[open]) [data-task-input]{display:none}</style>`), 'fail', 'task-input-visible'],
      ['missing-cjk-glyphs', fixture('<p>数据结构</p>', '<script>HTMLCanvasElement.prototype.toDataURL=()=>"same-tofu";</script>'), 'fail', 'cjk-glyphs'],
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
  } finally { fs.rmSync(output, {recursive:true, force:true}); }
});
