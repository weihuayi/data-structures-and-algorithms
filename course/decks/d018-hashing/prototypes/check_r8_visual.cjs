/* D018 R8: compare real D017/D018 outline fonts and capture 2/4/34.
 * Requires Playwright Chromium. No external network.
 * Usage: node course/decks/d018-hashing/prototypes/check_r8_visual.cjs [out-dir]
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const d018=path.resolve(__dirname,'..');
const d017=path.resolve(__dirname,'../../d017-bst-avl');
const output=path.resolve(process.argv[2]||path.join(os.tmpdir(),'d018-r8-visual'));
const localDriver=path.resolve(__dirname,'../../../../tools/deck/node_modules/playwright');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||process.env.DECK_PLAYWRIGHT_MODULE||(fs.existsSync(localDriver)?localDriver:'playwright'));
const selectors={
 number:'.course-outline-number',
 title:'.course-outline-topic strong',
 description:'.course-outline-topic p',
 pages:'.course-outline-pages'
};
async function openDeck(browser,dir,width,height){
 const file=path.join(dir,'index.html');
 assert(fs.existsSync(file),'Missing '+file);
 const page=await browser.newPage({viewport:{width,height}});
 await page.goto(pathToFileURL(file).href,{waitUntil:'load'});
 await page.evaluate(()=>document.fonts.ready);
 return page;
}
async function show(page,num,id){
 await page.locator('#slide-select').selectOption({index:num-1});
 await page.waitForFunction(expected=>document.querySelector('section.slide.active')?.dataset.pageId===expected,id);
}
async function inspectOutline(page){
 return page.evaluate(keys=>{
  const slide=document.querySelector('section.slide.active');
  const sizes={};
  for(const [name,selector] of Object.entries(keys)){
   const el=slide.querySelector(selector);
   if(!el)throw new Error('Missing '+selector);
   sizes[name]=parseFloat(getComputedStyle(el).fontSize);
  }
  const root=document.documentElement;
  return {id:slide.dataset.pageId,sizes,slideOverflow:slide.scrollHeight-slide.clientHeight,horizontalOverflow:root.scrollWidth-innerWidth};
 },selectors);
}
async function run(){
 fs.mkdirSync(output,{recursive:true});
 const executablePath=process.env.CHROMIUM_EXECUTABLE_PATH||process.env.DECK_BROWSER_EXECUTABLE;
 const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
 const evidence={viewports:[],screenshots:[]};
 try{
  for(const [width,height] of [[1280,720],[1440,900],[2048,1107]]){
   const ref=await openDeck(browser,d017,width,height);
   const d18=await openDeck(browser,d018,width,height);
   const save=async(page,name)=>{
    const file=name+'-'+width+'x'+height+'.png';
    await page.screenshot({path:path.join(output,file),fullPage:false});
    evidence.screenshots.push(file);
   };
   try{
    await show(ref,2,'outline');
    await show(d18,2,'outline');
    const a=await inspectOutline(ref),b=await inspectOutline(d18);
    for(const key of Object.keys(selectors)){
      assert(Math.abs(a.sizes[key]-b.sizes[key])<0.1,'D017/D018 '+key+' actual font mismatch: '+a.sizes[key]+' vs '+b.sizes[key]);
    }
    assert(a.slideOverflow<=1&&b.slideOverflow<=1,'Outline 720/900/2048 height overflow');
    assert(a.horizontalOverflow<=1&&b.horizontalOverflow<=1,'Outline horizontal overflow');
    await save(ref,'d017-outline');
    await save(d18,'d018-outline');
    const current={viewport:[width,height],reference:a,actual:b,reviewPages:[]};
    for(const [num,id] of [[4,'recall-avl'],[34,'homework']]){
     await show(d18,num,id);
     const item=await d18.evaluate(()=>{
      const slide=document.querySelector('section.slide.active');
      const root=document.documentElement;
      const svg=slide.querySelector('svg.hash-r8-bst-svg');
      const pre=slide.querySelector('pre.hash-r8-homework-code');
      return{
       id:slide.dataset.pageId,
       overflowY:slide.scrollHeight-slide.clientHeight,
       overflowX:root.scrollWidth-innerWidth,
       nodeCount:svg?svg.querySelectorAll('circle').length:0,
       codeVisible:!!pre&&pre.getBoundingClientRect().width>0,
       answersClosed:[...slide.querySelectorAll('details.course-answer')].every(x=>!x.open)
      };
     });
     assert.equal(item.id,id);
     assert(item.overflowY<=1&&item.overflowX<=1,id+' overflow '+JSON.stringify(item));
     assert(item.answersClosed,id+' answer unexpectedly expanded');
     if(id==='recall-avl')assert.equal(item.nodeCount,7);
     if(id==='homework')assert(item.codeVisible,'C11 command block not visible');
     current.reviewPages.push(item);
     await save(d18,'d018-'+id);
    }
    evidence.viewports.push(current);
   }finally{await ref.close();await d18.close();}
  }
 }finally{await browser.close();}
 fs.writeFileSync(path.join(output,'r8-visual-report.json'),JSON.stringify(evidence,null,2)+'\n');
 console.log('R8 visual PASS: 3 matching outline font comparisons and '+evidence.screenshots.length+' actual screenshots');
}
run().catch(e=>{console.error(e);process.exitCode=1});
