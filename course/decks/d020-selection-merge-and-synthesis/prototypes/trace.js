"use strict";
/* Pure D020 teaching traces; no DOM and no platform dependencies.
   Input records are copied. Sorting uses key; id preserves record identity. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.D020Trace = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function assertArray(a) {
    if (!Array.isArray(a) || !a.every(Number.isFinite)) throw new TypeError("Finite numeric key array required");
  }
  function validHeap(a, size) {
    const n = size === undefined ? a.length : size;
    if (!Number.isInteger(n) || n < 0 || n > a.length) return false;
    for (let i = 1; i < n; i++) if (a[(i - 1) >> 1] < a[i]) return false;
    return true;
  }
  function siftDown(a, start, size, report) {
    let i = start;
    while (2 * i + 1 < size) {
      let c = 2 * i + 1;
      if (c + 1 < size && a[c + 1] > a[c]) c++;
      if (a[i] >= a[c]) break;
      const t = a[i]; a[i] = a[c]; a[c] = t;
      report({kind:"swap", values:a.slice(), active:size, focus:[i,c],
        note:"下标 " + i + " 与较大的孩子 " + c + " 交换；潜在违反位置沿路径下移"});
      i = c;
    }
  }
  function heapTrace(input) {
    assertArray(input);
    const a = input.slice(), states = [], n = a.length;
    const push = s => states.push(s);
    push({kind:"input",values:a.slice(),active:n,focus:[],note:"原始数组。首先从最后一个非叶结点向前建堆。"});
    for (let i = Math.floor(n / 2)-1; i >= 0; i--) {
      // Child subtrees are heaps before processing i.
      siftDown(a,i,n,push);
      push({kind:"subheap",values:a.slice(),active:n,focus:[i],note:"结点 " + i + " 的子树已经是最大堆；上方结点未必已经合法。"});
    }
    const built = a.slice();
    push({kind:"built",values:a.slice(),active:n,focus:n?[0]:[],note:"建堆完成：整段数组满足最大堆性质。"});
    if (n > 1) {
      const t=a[0];a[0]=a[n-1];a[n-1]=t;
      push({kind:"extract",values:a.slice(),active:n-1,focus:[0,n-1],note:"根与最后一个有效元素交换；最右元素进入已排序后缀，暂时可能违反堆序。"});
      siftDown(a,0,n-1,push);
      push({kind:"repaired",values:a.slice(),active:n-1,focus:[0],note:"恢复有效前缀的堆序；右侧排序后缀不再参与堆操作。"});
    }
    return {states:states,built:built,afterExtract:a.slice(),activeAfter:Math.max(0,n-1)};
  }
  function rootDownCounterexample() {
    const a=[2,5,7,3,4,6,8], states=[];
    siftDown(a,0,a.length,s=>states.push(s));
    return {original:[2,5,7,3,4,6,8],result:a,stillInvalid:!validHeap(a),states:states};
  }
  function record(key,id) { return {key:key,id:String(id)}; }
  function checkRecords(a) {
    if (!Array.isArray(a)||!a.every(x=>x&&Number.isFinite(x.key)&&typeof x.id==="string")) {
      throw new TypeError("Records must have finite numeric key and string id");
    }
  }
  function stableMergeTrace(left,right) {
    checkRecords(left);checkRecords(right);
    const ordered = a=>a.every((v,i)=>!i||a[i-1].key<=v.key);
    if (!ordered(left)||!ordered(right)) throw new Error("Merge requires two sorted inputs");
    let i=0,j=0;
    const out=[],states=[];
    const capture=(kind,note,choice)=>states.push({kind:kind,i:i,j:j,output:out.slice(),choice:choice||"",
      note:note});
    capture("start","两个输入分别有序；每次比较各自未处理后缀的首元素。");
    while (i<left.length||j<right.length) {
      let takeLeft=j===right.length||(i<left.length&&left[i].key<=right[j].key);
      const v=takeLeft?left[i++]:right[j++];
      out.push({key:v.key,id:v.id});
      capture("take","取出 "+v.key+"（"+v.id+"）"+(takeLeft?"，来自左列":"，来自右列")+
        "；相等时优先取左列。",takeLeft?"L":"R");
    }
    return {states:states,result:out,left:left.slice(),right:right.slice()};
  }
  function radixTrace(input,base,digits) {
    checkRecords(input);
    if (!input.every(r=>Number.isSafeInteger(r.key)&&r.key>=0)) throw new Error("Radix keys must be nonnegative safe integers");
    base=base===undefined?10:base;
    if (!Number.isInteger(base)||base<2||base>36) throw new Error("Base must be 2..36");
    let a=input.map(r=>({key:r.key,id:r.id}));
    let max=Math.max(0,...a.map(r=>r.key)), need=1;
    while (max>=base) {max=Math.floor(max/base);need++;}
    digits=digits===undefined?need:digits;
    if (!Number.isInteger(digits)||digits<need) throw new Error("Digits too small");
    let all=[], rounds=[], divisor=1;
    for (let d=0; d<digits; d++) {
      const start=a.slice(), buckets=Array.from({length:base},()=>[]);
      all.push({kind:"start",digit:d,divisor:divisor,input:start, buckets:buckets.map(b=>b.slice()),collected:[],
        note:"第 "+(d+1)+" 轮：从低位起处理第 "+(d+1)+" 位。"});
      for(const r of start) {
        const b=Math.floor(r.key/divisor)%base;
        buckets[b].push(r);
        all.push({kind:"allocate",digit:d,divisor:divisor,input:start,buckets:buckets.map(x=>x.slice()),collected:[],focus:b,
          note:r.key+"（"+r.id+"）按本位数字 "+b+" 追加到桶尾；同桶先后不变。"});
      }
      a=buckets.flat();
      all.push({kind:"collect",digit:d,divisor:divisor,input:start,buckets:buckets.map(x=>x.slice()),collected:a.slice(),
        note:"按桶 0→"+(base-1)+" 从头到尾稳定收集。"});
      rounds.push(a.slice());divisor*=base;
    }
    return {states:all,rounds:rounds,result:a,base:base,digits:digits};
  }
  return {validHeap:validHeap,siftDown:siftDown,heapTrace:heapTrace,
    rootDownCounterexample:rootDownCounterexample,record:record,
    stableMergeTrace:stableMergeTrace,radixTrace:radixTrace};
});
