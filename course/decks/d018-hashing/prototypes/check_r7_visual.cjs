/* D018 R7 visual-scale audit for the three-page style trial.
 * Requires Node.js + Playwright Chromium.
 * Usage: node course/decks/d018-hashing/prototypes/check_r7_visual.cjs [output-dir]
 * Output: screenshots and computed CSS/SVG typography report.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..');
const html=path.join(root,'index.html');
const output=path.resolve(process.argv[2]||path.join(os.tmpdir(),'d018-r7-visual'));
const targets=[
  {id:'cover',n:1,required:{'.hash-r7-cover-lead':27,'.hash-r7-cover-sequence':21,'.hash-r7-cover-note':17}},
  {id:'detect-collision',n:9,required:{'.hash-lead':23,'.course-prompt':23,'.hash-v2-cell strong':28,'.hash-v2-state':16.5,'.hash-v2-figure figcaption':17}},
  {id:'chain-lookup',n:12,required:{'.hash-v2-intro':20,'.course-prompt':23},svg:{'.hash-r7-bucket-label':16,'.hash-r7-chain-key':20,'.hash-r7-chain-next':17,'.hash-r7-chain-null':17}}
];
async function check(){
  assert(fs.existsSync(html),'D018 index.html not found; run the repo builder first');
  const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE_PATH?{executablePath:process.env.CHROMIUM_EXECUTABLE_PATH}:{})});
  fs.mkdirSync(output,{recursive:true});
  const report={source:html,viewports:[],limits:['Browser computed metrics are not actual classroom viewing measurements.']};
  try{
    for(const [width,height] of [[1280,720],[1440,900],[2048,1107]]){
      const page=await browser.newPage({viewport:{width,height}});
      const errors=[];
      page.on('pageerror',e=>errors.push(String(e)));
      await page.goto(pathToFileURL(html).href,{waitUntil:'load'});
      const set={viewport:[width,height],pages:[]};
      for(const target of targets){
        await page.locator('#slide-select').selectOption({index:target.n-1});
        await page.waitForFunction(id=>document.querySelector('section.slide.active')?.dataset.pageId===id,target.id);
        const metrics=await page.evaluate(({required,svg})=>{
          const slide=document.querySelector('section.slide.active');
          const area=slide.querySelector('.hash-lesson');
          const title=slide.querySelector('h2');
          const box=el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
          const round=n=>Math.round(n*10)/10;
          const sizes={};
          const pick=(selector,isSvg=false)=>{
            const el=slide.querySelector(selector);
            if(!el)return null;
            const font=parseFloat(getComputedStyle(el).fontSize);
            let scale=1;
            if(isSvg){
              const canvas=el.closest('svg');
              const rect=canvas.getBoundingClientRect();
              const vb=canvas.viewBox.baseVal;
              scale=Math.min(rect.width/vb.width,rect.height/vb.height);
            }
            return{css:round(font),effective:round(font*scale),box:box(el)};
          };
          for(const sel of Object.keys(required))sizes[sel]=pick(sel);
          for(const sel of Object.keys(svg||{}))sizes[sel]=pick(sel,true);
          const root=document.documentElement;
          return {
            pageId:slide.dataset.pageId,
            title:title.textContent,
            content:box(area),titleBox:box(title),
            overflow:{horizontal:root.scrollWidth-innerWidth,vertical:root.scrollHeight-innerHeight,slideExtra:slide.scrollHeight-slide.clientHeight},
            answerOpen:[...slide.querySelectorAll('details.course-answer')].some(el=>el.open),
            sizes
          };
        },target);
        assert.equal(metrics.pageId,target.id,'wrong active page');
        assert(!metrics.answerOpen,'answers should initially be closed: '+target.id);
        assert(metrics.overflow.horizontal<=1,'Horizontal overflow: '+JSON.stringify(metrics.overflow));
        for(const [sel,min] of Object.entries(target.required)){
          const v=metrics.sizes[sel];assert(v,'Missing '+sel+' on '+target.id);
          assert(v.effective>=min,target.id+' '+sel+' too small: '+v.effective+'px < '+min+'px');
        }
        for(const [sel,min] of Object.entries(target.svg||{})){
          const v=metrics.sizes[sel];assert(v,'Missing SVG label '+sel);
          assert(v.effective>=min,target.id+' '+sel+' too small: '+v.effective+'px < '+min+'px');
        }
        assert(Math.abs(metrics.content.x-metrics.titleBox.x)<=12,target.id+' title/content horizontal drift');
        const filename='d018-r7-'+target.id+'-'+width+'x'+height+'.png';
        await page.screenshot({path:path.join(output,filename),fullPage:false});
        set.pages.push({...metrics,screenshot:filename});
      }
      assert.equal(errors.length,0,errors.join('\n'));
      report.viewports.push(set);
      await page.close();
    }
  }finally{await browser.close();}
  fs.writeFileSync(path.join(output,'visual-scale-audit.json'),JSON.stringify(report,null,2)+'\n');
  console.log('D018 R7 visual scale: '+report.viewports.reduce((a,v)=>a+v.pages.length,0)+' captures passed; '+output);
}
check().catch(e=>{console.error(e);process.exitCode=1});
