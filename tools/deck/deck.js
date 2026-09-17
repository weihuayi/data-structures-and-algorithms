/* Shared interaction logic for repository-hosted classroom Decks. */
function pairTrace(values,target,mode){
 const items=values.map((v,id)=>({v,id}));
 if(mode==='sorted')items.sort((a,b)=>a.v-b.v||a.id-b.id);
 const states=[];let found=false;
 if(mode==='brute'){
  outer:for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++){
   const sum=items[i].v+items[j].v;const hit=sum===target;
   states.push({i,j,sum,hit,left:0,right:items.length-1,reason:hit?'找到一组，停止。':'这一对不满足，继续检查下一对。'});
   if(hit){found=true;break outer;}
  }
 }else{
  let i=0,j=items.length-1;
  while(i<j){const sum=items[i].v+items[j].v,hit=sum===target;
   states.push({i,j,sum,hit,left:i,right:j,reason:hit?'找到一组，停止。':sum<target?'和太小：当前左端与范围内任何价格相加都不够，排除左端。':'和太大：当前右端与范围内任何价格相加都超出，排除右端。'});
   if(hit){found=true;break;} if(sum<target)i++;else j--;
  }
 }
 return{items,states,found};
}
const MAZE=['#########','#S....#G#','#.###.#.#','#.#...#.#','#.#####.#','#.......#','#########'];
function mazeStep(pos,dr,dc){const r=pos[0]+dr,c=pos[1]+dc;return MAZE[r]&&MAZE[r][c]&&MAZE[r][c]!=='#'?[r,c]:pos;}
function openNeighbors(r,c){return [[r-1,c],[r+1,c],[r,c-1],[r,c+1]].filter(([x,y])=>x>=0&&x<MAZE.length&&y>=0&&y<MAZE[0].length&&MAZE[x][y]!=='#');}
/* data-mem: continuous memory strip traces (pure logic, no DOM). */
function memInsertTrace(values,pos,value){
 const n=values.length,moves=n-pos+1,steps=[];
 const base=values.map((v,id)=>({v,id}));
 const framed=()=>base.concat([null]);
 steps.push({cells:framed(),msg:`新同学 ${value} 要按学号插到第 ${pos} 位。先预测：需要搬动几个人？`});
 steps.push({cells:framed(),hi:[...Array(moves)].map((_,k)=>pos-1+k),count:0,msg:moves?`第 ${pos} 位到第 ${n} 位共 ${moves} 个人都要后移一位（n − i + 1 = ${n} − ${pos} + 1 = ${moves}）。从最后一个人开始搬，才不会覆盖还没搬走的元素。`:`第 ${pos} 位就是队尾，没有人需要搬。`});
 const cells=framed();
 for(let k=0;k<moves;k++){
  const from=n-1-k;
  cells[from+1]=cells[from];cells[from]=null;
  steps.push({cells:cells.slice(),hi:[from+1],count:k+1,msg:`${cells[from+1].v} 后移一位，腾出它原来的位置。`});
 }
 cells[pos-1]={v:value,id:'new'};
 steps.push({cells:cells.slice(),hi:[pos-1],count:moves,msg:`${value} 入住第 ${pos} 位，共搬运 ${moves} 次。不变量恢复：第 i 个元素恒在 base + (i − 1) × L。`});
 return steps;
}
function memDeleteTrace(values,pos){
 const n=values.length,moves=n-pos,steps=[];
 const base=values.map((v,id)=>({v,id}));
 steps.push({cells:base.slice(),msg:`删除第 ${pos} 位的 ${base[pos-1].v}。先预测：需要搬动几个人？`});
 steps.push({cells:base.slice(),hi:[pos-1],count:0,msg:moves?`${base[pos-1].v} 离开，空出第 ${pos} 位。其后 ${moves} 个人都要前移补位（n − i = ${n} − ${pos} = ${moves}）。`:`${base[pos-1].v} 就在队尾，直接离开，没有人需要搬。`});
 const cells=base.slice();cells[pos-1]=null;
 for(let k=0;k<moves;k++){
  const from=pos+k;
  cells[from-1]=cells[from];cells[from]=null;
  steps.push({cells:cells.slice(),hi:[from-1],count:k+1,msg:`${cells[from-1].v} 前移一位，补上左边的空位。`});
 }
 steps.push({cells:cells.filter(Boolean),count:moves,msg:`补位完成，共搬运 ${moves} 次。元素仍然一个接一个，物理连续的不变量恢复。`});
 return steps;
}
function memAccessTrace(values,i,mode){
 const base=1000,L=4,steps=[];
 const cells=values.map((v,id)=>({v,id,addr:base+id*L}));
 if(mode==='direct'){
  steps.push({cells,msg:`要取 a[${i}] 的值。有了地址公式，需要几次操作？`});
  steps.push({cells,hi:[i],count:1,msg:`LOC = ${base} + ${i} × ${L} = ${base+i*L}：一次乘法、一次加法，直接定位，a[${i}] = ${values[i]}。换成第 100 万个元素，也同样是一次计算。`});
 }else{
  steps.push({cells,msg:`假如没有地址公式，只能从头逐个找 a[${i}]。先预测：要检查几个元素？`});
  for(let k=0;k<=i;k++){
   steps.push({cells,hi:[k],seen:[...Array(k)].map((_,x)=>x),count:k+1,msg:k<i?`检查 a[${k}]：不是要取的，继续下一个。`:`检查 a[${k}]：找到了。共检查 ${i+1} 个——找得越靠后，代价越大。`});
  }
 }
 return steps;
}
function memExpandTrace(values){
 const n=values.length,cap2=n*2,steps=[];
 const old=values.map((v,id)=>({v,id}));
 steps.push({old:old.slice(),fresh:null,msg:`8 个位置住满了（8 / 8）。第 9 位新同学 117 来了，还能住下吗？`});
 steps.push({old:old.slice(),fresh:null,hiOld:true,msg:`住不下——原来的地块周围可能已被占满，不能扒别人的房子，只能另找一块更大的地。`});
 steps.push({old:old.slice(),fresh:Array(cap2).fill(null),count:0,msg:`申请一块容量翻倍的新地块（16 个位置），开始整体搬迁。`});
 const cur=old.slice(),fresh=Array(cap2).fill(null);
 for(let k=0;k<n;k++){
  fresh[k]=cur[k];cur[k]=null;
  steps.push({old:cur.slice(),fresh:fresh.slice(),count:k+1,msg:`${fresh[k].v} 搬到新地块的第 ${k+1} 位。`});
 }
 steps.push({old:cur.slice(),fresh:fresh.slice(),count:n,released:true,msg:`全部搬完（共 ${n} 次），旧地块释放。`});
 fresh[n]={v:117,id:'new'};
 steps.push({old:cur.slice(),fresh:fresh.slice(),count:n,released:true,hi:[n],msg:`117 入住新地块。一次搬 ${n} 个看似昂贵，但接下来 ${n-1} 次新同学到来都不用再搬——高代价被平摊到多次插入中。`});
 return steps;
}
function memCacheTrace(n,lineSize){
 const steps=[];
 let contFetch=0,contHit=0;
 steps.push({k:-1,contFetch,contHit,scatFetch:0,msg:`依次访问 a[0] 到 a[${n-1}]。取内存很慢，所以每次都会把目标所在的一整行（连续 ${lineSize} 个元素）取进缓存。先预测：两种布局各要取几次内存？`});
 for(let k=0;k<n;k++){
  const miss=k%lineSize===0;
  if(miss)contFetch++;else contHit++;
  steps.push({k,miss,contFetch,contHit,scatFetch:k+1,msg:miss?`访问 a[${k}]：缓存里没有，取回整行——a[${k}] 到 a[${Math.min(k+lineSize-1,n-1)}] 一起进缓存。分散布局每个元素各占一行，也得取一次。`:`访问 a[${k}]：它已经随上一行进缓存了，命中！分散布局仍要再取一次内存。`});
 }
 steps.push({k:n,done:true,contFetch,contHit,scatFetch:n,msg:`同样的 ${n} 次访问：连续布局取内存 ${contFetch} 次、命中 ${contHit} 次；分散布局取内存 ${n} 次。这就是科学计算偏爱连续布局的深层原因。`});
 return steps;
}
if(typeof module!=='undefined')module.exports={pairTrace,MAZE,mazeStep,openNeighbors,memInsertTrace,memDeleteTrace,memAccessTrace,memExpandTrace,memCacheTrace};
if(typeof document!=='undefined'){
 const slides=[...document.querySelectorAll('.slide')];
 let current=0;
 const select=document.getElementById('slide-select');
 slides.forEach((s,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${String(i+1).padStart(2,'0')} · ${s.dataset.title}`;select.append(o);});
 function show(n,scroll=true){current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));select.value=current;document.getElementById('page').textContent=`${current+1} / ${slides.length}`;document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===slides.length-1;document.getElementById('progress').style.width=`${100*(current+1)/slides.length}%`;history.replaceState(null,'',`#slide-${current+1}`);if(scroll){if(document.body.classList.contains('reading'))slides[current].scrollIntoView({block:'start'});else document.querySelector('main').scrollTo(0,0);}}
 document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);select.onchange=()=>show(Number(select.value));
 document.getElementById('read').onclick=()=>{document.body.classList.toggle('reading');document.getElementById('read').textContent=document.body.classList.contains('reading')?'翻页讲授':'连续阅读';show(current);};
 document.addEventListener('keydown',e=>{if(/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();show(current+1);}if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();show(current-1);}if(e.key==='Home'){e.preventDefault();show(0);}if(e.key==='End'){e.preventDefault();show(slides.length-1);}});
 const hash=location.hash.match(/^#slide-(\d+)$/);show(hash?Number(hash[1])-1:0,false);
 document.querySelectorAll('[data-pair]').forEach(root=>{
  const mode=root.dataset.pair;let step=-1;let phase=0;let trace;
  const presets=[{a:[18,7,25,12,33,20],t:32},{a:[18,7,25,12,33,20],t:100},{a:[16,16],t:32},{a:[16],t:32},{a:[7,12,18,20,25,33],t:37}];
  const choice=root.querySelector('select');
  function render(){const s=trace.states[step];const staged=mode==='sorted';const excluded=s&&!s.hit&&phase===1?(s.sum<presets[choice.value].t?s.i:s.j):-1;
   root.querySelector('.tiles').innerHTML=trace.items.map((x,k)=>`<div class="tile ${s&&(k===s.i||k===s.j)?'pick':''} ${s&&(k<s.left||k>s.right)?'out':''} ${k===excluded?'excluded':''}">${x.v}<small>位置 ${k} · 编号 ${x.id}</small></div>`).join('');
   const ended=step===trace.states.length-1&&!trace.found;
   root.querySelector('.status').textContent=s?`已检查 ${step+1} 对：${trace.items[s.i].v} + ${trace.items[s.j].v} = ${s.sum}。${staged&&phase===0?'请判断下一步；先说出依据。':s.reason}${ended&&(!staged||phase===1)?' 所有候选已排除，没有解。':''}`:trace.states.length?`目标 ${presets[choice.value].t} 元。先预测下一对，再点击“下一步”。已检查 0 对。`:'不足两件商品，没有可检查的配对。已检查 0 对。';
   const bridge=root.querySelector('.pair-bridge');
   if(bridge){let text='有序价格记为 a[k]；k 是当前位置，原编号随商品保存。';if(s&&phase===0)text=`L = ${s.i}，R = ${s.j}。当前范围内，a[L] 最小，a[R] 最大。`;if(s&&phase===1){const t=presets[choice.value].t;text=s.hit?`数学条件：a[L] + a[R] = ${t}，且 L < R。程序动作：返回这一对；原商品编号为 ${trace.items[s.i].id}、${trace.items[s.j].id}。`:s.sum<t?`对 L < k ≤ R：a[L] + a[k] ≤ ${s.sum} < ${t}。排除位置 L = ${s.i} 与剩余其他位置的所有配对。程序动作：++left。`:`对 L ≤ k < R：a[k] + a[R] ≥ ${s.sum} > ${t}。排除位置 R = ${s.j} 与剩余其他位置的所有配对。程序动作：--right。`; }bridge.textContent=text;}
   root.querySelector('[data-next]').disabled=trace.states.length===0||(step>=trace.states.length-1&&(!staged||phase===1));root.querySelector('[data-next]').textContent=staged&&step>=0&&phase===0?'揭示依据':staged&&step>=0?'执行并检查下一对':'下一步';root.querySelector('[data-prev]').disabled=step<0;
  }
  function reset(){const p=presets[choice.value];trace=pairTrace(p.a,p.t,mode);step=-1;phase=0;render();}
  choice.onchange=reset;root.querySelector('[data-next]').onclick=()=>{if(mode==='sorted'&&step>=0&&phase===0)phase=1;else if(step<trace.states.length-1){step++;phase=0;}render();};root.querySelector('[data-prev]').onclick=()=>{if(mode==='sorted'&&phase===1)phase=0;else{step--;phase=mode==='sorted'&&step>=0?1:0;}render();};root.querySelector('[data-reset]').onclick=reset;reset();
 });
 document.querySelectorAll('[data-map]').forEach(root=>{
  let selected=[1,1];const encoded=root.dataset.map==='encoded';
  const grid=root.querySelector('.map-grid');
  function draw(){const [r,c]=selected;const nearby=MAZE[r][c]==='#'?[]:openNeighbors(r,c);
   grid.innerHTML='<span class="axis">r / c</span>'+[...MAZE[0]].map((_,c)=>`<span class="axis">${c}</span>`).join('')+MAZE.map((row,r0)=>`<span class="axis">${r0}</span>`+[...row].map((v,c0)=>{const sel=r===r0&&c===c0,neighbor=nearby.some(([x,y])=>x===r0&&y===c0);return `<button class="map-cell ${v==='#'?'wall':''} ${sel?'selected':''} ${neighbor?'neighbor':''}" data-r="${r0}" data-c="${c0}" aria-label="选择位置 ${r0},${c0}，${v==='#'?'障碍':'可通行'}" aria-pressed="${sel}">${encoded?(v==='#'?'0':'1'):(sel?'●':v==='S'?'起':v==='G'?'终':'')}</button>`;}).join('')).join('');
   root.querySelector('.map-position').textContent=`位置 (r, c) = (${r}, ${c})`;
   root.querySelector('.map-value').textContent=`grid[${r}][${c}] = ${MAZE[r][c]==='#'?0:1} → ${MAZE[r][c]==='#'?'障碍':'可通行'}`;
   root.querySelector('.map-neighbors').textContent=MAZE[r][c]==='#'?'所选格子是障碍，不作为路径上的位置。':`可走到：${nearby.map(([r,c])=>`(${r}, ${c})`).join('、')||'无'}`;
   if(root.querySelector('.map-row'))root.querySelector('.map-row').textContent=`grid[${r}] = {${[...MAZE[r]].map(v=>v==='#'?0:1).join(', ')}}`;
  }
  grid.addEventListener('click',e=>{const b=e.target.closest('button[data-r]');if(b){selected=[Number(b.dataset.r),Number(b.dataset.c)];draw();grid.querySelector(`[data-r="${selected[0]}"][data-c="${selected[1]}"]`).focus();}});draw();
 });
 document.querySelectorAll('[data-maze]').forEach(root=>{
  let path=[[1,1]];
  function draw(msg='每次只能上下左右走一格。请先预测下一步。'){
   const p=path[path.length-1];root.querySelector('.maze').innerHTML=MAZE.flatMap((row,r)=>[...row].map((v,c)=>{const seen=path.some(q=>q[0]===r&&q[1]===c),cur=p[0]===r&&p[1]===c;return `<div class="cell ${v==='#'?'wall':''} ${seen?'path':''} ${cur?'current':''} ${v==='S'?'start':''} ${v==='G'?'goal':''}" aria-label="第${r}行第${c}列${v==='#'?'障碍':v==='G'?'出口':cur?'当前位置':'通道'}">${cur?'●':v==='S'?'起':v==='G'?'终':''}</div>`;})).join('');
   root.querySelector('.maze-info').textContent=MAZE[p[0]][p[1]]==='G'?`到达出口，共走 ${path.length-1} 步。你能说明为什么这条路有效吗？`:msg;
  }
  root.querySelectorAll('[data-move]').forEach(b=>b.onclick=()=>{const p=path[path.length-1];if(MAZE[p[0]][p[1]]==='G')return;const [dr,dc]=b.dataset.move.split(',').map(Number);const q=mazeStep(p,dr,dc);if(q===p){draw('这里是墙，不能走。换一个方向试试。');return;}path.push(q);draw(`已走 ${path.length-1} 步。更接近出口了吗？还记得走过哪里吗？`);});
  root.querySelector('[data-maze-reset]').onclick=()=>{path=[[1,1]];draw();};
  root.querySelector('[data-maze-back]').onclick=()=>{if(path.length>1)path.pop();draw('回到上一步。下一次探索需要记住什么？');};draw();
 });
 document.querySelectorAll('[data-mem]').forEach(root=>{
  const mode=root.dataset.mem;
  const selects=[...root.querySelectorAll('select')];
  const zones=root.querySelector('.mem-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  const VALUES=[101,103,105,107,109,111,113,115];
  let step=0,steps=[];
  const tile=(c,cls,small)=>c?`<div class="tile ${cls||''}" data-mid="${c.id}">${c.v}${small?`<small>${small}</small>`:''}</div>`:'<div class="tile mem-slot"><span class="mem-ghost">0</span><small class="mem-ghost">a[0]</small></div>';
  const band=(title,inner,cls)=>`<div class="mem-band ${cls||''}"><p class="mem-title">${title}</p>${inner}</div>`;
  const strip=(cells,hi,seen,smallOf)=>`<div class="tiles">${cells.map((c,k)=>tile(c,[hi&&hi.includes(k)?'pick':'',seen&&seen.includes(k)?'out':''].join(' '),c&&smallOf?smallOf(c,k):'')).join('')}</div>`;
  function build(){
   if(mode==='insert'){const p=[[3,104],[1,100],[9,116]][Number(selects[0].value)];steps=memInsertTrace(VALUES,p[0],p[1]);}
   else if(mode==='delete'){steps=memDeleteTrace(VALUES,[3,1,8][Number(selects[0].value)]);}
   else if(mode==='access'){steps=memAccessTrace([18,7,25,12,33,20,9,41],[0,4,7][Number(selects[0].value)],['direct','scan'][Number(selects[1].value)]);}
   else if(mode==='expand'){steps=memExpandTrace(VALUES);}
   else steps=memCacheTrace(8,4);
  }
  function render(){
   const s=steps[step];
   if(mode==='insert'||mode==='delete'){
    zones.innerHTML=strip(s.cells,s.hi,null,(c,k)=>`位置 ${k+1}`);
    counter.textContent=s.count==null?'':`已搬运 ${s.count} 次`;
   }else if(mode==='access'){
    zones.innerHTML=strip(s.cells,s.hi,s.seen,c=>`地址 ${c.addr}`);
    counter.textContent=s.count==null?'':(s.seen?`已检查 ${s.count} 个`:`地址计算 ${s.count} 次`);
   }else if(mode==='expand'){
    zones.innerHTML=band(`原地块 · 容量 8${s.released?'（已释放）':''}`,strip(s.old,s.hiOld?[...Array(8)].map((_,k)=>k):null,null,(c,k)=>`位置 ${k+1}`),s.released?'mem-old':'')+(s.fresh?band('新地块 · 容量 16',strip(s.fresh,s.hi,null,(c,k)=>`位置 ${k+1}`)):'');
    counter.textContent=s.count==null?'':`已搬迁 ${s.count} 个`;
   }else{
    const PRICES=[18,7,25,12,33,20,9,41];
    const contHtml=[0,1].map(li=>{
     const fetched=s.k>=li*4,isCur=s.k>=0&&s.k<8&&Math.floor(s.k/4)===li;
     const cls=['mem-line',fetched?'mem-cached':'',isCur&&s.miss?'mem-miss':''].join(' ');
     return `<div class="${cls}">${[0,1,2,3].map(j=>li*4+j).map(x=>tile({id:x,v:PRICES[x]},isCur&&x===s.k&&!s.miss?'mem-hit':'',`a[${x}]`)).join('')}</div>`;
    }).join('');
    const scatHtml=[...Array(8)].map((_,li)=>{
     const cls=['mem-line',s.k===li?'mem-miss':''].join(' ');
     return `<div class="${cls}">${tile({id:li,v:PRICES[li]},'',`a[${li}]`)}${tile(null)}${tile(null)}${tile(null)}</div>`;
    }).join('');
    zones.innerHTML=`<div class="mem-cache-grid">${band(`连续布局｜取内存 ${s.contFetch} 次 · 命中 ${s.contHit} 次`,contHtml)}${band('分散布局（预告链表）｜取内存 '+s.scatFetch+' 次',`<div class="mem-scat">${scatHtml}</div>`)}</div>`;
    counter.textContent='';
   }
   status.textContent=s.msg;
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  function draw(){
   const before=new Map();
   root.querySelectorAll('[data-mid]').forEach(el=>{const r=el.getBoundingClientRect();before.set(el.dataset.mid,[r.left,r.top]);});
   render();
   root.querySelectorAll('[data-mid]').forEach(el=>{
    const b=before.get(el.dataset.mid);if(!b)return;
    const r=el.getBoundingClientRect(),dx=b[0]-r.left,dy=b[1]-r.top;
    if(dx||dy){el.style.transition='none';el.style.transform=`translate(${dx}px,${dy}px)`;requestAnimationFrame(()=>{el.style.transition='';el.style.transform='';});}
   });
  }
  selects.forEach(sel=>sel.onchange=()=>{build();step=0;draw();});
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;draw();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;draw();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;draw();};
  build();draw();
 });
}
