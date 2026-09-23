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
  'class="quote">次序不能靠“住在隔壁”表达了，<br>还能靠什么？</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（约 4 '
  '分钟，9/21 课堂已验证）：由“9998 个零不住”延伸到稀疏性——0 乘任何数、加任何数都不改变对象，能不存就不存。有限差分、有限元求解 '
  'PDE 得到的矩阵大多是稀疏的：n 阶矩阵有 n² 个元素，非零元只有 O(n) 个，不该用 O(n²) 的存储装 O(n) '
  '的信息。再进一步：大数据中，高维数据往往集中在低维流形上（三维空间中的曲面本质是二维的）——找规律就是找低维结构，“只存该存的”是同一种思想。</p></details>',
  '回到问题'],
 ['一个结点，要住下什么？',
  '<p>每一项自己报告三件事：</p><ul><li><strong>系数</strong> coef；</li><li><strong>次数</strong> '
  'exp；</li><li><strong>下一项住在哪</strong> next。</li></ul><table><thead><tr><th>数据域</th><th>链接域</th></tr></thead><tbody><tr><td>coef　exp</td><td>next '
  '→</td></tr></tbody></table><p>次序不再靠物理相邻，靠链接显式表达——每个结点指着下一个结点。</p><p '
  'class="small">工程连接：工序链中每道工序只登记下一道是什么；整条链的次序，就藏在一个个“下一个”里。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开：人脑提取信息更像链表而非数组——联想是一个线索引出下一个线索，逻辑推理也是一条链；某处断了，推理就停在那里，只能回头走分支，链就此连成树（预告 '
  'D008）。工作记忆只能装六七个信息块，所以思考要依赖外化的链条。</p><p>史料：1955 年，Newell、Shaw 与 Simon '
  '在兰德公司为 IPL 语言（最早的人工智能语言之一）发明链表——最初的设计目的就是模拟人类思维的“联想”；Simon 后来获诺贝尔经济学奖。链表不是为存储而生的，是为“思考”而生的。</p></details>',
  '结点设计'],
 ['寻宝游戏为什么没法直奔第 5 个地点？',
  '<div class="columns"><div class="panel"><p><strong>快递柜（D003）</strong></p><p>柜号直接算出格子位置，凭号码直接开柜。</p></div><div '
  'class="panel"><p><strong>寻宝游戏</strong></p><p>每条线索只写着下一个地点，必须从第 1 张纸条走起。</p></div></div><div '
  'class="quote">线索 ↔ next 指针。<br>想到第 5 个地点，只能沿着线索走 4 次。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>对照提问脚本：先让学生自己说“快递柜 vs 寻宝差在哪”——柜号可以直接算出位置，线索只能沿着走；一个能直奔，一个不能。让学生先给出答案，再落到“地址公式失效”这一层。</p></details>',
  '生活类比'],
 ['结点在内存里住成什么样？',
  '<p>回收 D003：内存是一个巨大的字节数组；指针是记录地址的变量。结点散落各处，指针把它们串成链。</p><table><thead><tr><th>结点</th><th>住址（地址）</th><th>next（下一项住址）</th></tr></thead><tbody><tr><td>3x²</td><td>100</td><td>316</td></tr><tr><td>2x</td><td>316</td><td>208</td></tr><tr><td>1</td><td>208</td><td>空（NULL）</td></tr></tbody></table><div '
  'class="record-strip ordered"><span>3x² @100</span><span>→</span><span>2x @316</span><span>→</span><span>1 '
  '@208</span><span>→</span><span>NULL</span></div><p>地址 100、316、208 互不相邻，链却串起了次序。</p><p '
  'class="small">head 只记录第一个结点的地址 100——这是整条链的全部家当。</p>',
  '内存模型'],
 ['struct Node：一个结点在 C 里怎样出生？',
  '<pre>struct Node {\n    int coef;           /* 系数           */\n    int exp;            /* 次数           */\n    struct Node *next;  /* 下一项住在哪   */\n};</pre><div '
  'class="columns"><div class="panel"><p><strong>malloc：结点出生</strong></p><p>按需申请一个结点的住处，“住满”问题消失。</p></div><div '
  'class="panel"><p><strong>free：结点死亡</strong></p><p>归还住处；内存管理的责任出现了。</p></div></div><details '
  'class="teacher-note"><summary>教学注记</summary><p>指针痛点正面应对：next 就是“下一个住哪”的门牌号，先建立这个直观，再谈语法。free '
  '是责任：malloc 来的住处不归还，内存会一点点漏掉（内存泄漏）——一句话点到，不展开。</p><p>可展开的类比（9/21 '
  '课堂已验证）：内存管理的责任就是善始善终——挂横幅只管挂不管收、东西用完不归回原位，都是“内存泄漏”的生活版；用完归位，无谓的麻烦才不会累积。</p></details>',
  '从数学到 C'],
 ['malloc 出来的 3 个结点，地址相邻吗？',
  '<p>先预测：连续三次 malloc，拿到的地址会相邻吗？</p><details><summary>说出你的预测与理由</summary><p>不会。即使某次运行看似有规律，也不在语言的保证之内——顺序和间距都不可依赖。</p></details><p>运行 '
  '<code>code/link_demo.c</code>，打印三个结点的真实地址，检查预测。</p><div class="quote '
  'compact-quote">不相邻，但链得起来。</div><p class="small">与 D003 的 addr_demo '
  '恰成对照实验：那里相邻元素地址差恒为 sizeof，这里相邻结点之间隔着空隙，地址差不再是 '
  'sizeof。同一个验证口径——先预测、再运行、再检查。</p>',
  '先预测再运行'],
 ['取第 i 项，要走几步？',
  '<p>地址公式失效：结点不住在 base + (i−1)×L，算不出，只能走。亲手沿指针走一走：</p><div '
  'data-link="access"><div class="toolbar"><label>取哪一项 <select aria-label="选择访问位置"><option '
  'value="0">第 1 项</option><option value="1">第 4 项</option><option value="2">第 8 '
  '项</option></select></label><button data-prev>上一步</button><button data-next>开始推演</button><button '
  'data-reset>重置</button></div><div class="mem-counter"></div><div class="link-zones"></div><div '
  'class="status" aria-live="polite"></div></div><div class="quote">从 head 出发，沿 next 走 i−1 '
  '步，到达第 i 个元素。</div><p>取第 1 项走 0 步，取第 n 项走 n−1 步：访问是 '
  '<strong>O(n)</strong>。等可能取任意一项，平均走 (n−1)/2 步——期望仍是 O(n)（回收 D003：复杂度 = 数数 + '
  '期望）。</p><p><strong>表示不变量换了形态</strong>：顺序表是“第 i 个元素恒在 '
  'base+(i−1)×L”；链表是“从 head 出发沿 next 走 i−1 步，恒到达第 i 个元素”。</p><p '
  'class="small">数学接口：这正是递推——首项加递推关系，第 i 项只能逐项推出；head 加 next，第 i 个结点只能逐个走到。</p>',
  '访问'],
 ['新同学又来了：这次要搬几次？',
  '<p>还是按学号插入 104。链表里没有“腾出位置”这回事：</p><div class="quote">插入只需改两个链接：<br>新结点指向后继，前驱指向新结点。</div><div '
  'class="record-strip ordered"><span>103</span><span>→</span><span>104</span><span>→</span><span>105</span></div><p>没有一个人搬家——到达插入位置之后，插入本身是 '
  '<strong>O(1)</strong>。</p>',
  '插入'],
 ['两个链接，先改哪个？',
  '<p>新结点 104 已经 malloc 出生，要插到 103 与 105 之间。先自己答：s->next = p->next 与 p->next = '
  's，先做哪一步？说出顺序与理由，再亲手推演——两种顺序各看一遍：</p><div '
  'data-link="insert"><div class="toolbar"><label>改链接顺序 <select aria-label="选择改链接顺序"><option '
  'value="0">先 s->next = p->next</option><option value="1">先 p->next = '
  's</option></select></label><button data-prev>上一步</button><button data-next>开始推演</button><button '
  'data-reset>重置</button></div><div class="mem-counter"></div><div class="link-zones"></div><div '
  'class="status" aria-live="polite"></div></div><div '
  'class="quote compact-quote">断链是指针操作的经典陷阱：<br>唯一的线索被覆盖，后面的世界就消失了。</div><p '
  'class="small">课堂互动：请一位同学上黑板，画出两种顺序各自的结果，再与推演对照。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（约 3 分钟，9/21 '
  '课堂已验证）：两种顺序的对照正是“理解 → 判断 → 决策”的最小实例——先理解每种做法的后果，再判断对错，最后决策。迁移到学生的未来焦虑：不理解这个世界存在不确定性、不承认自己暂时不具备判断能力，就无法对“考研还是工作”做出好决策；先接受现状，才有行动的起点。</p></details>',
  '插入'],
 ['摘下结点，就完事了吗？',
  '<p>删除 104：改链接与 free，少一步会怎样？两种做法各推演一遍：</p><div '
  'data-link="delete"><div class="toolbar"><label>删除方式 <select aria-label="选择删除方式"><option '
  'value="0">q 记录 → 改链接 → free(q)</option><option value="1">直接改链接（看看会发生什么）</option></select></label><button '
  'data-prev>上一步</button><button data-next>开始推演</button><button data-reset>重置</button></div><div '
  'class="mem-counter"></div><div class="link-zones"></div><div class="status" '
  'aria-live="polite"></div></div><div '
  'class="quote">只改链接不 free，结点成了无家可归的孤儿：内存泄漏。</div><p>运行 '
  '<code>code/linklist.c</code>，演示插入与删除的完整过程。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（约 3 分钟，9/21 '
  '课堂已验证）：内存泄漏的生活版是时间泄漏——本来安排做作业的时间，被手机消息一次次漏掉；内存越漏越少，程序越跑越慢。更本质的原因：资源永远有限（时间、注意力、空间），所以用完必须归位、释放、整理。</p></details>',
  '删除'],
 ['顺序表 vs 链表，代价为何严格互换？',
  '<table><thead><tr><th></th><th>顺序表</th><th>链表</th></tr></thead><tbody><tr '
  'class="focus-row"><td>按位置访问</td><td>O(1)</td><td>O(n)</td></tr><tr><td>插入 / '
  '删除</td><td>O(n)</td><td>O(1)（已知位置后）</td></tr><tr><td>空间开销</td><td>无额外</td><td>每结点至少多一个指针；多项式情形还要多存次数</td></tr><tr><td>容量</td><td>定长，需扩容</td><td>按需生长</td></tr></tbody></table><div '
  'class="quote">强项与边界，仍来自同一个原因：布局选择。</div><p '
  'class="small">换取一样东西的方式，就是放弃另一样东西。</p>',
  '对照收口'],
 ['什么时候用顺序表，什么时候用链表？',
  '<div class="columns"><div class="panel"><p><strong>选顺序表</strong></p><p>访问为主、增删稀少；<br>规模稳定、可以预估。</p></div><div '
  'class="panel"><p><strong>选链表</strong></p><p>增删频繁、位置多变；<br>规模不定、难以预估。</p></div></div><div '
  'class="quote">没有最好的表示，只有适合任务的表示。<br>操作模式，决定表示选择。</div><p '
  'class="small">呼应 D003：认识一种表示，连同它的边界一起认识。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（9/21 '
  '课堂已验证）：“换取一样东西的方式，就是放弃另一样东西”可上升为第一性原理——没有无代价的方案。生物界同样如此：雄孔雀华丽的尾羽吸引配偶，却拖慢飞行、暴露行踪——进化也无法同时优化所有维度，只有适合环境的妥协。</p><p>回收克莱姆法则（D002 '
  '注记）：小规模与理论场景适用，大规模真实计算失效——每个知识和方法都有边界，要连同边界一起认识；就像认识一个人，要连同他的缺点一起认识。</p></details>',
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
  '<p>承接 D002 双索引扫描的思想：两个指针各盯一条链的当前结点。</p><ol><li>比较两个指针所指的结点；</li><li>把较小的结点接到结果链的尾部；</li><li>对应的指针前进一步，直到一条链走完。</li></ol><div '
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
  'class="teacher-note"><summary>教学注记</summary><p>课堂提问脚本（约 10 分钟，9/21 '
  '课堂已验证有效）：先请学生举“把表示当成对象本身”的生活例子，再递进三个例子——</p><ol><li><strong>名字与标签</strong>：名字、外号、标签是你吗？身高、体重、年龄的清单是你这个人吗？</li><li><strong>空间点与坐标</strong>：给定坐标系后某点的坐标是 '
  '(1,3,4)——没有坐标系，这个点存在吗？换坐标系，坐标变，点变吗？</li><li><strong>矩阵与数表</strong>：矩阵的本质是线性算子，数表只是它在给定基下的表示；换一组基，数表变，算子不变。只要数据里出现数，背后一定有某种“坐标系”。</li></ol><p>收口到学生处境：工资是能力与责任的外化表示，可能与你错位；工作的本质是社会协作网络中的角色与责任，认知与能力才是根基——把“找什么工作”的焦虑，转化为“提升认知与能力”的行动。</p><p>哲学锚点：Korzybski（1931）“地图非疆域”——任何表征都只是现实的简化，不能当作现实本身。这条元认识将反复回收：栈、队列、树、图，都会面对“同一抽象、多种表示”。</p></details>',
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
 ['课后：教材导航与本周作业',
  '<p><strong>教材导航</strong>：精读 2.5–2.8 节。课件中带“教学注记”的页面，课后可以自行点开再看；带演示的页面可以反复推演。</p><p><strong>本周作业</strong>（作业规范见 '
  'course/assignments/homework-guide.md）：</p><p><strong>A. 书本习题</strong>：第 2 '
  '章选择题 (4)(5)(6)(7)(12)(13)、算法设计题 (1)。选择题每题附一句“为什么选它”；算法设计题写出思路与关键步骤。</p><p><strong>B. '
  '扩展作业</strong>：补全 <code>code/linklist.c</code> 的 insert 链接顺序：先把两行赋值注释掉、自己补全，再运行核对插入 '
  '104 的结果；附预测与实测对照。</p><p '
  'class="small">自学练习（不提交）：思考——双向链表多付的代价，换来了什么？可试做选择题 (14)(15) 检验自己的想法。<br>挑战：约瑟夫环——10 '
  '人围成一圈，从 1 开始报数，数到 3 的人出局，谁留到最后？算法设计题 (7)：把单链表的链接方向“原地”逆转。<br>探究：阅读教材 2.8 '
  '节，用本讲的结点结构实现一元多项式相加——它正是本讲的引入案例。</p>',
  '课后衔接'],
 ['如果只允许在一头存取呢？',
  '<p>链表把“住”的自由给了我们。但有时，自由本身需要被限制：</p><ul><li>食堂的餐盘叠成一摞：只能从顶上放、从顶上取；</li><li>挤满人的电梯：先到的人后走；</li><li>编辑器的“撤销”：最后做的事，最先撤回。</li></ul><div '
  'class="quote">只允许在一头存取，会得到什么结构？<br>下次课：受限的线性结构。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（约 5 分钟，9/21 '
  '课堂已验证；与 D005“约束不是损失，是设计”呼应）：从高中到大学，外界约束突然撤掉，很多人反而荒废了学业——自由需要自我约束来承接。方法层面给实例：工作时手机完全静音、放到伸手拿不到的地方；给易分心的应用加使用限制。约束不是枷锁：资源的约束、物理的约束、自我施加的约束，往往是创造力的来源；成就大事的个人与组织，都有明确的自我约束。</p></details>',
  '留下问题']]
