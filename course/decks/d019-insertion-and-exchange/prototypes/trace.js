/* Deterministic, record-preserving teaching traces; no dependency on presentation DOM. */
(function(root){
  'use strict';
  function records(values){return values.map((key,i)=>({key,id:'r'+i}));}
  function sameIds(left,right){return left.map(x=>x.id).sort().join(',')===right.map(x=>x.id).sort().join(',');}
  function capture(a,held,initial,name,explanation,hole){
    const present=a.filter(x=>x!==null).concat(held===null?[]:[held]);
    if(!sameIds(present,initial))throw Error('Record identity not preserved');
    if(a.filter(x=>x===null).length!==(held===null?0:1))throw Error('Logical hole mismatch');
    return {name,explanation,values:a.map(x=>x===null?null:x.key),ids:a.map(x=>x===null?null:x.id),held:held===null?null:{key:held.key,id:held.id},hole};
  }
  function insertionTrace(values,position){
    if(!Array.isArray(values)||!Number.isInteger(position)||position<1||position>=values.length)throw Error('Invalid insertion input');
    const a=records(values),initial=a.slice(),out=[];
    if(!a.slice(0,position).every((v,i,s)=>i===0||s[i-1].key<=v.key))throw Error('Prefix must be sorted');
    out.push(capture(a,null,initial,'初始状态','前缀已经有序；准备插入下一条记录。',-1));
    const held=a[position];a[position]=null;let j=position;
    out.push(capture(a,held,initial,'暂存记录',`将 ${held.key} 保存到临时变量，原位置成为逻辑空位。`,j));
    while(j>0&&a[j-1].key>held.key){
      const moved=a[j-1];a[j]=moved;a[j-1]=null;j--;
      out.push(capture(a,held,initial,`记录 ${moved.key} 右移`,`${moved.key} > ${held.key}，记录右移，空位左移至下标 ${j}。`,j));
    }
    a[j]=held;
    if(!a.slice(0,position+1).every((v,i,s)=>i===0||s[i-1].key<=v.key))throw Error('Prefix is not sorted');
    out.push(capture(a,null,initial,'插入完成',`把暂存记录写回位置 ${j}；前 ${position+1} 条记录有序。`,-1));
    return out;
  }
  function partitionTrace(values){
    if(!Array.isArray(values)||values.length<1)throw Error('Partition needs at least one record');
    const a=records(values),orig=a.slice(),frames=[];
    const pivot=a[0];let low=0,high=a.length-1;
    function frame(name){
      const snapshot=capture(a,a.includes(pivot)?null:pivot,orig,name,'',a.includes(pivot)?-1:a.findIndex(x=>x===null));
      frames.push({...snapshot,low,high});
    }
    a[0]=null;frame('暂存枢轴');
    while(low<high){
      while(low<high&&a[high].key>=pivot.key)high--;
      if(low<high){a[low]=a[high];a[high]=null;frame('从右向左填补空位');}
      while(low<high&&a[low].key<=pivot.key)low++;
      if(low<high){a[high]=a[low];a[low]=null;frame('从左向右填补空位');}
    }
    a[low]=pivot;frame('枢轴归位');
    if(!a.slice(0,low).every(x=>x.key<=pivot.key)||!a.slice(low+1).every(x=>x.key>=pivot.key)||!sameIds(a,orig))throw Error('Partition postcondition failed');
    return {values:a.map(x=>x.key),ids:a.map(x=>x.id),pivotIndex:low,frames};
  }
  const api={insertionTrace,partitionTrace};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.D019Trace=api;
})(typeof window!=='undefined'?window:globalThis);