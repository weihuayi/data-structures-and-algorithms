/* Full-deck, D019-specific all-page + custom-interaction regression. */
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../../../');
const dir=path.resolve(__dirname,'..');
const modulePath=process.env.DECK_PLAYWRIGHT_MODULE||path.join(root,'tools/deck/node_modules/playwright');
const {chromium}=require(modulePath);
const source=fs.readFileSync(path.join(dir,'index.html'),'utf8');
function embed(html){
 return html.replace(/<link rel="stylesheet" href="([^"]+)">/g,(_,f)=>`<style>${fs.readFileSync(path.resolve(dir,f),'utf8')}</style>`)
 .replace(/<script(?: defer)? src="([^"]+)"><\/script>/g,(_,f)=>`<script>${fs.readFileSync(path.resolve(dir,f),'utf8')}</script>`);
}
const html=embed(source);
const viewportSet=[[1280,720],[1440,900],[2048,1107]];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined});
 try{
  for(const [width,height] of viewportSet){
   const page=await browser.newPage({viewport:{width,height}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.setContent(html,{waitUntil:'load'});
   const total=34; assert.equal(await page.locator('.slide').count(),total);
   for(let i=0;i<total;i++){
    await page.selectOption('#slide-select',String(i));
    const o=await page.evaluate(()=>{let m=document.querySelector('main'),s=document.querySelector('.slide.active');return{id:s.dataset.pageId,w:m.scrollWidth,cw:m.clientWidth,h:m.scrollHeight,ch:m.clientHeight}});
    assert(o.w<=o.cw+2,`horizontal overflow ${o.id} ${width}x${height}`);
    assert(o.h<=o.ch+2,`vertical default overflow ${o.id} ${width}x${height}`);
    assert.equal(await page.locator('.slide.active').count(),1);
   }
   for(const pid of ['stability-task','insertion-independent','bubble-stop-task','partition-independent','cost-diagnosis']){
    await page.selectOption('#slide-select',String(await page.locator('.slide').evaluateAll((nodes,target)=>nodes.findIndex(n=>n.dataset.pageId===target),pid)));
    const card=page.locator(`[data-page-id="${pid}"]`);
    const a=card.locator('details.course-answer');
    assert.equal(await a.getAttribute('open'),null,`answer prematurely open ${pid}`);
    const input=card.locator('[data-task-input]');
    const prompt=card.locator('[data-task-prompt]');
    assert(await input.isVisible()&&await prompt.isVisible());
    if(pid==='partition-independent') await card.locator('#d19-student-answer').fill('我先预测，后核对');
    await a.locator('summary').click();
    assert.equal(await a.getAttribute('open'),'');
    assert(await input.isVisible()&&await prompt.isVisible());
    if(pid==='partition-independent')assert.equal(await card.locator('#d19-student-answer').inputValue(),'我先预测，后核对');
    const dims=await page.evaluate(()=>{let m=document.querySelector('main');return[m.scrollWidth,m.clientWidth]});
    assert(dims[0]<=dims[1]+2,`expanded horizontal overflow ${pid}`);
    await a.locator('summary').click();
   }
   await page.selectOption('#slide-select',String(await page.locator('.slide').evaluateAll(nodes=>nodes.findIndex(n=>n.dataset.pageId==='insertion-trace')));
   for(let i=0;i<4;i++)await page.click('#ins-next');
   assert.match(await page.locator('#ins-stage').innerText(),/5\/5/);
   assert.equal((await page.locator('#ins-array strong').allInnerTexts()).join(','),'2,5,6,7,8');
   await page.click('#ins-reset');assert.match(await page.locator('#ins-stage').innerText(),/1\/5/);
   await page.selectOption('#slide-select',String(await page.locator('.slide').evaluateAll(nodes=>nodes.findIndex(n=>n.dataset.pageId==='partition-trace')));
   for(let i=0;i<5;i++)await page.click('#quick-next');
   assert.equal((await page.locator('#quick-array strong').allInnerTexts()).join(','),'1,3,2,4,8,6,7');
   await page.click('#quick-reset');
   assert.equal(await page.locator('#quick-array strong').first().innerText(),'□');
   assert.deepEqual(errors,[]);
   await page.close();
   console.log(`PASS D019 browser: ${width}x${height}; 34 default pages, 5 tasks, both custom players`);
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});