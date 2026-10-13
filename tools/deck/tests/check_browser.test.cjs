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
    ];
    for (const [id, html, status, check] of cases) {
      const file = path.join(output, id + '.html'); fs.writeFileSync(file, html);
      const result = await run({decks: [{id, url: pathToFileURL(file).href, slides: 1}], viewports: [[1280,720]], output, screenshots: 'none', playwrightModule: process.env.DECK_PLAYWRIGHT_MODULE, executablePath: process.env.DECK_BROWSER_EXECUTABLE});
      assert.equal(result.status, status, `${id}: ${JSON.stringify(result)}`);
      if (check) assert.ok(result.checks.some(c => c.check === check && c.status !== 'pass' && c.page === 1), id);
    }
  } finally { fs.rmSync(output, {recursive:true, force:true}); }
});
