"use strict";
/* D018/D019/D020 cover and homework visual regression.
 * Tests rendered hierarchy and geometry; normal page tests cannot prove this.
 */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const root=path.resolve(__dirname,"../../../..");
const {chromium}=require(process.env.DECK_PLAYWRIGHT_MODULE||
 path.join(root,"tools/deck/node_modules/playwright"));
const specs=[
 ["D018","d018-hashing",".hash-r7-cover",".hash-r7-cover-lead",".hash-r7-cover-line",".hash-r7-cover-label",".hash-r7-cover-note",".hash-r8-homework"],
 ["D019","d019-insertion-and-exchange",".d19-cover",".d19-cover-lead",".d19-cover-line",".d19-cover-label",".d19-cover-note",".d19-homework"],
 ["D020","d020-selection-merge-and-synthesis",".d20-cover",".d20-cover-lead",".d20-cover-line",".d20-cover-label",".d20-cover-note",".d20-homework"]
];
const sizes=[[1280,720],[1440,900],[2048,1107]],dir=process.env.D020_EDGE_VISUAL_DIR||"/tmp/d020-edge-visual";
fs.mkdirSync(dir,{recursive:true});
const near=(a,b,tol=1.5)=>Math.abs(a-b)<=tol;
async function snapshot(page,selectors){
 return await page.evaluate((s)=>{
  const slide=document.querySelector("main .slide.active");
  function info(sel){
   const el=slide.querySelector(sel);if(!el)return null;
   const st=getComputedStyle(el),r=el.getBoundingClientRect();
   return {left:r.left,width:r.width,font:parseFloat(st.fontSize),background:st.backgroundColor,
     borderLeft:parseFloat(st.borderLeftWidth),text:el.textContent.trim().slice(0,120)};
  }
  return {id:slide.dataset.pageId,kicker:info(".kicker"),header:info("h2"),
    root:info(s.root),lead:info(s.lead),line:info(s.line),label:info(s.label),
    note:info(s.note),firstText:info(s.root+" p"),code:info(s.root+" pre"),
    minor:info(s.root+" [class$='homework-note']"),
    content:slide.querySelector(s.root)?.innerText.slice(0,1500),
    overflowX:slide.scrollWidth-slide.clientWidth,
    overflowY:slide.scrollHeight-slide.clientHeight};
 },selectors);
}
(async()=>{
 const browser=await chromium.launch({headless:true,
  executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined,
  args:["--allow-file-access-from-files"]});
 const report=[],fail=[];
 try{
  for(const size of sizes){
   const data={};
   for(const [id,slug,cover,lead,line,label,note,homework] of specs){
    const p=await browser.newPage({viewport:{width:size[0],height:size[1]}});
    const f=path.join(root,"course/decks",slug,"index.html");
    assert(fs.existsSync(f),"Missing generated HTML: "+f);
    await p.goto("file://"+f,{waitUntil:"load"});
    await p.evaluate(()=>document.fonts.ready);
    const n=await p.locator("main .slide").count();
    assert.equal(n,34,id+" page count");
    const select=async idx=>{
     await p.selectOption("#slide-select",String(idx));
     await p.waitForFunction(i=>document.querySelectorAll("main .slide")[i]?.classList.contains("active"),idx);
     assert.equal((await p.locator("#page").innerText()).trim(),
       String(idx+1)+" / "+String(n));
    };
    await select(0);
    const c=await snapshot(p,{root:cover,lead,line,label,note});
    await p.screenshot({path:path.join(dir,id.toLowerCase()+"-cover-"+size.join("x")+".png")});
    await select(n-1);
    const h=await snapshot(p,{root:homework,lead,line,label,note});
    await p.screenshot({path:path.join(dir,id.toLowerCase()+"-homework-"+size.join("x")+".png")});
    data[id]={cover:c,homework:h};
    report.push({deck:id,viewport:size.join("x"),cover:c,homework:h});
    await p.close();
   }
   const a=data.D018,b=data.D019,c=data.D020;
   for(const [id,item] of Object.entries(data)){
    const z=item.cover,h=item.homework;
    if(!z.root||!z.lead||!z.line||!z.label||!z.note)
     fail.push(id+" cover missing semantic visual element at "+size);
    if(!z.kicker?.text.includes("课程导入"))
     fail.push(id+" missing course kicker at "+size);
    if(!z.line||z.line.borderLeft<5.8)
     fail.push(id+" missing cover blue route bar at "+size);
    if(!h.firstText||!h.code||!h.minor)
     fail.push(id+" missing homework role at "+size);
    if(!h.content?.includes("A · 教材作业")||!h.content?.includes("B · C11 程序实践"))
     fail.push(id+" homework A/B missing at "+size);
   }
   if(!near(c.cover.lead.font,a.cover.lead.font)||!near(c.cover.lead.font,b.cover.lead.font))
    fail.push("D020 cover question font different from D018/D019 at "+size);
   if(c.cover.line.background!==a.cover.line.background||
      c.cover.line.background!==b.cover.line.background)
    fail.push("D020 cover route background differs at "+size);
   if(!near(c.cover.root.left,b.cover.root.left,12))
    fail.push("D020 cover left position differs from D019 at "+size);
   if(!near(c.homework.root.left,b.homework.root.left,12))
    fail.push("D020 homework left position differs from D019 at "+size);
   if(!near(c.homework.firstText.font,a.homework.firstText.font)||
      !near(c.homework.firstText.font,b.homework.firstText.font))
    fail.push("D020 homework body font differs at "+size);
   if(c.homework.code.background!==a.homework.code.background||
      c.homework.code.background!==b.homework.code.background)
    fail.push("D020 homework code panel color differs at "+size);
   for(const [key,item] of Object.entries({cover:c.cover,homework:c.homework}))
    if(item.overflowX>2||item.overflowY>3)
     fail.push("D020 "+key+" overflow at "+size+": "+item.overflowX+"/"+item.overflowY);
  }
  fs.writeFileSync(path.join(dir,"edge-visual-metrics.json"),JSON.stringify({report,fail},null,2));
  fail.forEach(x=>console.error("EDGE QA: "+x));
  console.log("Edge visual comparator: "+report.length+" comparisons, failures="+fail.length);
  assert.deepEqual(fail,[],"D020 first and last slide consistency");
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1;});
