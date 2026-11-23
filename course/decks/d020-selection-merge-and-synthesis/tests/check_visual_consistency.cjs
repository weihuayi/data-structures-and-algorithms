"use strict";
/* D020 visual consistency QA with D017/D018 measured in the same browser.
 * Cross-course invariants: shared slide chrome, typography hierarchy, real
 * navigation and answer semantics. Subject-specific figures are NOT pixel-equal.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"../../../..");
const {chromium}=require(process.env.DECK_PLAYWRIGHT_MODULE||
  path.join(root,"tools/deck/node_modules/playwright"));
const target=[
  {id:"D017",name:"d017-bst-avl",expect:37},
  {id:"D018",name:"d018-hashing",expect:34},
  {id:"D020",name:"d020-selection-merge-and-synthesis",expect:34}
];
const viewports=[[1280,720],[1440,900],[2048,1107]];
const output=path.resolve(process.env.D020_VISUAL_DIR||"/tmp/d020-visual-qa");
fs.mkdirSync(output,{recursive:true});
const abs=x=>Math.abs(x);
const num=x=>Number.parseFloat(x)||0;
const cssElement=(root,selector)=>{
  const el=root.querySelector(selector);
  if(!el)return null;
  const st=getComputedStyle(el);
  const rect=el.getBoundingClientRect();
  return {fontPx:num(st.fontSize),lineHeightPx:num(st.lineHeight),
    color:st.color,background:st.backgroundColor,
    width:Math.round(rect.width),height:Math.round(rect.height),
    bottom:Math.round(rect.bottom),top:Math.round(rect.top)};
};
async function metrics(page){
  return page.evaluate(()=>{
    const active=document.querySelector("main .slide.active");
    const main=document.querySelector("main");
    const cs=(selector)=>{
      const el=active.querySelector(selector);if(!el)return null;
      const st=getComputedStyle(el),r=el.getBoundingClientRect();
      return {fontPx:parseFloat(st.fontSize)||0,lineHeightPx:parseFloat(st.lineHeight)||0,
        color:st.color,background:st.backgroundColor,
        width:Math.round(r.width),height:Math.round(r.height),
        top:Math.round(r.top),bottom:Math.round(r.bottom)};
    };
    const first=active.querySelector(".d20-tree .d20-node-index");
    const maxRatio=main.scrollWidth/main.clientWidth;
    return {id:active.dataset.pageId,role:active.dataset.role,
      page:document.querySelector("#page").textContent.trim(),
      nav:document.querySelector("#slide-select").value,
      mainWidth:main.clientWidth,mainScrollWidth:main.scrollWidth,
      mainHeight:main.clientHeight,mainScrollHeight:main.scrollHeight,
      slideWidth:active.clientWidth,slideScrollWidth:active.scrollWidth,
      slideHeight:active.clientHeight,slideScrollHeight:active.scrollHeight,
      h2:cs("h2"),kicker:cs(".kicker"),
      outlineTitle:cs(".course-outline-topic strong"),
      outlineQuestion:cs(".course-outline-topic p"),
      sectionQuestion:cs(".course-section .lead"),
      sectionScope:cs(".course-section .course-section-scope"),
      contentText:cs(".d017 p")||cs(".hash-lesson>p")||cs(".d20-lesson p"),
      prompt:cs(".course-prompt"),
      questionAnswer:cs(".course-answer summary"),
      note:cs(".d17-note")||cs(".hash-note")||cs(".d20-note"),
      arrayIndex:cs(".d17-cell span")||cs(".hash-v2-index")||cs(".d20-cell small"),
      homeworkText:cs(".d20-homework p"),
      homeworkCode:cs(".d20-homework pre"),
      treeIndexPixels:first?Math.round(first.getBoundingClientRect().height*10)/10:null,
      katexErrors:active.querySelectorAll(".katex-error").length,
      openedAnswers:active.querySelectorAll(".course-answer[open]").length};
  });
}
function choose(pageList,deckId){
  const firstRole=role=>pageList.find(x=>x.role===role)?.index;
  const idx=[firstRole("cover"),firstRole("outline"),firstRole("section"),
    firstRole("exercise"),firstRole("closing")];
  if(deckId==="D020"){
    for(const id of ["heap-contract","heap-array","sift-down","heap-independent",
      "stable-merge-independent","radix-linked-trace","radix-independent",
      "comparison-model","homework-bridge"]){
      const item=pageList.find(x=>x.id===id);if(item)idx.push(item.index);
    }
  }
  return [...new Set(idx.filter(Number.isInteger))].sort((a,b)=>a-b);
}
(async()=>{
  const browser=await chromium.launch({headless:true,
    executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined,
    args:["--allow-file-access-from-files"]});
  const results=[],failures=[];
  try{
    for(const [width,height] of viewports){
      for(const d of target){
        const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
        const scriptErrors=[];
        page.on("pageerror",e=>scriptErrors.push(e.message));
        const file=path.join(root,"course/decks",d.name,"index.html");
        assert(fs.existsSync(file),d.id+" missing generated HTML "+file);
        await page.goto("file://"+file,{waitUntil:"load"});
        const items=await page.locator("main .slide").evaluateAll(elems=>elems.map((x,index)=>(
          {id:x.dataset.pageId,role:x.dataset.role,index})));
        assert.equal(items.length,d.expect,d.id+" page count");
        const selected=new Set(choose(items,d.id));
        if(d.id==="D020"&&width===1280)items.forEach(x=>selected.add(x.index));
        for(const idx of [...selected].sort((a,b)=>a-b)){
          // Use actual player navigation; merely toggling .active leaves header/page stale.
          await page.selectOption("#slide-select",String(idx));
          await page.waitForFunction(x=>document.querySelector("main .slide.active")?.dataset.pageId===x,
            items[idx].id);
          const m=await metrics(page);
          if(m.nav!==String(idx)||m.page!==String(idx+1)+" / "+items.length)
            failures.push(d.id+" "+width+"x"+height+" "+m.id+" stale navigation "+m.page);
          if(m.mainScrollWidth>m.mainWidth+2||m.slideScrollWidth>m.slideWidth+2)
            failures.push(d.id+" "+width+"x"+height+" "+m.id+" horizontal overflow");
          // Only D020 is under modification. Existing D017/D018 are comparators, not idealized targets.
          if(d.id==="D020"){
            if(m.mainScrollHeight>m.mainHeight+3||m.slideScrollHeight>m.slideHeight+3)
              failures.push("D020 "+width+"x"+height+" "+m.id+
                " default vertical overflow "+m.mainScrollHeight+"/"+m.mainHeight+
                " slide "+m.slideScrollHeight+"/"+m.slideHeight);
            if(m.openedAnswers)failures.push("D020 "+m.id+" reveals answers by default");
            if(m.katexErrors)failures.push("D020 "+m.id+" has KaTeX errors");
            if(m.arrayIndex&&m.arrayIndex.fontPx<15.9)
              failures.push("D020 "+m.id+" array index below 16px "+m.arrayIndex.fontPx);
            if(m.prompt&&m.prompt.fontPx<23.9)
              failures.push("D020 "+m.id+" task prompt below 24px "+m.prompt.fontPx);
            if(m.id==="heap-contract"&&m.treeIndexPixels!==null&&m.treeIndexPixels<12)
              failures.push("D020 SVG tree index < 12 projected pixels");
            if(m.id==="homework-bridge"){
              if(!m.homeworkText||m.homeworkText.fontPx<22.9)
                failures.push("D020 homework text smaller than 23px");
              if(!m.homeworkCode||m.homeworkCode.fontPx<17.9)
                failures.push("D020 homework code smaller than 18px");
              if(m.homeworkCode?.background==="rgb(24, 56, 80)")
                failures.push("D020 homework code still uses dark visual block");
            }
          }
          results.push({deck:d.id,viewport:width+"x"+height,...m});
          if((width===1280||width===1440)&&
             (d.id==="D020"||selected.has(idx))){
            await page.screenshot({path:path.join(output,
              d.id.toLowerCase()+"-"+String(idx+1).padStart(2,"0")+"-"+m.id+
              "-"+width+"x"+height+".png")});
          }
        }
        if(scriptErrors.length)failures.push(d.id+" JavaScript: "+JSON.stringify(scriptErrors));
        await page.close();
      }
    }
    for(const vp of viewports.map(x=>x.join("x"))){
      const byDeck=Object.fromEntries(target.map(d=>[d.id,results.filter(
        r=>r.deck===d.id&&r.viewport===vp)]));
      for(const field of ["h2","kicker","outlineTitle","sectionQuestion"]){
        const vals=target.map(d=>byDeck[d.id].find(r=>r[field])?.[field]?.fontPx)
          .filter(Number.isFinite);
        if(vals.length===3&&Math.max(...vals)-Math.min(...vals)>2.0)
          failures.push(vp+" shared "+field+" diverges "+JSON.stringify(vals));
      }
      const d17=byDeck.D017.find(r=>r.id==="cover")?.contentText?.fontPx;
      const d20=byDeck.D020.find(r=>r.id==="cover")?.contentText?.fontPx;
      if(Number.isFinite(d17)&&Number.isFinite(d20)&&abs(d17-d20)>2.1)
        failures.push(vp+" D020 body typography not aligned with D017: "+
                      d20+" vs "+d17);
    }
    fs.writeFileSync(path.join(output,"visual-metrics.json"),
      JSON.stringify({baseline:["D017","D018"],candidate:"D020",
        widths:viewports,results,failures},null,2));
    const report=results.map(x=>[
      x.deck,x.viewport,x.id,x.h2?.fontPx||"",
      x.contentText?.fontPx||"",x.prompt?.fontPx||"",
      x.arrayIndex?.fontPx||"",x.mainScrollHeight-x.mainHeight,
      x.slideScrollHeight-x.slideHeight
    ].join("\t"));
    fs.writeFileSync(path.join(output,"visual-metrics.tsv"),
      ["deck\tviewport\tpageId\theadingPx\tbodyPx\tpromptPx\tarrayIndexPx"+
       "\tmainOverflowY\tslideOverflowY",...report].join("\n"));
    console.log("D020/D017/D018 visual QA screenshot and metrics count: "+results.length);
    console.log("FAILURE_COUNT="+failures.length);
    failures.forEach(x=>console.error("VISUAL-QA:",x));
    assert.deepEqual(failures,[],"Visual consistency and projection blockers");
  } finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
