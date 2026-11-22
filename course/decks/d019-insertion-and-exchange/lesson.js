/* D019 stage-specific viewers. Algorithms and correctness checks live in prototypes/trace.js. */
(function(){
  'use strict';
  function init(){
    if(!window.D019Trace)return;
    const byId=id=>document.getElementById(id);
    const insertion=window.D019Trace.insertionTrace([2,4,7,3,6],3);
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
    viewer('ins',insertion,s=>({held:s.held?`暂存 x=${s.held.key}（${s.held.id}）`:'临时变量：无',note:s.explanation}));
    viewer('quick',quick.frames,s=>({held:s.held?`枢轴暂存：${s.held.key}；指针 ${s.low}, ${s.high}`:`枢轴已写回；下标 ${s.low}`,note:(s.name==='枢轴归位'?'枢轴已经就位，左侧 ≤ 枢轴 ≤ 右侧；内部还需要递归排序。':`low=${s.low}，high=${s.high}；移动填补逻辑空位，保持左 ≤ 枢轴、右 ≥ 枢轴。`)}));
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
