"use strict";
document.addEventListener("DOMContentLoaded", function () {
  const T=window.D020Trace;
  if(!T) throw new Error("D020Trace missing; trace.js must be loaded first");
  const $=id=>document.getElementById(id);
  const heap=T.heapTrace([5,3,8,2,7,1,6]);
  const merge=T.stableMergeTrace(
    [T.record(2,"甲"),T.record(5,"乙"),T.record(8,"戊")],
    [T.record(2,"丙"),T.record(6,"丁"),T.record(7,"己")]
  );
  const radix=T.radixTrace(
    [T.record(21,"A"),T.record(13,"B"),T.record(12,"C"),T.record(22,"D")],
    10,2
  );
  const pointers={heap:0,merge:0,radix:0};
  const make=(tag,cls,txt)=>{
    const e=document.createElement(tag);if(cls)e.className=cls;
    if(txt!==undefined&&txt!==null)e.textContent=String(txt);
    return e;
  };
  const drawCells=(id,items,option)=>{
    const root=$(id);root.replaceChildren();
    for(let i=0;i<items.length;i++){
      const entry=items[i],key=typeof entry==="number"?entry:entry.key;
      let cls="item";
      if(option&&option.active!==undefined&&i>=option.active)cls+=" sorted";
      if(option&&option.used!==undefined&&i<option.used)cls+=" used";
      if(option&&option.focus&&option.focus.includes(i))cls+=" focus";
      const el=make("div",cls);
      el.append(make("strong","",key));
      el.append(make("small","",typeof entry==="number"?"i="+i:entry.id));
      root.append(el);
    }
    if(!items.length)root.append(make("span","note","尚未写入记录"));
  };
  const controls=(name,len,refresh)=>{
    $(name+"-prev").addEventListener("click",()=>{
      pointers[name]=Math.max(0,pointers[name]-1);refresh();
    });
    $(name+"-next").addEventListener("click",()=>{
      pointers[name]=Math.min(len-1,pointers[name]+1);refresh();
    });
    $(name+"-reset").addEventListener("click",()=>{pointers[name]=0;refresh();});
    return ()=>{
      $(name+"-prev").disabled=pointers[name]===0;
      $(name+"-next").disabled=pointers[name]>=len-1;
    };
  };
  let heapButtons;
  const drawHeap=()=>{
    const s=heap.states[pointers.heap];
    drawCells("heap-array",s.values,{active:s.active,focus:s.focus||[]});
    const titles={input:"输入",swap:"单路径修复",subheap:"当前子树已修复",
      built:"建堆完成",extract:"提取最大值",repaired:"剩余堆恢复"};
    $("heap-state-title").textContent=titles[s.kind]||s.kind;
    $("heap-counter").textContent=(pointers.heap+1)+" / "+heap.states.length;
    $("heap-note").textContent=s.note;
    if(heapButtons)heapButtons();
  };
  heapButtons=controls("heap",heap.states.length,drawHeap);
  drawHeap();
  let mergeButtons;
  const drawMerge=()=>{
    const s=merge.states[pointers.merge];
    drawCells("merge-left",merge.left,{used:s.i,focus:s.i<merge.left.length?[s.i]:[]});
    drawCells("merge-right",merge.right,{used:s.j,focus:s.j<merge.right.length?[s.j]:[]});
    drawCells("merge-output",s.output,{});
    $("merge-state-title").textContent=s.kind==="start"?"归并初始状态":"本次选择："+(s.choice==="L"?"左列":"右列");
    $("merge-counter").textContent=(pointers.merge+1)+" / "+merge.states.length;
    $("merge-note").textContent=s.note;
    if(mergeButtons)mergeButtons();
  };
  mergeButtons=controls("merge",merge.states.length,drawMerge);
  drawMerge();
  let radixButtons;
  const drawRadix=()=>{
    const s=radix.states[pointers.radix];
    drawCells("radix-input",s.input,{});
    const grid=$("radix-buckets");grid.replaceChildren();
    for(let i=0;i<radix.base;i++){
      const b=make("div","bucket"+(s.focus===i?" focus":"")+
        (!s.buckets[i].length?" empty":""));
      b.append(make("b","", "桶 "+i));
      const contents=s.buckets[i].map(x=>x.key+"("+x.id+")").join(" → ");
      b.append(make("div","chain",contents||"—"));grid.append(b);
    }
    drawCells("radix-output",s.collected,{});
    const titles={start:"本轮开始",allocate:"按当前数位分配",collect:"按桶号稳定收集"};
    $("radix-state-title").textContent="第 "+(s.digit+1)+" 轮（"+
      (s.digit===0?"个位":s.digit===1?"十位":"第 "+(s.digit+1)+" 位")+"）· "+titles[s.kind];
    $("radix-counter").textContent=(pointers.radix+1)+" / "+radix.states.length;
    $("radix-note").textContent=s.note;
    if(radixButtons)radixButtons();
  };
  radixButtons=controls("radix",radix.states.length,drawRadix);
  drawRadix();
  for(const tab of document.querySelectorAll(".tab[data-target]")){
    tab.addEventListener("click",()=>{
      const dest=tab.dataset.target;
      for(const section of document.querySelectorAll(".lesson"))
        section.hidden=section.id!==dest;
      for(const each of document.querySelectorAll(".tab")){
        const on=each===tab;each.classList.toggle("is-active",on);each.setAttribute("aria-pressed",String(on));
      }
    });
  }
});
