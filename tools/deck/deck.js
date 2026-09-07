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
if(typeof module!=='undefined')module.exports={pairTrace,MAZE,mazeStep,openNeighbors};
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
}
