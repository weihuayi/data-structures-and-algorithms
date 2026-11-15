"""D018 hashing: registered slide metadata and trusted lesson content."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools/deck'))
from components import CourseDeck, Section

DECK_ID = "D018"
TITLE = "散列：映射与工程权衡"
MATH = True
COURSE = CourseDeck([
    Section("bridge", "从已有查找方法出发", "不用关键字大小比较，还能快速定位记录吗？", "回收 D016 查找契约与 D017 AVL 的顺序路径", "区分按键查找与数组按下标访问"),
    Section("mapping", "从直接寻址到散列映射", "关键字很多而记录很少，怎样计算候选位置？", "地址空间、取模映射与必然可能发生的冲突", "理解映射不是已完成的查找"),
    Section("collision", "怎样处理映射冲突", "相同候选地址的记录怎样共存和被找到？", "链地址法、线性探查与存储语义对比", "独立构造并解释两类冲突处理结构"),
    Section("correctness", "操作怎样保持正确", "删除或更新之后，怎样证明查找不会漏掉记录？", "成功与失败、EMPTY/DELETED、重复键与有限探查", "解释同一探查路径的保持性质"),
    Section("cost", "查找代价为什么不同", "同样的装载因子，为什么搜索次数仍不同？", "探查次数、ASL、冲突分布与性能成立条件", "有条件地分析时间和空间成本"),
    Section("choice", "按实际需求选择结构", "什么时候选散列表，什么时候选 AVL？", "范围查询、C11 对照、课堂与作业收束", "针对新需求给出可解释的条件化判断")
])
PAGES = json.loads(r'''[
  {
    "id": "cover",
    "title": "散列：映射与工程权衡",
    "body": "<style>\n.hash-lesson{max-width:1120px;margin:0 auto}\n.hash-lesson .hash-lead{font-size:1.19em;line-height:1.47;font-weight:650;color:#224c76;margin:.32rem 0 .8rem}\n.hash-lesson .hash-note{font-size:.85em;line-height:1.48;color:#576979;margin:.48rem 0}\n.hash-lesson .hash-card{border:1px solid #bdcedd;border-radius:12px;background:rgba(223,235,248,.25);padding:.6rem .85rem;margin:.45rem 0}\n.hash-lesson .hash-pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem}\n.hash-lesson .hash-pair>*{min-width:0}\n.hash-lesson .hash-table,.hash-lesson .hash-slots{width:100%;border-collapse:collapse;table-layout:fixed;line-height:1.36}\n.hash-lesson .hash-table{font-size:.91em;margin:.4rem 0}\n.hash-lesson .hash-table th,.hash-lesson .hash-table td{border-bottom:1px solid #c7d3df;padding:.43rem .45rem;text-align:left;vertical-align:top}\n.hash-lesson .hash-table th{background:#e8f1fa;color:#224d76}\n.hash-lesson .hash-slots{max-width:830px;margin:.36rem auto;font-size:1.08em}\n.hash-lesson .hash-slots th{font-size:.76em;font-weight:500;color:#52677b;padding:.2rem}\n.hash-lesson .hash-slots td{border:1px solid #9cafbf;background:#e7eef5;border-radius:5px;text-align:center;padding:.56rem .1rem;font-weight:700}\n.hash-lesson .hash-slots td.hash-empty{color:#8a9ca9;background:#f8fafc}\n.hash-lesson .hash-slots td.hash-deleted{color:#a45c1b;background:#fff0dd}\n.hash-lesson .hash-slots td.hash-mark{color:#16577a;background:#deedf8}\n.hash-lesson .hash-figure{margin:.4rem 0}\n.hash-lesson .hash-figure figcaption{font-size:.78em;color:#596c7d;margin-top:.38rem;text-align:center}\n.hash-lesson .hash-code{background:#f0f4f8;border:1px solid #cbd5df;border-radius:9px;padding:.65rem .8rem;font-size:.77em;line-height:1.35;white-space:pre-wrap;overflow-x:auto;color:#263b51}\n.hash-lesson .hash-steps{display:flex;flex-wrap:wrap;gap:.42rem;align-items:center;margin:.52rem 0}\n.hash-lesson .hash-chip{padding:.38rem .62rem;border-radius:8px;border:1px solid #abc1d4;background:#ebf4fd;font-weight:600}\n.hash-lesson .hash-arrow{color:#67839e}\n.hash-lesson .hash-formula{font-size:1.05em;margin:.65rem 0}\n.hash-lesson strong{color:#204c75}\n@media(max-width:820px){.hash-lesson .hash-pair{grid-template-columns:1fr}.hash-lesson .hash-slots{font-size:.86em}.hash-lesson .hash-table{font-size:.78em}}\n</style><p class=\"hash-lead\">不依赖关键字的大小顺序，怎样计算候选地址，并正确地完成查找？</p><div class=\"hash-card\"><strong>核心主线</strong>：映射定位 → 冲突处理 → 操作正确性 → 条件化代价与选择。</div><p class=\"hash-note\">D018 · 数据结构与算法 · 教材第 7 章 7.4</p>",
    "section": null,
    "role": "cover",
    "goal": "定位本讲新查找路线与核心问题",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "outline",
    "title": "本讲要解决哪些问题？",
    "body": "",
    "section": null,
    "role": "outline",
    "goal": "认识从映射到正确性再到结构选择的学习路径",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "part-bridge",
    "title": "",
    "body": "",
    "section": "bridge",
    "role": "section",
    "goal": "区分按键查找与数组按下标访问",
    "activity": "小节转折"
  },
  {
    "id": "recall-avl",
    "title": "AVL 是根据什么信息决定下一步？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\">回收 D017：AVL 中每个结点维护 BST 顺序性质，并保持高度平衡。</div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>查找关键字 35 时，AVL 为何可以在结点 40 处排除右子树？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>因为要找的关键字小于 40，并且右子树所有关键字都大于 40。AVL 依靠<strong>顺序关系</strong>排除候选；平衡维护约束查找路径长度。</p></div></details></div></div>",
    "section": "bridge",
    "role": "回收顺序信息与搜索方向的关系",
    "goal": "独立回答并核对",
    "activity": "exercise"
  },
  {
    "id": "access-vs-lookup",
    "title": "数组访问快，按关键字查找也快吗？",
    "body": "<p class=\"hash-lead\">已知下标可以直接访问数组元素；已知关键字却不等于知道下标。</p><table class=\"hash-table\"><thead><tr><th>已知的信息</th><th>要完成的操作</th><th>主要问题</th></tr></thead><tbody><tr><td>数组下标 3</td><td>读取 A[3]</td><td>下标已经给定，随机访问</td></tr><tr><td>学号 key=31001234</td><td>找到对应记录</td><td>存储地址未知，不能直接把学号当作下标</td></tr></tbody></table><p class=\"hash-note\">新想法：如果能够由 key 计算一个有效数组位置，会怎样？</p>",
    "section": "bridge",
    "role": "区分按下标访问与按关键字定位",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "part-mapping",
    "title": "",
    "body": "",
    "section": "mapping",
    "role": "section",
    "goal": "理解映射不是已完成的查找",
    "activity": "小节转折"
  },
  {
    "id": "direct-space",
    "title": "为什么不能直接以学号作为数组下标？",
    "body": "<p class=\"hash-lead\">学号可能很大且稀疏，实际存储的记录却很少。</p><div class=\"hash-card\"><strong>直接寻址</strong>：若把关键字直接作为下标，需要覆盖巨大的地址范围；大量单元可能未使用。</div><table class=\"hash-table\"><thead><tr><th>问题条件</th><th>计算与空间判断</th></tr></thead><tbody><tr><td>可能的整数关键字范围很大</td><td>直接建立同规模数组，空间开销可能过高</td></tr><tr><td>实际记录数 n 远小于关键字范围</td><td>希望使用容量 m 较小的数组存放记录</td></tr></tbody></table><p class=\"hash-note\">这里讨论空间利用；不预设具体机器内存规模。</p>",
    "section": "mapping",
    "role": "从关键字空间与记录规模差异引出映射",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "hash-map",
    "title": "散列函数计算的是哪一个位置？",
    "body": "<p class=\"hash-lead\">散列（Hashing）：把关键字映射到有限的初始地址空间。</p><div class=\"hash-card\"><p class=\"hash-formula\">\\(h(k)=k\\bmod m\\)，本例 \\(m=7\\)，地址为 0–6。</p><p>\\(h(10)=3,\\ h(17)=3,\\ h(24)=3,\\ h(13)=6\\)。</p></div><table class=\"hash-table\"><thead><tr><th>对象</th><th>意义</th></tr></thead><tbody><tr><td>k</td><td>关键字（Key）</td></tr><tr><td>m</td><td>桶数组或槽位数组长度（容量）</td></tr><tr><td>h(k)</td><td>由关键字计算的初始候选地址</td></tr></tbody></table><p class=\"hash-note\">不同关键字可以有相同散列值；函数不必取遍全部地址。</p>",
    "section": "mapping",
    "role": "建立 k、m、h(k) 的对象语义",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "detect-collision",
    "title": "四条记录都能直接放到算出的地址吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>如果每个数组位置只能保存一条记录，直接按照 h(k) 存入，会遇到什么问题？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>10、17、24 的散列地址都是 3，三个不同关键字竞争同一个槽位。这叫<strong>散列冲突（Collision）</strong>。初始地址是候选位置，并非完整查找结果；必须设计冲突处理规则。</p></div></details></div></div>",
    "section": "mapping",
    "role": "通过同址实例独立识别冲突的必然可能性",
    "goal": "先计算、后核对",
    "activity": "exercise",
    "withheld_results": [
      "三个不同关键字竞争同一个槽位"
    ]
  },
  {
    "id": "part-collision",
    "title": "",
    "body": "",
    "section": "collision",
    "role": "section",
    "goal": "独立构造并解释两类冲突处理结构",
    "activity": "小节转折"
  },
  {
    "id": "chaining",
    "title": "链地址法把冲突记录保存在哪里？",
    "body": "<p class=\"hash-lead\">链地址法（Separate Chaining）：数组的每个位置保存一个桶的入口。</p><table class=\"hash-table\"><thead><tr><th>桶下标</th><th>桶内关键字（按插入顺序）</th></tr></thead><tbody><tr><td>3</td><td>10 → 17 → 24</td></tr><tr><td>6</td><td>13</td></tr><tr><td>0、1、2、4、5</td><td>空桶</td></tr></tbody></table><div class=\"hash-card\"><strong>结构性质：</strong>键 k 的记录必须位于编号为 h(k) 的桶；同一桶允许多条记录。</div><p class=\"hash-note\">这里 m 是桶头数组长度，桶内链表结点不是数组槽位。</p>",
    "section": "collision",
    "role": "明确链地址中的桶与记录身份",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "chain-lookup",
    "title": "只查一个桶，就能断定不存在吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><table class=\"hash-table\"><thead><tr><th>桶</th><th>记录</th></tr></thead><tbody><tr><td>3</td><td>10 → 17 → 24</td></tr><tr><td>6</td><td>13</td></tr></tbody></table></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>查找 24 与 31 分别需要检查什么？为什么不用检查其它桶？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>\\(h(24)=h(31)=3\\)，都只需检查桶 3。查找 24 比较 10→17→24，成功；查找 31 比较全部三个记录，没有相等关键字，失败。因为所有已有记录始终按其 h(k) 归入对应桶，其它桶不可能含该键。</p></div></details></div></div>",
    "section": "collision",
    "role": "用分桶不变量解释成功与失败",
    "goal": "独立推演与核对",
    "activity": "exercise"
  },
  {
    "id": "linear-probe",
    "title": "开放定址法怎样寻找后续槽位？",
    "body": "<p class=\"hash-lead\">开放定址法（Open Addressing）：记录直接保存在数组槽位中。</p><div class=\"hash-card\"><p class=\"hash-formula\">线性探查：\\(p(k,i)=(h(k)+i)\\bmod m\\)，\\(i=0,1,\\ldots,m-1\\)。</p><p>发生冲突则尝试同一数组内的下一个槽位，环绕回到开头。</p></div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure><p class=\"hash-note\">插入次序：10@3、17@4、24@5、13@6；最后一个键的初始地址是 6。</p>",
    "section": "collision",
    "role": "建立初始地址、探查序列和实际存储位置的关系",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "mechanism-compare",
    "title": "链地址法与线性探查的结构性质相同吗？",
    "body": "<table class=\"hash-table\"><thead><tr><th>比较对象</th><th>链地址法</th><th>线性探查</th></tr></thead><tbody><tr><td>数组位置代表什么</td><td>桶（链表入口）</td><td>能保存一条记录的槽位</td></tr><tr><td>冲突后的记录在哪里</td><td>同一桶的链表中</td><td>顺着探查序列的其它槽位中</td></tr><tr><td>关键正确性要求</td><td>记录属于 h(k) 所在桶</td><td>查找与插入使用同一探查路径</td></tr><tr><td>装载因子 n/m</td><td>每桶平均记录数</td><td>有效槽位占比，不能超过 1</td></tr></tbody></table><p class=\"hash-note\">相同符号 m 表示数组容量，但数组单元承载的含义不同。</p>",
    "section": "collision",
    "role": "区分两个冲突机制的存储语义和正确性规则",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "part-correctness",
    "title": "",
    "body": "",
    "section": "correctness",
    "role": "section",
    "goal": "解释同一探查路径的保持性质",
    "activity": "小节转折"
  },
  {
    "id": "probe-find",
    "title": "查找 24，需要经过哪些位置？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>沿线性探查规则查找 24。写出每一步位置及是否继续或终止。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>\\(h(24)=3\\)。在 3 比较 10，在 4 比较 17，在 5 找到 24。因此访问路径为 <strong>3 → 4 → 5</strong>，共检查 3 个槽位。</p></div></details></div></div>",
    "section": "correctness",
    "role": "独立执行成功查找并保持初始输入在场",
    "goal": "独立预测再核对",
    "activity": "exercise"
  },
  {
    "id": "probe-delete",
    "title": "删除 17，为什么不能简单改成 EMPTY？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>删去 17 后，如果把位置 4 改为 EMPTY，再查找 24，会发生什么错误？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>查找 24 从位置 3 出发，在位置 4 遇到 EMPTY 就会被错误地判为不存在，尽管位置 5 仍存有 24。采用墓碑策略应将位置 4 标为 DELETED。</p><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-deleted\">DEL</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>位置 4 为 DELETED；“—”为 EMPTY。</figcaption></figure></div></details></div></div>",
    "section": "correctness",
    "role": "识别删除造成的早停反例并解释墓碑作用",
    "goal": "反例预测与核对",
    "activity": "exercise"
  },
  {
    "id": "probe-miss",
    "title": "查找 31，应当在哪里停止？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><p>当前状态：已删除 17，位置 4 是 DELETED。</p></div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-deleted\">DEL</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>位置 4 为 DELETED；“—”为 EMPTY。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>给定 \\(h(31)=3\\)，写出查找 31 的完整探查路径，并说明失败依据。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p><strong>3 → 4 → 5 → 6 → 0</strong>，位置 0 为 EMPTY，才可判定不存在。不能在位置 4 的 DELETED 停止。共检查 5 个槽位，其中仅与 3 个有效关键字比较。</p></div></details></div></div>",
    "section": "correctness",
    "role": "独立解释失败查找终止依据与计数",
    "goal": "独立推演与核对",
    "activity": "exercise"
  },
  {
    "id": "invariant",
    "title": "三种状态怎样共同保证操作正确？",
    "body": "<p class=\"hash-lead\">维护同一探查序列，并保证已有关键字之前不会出现使查找提前停止的 EMPTY。</p><table class=\"hash-table\"><thead><tr><th>槽位状态</th><th>查找操作</th><th>插入操作</th></tr></thead><tbody><tr><td>OCCUPIED</td><td>比较 key；不匹配继续</td><td>检查是否重复；不匹配继续</td></tr><tr><td>DELETED</td><td>不能作为失败依据，继续</td><td>记住可复用位置；仍需查重</td></tr><tr><td>EMPTY</td><td>可以判定查找失败</td><td>此前已排除重复，必要时复用墓碑</td></tr></tbody></table><p class=\"hash-note\">始终限制探查次数不超过 m，避免满表或异常状态中无限循环。</p>",
    "section": "correctness",
    "role": "建立插入、删除、查找共同保持的不变量",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "reuse-and-duplicate",
    "title": "墓碑出现后，插入时能立刻占用吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-deleted\">DEL</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>位置 4 为 DELETED；“—”为 EMPTY。</figcaption></figure><p>现在依次考虑插入已有键 24，以及新键 31。</p></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>遇到位置 4 的 DELETED 时，能否立即插入 24？插入新键 31 后最终表怎样变化？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>不能立即写入 24，因为位置 5 已有该键，字典要求键唯一。继续检查直到命中 24，判定重复。对于 31，确认沿路径 3→4→5→6→0 不存在后，复用已记住的位置 4。</p><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"\">10</td><td class=\"hash-mark\">31</td><td class=\"\">24</td><td class=\"\">13</td></tr></tbody></table><figcaption>查明 31 不存在后复用位置 4。</figcaption></figure></div></details></div></div>",
    "section": "correctness",
    "role": "将重复键契约与墓碑复用条件联系起来",
    "goal": "独立判断和完整核对",
    "activity": "exercise"
  },
  {
    "id": "part-cost",
    "title": "",
    "body": "",
    "section": "cost",
    "role": "section",
    "goal": "有条件地分析时间和空间成本",
    "activity": "小节转折"
  },
  {
    "id": "cost-units",
    "title": "探查次数和关键字比较次数是一回事吗？",
    "body": "<p class=\"hash-lead\">必须先声明成本模型，才可能解释 ASL。</p><table class=\"hash-table\"><thead><tr><th>查找 31（删除 17 后）</th><th>次数</th><th>依据</th></tr></thead><tbody><tr><td>检查槽位次数</td><td>5</td><td>位置 3、4、5、6、0</td></tr><tr><td>有效关键字相等比较</td><td>3</td><td>比较 10、24、13；DEL 与 EMPTY 不保存有效键</td></tr><tr><td>实际运行时间</td><td>未测量</td><td>不能从探查次数直接断言真实 CPU 时间</td></tr></tbody></table><p class=\"hash-note\">本讲的开放定址主例统一采用“检查一个槽位计一次探查”。链地址法中的结点比较须另记。</p>",
    "section": "cost",
    "role": "建立一致计数口径并识别单位差异",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "cost-asl",
    "title": "成功查找的平均长度如何算？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>如果四个已有键被等概率查询，请分别写出各键成功探查次数并计算 ASL。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>10、17、24、13 的探查次数分别为 1、2、3、1。</p><p>\\(ASL_{succ}=(1+2+3+1)/4=7/4=1.75\\)。这是对<strong>给定四个键的等概率成功查询</strong>的条件平均，不是任意失败查询的平均。</p></div></details></div></div>",
    "section": "cost",
    "role": "独立计算给定概率下的成功 ASL",
    "goal": "先算再核对",
    "activity": "exercise"
  },
  {
    "id": "same-load",
    "title": "同样装载因子，查找代价也相同吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><p>两组不同关键字按序插入，均用 \\(m=7\\)、\\(h(k)=k\\bmod7\\)、线性探查。</p><p>\\(S_1=(3,4,5,6)\\)，\\(S_2=(3,10,17,24)\\)。</p></div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"\">3/3</td><td class=\"\">4/10</td><td class=\"\">5/17</td><td class=\"\">6/24</td></tr></tbody></table><figcaption>每个占用槽依次展示 S1/S2 的记录键；最终占用位置相同。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>两组都是 \\(\\alpha=4/7\\)。计算两种情况下等概率成功 ASL，并说明不同原因。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>\\(S_1\\)：所有记录初始地址就是实际位置，ASL=1。\\(S_2\\)：四个键初始地址均为 3，探查次数 1、2、3、4，ASL=2.5。</p><p>装载因子相同不足以确定查找成本；分布、散列函数和探查路径仍起作用。这里两表的失败查找长度不会仅因为成功 ASL 不同而自动不同。</p></div></details></div></div>",
    "section": "cost",
    "role": "用具体反例区分装载因子和冲突分布",
    "goal": "独立计算与解释",
    "activity": "exercise"
  },
  {
    "id": "quadratic-note",
    "title": "跳过相邻槽位，就一定能找到空位吗？",
    "body": "<p class=\"hash-lead\">二次探查是一种改变探查路径的方法，但需要说明具体规则和覆盖条件。</p><div class=\"hash-card\"><p>示例：\\(p(k,i)=(h(k)+i^2)\\bmod7\\)。初始地址为 4 时，访问序列为 <strong>4 → 5 → 1 → 6 → 6 → 1 → 5</strong>……</p><p>在这条序列里，部分槽位没有被访问；表有空位不等于此规则一定能找到。</p></div><p class=\"hash-note\">教材中另有表长与哈希取模常数不同的二次探测习题；演示和作业须以原题规定的增量、容量与终止规则为准。</p>",
    "section": "cost",
    "role": "认识探查覆盖与冲突减少不是同一问题",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "expected-cost",
    "title": "为什么不能无条件说“散列查找 O(1)”？",
    "body": "<table class=\"hash-table\"><thead><tr><th>主张</th><th>需要说明的条件</th></tr></thead><tbody><tr><td>一次具体查找</td><td>取决于冲突、探查路径、是否命中和操作历史；最坏可能 O(n)</td></tr><tr><td>常见的期望 O(1) 查找</td><td>需要适当的散列随机性/分布假设、装载因子控制和单位成本模型</td></tr><tr><td>开放定址的动态插入</td><td>墓碑及扩容可能影响成本；几何扩容的总重建代价可做摊还分析</td></tr><tr><td>与 AVL 的比较</td><td>AVL 有明确的最坏 O(log n) 结构保证，且能够支持有序范围查询</td></tr></tbody></table><p class=\"hash-note\">概率期望与操作序列摊还是不同的分析；本讲理解条件性，不要求推导通用散列完整证明。</p>",
    "section": "cost",
    "role": "分清单次、期望、摊还与最坏保证",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "part-choice",
    "title": "",
    "body": "",
    "section": "choice",
    "role": "section",
    "goal": "针对新需求给出可解释的条件化判断",
    "activity": "小节转折"
  },
  {
    "id": "choice-task",
    "title": "设备编号查询与区间查询，应如何组织？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><p>某系统维护设备编号及状态：多数请求按编号精确查找，同时还需要按编号区间查询。允许根据需求组合索引，但每次更新必须保持索引一致。</p></div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>比较单独使用散列表、AVL 或双索引方案：各自的优势、代价和可能改选条件是什么？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>精确查找占主导且接受期望保证：散列表是候选；频繁区间查询且要求有序输出：AVL 等有序结构具有直接优势；两种操作都很关键时可组合索引，但增加存储、更新与一致性维护成本。不能脱离频率、规模及最坏延迟要求给出唯一最优方案。</p></div></details></div></div>",
    "section": "choice",
    "role": "在新情境中提出结构选择与适用条件",
    "goal": "独立判断并核对",
    "activity": "exercise"
  },
  {
    "id": "code-bridge",
    "title": "数学探查过程在 C11 程序里对应什么？",
    "body": "<p class=\"hash-lead\">程序验证机制，不替代理解；先预测结果，再运行核对。</p><table class=\"hash-table\"><thead><tr><th>数学／结构对象</th><th>C11 示例字段／函数</th><th>职责</th></tr></thead><tbody><tr><td>\\(k\\)，\\(m\\)</td><td>key，CAP</td><td>目标键与槽位容量</td></tr><tr><td>\\(p(k,i)\\)</td><td>position(key,i)</td><td>由键和探查次数计算位置</td></tr><tr><td>EMPTY / OCCUPIED / DELETED</td><td>SlotState state</td><td>决定比较、继续或停止</td></tr><tr><td>已访问槽位数</td><td>probes</td><td>对照学生的探查轨迹</td></tr><tr><td>动态字典契约</td><td>lookup / insert / erase</td><td>查重、墓碑复用、有限终止</td></tr></tbody></table><div class=\"hash-card\"><pre class=\"hash-code\">gcc -std=c11 -Wall -Wextra -pedantic code/hash_demo.c -o hash_demo\n./hash_demo demo\n./hash_demo --self-test</pre></div><p class=\"hash-note\">仅为本地命令示例。源文件可复制到学生自己的目录运行，不要求进入 Git 仓库；先定位工作目录下的相对源码路径。</p>",
    "section": "choice",
    "role": "建立数学状态与 C11 变量及程序输出的对应",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "summary",
    "title": "我们究竟利用了关键字的什么信息？",
    "body": "<p class=\"hash-lead\">从按比较排除候选，到按散列计算候选地址。</p><table class=\"hash-table\"><thead><tr><th>定位路线</th><th>必须维护的性质</th><th>收益与限制</th></tr></thead><tbody><tr><td>AVL</td><td>关键字顺序 + 高度平衡</td><td>最坏对数查找；天然支持有序操作</td></tr><tr><td>散列表</td><td>映射 + 冲突规则 + 操作不变量</td><td>适当条件下精确查询期望高效；不直接提供顺序</td></tr></tbody></table><div class=\"hash-card\"><strong>独立检查：</strong>能否解释一个失败查找为什么正确？能否说明 ASL 的条件？能否对新的数据需求给出改选理由？</div>",
    "section": "choice",
    "role": "回收映射—正确性—代价—选择的承重关系",
    "goal": "",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "homework",
    "title": "课后怎样预测、运行和核对？",
    "body": "<p class=\"hash-lead\">A、B 为正式必做；扩展自学不提交。</p><table class=\"hash-table\"><thead><tr><th>部分</th><th>具体任务及应提交的证据</th></tr></thead><tbody><tr><td>A · 书本习题</td><td>第 7 章选择题 (12)(13)(14)、应用题 (5)。选择题给一句理由；应用题给出构表、探查序列、ASL 的关键过程。</td></tr><tr><td>B · C11 程序实践</td><td>先预测删除 17、查找 24/31、重复插入 24、插入 31 后的状态与查找路径；在本地运行 code/hash_demo.c 的 demo 和 --self-test，记录输出、差异及正确性解释。</td></tr><tr><td>自学／选做，不提交</td><td>应用题 (6)(7)、算法设计题 (6)；用于补充二次探查、两种冲突处理及链地址法程序设计。</td></tr></tbody></table><div class=\"hash-card\"><p><strong>提交</strong>：按课程共同规范整理飞书文档并提交可查看链接；末尾保留 3–5 行过程记录。只运行示例不强制附代码或截图；修改源码才提供必要代码和测试。无须向 GitHub 提交。</p><p><strong>运行</strong>：可在自己电脑的合适目录使用 C11 编译器/IDE；示例相对路径按实际存放位置调整。</p></div><p class=\"hash-note\">教材题号已按仓库提取草案列出，公开课件发布前仍须对照原题校核；教材题设为最终准据。</p>",
    "section": null,
    "role": "closing",
    "goal": "明确 A/B 正式作业和提交、核对与代码使用边界",
    "activity": "独立完成课后任务"
  }
]''')
for item in PAGES:
    if item["role"] == "outline":
        COURSE.outline()
    elif item["role"] == "section":
        COURSE.start_section(item["section"], page_id=item["id"])
    else:
        COURSE.add(item["id"], item["title"], '<div class="hash-lesson">' + item["body"] + '</div>',
                   section=item["section"], role=item["role"], goal=item["goal"],
                   activity=item["activity"], label="课程导入" if item["role"] == "cover" else "",
                   withheld_results=item.get("withheld_results", ()))
SLIDES = COURSE.finalize()
