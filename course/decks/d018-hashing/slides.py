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
    "body": "<style>\n.hash-lesson{max-width:1120px;margin:0 auto}\n.hash-lesson .hash-lead{font-size:1.19em;line-height:1.47;font-weight:650;color:#224c76;margin:.32rem 0 .8rem}\n.hash-lesson .hash-note{font-size:.85em;line-height:1.48;color:#576979;margin:.48rem 0}\n.hash-lesson .hash-card{border:1px solid #bdcedd;border-radius:12px;background:rgba(223,235,248,.25);padding:.6rem .85rem;margin:.45rem 0}\n.hash-lesson .hash-pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem}\n.hash-lesson .hash-pair>*{min-width:0}\n.hash-lesson .hash-table,.hash-lesson .hash-slots{width:100%;border-collapse:collapse;table-layout:fixed;line-height:1.36}\n.hash-lesson .hash-table{font-size:.91em;margin:.4rem 0}\n.hash-lesson .hash-table th,.hash-lesson .hash-table td{border-bottom:1px solid #c7d3df;padding:.43rem .45rem;text-align:left;vertical-align:top}\n.hash-lesson .hash-table th{background:#e8f1fa;color:#224d76}\n.hash-lesson .hash-slots{max-width:830px;margin:.36rem auto;font-size:1.08em}\n.hash-lesson .hash-slots th{font-size:.76em;font-weight:500;color:#52677b;padding:.2rem}\n.hash-lesson .hash-slots td{border:1px solid #9cafbf;background:#e7eef5;border-radius:5px;text-align:center;padding:.56rem .1rem;font-weight:700}\n.hash-lesson .hash-slots td.hash-empty{color:#8a9ca9;background:#f8fafc}\n.hash-lesson .hash-slots td.hash-deleted{color:#a45c1b;background:#fff0dd}\n.hash-lesson .hash-slots td.hash-mark{color:#16577a;background:#deedf8}\n.hash-lesson .hash-figure{margin:.4rem 0}\n.hash-lesson .hash-figure figcaption{font-size:.78em;color:#596c7d;margin-top:.38rem;text-align:center}\n.hash-lesson .hash-code{background:#f0f4f8;border:1px solid #cbd5df;border-radius:9px;padding:.65rem .8rem;font-size:.77em;line-height:1.35;white-space:pre-wrap;overflow-x:auto;color:#263b51}\n.hash-lesson .hash-steps{display:flex;flex-wrap:wrap;gap:.42rem;align-items:center;margin:.52rem 0}\n.hash-lesson .hash-chip{padding:.38rem .62rem;border-radius:8px;border:1px solid #abc1d4;background:#ebf4fd;font-weight:600}\n.hash-lesson .hash-arrow{color:#67839e}\n.hash-lesson .hash-formula{font-size:1.05em;margin:.65rem 0}\n.hash-lesson strong{color:#204c75}\n@media(max-width:820px){.hash-lesson .hash-pair{grid-template-columns:1fr}.hash-lesson .hash-slots{font-size:.86em}.hash-lesson .hash-table{font-size:.78em}}\n\n/* The shared six-section outline needs a denser projection layout. */\n.deck .course-outline.course-outline-dense{gap:4px;margin:2px 0}\n.deck .course-outline.course-outline-dense>li{padding:4px 0;gap:10px;line-height:1.18}\n.deck .course-outline-dense .course-outline-number{font-size:26px}\n.deck .course-outline-dense .course-outline-topic strong{font-size:.94em;line-height:1.14}\n.deck .course-outline-dense .course-outline-topic p{font-size:.82em;line-height:1.16;margin:2px 0 0}\n.deck .course-outline-dense .course-outline-pages{font-size:.76em}\n</style><p class=\"hash-lead\">不依赖关键字的大小顺序，怎样计算候选地址，并正确地完成查找？</p><div class=\"hash-card\"><strong>核心主线</strong>：映射定位 → 冲突处理 → 操作正确性 → 条件化代价与选择。</div><p class=\"hash-note\">D018 · 数据结构与算法 · 教材第 7 章 7.4</p>",
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
    "role": "exercise",
    "goal": "回收顺序信息与搜索方向的关系",
    "activity": "独立回答并核对"
  },
  {
    "id": "access-vs-lookup",
    "title": "数组访问快，按关键字查找也快吗？",
    "body": "<p class=\"hash-lead\">已知下标可以直接访问数组元素；已知关键字却不等于知道下标。</p><table class=\"hash-table\"><thead><tr><th>已知的信息</th><th>要完成的操作</th><th>主要问题</th></tr></thead><tbody><tr><td>数组下标 3</td><td>读取 A[3]</td><td>下标已经给定，随机访问</td></tr><tr><td>学号 key=31001234</td><td>找到对应记录</td><td>存储地址未知，不能直接把学号当作下标</td></tr></tbody></table><p class=\"hash-note\">新想法：如果能够由 key 计算一个有效数组位置，会怎样？</p>",
    "section": "bridge",
    "role": "content",
    "goal": "区分按下标访问与按关键字定位",
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
    "role": "content",
    "goal": "从关键字空间与记录规模差异引出映射",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "hash-map",
    "title": "散列函数计算的是哪一个位置？",
    "body": "<p class=\"hash-lead\">散列（Hashing）：把关键字映射到有限的初始地址空间。</p><div class=\"hash-card\"><p class=\"hash-formula\">\\(h(k)=k\\bmod m\\)，本例 \\(m=7\\)，地址为 0–6。</p><p>示范计算：\\(h(10)=3\\)。其余关键字的地址留到下一页独立计算。</p></div><table class=\"hash-table\"><thead><tr><th>对象</th><th>意义</th></tr></thead><tbody><tr><td>k</td><td>关键字（Key）</td></tr><tr><td>m</td><td>桶数组或槽位数组长度（容量）</td></tr><tr><td>h(k)</td><td>由关键字计算的初始候选地址</td></tr></tbody></table><p class=\"hash-note\">不同关键字可以有相同散列值；函数不必取遍全部地址。</p>",
    "section": "mapping",
    "role": "content",
    "goal": "建立 k、m、h(k) 的对象语义",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "detect-collision",
    "title": "四条记录都能直接放到算出的地址吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>如果每个数组位置只能保存一条记录，直接按照 h(k) 存入，会遇到什么问题？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>10、17、24 的散列地址都是 3，三个不同关键字竞争同一个槽位。这叫<strong>散列冲突（Collision）</strong>。初始地址是候选位置，并非完整查找结果；必须设计冲突处理规则。</p></div></details></div></div>",
    "section": "mapping",
    "role": "exercise",
    "goal": "通过同址实例独立识别冲突的必然可能性",
    "activity": "先计算、后核对",
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
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>给定输入</strong>：容量 \\(m=7\\)，\\(h(k)=k\\bmod7\\)；依次插入 \\(10,17,24,13\\)（互异的非负整数键）。</div><div class=\"hash-card\"><strong>规则</strong>：链地址法（Separate Chaining）中，每个数组位置是一个桶的链表入口；按给定顺序把记录接到所属桶尾部。</div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>先独立填写非空桶及桶内顺序；发生冲突时，为什么仍能保留全部记录？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><table class=\"hash-table\"><thead><tr><th>桶下标</th><th>桶内记录（按插入顺序）</th></tr></thead><tbody><tr><td>3</td><td>10 → 17 → 24</td></tr><tr><td>6</td><td>13</td></tr><tr><td>0、1、2、4、5</td><td>空桶</td></tr></tbody></table><p><strong>解释：</strong>任何键 k 只能存放在桶 h(k) 中。桶中保存多条记录；桶头数组的位置不是一条记录的专用槽位。</p></div></details></div></div>",
    "section": "collision",
    "role": "exercise",
    "goal": "明确链地址中的桶与记录身份",
    "activity": "独立构表、核对完整结构与归属不变量"
  },
  {
    "id": "chain-lookup",
    "title": "只查一个桶，就能断定不存在吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><table class=\"hash-table\"><thead><tr><th>桶</th><th>记录</th></tr></thead><tbody><tr><td>3</td><td>10 → 17 → 24</td></tr><tr><td>6</td><td>13</td></tr></tbody></table></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>查找 24 与 31 分别需要检查什么？为什么不用检查其它桶？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>\\(h(24)=h(31)=3\\)，都只需检查桶 3。查找 24 比较 10→17→24，成功；查找 31 比较全部三个记录，没有相等关键字，失败。因为所有已有记录始终按其 h(k) 归入对应桶，其它桶不可能含该键。</p></div></details></div></div>",
    "section": "collision",
    "role": "exercise",
    "goal": "用分桶不变量解释成功与失败",
    "activity": "独立推演与核对"
  },
  {
    "id": "linear-probe",
    "title": "开放定址法怎样寻找后续槽位？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>给定输入</strong>：容量 \\(m=7\\)，\\(h(k)=k\\bmod7\\)；依次插入 \\(10,17,24,13\\)（互异的非负整数键）。</div><div class=\"hash-card\"><p><strong>规则</strong>：开放定址法（Open Addressing）的每个槽只存一条记录。</p><p>线性探查 \\(p(k,i)=(h(k)+i)\\bmod7\\)，\\(i=0,\\ldots,6\\)；冲突时继续下一槽（环绕）。</p></div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td></tr></tbody></table><figcaption>待填槽位：容量 7，下标 0–6（初始表为空）。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>按插入顺序独立填写最终数组，并给出每个键的初始地址与实际落位；何时必须继续探查？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><table class=\"hash-table\"><thead><tr><th>键 k</th><th>初始地址 h(k)</th><th>实际槽位</th><th>探查轨迹</th></tr></thead><tbody><tr><td>10</td><td>3</td><td>3</td><td>3</td></tr><tr><td>17</td><td>3</td><td>4</td><td>3 → 4</td></tr><tr><td>24</td><td>3</td><td>5</td><td>3 → 4 → 5</td></tr><tr><td>13</td><td>6</td><td>6</td><td>6</td></tr></tbody></table><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure><p><strong>解释：</strong>所有操作都沿同一探查序列检查槽位；初始散列地址与最终存储地址可以不同。</p></div></details></div></div>",
    "section": "collision",
    "role": "exercise",
    "goal": "建立初始地址、探查序列和实际存储位置的关系",
    "activity": "独立构造线性探查表、核对轨迹与完整状态"
  },
  {
    "id": "mechanism-compare",
    "title": "链地址法与线性探查的结构性质相同吗？",
    "body": "<table class=\"hash-table\"><thead><tr><th>比较对象</th><th>链地址法</th><th>线性探查</th></tr></thead><tbody><tr><td>数组位置代表什么</td><td>桶（链表入口）</td><td>能保存一条记录的槽位</td></tr><tr><td>冲突后的记录在哪里</td><td>同一桶的链表中</td><td>顺着探查序列的其它槽位中</td></tr><tr><td>关键正确性要求</td><td>记录属于 h(k) 所在桶</td><td>查找与插入使用同一探查路径</td></tr><tr><td>装载因子 n/m</td><td>每桶平均记录数</td><td>有效槽位占比，不能超过 1</td></tr></tbody></table><p class=\"hash-note\">相同符号 m 表示数组容量，但数组单元承载的含义不同。</p>",
    "section": "collision",
    "role": "content",
    "goal": "区分两个冲突机制的存储语义和正确性规则",
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
    "role": "exercise",
    "goal": "独立执行成功查找并保持初始输入在场",
    "activity": "独立预测再核对"
  },
  {
    "id": "probe-delete",
    "title": "删除 17，为什么不能简单改成 EMPTY？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>删去 17 后，如果把位置 4 改为 EMPTY，再查找 24，会发生什么错误？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>查找 24 从位置 3 出发，在位置 4 遇到 EMPTY 就会被错误地判为不存在，尽管位置 5 仍存有 24。采用墓碑策略应将位置 4 标为 DELETED。</p><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-deleted\">DEL</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>位置 4 为 DELETED；“—”为 EMPTY。</figcaption></figure></div></details></div></div>",
    "section": "correctness",
    "role": "exercise",
    "goal": "识别删除造成的早停反例并解释墓碑作用",
    "activity": "反例预测与核对"
  },
  {
    "id": "probe-miss",
    "title": "查找 31，应当在哪里停止？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><p>当前状态：已删除 17，位置 4 是 DELETED。</p></div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-deleted\">DEL</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>位置 4 为 DELETED；“—”为 EMPTY。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>给定 \\(h(31)=3\\)，写出查找 31 的完整探查路径，并说明失败依据。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p><strong>3 → 4 → 5 → 6 → 0</strong>，位置 0 为 EMPTY，才可判定不存在。不能在位置 4 的 DELETED 停止。共检查 5 个槽位，其中仅与 3 个有效关键字比较。</p></div></details></div></div>",
    "section": "correctness",
    "role": "exercise",
    "goal": "独立解释失败查找终止依据与计数",
    "activity": "独立推演与核对"
  },
  {
    "id": "invariant",
    "title": "三种状态怎样共同保证操作正确？",
    "body": "<p class=\"hash-lead\">已存关键字在其探查路径上，不得被提前遇到的 EMPTY 隔断。</p>\n<div class=\"hash-pair\">\n<div class=\"hash-card\"><strong>三种状态与查找规则</strong>\n<table class=\"hash-table\"><thead><tr><th>状态</th><th>操作</th></tr></thead><tbody>\n<tr><td>OCCUPIED</td><td>比较键；不相等继续</td></tr>\n<tr><td>DELETED</td><td>继续，不能判定失败</td></tr>\n<tr><td>EMPTY</td><td>正确判定不存在</td></tr>\n</tbody></table></div>\n<div class=\"hash-card\"><strong>C11 查找分支节选</strong>\n<pre class=\"hash-code\">/* p 已由 position(key,i) 得到 */\nif (t->slot[p].state == EMPTY)\n    return -1;\nif (t->slot[p].state == OCCUPIED\n    && t->slot[p].key == key)\n    return (int)p;\n/* 其余情况继续探查 */</pre></div></div>\n<p class=\"hash-note\">循环最多执行 m 次；插入遇到 DELETED 要记住可复用位置，但仍须继续检查是否存在重复键（见下一页）。节选省略轨迹输出与计数。</p>",
    "section": "correctness",
    "role": "content",
    "goal": "建立插入、删除、查找共同保持的不变量",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "reuse-and-duplicate",
    "title": "墓碑出现后，插入时能立刻占用吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-deleted\">DEL</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>位置 4 为 DELETED；“—”为 EMPTY。</figcaption></figure><p>现在依次考虑插入已有键 24，以及新键 31。</p></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>遇到位置 4 的 DELETED 时，能否立即插入 24？插入新键 31 后最终表怎样变化？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>不能立即写入 24，因为位置 5 已有该键，字典要求键唯一。继续检查直到命中 24，判定重复。对于 31，确认沿路径 3→4→5→6→0 不存在后，复用已记住的位置 4。</p><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"\">10</td><td class=\"hash-mark\">31</td><td class=\"\">24</td><td class=\"\">13</td></tr></tbody></table><figcaption>查明 31 不存在后复用位置 4。</figcaption></figure></div></details></div></div>",
    "section": "correctness",
    "role": "exercise",
    "goal": "将重复键契约与墓碑复用条件联系起来",
    "activity": "独立判断和完整核对"
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
    "role": "content",
    "goal": "建立一致计数口径并识别单位差异",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "cost-asl",
    "title": "成功查找的平均长度如何算？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>共同输入</strong>：非负整数键，按顺序插入 \\(10,17,24,13\\)；\\(m=7\\)，\\(h(k)=k\\bmod7\\)。</div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>如果四个已有键被等概率查询，请分别写出各键成功探查次数并计算 ASL。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>10、17、24、13 的探查次数分别为 1、2、3、1。</p><p>\\(ASL_{succ}=(1+2+3+1)/4=7/4=1.75\\)。这是对<strong>给定四个键的等概率成功查询</strong>的条件平均，不是任意失败查询的平均。</p></div></details></div></div>",
    "section": "cost",
    "role": "exercise",
    "goal": "独立计算给定概率下的成功 ASL",
    "activity": "先算再核对"
  },
  {
    "id": "cost-asl-fail",
    "title": "失败查找的平均长度如何计算？",
    "role": "exercise",
    "section": "cost",
    "goal": "在明确失败查询的概率分布后独立求 ASL，并与成功 ASL 区分",
    "activity": "独立推演各初始地址的失败路径并解释均值口径",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><strong>给定输入</strong>：容量 \\(m=7\\)，\\(h(k)=k\\bmod7\\)；依次插入 \\(10,17,24,13\\)（互异的非负整数键）。</div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-mark\">10</td><td class=\"hash-mark\">17</td><td class=\"hash-mark\">24</td><td class=\"hash-mark\">13</td></tr></tbody></table><figcaption>线性探查构造结果：容量 7，下标 0–6。</figcaption></figure><p class=\"hash-note\">表为插入四个键后的<strong>初始状态（尚未删除）</strong>。设失败查询的初始散列地址 \\(r=0,1,\\ldots,6\\) 各以 \\(1/7\\) 的概率出现；按检查槽位次数计费。</p></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>对于七种初始地址，分别写出查找不存在关键字时的探查次数，再计算失败 ASL。为什么不能把它与上一页的成功 ASL 混为一谈？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><table class=\"hash-table\"><thead><tr><th>失败查询的初始地址 r</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td>槽位探查次数</td><td>1</td><td>1</td><td>1</td><td>5</td><td>4</td><td>3</td><td>2</td></tr></tbody></table><p>\\(\\displaystyle ASL_{\\mathrm{unsucc}}=\\frac{1+1+1+5+4+3+2}{7}=\\frac{17}{7}\\)。该平均值以<strong>失败查询的初始地址均匀分布</strong>为前提；上一页 \\(7/4\\) 是对四个已存关键字等概率查询的成功 ASL，两者的概率空间不同。</p></div></details></div></div>"
  },
  {
    "id": "same-load",
    "title": "同样装载因子，查找代价也相同吗？",
    "body": "<div class=\"course-workspace course-workspace-stacked\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"hash-card\"><p>两组不同关键字按序插入，均用 \\(m=7\\)、\\(h(k)=k\\bmod7\\)、线性探查。</p><p>\\(S_1=(3,4,5,6)\\)，\\(S_2=(3,10,17,24)\\)。</p></div><figure class=\"hash-figure\"><table class=\"hash-slots\"><thead><tr><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"hash-empty\">—</td><td class=\"\">3/3</td><td class=\"\">4/10</td><td class=\"\">5/17</td><td class=\"\">6/24</td></tr></tbody></table><figcaption>每个占用槽依次展示 S1/S2 的记录键；最终占用位置相同。</figcaption></figure></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>两组都是 \\(\\alpha=4/7\\)。计算两种情况下等概率成功 ASL，并说明不同原因。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>\\(S_1\\)：所有记录初始地址就是实际位置，ASL=1。\\(S_2\\)：四个键初始地址均为 3，探查次数 1、2、3、4，ASL=2.5。</p><p>装载因子相同不足以确定查找成本；分布、散列函数和探查路径仍起作用。这里两表的失败查找长度不会仅因为成功 ASL 不同而自动不同。</p></div></details></div></div>",
    "section": "cost",
    "role": "exercise",
    "goal": "用具体反例区分装载因子和冲突分布",
    "activity": "独立计算与解释"
  },
  {
    "id": "quadratic-note",
    "title": "跳过相邻槽位，就一定能找到空位吗？",
    "body": "<p class=\"hash-lead\">二次探查改变访问次序，必须声明具体的增量规则与表长。</p>\n<div class=\"hash-card\">\n<p><strong>教材 7.4.3 的双向平方探查</strong>：以初始地址 \\(h(k)\\) 为基点，按 \\(d_i=0,+1^2,-1^2,+2^2,-2^2,\\ldots\\) 尝试，并对槽位容量 \\(m\\) 取模。</p>\n<p>例如 \\(m=8,\\ h(k)=4\\)：前几次访问 <strong>4 → 5 → 3 → 0 → 0 → 5 → 3</strong>……，并未覆盖全部槽位。</p>\n</div>\n<p class=\"hash-note\">教材选择题 (14) 用表长 14、\\(H(key)=key\\bmod11\\)；应用题 (6) 另外限定只取正平方增量。按各题明示的规则演算，初始散列取模常数不必等于数组容量。</p>",
    "section": "cost",
    "role": "content",
    "goal": "认识探查覆盖与冲突减少不是同一问题",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "expected-cost",
    "title": "为什么不能无条件说“散列查找 O(1)”？",
    "body": "<table class=\"hash-table\"><thead><tr><th>分析对象</th><th>结论成立的条件</th></tr></thead><tbody>\n<tr><td>单次最坏查找</td><td>开放定址 O(m)；若 m=Θ(n) 则 O(n)。链地址法最坏 O(n)</td></tr>\n<tr><td>期望 O(1) 查找</td><td>需要适当的散列分布假设、受控装载因子和单位成本模型</td></tr>\n<tr><td>动态维护</td><td>墓碑、扩容会改变实际成本；一次重建可能为 O(n)</td></tr>\n<tr><td>与 AVL 比较</td><td>AVL 最坏 O(log n)，并支持有序区间查询</td></tr>\n</tbody></table>\n<p class=\"hash-note\">m 是槽位容量，n 是有效记录数；单次最坏界、概率期望和摊还成本不能互相替代。</p>",
    "section": "cost",
    "role": "content",
    "goal": "分清单次、期望、摊还与最坏保证",
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
    "role": "exercise",
    "goal": "在新情境中提出结构选择与适用条件",
    "activity": "独立判断并核对"
  },
  {
    "id": "code-bridge",
    "title": "数学探查过程在 C11 程序里对应什么？",
    "body": "<p class=\"hash-lead\">把地址、状态、探查次数与实际 C11 程序逐项对应。</p>\n<table class=\"hash-table\"><thead><tr><th>数学对象</th><th>程序接口</th><th>对应的计算职责</th></tr></thead><tbody>\n<tr><td>\\(k\\)、\\(m\\)、\\(p(k,i)\\)</td><td><code>key</code>、<code>CAP</code>、<code>position()</code></td><td>确定下一槽位</td></tr>\n<tr><td>EMPTY / DELETED / OCCUPIED</td><td><code>SlotState</code>、<code>lookup()</code></td><td>判断命中、继续或失败（参见正确性部分）</td></tr>\n<tr><td>探查次数、更新契约</td><td><code>probes</code>、<code>insert()</code>、<code>erase()</code></td><td>记录路径并维护去重及墓碑</td></tr>\n</tbody></table>\n<div class=\"hash-card\"><strong>本地编译：</strong><code>gcc -std=c11 -Wall -Wextra code/hash_demo.c -o hash_demo</code></div>\n<p class=\"hash-note\">先预测，再运行 <code>./hash_demo demo</code> 和 <code>./hash_demo --self-test</code> 核对；源码可复制到个人电脑任意目录，命令中的相对路径按实际位置调整。</p>",
    "section": "choice",
    "role": "content",
    "goal": "建立数学状态与 C11 变量及程序输出的对应",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "summary",
    "title": "我们究竟利用了关键字的什么信息？",
    "body": "<p class=\"hash-lead\">从按比较排除候选，到按散列计算候选地址。</p><table class=\"hash-table\"><thead><tr><th>定位路线</th><th>必须维护的性质</th><th>收益与限制</th></tr></thead><tbody><tr><td>AVL</td><td>关键字顺序 + 高度平衡</td><td>最坏对数查找；天然支持有序操作</td></tr><tr><td>散列表</td><td>映射 + 冲突规则 + 操作不变量</td><td>适当条件下精确查询期望高效；不直接提供顺序</td></tr></tbody></table><div class=\"hash-card\"><strong>独立检查：</strong>能否解释一个失败查找为什么正确？能否说明 ASL 的条件？能否对新的数据需求给出改选理由？</div>",
    "section": "choice",
    "role": "content",
    "goal": "回收映射—正确性—代价—选择的承重关系",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "homework",
    "title": "课后怎样预测、运行和核对？",
    "body": "<p class=\"hash-lead\">A、B 为正式必做；扩展自学不提交。</p>\n<div class=\"hash-pair\">\n  <div class=\"hash-card\"><p><strong>A · 书本习题</strong></p><p>第 7 章选择题 (12)(13)(14)、应用题 (5)。附选择理由，并保留构表、探查与 ASL 的关键过程。</p></div>\n  <div class=\"hash-card\"><p><strong>B · C11 程序实践</strong></p><p>先预测删除 17、查找 24/31、插入 24/31 后的状态与路径；本地运行 <code>code/hash_demo.c</code> 的 <code>demo</code> 与 <code>--self-test</code>，解释预测与实测。</p></div>\n</div>\n<p class=\"hash-note\">自学／选做，不提交：应用题 (6)(7)、算法设计题 (6)。</p>\n<p class=\"hash-note\"><strong>提交与过程记录：</strong>飞书文档链接，附 3–5 行过程记录；只运行示例无需截图或另附代码。共同要求见 <code>../../assignments/homework-guide.md</code>（课程作业规范）；不要求在 Git 仓库运行。</p>\n<p class=\"hash-note\">题号依据仓库第 7 章逐题核对清单；教师正式使用前仍须检查原教材题设、二次探查约定与本周累计作业量。</p>",
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
