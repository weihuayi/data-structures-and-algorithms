/* D018 R5 second-batch visual and independent mathematical regression.
 * Requires Node.js and Playwright: node check_followup.cjs
 * Browser executable can be set with CHROMIUM_EXECUTABLE_PATH.
 */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');

function buildLinear(keys,m=7){
  const slots = Array(m).fill(null);
  const paths=[];
  for(const key of keys){
    const trail=[];let written=false;
    for(let i=0;i<m;i++){
      const at=(key%m+i)%m;trail.push(at);
      if(slots[at]===null){slots[at]=key;written=true;break;}
    }
    assert(written,'unexpected full table'); paths.push(trail);
  }
  return {slots,paths};
}
function missProbeCount(slots,initial){
  const seq=[];
  for(let i=0;i<slots.length;i++){
    const at=(initial+i)%slots.length;seq.push(at);
    if(slots[at]===null) return seq;
  }
  return seq;
}
function chains(keys,m=7){
  const buckets=Array.from({length:m},()=>[]);
  for(const key of keys)buckets[key%m].push(key);
  return buckets;
}
async function main(){
  // Compute independently of embedded slide scene values.
  const expected=buildLinear([10,17,24,13]);
  assert.deepEqual(expected.slots,[null,null,null,10,17,24,13]);
  assert.deepEqual(expected.paths,[[3],[3,4],[3,4,5],[6]]);
  const buckets=chains([10,17,24,13]);
  assert.deepEqual(buckets[3],[10,17,24]);assert.deepEqual(buckets[6],[13]);
  const miss=Array.from({length:7},(_,r)=>missProbeCount(expected.slots,r));
  assert.deepEqual(miss.map(x=>x.length),[1,1,1,5,4,3,2]);
  assert.equal(miss.reduce((sum,x)=>sum+x.length,0),17);

  const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE_PATH?{executablePath:process.env.CHROMIUM_EXECUTABLE_PATH}:{})});
  const viewports=[[1280,720],[1440,900]];
  const scenes={P1:4,P3:4,P5:4};
  let checked=0;
  try{
    for(const [width,height] of viewports){
      const page=await browser.newPage({viewport:{width,height}});
      const errors=[];
      page.on('pageerror',e=>errors.push(String(e)));
      await page.route(/^https?:/,route=>route.abort());
      await page.setContent(fs.readFileSync(path.join(__dirname,'r5-followup-prototypes.html'),'utf8'),{waitUntil:'load'});
      for(const [mode,count] of Object.entries(scenes)){
        await page.locator(`button.tab[data-mode="${mode}"]`).click();
        for(let step=0;step<count;step++){
          assert.equal(await page.locator('body').getAttribute('data-scene'),`${mode}.${step+1}`);
          const layout=await page.evaluate(()=>{
            const d=document.documentElement,b=document.body,r=document.getElementById('visual').getBoundingClientRect();
            return {sw:d.scrollWidth,sh:d.scrollHeight,bw:b.scrollWidth,bh:b.scrollHeight,visualRight:r.right,visualBottom:r.bottom};
          });
          assert(layout.sw<=width+1&&layout.sh<=height+1,`${mode}.${step+1} ${width}x${height} overflow ${JSON.stringify(layout)}`);
          assert(layout.visualRight<=width-20&&layout.visualBottom<=height-45,`${mode}.${step+1} clipped illustration`);
          if(mode==='P1'){
            const nodes=await page.locator('rect.node').count();
            assert.equal(nodes,[0,1,4,4][step]);
            if(step>=2) assert.deepEqual(await page.locator('text.ktext').allTextContents(),[10,17,24,13].map(String));
          }else if(mode==='P3'){
            const actual=await page.locator('[data-slot]').evaluateAll(els=>els.map(e=>e.dataset.value));
            const target=step<2?[null,null,null,10,17,null,null]:step===2?[null,null,null,10,17,24,null]:expected.slots;
            assert.deepEqual(actual,target.map(v=>v===null?'EMPTY':String(v)));
            if(step===0)assert.equal((await page.locator('.path').innerText()).includes('不显示完成路径'),true);
          }else{
            const actual=await page.locator('[data-r]').evaluateAll(els=>els.map(e=>e.dataset.cost));
            const all=miss.map(a=>String(a.length));
            const target=step===0?Array(7).fill('hidden'):step===1?['hidden','hidden','hidden','5','hidden','hidden','hidden']:all;
            assert.deepEqual(actual,target);
            if(step===3)assert((await page.locator('.formula-result').innerText()).includes('17/7'));
          }
          checked++;
          if(step<count-1)await page.locator('#next').click();
        }
        assert(await page.locator('#next').isDisabled());
        await page.locator('#reset').click();
        assert.equal(await page.locator('body').getAttribute('data-step'),'0');
        await page.keyboard.press('ArrowRight');assert.equal(await page.locator('body').getAttribute('data-step'),'1');
        await page.keyboard.press('ArrowLeft');assert.equal(await page.locator('body').getAttribute('data-step'),'0');
      }
      assert.deepEqual(errors,[]);
      await page.close();
    }
    console.log(`D018 R5 P1/P3/P5 check: PASS (${checked} scene × viewport states; 3 prototypes; independent algorithm checks)`);
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1});