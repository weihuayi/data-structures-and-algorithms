/* Independent assertions about the generated traces, including repeated-key inputs. */
const assert=require('node:assert/strict');
const {insertionTrace,partitionTrace}=require('./trace.js');
assert.deepEqual(insertionTrace([2,4,7,3,6],3).map(x=>x.values),[
 [2,4,7,3,6],[2,4,7,null,6],[2,4,null,7,6],[2,null,4,7,6],[2,3,4,7,6]]);
const revised=insertionTrace([2,6,7,5,1],3);
assert.deepEqual(revised.map(x=>x.values),[
 [2,6,7,5,1],[2,6,7,null,1],[2,6,null,7,1],
 [2,null,6,7,1],[2,5,6,7,1]]);
assert.deepEqual(revised.at(-1).values.slice(0,4),[2,5,6,7]);
assert.notDeepEqual(revised.at(-1).values,[...revised.at(-1).values].sort((a,b)=>a-b));
const given=partitionTrace([5,9,3,8,2,7,4,6,1]);
assert.deepEqual(given.values,[1,4,3,2,5,7,8,6,9]);assert.equal(given.pivotIndex,4);
let seed=270019,checks=0;
function random(){seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed;}
for(let trial=0;trial<900;trial++){
  const len=1+random()%18,values=Array.from({length:len},()=>random()%9);
  const out=partitionTrace(values),v=out.values,p=out.pivotIndex;
  assert.equal(v[p],values[0]);
  assert(v.slice(0,p).every(x=>x<=v[p]));assert(v.slice(p+1).every(x=>x>=v[p]));
  assert.deepEqual(v.slice().sort((a,b)=>a-b),values.slice().sort((a,b)=>a-b));
  assert.deepEqual(out.ids.slice().sort(),values.map((_,i)=>'r'+i).sort());
  if(len>1){
    const k=1+random()%(len-1),a=values.slice();a.splice(0,k,...a.slice(0,k).sort((x,y)=>x-y));
    const frames=insertionTrace(a,k),last=frames.at(-1);
    assert(last.values.slice(0,k+1).every((x,i,s)=>i===0||s[i-1]<=x));
    assert.deepEqual(last.values.slice().sort((x,y)=>x-y),a.slice().sort((x,y)=>x-y));
    assert.deepEqual(last.ids.slice().sort(),a.map((_,i)=>'r'+i).sort());
  }
  checks++;
}
console.log(`PASS: exact examples and ${checks} generated inputs, with duplicate keys and record-identity checks`);