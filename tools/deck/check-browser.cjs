/* Browser checks for repository Decks. Does not build or install dependencies. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

async function run(config) {
  const report = {status: 'pending', scope: config.scope || 'full', node: process.version, checks: []};
  let browser;
  try {
    const {chromium} = require(config.playwrightModule || 'playwright');
    browser = await chromium.launch({headless: true, ...(config.executablePath ? {executablePath: config.executablePath} : {})});
    report.browserVersion = browser.version();
  } catch (error) {
    return {...report, status: 'unavailable', error: String(error)};
  }
  let serial = 0;
  try {
    for (const deck of config.decks) for (const [width, height] of config.viewports) {
      const context = await browser.newContext({viewport: {width, height}});
      const page = await context.newPage();
      page.setDefaultTimeout(5000);
      let location = {deck: deck.id, viewport: `${width}x${height}`, page: 0, state: 'load'};
      const add = (check, ok, detail) => report.checks.push({...location, check, status: ok ? 'pass' : 'fail', detail});
      const errors = [];
      page.on('pageerror', e => errors.push(String(e)));
      page.on('requestfailed', r => errors.push(`${r.url()}: ${r.failure()?.errorText}`));
      await page.route(/^https?:/, route => route.abort());
      async function capture(failed, initial = false) {
        const mode = config.screenshots || 'failures';
        if (mode === 'none' || !(failed || mode === 'all' || (mode === 'pages' && initial))) return;
        const name = `${deck.id}-${width}x${height}-p${location.page}-${++serial}.png`.replace(/[^a-zA-Z0-9_.-]/g, '_');
        await page.screenshot({path: path.join(config.output, name)});
        report.checks[report.checks.length - 1].screenshot = name;
      }
      async function layout(allowVertical = false, initial = false) {
        const size = await page.locator('main').evaluate(el => ({x: el.scrollWidth - el.clientWidth, y: el.scrollHeight - el.clientHeight}));
        const ok = size.x <= 3 && (allowVertical || size.y <= 3);
        add('projection-layout', ok, `overflow x=${size.x}, y=${size.y}${allowVertical ? '; teacher-note vertical scroll allowed' : ''}`);
        await capture(!ok, initial);
      }
      async function taskInputs(slide) {
        const tasks = slide.locator('[data-course-component="task-workspace"]');
        for (let t = 0; t < await tasks.count(); t++) {
          const task = tasks.nth(t), input = task.locator(':scope > [data-task-input]');
          add('task-input-visible', await input.count() === 1 && await input.isVisible(),
              `task ${t + 1}: required input remains visible`);
        }
      }
      try {
        await page.goto(deck.url, {waitUntil: 'load'});
        await page.evaluate(() => document.fonts.ready);
        const glyphs = await page.evaluate(() => {
          if (!/[\u4e00-\u9fff]/.test(document.body.innerText)) return null;
          const canvas = document.createElement('canvas'); canvas.width = 96; canvas.height = 64;
          const context = canvas.getContext('2d');
          const family = getComputedStyle(document.body).fontFamily;
          context.font = '32px ' + family;
          const images = [...'数据结构'].map(char => {
            context.clearRect(0, 0, 96, 64); context.fillText(char, 8, 48); return canvas.toDataURL();
          });
          return {family, distinct: new Set(images).size};
        });
        if (glyphs) add('cjk-glyphs', glyphs.distinct >= 3,
                       `Chinese glyph probe: ${glyphs.distinct} distinct glyphs; ${glyphs.family}; install a CJK font if tofu is shown`);
        const slides = page.locator('.slide');
        const count = await slides.count();
        add('slide-count', count > 0 && (!deck.slides || deck.slides === count), `${count} slides`);
        for (let i = 0; i < count; i++) {
          location = {...location, page: i + 1, state: 'initial'};
          await page.locator('#slide-select').selectOption(String(i));
          const slide = slides.nth(i);
          location.title = await slide.locator('h1,h2').first().innerText();
          location.pageId = await slide.getAttribute('data-page-id');
          location.role = await slide.getAttribute('data-role');
          location.pageFingerprint = crypto.createHash('sha256').update(await slide.evaluate(el => el.outerHTML)).digest('hex');
          const math = await slide.evaluate(el => {
            const raw = [];
            const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
              const n = walker.currentNode;
              if (!n.parentElement.closest('.katex,pre,code,svg,script,style,option') && /\\[([]/.test(n.textContent)) raw.push(n.textContent.trim().slice(0, 100));
            }
            return {errors: el.querySelectorAll('.katex-error').length, raw};
          });
          add('math-rendering', !math.errors && !math.raw.length, JSON.stringify(math));
          add('disclosures-initially-closed', await slide.locator('details[open]').count() === 0, 'Answers and notes start collapsed');
          await layout(false, true);
          await taskInputs(slide);
          if (config.scope === 'default-pages') continue;
          const unsupported = await slide.evaluate(el => [...el.querySelectorAll('button,select,input,[data-pair],[data-map],[data-maze],[data-mem],[data-link],[data-stack],[data-queue],[data-recur],[data-hanoi],[data-match]')].filter(n => !n.closest('[data-tree-player]')).map(n => n.tagName + ':' + [...n.attributes].filter(a => a.name.startsWith('data-')).map(a => a.name).join(',')));
          if (unsupported.length) report.checks.push({...location, check: 'interaction-coverage', status: 'uncovered', detail: [...new Set(unsupported)].join(', ')});
          const players = slide.locator('[data-tree-player]');
          for (let p = 0; p < await players.count(); p++) {
            const player = players.nth(p);
            const panels = player.locator(':scope > .tree-step-panel');
            const total = await panels.count();
            if (!await player.isVisible()) {
              report.checks.push({...location, check: 'step-coverage', status: 'uncovered', detail: `Player ${p + 1} hidden behind disclosure`});
              continue;
            }
            if (!total || total > 500) {
              report.checks.push({...location, check: 'step-coverage', status: 'uncovered', detail: `Player ${p + 1}: unsupported state count ${total}`});
              continue;
            }
            const prev = player.locator('[data-step="prev"]'), next = player.locator('[data-step="next"]'), reset = player.locator('[data-step="reset"]');
            async function state(expected) {
              const visible = await panels.evaluateAll(ns => ns.flatMap((n, k) => !n.hidden && getComputedStyle(n).display !== 'none' ? [k] : []));
              add('step-state', visible.length === 1 && visible[0] === expected && await prev.isDisabled() === (expected === 0) && await next.isDisabled() === (expected === total - 1), `player ${p + 1}: expected ${expected}, visible ${visible}`);
              await layout();
            }
            for (let n = 0; n < total; n++) {
              location.state = `player-${p + 1}/step-${n + 1}`;
              await state(n);
              if (n < total - 1) await next.click();
            }
            if (total > 1) {
              location.state = `player-${p + 1}/back-forward`;
              await prev.click(); await state(total - 2);
              await next.click(); await state(total - 1);
            }
            location.state = `player-${p + 1}/reset`;
            await reset.click(); await state(0);
          }
          const disclosures = slide.locator('details');
          for (let d = 0; d < await disclosures.count(); d++) {
            const detail = disclosures.nth(d), summary = detail.locator(':scope > summary');
            location.state = `disclosure-${d + 1}`;
            if (!await summary.isVisible()) {
              report.checks.push({...location, check: 'disclosure-coverage', status: 'uncovered', detail: 'Nested/hidden disclosure requires manual verification'});
              continue;
            }
            await summary.click();
            add('disclosure-open', await detail.getAttribute('open') !== null, await summary.innerText());
            await taskInputs(slide);
            const teacher = await detail.evaluate(el => el.classList.contains('teacher-note'));
            const taskAnswer = await detail.getAttribute('data-task-answer') !== null;
            if (taskAnswer) {
              const prompt = detail.locator('..').locator(':scope > [data-task-prompt]');
              add('task-answer-replaces-prompt', !await prompt.isVisible(), 'Answer replaces the prompt while input stays in place');
            }
            await layout(teacher);
            const name = await detail.getAttribute('name');
            if (name) add('disclosure-exclusive', await slide.locator('details[open]').evaluateAll((ns, name) => ns.filter(n => n.getAttribute('name') === name).length, name) === 1, name);
            if (teacher || taskAnswer) {
              await page.emulateMedia({media: 'print'});
              add(teacher ? 'teacher-note-print' : 'task-answer-print', await detail.evaluate(el => [...el.children].filter(n => n.tagName !== 'SUMMARY').every(n => getComputedStyle(n).display === 'none')), 'Disclosure content remains hidden in print');
              if (taskAnswer) {
                const prompt = detail.locator('..').locator(':scope > [data-task-prompt]');
                add('task-prompt-print', await prompt.isVisible(), 'Question is restored in print even if the answer was opened');
                await taskInputs(slide);
              }
              await page.emulateMedia({media: 'screen'});
            }
            await summary.click();
            add('disclosure-close', await detail.getAttribute('open') === null, 'Closed after inspection');
          }
          const learner = slide.locator('details:not(.teacher-note)');
          const groups = await learner.evaluateAll(ns => [...new Set(ns.map(n => n.getAttribute('name')).filter(Boolean))]);
          for (const group of groups) {
            location.state = `exclusive-group/${group}`;
            const members = learner.filter({has: page.locator('summary')});
            for (let d = 0; d < await members.count(); d++) {
              const detail = members.nth(d);
              if (await detail.getAttribute('name') !== group) continue;
              const summary = detail.locator(':scope > summary');
              if (!await summary.isVisible()) continue;
              await summary.click();
              add('disclosure-exclusive-transition', await learner.evaluateAll((ns, g) => ns.filter(n => n.open && n.getAttribute('name') === g).length, group) === 1, group);
              await layout();
            }
            for (let d = 0; d < await learner.count(); d++) {
              const detail = learner.nth(d);
              if (await detail.getAttribute('open') !== null) await detail.locator(':scope > summary').click();
            }
          }
          const independent = await learner.evaluateAll(ns => ns.filter(n => !n.getAttribute('name')).length + new Set(ns.map(n => n.getAttribute('name')).filter(Boolean)).size);
          if (independent > 1 && groups.length === 0 && independent <= 6) {
            for (let mask = 1; mask < (1 << independent); mask++) {
              location.state = `disclosure-combination/${mask}`;
              let reachable = true;
              for (let d = 0; d < await learner.count(); d++) {
                const detail = learner.nth(d), summary = detail.locator(':scope > summary');
                const wanted = Boolean(mask & (1 << d));
                if ((await detail.getAttribute('open') !== null) !== wanted) {
                  if (!await summary.isVisible()) { reachable = false; break; }
                  await summary.click();
                }
              }
              if (reachable) await layout();
              else report.checks.push({...location, check: 'disclosure-coverage', status: 'uncovered', detail: 'Combination not reachable via visible summaries'});
            }
            for (let d = 0; d < await learner.count(); d++) {
              const detail = learner.nth(d);
              if (await detail.getAttribute('open') !== null && await detail.locator(':scope > summary').isVisible()) await detail.locator(':scope > summary').click();
            }
          } else if (independent > 1) report.checks.push({...location, state: 'disclosure-combinations', check: 'disclosure-coverage', status: 'uncovered', detail: 'More than six independent disclosures or mixed named groups require manual verification'});
        }
        if (config.scope !== 'default-pages') {
        location.state = 'reading';
        await page.locator('#read').click();
        add('reading-mode', await slides.evaluateAll(ns => ns.every(n => getComputedStyle(n).display !== 'none')), 'All slides displayed');
        await page.locator('#read').click();
        await page.emulateMedia({media: 'print'});
        location.state = 'print';
        add('hidden-steps-print', await page.locator('.tree-step-panel[hidden]').evaluateAll(ns => ns.every(n => getComputedStyle(n).display === 'none')), 'Hidden snapshots remain hidden in print');
        await page.emulateMedia({media: 'screen'});
        }
        location.state = 'resources';
        add('runtime-and-resources', errors.length === 0, errors.join('\n') || 'No failed resources or JavaScript errors; external network blocked');
      } catch (error) {
        add('browser-execution', false, String(error));
        await capture(true).catch(() => {});
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
  report.status = report.checks.some(c => c.status === 'fail') ? 'fail' : report.checks.some(c => c.status === 'uncovered') ? 'incomplete' : 'pass';
  return report;
}
module.exports = {run};
if (require.main === module) {
  const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  run(config).catch(error => ({status: 'unavailable', error: String(error)})).then(report => {
    fs.writeFileSync(path.join(config.output, 'browser-report.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(report.status);
    process.exitCode = report.status === 'pass' ? 0 : report.status === 'fail' ? 1 : 2;
  });
}
