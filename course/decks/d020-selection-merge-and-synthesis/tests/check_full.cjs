/* Full D020 Chromium smoke test on controlled, generated index.html.
 * All pages: default projection layout; key interactions: step and answer flow.
 */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const modulePath=process.env.DECK_PLAYWRIGHT_MODULE||
 path.resolve(__dirname,"../../../../tools/deck/node_modules/playwright");
const {chromium}=require(modulePath);
const html=path.resolve(__dirname,"../index.html");
const ids=[
 "cover","outline","part-selection","sort-contract-recall",
 "simple-selection","tournament-bridge","heap-opportunity","heap-contract",
 "heap-array","heap-vs-bst","sift-down","sift-counterexample","build-heap",
 "heap-independent","heapsort-boundary","heap-checkpoint","part-merge",
 "merge-opportunity","merge-trace","stable-merge-independent","merge-invariant",
 "merge-recursion","merge-cost","part-radix","radix-opportunity","radix-buckets",
 "radix-linked-trace","radix-independent","radix-stability","part-choice",
 "comparison-model","choice-independent","mechanism-synthesis","homework-bridge"
];
(async()=>{
 assert(fs.existsSync(html),"Build derived index.html before the browser check");
 const browser=await chromium.launch({headless:true,
  executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined,
  args:["--allow-file-access-from-files"]});
 try{
  for(const [width,height] of [[1280,720],[1440,900],[2048,1107]]){
   const page=await browser.newPage({viewport:{width,height}});
   const jsErrors=[];
   page.on("pageerror",e=>jsErrors.push(e.message));
   await page.goto("file://"+html,{waitUntil:"load"});
   await page.waitForSelector('[data-page-id="homework-bridge"]',{state:"attached"});
   assert.equal(await page.locator("main .slide").count(),34);
   assert.deepEqual(await page.locator("main .slide").evaluateAll(
     all=>all.map(x=>x.dataset.pageId)),ids);
   assert.equal(await page.locator(".slide[data-role=section]").count(),4);
   const failures=[];
   for(const id of ids){
    await page.evaluate(pid=>{
      for(const s of document.querySelectorAll("main .slide"))
       s.classList.toggle("active",s.dataset.pageId===pid);
    },id);
    const geom=await page.evaluate(()=>{
      const m=document.querySelector("main");
      const s=document.querySelector("main .slide.active");
      return {mw:m.clientWidth,sw:m.scrollWidth,mh:m.clientHeight,sh:m.scrollHeight,
        slidew:s.clientWidth,scrollw:s.scrollWidth,slideh:s.clientHeight,scrollh:s.scrollHeight};
    });
    if(geom.sw>geom.mw+2||geom.scrollw>geom.slidew+2)
     failures.push(id+" horizontal "+JSON.stringify(geom));
    if(geom.sh>geom.mh+3||geom.scrollh>geom.slideh+3)
     failures.push(id+" default vertical "+JSON.stringify(geom));
    if(await page.locator('.slide.active .course-answer[open]').count())
     failures.push(id+" leaked answer by default");
   }
   await page.evaluate(()=>document.querySelectorAll("main .slide").forEach(s=>
     s.classList.toggle("active",s.dataset.pageId==="stable-merge-independent")));
   const task=page.locator('[data-page-id="stable-merge-independent"]');
   assert.equal(await task.locator('[data-task-input]').count(),1);
   const inputBefore=await task.locator('[data-task-input]').innerText();
   await task.locator(".course-answer summary").click();
   assert.equal(await task.locator(".course-answer").getAttribute("open"),"");
   assert.equal(await task.locator('[data-task-input]').innerText(),inputBefore);
   assert.match(await task.locator(".course-solution").innerText(),/甲/);
   await page.evaluate(()=>document.querySelectorAll("main .slide").forEach(s=>
     s.classList.toggle("active",s.dataset.pageId==="build-heap")));
   const player=page.locator("#build-heap-viewer");
   const expected=["5,3,8,2,7,1,6","5,3,8,2,7,1,6","5,7,8,2,3,1,6","8,7,6,2,3,1,5"];
   for(let i=0;i<expected.length;i++){
     const panel=player.locator(".tree-step-panel:not([hidden])");
     assert.equal(await panel.getAttribute("data-heap-state"),expected[i]);
     assert.equal(await panel.locator(".d20-node-key").allTextContents().then(a=>a.join(",")),expected[i]);
     assert.equal(await panel.locator(".d20-cell strong").allTextContents().then(a=>a.join(",")),expected[i]);
     const geom=await page.evaluate(()=>{const m=document.querySelector("main");return [m.scrollWidth-m.clientWidth,m.scrollHeight-m.clientHeight]});
     if(geom[0]>2||geom[1]>3)failures.push("build-heap step "+i+" overflow "+geom);
     if(i+1<expected.length)await page.locator("#build-heap-next").click();
   }
   assert.equal(await page.locator("#build-heap-next").isDisabled(),true);
   await page.locator("#build-heap-prev").click();
   assert.equal(await player.locator(".tree-step-panel:not([hidden])").getAttribute("data-heap-state"),expected[2]);
   await page.locator("#build-heap-reset").click();
   assert.equal(await player.locator(".tree-step-panel:not([hidden])").getAttribute("data-heap-state"),expected[0]);
   assert.equal(await page.locator("#build-heap-prev").isDisabled(),true);
   await page.evaluate(()=>document.querySelectorAll("main .slide").forEach(s=>
     s.classList.toggle("active",s.dataset.pageId==="merge-trace")));
   assert.match(await page.locator("#merge-stage").innerText(),/步骤 1/);
   await page.locator("#merge-next").click();
   assert.match(await page.locator("#merge-stage").innerText(),/步骤 2/);
   await page.locator("#merge-reset").click();
   assert.match(await page.locator("#merge-stage").innerText(),/步骤 1/);
   await page.evaluate(()=>document.querySelectorAll("main .slide").forEach(s=>
     s.classList.toggle("active",s.dataset.pageId==="radix-linked-trace")));
   assert.equal(await page.locator("#merge-viewer > .tree-step-panel").count(),7);
   assert.equal(await page.locator("#radix-viewer > .tree-step-panel").count(),12);
   assert.equal(await page.locator("#radix-viewer > .tree-step-panel:not([hidden]) .d20-bucket").count(),10);
   await page.locator("#radix-next").click();
   assert.match(await page.locator("#radix-stage").innerText(),/步骤 2/);
   await page.locator("#radix-reset").click();
   await page.evaluate(()=>document.querySelectorAll("main .slide").forEach(s=>
     s.classList.toggle("active",s.dataset.pageId==="heap-independent")));
   await page.locator('[data-page-id="heap-independent"] .course-answer summary').click();
   const openGeom=await page.evaluate(()=>{
     const m=document.querySelector("main");
     return {cw:m.clientWidth,sw:m.scrollWidth};
   });
   if(openGeom.sw>openGeom.cw+2)failures.push("heap-independent expanded horizontal");
   assert.deepEqual(jsErrors,[],"Page JavaScript errors");
   if(process.env.D020_SCREENSHOT_DIR){
     const folder=path.resolve(process.env.D020_SCREENSHOT_DIR);fs.mkdirSync(folder,{recursive:true});
     for(const pid of ["heap-contract","stable-merge-independent","radix-linked-trace","homework-bridge"]){
       await page.evaluate(x=>document.querySelectorAll("main .slide").forEach(s=>
         s.classList.toggle("active",s.dataset.pageId===x)),pid);
       await page.screenshot({path:path.join(folder,"d020-"+pid+"-"+width+"x"+height+".png")});
     }
   }
   assert.deepEqual(failures,[],failures.join("\n"));
   console.log("PASS full D020 Chromium "+width+"x"+height+
     " 34 pages, no default overflow, step controls, answer context");
   await page.close();
  }
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
