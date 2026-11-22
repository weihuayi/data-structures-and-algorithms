"use strict";
/* Isolated D020 Chromium review, not full CourseDeck compliance. */
const assert=require("node:assert/strict");
const path=require("node:path");
const fs=require("node:fs");
const browserModule=process.env.DECK_PLAYWRIGHT_MODULE||
  path.resolve(__dirname,"../../../../tools/deck/node_modules/playwright");
const {chromium}=require(browserModule);
const target="file://"+path.resolve(__dirname,"index.html");
const screens=[[1280,720],[1440,900],[2048,1107]];
(async()=>{
  const browser=await chromium.launch({
    headless:true,
    executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined,
    args:["--allow-file-access-from-files"]
  });
  try{
    for(const [width,height] of screens){
      const page=await browser.newPage({viewport:{width,height}});
      const errors=[];
      page.on("pageerror",e=>errors.push(e.message));
      await page.goto(target,{waitUntil:"load"});
      await page.waitForSelector("#heap-array .item");
      assert.equal(await page.locator("#heap-tree svg circle").count(),7,"tree and array must show same active items");
      assert.equal(await page.locator("#heap-tree svg line").count(),6,"tree edges must preserve complete binary shape");
      assert.equal(await page.locator(".lesson").count(),3);
      assert.equal(await page.locator("#heap-panel").isVisible(),true);
      assert.equal(await page.locator("#merge-panel").isVisible(),false);
      assert.equal(await page.locator("#heap-counterexample").getAttribute("open"),null);
      assert.equal(await page.locator("#heap-independent").getAttribute("open"),null);
      const initial=await page.locator("#heap-array").innerText();
      await page.click("#heap-next");
      assert.notEqual(await page.locator("#heap-counter").innerText(),"1 / 1");
      await page.click("#heap-reset");
      assert.equal(await page.locator("#heap-array").innerText(),initial);
      await page.locator("#heap-counterexample summary").click();
      assert.equal(await page.locator("#heap-counterexample").getAttribute("open"),"");
      await page.locator('[data-target="merge-panel"]').click();
      assert.equal(await page.locator("#merge-panel").isVisible(),true);
      assert.equal(await page.locator("#heap-panel").isVisible(),false);
      assert.equal(await page.locator("#merge-answer").getAttribute("open"),null);
      await page.locator("#merge-student").fill("独立预测：相等取左，保证身份稳定");
      await page.locator("#merge-answer summary").click();
      await page.locator("#merge-next").click();
      await page.locator("#merge-next").click();
      assert.match(await page.locator("#merge-output").innerText(),/甲/);
      assert.equal(await page.locator("#merge-student").inputValue(),"独立预测：相等取左，保证身份稳定");
      assert.match(await page.locator("#merge-left").innerText(),/甲/);
      assert.match(await page.locator("#merge-right").innerText(),/丙/);
      await page.locator('[data-target="radix-panel"]').click();
      assert.equal(await page.locator("#radix-panel").isVisible(),true);
      assert.equal(await page.locator("#radix-independent").getAttribute("open"),null);
      assert.equal(await page.locator("#radix-buckets .bucket").count(),10);
      for(let i=0;i<5;i++)await page.click("#radix-next");
      assert.match(await page.locator("#radix-output").innerText(),/21/);
      await page.locator("#radix-independent summary").click();
      assert.match(await page.locator("#radix-independent").innerText(),/331/);
      const layout=await page.evaluate(()=>({
        bodyWidth:document.documentElement.scrollWidth,
        viewportWidth:innerWidth,
        bodyHeight:document.documentElement.scrollHeight,
        viewportHeight:innerHeight
      }));
      assert(layout.bodyWidth<=layout.viewportWidth+1,"horizontal document overflow at "+width+"x"+height);
      assert.deepEqual(errors,[],"JavaScript errors");
      if(process.env.D020_SCREENSHOT_DIR){
        const folder=path.resolve(process.env.D020_SCREENSHOT_DIR);
        fs.mkdirSync(folder,{recursive:true});
        await page.screenshot({path:path.join(folder,"d020-radix-"+width+"x"+height+".png"),fullPage:true});
      }
      console.log("PASS isolated Chromium "+width+"x"+height+
        "; default height="+layout.bodyHeight+" vs viewport="+layout.viewportHeight);
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1);});
