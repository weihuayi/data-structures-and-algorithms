DECK_ID = 'D005'
TITLE = '受限的线性结构：栈与队列'

# Each slide is [title, body_html, section_label].
SLIDES = [['受限的线性结构：栈与队列',
  '<p class="lead">拿走一些自由，会得到什么能力？</p><p>数据结构与算法 · D005</p><p '
  'class="small">教材对应：《数据结构（C语言版）（第3版）》第 3 章 栈和队列，3.1–3.3、3.5 节</p>',
  '课程名'],
 ['这些结构为什么“故意不自由”？',
  '<p>回收 D004 留问：生活里有三种“不自由”的结构——</p><ul><li>食堂的餐盘叠成一摞：只能从顶上放、从顶上取；</li><li>挤满人的电梯：先到的人后走；</li><li>编辑器的“撤销”：最后做的事，最先撤回。</li></ul><div '
  'class="quote">它们明明可以随便存取，<br>为什么偏要“故意不自由”？</div>',
  '回到问题'],
 ['一个新思想：给线性表加限制',
  '<p>线性表已经学过两种表示：顺序表（D003）、链表（D004）。<br>这一次，不发明新的“住处”，只在<strong>操作</strong>上做文章。</p><div '
  'class="quote">不发明新的结构，只限制操作——<br>能力可以靠“限制”获得。</div><p>栈与队列，就是给同一个线性表施加的两种操作限制。</p>',
  '回到问题'],
 ['只允许在一端存取，得到什么？',
  '<p><strong>栈（Stack）</strong>：插入、删除只能在同一端进行，这一端叫<strong>栈顶</strong>。</p><div '
  'class="record-strip ordered"><span>栈底</span><span>a₁</span><span>a₂</span><span>…</span><span>aₙ</span><span>栈顶 '
  '← 唯一出入口</span></div><p>最后压进去的元素，最先弹出来——<strong>后进先出（LIFO）</strong>。</p><div '
  'class="columns"><div class="panel"><p><strong>餐盘</strong></p><p>只能从顶上放、从顶上取；取最底下的，得先把上面的全拿走。</p></div><div '
  'class="panel"><p><strong>撤销</strong></p><p>最后做的操作，最先被撤回；一层一层往回退。</p></div></div>',
  '栈'],
 ['为什么限制反而有用？',
  '<p>撤销的语义是：“最后发生的，最先撤回。”</p><p>栈用一条限制，把这个语义变成了<strong>保证</strong>：不用检查、不用搜索，pop '
  '弹出的恒是最后发生的那一步。</p><div '
  'class="quote">操作越受限，行为越可预测；<br>行为可预测，才能对顺序做保证。</div>',
  '栈'],
 ['栈的接口有多大？',
  '<p>栈的全部操作：</p><table><thead><tr><th>操作</th><th>作用</th></tr></thead><tbody><tr '
  'class="focus-row"><td>push</td><td>压栈：栈顶加入一个元素</td></tr><tr><td>pop</td><td>弹栈：取走栈顶元素</td></tr><tr><td>top</td><td>看一眼栈顶，不取走</td></tr><tr><td>isEmpty</td><td>栈空了吗</td></tr></tbody></table><p>只有四个操作，比线性表小得多——没有“按位置取”，没有“插到中间”。</p><div '
  'class="quote compact-quote">接口越窄，越不容易用错。</div>',
  '栈'],
 ['括号在哪一步配不上？',
  '<p>规则：遇到左括号压栈，遇到右括号弹栈核对。</p><p>先口算：<code>({[}]</code> 在哪一步配不上？</p><details><summary>栈轨迹推演</summary><table><thead><tr><th>字符</th><th>动作</th><th>栈（左底右顶）</th></tr></thead><tbody><tr><td>(</td><td>压栈</td><td>(</td></tr><tr><td>{</td><td>压栈</td><td>( '
  '{</td></tr><tr><td>[</td><td>压栈</td><td>( { [</td></tr><tr><td>}</td><td>弹栈核对</td><td>栈顶是 [，与 } '
  '配不上</td></tr></tbody></table><p>第 4 个字符处发现不匹配。</p></details><details '
  'class="teacher-note"><summary>教学注记</summary><p>提问脚本：先让学生口算 <code>({[}]</code> '
  '的栈轨迹、说出第几步配不上，再展开答案。追问：如果只有左括号、没有右括号呢？——遍历完栈非空即错。</p></details>',
  '栈'],
 ['顺序栈：数组 + top，回收 D003',
  '<p>回收 D003：数组天然有一端是固定的——下标 0 作栈底，栈顶用一个下标 top 标记。</p><pre>#define MAX '
  '100\nint data[MAX];\nint top = -1;   /* 空栈 */</pre><p>push：<code>data[++top] = '
  'x;</code>　　pop：<code>x = data[top--];</code></p><div class="quote">不变量：top '
  '恒指向“最年轻的元素”。</div>',
  '栈'],
 ['先预测，再运行：stack_demo',
  '<p>先预测：<code>({[}]</code> 与 <code>({[]})</code> '
  '两个串，程序各会给出什么判定？</p><details><summary>说出你的预测与理由</summary><p>第一个在第 4 '
  '个字符处不匹配：} 要配对的栈顶是 [；第二个层层配对成功，栈最终为空。</p></details><p>运行 '
  '<code>code/stack_demo.c</code>：先看 push/pop 轨迹，再看两个串的括号匹配验证。</p><div class="quote '
  'compact-quote">先预测、再运行、再检查。</div>',
  '先预测再运行'],
 ['链栈：栈顶放在链表哪一头？',
  '<p>回收 D004：栈也可以用链式表示——链栈。先自己答：</p><div class="quote">栈顶放在链表的头部，还是尾部？</div><details><summary>说出你的判断与理由</summary><p><strong>放头部。</strong>头插、头删都是 '
  'O(1)；放尾部，pop 要先走到倒数第二个结点，是 O(n)。</p></details><p '
  'class="small">表示选择又回来了：同一个栈，数组能做，链表也能做。</p>',
  '栈'],
 ['两头各管一件事，得到什么？',
  '<p><strong>队列（Queue）</strong>：一端只进（队尾），另一端只出（队头）。</p><div '
  'class="record-strip ordered"><span>出队 ← 队头</span><span>a₁</span><span>a₂</span><span>…</span><span>aₙ</span><span>队尾 '
  '← 入队</span></div><p>最先进队的元素，最先出队——<strong>先进先出（FIFO）</strong>。</p><div '
  'class="columns"><div class="panel"><p><strong>排队</strong></p><p>先到先服务，后来者站到队尾。</p></div><div '
  'class="panel"><p><strong>打印任务</strong></p><p>先提交的文档，先被打印。</p></div></div>',
  '队列'],
 ['为什么先到先服务？',
  '<p><strong>公平</strong>：谁先到达，谁先被服务——顺序本身就是规则。<br><strong>缓冲</strong>：生产与消费速度不一致时，队列在中间削峰。</p><p><strong>工程连接：AGV '
  '任务队列。</strong>几千台搬运小车的任务按到达顺序进入队列、依次派发；高峰时任务在队列里排队等待，不至于把调度系统压垮。</p><div '
  'class="quote">队列 = 公平 + 缓冲。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>AGV 任务队列工程细节（约 3 '
  '分钟）：任务到达有峰谷——夜班集中入库、白天零星补货；队列削峰，让调度按自己的能力消化；先到先服务保公平，没有哪台车的任务被永远插队。可联系 '
  'D001 的迷宫案例：同一类工程问题，换一个主角。</p></details>',
  '队列'],
 ['顺序队列的麻烦：rear 一路向后走',
  '<p>顺序队列：数组 + 队头 front + 队尾 rear。dequeue 只是 front 向后走一格——前部的位置空出来了，rear 却一路向后走。</p><div '
  'class="record-strip"><span>空</span><span>空</span><span>空</span><span>D</span><span>E</span></div><p '
  'class="small">N = 5：front 指向 D，rear 已顶到数组末尾。明明空着 3 个位置，新元素却进不来。</p><div '
  'class="quote">rear 顶到头，前部空着——这就是“假满”。</div>',
  '队列'],
 ['怎样把数组弯成环？',
  '<p>让下标“到头就绕回”：</p><div class="quote">rear = (rear + 1) % N</div><p>取模的余数永远在 0 '
  '到 N−1 之间：走到数组末尾，下一步回到 0。</p><p class="small">数学接口：同余——模 N 的世界里，N 和 0 '
  '是同一个位置；时钟就是日常的同余，13 点 ≡ 1 点（mod 12）。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>取模与同余的数学深化：模算术是循环世界的算术——一切有周期的事物（时钟、星期、环形缓冲区）都在做同余运算。可展开一句：计算机里的地址回绕、哈希表，都是这颗数学种子的果实。</p></details>',
  '循环队列'],
 ['front == rear，是空还是满？',
  '<p>空队列：front == rear。<br>可一直入队，rear 绕一圈追上 front，也是 front == '
  'rear——<strong>判空判满撞车了。</strong></p><div class="columns"><div '
  'class="panel"><p><strong>方案一：牺牲一个单元</strong></p><p>最多装 N−1 个元素；(rear+1)%N == front '
  '判满，front == rear 判空。</p></div><div class="panel"><p><strong>方案二：加一个计数器</strong></p><p>多记一个 '
  'count：count == 0 判空，count == N 判满，N 个位置全用上。</p></div></div><div '
  'class="quote">少用一个格子，还是多记一个数——<br>工程权衡，没有免费午餐。</div>',
  '循环队列'],
 ['手工推演：N = 5 的循环队列',
  '<p>采用方案一（牺牲一个单元，最多装 4 个），front、rear 从 0 出发。分两级推演：</p><p><strong>第一级（全班一起）</strong></p><ol><li>enqueue 4 个元素 '
  'A、B、C、D：rear 走到 4，(4+1)%5 == 0 == front，<strong>已满</strong>；</li><li>dequeue 2 个：A、B 离开，front 走到 '
  '2。</li></ol><p><strong>第二级（学生独立）</strong>：再 enqueue 2 个 E、F——rear 落在哪？队列判满了吗？</p><details><summary>核对答案</summary><p>再入队 '
  'E、F：rear 从 4 绕回 0、再到 1。<br>最终 front = 2，rear = 1；(1+1)%5 == 2 == '
  'front，<strong>再次判满</strong>——E、F 之后一个也进不来。</p></details>',
  '循环队列'],
 ['先预测，再运行：queue_demo',
  '<p>先预测：普通顺序队列（N = 5）交替入队、出队之后，rear 顶到末尾，还能再入队吗？</p><details><summary>说出你的预测与理由</summary><p>不能——前部空位用不上，假满；换成循环队列后，rear '
  '会绕回前部继续装。</p></details><p>运行 '
  '<code>code/queue_demo.c</code>：先看假满现象复现，再看循环队列的 front/rear 轨迹与判满条件生效。</p><div '
  'class="quote compact-quote">先预测、再运行、再检查。</div>',
  '先预测再运行'],
 ['链队：回收 D004 第三次',
  '<p>队列的链式表示：头出、尾进，需要同时守住两头。</p><ul><li>front 守头：dequeue = 头删，O(1)；</li><li>rear '
  '守尾：enqueue = 尾插，O(1)。</li></ul><div '
  'class="quote">同一个队列抽象，数组、循环数组、链表——三种表示。</div><p '
  'class="small">“同一抽象、多种表示”（D003 → D004 → '
  'D005），到这里应开始成为条件反射。</p>',
  '队列'],
 ['栈 vs 队列，一眼看清',
  '<table><thead><tr><th></th><th>栈</th><th>队列</th></tr></thead><tbody><tr '
  'class="focus-row"><td>限制在哪</td><td>同一端插入、删除</td><td>一端插入，另一端删除</td></tr><tr><td>行为语义</td><td>LIFO：后进先出</td><td>FIFO：先进先出</td></tr><tr><td>不变量</td><td>top '
  '恒指向最年轻的元素</td><td>front 守头、rear 守尾</td></tr><tr><td>典型场景</td><td>撤销、括号匹配</td><td>排队、任务派发</td></tr></tbody></table><div '
  'class="record-strip ordered"><span>线性表</span><span>— 限制：同一端存取 →</span><span>栈</span></div><div '
  'class="record-strip ordered"><span>线性表</span><span>— 限制：一端进、另一端出 '
  '→</span><span>队列</span></div>',
  '对照收口'],
 ['约束不是损失，是设计',
  '<p>拿走了“随便存取”的自由，换来了：</p><ul><li><strong>语义</strong>：LIFO 与 '
  'FIFO——顺序本身有了保证；</li><li><strong>简单</strong>：接口只有三四个操作，不容易用错；</li><li><strong>可维护</strong>：接口越窄，不变量越容易维护，正确性越好保证。</li></ul><div '
  'class="quote">限制换语义：约束不是损失，是设计。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>“接口越窄、不变量越容易维护”对应软件工程的信息隐藏原理：模块暴露得越少，外部能破坏的东西就越少。可预告一句：以后看到的好的模块设计，都在做“限制”这门功课。</p><p>限制与自由的辩证法（控制在 2 '
  '分钟）：好的约束让行为可预期——“戴着镣铐跳舞”，镣铐反而成就了诗的形式。工程与人生同构：纪律不是负担，是能力的前提。点到为止，不展开说教。</p></details>',
  '本质收口'],
 ['把三个情境放在一起看',
  '<table><thead><tr><th>情境</th><th>数学</th><th>操作</th></tr></thead><tbody><tr><td>餐盘：只从顶上放取</td><td>LIFO '
  '逆序</td><td>push / pop</td></tr><tr><td>排队：先到先服务</td><td>FIFO '
  '保序</td><td>enqueue / dequeue</td></tr><tr><td>括号：配对嵌套</td><td>最近未配对者先闭合</td><td>栈轨迹：压左括号、弹栈核对</td></tr></tbody></table><p '
  'class="small">三个情境，同一个思想：用操作限制，换来顺序的保证。</p>',
  '案例收口'],
 ['回到教材：栈与队列的定义',
  '<div class="quote compact-quote"><strong>教材定义</strong><br>栈是限定仅在表尾进行插入或删除操作的线性表；队列是只允许在表的一端进行插入、而在另一端删除元素的线性表。</div><p>教材 '
  '3.1 节的这句话，正是本讲的全部故事：<strong>栈和队列是“操作受限的线性表”</strong>——逻辑结构没变，操作集合收窄了。</p><p '
  'class="small">见教材 3.1–3.3、3.5 节；3.6 的案例思想已融入括号匹配的推演。</p>',
  '教材定义'],
 ['我怎样知道自己真的学会了？',
  '<ul><li>能解释撤销为什么用栈、不用队列；</li><li>能手写循环队列的判满条件，并说清两种方案的取舍；</li><li>能说清“接口越窄越容易维护”的理由。</li></ul><div '
  'class="quote">把一次“我以为”变成一次有依据的修正。</div>',
  '学会了吗'],
 ['课后：教材导航与三个练习',
  '<p><strong>教材导航</strong>：精读 3.1–3.3、3.5 节；完成教材第 3 '
  '章课后习题中与栈和队列相关的题目。课件中带“教学注记”的页面，课后可以自行点开再看。</p><ol><li>用栈实现一个序列的逆序输出：体会“栈是逆序器”；</li><li>补全 '
  '<code>code/queue_demo.c</code> 的判满条件：牺牲单元与计数器两种方案各试一次，运行核对；</li><li>思考：两个栈能实现一个队列吗？</li></ol><p '
  'class="small">挑战：写一个完整的括号匹配程序，支持 ()、[]、{} 三种括号。<br>借助同学或 AI '
  '时，记录获得的帮助，独立核对关键判断。</p>',
  '课后衔接'],
 ['函数调用函数，又调用函数……谁在记住“该回到哪里”？',
  '<p>程序运行时，函数调用函数、又调用函数，层层深入：</p><div class="quote">每一层调用结束，<br>是谁在记住“该回到哪里”？</div><p>下次课：栈与递归——谜底就在今天讲的栈里。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>铺垫提示：下次课把“谁在记住回到哪”彻底揭开（函数调用栈）。可让学生今晚先想一想：main 调 '
  'f、f 调 g，g 返回后为什么恰好回到 f 里调用它的那一行？</p></details>',
  '留下问题']]
