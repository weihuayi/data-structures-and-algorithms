DECK_ID = 'D007'
TITLE = '串与模式匹配'

# Each slide is [title, body_html, section_label].
SLIDES = [['串与模式匹配',
  '<p class="lead">在一篇文章里找一个词，计算机怎么找？</p><p>数据结构与算法 · D007</p><p '
  'class="small">教材对应：《数据结构（C语言版）（第3版）》第 4 章 串、数组和广义表，4.1–4.3 '
  '节（4.4–4.5 自学导航）</p>',
  '课程名'],
 ['在一篇文章里找一个词，你会怎么找？',
  '<p>回收 D006 留问。不急着讲算法，先说你自己会怎么找：</p><div class="quote">大概率是：从头开始，'
  '逐个字符比过去。</div><p>这个直觉就是今天第一个算法的全部内容。问题是——它够好吗？</p>',
  '回到问题'],
 ['串：内容受限的线性表',
  '<p>第 2 章的线性表，元素可以是任何东西；如果规定<strong>元素只能是字符</strong>，就得到串：</p><div '
  'class="quote">串 = 内容受限的线性表。<br>特殊不在结构上，在内容上。</div><p>C '
  '语言里你早就见过它：字符串就是 <strong>\'\\0\' 结尾的字符数组</strong>——回收 D003 '
  '的连续布局，每个字符住在一个字节里，地址同样能用公式算。</p>',
  '串是什么'],
 ['串的术语：先约定语言',
  '<div class="quote compact-quote"><strong>教材定义</strong><br>串（string）是由零个或多个字符组成的有限序列，'
  '记为 s = "a₁a₂…aₙ"。串中字符的数目 n 称为串的<strong>长度</strong>；零个字符的串称为<strong>空串</strong>；'
  '串中任意个连续字符组成的子序列称为<strong>子串</strong>，包含子串的串称为<strong>主串</strong>；'
  '子串在主串中的位置，以子串第一个字符在主串中的位置表示。</div><ul><li>空串 ≠ 空格串："　"长度是 '
  '1，不是 0；</li><li>例：a="BEI"、b="JING"、c="BEIJING"——a 是 c 的子串，位置是 1；b 是 c 的子串，位置是 '
  '4。</li></ul><p class="small">见教材 4.1 节：串的定义。</p>',
  '教材定义'],
 ['一种植物病毒，怎么变成计算问题？',
  '<p>教材案例 4.1：植物双生病毒是全球性 DNA 病毒，危害苹果、桑树等多种树种。研究人员不断从新树种中检测到新病毒'
  '（苹果双生病毒 AGV、桑花叶萎缩相关病毒 MMDaV）。</p><p><strong>检测问题</strong>：给一株植物的 DNA '
  '序列，判断某种病毒的 DNA 序列是否在其中出现过。</p><p class="small">DNA '
  '序列就是字母组成的串——这不是修辞，是建模的第一步。见教材 4.2 节案例引入。</p>',
  '案例引入'],
 ['把检测翻译成模式匹配',
  '<div class="quote compact-quote"><strong>教材定义</strong><br>设 S 为主串（正文串），T 为子串（模式）。'
  '在主串 S 中查找与模式 T 相匹配的子串，若成功，确定其第一个字符在 S 中的位置——子串的定位运算称为<strong>模式匹配</strong>。'
  '</div><ul><li>植物 DNA 序列 = 主串 S；病毒 DNA 序列 = 模式 T；</li><li>匹配成功 → '
  '感染；匹配失败 → 未感染。</li></ul><p>搜索引擎、拼写检查、入侵检测、病毒特征码——同一个问题，不同的主串和模式。</p>',
  '建模'],
 ['最直观的找法：BF 算法',
  '<p>BF（Brute-Force，朴素匹配）：主串指针 i、模式指针 j。</p><pre>比较 S[i] 与 T[j]：\n    '
  '相等　→ i、j 各进一步，继续比；\n    不等　→ i 退回 i−j+2（主串下一个起点），j 退回 '
  '1，重新来；\n直到 j 越界（匹配成功，位置 = i−m）或 i 越界（失败）。</pre><p '
  'class="small">见教材 4.3.3 节算法 4.1。这就是你第 2 页凭直觉想出的办法。</p>',
  'BF'],
 ['手工推演：BF 的五趟',
  '<p>S = "abcdefghi"，T = "abcdx"。先自己动手：一共几趟？每趟比几次？再用推演核对：</p><div '
  'data-match="bf"><div class="toolbar"><button data-prev>上一步</button><button data-next>开始推演</button><button '
  'data-reset>重置</button></div><div class="mem-counter"></div><div class="match-zones"></div><div '
  'class="status" aria-live="polite"></div></div><p>注意第 2、3、4 '
  '趟：<strong>还没开始比，结局就已经定了</strong>——为什么？</p>',
  '手工推演'],
 ['失配时，我们扔掉了什么？',
  '<p>第 1 趟已经告诉我们：S 的前 4 个字符是 a、b、c、d。</p><ul><li>所以 S 的第 2、3、4 位是 b、c、d，'
  '<strong>已知</strong>它们都不等于 T 的首字符 a；</li><li>第 2、3、4 趟是去验证一件已经知道答案的事。</li></ul><div '
  'class="quote">BF 浪费的不只是时间，是信息。<br>失配不是纯粹的失败——它携带信息。</div><p>最坏情形：S = '
  '"aaaaaa…ab"，T = "aaab"，每趟都比到最后才失败——O(n·m)。</p>',
  '浪费'],
 ['教材例 4.1：再看一次浪费',
  '<p>S = "abaabaabcde"，T = "abaabc"（教材例 4.1）：</p><table><thead><tr><th>趟次</th><th>起点</th><th>结果</th><th>比较次数</th></tr></thead><tbody><tr><td>1</td><td>1</td><td>比到第 '
  '6 个字符失配（a≠c）</td><td>6</td></tr><tr><td>2</td><td>2</td><td>b≠a，立即失败</td><td>1</td></tr><tr><td>3</td><td>3</td><td>第 '
  '2 个字符失配</td><td>2</td></tr><tr class="focus-row"><td>4</td><td>4</td><td>全部相等，匹配成功，位置 '
  '4</td><td>6</td></tr></tbody></table><p>共 15 次比较。第 1 趟比出来的 5 个字符，后面真的被用上了吗？</p>',
  'BF'],
 ['主串指针一定要回头吗？',
  '<p>BF 每次失配，i 都要退回去。可是失配点左边的字符，我们全都见过、全都认识。</p><div '
  'class="quote">已匹配的信息，能不能不浪费？<br>主串指针 i，能不能不回头？</div><p>教材提出理解 KMP '
  '的两个问题：<strong>① i 为什么可以不回溯？② j 该回溯到什么位置？</strong>接下来逐一回答。</p>',
  'KMP'],
 ['第一问：i 为什么不回头？',
  '<p>失配发生在 S 的第 i 位。此时 i 左边的 j−1 个字符，与 T 的前 j−1 个字符<strong>逐一相等</strong>——这是我们刚比出来的事实。</p><p>所以任何一个'
  '“更早的起点”要不要试，<strong>不用看主串，查模式自己就能判断</strong>：T 的前几个字符，和 T 失配点左边那几个字符，对得上吗？</p><div '
  'class="quote">i 不回头的前提：回头能知道的事，<br>不回头也能知道。</div>',
  'KMP'],
 ['第二问：j 退到哪里？谁说了算？',
  '<p>例 4.1 第 1 趟：i=6、j=6 处失配。此时 S 第 4、5 位是 "ab"，恰好等于 T 的前两个字符 '
  '"ab"。</p><p>于是第 2 趟不必从 S 第 2 位重来：<strong>i 停在 6 不动，j 退到 3</strong> 继续比——相当于把模式向右滑，'
  '让它的前缀对准主串中已经确认相等的部分。</p><div class="quote">j 退到哪，由模式的自相似结构决定，<br>与主串无关。</div>',
  'KMP'],
 ['next[j]：把“退到哪”算出来',
  '<div class="quote compact-quote"><strong>教材定义</strong><br>next[j]：失配发生在模式第 j 位时，j '
  '应退到的位置。设 T′ 为失配点左边的子串 "t₁t₂…tⱼ₋₁"：若 T′ 存在相等的<strong>前缀与后缀</strong>，取其最大长度 '
  'l_max，则 next[j] = l_max + 1；不存在则 next[j] = 1；规定 next[1] = 0。</div><p '
  'class="small">见教材 4.3.3 节式（4-1）。前缀后缀相等 = 模式开头的一段，在失配点左边刚刚出现过。</p><p>注意：这个定义里<strong>没有出现主串</strong>。</p>',
  'next'],
 ['手工推演：T = "abaabc" 的 next 表',
  '<p>按定义手算。先算两个：next[4] 与 next[6]，其余自己补齐。</p><details><summary>next[4] '
  '怎么算？</summary><p>T′ = "aba"。前缀候选：a、ab；后缀候选：a、ba。相等且最长的只有 "a"，长度 1，所以 next[4] '
  '= 2。</p></details><details><summary>完整 next 表</summary><table><thead><tr><th>j</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td>T[j]</td><td>a</td><td>b</td><td>a</td><td>a</td><td>b</td><td>c</td></tr><tr '
  'class="focus-row"><td>next[j]</td><td>0</td><td>1</td><td>1</td><td>2</td><td>2</td><td>3</td></tr></tbody></table><p>next[6] '
  '= 3：T′ = "abaab" 的最长相等前后缀是 "ab"——正是第 13 页"j 退到 3"的依据。</p></details><p>观察整张表：<strong>没有一个字符来自主串</strong>。</p>',
  '手工推演'],
 ['手工模拟：KMP 跑教材例 4.1',
  '<p>同一组 S = "abaabaabcde"、T = "abaabc"，用 next 表走一遍。规则：失配时 <strong>i 不动，j = '
  'next[j]</strong>；j = 0 时 i、j 各进一步。先自己模拟，再用推演核对——也可以切到 BF '
  '跑同一组数据，当场对照：</p><div data-match="kmp"><div class="toolbar"><label>算法 <select '
  'aria-label="选择算法"><option value="0">KMP（i 不回头）</option><option value="1">BF（对照）</option></select></label><button '
  'data-prev>上一步</button><button data-next>开始推演</button><button data-reset>重置</button></div><div '
  'class="mem-counter"></div><div class="match-zones"></div><div class="status" '
  'aria-live="polite"></div></div><p class="small">同一组数据：KMP 10 次比较、i 一次头也没回；BF 15 '
  '次、回溯 3 次——浪费看得见。</p>',
  '手工推演'],
 ['求 next 本身，也是一次匹配',
  '<p>按定义逐个算 next 当然可以，但教材给了一个更快的算法（算法 '
  '4.3），它的核心观察漂亮得值得单独记住：</p><div class="quote">求 next 的过程，是模式 T 在跟自己匹配——<br>自己当前缀，自己当后缀。</div><p>已知 next[j]，就能推 '
  'next[j+1]：又是一次"已匹配的信息不浪费"。算法细节课后对照教材 4.3.3 节推一遍。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>一句话历史：Knuth '
  '从自动机理论得到这个算法，Morris 与 Pratt 独立发现——所以叫 KMP。点到为止。</p></details>',
  'next'],
 ['先预测，再运行：match_demo',
  '<p><code>code/match_demo.c</code>：同一组 S、T 上分别跑 BF 与 '
  'KMP，打印各自的字符比较次数。</p><ul><li>例 A：S = "abaabaabcde"，T = "abaabc"；</li><li>例 B：S = '
  '"aaaaaaab"，T = "aaab"。</li></ul><p>先预测：两例各比多少次？哪一例 BF 与 KMP 的差距更大，为什么？</p><details><summary>说出你的预测与理由</summary><p>例 '
  'A：BF 15 次，KMP 10 次（第 10、16 页已推演）；例 B：BF 每趟都比到最后才失败，共 20 次，KMP 12 次。例 B '
  '差距更大：模式自相似越强、主串重复越多，回溯的浪费越大。</p></details><div class="quote '
  'compact-quote">先预测、再运行、再检查。</div>',
  '先预测再运行'],
 ['代价对照：预处理换一遍过',
  '<table><thead><tr><th></th><th>BF</th><th>KMP</th></tr></thead><tbody><tr><td>主串指针</td><td>失配即回溯</td><td '
  'class="focus-row">全程不回头</td></tr><tr><td>预处理</td><td>无</td><td>对模式算 next，O(m)</td></tr><tr><td>时间</td><td>最坏 '
  'O(n·m)</td><td class="focus-row">O(n+m)</td></tr><tr><td>思想</td><td>每次失配从头再来</td><td>已匹配的信息不浪费</td></tr></tbody></table><p>回收 '
  'D002：这不是"更聪明的技巧"，是<strong>用对模式的一次预处理，换主串的一遍过</strong>。</p><details '
  'class="teacher-note"><summary>教学注记</summary><p>nextval '
  '修正（教材算法 4.4）：失配时若 T[j] 与退回位置的字符相同，这次比较注定失败，可再退一层——一种可以预见的浪费，顺手省掉。学有余力的学生自学，课堂不展开。</p></details>',
  '代价对照'],
 ['串住在哪里？三种存储结构',
  '<table><thead><tr><th>结构</th><th>做法</th><th>强项与边界</th></tr></thead><tbody><tr><td>定长顺序存储</td><td>定长字符数组，超长截断</td><td>简单；长度受限，截断即信息丢失</td></tr><tr><td>堆分配存储</td><td>按实际长度动态申请</td><td>长度自由；要管理申请与释放</td></tr><tr><td>块链存储</td><td>链表，每个结点存一块字符</td><td>插入删除灵活；块大小的权衡</td></tr></tbody></table><p>回收 '
  'D003/D004：又是一次"没有最好的表示，只有适合任务的表示"。见教材 4.3.2 节，课堂不展开，课后对照阅读。</p>',
  '存储结构'],
 ['回到病毒案例：环形的怎么办？',
  '<p>教材 4.6 节补了一个关键细节：双生病毒的 DNA 是<strong>环状</strong>的——模式可以从任意位置"转着圈"开始。</p><div '
  'class="quote">转化：把长度为 m 的环状序列连续存两遍，得到长 2m 的串；<br>环上每个起点 = 新串中一个长度为 m '
  '的子串。</div><p>m 个起点各做一次模式匹配，成功一次即感染。算法没变，<strong>问题被翻译成了会做的样子</strong>——这种转化比算法本身更值得带走。</p>',
  '回到案例'],
 ['4.4–4.5 自学导航',
  '<ul><li><strong>4.4 数组</strong>：二维数组的顺序存储，就是 D003 地址公式的二维推广——LOC(aᵢⱼ) = base + '
  '(i×n + j)×L；特殊矩阵压缩存储：对称、三角、稀疏矩阵，<strong>只存该存的</strong>；</li><li><strong>4.5 '
  '广义表</strong>：元素本身又可以是一个表——"表的递归定义"，呼应 D006；</li><li>串的堆分配与块链细节：4.3.2 '
  '节。</li></ul><p class="small">课堂不展开，按教材对应小节阅读；考到什么程度，以课后习题清单为准。</p>',
  '自学导航'],
 ['已匹配的信息不浪费',
  '<p>本讲的完整链条：</p><ol><li>BF：失配即回溯，把刚比出来的信息全部扔掉；</li><li>KMP：i 不回头——回头能知道的事，查模式就能知道；</li><li>next[j] '
  '由模式自相似决定，与主串无关；求 next 又是一次同样的匹配。</li></ol><div class="quote">失配携带信息，不是纯粹的失败。<br>已经知道的东西，不要花代价再知道一次。</div>',
  '本质收口'],
 ['把几个情境放在一起看',
  '<table><thead><tr><th>情境</th><th>数学/结构</th><th>C 表达</th></tr></thead><tbody><tr><td>在文章里找一个词</td><td>主串 S、模式 '
  'T、定位运算</td><td>字符数组，\'\\0\' 结尾</td></tr><tr><td>失配后重新起点</td><td>i 回溯到 '
  'i−j+2</td><td>BF：两重指针</td></tr><tr '
  'class="focus-row"><td>失配后不回头</td><td>next[j] = 最大相等前后缀长度 + 1</td><td>KMP：预处理 '
  'next，一遍过</td></tr><tr><td>环状病毒检测</td><td>环 = 序列存两遍</td><td>m 个起点，m '
  '次匹配</td></tr></tbody></table><p class="small">同一个问题，四层的翻译。</p>',
  '案例收口'],
 ['我怎样知道自己真的学会了？',
  '<ul><li>能手工模拟 BF：写出 i、j 轨迹，指出失配时浪费掉的信息是什么；</li><li>能不看书手算一个模式的 next '
  '表，并用它手工模拟 KMP，说出 i 为什么可以不回头；</li><li>能解释 next[j] 为什么只跟模式有关，跟主串无关；</li><li>能对病毒案例说出"环形 → '
  '倍长复制"的问题转化。</li></ul><div class="quote">能讲给别人听，能算出别人算错的题。</div>',
  '学会了吗'],
 ['课后：教材导航与本周作业',
  '<p><strong>教材导航</strong>：精读 4.1–4.3（重点 4.3.3，对照第 15、17 页重新推一遍 next '
  '的定义与求法）；浏览 4.4–4.5。带“教学注记”的页面课后可自行点开，带演示的页面可以反复推演。</p><p><strong>本周作业</strong>（作业规范见 '
  'course/assignments/homework-guide.md）：</p><p><strong>A. 书本习题</strong>：第 4 '
  '章选择题 (2)(3)(4)(5)、应用题 (1)、算法设计题 (2)。选择题每题附一句“为什么选它”；应用题与算法设计题写出完整过程。</p><p><strong>B. '
  '扩展作业</strong>：运行 <code>code/match_demo.c</code>，先写下你对两例比较次数的预测，再实测对照。</p><p '
  'class="small">自学练习（不提交）：应用题 (2)——画出 KMP 的每趟匹配过程（训练价值高，耗时较长）；4.4 数组自学路径：选择题 '
  '(6)(7)(9)(12)、应用题 (3)；4.5 广义表自学路径：选择题 (13)(14)(15)、应用题 (4)。<br>挑战：自己构造一组 '
  'S、T，让 BF 相对 KMP 的浪费尽量大，并解释为什么这组输入能做到。</p>',
  '课后衔接'],
 ['如果关系不是“一个接一个”呢？',
  '<p>串、表、栈、队列——到目前为止，数据之间都是"一个接一个"的线性关系。</p><div '
  'class="quote">如果数据之间是"一个管着多个"呢？<br>文件系统、组织架构、家族谱……</div><p>下次课：树与二叉树——层次组织。</p>',
  '留下问题']]
