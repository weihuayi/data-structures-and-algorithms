/* D018 R7 actual browser visual-scale audit, full 34-page coverage.
 * No external pages or remote assets. Requires Node + Playwright Chromium.
 * Usage: node course/decks/d018-hashing/prototypes/check_r7_visual.cjs [output-dir]
 * Recorded CSS/SVG sizes and screenshots are implementation evidence,
 * not direct observations of a classroom.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..');
const html=path.join(root,'index.html');
const out=path.resolve(process.argv[2]||path.join(os.tmpdir(),'d018-r7-visual'));
const packagePath=path.resolve(__dirname,'../../../../tools/deck/node_modules/playwright');
const playwrightModule=process.env.PLAYWRIGHT_MODULE||process.env.DECK_PLAYWRIGHT_MODULE||(fs.existsSync(packagePath)?packagePath:'playwright');
const sample=new Set(['cover','detect-collision','chaining','chain-lookup','linear-probe','linear-probe-complete','probe-delete','probe-delete-tombstone','invariant','cost-asl-fail','code-bridge','homework']);
const views=[[1280,720],[1440,900],[2048,1107]];
const minSizes={
 '.hash-r7-cover-lead':27,
 '.hash-r7-cover-sequence':21,
 '.hash-lead':23.5,
 '.hash-note':16.5,
 '.hash-v2-intro':20.5,
 '.hash-v2-cell strong':27.5,
 '.hash-v2-index':17.5,
 '.hash-v2-state':15.5,
 '.hash-v2-figure figcaption':17.5,
 '.hash-table td':19.5,
 '.hash-table th':19.5,
 '.course-prompt':23.5,
 '.course-answer summary':19.5,
 '.hash-v2-cost strong':24.5,
 '.hash-v2-cost span':16.5,
 '.hash-r7-chain-key':19,
 '.hash-r7-chain-next':16.5,
 '.hash-r7-chain-null':16.5,
 '.hash-r7-bucket-label':16.5
};
async function main(){
  assert(fs.existsSync(html),'No generated HTML: '+html);
  const {chromium}=require(playwrightModule);
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE_PATH||process.env.DECK_BROWSER_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE_PATH||process.env.DECK_BROWSER_EXECUTABLE}:{})});
  fs.mkdirSync(out,{recursive:true});
  const result={source:'course/decks/d018-hashing/index.html',viewports:[],limits:['Recorded browser CSS/SVG font sizes are not classroom viewing measurements.']};
  let count=0;
  try{
    for(const [width,height] of views){
      const page=await browser.newPage({viewport:{width,height}});
      const errors=[];
      page.on('pageerror',err=>errors.push(String(err)));
      await page.goto(pathToFileURL(html).href,{waitUntil:'load'});
      await page.evaluate(()=>document.fonts.ready);
      const batch={viewport:[width,height],slides:[]};
      const ids=await page.locator('.slide').evaluateAll(slides=>slides.map(s=>s.dataset.pageId));
      assert.equal(ids.length,34,'D018 must have 34 slides');
      for(let i=0;i<ids.length;i++){
        await page.locator('#slide-select').selectOption({index:i});
        await page.waitForFunction(id=>document.querySelector('section.slide.active')?.dataset.pageId===id,ids[i]);
        const data=await page.evaluate(()=>{
          const slide=document.querySelector('section.slide.active');
          const area=slide.querySelector('.hash-lesson');
          const title=slide.querySelector('h2');
          const box=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
          const round=n=>Math.round(n*10)/10;
          const sizes={};
          for(const sel of Object.keys(window.__d018Selectors||{})){/* reserved for simple iteration */}
          const keys=[
            '.hash-r7-cover-lead','.hash-r7-cover-sequence','.hash-lead','.hash-note',
            '.hash-v2-intro','.hash-v2-cell strong','.hash-v2-index','.hash-v2-state',
            '.hash-v2-figure figcaption','.hash-table td','.hash-table th',
            '.course-prompt','.course-answer summary','.hash-v2-cost strong',
            '.hash-v2-cost span','.hash-r7-chain-key','.hash-r7-chain-next',
            '.hash-r7-chain-null','.hash-r7-bucket-label'
          ];
          for(const selector of keys){
            const el=slide.querySelector(selector);
            if(!el)continue;
            const font=parseFloat(getComputedStyle(el).fontSize);
            const svg=el.closest('svg');
            let scale=1;
            if(svg){
              const rect=svg.getBoundingClientRect();
              const vb=svg.viewBox.baseVal;
              scale=Math.min(rect.width/vb.width,rect.height/vb.height);
            }
            sizes[selector]={css:round(font),effective:round(font*scale),visible:el.getClientRects().length>0};
          }
          const root=document.documentElement;
          return {
            id:slide.dataset.pageId,role:slide.dataset.role,
            content:area?box(area):null,title:title?box(title):null,
            answerClosed:[...slide.querySelectorAll('details.course-answer')].every(e=>!e.open),
            documentOverflow:{x:round(root.scrollWidth-innerWidth),y:round(root.scrollHeight-innerHeight)},
            slideOverflow:round(slide.scrollHeight-slide.clientHeight),
            sizes
          };
        });
        assert.equal(data.id,ids[i]);
        assert(data.answerClosed,'Student answer is expanded by default: '+data.id);
        assert(data.documentOverflow.x<=1,'Horizontal overflow: '+JSON.stringify({id:data.id,viewport:[width,height],overflow:data.documentOverflow}));
        if(data.content){
          assert(data.title,'No page heading: '+data.id);
          assert(Math.abs(data.content.x-data.title.x)<=12,'Title/content baseline mismatch: '+data.id);
          for(const [selector,minimum] of Object.entries(minSizes)){
            const v=data.sizes[selector];
            if(v&&v.visible){
              assert(v.effective>=minimum,data.id+' '+selector+' actual '+v.effective+'px, required '+minimum+'px at '+width+'x'+height);
            }
          }
          const contentFont=await page.locator('section.slide.active .hash-lesson').evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
          assert(contentFont>=20.5,'Root content font too small on '+data.id);
        }
        if(sample.has(data.id)){
          const filename='r7-'+data.id+'-'+width+'x'+height+'.png';
          await page.screenshot({path:path.join(out,filename),fullPage:false});
          data.screenshot=filename;
        }
        batch.slides.push(data);count++;
      }
      assert.deepEqual(errors,[],'Browser errors at '+width+'x'+height);
      result.viewports.push(batch);
      await page.close();
    }
  }finally{await browser.close();}
  fs.writeFileSync(path.join(out,'visual-scale-audit.json'),JSON.stringify(result,null,2)+'\n');
  console.log('R7 visual-scale audit PASS: '+count+' slide/viewport combinations; 34 pages × 3 viewports. Evidence: '+out);
}
main().catch(e=>{console.error(e);process.exitCode=1});
