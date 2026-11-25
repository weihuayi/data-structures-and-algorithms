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
// Explicit D020 peer groups only; compact input, tasks and arbitrary boxes
// are not equivalent semantic containers. Radix stability's group is folded.
const peerGroups = {
  "simple-selection":2,"tournament-bridge":1,"heap-opportunity":1,
  "heap-contract":1,"heap-vs-bst":1,"sift-down":1,"merge-opportunity":1,
  "stable-merge-independent":1,"merge-invariant":1,"merge-cost":1,
  "radix-opportunity":1,"radix-buckets":1,"radix-stability":1,
  "comparison-model":1,"mechanism-synthesis":1
};
async function peerGeometry(page){
  return page.evaluate(()=>{
    const slide=document.querySelector("main .slide.active");
    return [...slide.querySelectorAll(".d20-columns,.d20-compare")].map((g,index)=>{
      const rect=e=>{const r=e.getBoundingClientRect();return {
        top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height
      }};
      const cs=getComputedStyle(g),r=rect(g);
      const cards=[...g.children].map(e=>{
        const s=getComputedStyle(e);
        return {...rect(e),card:e.classList.contains("d20-box"),
          overflowX:e.scrollWidth-e.clientWidth,overflowY:e.scrollHeight-e.clientHeight,
          marginTop:parseFloat(s.marginTop),marginBottom:parseFloat(s.marginBottom)};
      });
      // Hidden answer groups are inventoried but not treated as zero-sized cards.
      return {index,kind:g.classList.contains("d20-compare")?"compare":"columns",
        visible:r.width>0&&r.height>0&&(!g.closest("details")||g.closest("details").open),
        columns:cs.gridTemplateColumns,align:cs.alignItems,
        gapX:parseFloat(cs.columnGap),gapY:parseFloat(cs.rowGap),...r,cards};
    });
  });
}
function peerIssues(groups,pid,narrow,expanded=false){
  const issues=[],tol=1;
  const near=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=tol;
  const expected=peerGroups[pid]||0;
  if(groups.length!==expected)issues.push("peer inventory "+groups.length+"/"+expected);
  const visible=groups.filter(g=>g.visible);
  const visibleExpected=pid==="radix-stability"&&!expanded?0:expected;
  if(visible.length!==visibleExpected)issues.push("visible peer groups "+visible.length+"/"+visibleExpected);
  for(const g of visible){
    const bad=msg=>issues.push("peer group "+g.index+" "+msg);
    const k=g.kind==="compare"?3:2,c=g.cards;
    if(c.length!==k||c.some(x=>!x.card)){bad("unexpected direct card children");continue;}
    if(g.align!=="stretch")bad("align-items="+g.align);
    if(g.columns.trim().split(/\s+/).length!==(narrow?1:k))bad("unexpected grid columns "+g.columns);
    if(c.some(x=>x.width<=0||x.height<=0||x.overflowX>2||x.overflowY>2))bad("card content overflow/zero size");
    if(c.some(x=>!near(x.marginTop,0)||!near(x.marginBottom,0)))bad("vertical card margins");
    if(narrow){
      for(let i=0;i<c.length;i++){
        if(!near(c[i].left,g.left)||!near(c[i].right,g.right))bad("single column width");
        if(i&&!near(c[i].top-c[i-1].bottom,g.gapY))bad("single column gap");
      }
    }else{
      for(let i=0;i<c.length;i++){
        if(!near(c[i].top,c[0].top)||!near(c[i].bottom,c[0].bottom)||!near(c[i].width,c[0].width))
          bad("unequal card outer geometry");
        if(i&&!near(c[i].left-c[i-1].right,g.gapX))bad("column gap");
      }
      if(!near(c[0].left,g.left)||!near(c[k-1].right,g.right))bad("group width not filled");
    }
  }
  return issues;
}
async function checkPeerGeometry(page,pid,width,height,expanded,results,failures){
  const groups=await peerGeometry(page);
  const issues=peerIssues(groups,pid,width<=900,expanded);
  for(const issue of issues)failures.push("D020 "+width+"x"+height+" "+pid+" "+issue);
  if(groups.length)results.push({id:pid,viewport:width+"x"+height,expanded,groups,issues});
}
async function testPeerAdaptation(page,results,failures){
  // Fault injection against the actual asymmetric page-6 input, not a
  // stylesheet string check. Restore the DOM and inline styles before leaving.
  const group=page.locator("main .slide.active .d20-columns");
  const baseline=await peerGeometry(page);
  const [original]=baseline;
  assert(original&&original.visible,"peer adaptation fixture missing");
  const natural=await group.evaluate(g=>{
    const prev=g.style.alignItems;
    try{
      g.style.alignItems="start";
      return [...g.children].map(e=>e.getBoundingClientRect().height);
    }finally{g.style.alignItems=prev;}
  });
  if(Math.abs(natural[0]-natural[1])<=1)failures.push("D020 peer negative fixture must be asymmetric");
  if(Math.abs(Math.max(...natural)-original.cards[0].height)>1)
    failures.push("D020 stretch row taller than natural maximum");
  await group.evaluate(g=>{g.style.alignItems="start";});
  try{
    const bad=peerIssues(await peerGeometry(page),"tournament-bridge",false);
    if(!bad.some(x=>x.includes("unequal card outer geometry")))failures.push("D020 geometry checker missed injected unequal heights");
  }finally{await group.evaluate(g=>{g.style.removeProperty("align-items");});}
  await group.evaluate(g=>{
    const p=document.createElement("p");
    p.dataset.peerTest="growth";p.textContent="测试动态内容。".repeat(160);
    g.children[0].append(p);
  });
  try{
    const grown=await peerGeometry(page),issues=peerIssues(grown,"tournament-bridge",false);
    if(issues.length||grown[0].cards[0].height<=original.cards[0].height+1)
      failures.push("D020 peer growth did not stretch both cards: "+issues.join("; "));
    results.push({id:"tournament-bridge",test:"fault-and-growth",natural,
      baseline:original.cards.map(x=>x.height),grown:grown[0].cards.map(x=>x.height),issues});
  }finally{await group.locator("[data-peer-test='growth']").evaluate(e=>e.remove());}
  const restored=await peerGeometry(page);
  if(restored.some((g,i)=>g.cards.some((c,j)=>Math.abs(c.height-baseline[i].cards[j].height)>1)))
    failures.push("D020 peer growth fixture did not restore geometry");
}
async function checkNarrowPeers(browser,results,failures){
  const width=800,height=900;
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  try{
    await page.goto("file://"+path.join(root,"course/decks/d020-selection-merge-and-synthesis/index.html"),{waitUntil:"load"});
    const items=await page.locator("main .slide").evaluateAll(elems=>elems.map((e,index)=>({id:e.dataset.pageId,index})));
    for(const pid of Object.keys(peerGroups)){
      const item=items.find(x=>x.id===pid);assert(item,pid+" missing");
      await page.selectOption("#slide-select",String(item.index));
      await page.waitForFunction(x=>document.querySelector("main .slide.active")?.dataset.pageId===x,pid);
      await checkPeerGeometry(page,pid,width,height,false,results,failures);
      if(pid==="radix-stability"){
        const details=page.locator("main .slide.active details.course-answer");
        await details.locator(":scope > summary").click();
        await checkPeerGeometry(page,pid,width,height,true,results,failures);
      }
      // Natural heights must not be equalized across separate grid rows.
      const changes=await page.locator("main .slide.active .d20-columns,.deck .slide.active .d20-compare").evaluateAll(groups=>groups.filter(g=>g.getBoundingClientRect().height>0).map(g=>{
        const heights=()=>[...g.children].map(e=>e.getBoundingClientRect().height);
        const before=heights(),prev=g.style.alignItems;
        try{g.style.alignItems="start";return heights().map((h,i)=>Math.abs(h-before[i]));}
        finally{g.style.alignItems=prev;}
      }));
      if(changes.flat().some(x=>x>1))failures.push("D020 narrow "+pid+" unnatural row height");
    }
  }finally{await page.close();}
}

function choose(pageList,deckId){
  const firstRole=role=>pageList.find(x=>x.role===role)?.index;
  const idx=[firstRole("cover"),firstRole("outline"),firstRole("section"),
    firstRole("exercise"),pageList.length-1]; // final page may be role=content in legacy D017
  if(deckId==="D020"){
    for(const id of Object.keys(peerGroups)){
      const item=pageList.find(x=>x.id===id);if(item)idx.push(item.index);
    }
    for(const id of ["simple-selection","tournament-bridge","heap-opportunity","heap-contract","heap-array","heap-vs-bst","sift-down","sift-counterexample","build-heap","heap-independent","heapsort-boundary","heap-checkpoint",
      "merge-trace","stable-merge-independent","radix-linked-trace","radix-independent","radix-stability",
      "comparison-model","mechanism-synthesis","homework-bridge"]){
      const item=pageList.find(x=>x.id===id);if(item)idx.push(item.index);
    }
  }
  return [...new Set(idx.filter(Number.isInteger))].sort((a,b)=>a-b);
}
(async()=>{
  const browser=await chromium.launch({headless:true,
    executablePath:process.env.DECK_BROWSER_EXECUTABLE||undefined,
    args:["--allow-file-access-from-files"]});
  const results=[],failures=[],peerResults=[];
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
            await checkPeerGeometry(page,m.id,width,height,false,peerResults,failures);
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
              if(!m.homeworkText||m.homeworkText.fontPx<20.9)
                failures.push("D020 homework text smaller than D018/D019 A/B 21px floor");
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
        if(d.id==="D020"){
          const record=items.find(x=>x.id==="tournament-bridge");
          await page.selectOption("#slide-select",String(record.index));
          await page.waitForFunction(()=>document.querySelector("main .slide.active")?.dataset.pageId==="tournament-bridge");
          await testPeerAdaptation(page,peerResults,failures);
        }
        // Additional D020 teaching states: opening an answer must not destroy
        // the original problem, and scrolling is allowed but clipping is not.
        if(d.id==="D020"){
          for(const pid of ["tournament-bridge","sift-counterexample","heap-independent","heapsort-boundary","heap-checkpoint","stable-merge-independent",
            "radix-independent","radix-stability","comparison-model","choice-independent"]){
            const record=items.find(x=>x.id===pid);
            assert(record,pid+" missing");
            await page.selectOption("#slide-select",String(record.index));
            await page.waitForFunction(x=>document.querySelector("main .slide.active")?.dataset.pageId===x,pid);
            const task=page.locator("main .slide.active .course-workspace");
            const input=task.locator("[data-task-input]");
            const original=await input.innerText();
            const answer=task.locator("details.course-answer");
            assert.equal(await answer.count(),1,pid+" must have one answer");
            assert.equal(await answer.getAttribute("open"),null,pid+" answer leaked");
            await answer.locator(":scope > summary").click();
            assert.equal(await answer.getAttribute("open"),"",pid+" cannot open answer");
            assert.equal(await input.innerText(),original,pid+" lost input");
            const state=await metrics(page);
            await checkPeerGeometry(page,pid,width,height,true,peerResults,failures);
            if(state.mainScrollWidth>state.mainWidth+2||
               state.slideScrollWidth>state.slideWidth+2)
              failures.push("D020 "+pid+" expanded horizontal overflow "+width);
            await page.screenshot({path:path.join(output,
              "d020-expanded-"+pid+"-"+width+"x"+height+".png")});
            if(pid==="choice-independent"){
              // The optional C prompt stays readable but is NOT required for
              // A/B completion; one shared answer disclosure has no nested
              // hidden state that the generic course checker cannot reach.
              assert.equal(await task.locator("details").count(),1,
                "P4 should have exactly one independent answer disclosure");
              assert.match(await input.innerText(),/C（选做挑战）/);
              assert.match(await answer.innerText(),/选做 C 参考/);
            }
            const solution=task.locator(".course-solution");
            await solution.scrollIntoViewIfNeeded();
            assert(await solution.isVisible(),pid+" solution not reachable");
            if(width===1280){
              await page.screenshot({path:path.join(output,
                "d020-solution-"+pid+"-"+width+"x"+height+".png")});
            }
          }
          for(const [pid,buttonId] of [["build-heap","#build-heap-next"],["merge-trace","#merge-next"],
                                      ["radix-linked-trace","#radix-next"]]){
            const record=items.find(x=>x.id===pid);
            await page.selectOption("#slide-select",String(record.index));
            for(let n=0;n<3;n++)await page.locator(buttonId).click();
            const state=await metrics(page);
            if(state.mainScrollWidth>state.mainWidth+2||
               state.slideScrollWidth>state.slideWidth+2)
              failures.push("D020 "+pid+" trace horizontal overflow "+width);
            await page.screenshot({path:path.join(output,
              "d020-step-"+pid+"-"+width+"x"+height+".png")});
          }
        }
        if(scriptErrors.length)failures.push(d.id+" JavaScript: "+JSON.stringify(scriptErrors));
        await page.close();
      }
    }
    await checkNarrowPeers(browser,peerResults,failures);
    fs.writeFileSync(path.join(output,"peer-geometry.json"),JSON.stringify({candidate:"D020",peerResults},null,2));
    for(const vp of viewports.map(x=>x.join("x"))){
      const byDeck=Object.fromEntries(target.map(d=>[d.id,results.filter(
        r=>r.deck===d.id&&r.viewport===vp)]));
      for(const field of ["h2","kicker","outlineTitle","sectionQuestion"]){
        const vals=target.map(d=>byDeck[d.id].find(r=>r[field])?.[field]?.fontPx)
          .filter(Number.isFinite);
        if(vals.length===3&&Math.max(...vals)-Math.min(...vals)>2.0)
          failures.push(vp+" shared "+field+" diverges "+JSON.stringify(vals));
      }
      // D017 generic cover paragraph and D020 lead are DIFFERENT semantic
      // roles, so font-size equality would be a false visual contract.
      // D018/D019/D020 matching cover lead and A/B homework metrics are
      // asserted by check_cover_homework_consistency.cjs using actual pixels.
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
