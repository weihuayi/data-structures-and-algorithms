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
/* data-link: linked list chain traces (pure logic, no DOM). */
const LINK_VALUES=[101,103,105,107,109,111,113,115];
const LINK_ADDRS=[100,316,208,452,128,604,388,540];
function linkBase(){return LINK_VALUES.map((v,k)=>({v,addr:LINK_ADDRS[k],next:k<LINK_VALUES.length-1?LINK_ADDRS[k+1]:null}));}
function linkAccessTrace(i){
 const nodes=linkBase(),steps=[];
 steps.push({nodes,counter:'',msg:`要取第 ${i+1} 项（学号 ${LINK_VALUES[i]}）。地址公式失效——每个结点住在哪，只有它的前驱知道。先预测：从 head 出发要走几步？`});
 for(let k=1;k<=i;k++){
  steps.push({nodes,cur:k,count:k,counter:`已走 ${k} 步`,msg:`走第 ${k} 步：当前结点 ${LINK_VALUES[k-1]} 的 next = ${LINK_ADDRS[k]}，沿指针到达第 ${k+1} 个结点 ${LINK_VALUES[k]}。`});
 }
 steps.push({nodes,cur:i,count:i,counter:`已走 ${i} 步`,msg:i?`到达第 ${i+1} 项，共走 ${i} 步。顺序表取同一项只要一次地址计算；取第 n 项要走 n − 1 步——链表的访问是 O(n)。`:`第 1 项就是 head 所指，走 0 步。但换成第 n 项，就要走 n − 1 步——访问是 O(n)。`});
 return steps;
}
function linkSmallBase(){
 return [{v:101,addr:100,next:316},{v:103,addr:316,next:452},{v:104,addr:208,next:null,state:'new'},{v:105,addr:452,next:null}];
}
function linkInsertTrace(order){
 const nodes=linkSmallBase(),steps=[];
 steps.push({nodes,counter:'',msg:'104 已 malloc 出生（@208），要插到 103 与 105 之间。先预测：要改哪两个链接？先改哪个，才不会出事？'});
 if(order==='correct'){
  steps.push({nodes,mod:{2:{next:452}},count:1,counter:'已改 1 个链接',msg:'第 1 步：s->next = p->next——104 先接上后继 105（@452）。此时 103 仍指向 105，链完好无损。'});
  steps.push({nodes,mod:{2:{next:452},1:{next:208}},count:2,counter:'已改 2 个链接',msg:'第 2 步：p->next = s——103 改指 104（@208）。插入完成。'});
  steps.push({nodes,mod:{2:{next:452},1:{next:208}},count:2,counter:'已改 2 个链接',msg:'共改 2 个链接，没有一个人搬家。不变量恢复：从 head 沿 next 走，恰好依次经过 101、103、104、105。'});
 }else{
  steps.push({nodes,mod:{1:{next:208},3:{state:'lost'}},count:1,counter:'已改 1 个链接',msg:'第 1 步：p->next = s——103 改指 104。危险已经发生：103 原本指向 105 的线索被覆盖，从 head 出发再也到不了 105。'});
  steps.push({nodes,mod:{1:{next:208},2:{next:208},3:{state:'lost'}},count:2,counter:'已改 2 个链接',msg:'第 2 步：s->next = p->next——但 p->next 现在已是 104 自己：104 指向了自己（自环）。'});
  steps.push({nodes,mod:{1:{next:208},2:{next:208},3:{state:'lost'}},count:2,counter:'已改 2 个链接',msg:'从 head 走：101 → 103 → 104 → 104 → … 死循环；105 及之后的结点永远丢失。断链是经典陷阱：唯一的线索被覆盖，后面的世界就消失了。正确顺序：先接后继，再改前驱。'});
 }
 return steps;
}
function linkDeleteTrace(mode){
 const nodes=[{v:101,addr:100,next:316},{v:103,addr:316,next:208},{v:104,addr:208,next:452},{v:105,addr:452,next:null}],steps=[];
 steps.push({nodes,counter:'',msg:'要删除 104。先预测：把 103 的 next 直接改过去，就完事了吗？'});
 if(mode==='complete'){
  steps.push({nodes,cur:2,counter:'',msg:'第 1 步：q = p->next——先用 q 记住 104 的地址（@208），它是找回这个结点的唯一线索。'});
  steps.push({nodes,mod:{1:{next:452}},cur:2,counter:'',msg:'第 2 步：p->next = q->next——103 跳过 104，改指 105（@452）。104 已不在链上，但 q 还握着它。'});
  steps.push({nodes,mod:{1:{next:452},2:{state:'freed'}},counter:'',msg:'第 3 步：free(q)——归还 104 占用的内存。删除完成：101 → 103 → 105，链干净，内存也干净。'});
 }else{
  steps.push({nodes,mod:{1:{next:452},2:{state:'orphan'}},counter:'',msg:'直接 p->next = p->next->next：103 跳过 104，改指 105（@452）。看上去完成了？'});
  steps.push({nodes,mod:{1:{next:452},2:{state:'orphan'}},counter:'',msg:'104 还占着内存，却已没有任何指针能找到它——无家可归的孤儿：内存泄漏。程序长期运行，内存会一点点漏光。正确做法：先用 q 记住，改完链接再 free(q)。'});
 }
 return steps;
}
/* data-stack / data-queue: restricted linear structure traces (pure logic, no DOM). */
function stackBracketsTrace(s){
 const match={')':'(',']':'[','}':'{'};
 const steps=[];const stack=[];let fail=false;
 steps.push({input:s,i:-1,stack:[],msg:`规则：遇到左括号压栈，遇到右括号弹栈核对。先预测：扫描 ${s}，能否全部配上？若不能，在第几个字符出事？`});
 for(let k=0;k<s.length;k++){
  const ch=s[k];
  if('([{'.includes(ch)){
   stack.push(ch);
   steps.push({input:s,i:k,stack:stack.slice(),count:stack.length,msg:`第 ${k+1} 个字符 '${ch}'：左括号，压栈。栈内 ${stack.length} 个，等待各自的右括号。`});
  }else if(!stack.length){
   steps.push({input:s,i:k,stack:[],fail:true,count:0,msg:`第 ${k+1} 个字符 '${ch}'：栈已空，没有左括号可与它配对——不匹配。`});
   fail=true;break;
  }else{
   const top=stack[stack.length-1];
   if(match[ch]===top){
    stack.pop();
    steps.push({input:s,i:k,stack:stack.slice(),count:stack.length,msg:`第 ${k+1} 个字符 '${ch}'：右括号，弹栈核对——栈顶 '${top}' 与 '${ch}' 正好配对。`});
   }else{
    steps.push({input:s,i:k,stack:stack.slice(),fail:true,count:stack.length,msg:`第 ${k+1} 个字符 '${ch}'：弹栈核对——栈顶是 '${top}'，与 '${ch}' 配不上！最近未配对者先闭合：'${ch}' 想找的是 '${top}' 的搭档。在第 ${k+1} 个字符处发现不匹配。`});
    fail=true;break;
   }
  }
 }
 if(!fail){
  steps.push(stack.length?{input:s,i:s.length-1,stack:stack.slice(),fail:true,count:stack.length,msg:`扫描完毕，栈内还剩 ${stack.length} 个左括号——它们没等到自己的右括号，不匹配。`}:{input:s,i:s.length-1,stack:[],ok:true,count:0,msg:'扫描完毕，栈空——每一对括号都是最近未配对者先闭合，全部配对成功。'});
 }
 return steps;
}
function plainQueueTrace(){
 const steps=[];const cells=Array(5).fill(null);
 steps.push({cells:cells.slice(),front:0,rear:0,counter:'',msg:'顺序队列：数组 + front + rear（容量 5），front 守队头、rear 指向下一个可住位置。先入队 A 到 E，再出队 2 个，然后再想入队——会发生什么？'});
 const vs=['A','B','C','D','E'];
 for(let k=0;k<5;k++){
  cells[k]=vs[k];
  steps.push({cells:cells.slice(),front:0,rear:k+1,count:k+1,counter:`队内 ${k+1} 个`,hi:k,msg:`enqueue ${vs[k]}：住进位置 ${k}，rear 走到 ${k+1}。`});
 }
 cells[0]=null;steps.push({cells:cells.slice(),front:1,rear:5,count:4,counter:'队内 4 个',msg:'dequeue：A 离开，front 走到 1。位置 0 空出来了。'});
 cells[1]=null;steps.push({cells:cells.slice(),front:2,rear:5,count:3,counter:'队内 3 个',msg:'dequeue：B 离开，front 走到 2。前部已空出 2 个位置。'});
 steps.push({cells:cells.slice(),front:2,rear:5,fail:true,count:3,counter:'队内 3 个',msg:'enqueue F：rear = 5 已顶到数组末尾，进不来——前部明明空着 2 个位置，新元素却无处安放。这就是假满。'});
 return steps;
}
function circQueueTrace(){
 const steps=[];const cells=Array(5).fill(null);
 steps.push({cells:cells.slice(),front:0,rear:0,counter:'',msg:'循环队列：牺牲一个单元，最多装 4 个；front、rear 从 0 出发，下标"到头就绕回"。先预测：入队 A、B、C、D 之后，(rear+1)%5 == front 成立吗？'});
 const vs=['A','B','C','D'];
 for(let k=0;k<4;k++){
  cells[k]=vs[k];
  const last=k===3;
  steps.push({cells:cells.slice(),front:0,rear:k+1,count:k+1,counter:`队内 ${k+1} 个`,hi:k,msg:last?'enqueue D：住进位置 3，rear 走到 4。判满：(4+1)%5 = 0 == front——已满（4 个元素，位置 4 被牺牲）。':`enqueue ${vs[k]}：住进位置 ${k}，rear 走到 ${k+1}。`});
 }
 cells[0]=null;steps.push({cells:cells.slice(),front:1,rear:4,count:3,counter:'队内 3 个',msg:'dequeue：A 离开，front 走到 1。'});
 cells[1]=null;steps.push({cells:cells.slice(),front:2,rear:4,count:2,counter:'队内 2 个',msg:'dequeue：B 离开，front 走到 2。前部空出位置 0、1——这次它们还能用上吗？'});
 cells[4]='E';steps.push({cells:cells.slice(),front:2,rear:0,count:3,counter:'队内 3 个',hi:4,msg:'enqueue E：住进位置 4，rear = (4+1)%5 = 0——到下标末尾，绕回开头！'});
 cells[0]='F';steps.push({cells:cells.slice(),front:2,rear:1,count:4,counter:'队内 4 个',hi:0,msg:'enqueue F：住进位置 0（前部空位重新用上了），rear 走到 1。判满：(1+1)%5 = 2 == front——再次判满。'});
 steps.push({cells:cells.slice(),front:2,rear:1,ok:true,count:4,counter:'队内 4 个',msg:'最终 front = 2、rear = 1，队内 C、D、E、F 共 4 个。取模把数组弯成环，前部空位重新可用——假满消失。'});
 return steps;
}
/* data-recur / data-hanoi: recursion traces (pure logic, no DOM). */
function recurFactorialTrace(n){
 const steps=[];
 const frame=k=>({label:`f(${k})`,n:k,ret:null});
 steps.push({frames:[],msg:`手工推演 factorial(${n}) 的栈生长与回退。先预测：压几帧？回退时各层依次返回什么？`});
 for(let k=n;k>=0;k--){
  const frames=[];for(let j=n;j>=k;j--)frames.push(frame(j));
  steps.push({frames,top:n-k,count:n-k+1,msg:k===n?`main 调用 factorial(${n})，压一帧。f(${n}) 需要 f(${n-1}) 的值，才能算 ${n} × f(${n-1})。`:k===0?`f(1) 需要 f(0)——压一帧。f(0) 到达出口 n == 0，不再深入。`:`f(${k+1}) 需要 f(${k}) 的值——压一帧。`});
 }
 let ret=1;
 for(let k=0;k<=n;k++){
  const prev=k===0?1:ret;
  if(k>0)ret=k*prev;
  const val=k===0?1:ret;
  const shown=[];for(let j=n;j>k;j--)shown.push(frame(j));
  steps.push({frames:shown,retFrame:{label:`f(${k})`,val},count:n-k,msg:k===0?`出口：f(0) = 1，弹帧。返回值 1 交给 f(1)。`:`f(${k}) = ${k} × f(${k-1}) = ${k} × ${prev} = ${val}，弹帧。${k===n?`栈空——main 拿到 ${val}。`:`返回值 ${val} 交给 f(${k+1})。`}`});
 }
 return steps;
}
function hanoiTrace(n){
 const pegs=[[],[],[]];
 for(let k=n;k>=1;k--)pegs[0].push(k);
 const names=['A','B','C'],steps=[];
 steps.push({pegs:pegs.map(p=>p.slice()),msg:`hanoi(${n})：把 ${n} 个盘子从 A 移到 C。先自己写出每一步，再用推演核对。`});
 let k=0;
 const total=2**n-1;
 function move(d,from,to){
  pegs[to].push(pegs[from].pop());k++;
  let phase='';
  if(n===3){
   if(k<=3)phase='（属于“把 2 盘整体移到 B”）';
   else if(k===4)phase='（最大盘落位）';
   else phase='（属于“把 2 盘整体移回 C”）';
  }
  steps.push({pegs:pegs.map(p=>p.slice()),disk:d,count:k,msg:`第 ${k} 步：盘 ${d} 从 ${names[from]} → ${names[to]}。${phase}`});
 }
 function solve(m,from,to,aux){
  if(m===0)return;
  solve(m-1,from,aux,to);
  move(m,from,to);
  solve(m-1,aux,to,from);
 }
 solve(n,0,2,1);
 steps.push({pegs:pegs.map(p=>p.slice()),ok:true,count:k,msg:`完成：共 ${k} 步 = 2^${n} − 1 = ${total}。${n===3?'第 1–3 步是“2 盘移到 B”，第 4 步最大盘落位，第 5–7 步是“2 盘移回 C”——整体法的三步结构，在轨迹里看得清清楚楚。':''}`});
 return steps;
}
/* data-match: BF / KMP pattern matching traces (pure logic, no DOM). */
function nextTable(T){
 const m=T.length,next=Array(m+1).fill(0);
 for(let j=2;j<=m;j++){
  let l=0;
  for(let k=1;k<=j-2;k++)if(T.slice(0,k)===T.slice(j-1-k,j-1))l=k;
  next[j]=l+1;
 }
 return next;
}
function matchTrace(S,T,mode){
 const n=S.length,m=T.length,steps=[];
 let cmp=0;
 if(mode==='bf'){
  steps.push({i:1,j:1,start:1,cmp:0,msg:`BF：主串指针 i、模式指针 j，起点从 1 到 ${n-m+1}。失配时 i 退回下一个起点、j 回 1。先预测：一共几趟？每趟比几次？`});
  for(let start=1;start<=n-m+1;start++){
   let j=1,i=start;
   while(j<=m){
    cmp++;
    const equal=S[i-1]===T[j-1];
    steps.push({i,j,start,cmp,hit:equal,msg:equal?`第 ${start} 趟：S[${i}] = '${S[i-1]}' 与 T[${j}] = '${T[j-1]}' 相等，i、j 各进一步。`:`第 ${start} 趟：S[${i}] = '${S[i-1]}' ≠ T[${j}] = '${T[j-1]}'，失配——这一趟比出来的 ${j-1} 个字符全部作废，i 退回 ${start+1}，j 回 1。`});
    if(!equal)break;
    i++;j++;
   }
   if(j>m){
    steps.push({i:i-1,j:m,start,cmp,ok:true,msg:`j 越界——匹配成功，位置 = ${start}。共 ${cmp} 次比较。`});
    return steps;
   }
  }
  steps.push({i:n,j:1,start:n-m+1,cmp,fail:true,msg:`剩下的字符不够 ${m} 个了——匹配失败。共 ${cmp} 次比较。`});
 }else{
  const next=nextTable(T);
  steps.push({i:1,j:1,start:1,cmp:0,msg:'KMP：失配时 i 不动，j = next[j]；j = 0 时 i、j 各进一步。先预测：i 会回头吗？共比几次？'});
  let i=1,j=1;
  while(i<=n){
   if(j===0){steps.push({i,j:1,start:i,cmp,msg:'j 退到 0：连首字符都对不上——i、j 各进一步。'});i++;j=1;continue;}
   cmp++;
   const equal=S[i-1]===T[j-1];
   if(equal){
    steps.push({i,j,start:i-j+1,cmp,hit:true,msg:`S[${i}] = '${S[i-1]}' 与 T[${j}] = '${T[j-1]}' 相等，i、j 各进一步。`});
    i++;j++;
    if(j>m){steps.push({i:i-1,j:m,start:i-m,cmp,ok:true,msg:`j 越界——匹配成功，位置 = ${i-m}。共 ${cmp} 次比较；i 从 1 走到 ${i-1}，一次头也没回。`});return steps;}
   }else{
    const nj=next[j];
    steps.push({i,j,start:i-j+1,cmp,hit:false,msg:`S[${i}] = '${S[i-1]}' ≠ T[${j}] = '${T[j-1]}'，失配——i 停在 ${i} 不动，j = next[${j}] = ${nj}：模式向右滑，前缀对准已确认相等的部分。`});
    j=nj;
   }
  }
  steps.push({i:n,j,cmp,fail:true,msg:`主串走完——匹配失败。共 ${cmp} 次比较。`});
 }
 return steps;
}
if(typeof module!=='undefined')module.exports={pairTrace,MAZE,mazeStep,openNeighbors,memInsertTrace,memDeleteTrace,memAccessTrace,memExpandTrace,memCacheTrace,linkAccessTrace,linkInsertTrace,linkDeleteTrace,stackBracketsTrace,plainQueueTrace,circQueueTrace,recurFactorialTrace,hanoiTrace,nextTable,matchTrace};
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
 document.querySelectorAll('[data-link]').forEach(root=>{
  const mode=root.dataset.link;
  const selects=[...root.querySelectorAll('select')];
  const zones=root.querySelector('.link-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  let step=0,steps=[];
  function build(){
   if(mode==='access')steps=linkAccessTrace([0,3,7][Number(selects[0].value)]);
   else if(mode==='insert')steps=linkInsertTrace(['correct','wrong'][Number(selects[0].value)]);
   else steps=linkDeleteTrace(['complete','leak'][Number(selects[0].value)]);
  }
  function render(){
   const s=steps[step];
   const nodes=s.nodes.map((n,k)=>Object.assign({},n,(s.mod&&s.mod[k])||{}));
   const chip=n=>{
    if(n.next==null)return n.state==='new'?'<span class="link-arrow">→ —</span>':'<span class="link-arrow">→ NULL</span>';
    if(n.next===n.addr)return '<span class="link-arrow link-broken">↺ 自环</span>';
    return `<span class="link-arrow">→ @${n.next}</span>`;
   };
   zones.innerHTML=`<div class="link-chain"><span class="link-head">head</span><span class="link-arrow">→ @${nodes[0].addr}</span>`+nodes.map((n,k)=>{
    const cls=['tile',k===s.cur?'pick':'',n.state?`link-${n.state}`:''].join(' ');
    return `<div class="${cls}">${n.v}<small>地址 @${n.addr}</small></div>${chip(n)}`;
   }).join('')+'</div>';
   counter.textContent=s.counter||'';
   status.textContent=s.msg;
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  selects.forEach(sel=>sel.onchange=()=>{build();step=0;render();});
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;render();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;render();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;render();};
  build();render();
 });
 document.querySelectorAll('[data-stack]').forEach(root=>{
  const select=root.querySelector('select');
  const zones=root.querySelector('.stack-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  const STRS=['({[}]','({[]})','(()'];
  let step=0,steps=[];
  function render(){
   const s=steps[step];
   const inHtml=[...s.input].map((ch,k)=>`<div class="tile stack-char ${k===s.i?'pick':''} ${k<s.i?'out':''}">${ch}</div>`).join('');
   const stackHtml=s.stack.length?s.stack.map(ch=>`<div class="tile">${ch}</div>`).join(''):'<div class="tile mem-slot"><span class="mem-ghost">(</span></div>';
   zones.innerHTML=`<p class="mem-title">输入串</p><div class="tiles">${inHtml}</div><p class="mem-title">栈（左底右顶）</p><div class="link-chain"><span class="link-head">栈底</span>${stackHtml}<span class="link-arrow">← 栈顶</span></div>`;
   counter.textContent=s.count==null?'':`栈内 ${s.count} 个`;
   status.textContent=s.msg;
   status.classList.toggle('status-fail',!!s.fail);
   status.classList.toggle('status-ok',!!s.ok);
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  select.onchange=()=>{steps=stackBracketsTrace(STRS[Number(select.value)]);step=0;render();};
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;render();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;render();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;render();};
  steps=stackBracketsTrace(STRS[0]);render();
 });
 document.querySelectorAll('[data-queue]').forEach(root=>{
  const mode=root.dataset.queue;
  const zones=root.querySelector('.queue-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  const steps=mode==='plain'?plainQueueTrace():circQueueTrace();
  let step=0;
  function render(){
   const s=steps[step];
   zones.innerHTML='<div class="tiles">'+s.cells.map((c,k)=>{
    const marks=[k===s.front?'front':'',k===s.rear?'rear':''].filter(Boolean).join(' · ');
    const small=`位置 ${k}${marks?`<br><span class="queue-mark">▲ ${marks}</span>`:''}`;
    return c?`<div class="tile ${k===s.hi?'pick':''}">${c}<small>${small}</small></div>`:`<div class="tile mem-slot"><span class="mem-ghost">0</span><small>${small}</small></div>`;
   }).join('')+'</div>';
   counter.textContent=s.counter||'';
   status.textContent=s.msg;
   status.classList.toggle('status-fail',!!s.fail);
   status.classList.toggle('status-ok',!!s.ok);
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;render();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;render();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;render();};
  render();
 });
 document.querySelectorAll('[data-recur]').forEach(root=>{
  const zones=root.querySelector('.recur-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  const steps=recurFactorialTrace(4);
  let step=0;
  function render(){
   const s=steps[step];
   const framesHtml=s.frames.length?s.frames.map(f=>`<div class="tile recur-frame">${f.label}</div>`).join(''):'<div class="tile mem-slot"><span class="mem-ghost">f</span></div>';
   const retHtml=s.retFrame?`<div class="tile pick recur-ret">${s.retFrame.label}<small>返回 ${s.retFrame.val}</small></div>`:'';
   zones.innerHTML=`<div class="link-chain"><span class="link-head">栈底</span>${framesHtml}<span class="link-arrow">← 栈顶</span>${retHtml}</div>`;
   counter.textContent=s.count==null?'':`栈内 ${s.count} 帧`;
   status.textContent=s.msg;
   status.classList.toggle('status-ok',step===steps.length-1);
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;render();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;render();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;render();};
  render();
 });
 document.querySelectorAll('[data-hanoi]').forEach(root=>{
  const select=root.querySelector('select');
  const zones=root.querySelector('.hanoi-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  const names=['A','B','C'];
  let step=0,steps=[];
  function render(){
   const s=steps[step];
   zones.innerHTML='<div class="hanoi-pegs">'+s.pegs.map((peg,p)=>{
    const disks=peg.map(d=>`<div class="hanoi-disk ${d===s.disk&&peg[peg.length-1]===d?'hanoi-moved':''}" style="width:${26+d*22}px"></div>`).join('');
    return `<div class="hanoi-peg"><div class="hanoi-stack">${disks}</div><span class="hanoi-name">${names[p]}</span></div>`;
   }).join('')+'</div>';
   counter.textContent=s.count==null?'':`已移 ${s.count} 步`;
   status.textContent=s.msg;
   status.classList.toggle('status-ok',!!s.ok);
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  select.onchange=()=>{steps=hanoiTrace([3,2][Number(select.value)]);step=0;render();};
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;render();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;render();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;render();};
  steps=hanoiTrace(3);render();
 });
 document.querySelectorAll('[data-match]').forEach(root=>{
  const fixed=root.dataset.match;
  const selects=[...root.querySelectorAll('select')];
  const zones=root.querySelector('.match-zones'),status=root.querySelector('.status'),counter=root.querySelector('.mem-counter');
  const S=fixed==='bf'?'abcdefghi':'abaabaabcde',T=fixed==='bf'?'abcdx':'abaabc',n=S.length;
  let step=0,steps=[];
  function build(){steps=matchTrace(S,T,fixed==='bf'?'bf':['kmp','bf'][Number(selects[0].value)]);}
  function render(){
   const s=steps[step];
   const cells=[];
   for(let k=1;k<=n;k++)cells.push(`<div class="match-cell ${k===s.i?'pick':''}">${S[k-1]}<small>${k===s.i?'i':''}</small></div>`);
   for(let k=1;k<=n;k++){
    const tIdx=k-s.start+1;
    if(tIdx>=1&&tIdx<=T.length){
     const cur=k===s.i&&tIdx===s.j;
     const cls=cur?(s.hit===false?'match-fail':'pick'):(tIdx<s.j?'match-ok':'');
     cells.push(`<div class="match-cell ${cls}">${T[tIdx-1]}<small>${tIdx===s.j?'j':''}</small></div>`);
    }else cells.push('<div class="match-cell match-blank">&nbsp;<small></small></div>');
   }
   zones.innerHTML=`<div class="match-grid" style="grid-template-columns:repeat(${n},minmax(30px,44px))">${cells.join('')}</div>`;
   counter.textContent=`已比较 ${s.cmp} 次`;
   status.textContent=s.msg;
   status.classList.toggle('status-fail',!!s.fail);
   status.classList.toggle('status-ok',!!s.ok);
   root.querySelector('[data-prev]').disabled=step<=0;
   root.querySelector('[data-next]').disabled=step>=steps.length-1;
   root.querySelector('[data-next]').textContent=step===0?'开始推演':'下一步';
  }
  if(selects.length)selects.forEach(sel=>sel.onchange=()=>{build();step=0;render();});
  root.querySelector('[data-next]').onclick=()=>{if(step<steps.length-1){step++;render();}};
  root.querySelector('[data-prev]').onclick=()=>{if(step>0){step--;render();}};
  root.querySelector('[data-reset]').onclick=()=>{step=0;render();};
  build();render();
 });
}
