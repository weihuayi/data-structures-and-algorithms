/* Standalone R4 prototype review, not a check for released D017 slides. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {chromium} = require(path.resolve(__dirname, '../../../../tools/deck/node_modules/playwright'));

const ids = ['recall-sorted', 'bst-check', 'bst-delete-two', 'right-rotate', 'independent-avl'];
const file = path.join(__dirname, 'r4-five-page-review.html');
const out = process.env.D017_R4_SCREENSHOT_DIR || '/tmp/course-verification/d017-r4-preview';
const viewports = [{width: 1280, height: 720}, {width: 1440, height: 900}];
const result = {provenance: 'R4 isolated five-page prototype; not the 37-page released lesson',
                pages: ids, checks: [], failures: []};
const screenshotName = (id,w,h,state) => id + '-' + w + 'x' + h + '-' + state + '.png';
const save = async (page,id,w,h,state) =>
  page.screenshot({path: path.join(out,screenshotName(id,w,h,state))});

async function main(){
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true});
  try{
    for(const v of viewports){
      const page = await browser.newPage({viewport:v,deviceScaleFactor:1});
      for(const id of ids){
        await page.goto(pathToFileURL(file).href + '#' + id);
        await page.locator('section.slide.active[data-page-id="' + id + '"]').waitFor();
        const data = await page.evaluate(() => {
          const main=document.querySelector('.viewport'), current=document.querySelector('section.slide.active');
          const details=current.querySelector('details.feedback');
          const question=current.querySelector('.question');
          const visibleText=[...current.querySelectorAll('svg text')];
          const labels=visibleText.map(x=>{
            const box=x.getBoundingClientRect(); return {value:x.textContent.trim(),height:box.height};
          });
          return {id:current.dataset.pageId,viewport:[innerWidth,innerHeight],
            horizOverflow:main.scrollWidth-main.clientWidth,
            verticalOverflow:main.scrollHeight-main.clientHeight,
            titleSize:parseFloat(getComputedStyle(current.querySelector('h1')).fontSize),
            questionSize:question?parseFloat(getComputedStyle(question).fontSize):null,
            nodeMinHeight:labels.length?Math.min(...labels.map(x=>x.height)):null,
            nodeLabels:labels,
            answerHidden:details?(!details.open && !details.querySelector('.answer').getClientRects().length):null};
        });
        const log={page:id,viewport:v.width+'x'+v.height,state:'default',...data};
        result.checks.push(log);
        assert.ok(data.horizOverflow <= 3, id+' default horizontal overflow '+data.horizOverflow);
        assert.ok(data.titleSize >= 29, id+' heading too small');
        if(data.questionSize!==null)assert.ok(data.questionSize >= 22, id+' question too small');
        assert.ok(data.nodeMinHeight===null||data.nodeMinHeight>=18.2,
                  id+' tree label rendered too small '+data.nodeMinHeight);
        if(id==='right-rotate')assert.equal(data.answerHidden,null);
        else assert.equal(data.answerHidden,true, id+' leaked default answer');
        // With sufficient viewport, don't hide most of the default slide below fold.
        assert.ok(data.verticalOverflow<=120, id+' default excessive vertical scroll '+data.verticalOverflow);
        await save(page,id,v.width,v.height,'default');
        const details=page.locator('section.slide.active details.feedback');
        if(await details.count()){
          await details.locator('summary').click();
          assert.ok(await details.locator('.answer').isVisible(),id+' answer not visible after expansion');
          const opened=await page.evaluate(() => {
            const m=document.querySelector('.viewport');
            return {horizontalOverflow:m.scrollWidth-m.clientWidth, verticalOverflow:m.scrollHeight-m.clientHeight};
          });
          result.checks.push({page:id,viewport:v.width+'x'+v.height,state:'answer-open',...opened});
          assert.ok(opened.horizontalOverflow<=3,id+' expanded answer horizontal overflow '+opened.horizontalOverflow);
          await save(page,id,v.width,v.height,'answer-open');
          await page.locator('.viewport').evaluate(x=>{x.scrollTop=x.scrollHeight});
          await save(page,id,v.width,v.height,'answer-bottom');
        }
      }
      await page.close();
    }
  } finally {await browser.close();}
  fs.writeFileSync(path.join(out,'review-report.json'),JSON.stringify(result,null,2));
  process.stdout.write('D017 R4 prototype browser check: '+result.checks.length+' states / '+(ids.length*2)+' default pages verified; screenshots in '+out+'\n');
}
main().catch(e=>{
  result.failures.push(String(e.stack||e));
  fs.mkdirSync(out,{recursive:true});
  fs.writeFileSync(path.join(out,'review-report.json'),JSON.stringify(result,null,2));
  process.stderr.write(String(e.stack||e)+'\n');process.exitCode=1;
});