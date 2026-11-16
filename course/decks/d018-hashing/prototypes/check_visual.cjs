/* D018 R5 prototype verification; run with Node + Playwright.
 * node course/decks/d018-hashing/prototypes/check_visual.cjs [output-directory]
 * By design this does not load or modify the formal D018 deck.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');

const HTML = path.join(__dirname,'r5-two-core-prototypes.html');
const OUTPUT = process.argv[2] || path.join(__dirname,'evidence');
const A = [null,null,null,10,17,24,13];
const W = [null,null,null,10,null,24,13];
const B = [null,null,null,10,'DEL',24,13];
const P2 = [
  {slots:[null,null,null,10,null,null,null],path:[]},
  {slots:[null,null,null,10,null,null,null],path:[3]},
  {slots:[null,null,null,10,null,null,null],path:[3,4]},
  {slots:[null,null,null,10,17,null,null],path:[3,4]},
];
const P4 = [
  {slots:A,path:[]},
  {slots:W,path:[3,4]},
  {slots:A,path:[]},
  {slots:B,path:[3,4,5]},
  {slots:B,path:[3,4,5]},
];
function independentFind(slots,key) {
  const visits=[];
  for(let i=0;i<7;i++){
    const at=(key%7+i)%7;visits.push(at);
    if(slots[at]===null)return {found:-1,visits};
    if(typeof slots[at]==='number' && slots[at]===key)return {found:at,visits};
  }
  return {found:-1,visits};
}
assert.deepEqual(independentFind(A,24),{found:5,visits:[3,4,5]});
assert.deepEqual(independentFind(W,24),{found:-1,visits:[3,4]});
assert.deepEqual(independentFind(B,24),{found:5,visits:[3,4,5]});

async function main() {
  fs.mkdirSync(OUTPUT,{recursive:true});
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
  const report=[];
  try {
    for(const [width,height] of [[1280,720],[1440,900]]) {
      const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
      const errors=[];page.on('pageerror',e=>errors.push(String(e)));
      await page.setContent(fs.readFileSync(HTML,'utf8'));
      for(const [mode,expected] of [['P2',P2],['P4',P4]]) {
        await page.locator(`button[data-mode="${mode}"]`).click();
        assert.equal(await page.locator('#prev').isDisabled(),true);
        for(let i=0;i<expected.length;i++) {
          const state=await page.evaluate(()=>window.D018Prototype.getState());
          assert.equal(state.mode,mode);assert.equal(state.step,i);
          assert.deepEqual(state.scene.slots,expected[i].slots);
          assert.deepEqual(state.scene.path,expected[i].path);
          const dom=await page.evaluate(()=>({
            states:[...document.querySelectorAll('.slot')].map(e=>e.dataset.state),
            path:[...document.querySelectorAll('.visit')].map(e=>Number(e.textContent)),
            dimensions:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},
            rects:[...document.querySelectorAll('.head,.slide,.context,.main,.stage,.reason,.footer')].map(e=>({x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right,bottom:e.getBoundingClientRect().bottom}))
          }));
          assert.deepEqual(dom.path,expected[i].path);
          const states=expected[i].slots.map(v=>v===null?'EMPTY':v==='DEL'?'DELETED':'OCCUPIED');
          assert.deepEqual(dom.states,states);
          assert.ok(dom.dimensions.width<=width+1,`horizontal overflow: ${mode} ${i} ${width}x${height}`);
          assert.ok(dom.dimensions.height<=height+1,`vertical overflow: ${mode} ${i} ${width}x${height}`);
          for(const r of dom.rects){
            assert.ok(r.x>=-1&&r.right<=width+1,`out-of-bounds horizontal region: ${mode} ${i}`);
            assert.ok(r.bottom<=height+1,`out-of-bounds vertical region: ${mode} ${i}`);
          }
          const fname=`${mode.toLowerCase()}-s${i+1}-${width}x${height}.png`;
          await page.screenshot({path:path.join(OUTPUT,fname)});
          report.push({mode,step:i+1,viewport:`${width}x${height}`,screenshot:fname,status:'pass'});
          if(i<expected.length-1)await page.locator('#next').click();
        }
        assert.equal(await page.locator('#next').isDisabled(),true);
        await page.locator('#reset').click();
        assert.equal((await page.evaluate(()=>window.D018Prototype.getState())).step,0);
        await page.keyboard.press('ArrowRight');
        assert.equal((await page.evaluate(()=>window.D018Prototype.getState())).step,1);
      }
      assert.deepEqual(errors,[]);
      await page.close();
    }
  } finally {await browser.close();}
  fs.writeFileSync(path.join(OUTPUT,'report.json'),JSON.stringify({status:'pass',checks:report},null,2));
  console.log(`D018 R5 P2/P4 browser prototypes: PASS (${report.length} scene × viewport checks)`);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
