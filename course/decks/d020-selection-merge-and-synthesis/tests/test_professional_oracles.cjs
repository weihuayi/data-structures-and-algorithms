"use strict";
/* Deterministic property tests against independent reference sorting oracles.
 * Do not use the algorithm-under-test's own traced result as the oracle.
 */
const assert=require("node:assert/strict");
const T=require("../prototypes/trace.js");
let seed=20261124;
function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
const range=n=>Array.from({length:n},(_,i)=>i);
let heap=0,merges=0,radix=0,negative=0;
for(let n=0;n<=45;n++)for(let t=0;t<28;t++){
 const a=range(n).map(()=>Math.floor(rand()*51)-25), original=a.slice();
 const expected=a.slice().sort((x,y)=>x-y),result=T.heapTrace(a);
 assert(T.validHeap(result.built),"heap order n="+n);
 assert.deepEqual(result.built.slice().sort((x,y)=>x-y),expected);
 if(n>1){
  assert(T.validHeap(result.afterExtract,n-1));
  assert.equal(result.afterExtract[n-1],expected[n-1]);
  assert.deepEqual(result.afterExtract.slice().sort((x,y)=>x-y),expected);
 }
 assert.deepEqual(a,original,"input mutation");
 heap++;
}
assert.equal(T.rootDownCounterexample().stillInvalid,true);negative++;
for(let i=0;i<900;i++){
 const left=range(Math.floor(rand()*25)).map(i=>T.record(Math.floor(rand()*13),"L"+i)).sort((a,b)=>a.key-b.key);
 const right=range(Math.floor(rand()*25)).map(i=>T.record(Math.floor(rand()*13),"R"+i)).sort((a,b)=>a.key-b.key);
 const expected=left.concat(right).map((x,pos)=>({...x,pos}))
  .sort((a,b)=>a.key-b.key||a.pos-b.pos).map(x=>x.id);
 const result=T.stableMergeTrace(left,right);
 assert.deepEqual(result.result.map(x=>x.id),expected);
 merges++;
}
assert.throws(()=>T.stableMergeTrace([T.record(2,"a"),T.record(1,"b")],[]),/sorted/);
negative++;
for(const base of [2,10,16])for(let i=0;i<200;i++){
 const n=Math.floor(rand()*36),values=range(n).map(i=>T.record(Math.floor(rand()*2049),"R"+i));
 const result=T.radixTrace(values,base);
 const expected=values.slice().sort((a,b)=>a.key-b.key).map(x=>x.id);
 assert.deepEqual(result.result.map(x=>x.id),expected);
 for(let d=0;d<result.rounds.length;d++){
  const mod=base**(d+1);
  const refRound=values.slice().sort((a,b)=>(a.key%mod)-(b.key%mod)).map(x=>x.id);
  assert.deepEqual(result.rounds[d].map(x=>x.id),refRound);
 }
 radix++;
}
assert.throws(()=>T.radixTrace([T.record(-1,"x")]),/nonnegative/);
assert.throws(()=>T.radixTrace([T.record(100,"x")],10,2),/Digits too small/);
negative+=2;
console.log("PASS independent JS oracle cases: heap="+heap+" merge="+merges+" radix="+radix+" invalid="+negative+" seed=20261124");
