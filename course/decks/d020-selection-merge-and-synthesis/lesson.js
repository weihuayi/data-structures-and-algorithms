/* D020's two formal dynamic viewers. The verified algorithmic state lives in prototypes/trace.js. */
(function(){
 "use strict";
 function init(){
  const T=window.D020Trace;if(!T)return;
  const $=id=>document.getElementById(id);
  const htmlEscape=x=>String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  const cells=(arr,ids)=>'<div class="d20-cells" style="--n:'+Math.max(1,arr.length)+'">'+arr.map((r,i)=>{
    const v=typeof r==="number"?r:r.key;
    const id=typeof r==="number"?"i="+i:"id="+(r.id||ids&&ids[i]||"");
    return '<div class="d20-cell"><small>'+htmlEscape(id)+'</small><strong>'+htmlEscape(v)+'</strong></div>';
  }).join("")+'</div>';
  function viewer(name,states,describe){
    const root=$(name+"-viewer");if(!root)return;
    let index=0;
    const stage=$(name+"-stage"),content=$(name+"-state");
    const prev=$(name+"-prev"),next=$(name+"-next"),reset=$(name+"-reset");
    function draw(){
      const s=states[index],o=describe(s);
      stage.textContent="状态 "+(index+1)+"/"+states.length+" · "+o.title;
      content.innerHTML=o.html+'<p class="d20-view-note">'+htmlEscape(o.note)+'</p>';
      prev.disabled=index===0;next.disabled=index===states.length-1;
    }
    prev.addEventListener("click",()=>{index=Math.max(0,index-1);draw()});
    next.addEventListener("click",()=>{index=Math.min(states.length-1,index+1);draw()});
    reset.addEventListener("click",()=>{index=0;draw()});draw();
  }
  const m=T.stableMergeTrace(
    [T.record(2,"a"),T.record(5,"b"),T.record(8,"c")],
    [T.record(1,"d"),T.record(6,"e"),T.record(7,"f")]
  );
  viewer("merge",m.states,s=>({
    title:s.kind==="start"?"两个输入均已排序":"输出有序前缀不断延长",
    html:'<div class="d20-columns">'
          +'<div><strong>左侧已取 '+s.i+'/'+m.left.length+'</strong>'+cells(m.left.slice(s.i))+'</div>'
          +'<div><strong>右侧已取 '+s.j+'/'+m.right.length+'</strong>'+cells(m.right.slice(s.j))+'</div>'
          +'</div><strong>当前有序输出</strong>'+cells(s.output),
    note:s.note
  }));
  const r=T.radixTrace([T.record(21,"A"),T.record(13,"B"),
                       T.record(12,"C"),T.record(22,"D")],10,2);
  viewer("radix",r.states,s=>({
    title:"第 "+(s.digit+1)+" 轮 · "+(s.kind==="collect"?"收集":"稳定分配"),
    html:'<div class="d20-buckets">'+s.buckets.map((b,i)=>
      '<div class="d20-bucket '+(s.focus===i?'d20-focus':'')+'"><strong>桶 '+i+
      '</strong><div class="d20-bucket-list">'+(b.map(x=>htmlEscape(x.key+"("+x.id+")")).join(" → ")||"—")+'</div></div>'
    ).join("")+'</div><strong>本轮已收集记录</strong>'+cells(s.collected),
    note:s.note
  }));
 }
 if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
