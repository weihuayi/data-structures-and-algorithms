DECK_ID = 'D002'
TITLE = '数据组织如何改变搜索'

# Each slide is [title, body_html, section_label].
SLIDES = [['组织数据，让计算更有效',
  '<div class="quote">前面的程序能找到答案。数据多了以后，还能怎样改进？</div><p>回看枚举 → 成批排除 → 为什么排序 → 双索引扫描与依据</p>',
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
  '40。<br>33元与其他商品配对，可能凑成32吗？</div><details><summary>说出排除整批配对的依据</summary><p>其余价格 p ≥ 7，所以33 + p ≥ 33 + 7 = '
  '40 &gt; 32。<br>与33元有关的五对都可以排除。</p></details>',
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
  'data-reset>重置</button></div><div class="tiles"></div><div class="status" aria-live="polite"></div><div '
  'class="pair-bridge" aria-live="polite"></div></div>',
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
  'class="quote">任务变了，先检查需要保留的信息与停止条件。</div>',
  '检查边界'],
 ['把两个案例放在一起看',
  '<table><thead><tr><th>问题</th><th>迷宫</th><th>商品配对</th></tr></thead><tbody><tr><td>对象与关系</td><td>位置、通行、邻接</td><td>商品、价格、配对条件</td></tr><tr><td>表示与保存</td><td>地图数组及编码</td><td>价格、编号与顺序</td></tr><tr><td>组织计算</td><td>选择位置、保存探索记录</td><td>遍历配对、移动两端</td></tr><tr><td>答案应满足的条件</td><td>满足路径与通行条件</td><td>不同商品、目标金额</td></tr><tr><td>计算代价</td><td>探索工作与访问记录</td><td>枚举、排序、扫描与副本</td></tr></tbody></table>',
  '跨案例回看'],
 ['程序面对的真的是“商品”本身吗？',
  '<div class="columns"><div '
  'class="panel"><p><strong>现实中的一件商品</strong></p><p>编号：2<br>名称：……<br>价格：25元<br>类别：……<br>品牌：……</p></div><div '
  'class="panel"><p><strong>当前任务</strong></p><p>找两件不同商品，使价格之和为32元，并能指出是哪两件。</p><div '
  'class="quote">当前至少要保留：<br>(商品编号, 价格)</div></div></div><p '
  'class="small">现实对象包含很多信息；计算时只选择当前任务需要表达和区分的信息。</p>',
  '从具体对象到专业术语'],
 ['一条商品记录里，有哪些信息？',
  '<p>在当前建模中，用 <strong>eᵢ = (idᵢ, pᵢ)</strong> 表示第 i 件商品需要保留的数据。</p><table><thead><tr><th>商品编号 id</th><th>价格 '
  'p</th><th>怎么看</th></tr></thead><tbody><tr><td>0</td><td>18</td><td>一条商品记录</td></tr><tr '
  'class="focus-row"><td>2</td><td>25</td><td><strong>作为一个整体处理</strong></td></tr><tr><td>5</td><td>20</td><td>一条商品记录</td></tr></tbody></table><div '
  'class="columns"><div class="panel"><p><strong>数据元素（Data '
  'Element）</strong></p><p>当前数据集合中，作为一个整体组织和处理的基本对象。</p><p>本例：一条商品记录 eᵢ。</p></div><div '
  'class="panel"><p><strong>数据项（Data Item）</strong></p><p>组成一个数据元素的具体信息。</p><p>本例：商品编号、价格。</p></div></div><p '
  'class="small">业务语言“一件商品” → 数据表达“一条记录” → 数据结构术语“一个数据元素”；记录中的字段对应数据项。</p>',
  '从具体对象到专业术语'],
 ['有了很多数据元素，还缺什么？',
  '<p>先有这些商品记录：</p><div '
  'class="record-strip"><span>(0,18)</span><span>(1,7)</span><span>(2,25)</span><span>(3,12)</span><span>(4,33)</span><span>(5,20)</span></div><p>按价格重新组织后：</p><div '
  'class="record-strip '
  'ordered"><span>(1,7)</span><span>→</span><span>(3,12)</span><span>→</span><span>(0,18)</span><span>→</span><span>(5,20)</span><span>→</span><span>(2,25)</span><span>→</span><span>(4,33)</span></div><div '
  'class="quote"><strong>逻辑结构（Logical '
  'Structure）</strong>关注数据元素之间具有怎样的逻辑关系。</div><p>本例中，商品记录被组织成一个<strong>线性次序</strong>；排序后，这个次序与价格的非降序一致：</p><p '
  'style="text-align:center">pᵢ₀ ≤ pᵢ₁ ≤ ··· ≤ pᵢₙ₋₁</p><p class="small">排序是一种操作；排序后的线性次序关系是我们随后利用的结构信息。</p>',
  '从具体对象到专业术语'],
 ['逻辑上的关系，怎样真正放进计算机？',
  '<p>逻辑上，我们希望保存按价格排列的商品记录序列。</p><table><thead><tr><th>数组位置 '
  'k</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr></thead><tbody><tr><td>price[k]</td><td>7</td><td>12</td><td>18</td><td>20</td><td>25</td><td>33</td></tr><tr><td>id[k]</td><td>1</td><td>3</td><td>0</td><td>5</td><td>2</td><td>4</td></tr></tbody></table><div '
  'class="quote"><strong>存储结构（Storage '
  'Structure）</strong>关注数据元素及其逻辑关系在计算机中的具体表示方式。</div><p>这里用两个对应数组保存价格与商品编号，数组位置 0,1,2,… 承载当前线性次序。</p><div '
  'class="columns"><div class="panel"><p><strong>逻辑结构</strong></p><p>商品记录之间按价格形成线性次序。</p></div><div '
  'class="panel"><p><strong>存储结构</strong></p><p>用数组及其下标具体保存这些记录和次序。</p></div></div><p '
  'class="small">同一种逻辑结构可以有不同的存储方式；当前阶段先使用已经熟悉的数组。</p>',
  '从具体对象到专业术语'],
 ['从这些术语，回到“数据结构与算法”',
  '<div '
  'class="concept-flow"><div><strong>现实对象</strong><span>商品</span></div><b>→</b><div><strong>数据元素</strong><span>一条记录；由数据项 '
  'id、price '
  '描述</span></div><b>→</b><div><strong>逻辑结构</strong><span>按价格的线性次序</span></div><b>→</b><div><strong>存储结构</strong><span>数组 '
  '+ 下标</span></div><b>→</b><div><strong>算法操作</strong><span>双索引缩小范围</span></div></div><div '
  'class="columns"><div class="panel"><p><strong>数据结构（Data '
  'Structure）</strong></p><p>围绕数据元素及其关系，选择合适的组织与表示方式，以支持需要的操作。</p></div><div '
  'class="panel"><p><strong>算法（Algorithm）</strong></p><p>在明确输入、表示和条件上，用有限、明确、可执行的步骤完成计算任务。</p></div></div><div '
  'class="quote">本例：有序关系提供成批排除的依据；数组支持访问两端；双索引扫描利用这些条件逐步缩小候选范围。</div>',
  '从专业术语回到课程主线'],
 ['枚举代价：由配对条件数出来',
  '<div class="quote">(n − 1) + (n − 2) + … + 1 = n(n − 1) / '
  '2</div><table><thead><tr><th>商品数</th><th>6</th><th>100</th><th>1,000</th><th>100,000</th></tr></thead><tbody><tr><td>完整枚举配对数</td><td>15</td><td>4,950</td><td>499,500</td><td>4,999,950,000</td></tr></tbody></table><p><span '
  'class="small">计数来自 0 ≤ i &lt; j &lt; n。找到一组提前停止时，实际次数可能更少。</span></p>',
  '规模与代价'],
 ['扫描很快，排序也要花时间',
  '<table><thead><tr><th>阶段</th><th>成本说明</th></tr></thead><tbody><tr><td>枚举配对</td><td>最坏检查 n(n − 1)/2 '
  '对</td></tr><tr><td>有序数组上的双索引扫描</td><td>每次缩小范围，最多检查 n − 1 对（n ≥ 2）</td></tr><tr><td>从无序数据开始</td><td>总成本 = '
  '排序成本 + 扫描成本</td></tr></tbody></table><p class="small">先看检查次数怎样随数据规模增长；增长上界的大O记号见讲义。</p>',
  '总体代价'],
 ['从商品记录，到一次数据查询',
  '<p>“找到满足金额条件的两条不同商品记录”，可以看作一次查询。</p><div class="columns"><div class="panel"><p>只有几件 → '
  '十万件</p><p>候选数量、访问方式和存储开始影响可行性。</p></div><div class="panel"><p>只查一次 → '
  '反复查询</p><p>预先排序的工作能否复用？价格变化后还有效吗？</p></div></div><p><span '
  'class="small">数据处理还关心身份、字段、查询和更新；规模只是其中一个条件。</span></p>',
  '数据处理视角'],
 ['后面的课程，会怎样接上？',
  '<table><thead><tr><th>当前留下的问题</th><th>后续学习</th></tr></thead><tbody><tr><td>数据不断增加、删除，怎样组织？</td><td>线性表与存储方式</td></tr><tr><td>迷宫中下一步处理哪个候选？</td><td>栈、队列与搜索</td></tr><tr><td>数据有层次或复杂连接，怎样表达？</td><td>树与图</td></tr><tr><td>怎样快速找到、整理需要的数据？</td><td>查找与排序</td></tr></tbody></table>',
  '课程地图'],
 ['在几种表达之间来回检查',
  '<ul><li>情境 → 数学：条件是否完整，目标是否明确？</li><li>数学 → 程序：下标、判断和循环是否对应？</li><li>程序 → 情境：输出是否回答了原来的问题？</li><li>数据变化 → '
  '方法：原来的条件和表示还成立吗？</li></ul>',
  '学习方法'],
 ['我怎样知道自己真的学会了？',
  '<ul><li>不看动画，解释该移动哪一端。</li><li>给出一个让错误方法失败的输入。</li><li>修改程序，并解释结果为何变化。</li><li>说清楚帮助来自哪里，自己怎样核对。</li></ul><div '
  'class="quote">把一次“我以为”变成一次有依据的修正。</div>',
  '学习方法'],
 ['课后：完成三个对应任务',
  '<ol><li>排序映射：写出新位置、原编号与价格的对应。</li><li>目标37：记录双索引扫描轨迹，解释一次排除并写出不等式。</li><li>程序核对：运行有序扫描示例，说明输出位置与排序成本的边界。</li></ol><p '
  'class="small">输出全部配对为可选挑战。具体练习要求以课程发布内容为准。</p>',
  '课后练习'],
 ['这一阶段，你改变了哪个判断？',
  '<div class="quote">“原来我以为 ______，现在我知道 ______，依据是 ______。”</div><p>再写一个仍未解决的问题。</p><p><span '
  'class="small">带着这个问题进入后续学习。完整课件、讲义和源码可以反复阅读。</span></p>',
  '回看']]
