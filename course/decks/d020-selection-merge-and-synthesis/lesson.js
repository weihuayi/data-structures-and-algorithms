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
    const panels=[...root.querySelectorAll(":scope > .tree-step-panel")];
    if(panels.length!==states.length){
      throw new Error("D020 "+name+" trace count mismatch: panels="+panels.length+
                      " states="+states.length);
    }
    // Each snapshot belongs to its own accessible panel. The common deck.js
    // step controller handles buttons, reset, disabled-state and visibility.
    panels.forEach((panel,index)=>{
      const state=states[index],o=describe(state);
      panel.innerHTML='<div class="d20-step-label">状态 '+(index+1)+
        '/'+states.length+' · '+htmlEscape(o.title)+'</div>'+
        '<div class="d20-live">'+o.html+
        '<p class="d20-view-note">'+htmlEscape(o.note)+'</p></div>';
    });
  }
  const m=T.stableMergeTrace(
    [T.record(2,"a"),T.record(5,"b"),T.record(8,"c")],
    [T.record(1,"d"),T.record(6,"e"),T.record(7,"f")]
  );
  viewer("merge",m.states,s=>({
    title:s.kind==="start"?"两个输入均已排序":"输出有序前缀不断延长",
    html:'<div class="d20-current-candidates">'
          +'<span>左侧指针 i='+s.i+'；当前候选 '+(s.i<m.left.length?htmlEscape(m.left[s.i].key+'('+m.left[s.i].id+')'):'已耗尽')+'</span>'
          +'<span>右侧指针 j='+s.j+'；当前候选 '+(s.j<m.right.length?htmlEscape(m.right[s.j].key+'('+m.right[s.j].id+')'):'已耗尽')+'</span>'
          +'</div><strong>已经确定的输出前缀</strong>'+cells(s.output),
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
