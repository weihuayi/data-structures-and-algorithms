DECK_ID = 'D003'
TITLE = '顺序表：表示与访问机制'

# Each slide is [title, body_html, section_label].
SLIDES = [['顺序表：表示与访问机制',
  '<p class="lead">数据住进内存，到底住成什么样？</p><p>数据结构与算法 · D003</p><p '
  'class="small">教材对应：《数据结构（C语言版）（第3版）》第 2 章 线性表，2.1–2.4 节</p>',
  '课程名'],
 ['排好序的清单，世界却一直在变',
  '<div class="quote">新商品上架，旧商品下架。<br>排好序的商品清单，怎样跟得上变化？</div><p>上次课：排序与双索引扫描让搜索更快。<br>数据组织不仅要“找得快”，还要“变得起”。</p>',
  '回到问题'],
 ['数据住进内存，要回答哪三个问题？',
  '<div class="question-cards"><div><span>住成什么样</span><strong>元素之间的关系怎样表示？</strong><p>逻辑上的先后次序，在内存里怎样安顿？</p></div><div><span>放在哪</span><strong>每个元素住在哪里？</strong><p>位置与次序是什么关系？</p></div><div><span>怎么找、怎么改</span><strong>访问与修改各花多少代价？</strong><p>代价由什么决定？</p></div></div><p '
  'class="small">本次课沿这三个问题，认识第一种存储方式：顺序表示。</p>',
  '回到问题'],
 ['内存是什么？',
  '<p>先认识内存：内存是一个巨大的字节数组，每个字节有一个编号，叫做<strong>地址</strong>。</p><table><thead><tr><th>地址</th><th>100</th><th>101</th><th>102</th><th>103</th><th>104</th><th>105</th><th>…</th></tr></thead><tbody><tr><td>字节内容</td><td>…</td><td>…</td><td>…</td><td>…</td><td>…</td><td>…</td><td>…</td></tr></tbody></table><p>给出一个地址，就能直接读出那个字节——不需要从头找起。</p>',
  '内存模型'],
 ['快递柜为什么不用挨个敲门？',
  '<div class="columns"><div class="panel"><p><strong>挨家敲门</strong></p><p>想知道包裹在哪家，只能一户一户问过去。</p></div><div '
  'class="panel"><p><strong>快递柜</strong></p><p>柜号直接对应一个格子，凭号码直接开柜。</p></div></div><div '
  'class="quote">柜号 ↔ 地址。<br>知道编号，就直接定位，代价与柜子总数无关。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开：很多学生指针学不好的根源，是对内存模型没有直观认识。可联系取快递的经验多问几个学生：柜号是怎么来的？号码和格子的对应是谁规定的？为后续指针学习打底。</p></details>',
  '内存模型'],
 ['元素之间，只有“前后相继”的关系吗？',
  '<p>回收 D002：排序前后的商品清单都是线性结构——序是逻辑关系，与住在哪里无关。</p><div class="quote '
  'compact-quote"><strong>线性表</strong>：n 个数据元素的有限序列，元素之间只有前后相继的关系。</div><p>名单、成绩单、每日股价……都先抽象成线性表。</p>',
  '顺序表示'],
 ['一个自然的选择：逻辑相邻，物理也相邻',
  '<p>把线性表的序关系，直接映射为内存中的连续布局。</p><div '
  'class="record-strip"><span>a₁</span><span>a₂</span><span>a₃</span><span>a₄</span><span>a₅</span><span>…</span></div><p>第 '
  '1 个元素之后紧接着第 2 个，依次排下去。<br>逻辑上的“下一个”，就是物理上的“隔壁”。</p><p '
  'class="small">这就是顺序存储表示，这样实现的线性表称为顺序表。</p>',
  '顺序表示'],
 ['知道第几个，怎样算出它住在哪？',
  '<div class="quote">LOC(aᵢ) = base + (i − 1) × L</div><ul><li>base：第 1 '
  '个元素的地址（基址）；</li><li>L：每个元素占用的字节数；</li><li>i − 1：第 i 个元素前面隔着 i − 1 '
  '个元素。</li></ul><p><strong>访问代价与 i 无关</strong>：无论找第几个，都只做一次乘法、一次加法。</p>',
  '顺序表示'],
 ['int a[8]; 的 a[i] 是什么？',
  '<p>C 编译器正是按地址公式工作的：</p><ul><li>数组名 a 记录首元素的地址（基址）；</li><li>sizeof(int) '
  '给出每个元素的字节数 L；</li><li>a[i] 是地址 base + i × L 处的内容。</li></ul><p class="small">C 的下标从 0 '
  '开始：第 1 个元素是 a[0]，地址即 base，对应公式中 i − 1 = 0。数组名与地址的关系先建立直观，指针的细节后续专门学习。</p>',
  '从数学到 C'],
 ['a[3] 与 a[0] 的地址，相差多少？',
  '<p>先预测：若 int 占 4 字节，&amp;a[3] 与 &amp;a[0] 的地址相差多少字节？</p><details><summary>说出你的预测与理由</summary><p>相差 '
  '3 个元素 × 4 字节 = 12 字节。理由就是地址公式：LOC(a₄) − LOC(a₁) = 3 × '
  'L。</p></details><p>运行 <code>code/addr_demo.c</code>，打印每个元素的真实地址，检查预测。</p><div class="quote '
  'compact-quote">先预测、再运行、再检查。</div>',
  '先预测再运行'],
 ['O(1) 意味着什么？',
  '<div class="columns"><div class="panel"><p><strong>100 件商品</strong></p><p>取第 57 '
  '件：一次地址计算。</p></div><div class="panel"><p><strong>100 万件商品</strong></p><p>取第 57 '
  '万件：仍然一次地址计算。</p></div></div><p>访问代价不随规模增长——这就是 O(1)，顺序表示用连续布局换来的回报。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>回收大 O：D002 已建立从精确计数到近似度量的认识——大 O 不关心具体几次，只关心随规模怎样增长。这里点一句即可：O(1) '
  '不是说“只要 1 纳秒”，而是说“规模翻倍，代价不变”。</p></details>',
  '访问'],
 ['新任务：转专业的新同学来了',
  '<p>班级名单按学号排好，新同学要按学号插到正确的位置。</p><div '
  'class="quote">这一次，主角不再是“找”，而是“改”。</div><p>插入一个元素，顺序表里会发生什么？</p>',
  '插入'],
 ['插到第 3 位，要搬几次？',
  '<p>8 人名单（按学号）：</p><div '
  'class="record-strip"><span>101</span><span>103</span><span>105</span><span>107</span><span>109</span><span>111</span><span>113</span><span>115</span></div><p>新同学学号 '
  '104，应插到第 3 位。</p><div class="quote">先自己答：要把 104 安顿好，需要搬动几个人？</div><details><summary>手工推演</summary><p>从 '
  '115 开始，105 到 115 共 6 人依次后移一位，腾出第 3 个位置，再放入 104。<br>插到第 i 位，要后移 n − i + 1 '
  '个元素。</p></details><p class="small">为什么从最后一个人开始搬？可以从后往前推演，避免覆盖还没搬走的元素。</p>',
  '插入'],
 ['删除，是搬运的另一面',
  '<div class="columns"><div class="panel"><p><strong>插入第 i 位</strong></p><p>后移 n − i + 1 '
  '个元素</p></div><div class="panel"><p><strong>删除第 i 位</strong></p><p>前移 n − i '
  '个元素</p></div></div><p>平均要搬约一半元素，最坏全搬：插入与删除都是 <strong>O(n)</strong>。</p>',
  '删除'],
 ['访问与增删，代价为何如此不同？',
  '<table><thead><tr><th>操作</th><th>代价</th><th>原因</th></tr></thead><tbody><tr '
  'class="focus-row"><td>按位置访问</td><td>O(1)</td><td>地址公式直接定位</td></tr><tr><td>插入</td><td>O(n)</td><td>为保持连续，整体后移腾位</td></tr><tr><td>删除</td><td>O(n)</td><td>为保持连续，整体前移补位</td></tr></tbody></table><div '
  'class="quote">知道什么时候不该用它，<br>和知道它是什么同样重要。</div><p '
  'class="small">代价对照就是顺序表示的适用边界：强项与边界来自同一个原因——连续布局。</p>',
  '对照收口'],
 ['为什么还愿意付搬运的代价？',
  '<p>很多场景里，访问远远多于增删：</p><ul><li>成绩表：一学期录入几次，查询成百上千次；</li><li>每日股价：每天新增一条，分析时反复读取；</li><li>向量运算：数据固定，反复按位置参与计算。</li></ul><div '
  'class="quote">没有最好的表示，只有适合任务的表示。</div><p class="small">呼应 D002：数据组织方式要回应操作的需要。</p>',
  '判断与选择'],
 ['数组，是数学向量的直接表示',
  '<p>向量 x 的第 i 个分量 ↔ <code>x[i]</code>：下标就是分量编号。</p><p>科学计算的一切——矩阵、BLAS '
  '基础线性代数库、有限元——都建在连续数组上。</p><div class="quote compact-quote">数学对象找到对的计算表示，整套计算工具就都能用上。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（控制在 3 '
  '分钟内）：连续内存对 CPU 缓存友好——取一个元素时，相邻元素已被一并预取；科学计算不用链表，正因为指针跳转破坏这种局部性。可结合 FEALPy '
  '等数值计算软件提一句：这门课学的表示选择，直接决定大规模计算的效率。</p></details>',
  '数学接口'],
 ['int a[8]; 住满了怎么办？',
  '<p>数组定长：第 9 位新同学来了，原来的 8 个位置住不下。</p><p><strong>扩容</strong> = '
  '重新分配一块更大的连续空间 + 把所有人整体搬过去。</p><div class="quote">定长，是顺序表示的第二个代价。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>预告不展开：有没有办法让扩容的代价平均下来很低？（每次扩一倍的均摊思想。）留一个悬念，后续再谈。</p></details>',
  '容量'],
 ['回到教材：线性表的定义与抽象数据类型',
  '<div class="quote compact-quote"><strong>教材定义</strong><br>线性表是 n '
  '个具有相同特性的数据元素的有限序列。</div><p>教材 2.3 '
  '节给出线性表的抽象数据类型，基本操作包括：</p><table><thead><tr><th>操作</th><th>作用</th></tr></thead><tbody><tr><td>InitList '
  '/ Length</td><td>构造空表 / 求表长</td></tr><tr><td>GetElem / '
  'LocateElem</td><td>按位置取元素 / 按值找位置</td></tr><tr><td>ListInsert / '
  'ListDelete</td><td>在指定位置插入 / 删除元素</td></tr></tbody></table><p class="small">ADT '
  '规定“能做什么、条件与结果是什么”，不规定“怎样存”。本讲的顺序表是这些操作的一种实现。见教材 2.1–2.3 节。</p>',
  '教材定义'],
 ['一元多项式，怎样住进数组？',
  '<p>P(x) = 3x² + 2x + 1</p><table><thead><tr><th>下标（次数）</th><th>0</th><th>1</th><th>2</th></tr></thead><tbody><tr><td>系数</td><td>1</td><td>2</td><td>3</td></tr></tbody></table><p>系数住数组，<strong>下标即次数</strong>——地址公式的又一个化身：知道次数，一次算出系数的住处。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>可展开（约 2 '
  '分钟）：多项式是数值计算的常客（插值、逼近）。数组表示让它可以直接交给 BLAS 等成熟计算库——选对表示，就是接入整个科学计算生态。</p></details>',
  '案例引入'],
 ['x¹⁰⁰⁰⁰ + 2x + 1，也要 10001 个位置吗？',
  '<p>按“下标即次数”，这个多项式要开一个 10001 个位置的数组，其中 9998 个位置住着 0。</p><div '
  'class="quote">绝大多数位置空着，只为保住“下标即次数”。<br>顺序表示在这里输了。</div><p>有没有一种表示，只给真正存在的项安排住处？——下次课回答。</p>',
  '留下问题'],
 ['把三个情境放在一起看',
  '<table><thead><tr><th>情境</th><th>数学</th><th>C</th></tr></thead><tbody><tr><td>快递柜：凭柜号直接开柜</td><td>序关系映射为连续布局</td><td>数组</td></tr><tr><td>名单：按学号插入新同学</td><td>LOC(aᵢ) '
  '= base + (i−1)×L</td><td>下标与 sizeof</td></tr><tr><td>多项式：下标即次数</td><td>第 i 项恒在其位的映射</td><td>coef[i] '
  '直接读写</td></tr></tbody></table><p class="small">三个情境，同一套机制：连续布局 + 地址公式。</p>',
  '案例收口'],
 ['搬运不是麻烦，是在维护什么？',
  '<div class="quote">表示不变量：无论怎么插入、删除，<br>第 i 个元素恒在 base + (i−1)×L。</div><p>每一次搬运，都是为了让这个不变量重新成立——正是它保证了访问的 '
  'O(1)。</p><details class="teacher-note"><summary>教学注记</summary><p>可展开：在变化中找不变的东西，是判断数据结构正确性的通用方法（呼应 '
  'D002“面对变化找不变”）。检查插入、删除代码的标准不是“跑通了”，而是“不变量是否仍成立”。</p></details>',
  '本质收口'],
 ['我怎样知道自己真的学会了？',
  '<ul><li>能写出地址公式，并解释每一项的含义；</li><li>能预测一次插入要搬几个元素，并说清为什么；</li><li>能举出一个不该用顺序表示的场景。</li></ul><div '
  'class="quote">把一次“我以为”变成一次有依据的修正。</div>',
  '学会了吗'],
 ['课后：教材导航与本周作业',
  '<p><strong>教材导航</strong>：精读 2.1–2.4 节。课件中带“教学注记”的页面，课后可以自行点开再看。</p><p><strong>本周作业</strong>（作业规范见 '
  'course/assignments/homework-guide.md）：</p><p><strong>A. 书本习题</strong>：第 2 '
  '章选择题 (2)(3)(9)(10)、算法设计题 (10)。选择题每题附一句“为什么选它”。</p><p><strong>B. '
  '扩展作业</strong>：补全 <code>code/seqlist.c</code> 的 insert '
  '搬运循环：先把循环注释掉、自己补全，再运行核对搬运次数是否符合预测；附预测与实测对照。</p><p '
  'class="small">自学练习（不提交）：修改 <code>code/addr_demo.c</code>，验证 double、char 等类型各自的 '
  'L；思考：如果名单经常变动，你会怎样组织？<br>挑战：设计实验，测量访问第 1 个与第 100 '
  '万个元素的时间差（提示：结果可能出乎意料——想想缓存）。</p>',
  '课后衔接']]
