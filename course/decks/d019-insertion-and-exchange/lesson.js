/* D019 stage-specific viewers. Algorithms and correctness checks live in prototypes/trace.js. */
(function(){
  'use strict';
  function init(){
    if(!window.D019Trace)return;
    const byId=id=>document.getElementById(id);
    const insertion=window.D019Trace.insertionTrace([2,6,7,5,1],3);
    const quick=window.D019Trace.partitionTrace([4,7,2,8,3,6,1]);
    function htmlCells(values,emptyAt,markedAt,state){
      return values.map((v,i)=>{
        const pointers=state&&Number.isInteger(state.low)?(i===state.low&&i===state.high?'low = high':i===state.low?'low':i===state.high?'high':''):'';
        return `<div class="d19-cell ${i===emptyAt?'d19-hole':i===markedAt?'d19-marked':''}"><span class="d19-index">${i}</span><strong>${v===null?'□':v}</strong>${pointers?`<span class="d19-pointer">${pointers}</span>`:''}</div>`;
      }).join('');
    }
    function viewer(prefix,states,describe){
      let step=0;
      const el=byId(prefix+'-array');if(!el)return;
      const prev=byId(prefix+'-prev'),next=byId(prefix+'-next'),reset=byId(prefix+'-reset');
      function draw(){
        const state=states[step];
        el.innerHTML=htmlCells(state.values,state.hole,-1,prefix==='quick'?state:null);
        byId(prefix+'-stage').textContent=`状态 ${step+1}/${states.length} · ${state.name}`;
        const info=describe(state);
        byId(prefix+'-held').textContent=info.held;
        byId(prefix+'-note').textContent=info.note;
        const scan=byId(prefix+'-next-scan');if(scan)scan.textContent=info.nextScan||'';
        prev.disabled=step===0;next.disabled=step===states.length-1;
      }
      prev.addEventListener('click',()=>{step=Math.max(0,step-1);draw()});
      next.addEventListener('click',()=>{step=Math.min(states.length-1,step+1);draw()});
      reset.addEventListener('click',()=>{step=0;draw()});
      draw();
    }
    viewer('ins',insertion,s=>({held:s.held?`暂存 x=${s.held.key}`:'暂存：无',note:s.explanation}));
    viewer('quick',quick.frames,s=>{
      const done=s.name==='枢轴归位',met=s.low===s.high;
      const side=s.hole===s.low?'low':'high';
      const nextScan=done?'划分完成：枢轴已归位。':met?'low = high：停止扫描，将暂存枢轴写回当前空位。':side==='low'?'空位在 low：接下来从 high 向左寻找小于枢轴的记录。':'空位在 high：接下来从 low 向右寻找大于枢轴的记录。';
      return {held:done?`枢轴已写回下标 ${s.low}`:`暂存枢轴 ${s.held.key}；low=${s.low}，high=${s.high}`,
              nextScan,
              note:done?'枢轴就位，左右区域分别满足大小关系，但各自仍需排序。':s.name==='暂存枢轴'?'首元素暂存并留下逻辑空位；下一步由另一端向中间寻找记录。':`当前帧：${s.name}；显示的是搬移并更新指针后的检查点，□ 代表逻辑空位。`};
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
