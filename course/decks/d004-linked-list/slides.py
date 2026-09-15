DECK_ID = 'D004'
TITLE = '链表与表示的选择'

# Each slide is [title, body_html, section_label].
SLIDES = [['链表与表示的选择',
  '<p class="lead">放弃物理相邻，还能保住“前后相继”吗？</p><p>数据结构与算法 · D004</p><p '
  'class="small">教材对应：《数据结构（C语言版）（第3版）》第 2 章 线性表，2.5–2.8 节</p>',
  '课程名'],
 ['只给真正存在的项安排住处，次序怎么保？',
  '<p>回收 D003 留问：x¹⁰⁰⁰⁰ + 2x + 1 不该为 9998 个零系数浪费住处。</p><p>那就只给真正存在的三项安排住处：</p><div '
  'class="record-strip"><span>1·x¹⁰⁰⁰⁰</span><span>2·x¹</span><span>1·x⁰</span></div><p>但“下标即次数”丢了：三个项散落各处，谁先谁后？</p><div '
  'class="quote">次序不能靠“住在隔壁”表达了，<br>还能靠什么？</div>',
  '回到问题'],
 ['一个结点，要住下什么？',
  '<p>每一项自己报告三件事：</p><ul><li><strong>系数</strong> coef；</li><li><strong>次数</strong> '
  'exp；</li><li><strong>下一项住在哪</strong> next。</li></ul><table><thead><tr><th>数据域</th><th>链接域</th></tr></thead><tbody><tr><td>coef　exp</td><td>next '
  '→</td></tr></tbody></table><p>次序不再靠物理相邻，靠链接显式表达——每个结点指着下一个结点。</p><p '
  'class="small">工程连接：工序链中每道工序只登记下一道是什么；整条链的次序，就藏在一个个“下一个”里。</p>',
  '结点设计'],
 ['寻宝游戏为什么没法直奔第 5 个地点？',
  '<div class="columns"><div class="panel"><p><strong>快递柜（D003）</strong></p><p>柜号直接算出格子位置，凭号码直接开柜。</p></div><div '
  'class="panel"><p><strong>寻宝游戏</strong></p><p>每条线索只写着下一个地点，必须从第 1 张纸条走起。</p></div></div><div '
  'class="quote">线索 ↔ next 指针。<br>想到第 5 个地点，只能沿着线索走 4 次。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>对照提问脚本：先让学生自己说“快递柜 vs 寻宝差在哪”——柜号可以直接算出位置，线索只能沿着走；一个能直奔，一个不能。让学生先给出答案，再落到“地址公式失效”这一层。</p></details>',
  '生活类比'],
 ['结点在内存里住成什么样？',
  '<p>回收 D002：内存是一个巨大的字节数组，指针 = 地址。结点散落各处，指针把它们串成链。</p><table><thead><tr><th>结点</th><th>住址（地址）</th><th>next（下一项住址）</th></tr></thead><tbody><tr><td>3x²</td><td>100</td><td>316</td></tr><tr><td>2x</td><td>316</td><td>208</td></tr><tr><td>1</td><td>208</td><td>空（NULL）</td></tr></tbody></table><div '
  'class="record-strip ordered"><span>3x² @100</span><span>→</span><span>2x @316</span><span>→</span><span>1 '
  '@208</span><span>→</span><span>NULL</span></div><p>地址 100、316、208 互不相邻，链却串起了次序。</p><p '
  'class="small">head 只记录第一个结点的地址 100——这是整条链的全部家当。</p>',
  '内存模型'],
 ['struct Node：一个结点在 C 里怎样出生？',
  '<pre>struct Node {\n    int coef;           /* 系数           */\n    int exp;            /* 次数           */\n    struct Node *next;  /* 下一项住在哪   */\n};</pre><div '
  'class="columns"><div class="panel"><p><strong>malloc：结点出生</strong></p><p>按需申请一个结点的住处，“住满”问题消失。</p></div><div '
  'class="panel"><p><strong>free：结点死亡</strong></p><p>归还住处；内存管理的责任出现了。</p></div></div><details '
  'class="teacher-note"><summary>教学注记</summary><p>指针痛点正面应对：next 就是“下一个住哪”的门牌号，先建立这个直观，再谈语法。free 是责任：malloc 来的住处不归还，内存会一点点漏掉（内存泄漏）——一句话点到，不展开。</p></details>',
  '从数学到 C'],
 ['malloc 出来的 3 个结点，地址相邻吗？',
  '<p>先预测：连续三次 malloc，拿到的地址会相邻吗？</p><details><summary>说出你的预测与理由</summary><p>不会。即使某次运行看似有规律，也不在语言的保证之内——顺序和间距都不可依赖。</p></details><p>运行 '
  '<code>code/link_demo.c</code>，打印三个结点的真实地址，检查预测。</p><div class="quote '
  'compact-quote">不相邻，但链得起来。</div><p class="small">与 D003 的 addr_demo '
  '恰成对照实验：那里相邻元素地址差恒为 sizeof，这里相邻结点之间隔着空隙，地址差不再是 '
  'sizeof。同一个验证口径——先预测、再运行、再检查。</p>',
  '先预测再运行'],
 ['取第 i 项，要走几步？',
  '<p>地址公式失效：结点不住在 base + (i−1)×L，算不出，只能走。</p><div class="quote">从 head 出发，沿 next 走 i−1 '
  '步，到达第 i 个元素。</div><p>取第 1 项走 0 步，取第 n 项走 n−1 步：访问是 '
  '<strong>O(n)</strong>。</p><p><strong>表示不变量换了形态</strong>：顺序表是“第 i 个元素恒在 '
  'base+(i−1)×L”；链表是“从 head 出发沿 next 走 i−1 步，恒到达第 i 个元素”。</p><p '
  'class="small">数学接口：这正是递推——首项加递推关系，第 i 项只能逐项推出；head 加 next，第 i 个结点只能逐个走到。</p>',
  '访问'],
 ['新同学又来了：这次要搬几次？',
  '<p>还是按学号插入 104。链表里没有“腾出位置”这回事：</p><div class="quote">插入只需改两个链接：<br>新结点指向后继，前驱指向新结点。</div><div '
  'class="record-strip ordered"><span>103</span><span>→</span><span>104</span><span>→</span><span>105</span></div><p>没有一个人搬家——到达插入位置之后，插入本身是 '
  '<strong>O(1)</strong>。</p><p class="small">工程连接：火车挂摘一节车厢，只需解开两处挂钩，不必把后面的车厢全部移位。</p>',
  '插入'],
 ['两个链接，先改哪个？',
  '<p>先自己答：新结点指向后继、前驱指向新结点——这两步，先做哪一步？</p><details><summary>说出你的顺序与理由</summary><p><strong>先接后继，再改前驱。</strong><br>若先把前驱指向新结点，链从中间断开，后继的地址就被覆盖丢失——后半条链永远找不回来。</p></details><div '
  'class="quote compact-quote">断链是指针操作的经典陷阱：<br>唯一的线索被覆盖，后面的世界就消失了。</div><p '
  'class="small">课堂互动：请一位同学上黑板，画出两种顺序各自的结果。</p>',
  '插入'],
 ['摘下结点，就完事了吗？',
  '<div class="columns"><div class="panel"><p><strong>第一步：改链接</strong></p><p>前驱跳过被删结点，指向它的后继。</p></div><div '
  'class="panel"><p><strong>第二步：free</strong></p><p>归还结点占用的内存——责任才算完成。</p></div></div><div '
  'class="quote">只改链接不 free，结点成了无家可归的孤儿：内存泄漏。</div><p>运行 '
  '<code>code/linklist.c</code>，演示插入与删除的完整过程。</p>',
  '删除'],
 ['顺序表 vs 链表，代价为何严格互换？',
  '<table><thead><tr><th></th><th>顺序表</th><th>链表</th></tr></thead><tbody><tr '
  'class="focus-row"><td>按位置访问</td><td>O(1)</td><td>O(n)</td></tr><tr><td>插入 / '
  '删除</td><td>O(n)</td><td>O(1)（已知位置后）</td></tr><tr><td>空间开销</td><td>无额外</td><td>每结点多一个指针</td></tr><tr><td>容量</td><td>定长，需扩容</td><td>按需生长</td></tr></tbody></table><div '
  'class="quote">强项与边界，仍来自同一个原因：布局选择。</div><p '
  'class="small">换取一样东西的方式，就是放弃另一样东西。</p>',
  '对照收口'],
 ['什么时候用顺序表，什么时候用链表？',
  '<div class="columns"><div class="panel"><p><strong>选顺序表</strong></p><p>访问为主、增删稀少；<br>规模稳定、可以预估。</p></div><div '
  'class="panel"><p><strong>选链表</strong></p><p>增删频繁、位置多变；<br>规模不定、难以预估。</p></div></div><div '
  'class="quote">没有最好的表示，只有适合任务的表示。<br>操作模式，决定表示选择。</div><p '
  'class="small">呼应 D003：认识一种表示，连同它的边界一起认识。</p>',
  '判断与选择'],
 ['为什么还有人要循环链表和双向链表？',
  '<div class="columns"><div class="panel"><p><strong>循环链表</strong></p><p>尾结点的 next 回头指向 '
  'head：从任何一处出发，都能走完全程。约瑟夫问题——围成一圈报数，是天然的循环。</p></div><div '
  'class="panel"><p><strong>双向链表</strong></p><p>每个结点多付一个 prev 指针，换反向行走的自由。</p></div></div><p '
  'class="small">只讲动机，不展开实现。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>追问素材：循环链表遍历的终止条件怎么写？（回到起点就停，而不是遇到 '
  'NULL。）双向链表插入要改几个链接？（四个：新结点的两个，前驱、后继各一个。）</p></details>',
  '变体'],
 ['两个有序表合并，链表版怎么做？',
  '<p>回收 D002 双指针扫描：两个指针各盯一条链的当前结点。</p><ol><li>比较两个指针所指的结点；</li><li>把较小的结点接到结果链的尾部；</li><li>对应的指针前进一步，直到一条链走完。</li></ol><div '
  'class="quote">只改链接，不搬数据。</div><p '
  'class="small">数组版合并要逐个元素拷贝；链表版只是把现成的结点重新串联。</p>',
  '应用回收'],
 ['回到教材：链式存储结构',
  '<div class="quote compact-quote"><strong>教材定义</strong><br>链式存储结构用一组任意的存储单元存储线性表的数据元素；每个结点除存储数据元素本身的信息外，还要存储指示其直接后继的信息。</div><p>数据域 '
  '+ 指针域 = 结点；n 个结点链接成一个链表。每个结点只含一个指针域的，称为单链表（线性链表）。</p><p>这是线性表 ADT '
  '的<strong>第二种实现</strong>：操作集合没变，存储方式换了——教材 2.3 节“ADT 不规定怎样存”，在此兑现。</p><p '
  'class="small">见教材 2.5–2.7 节。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>习题路径：一元多项式相加的完整实现见教材 2.8 '
  '节，作为习题布置——它正是本讲的引入案例，学生已经走完“为什么需要链表”，剩下的实现细节适合独立攻下。</p></details>',
  '教材定义'],
 ['线性表，变了吗？',
  '<p>InitList、GetElem、ListInsert、ListDelete……操作集合一个没变。<br>变的只是元素“住”的方式：从连续布局，到散落加链接。</p><div '
  'class="quote">抽象对象与物理表示分离：<br>表示是服务抽象对象的方式，不是对象本身。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>这条元认识将反复回收：栈、队列、树、图，都会面对“同一抽象、多种表示”。本课是学生第一次完整经历这个切换，值得在这里停一分钟。</p></details>',
  '本质收口'],
 ['把三个情境放在一起看',
  '<table><thead><tr><th>情境</th><th>数学</th><th>C</th></tr></thead><tbody><tr><td>寻宝：沿线索逐个找地点</td><td>链接序表达“前后相继”</td><td>struct '
  'Node 与 next</td></tr><tr><td>名单：新同学插入不搬家</td><td>改两个链接</td><td>两次指针赋值</td></tr><tr><td>多项式：只给非零项住处</td><td>非零项序列</td><td>coef、exp、next '
  '结点链</td></tr></tbody></table><p class="small">三个情境，同一套机制：散落的结点 + 显式的链接。</p>',
  '案例收口'],
 ['我怎样知道自己真的学会了？',
  '<ul><li>能画出插入改链接的顺序，并解释为什么顺序重要；</li><li>能说清“链表访问 O(n)”与“数组访问 '
  'O(1)”差在内存模型的哪一步；</li><li>能各举一个该选链表、该选顺序表的场景。</li></ul><div '
  'class="quote">把一次“我以为”变成一次有依据的修正。</div>',
  '学会了吗'],
 ['课后：教材导航与三个练习',
  '<p><strong>教材导航</strong>：精读 2.5–2.7 节；完成教材第 2 '
  '章课后习题中与链表相关的题目。课件中带“教学注记”的页面，课后可以自行点开再看。</p><ol><li>补全 '
  '<code>code/linklist.c</code> 的 insert 链接顺序：先把两行赋值注释掉、自己补全，再运行核对插入 104 '
  '的结果；</li><li>实现两个有序链表的合并（对照本讲“应用回收”页的步骤）；</li><li>思考：双向链表多付的代价，换来了什么？</li></ol><p '
  'class="small">挑战：约瑟夫环——10 人围成一圈，从 1 开始报数，数到 3 的人出局，谁留到最后？<br>借助同学或 AI '
  '时，记录获得的帮助，独立核对关键判断。</p>',
  '课后衔接'],
 ['如果只允许在一头存取呢？',
  '<p>链表把“住”的自由给了我们。但有时，自由本身需要被限制：</p><ul><li>食堂的餐盘叠成一摞：只能从顶上放、从顶上取；</li><li>挤满人的电梯：先到的人后走；</li><li>编辑器的“撤销”：最后做的事，最先撤回。</li></ul><div '
  'class="quote">只允许在一头存取，会得到什么结构？<br>下次课：受限的线性结构。</div>',
  '留下问题']]
