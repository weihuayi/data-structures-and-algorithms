/* UI behavior for the three review pages. The shared deck.js handles navigation. */
(function(){
 'use strict';
 const byId=id=>document.getElementById(id);
 const trace=window.D019Trace.insertionTrace([2,4,7,3,6],3);
 const partition=window.D019Trace.partitionTrace([5,9,3,8,2,7,4,6,1]);
 let step=0;
 function cells(values,marker){return values.map((v,i)=>`<div class="d019-slot ${i===marker?'hole':''}"><span class="index">下标 ${i}</span><strong>${v===null?'□':v}</strong></div>`).join('');}
 function draw(){const state=trace[step];byId('ins-stage').textContent=`状态 ${step+1}/${trace.length} · ${state.name}`;byId('ins-held').textContent=state.held===null?'临时变量：无':`临时变量：x=${state.held.key}`;byId('ins-array').innerHTML=cells(state.values,state.hole);byId('ins-note').textContent=state.explanation;byId('ins-prev').disabled=step===0;byId('ins-next').disabled=step===trace.length-1;}
 byId('ins-prev').addEventListener('click',()=>{step--;draw()});byId('ins-next').addEventListener('click',()=>{step++;draw()});byId('ins-reset').addEventListener('click',()=>{step=0;draw()});
 byId('partition-input').innerHTML=cells([5,9,3,8,2,7,4,6,1],-1);
 byId('partition-output').innerHTML=partition.values.map((v,i)=>`<div class="d019-slot ${i===partition.pivotIndex?'pivot':i<partition.pivotIndex?'left':'right'}"><span class="index">${i}</span><strong>${v}</strong></div>`).join('');
 byId('partition-index').textContent=String(partition.pivotIndex);
 window.D019Preview={trace,partition};draw();
})();