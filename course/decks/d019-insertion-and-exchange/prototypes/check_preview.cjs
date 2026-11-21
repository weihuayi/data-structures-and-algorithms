/* Headless Chromium review of the subset, using the repository's shared deck renderer. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const modulePath=process.env.DECK_PLAYWRIGHT_MODULE||path.resolve(__dirname,'../../../../tools/deck/node_modules/playwright');
const {chromium}=require(modulePath);
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8')
 .replace(/<link rel="stylesheet" href="([^"]+)">/g,(_,url)=>`<style>${fs.readFileSync(path.resolve(__dirname,url),'utf8')}</style>`)
 .replace(/<script src="([^"]+)"><\/script>/g,(_,url)=>`<script>${fs.readFileSync(path.resolve(__dirname,url),'utf8')}</script>`);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined,args:['--allow-file-access-from-files']});
 try{
 for(const [width,height] of [[1280,720],[1440,900],[2048,1107]]){
   const page=await browser.newPage({viewport:{width,height}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.setContent(html,{waitUntil:'load'});
   await page.waitForSelector('#ins-array .d019-slot');
   assert.equal(await page.locator('.slide').count(),3);
   assert.equal(await page.locator('#ins-array .d019-slot').count(),5);
   assert.equal(await page.locator('#ins-stage').innerText().then(x=>x.includes('1/5')),true);
   for(let i=0;i<2;i++)await page.click('#ins-next');
   assert.match(await page.locator('#ins-array').innerText(),/□/);
   await page.click('#ins-reset');
   assert.match(await page.locator('#ins-stage').innerText(),/1\/5/);
   await page.click('#next');
   const details=page.locator('[data-page-id="partition-independent"] .course-answer');
   assert.equal(await details.getAttribute('open'),null);
   await page.locator('#d019-student-input').fill('我先尝试解释枢轴就位');
   await details.locator('summary').click();
   assert.equal(await details.getAttribute('open'),'');
   assert.match(await page.locator('#partition-output').innerText(),/5/);
   assert.match(await page.locator('#partition-input').innerText(),/9/);
   assert.equal(await page.locator('#d019-student-input').inputValue(),'我先尝试解释枢轴就位');
   await details.locator('summary').click();
   assert.equal(await details.getAttribute('open'),null);
   await page.click('#next');
   assert.match(await page.locator('.slide.active').innerText(),/已处理前缀有序/);
   for(const slide of await page.locator('.slide').all()){
     const id=await slide.getAttribute('data-page-id');
     await page.evaluate(id=>{const s=document.querySelector(`[data-page-id="${id}"]`);document.querySelectorAll('.slide').forEach(e=>e.classList.toggle('active',e===s))},id);
     const dimensions=await page.evaluate(()=>({w:document.querySelector('main').scrollWidth,cw:document.querySelector('main').clientWidth,h:document.querySelector('main').scrollHeight,ch:document.querySelector('main').clientHeight}));
     assert(dimensions.w<=dimensions.cw+1,`horizontal overflow: ${id} @ ${width}x${height}`);
     assert(dimensions.h<=dimensions.ch+1,`default vertical overflow: ${id} @ ${width}x${height}`);
   }
   assert.deepEqual(errors,[]);console.log(`PASS browser ${width}x${height}`);await page.close();
 }
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exit(1)});