DECK_ID = 'D002'
TITLE = '数据组织如何改变搜索'

# Each slide is [title, body_html, section_label].
SLIDES = [['组织数据，让计算更有效',
  '<div class="quote">前面的程序能找到答案。数据多了以后，还能怎样改进？</div><p>回看枚举 → 成批排除 → 为什么排序 → 双索引扫描与依据</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>开篇理念（约 3 分钟）：辩证法与主要矛盾——学习一门课，先抓住当前的主要矛盾。本课的主要矛盾不是"能记住多少种结构"，而是"数据的组织方式与搜索代价之间的关系"。</p></details>',
  '回到问题'],
 ['先解释，再继续',
  '<ul><li>迷宫中的 (r,c) 与 grid[r][c] 分别表达什么？</li><li>金额配对中的 i ≠ j 与 i &lt; j '
  '有什么关系？</li><li>目标100时输出无解，是程序错误吗？</li></ul>',
  '回看表达'],
 ['一次失败，能排除多少？',
  '<p>原价格：[18, 7, 25, 12, 33, 20]\u3000目标：32</p><div class="quote">18 + 7 = '
  '25，不够32。<br>能因此排除18元这件商品吗？</div><details><summary>比较一次检查与一批判断</summary><p>不能。换搭档会改变和值；这次只排除了这一对。</p></details><p>能否找到一种依据，一次排除一批不可能的配对？</p>',
  '从枚举出发'],
 ['33元，还需要逐个试搭档吗？',
  '<p>原价格：[18, 7, 25, 12, 33, 20]\u3000目标：32</p><div class="quote">最便宜的7元 + 最贵的33元 = '
  '40。<br>33元与其他商品配对，可能凑成32吗？</div><details><summary>说出排除整批配对的依据</summary><p>其余价格 p ≥ 7，所以33 + p ≥ 33 + '
  '7 = 40 &gt; 32。<br>与33元有关的五对都可以排除。</p></details>',
  '找到排除依据'],
 ['怎样方便地重复这样的判断？',
  '<p>排除33元后，剩下：[18, 7, 25, 12, 20]</p><div '
  'class="quote">下一次判断，还需要知道：<br>剩余商品中，哪件最便宜？哪件最贵？</div><p>可以反复遍历寻找，也可以先把价格按大小排好。</p><details><summary>我们尝试先排序</summary><p>有序排列的两端给出剩余最小、最大价格；排除端点后，向内移动即可继续判断。</p></details>',
  '由操作选择组织'],
 ['排序后，变了什么？',
  '<p class="small">回到完整输入：把六件商品按价格从小到大排列。</p><table><thead><tr><th>当前位置 '
  'k</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr></thead><tbody><tr><td>有序价格 '
  'a[k]</td><td>7</td><td>12</td><td>18</td><td>20</td><td>25</td><td>33</td></tr><tr><td>原商品编号</td><td>1</td><td>3</td><td>0</td><td>5</td><td>2</td><td>4</td></tr></tbody></table><p>商品没有改变，所在位置发生了变化。<br>有序价格记为 '
  'a[k]；原编号跟随商品一起移动。</p><p><span class="small">原登记顺序也要保留时，可考虑保留原记录并另建排序索引。</span></p>',
  '数据组织'],
 ['用两个索引标记左右两端',
  '<p>L、R 是两个数组索引，用整数变量记录。</p><div class="columns"><div class="panel"><p>开始位置</p><p>L = 0<br>R = n − '
  '1</p></div><div class="panel"><p>检查范围</p><p>只在 L &lt; R '
  '时检查，<br>保证是两件不同商品。</p></div></div><p>和太小，左端右移（++left）；和太大，右端左移（--right）。<br>和等于目标，返回这一对。接下来解释为什么能这样移动。</p>',
  '位置与动作'],
 ['先看配对，再说出排除依据',
  '<div data-pair="sorted"><div class="toolbar"><label>输入情形 <select aria-label="选择配对输入"><option '
  'value="0">六件商品 · 目标32</option><option value="1">六件商品 · 目标100（无解）</option><option value="2">16与16 · '
  '目标32</option><option value="3">只有16 · 目标32</option><option value="4">已排序 · '
  '目标37</option></select></label><button data-prev>上一步</button><button data-next>下一步</button><button '
  'data-reset>重置</button></div><div class="tiles"></div><div class="status" '
  'aria-live="polite"></div><div class="pair-bridge" aria-live="polite"></div></div>',
  '双索引扫描'],
 ['和太小，为什么能排除左端？',
  '<div class="quote">若 a[L] + a[R] &lt; T，那么对 L &lt; k ≤ R：<br>a[L] + a[k] ≤ a[L] + a[R] &lt; '
  'T。</div><p>右端已经是剩余范围内最大的价格。<br>左端与其余任何一件配对都不够，因此可以排除左端。</p>',
  '排除的依据'],
 ['和太大，为什么能排除右端？',
  '<div class="quote">若 a[L] + a[R] &gt; T，那么对 L ≤ k &lt; R：<br>a[k] + a[R] ≥ a[L] + a[R] &gt; '
  'T。</div><p>左端已经是剩余范围内最小的价格。<br>右端与其余任何一件配对都超出，因此可以排除右端。</p>',
  '排除的依据'],
 ['两件16元，和一件16元',
  '<div class="columns"><div class="panel"><p>[16, 16]，目标32</p><p>两件不同商品，可以配对。</p></div><div '
  'class="panel"><p>[16]，目标32</p><p>只有一件商品，没有解。</p></div></div><div class="quote">循环条件必须是 L &lt; '
  'R。</div><p>如果数组未排序，前面两个排除理由还成立吗？</p>',
  '条件检查'],
 ['同样的程序，能回答另一个问题吗？',
  '<ul><li>要求返回原商品编号：仅知道排序后位置够吗？</li><li>要求保留登记顺序：直接重排原数组合适吗？</li><li>要求输出全部配对：找到一组就返回还成立吗？</li></ul><div '
  'class="quote">任务变了，先检查需要保留的信息与停止条件。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>双 V 区分：验证（verification）——程序是否实现了设想的方法；确认（validation）——这个方法是否回答了原来的问题。"无解"可以是通过验证的正确答案；任务变了，要先重新确认。</p></details>',
  '检查边界'],
 ['把两个案例放在一起看',
  '<table><thead><tr><th>问题</th><th>迷宫</th><th>商品配对</th></tr></thead><tbody><tr><td>对象与关系</td><td>位置、通行、邻接</td><td>商品、价格、配对条件</td></tr><tr><td>表示与保存</td><td>地图数组及编码</td><td>价格、编号与顺序</td></tr><tr><td>组织计算</td><td>选择位置、保存探索记录</td><td>遍历配对、移动两端</td></tr><tr><td>答案应满足的条件</td><td>满足路径与通行条件</td><td>不同商品、目标金额</td></tr><tr><td>计算代价</td><td>探索工作与访问记录</td><td>枚举、排序、扫描与副本</td></tr></tbody></table>',
  '跨案例回看'],
 ['程序面对的真的是“商品”本身吗？',
  '<div class="columns"><div '
  'class="panel"><p><strong>现实中的一件商品</strong></p><p>编号：2<br>名称：……<br>价格：25元<br>类别：……<br>品牌：……</p></div><div '
  'class="panel"><p><strong>当前任务</strong></p><p>找两件不同商品，使价格之和为32元，并能指出是哪两件。</p><div '
  'class="quote">当前至少要保留：<br>(商品编号, 价格)</div></div></div><p '
  'class="small">本例中，编号、价格等可供计算机处理的信息是数据。现实对象包含很多信息；计算时选择任务需要表达和区分的部分。</p>',
  '从具体对象到专业术语'],
 ['一条商品记录里，有哪些信息？',
  '<p>在当前建模中，用 <strong>eᵢ = (idᵢ, pᵢ)</strong> 表示一条商品记录。</p>\n'
  '<table><thead><tr><th>本例</th><th>专业术语</th><th>怎样理解</th></tr></thead><tbody>\n'
  '<tr class="focus-row"><td>一条记录 (2,25)</td><td>数据元素</td><td>作为一个整体组织和处理</td></tr>\n'
  '<tr><td>编号 2、价格 25</td><td>数据项</td><td>组成数据元素的具体信息</td></tr>\n'
  '<tr><td>具有共同属性的商品记录的集合</td><td>数据对象</td><td>从一条记录看到同类记录的集合</td></tr>\n'
  '</tbody></table><p>在本例中，一条记录对应一个数据元素，字段对应数据项。</p>\n'
  '<p class="small">这里是结合商品案例的解释；现实商品、数据记录与记录集合需要分清。</p>',
  '从具体对象到专业术语'],
 ['商品记录之间的逻辑关系',
  '<p>按登记次序排列：</p><div '
  'class="record-strip"><span>(0,18)</span><span>(1,7)</span><span>(2,25)</span><span>(3,12)</span><span>(4,33)</span><span>(5,20)</span></div>\n'
  '<p>按价格重新排列：</p><div '
  'class="record-strip"><span>(1,7)</span><span>(3,12)</span><span>(0,18)</span><span>(5,20)</span><span>(2,25)</span><span>(4,33)</span></div>\n'
  '<div class="quote compact-quote"><strong>逻辑结构</strong>关注数据元素之间的逻辑关系。</div>\n'
  '<p>排序前后都可以是线性结构；改变了先后关系，排序后价格还满足非降序。</p>\n'
  '<details><summary>双索引扫描还需要什么条件？</summary><p>价格非降序。两端因此给出剩余价格的最小值和最大值。</p></details>',
  '从具体对象到专业术语'],
 ['抽象数据类型',
  '<p>除了数据及其关系，还需要规定对这些数据可以进行哪些操作。</p>\n'
  '<div class="quote '
  'compact-quote"><strong>教材定义</strong><br>抽象数据类型是指由用户定义的、表示应用问题的数学模型，以及定义在这个模型上的一组操作的总称。</div>\n'
  '<table><thead><tr><th>三个组成部分</th><th>商品记录序列中的对应</th></tr></thead><tbody>\n'
  '<tr><td>数据对象</td><td>具有本任务所需共同属性的商品记录的集合</td></tr>\n'
  '<tr><td>数据对象上关系的集合</td><td>记录之间的先后关系</td></tr>\n'
  '<tr><td>基本操作的集合</td><td>求长度、按位置取得记录等</td></tr>\n'
  '</tbody></table><p class="small">抽象数据类型（Abstract Data Type，ADT）。本讲只选取相关操作举例，完整操作集合在后续学习线性表时展开。</p>',
  '教材接口 · 数学模型与操作'],
 ['一项操作的条件与结果',
  '<table><thead><tr><th>位置 '
  'k</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr></thead><tbody>\n'
  '<tr><td>商品记录</td><td>(1,7)</td><td>(3,12)</td><td>(0,18)</td><td>(5,20)</td><td>(2,25)</td><td>(4,33)</td></tr></tbody></table>\n'
  '<p><strong>操作：按位置取得商品记录</strong></p><ul>\n'
  '<li>给定：记录序列及位置 k；序列长度为 n。</li>\n'
  '<li>条件：0 ≤ k &lt; n。</li>\n'
  '<li>结果：返回位置 k 上的记录，原序列保持不变。</li></ul>\n'
  '<p>k = 2 时，取得 (0,18)：原编号为 0，价格为 18。</p>\n'
  '<details><summary>这里规定了必须怎样存储吗？</summary><p>没有。这里说明操作的条件和结果，具体存储与实现方式可以选择。</p></details>',
  '抽象数据类型 · 基本操作'],
 ['记录与关系怎样存入计算机？',
  '<table><thead><tr><th>数组位置 '
  'k</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr></thead><tbody>\n'
  '<tr><td>price[k]</td><td>7</td><td>12</td><td>18</td><td>20</td><td>25</td><td>33</td></tr>\n'
  '<tr><td>id[k]</td><td>1</td><td>3</td><td>0</td><td>5</td><td>2</td><td>4</td></tr></tbody></table>\n'
  '<div class="quote compact-quote"><strong>教材表述</strong><br>存储结构是逻辑结构在计算机中的存储表示。</div>\n'
  '<p>同一位置的 id[k] 与 price[k] 共同表示一条记录；数组位置承载当前次序。</p>\n'
  '<p>取得位置 k 上的记录，可以通过读取 id[k] 和 price[k] 实现。</p>\n'
  '<p class="small">同一种逻辑结构可以有不同的存储方式。教材介绍顺序存储结构和链式存储结构，后续结合线性表展开。</p>',
  '从具体对象到专业术语'],
 ['数据结构与算法',
  '<p class="small">教材从逻辑结构和存储结构两个方面讨论数据结构，也关注对数据进行的操作。</p>\n'
  '<div class="quote compact-quote"><strong>教材定义</strong><br>算法是为了解决某类问题而规定的一个有限长的操作序列。</div>\n'
  '<p><strong>本例：对已按价格非降序排列的记录进行扫描。</strong></p>\n'
  '<ol><li>初始化 L = 0、R = n − 1。</li>\n'
  '<li>当 L &lt; R，读取两端价格，求和并与目标比较。</li>\n'
  '<li>和相等则返回；和太小移动 L，和太大移动 R，继续检查。</li>\n'
  '<li>搜索结束仍未找到，则报告无解。</li></ol>\n'
  '<p class="small">算法组织操作；操作也可由算法实现。代码返回排序后的位置，取得原编号还需对应关系。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>课堂讨论沉淀：程序是执行过程的描述，不是执行本身——有限行的代码描述的是一类执行；真正的执行由输入驱动、在运行中展开。这一区分在 D006 递归（调用栈把四行代码展开成任意深的执行）上将完整兑现。</p></details>',
  '从专业术语回到课程主线'],
 ['算法的五个特性',
  '<table><thead><tr><th>教材中的特性</th><th>本例中的体现</th></tr></thead><tbody>\n'
  '<tr><td>有穷性</td><td>每次未找到时范围缩小，最终结束</td></tr>\n'
  '<tr><td>确定性</td><td>比较结果明确决定返回或移动哪一端</td></tr>\n'
  '<tr><td>可行性</td><td>取值、求和、比较、更新索引均可执行</td></tr>\n'
  '<tr><td>输入</td><td>已排序的记录序列、目标金额</td></tr>\n'
  '<tr><td>输出</td><td>一组配对，或无解结果</td></tr></tbody></table>\n'
  '<p class="small">一般算法可以有零个或多个输入、一个或多个输出；输入不限定为键盘输入。</p>\n'
  '<details><summary>删去移动索引的操作，有限行代码一定会结束吗？</summary><p>不一定。可能反复检查同一对；描述有限不能代替终止理由。</p></details>',
  '教材接口 · 从案例检查特性'],
 ['枚举代价：由配对条件数出来',
  '<div class="quote">(n − 1) + (n − 2) + … + 1 = n(n − 1) / '
  '2</div><table><thead><tr><th>商品数</th><th>6</th><th>100</th><th>1,000</th><th>100,000</th></tr></thead><tbody><tr><td>完整枚举配对数</td><td>15</td><td>4,950</td><td>499,500</td><td>4,999,950,000</td></tr></tbody></table><p><span '
  'class="small">计数来自 0 ≤ i &lt; j &lt; n。找到一组提前停止时，实际次数可能更少。</span></p><p>问题规模是商品数量 '
  'n。时间复杂度关注执行时间随规模增长的变化。</p>\n'
  '<p>按每次配对检查为常数代价计，枚举最坏时间复杂度为 <strong>O(n²)</strong>。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>数学接口展开（约 5 分钟）：克莱姆法则——按行列式定义直接计算是 O(n!) 级别，n 稍大即超出可算范围；学习行列式性质把代价降下来，最终走向高斯消元/LU 的 O(n³)。同一条链：定义 → 性质 → 算法，与本页"枚举 O(n²) → 排序＋扫描 O(n)"同构。</p></details>',
  '规模与代价'],
 ['扫描很快，排序也要花时间',
  '<table><thead><tr><th>比较对象</th><th>时间代价</th><th>额外空间</th></tr></thead><tbody>\n'
  '<tr><td>枚举配对</td><td>最坏 O(n²)</td><td>辅助变量 O(1)</td></tr>\n'
  '<tr><td>已排序数据上的扫描</td><td>最坏 O(n)</td><td>辅助变量 O(1)</td></tr>\n'
  '<tr><td>无序输入，先排序再扫描</td><td>排序＋扫描</td><td>取决于排序与是否复制</td></tr></tbody></table>\n'
  '<p>保留原顺序而另建 n 个位置的排序索引，需要 O(n) 的额外空间。</p>\n'
  '<p class="small">空间复杂度描述空间需求随规模的增长；本表只统计额外空间。扫描最多检查 n − 1 对（n ≥ 2）。</p>\n'
  '<details><summary>教材怎样评价算法？</summary><p>正确性、可读性、健壮性和高效性。步骤明确不代表结果正确；“无解”可以是合法结果。</p></details>',
  '总体代价'],
 ['从商品记录，到一次数据查询',
  '<p>“找到满足金额条件的两条不同商品记录”，可以看作一次查询。</p><div class="columns"><div class="panel"><p>只有几件 → '
  '十万件</p><p>候选数量、访问方式和存储开始影响可行性。</p></div><div class="panel"><p>只查一次 → '
  '反复查询</p><p>预先排序的工作能否复用？价格变化后还有效吗？</p></div></div><p><span '
  'class="small">数据处理还关心身份、字段、查询和更新；规模只是其中一个条件。</span></p><details '
  'class="teacher-note"><summary>教学注记</summary><p>现实规模延伸：外卖骑手调度（每天几十万次查询，预处理必须可复用）；气候模拟与核聚变（百亿量级的变量，算法选择决定问题可算与否）；分布式存储（数据分散在多台机器，通信代价开始主导）。规模与反复查询，是让"数据组织"变成硬约束的两个条件。</p></details>',
  '数据处理视角'],
 ['后面的课程，会怎样接上？',
  '<table><thead><tr><th>基本逻辑结构</th><th>关系特征</th><th>课程中的联系</th></tr></thead><tbody>\n'
  '<tr><td>集合结构</td><td>只考虑同属一个集合</td><td>先辨认元素与集合</td></tr>\n'
  '<tr><td>线性结构</td><td>元素之间有先后关系</td><td>线性表、栈、队列</td></tr>\n'
  '<tr><td>树结构</td><td>分支与层次关系</td><td>树</td></tr>\n'
  '<tr><td>图结构</td><td>一般连接关系</td><td>图与搜索</td></tr></tbody></table>\n'
  '<p>线性表继续讨论操作与存储；查找与排序继续研究怎样访问、整理数据。</p>\n'
  '<p class="small">分类依据是元素之间的逻辑关系；具体存储和算法需要另行选择。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>数学接口：线性空间 = 集合上加结构（加法与数乘运算）；数据结构同样 = 数据集合上加关系结构。树形结构的生活类比：国家行政层级——省管市、市管县，层次是屏蔽复杂性的手段（D008 正式展开）。</p></details>',
  '课程地图'],
 ['在几种表达之间来回检查',
  '<ul><li>情境 → 数学：条件是否完整，目标是否明确？</li><li>数学 → 程序：下标、判断和循环是否对应？</li><li>程序 → '
  '情境：输出是否回答了原来的问题？</li><li>数据变化 → 方法：原来的条件和表示还成立吗？</li></ul><details '
  'class="teacher-note"><summary>教学注记</summary><p>显式命名费曼学习法：能讲给别人听，才算真的懂。同时提醒 AI 依赖问题：工具暴露懒的本质——AI 可以参与过程，但"先自己尝试、自己核对"不能让渡（与作业规范同一口径）。</p></details>',
  '学习方法'],
 ['我怎样知道自己真的学会了？',
  '<ul><li>不看动画，解释该移动哪一端。</li><li>给出一个让错误方法失败的输入。</li><li>修改程序，并解释结果为何变化。</li><li>说清楚帮助来自哪里，自己怎样核对。</li></ul><div '
  'class="quote">把一次“我以为”变成一次有依据的修正。</div><details '
  'class="teacher-note"><summary>教学注记</summary><p>收口一句话（拟人化总结）：把人看成机器——建模世界，就是设计你自己的数据结构：你选择保留什么信息、记住什么关系，决定了你能多快地"搜索"到答案。</p></details>',
  '学习方法'],
 ['课后：教材导航与本周作业',
  '<p><strong>A 部分 · 书本习题</strong>：第 1 章选择题 5(1)–(6)、第 6 题 (2)(3)(5)、简述题 '
  '4。选择题每题附一句"为什么选它"。</p>\n'
  '<p><strong>B 部分 · 扩展作业</strong>：</p>\n'
  '<ol><li><strong>排序映射：</strong>写出位置、原编号、价格的对应；辨认数据元素、数据项与被改变的关系。</li>\n'
  '<li><strong>目标 37：</strong>运行 <code>code/pair_sum_sorted.c</code> 前先写下你预测的扫描轨迹，再运行核对；解释一次排除并写出不等式，说明为什么会终止。</li>\n'
  '<li><strong>程序核对：</strong>说明输入是否已排序、输出位置的含义，以及未被计入的排序与存储成本。</li></ol>\n'
  '<p class="small">挑战（选做）：修改程序输出全部配对。AI 使用规范与提交格式见作业规范（course/assignments/homework-guide.md）：带着思考参与整个过程，附过程记录。</p>',
  '课后衔接'],
 ['回到教材第一章',
  '<table><thead><tr><th>读到教材概念时</th><th>回想课堂案例</th></tr></thead><tbody>\n'
  '<tr><td>数据、数据对象、数据元素与数据项</td><td>商品信息、记录集合、一条记录及其字段</td></tr>\n'
  '<tr><td>逻辑结构、存储结构</td><td>记录的先后关系与对应数组</td></tr>\n'
  '<tr><td>抽象数据类型</td><td>数据、关系和基本操作的要求</td></tr>\n'
  '<tr><td>算法、特性与评价</td><td>扫描过程、终止理由和结果要求</td></tr>\n'
  '<tr><td>时间、空间复杂度</td><td>检查次数、排序与额外索引</td></tr></tbody></table>\n'
  '<p>哪一个教材概念，你还不能用商品配对案例解释清楚？</p>\n'
  '<p class="small">阅读第一章对应内容与小结，再回看课件中带"教学注记"页面的案例说明。</p>',
  '教材接口 · 预习与复习'],
 ['排好序的清单，世界却一直在变，怎么办？',
  '<p>排序与双索引扫描让搜索更快。</p><div class="quote">但新商品上架、旧商品下架——<br>清单本身一直在变。</div><p>数据组织不仅要“找得快”，还要“变得起”。</p><p>下次课：数据住进内存，到底住成什么样？</p>',
  '留下问题']]
