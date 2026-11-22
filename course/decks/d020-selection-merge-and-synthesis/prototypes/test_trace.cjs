"use strict";
const assert=require("node:assert/strict");
const T=require("./trace.js");
function stableSorted(a) {
  return a.every((r,i)=>i===0||a[i-1].key<=r.key);
}
function keepIds(a,b) {
  assert.deepEqual(a.map(x=>x.id).sort(),b.map(x=>x.id).sort(),"Record identity multiset must be preserved");
}
function testHeap(){
  const known=T.heapTrace([4,1,7,3,6,2,5]);
  assert.deepEqual(known.built,[7,6,5,3,1,2,4]);
  assert.deepEqual(known.afterExtract,[6,4,5,3,1,2,7]);
  assert.equal(T.validHeap(known.built),true);
  assert.equal(T.validHeap(known.afterExtract,known.activeAfter),true);
  assert.equal(T.validHeap([2,5,7,3,4,6,8]),false);
  const wrong=T.rootDownCounterexample();
  assert.deepEqual(wrong.result,[7,5,8,3,4,6,2]);
  assert.equal(wrong.stillInvalid,true);
  // Deterministic generated inputs, including duplicates and already sorted data.
  let seed=20261123;
  function next(){seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed;}
  for(let n=0;n<=60;n++)for(let trial=0;trial<16;trial++){
    const a=Array.from({length:n},()=>next()%97);
    const t=T.heapTrace(a);
    assert.equal(T.validHeap(t.built),true);
    if(n){
      assert.equal(t.built[0],Math.max(...a));
      assert.deepEqual(t.afterExtract.slice(-1),[Math.max(...a)]);
      assert.equal(T.validHeap(t.afterExtract,t.activeAfter),true);
    }
    assert.deepEqual(t.built.slice().sort((x,y)=>x-y),a.slice().sort((x,y)=>x-y));
    assert.deepEqual(t.afterExtract.slice().sort((x,y)=>x-y),a.slice().sort((x,y)=>x-y));
  }
}
function testMerge(){
  const R=T.record;
  const l=[R(2,"甲"),R(5,"乙"),R(8,"戊")],r=[R(2,"丙"),R(6,"丁"),R(7,"己")];
  const m=T.stableMergeTrace(l,r);
  assert.deepEqual(m.result.map(x=>x.id),["甲","丙","乙","丁","己","戊"]);
  assert.equal(stableSorted(m.result),true);keepIds(m.result,l.concat(r));
  assert.throws(()=>T.stableMergeTrace([R(5,"A"),R(1,"B")],r),/sorted/);
  for(let n=0;n<=30;n++){
    const l=Array.from({length:n},(_,i)=>R(Math.floor(i/3),"L"+i));
    const r=Array.from({length:n},(_,i)=>R(Math.floor(i/3),"R"+i));
    const z=T.stableMergeTrace(l,r);
    assert.equal(stableSorted(z.result),true);keepIds(z.result,l.concat(r));
    // Left precedence for equal keys; internal order of both sources preserved.
    for(let k=0;k<=n;k++){
      const ids=z.result.filter(x=>x.key===k).map(x=>x.id);
      const expected=l.concat(r).filter(x=>x.key===k).map(x=>x.id);
      assert.deepEqual(ids,expected);
    }
  }
}
function testRadix(){
  const R=T.record;
  const a=[321,156,57,46,28,7,331,33,34,63].map((k,i)=>R(k,"id"+i));
  const radix=T.radixTrace(a,10,3);
  assert.deepEqual(radix.rounds.map(round=>round.map(x=>x.key)),[
    [321,331,33,63,34,156,46,57,7,28],
    [7,321,28,331,33,34,46,156,57,63],
    [7,28,33,34,46,57,63,156,321,331]
  ]);
  assert.equal(stableSorted(radix.result),true);keepIds(radix.result,a);
  assert.throws(()=>T.radixTrace(a,10,2),/Digits too small/);
  let seed=73123;
  function next(){seed=(Math.imul(1103515245,seed)+12345)>>>0;return seed;}
  for(let t=0;t<140;t++){
    const a=Array.from({length:t%19},(_,i)=>R(next()%10000,"rec"+i));
    const b=T.radixTrace(a);
    const baseline=a.slice().sort((x,y)=>x.key-y.key);
    assert.deepEqual(b.result,baseline);
    keepIds(b.result,a);
    // Every allocated bucket must retain the order in which records arrived this pass.
    for(const s of b.states.filter(q=>q.kind==="collect")){
      assert.deepEqual(s.buckets.flat(),s.collected);
    }
  }
}
testHeap();testMerge();testRadix();
console.log("D020 isolated trace tests passed: heap prerequisites/extract, stable merge, radix FIFO, 960 generated heap cases, 140 generated radix cases.");
