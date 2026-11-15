"""D017: single source for slides, adopting CourseDeck/Section metadata."""
import json
from components import CourseDeck, Section

DECK_ID = "D017"
TITLE = "树表查找：BST 与 AVL"
MATH = True
COURSE = CourseDeck([
    Section("bridge", "从有序信息到动态需求", "已存在的有序信息，为什么还需要维护？", "D016回收、连续数组的插入成本", "理解动态有序集合的新问题"),
    Section("bst", "BST如何动态保持顺序", "如何在查找、插入和删除后保持顺序性质？", "递归顺序、BST搜索、插入与典型删除", "以统一的递归顺序性质解释BST操作"),
    Section("height", "为什么正确的BST仍可能低效", "相同关键字为何出现不同查找次数？", "插入顺序、树高和最坏代价", "区分算法正确性与性能保证"),
    Section("avl", "AVL怎样维护高度平衡", "如何保持有序的同时修复失衡？", "BF、单旋/双旋、独立核验", "理解AVL平衡维护机制与条件"),
    Section("choice", "维护平衡换来了什么", "什么时候值得支付额外维护成本？", "结构选择、C11接口、课程作业", "能够有条件地选择结构"),
])
PAGES = json.loads(r'''[
  {
    "id": "cover",
    "title": "树表查找：BST 与 AVL",
    "body": "<style>\n.d017-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;align-items:start}\n.d017-grid>div{min-width:0}\n.d017-panel{border:1px solid #bed0de;border-radius:12px;padding:.65rem .9rem;background:rgba(217,231,246,.18)}\n.d017-lead{font-size:1.16em;font-weight:650;line-height:1.4;color:#254b70;margin:.4rem 0 .65rem}\n.d017-note{font-size:.84em;line-height:1.4;color:#52657a;margin:.48rem 0}\n.d017-tree{width:100%;display:block;max-height:288px}\n.d017-table{border-collapse:collapse;width:100%;font-size:.9em;line-height:1.34;margin:.5rem 0}\n.d017-table th,.d017-table td{border-bottom:1px solid #c6d2de;text-align:left;vertical-align:top;padding:.36rem .55rem}\n.d017-table th{background:#e7f1fb;color:#22486e}\n.d017-pre{padding:.7rem .8rem;background:#f1f5f9;border:1px solid #ccd7e1;border-radius:9px;font-size:.82em;line-height:1.38;white-space:pre-wrap;color:#1d3549}\n.d017-key{font-weight:750;color:#24577f}\n.d017-inline{padding:.1rem .35rem;background:#e9f2fb;border-radius:.35rem}\n.d017-small{font-size:.85em}\n@media(max-width:850px){.d017-grid{grid-template-columns:1fr}.d017-tree{max-height:170px}}\n</style><p class=\"d017-lead\">数据不断变化时，怎样既保持有序查找的正确性，又避免搜索路径越来越长？</p><div class=\"d017-panel\"><p>从 D016 的静态有序查找进入动态结构维护。</p><p>两条性质线索：<strong>BST 顺序关系</strong>与<strong>AVL 高度平衡</strong>。</p></div><p class=\"d017-note\">D017｜树表查找。主问题、结构性质、动态操作、计算代价。</p>",
    "section": null,
    "role": "cover",
    "goal": "明确本讲研究的是**动态集合**，不是一次静态查询",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "outline",
    "title": "本讲要解决哪些问题？",
    "body": "",
    "section": null,
    "role": "outline",
    "goal": "认识“动态维护顺序—退化—平衡—选择”的阶段链",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "part-bridge",
    "title": "从已有顺序到动态维护",
    "body": "",
    "section": "bridge",
    "role": "section",
    "goal": "确定当前研究任务与 D016 的关系",
    "activity": "小节转折"
  },
  {
    "id": "recall-sorted",
    "title": "已排好序，为什么查找少比较？",
    "body": "<p class=\"d017-lead\">有序信息能够让一次比较排除一组不可能的关键字。</p><table class=\"d017-table\"><thead><tr><th>位置</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td>编号</td><td>16</td><td>20</td><td>27</td><td>30</td><td>36</td><td>44</td><td>55</td></tr></tbody></table><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><p>查找编号 27。中点为 30，按同一关键字严格升序排列。</p></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>为什么可以直接排除 30 和它的右侧？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>因为 27&lt;30，且 30 右侧所有关键字都更大。折半查找的判定树是分析对象，并非已建立的 BST。</p></div></details></div></div>",
    "section": "bridge",
    "role": "exercise",
    "goal": "回收折半排除依据和比较计数口径",
    "activity": "独立预测并核对"
  },
  {
    "id": "update-array",
    "title": "插入一个编号，哪些记录要移动？",
    "body": "<p class=\"d017-lead\">有序数组查找高效，但新记录进入中间时，需要维护连续存放的顺序。</p><table class=\"d017-table\"><thead><tr><th>插入前</th><th>下标 0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th></tr></thead><tbody><tr><td>编号</td><td>16</td><td>20</td><td>27</td><td>30</td><td>36</td><td>44</td><td>55</td></tr></tbody></table><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><p>任务：将编号 25 插入这张有序数组，假设预留容量足够。</p></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>原有记录中哪些需要向右移动？</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>移动原有编号 27、30、36、44、55，它们各向右移动一个位置。</p><p>完成数组：16、20、25、27、30、36、44、55。</p><p>定位插入位置与搬移记录是不同的成本。</p></div></details></div></div><p class=\"d017-note\">是否有一种无需整体移动这些记录的表示？</p>",
    "section": "bridge",
    "role": "exercise",
    "goal": "看见有序数组的更新成本",
    "activity": "独立预测并核对"
  },
  {
    "id": "part-bst",
    "title": "用链接组织有序关系",
    "body": "",
    "section": "bst",
    "role": "section",
    "goal": "引出树形表示作为候选",
    "activity": "小节转折"
  },
  {
    "id": "bst-order",
    "title": "只要求左孩子小于父结点，够吗？",
    "body": "<p class=\"d017-lead\">二叉搜索树（Binary Search Tree，BST；教材称二叉排序树）的顺序约束作用于整棵左右子树，而不只是直接孩子。</p><div class=\"d017-grid\"><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"平衡形态的普通 BST，高度三层\"><line x1=\"216\" y1=\"24\" x2=\"107\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"24\" x2=\"324\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"46\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"164\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"267\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"389\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"107\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"107\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"324\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"324\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"46\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"46\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"164\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"164\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"267\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"267\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"389\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"389\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg></div><div><div class=\"d017-panel\"><p><strong>定义</strong>：任一结点左子树中所有关键字均小于该结点，右子树所有关键字均大于它，两子树递归成立。</p><p><strong>反例</strong>：根 30、左孩子 20、20 的右孩子 35；35 在 30 的左子树，却大于 30。</p></div></div></div><p class=\"d017-note\">本讲关键字互异；重复关键字必须另外明确策略。</p>",
    "section": "bst",
    "role": "content",
    "goal": "建立**整个左子树、整个右子树**的递归顺序约束",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "bst-search",
    "title": "查找 27，为什么只走一条路径？",
    "body": "<p class=\"d017-lead\">查找 27：30 → 20 → 27。</p><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"平衡形态的普通 BST，高度三层\"><line x1=\"216\" y1=\"24\" x2=\"107\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"24\" x2=\"324\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"46\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"164\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"267\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"389\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"107\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"107\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"324\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"324\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"46\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"46\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"164\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"164\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"267\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"267\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"389\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"389\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg><div class=\"d017-panel\">27&lt;30：排除右子树。27&gt;20：排除左子树。命中 27。</div><p class=\"d017-note\">搜索失败：合法方向上遇到空链接；空链接本身不是一次关键字比较。</p>",
    "section": "bst",
    "role": "content",
    "goal": "解释左/右排除及查找命中/失败",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "bst-insert",
    "title": "插入新编号，为什么不需要移动其他记录？",
    "body": "<p class=\"d017-lead\">查找失败的位置：30 左侧 → 20 右侧 → 27 左侧 → 空链接。</p><div class=\"d017-grid\"><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"平衡形态的普通 BST，高度三层\"><line x1=\"216\" y1=\"24\" x2=\"107\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"24\" x2=\"324\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"46\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"164\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"267\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"389\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"107\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"107\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"324\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"324\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"46\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"46\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"164\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"164\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"267\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"267\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"389\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"389\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg><p class=\"d017-note\">插入前：在 27 的左空链接处停止。</p></div><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 240\" role=\"img\" aria-label=\"插入25后的完整BST，25是27的左孩子\"><line x1=\"215\" y1=\"24\" x2=\"103\" y2=\"79\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"215\" y1=\"24\" x2=\"327\" y2=\"79\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"103\" y1=\"79\" x2=\"47\" y2=\"143\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"103\" y1=\"79\" x2=\"163\" y2=\"143\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"327\" y1=\"79\" x2=\"273\" y2=\"143\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"327\" y1=\"79\" x2=\"387\" y2=\"143\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"163\" y1=\"143\" x2=\"115\" y2=\"215\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"215\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"215\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"103\" cy=\"79\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"103\" y=\"84\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"327\" cy=\"79\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"327\" y=\"84\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"47\" cy=\"143\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"47\" y=\"148\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"163\" cy=\"143\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"163\" y=\"148\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"273\" cy=\"143\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"273\" y=\"148\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"387\" cy=\"143\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"387\" y=\"148\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text><circle cx=\"115\" cy=\"215\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"115\" y=\"220\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">25</text></svg><p class=\"d017-note\">插入后：新结点 25 成为 27 的左孩子，其他结构不变。</p></div></div><p class=\"d017-note\">25&lt;30、25&gt;20、25&lt;27，满足所有祖先范围约束。定位沿搜索路径进行；旧记录不需要整体移动。</p>",
    "section": "bst",
    "role": "content",
    "goal": "将失败的空孩子位置与合法新叶子连接",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "bst-check",
    "title": "插入 25 后，怎样检验 BST 顺序性质？",
    "body": "<p class=\"d017-lead\">插入完成之后，怎样验证整棵树仍然满足 BST 顺序性质？</p><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"d017-panel\">在原树上插入 25。搜索路径：30 → 20 → 27 → 空。</div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>为什么 25 满足整棵 BST 的顺序性质？请给出祖先约束。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>25&lt;30、25&gt;20、25&lt;27；新叶子放在合法的空链接上，所有祖先定义的关键字范围仍成立。</p><p>中序顺序也可以核对，但不能取代对原因的解释。</p></div></details></div></div>",
    "section": "bst",
    "role": "exercise",
    "goal": "认识路径上祖先约束也必须保持",
    "activity": "独立预测并核对"
  },
  {
    "id": "bst-delete-cases",
    "title": "删除结点时，为什么不能只清空指针？",
    "body": "<p class=\"d017-lead\">删除结点后，不能丢失其余子树中的记录。</p><table class=\"d017-table\"><thead><tr><th>结点情况</th><th>结构处理</th><th>必须保持</th></tr></thead><tbody><tr><td>叶子（0个孩子）</td><td>断开连接</td><td>不丢失其他记录</td></tr><tr><td>仅1个孩子</td><td>该孩子接替原位置</td><td>原有关键字范围</td></tr><tr><td>2个孩子</td><td>前驱/后继替代，再删原位置</td><td>左右两侧仍满足大小关系</td></tr></tbody></table><p class=\"d017-note\">删除根时须更新根指针；不能把断开父链接视为所有情况的统一操作。</p>",
    "section": "bst",
    "role": "content",
    "goal": "区分零/一/二个孩子三类结构处理",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "bst-delete-two",
    "title": "删除根 30，应该选择哪个替代关键字？",
    "body": "<p class=\"d017-lead\">删除有两个孩子的根结点 30，怎样使其余关键字仍保持顺序？</p><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"平衡形态的普通 BST，高度三层\"><line x1=\"216\" y1=\"24\" x2=\"107\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"24\" x2=\"324\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"46\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"164\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"267\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"389\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"107\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"107\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"324\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"324\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"46\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"46\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"164\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"164\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"267\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"267\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"389\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"389\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>采用中序前驱法：先指出应由哪个关键字接替 30，再画出最终 BST，并解释理由。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"前驱27取代30后的BST\"><line x1=\"214\" y1=\"25\" x2=\"106\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"214\" y1=\"25\" x2=\"326\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"106\" y1=\"87\" x2=\"50\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"326\" y1=\"87\" x2=\"265\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"326\" y1=\"87\" x2=\"390\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"25\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"214\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">27</text><circle cx=\"106\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"106\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"326\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"326\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"50\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"50\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"265\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"265\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"390\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"390\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg><p>原位置的前驱结点必须同时删去。前驱不可能有右子树，但可能有左子树，需重接。</p></div></details></div></div>",
    "section": "bst",
    "role": "exercise",
    "goal": "用前驱替代解释正确性，不强迫完整指针实现",
    "activity": "独立预测并核对"
  },
  {
    "id": "part-height",
    "title": "都保持有序，为什么代价不同？",
    "body": "",
    "section": "height",
    "role": "section",
    "goal": "转向结构形态与路径工作量",
    "activity": "小节转折"
  },
  {
    "id": "two-builds",
    "title": "相同七个编号，两种插入顺序",
    "body": "<p class=\"d017-lead\">同一个关键字集合，插入顺序不同，普通 BST 的形态也不同。</p><div class=\"d017-grid\"><div><div class=\"d017-panel\"><p><strong>顺序 A</strong>：30、20、44、16、27、36、55</p><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"平衡形态的普通 BST，高度三层\"><line x1=\"216\" y1=\"24\" x2=\"107\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"24\" x2=\"324\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"46\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"164\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"267\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"389\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"107\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"107\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"324\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"324\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"46\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"46\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"164\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"164\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"267\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"267\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"389\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"389\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg></div></div><div><div class=\"d017-panel\"><p><strong>顺序 B</strong>：16、20、27、30、36、44、55</p><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 215\" role=\"img\" aria-label=\"顺序插入形成的右单支 BST，高度七层\"><line x1=\"32\" y1=\"22\" x2=\"92\" y2=\"48\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"92\" y1=\"48\" x2=\"151\" y2=\"74\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"151\" y1=\"74\" x2=\"210\" y2=\"100\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"210\" y1=\"100\" x2=\"271\" y2=\"126\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"271\" y1=\"126\" x2=\"334\" y2=\"152\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"334\" y1=\"152\" x2=\"398\" y2=\"179\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"32\" cy=\"22\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"32\" y=\"27\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"92\" cy=\"48\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"92\" y=\"53\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"151\" cy=\"74\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"151\" y=\"79\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"210\" cy=\"100\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"210\" y=\"105\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"271\" cy=\"126\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"271\" y=\"131\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"334\" cy=\"152\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"334\" y=\"157\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"398\" cy=\"179\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"398\" y=\"184\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg></div></div></div><p class=\"d017-note\">两棵树都符合 BST 顺序性质；后者不是逐次插入后平衡维护的 AVL。</p>",
    "section": "height",
    "role": "content",
    "goal": "发现树形依赖插入顺序",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "compare-path",
    "title": "查找 55，两棵 BST 分别访问多少个结点？",
    "body": "<p class=\"d017-lead\">给定相同的查找目标 55，先分别追踪两棵树的路径。</p><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"d017-grid\"><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"平衡形态的普通 BST，高度三层\"><line x1=\"216\" y1=\"24\" x2=\"107\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"24\" x2=\"324\" y2=\"87\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"46\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"107\" y1=\"87\" x2=\"164\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"267\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"324\" y1=\"87\" x2=\"389\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"107\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"107\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"324\" cy=\"87\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"324\" y=\"92\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"46\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"46\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"164\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"164\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"267\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"267\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"389\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"389\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg></div><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 215\" role=\"img\" aria-label=\"顺序插入形成的右单支 BST，高度七层\"><line x1=\"32\" y1=\"22\" x2=\"92\" y2=\"48\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"92\" y1=\"48\" x2=\"151\" y2=\"74\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"151\" y1=\"74\" x2=\"210\" y2=\"100\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"210\" y1=\"100\" x2=\"271\" y2=\"126\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"271\" y1=\"126\" x2=\"334\" y2=\"152\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"334\" y1=\"152\" x2=\"398\" y2=\"179\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"32\" cy=\"22\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"32\" y=\"27\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"92\" cy=\"48\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"92\" y=\"53\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"151\" cy=\"74\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"151\" y=\"79\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">27</text><circle cx=\"210\" cy=\"100\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"210\" y=\"105\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"271\" cy=\"126\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"271\" y=\"131\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">36</text><circle cx=\"334\" cy=\"152\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"334\" y=\"157\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">44</text><circle cx=\"398\" cy=\"179\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"398\" y=\"184\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">55</text></svg></div></div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>分别写出查找55的路径、访问结点次数和按层数计的树高。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><table class=\"d017-table\"><thead><tr><th></th><th>树 A</th><th>树 B</th></tr></thead><tbody><tr><td>查找路径</td><td>30→44→55</td><td>16→20→27→30→36→44→55</td></tr><tr><td>比较次数</td><td>3</td><td>7</td></tr><tr><td>高度</td><td>3</td><td>7</td></tr></tbody></table><p>比较次数按访问过的非空结点计，不等于源代码中关系运算符的执行次数。</p></div></details></div></div>",
    "section": "height",
    "role": "exercise",
    "goal": "量化不同树形的路径开销",
    "activity": "独立预测并核对"
  },
  {
    "id": "worst-shape",
    "title": "规模增长，单支树的查找代价怎样变化？",
    "body": "<p class=\"d017-lead\">有序性正确，并不等于性能稳定。</p><div class=\"d017-panel\"><p>普通 BST 查找、插入、删除需要沿搜索路径访问结点，时间随树高增长：\\(O(h)\\)。</p><p>升序插入 \\(n\\) 个不同的关键字形成高度 \\(n\\) 的单支树，最坏可达 \\(O(n)\\)。</p></div><p class=\"d017-note\">这里 \\(h\\) 按非空层数计：空树0，单结点1。平均成本还取决于插入和查询分布。</p>",
    "section": "height",
    "role": "content",
    "goal": "识别 `O(h)` 与最坏 `O(n)` 的条件",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "need-balance",
    "title": "有没有办法控制最长查找路径？",
    "body": "<p class=\"d017-lead\">BST 顺序性质回答“走哪一侧”，没有回答“最多走多深”。</p><div class=\"d017-grid\"><div><div class=\"d017-panel\"><p><strong>已经保证</strong></p><p>递归的关键字顺序：支持合法查找和动态更新。</p></div></div><div><div class=\"d017-panel\"><p><strong>尚未保证</strong></p><p>最长搜索路径：普通 BST 可以高度退化。</p></div></div></div><p>新设计问题：能否增加一种更新后仍能高效维护的高度约束？</p>",
    "section": "height",
    "role": "content",
    "goal": "建立平衡维护的设计动机",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "part-avl",
    "title": "增加什么性质，才能约束树高？",
    "body": "",
    "section": "avl",
    "role": "section",
    "goal": "提出可维护的局部条件",
    "activity": "小节转折"
  },
  {
    "id": "avl-definition",
    "title": "什么叫高度平衡？",
    "body": "<p class=\"d017-lead\">AVL 树（AVL Tree）是在 BST 上增加逐结点高度平衡约束的结构。</p><div class=\"d017-panel\"><p>统一树高：空树高度 0，单结点 1。</p><p>\\(h(T)=1+\\max(h(L),h(R))\\)</p><p>\\(BF(v)=h(L(v))-h(R(v))\\)，每个结点均需满足 \\(|BF(v)|\\le1\\)。</p></div><p class=\"d017-note\">BF 是平衡因子（Balance Factor），不是关键字比较结果。任何内部结点不满足约束，整树就不是 AVL。</p>",
    "section": "avl",
    "role": "content",
    "goal": "定义 AVL：每个结点两子树高差不超过 1 且子树递归成立",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "bf-every-node",
    "title": "这棵树满足 AVL 的全部平衡条件吗？",
    "body": "<p class=\"d017-lead\">计算平衡因子，判断整棵树是否符合 AVL 定义。</p><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"根BF=0但内部失衡\"><line x1=\"214\" y1=\"21\" x2=\"114\" y2=\"64\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"214\" y1=\"21\" x2=\"325\" y2=\"64\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"114\" y1=\"64\" x2=\"70\" y2=\"112\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"70\" y1=\"112\" x2=\"38\" y2=\"171\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"325\" y1=\"64\" x2=\"364\" y2=\"112\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"364\" y1=\"112\" x2=\"399\" y2=\"171\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"21\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"214\" y=\"26\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">40</text><circle cx=\"114\" cy=\"64\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"114\" y=\"69\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">20</text><circle cx=\"325\" cy=\"64\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"325\" y=\"69\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">60</text><circle cx=\"70\" cy=\"112\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"70\" y=\"117\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">10</text><circle cx=\"364\" cy=\"112\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"364\" y=\"117\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">70</text><circle cx=\"38\" cy=\"171\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"38\" y=\"176\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">5</text><circle cx=\"399\" cy=\"171\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"399\" y=\"176\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">80</text></svg></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>根结点 40 的 BF 是多少？整棵树是 AVL 吗？逐结点说明判断依据。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><p>根两侧高度均为3，BF(40)=0；但结点20的BF=+2，结点60的BF=−2，因此整棵树不满足每个结点的平衡约束。</p></div></details></div></div>",
    "section": "avl",
    "role": "exercise",
    "goal": "认识平衡约束是对所有结点的递归要求",
    "activity": "独立预测并核对"
  },
  {
    "id": "ll-trigger",
    "title": "依次插入 30、20、16，哪里首次失衡？",
    "body": "<p class=\"d017-lead\">依次插入 30、20、16：最新结点使哪位祖先首次失衡？</p><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"LL插入失衡\"><line x1=\"214\" y1=\"25\" x2=\"132\" y2=\"88\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"132\" y1=\"88\" x2=\"64\" y2=\"160\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"25\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"214\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">30</text><circle cx=\"132\" cy=\"88\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"132\" y=\"93\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"64\" cy=\"160\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"64\" y=\"165\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text></svg><div class=\"d017-panel\">从插入点16沿祖先向上，结点20的 BF=+1，结点30的 BF=+2。较高路径为左→左（LL）。</div><p class=\"d017-note\">这里先展示 BST 插入完成但尚未修复 AVL 的临时状态。</p>",
    "section": "avl",
    "role": "content",
    "goal": "从合法 AVL 插入过程找到最低失衡祖先",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "right-rotate",
    "title": "为什么要让 20 接替 30？",
    "body": "<p class=\"d017-lead\">LL 型失衡：对 30 做一次右旋。</p><div class=\"d017-grid\"><div><div class=\"d017-panel\"><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"LL插入失衡\"><line x1=\"214\" y1=\"25\" x2=\"132\" y2=\"88\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"132\" y1=\"88\" x2=\"64\" y2=\"160\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"25\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"214\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">30</text><circle cx=\"132\" cy=\"88\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"132\" y=\"93\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"64\" cy=\"160\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"64\" y=\"165\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text></svg><p class=\"d017-note\">旋转前：根30，BF=+2。</p></div></div><div><div class=\"d017-panel\"><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"单旋或双旋完成后的平衡结构\"><line x1=\"214\" y1=\"28\" x2=\"123\" y2=\"123\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"214\" y1=\"28\" x2=\"305\" y2=\"123\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"28\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"214\" y=\"33\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"123\" cy=\"123\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"123\" y=\"128\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"305\" cy=\"123\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"305\" y=\"128\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text></svg><p class=\"d017-note\">旋转后：根20，左右等高。</p></div></div></div><p>中序仍为16、20、30；同时检查每个结点BF，不能只因为看上去对称就宣称修复。</p>",
    "section": "avl",
    "role": "content",
    "goal": "理解一次右旋的局部链接含义和高度结果",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "rotation-order",
    "title": "子树 B 换了位置，顺序为何不变？",
    "body": "<p class=\"d017-lead\">含有非空子树时，旋转怎样保持顺序？</p><div class=\"d017-grid\"><div><pre class=\"d017-pre\"><code>右旋之前：\n      z\n     / \\\n    y   C\n   / \\\n  A   B</code></pre></div><div><pre class=\"d017-pre\"><code>右旋之后：\n      y\n     / \\\n    A   z\n       / \\\n      B   C</code></pre></div></div><div class=\"d017-panel\"><p>A、B、C 分别是可为空的整棵子树，顺序关系是 \\(A&lt;y&lt;B&lt;z&lt;C\\)。</p><p>旋转前后顺序不变；但是否恢复 AVL 还需要检查高度。</p></div>",
    "section": "avl",
    "role": "content",
    "goal": "推广到带 A、B、C 的一般右旋顺序保持",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "lr-single-fails",
    "title": "30、16、20，只对 30 右旋会怎样？",
    "body": "<p class=\"d017-lead\">针对这棵树，尝试只对 30 做一次右旋。</p><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><div class=\"d017-grid\"><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"LR插入失衡\"><line x1=\"214\" y1=\"25\" x2=\"132\" y2=\"88\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"132\" y1=\"88\" x2=\"199\" y2=\"162\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"25\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"214\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">30</text><circle cx=\"132\" cy=\"88\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"132\" y=\"93\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"199\" cy=\"162\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"199\" y=\"167\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text></svg></div><div><div class=\"d017-panel\">先预测：对30右旋后树形是什么？单旋的结果一定符合AVL吗？</div></div></div></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>画出单旋结果，计算新根BF。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"LR误单旋后仍不平衡\"><line x1=\"133\" y1=\"25\" x2=\"239\" y2=\"89\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"239\" y1=\"89\" x2=\"178\" y2=\"162\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"133\" cy=\"25\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"133\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">16</text><circle cx=\"239\" cy=\"89\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"239\" y=\"94\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"178\" cy=\"162\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"178\" y=\"167\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text></svg><p>新根16的右子树高2、左子树高0，BF(16)=−2；虽然 BST 顺序仍成立，但AVL平衡尚未恢复。</p></div></details></div></div>",
    "section": "avl",
    "role": "exercise",
    "goal": "用反例发现条件限制",
    "activity": "独立预测并核对"
  },
  {
    "id": "lr-double",
    "title": "为什么先左旋、再右旋？",
    "body": "<p class=\"d017-lead\">LR 失衡：先对16左旋，再对最低失衡祖先30右旋。</p><div style=\"display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.6rem\"><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"LR插入失衡\"><line x1=\"214\" y1=\"25\" x2=\"132\" y2=\"88\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"132\" y1=\"88\" x2=\"199\" y2=\"162\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"25\" r=\"18\" fill=\"#ffe2d8\" stroke=\"#d37855\" stroke-width=\"1.7\"/><text x=\"214\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#88412e\">30</text><circle cx=\"132\" cy=\"88\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"132\" y=\"93\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"199\" cy=\"162\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"199\" y=\"167\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text></svg><p class=\"d017-note\">① 失衡：30 左16 右20</p></div><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 240\" role=\"img\" aria-label=\"LR双旋中间状态：先对16左旋，30的左孩子是20，20的左孩子是16\"><line x1=\"215\" y1=\"24\" x2=\"128\" y2=\"89\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"128\" y1=\"89\" x2=\"50\" y2=\"161\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"215\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"215\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"128\" cy=\"89\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"128\" y=\"94\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"50\" cy=\"161\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"50\" y=\"166\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text></svg><p class=\"d017-note\">② 对16左旋：变为 LL 形态</p></div><div><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"单旋或双旋完成后的平衡结构\"><line x1=\"214\" y1=\"28\" x2=\"123\" y2=\"123\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"214\" y1=\"28\" x2=\"305\" y2=\"123\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"28\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"214\" y=\"33\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"123\" cy=\"123\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"123\" y=\"128\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">16</text><circle cx=\"305\" cy=\"123\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"305\" y=\"128\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text></svg><p class=\"d017-note\">③ 对30右旋：根20、左右16与30</p></div></div><p>最终中序仍为16、20、30；各结点平衡因子为0。中间第二步尚不是最终平衡结果。</p>",
    "section": "avl",
    "role": "content",
    "goal": "形成 LR 双旋机制",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "mirror-cases",
    "title": "RR、RL 为什么不用重新设计新操作？",
    "body": "<p class=\"d017-lead\">四个名称按失衡路径分类，只需两种基本旋转。</p><table class=\"d017-table\"><thead><tr><th>失衡路径</th><th>调整方式</th></tr></thead><tbody><tr><td>LL（左→左）</td><td>右旋</td></tr><tr><td>RR（右→右）</td><td>左旋</td></tr><tr><td>LR（左→右）</td><td>先对左孩子左旋，再对失衡祖先右旋</td></tr><tr><td>RL（右→左）</td><td>先对右孩子右旋，再对失衡祖先左旋</td></tr></tbody></table><p class=\"d017-note\">表格描述插入造成的最低失衡祖先。AVL 删除可能有孩子 BF=0，且可能继续向上修复。</p>",
    "section": "avl",
    "role": "content",
    "goal": "对称推出四种失衡类型与调整关系",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "independent-avl",
    "title": "新树插入 5 后，还需要调整吗？",
    "body": "<p class=\"d017-lead\">新树独立检验：插入 5 后，需要做什么？</p><div class=\"course-workspace\" data-course-component=\"task-workspace\"><div class=\"course-input\" data-task-input><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"独立任务初始 AVL\"><line x1=\"216\" y1=\"25\" x2=\"116\" y2=\"84\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"216\" y1=\"25\" x2=\"327\" y2=\"84\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"116\" y1=\"84\" x2=\"57\" y2=\"156\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"116\" y1=\"84\" x2=\"169\" y2=\"156\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"216\" cy=\"25\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"216\" y=\"30\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"116\" cy=\"84\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"116\" y=\"89\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"327\" cy=\"84\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"327\" y=\"89\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">40</text><circle cx=\"57\" cy=\"156\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"57\" y=\"161\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">10</text><circle cx=\"169\" cy=\"156\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"169\" y=\"161\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">25</text></svg><p class=\"d017-note\">初始为合法AVL，关键字互异；高度按层数计。</p></div><div class=\"course-task\"><div class=\"course-prompt\" data-task-prompt>先按 BST 规则插入，判断是否失衡；如有失衡，找出最低失衡祖先并完成必要调整。分别核对 BST 顺序与 AVL 平衡。</div><details class=\"course-answer\" data-task-answer><summary>核对答案与理由</summary><div class=\"course-solution\"><svg class=\"d017-tree\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 430 210\" role=\"img\" aria-label=\"独立任务旋转后AVL\"><line x1=\"214\" y1=\"24\" x2=\"110\" y2=\"88\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"214\" y1=\"24\" x2=\"326\" y2=\"88\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"110\" y1=\"88\" x2=\"48\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"326\" y1=\"88\" x2=\"269\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><line x1=\"326\" y1=\"88\" x2=\"391\" y2=\"159\" stroke=\"#677c94\" stroke-width=\"2\"/><circle cx=\"214\" cy=\"24\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"214\" y=\"29\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">20</text><circle cx=\"110\" cy=\"88\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"110\" y=\"93\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">10</text><circle cx=\"326\" cy=\"88\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"326\" y=\"93\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">30</text><circle cx=\"48\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"48\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">5</text><circle cx=\"269\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"269\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">25</text><circle cx=\"391\" cy=\"159\" r=\"18\" fill=\"#e1eefc\" stroke=\"#688bb5\" stroke-width=\"1.7\"/><text x=\"391\" y=\"164\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"700\" fill=\"#173e65\">40</text></svg><p>插入后BF(30)=+2、BF(20)=+1，LL型；对30右旋。中序5、10、20、25、30、40，所有结点BF绝对值≤1。</p></div></details></div></div>",
    "section": "avl",
    "role": "exercise",
    "goal": "在未直接演示的输入上自主定位、操作、核验",
    "activity": "独立预测并核对"
  },
  {
    "id": "part-choice",
    "title": "额外维护换来了什么？",
    "body": "",
    "section": "choice",
    "role": "section",
    "goal": "回到最初的动态需求",
    "activity": "小节转折"
  },
  {
    "id": "structure-choice",
    "title": "什么时候更愿意选数组、BST 或 AVL？",
    "body": "<p class=\"d017-lead\">没有无条件最好的结构；负载与保证条件共同决定选择。</p><table class=\"d017-table\"><thead><tr><th>结构</th><th>查找最坏代价</th><th>动态更新</th></tr></thead><tbody><tr><td>有序数组</td><td>O(log n)（随机访问）</td><td>任意位置插删可能移动O(n)记录</td></tr><tr><td>BST</td><td>O(h)，最坏O(n)</td><td>沿树高修改链接，可能退化</td></tr><tr><td>AVL</td><td>O(log n)</td><td>额外维护高度及必要旋转</td></tr></tbody></table><p class=\"d017-note\">还须考虑内存布局、缓存、比较成本、实际查询/更新分布与实现质量。</p>",
    "section": "choice",
    "role": "content",
    "goal": "条件化选择，不说 AVL 全场景最优",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "c-bridge",
    "title": "树形变化怎样对应 C 的左右指针？",
    "body": "<p class=\"d017-lead\">数学子树重接，怎样在 C11 中表达？</p><div class=\"d017-grid\"><div><pre class=\"d017-pre\"><code>Node *y = z-&gt;left;\nNode *middle = y-&gt;right;\ny-&gt;right = z;\nz-&gt;left = middle;</code></pre></div><div><div class=\"d017-panel\"><p>z：旧子树根；y：旧根的左孩子；middle：原来y的右子树。</p><p>完整旋转还要更新高度，并让原父结点指向新子树根y。</p></div></div></div><p class=\"d017-note\">完整、可编译的演示见本讲 code/bst_avl_demo.c，程序不代替性质证明。</p>",
    "section": "choice",
    "role": "content",
    "goal": "认识局部代码的字段职责",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "synthesis",
    "title": "动态有序查找需要同时保持哪些性质？",
    "body": "<p class=\"d017-lead\">BST 保证顺序，AVL 在其上增加高度约束。</p><table class=\"d017-table\"><thead><tr><th>对象</th><th>结构性质</th><th>主要结论</th></tr></thead><tbody><tr><td>BST</td><td>递归顺序不变量</td><td>沿合法搜索路径查找和动态修改</td></tr><tr><td>AVL</td><td>BST顺序 + 每个结点BF∈{−1,0,+1}</td><td>高度对数上界及有条件的操作保证</td></tr></tbody></table><div class=\"d017-panel\">仅中序严格递增，能否判断这棵树一定是 AVL？不能，还要逐结点检查高度。</div>",
    "section": "choice",
    "role": "content",
    "goal": "已能比较结构、识别操作维护",
    "activity": "讲述、观察与追问"
  },
  {
    "id": "homework",
    "title": "课后怎样预测、运行与核对？",
    "body": "<p><strong>A · 书本习题（必做）：</strong>第7章选择题 (7)(8)、应用题 (2)。选择题写理由，构造题保留关键推演。</p><p><strong>B · 程序实践（必做）：</strong>先预测两种插入顺序的BST树高和查找55的结点访问次数，再在个人电脑编译运行 <code>code/bst_avl_demo.c</code> 的 <code>bst</code> 模式核对；运行 <code>avl</code> 模式解释LR两次旋转。</p><pre class=\"d017-pre\"><code>gcc -std=c11 -Wall -Wextra -Werror code/bst_avl_demo.c -o d017_demo\n./d017_demo bst\n./d017_demo avl</code></pre><p class=\"d017-note\">A/B均提交，B保留预测、实测及解释；附3–5行过程记录。按<a href=\"../../assignments/homework-guide.md\">作业规范</a>通过飞书提交，不要求在Git仓库执行或推送代码。算法设计题(2)为选做。</p>",
    "section": "choice",
    "role": "content",
    "goal": "明确正式作业及教材接口",
    "activity": "讲述、观察与追问"
  }
]''')
for item in PAGES:
    if item["role"] == "outline":
        COURSE.outline()
    elif item["role"] == "section":
        COURSE.start_section(item["section"], page_id=item["id"])
    else:
        COURSE.add(item["id"], item["title"], item["body"], section=item["section"],
                   role=item["role"], goal=item["goal"], activity=item["activity"],
                   label="课程导入" if item["role"] == "cover" else "")
SLIDES = COURSE.finalize()
