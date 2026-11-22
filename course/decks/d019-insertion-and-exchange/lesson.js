/* D019 stage-specific viewers. Algorithms and correctness checks live in prototypes/trace.js. */
(function(){
  'use strict';
  function init(){
    if(!window.D019Trace)return;
    const byId=id=>document.getElementById(id);
    const insertion=window.D019Trace.insertionTrace([2,6,7,5,1],3);
    const quick=window.D019Trace.partitionTrace([4,7,2,8,3,6,1]);
    function htmlCells(values,emptyAt,markedAt){
      return values.map((v,i)=>`<div class="d19-cell ${i===emptyAt?'d19-hole':i===markedAt?'d19-marked':''}"><span class="d19-index">${i}</span><strong>${v===null?'□':v}</strong></div>`).join('');
    }
    function viewer(prefix,states,describe){
      let step=0;
      const el=byId(prefix+'-array');if(!el)return;
      const prev=byId(prefix+'-prev'),next=byId(prefix+'-next'),reset=byId(prefix+'-reset');
      function draw(){
        const state=states[step];
        el.innerHTML=htmlCells(state.values,state.hole,-1);
        byId(prefix+'-stage').textContent=`状态 ${step+1}/${states.length} · ${state.name}`;
        const info=describe(state);
        byId(prefix+'-held').textContent=info.held;
        byId(prefix+'-note').textContent=info.note;
        prev.disabled=step===0;next.disabled=step===states.length-1;
      }
      prev.addEventListener('click',()=>{step=Math.max(0,step-1);draw()});
      next.addEventListener('click',()=>{step=Math.min(states.length-1,step+1);draw()});
      reset.addEventListener('click',()=>{step=0;draw()});
      draw();
    }
    viewer('ins',insertion,s=>({held:s.held?`暂存 x=${s.held.key}`:'暂存：无',note:s.explanation}));
    viewer('quick',quick.frames,s=>({held:s.held?`枢轴暂存：${s.held.key}；指针 ${s.low}, ${s.high}`:`枢轴已写回；下标 ${s.low}`,note:(s.name==='枢轴归位'?'枢轴已归位，左右区仍需排序。':s.name==='暂存枢轴'?`首记录已暂存；low=${s.low}、high=${s.high}，□ 为初始逻辑空位。`:`搬移并推进相应指针后：low=${s.low}、high=${s.high}；□ 标记新的逻辑空位。`)}));
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
