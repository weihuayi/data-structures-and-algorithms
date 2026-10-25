"""D012: graph search, visited information, and pending work."""
from html import escape
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools/deck'))
from graph_diagram import graph, beside
from graph_trace import NODES, EDGES, ADJ, INDEX, bfs_player, dfs_player

DECK_ID = 'D012'
TITLE = '图的遍历：怎样组织待处理工作'
MATH = True


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>' + text + '</p></details>'


def answer(html, title='核对答案与理由'):
    return '<details><summary>' + title + '</summary>' + html + '</details>'


def main_graph(*, visited=(), current=None, tree_edges=(), caption=None, details=None, legend=None):
    states = None
    if visited or current or tree_edges:
        states = {}
        for vertex in NODES:
            if vertex == current:
                states[vertex] = 'current'
            elif vertex in visited:
                states[vertex] = 'visited'
            else:
                states[vertex] = 'unvisited'
    if caption is None:
        caption = '无向主例 A–E；E 为孤立点，位置不代表距离。'
        if states:
            caption = '无向主例 A–E；橙色为当前，蓝色为已访问，灰色为未访问；E 孤立。'
    if legend is None:
        legend = '红=树边。' if tree_edges else ''
    return graph(NODES, EDGES, caption=caption, marked=tree_edges, states=states,
                 node_details=details, legend=legend)


def matrix_table(highlight=None):
    head = '<tr><th>行/列</th>' + ''.join(
        f'<th{" class=\"matrix-focus\"" if v == highlight else ""}>{v}({INDEX[v]})</th>' for v in NODES) + '</tr>'
    rows = []
    for row in NODES:
        cells = ''
        for col in NODES:
            value = 1 if col in ADJ[row] else 0
            cells += f'<td>{value}</td>'
        cls = ' class="matrix-focus"' if row == highlight else ''
        rows.append(f'<tr{cls}><th>{row}({INDEX[row]})</th>{cells}</tr>')
    return '<table class="compact-table matrix-table"><thead>' + head + '</thead><tbody>' + ''.join(rows) + '</tbody></table>'


def adjacency_table(highlight=None):
    rows = []
    for vertex in NODES:
        items = ' '.join(f'{i}→{w}' for i, w in enumerate(ADJ[vertex])) or '空'
        cls = ' class="matrix-focus"' if vertex == highlight else ''
        rows.append(f'<tr{cls}><th>{vertex}({INDEX[vertex]})</th><td>{items}</td></tr>')
    return ('<table class="compact-table adjacency-table"><thead><tr><th>顶点（编号）</th>'
            '<th>邻接项（位置→邻居）</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')


def vertex_map():
    return ('<table class="compact-table vertex-map"><thead><tr><th>顶点标签</th>' +
            ''.join(f'<th>{v}</th>' for v in NODES) + '</tr></thead><tbody><tr><th>整数编号</th>' +
            ''.join(f'<td>{INDEX[v]}</td>' for v in NODES) + '</tr></tbody></table>')


def directed_graph():
    nodes = {'P': (80, 70), 'Q': (300, 70), 'R': (80, 215), 'S': (300, 215)}
    edges = [('P', 'Q'), ('P', 'R'), ('Q', 'S'), ('R', 'S')]
    return graph(nodes, edges, directed=True,
                 caption='独立有向小图 P、Q、R、S：箭头表示单向关系。')


def triangle_graph():
    nodes = {'A': (95, 80), 'B': (320, 80), 'C': (205, 235)}
    edges = [('A', 'B'), ('A', 'C'), ('B', 'C')]
    return graph(nodes, edges, caption='独立无向小图：A—B、A—C、B—C。')


def website_graph():
    nodes = {'P': (65, 80), 'Q': (230, 60), 'R': (230, 205),
             'S': (370, 130), 'T': (475, 130), 'U': (370, 250)}
    edges = [('P', 'Q'), ('P', 'R'), ('Q', 'S'), ('R', 'S'), ('S', 'T')]
    return graph(nodes, edges, directed=True,
                 caption='网页链接图：箭头表示可点击方向；U 无链接。')


SLIDES = [
['图的遍历：怎样组织待处理工作？',
 r'<p class="lead">有环、有多条到达路径，怎样不重不漏？</p><p>数据结构与算法 · D012</p><p class="small">承接 D011；教材 6.4–6.5</p>',
 '进入问题'],

['本讲要解决哪四个问题？',
 r'''<table><thead><tr><th>阶段</th><th>要解决的问题</th><th>页码</th></tr></thead><tbody>
 <tr><td>第一节</td><td>图怎样表示？遍历任务要输出什么？</td><td>3–8</td></tr>
 <tr><td>第二节</td><td>深度优先搜索怎样深入、返回、继续？</td><td>9–14</td></tr>
 <tr><td>第三节</td><td>广度优先搜索怎样用队列逐层扩展？</td><td>15–19</td></tr>
 <tr><td>第四节</td><td>两种搜索为什么正确、代价多少、何时不适用？</td><td>20–29</td></tr>
 </tbody></table><p><strong>补充与收口</strong>：30–34（十字链表/邻接多重表、作业、D013）。<br>每节先给出一个认知转折；小节标题页各约 0.5 分钟，不占用独立活动时间。</p>''',
 '课程路线'],

['第一节：从图的关系到遍历任务',
 r'<p class="lead">先看清对象和表示，再决定怎样走。</p><p>主例仍是无向道路图 A–E；E 是孤立点。遍历要回答：从某点出发能到哪些点，以及怎样不重不漏地走完。</p><p class="small">本节：主图 → 任务语义 → 邻居接口 → 矩阵/邻接表代价 → 有向出入邻居。</p>',
 '第一节 · 从图到遍历任务'],

['沿着道路走，树的遍历还能直接照搬吗？',
 beside(main_graph(), '<p>从 A 出发：怎样列出所有能到达的地点？<br>若到一个地点就递归走它的所有邻居，会发生什么？</p>') +
 note('先留 1 分钟回收 D008 的无环、单亲条件。A→B→A 已可无限往返，三角环也会重复到达。E 不可从 A 到达。主例沿用 D011，边 AB、AC、BC、CD；边无方向、无权。'),
 '第一节 · 从图到遍历任务'],

['任务要“从 A 可达”，还是“检查全图”？',
 beside(main_graph(), r'''<table><thead><tr><th>任务</th><th>应输出什么</th></tr></thead><tbody>
 <tr><td>从 A 查可达地点</td><td>A、B、C、D；E 不应混入</td></tr>
 <tr><td>检查全部地点</td><td>A、B、C、D、E；可能需要多个起点</td></tr>
 <tr><td>按最少边数分层</td><td>A=0 层，B/C=1 层，D=2 层；E 未到达</td></tr>
 </tbody></table><p>先确定输出语义，再选择访问策略。</p>''') +
 note('这里的层数是从源点出发经过的边数，与 D008 根层次为 1 的约定不同。访问集合相同，不代表顺序或距离也相同。'),
 '第一节 · 从图到遍历任务'],

['算法向表示索取什么操作？',
 beside(main_graph(), r'''<p><strong>neighbors(u)</strong> 按编号升序枚举邻居；<strong>visited[v]</strong> 记录是否已经访问；<strong>parent[v]</strong> 记录第一次访问的来源。</p>''' +
 adjacency_table()) +
 note('教材 ADT 的 FirstAdjVex、NextAdjVex 与 neighbors(u) 是同一枚举语义：取第一个、取下一个邻接点。程序使用 0 起下标：A=0、B=1、C=2、D=3、E=4。有向图默认枚举出邻居；首次访问 v 时立即置 visited[v]=true 并输出；visited[v]=true 也不表示 v 的邻接点已处理完。'),
 '第一节 · 从图到遍历任务'],

['同一个 neighbors，扫描代价从哪里来？',
 beside(main_graph(current='C', caption='当前关注 C；C 的邻居是 A、B、D。'), r'''<p>同一图、同一枚举语义：矩阵 5 格，邻接表 3 项。</p>''' +
 matrix_table('C') + r'''<p>C 的邻接表 3 项；矩阵 C 行 5 格（3 个 1、2 个 0）。</p>''') +
 note('矩阵行 1、1、0、1、0。矩阵和邻接表描述同一个图；表示不同会改变邻居枚举机制和代价，不改变实际邻接关系。构造矩阵/邻接表另有成本，本页只比较枚举阶段。演示邻接表采用连续邻居数组，保留“仅枚举实际邻接项”的机制。'),
 '第一节 · 从图到遍历任务'],

['有向边的入邻居和出邻居相同吗？',
 beside(directed_graph(), r'''<p>D011 的带权时间网已有方向；这里用<strong>独立无权小图</strong> P/Q/R/S，只看入/出邻居。它与无向主例不是同一张图。</p>
 <table class="compact-table"><thead><tr><th>顶点</th><th>出邻居</th><th>入邻居</th></tr></thead><tbody>
 <tr><td>P</td><td>Q、R</td><td>空</td></tr><tr><td>Q</td><td>S</td><td>P</td></tr>
 <tr><td>R</td><td>S</td><td>P</td></tr><tr><td>S</td><td>空</td><td>Q、R</td></tr>
 </tbody></table><p>出邻接表：P:[Q,R]、Q:[S]、R:[S]、S:[]；<br>逆邻接表：P:[]、Q:[P]、R:[P]、S:[Q,R]。</p>''') +
 note('逆邻接表不是把原图的弧反过来，而是把同一组弧按“谁指向我”重新组织。教材应用题 (1) 要求入度、出度、矩阵、邻接表和逆邻接表。本页不复制教材附图；P/Q/R/S 是独立小例，不与主例混用。'),
 '第一节 · 从图到遍历任务'],

['第二节：深度优先搜索',
 r'<p class="lead">深度优先搜索（Depth First Search，DFS）沿着一条分支深入，直到必须返回。</p><p>返回后，程序怎样知道当前顶点从哪个邻接项继续？栈和游标要记住什么？</p><p class="small">本节：访问标记 → DFS 定义 → 递归轨迹 → 邻接顺序 → 显式帧栈。</p>',
 '第二节 · 深度优先搜索'],

['看到邻居，为什么不能立即再走一次？',
 beside(main_graph(visited={'A', 'B'}, current='B', caption='B 当前；A、B 已访问；C、D、E 未访问。'), r'''<pre>若 v 尚未访问：
    visited[v] = true
    parent[v] = u
    输出 v，并安排它的后续工作
否则：跳过这次重复到达</pre>
 <div class="quote compact-quote"><strong>本讲不变量</strong>：每个顶点至多被安排一次；visited 一旦为真不再变回假；parent 只在首次访问时写入。visited[v]=true 只表示首次访问已发生，不代表 v 的邻接点已处理完。</div>''') +
 note('本讲与教材一致使用 visited（已访问），标记时机为首次访问时，不等到邻居处理完。B 再看到 A 时跳过；A 后来看 C 时，C 可能已被深度优先搜索访问过。'),
 '第二节 · 深度优先搜索'],

['先把一条分支探索完：DFS',
 beside(main_graph(visited={'A'}, current='A', caption='从 A 开始；A 已访问。'), r'''<pre>dfs(u):                     # u 已访问
    对每个邻居 v（按编号升序）：
        若 v 未访问：
            访问 v：
                visited[v]=true；parent[v]=u
                输出 v
            dfs(v)</pre>
 <div class="quote compact-quote"><strong>教材定义（概述）</strong>：深度优先搜索（Depth First Search，DFS）：沿未访问邻接点深入，无法继续时回溯。</div>
''') +
 note('根由外层先访问；返回后继续检查当前顶点的下一个邻接项。教材 6.5.1 算法 6.3 在进入 DFS(v) 时置 visited[v]=true 并输出；本页把访问动作写在父结点一侧（调用 dfs(v) 之前完成），中间无其他操作，语义一致。'),
 '第二节 · 深度优先搜索'],

['DFS 怎样深入，又怎样返回？',
 '<p class="small">先预测下一步：会深入，还是会返回？推演结束后，红线会连成从 A 出发的<strong>深度优先生成树</strong>；E 不在其中。</p>' + dfs_player('recursive'),
 '第二节 · 深度优先搜索'],

['把邻居编号降序后，DFS 会先走谁？',
 beside(main_graph(visited={'A', 'C'}, current='C', tree_edges=[('A', 'C')], caption='降序 DFS：A、C 已访问；当前 C。'), r'''<p><strong>顶点标签与整数编号</strong></p>''' + vertex_map() + r'''
 <table class="compact-table"><thead><tr><th>顶点</th><th>升序（编号小→大）</th><th>降序（编号大→小）</th></tr></thead><tbody>
 <tr><td>A(0)</td><td>B(1)、C(2)</td><td>C(2)、B(1)</td></tr>
 <tr><td>C(2)</td><td>A(0)、B(1)、D(3)</td><td>D(3)、B(1)、A(0)</td></tr>
 </tbody></table>
 <p>DFS 已访问 A、C；下一位 ______，再下一位 ______。</p><p class="small">降序是按整数顶点编号从大到小枚举邻居，不是字母顺序，也不是图上的几何位置。邻接顺序改变，边的存在性不变。</p>''') +
 note('2 分钟补全及解释：A C D B，树边 AC、CD、CB；集合仍为 A B C D。不能把存储表示名称当成序列的唯一决定因素：还取决于起点、邻接次序、搜索策略。'),
 '第二节 · 深度优先搜索'],

['不用递归，栈里要记住什么？',
 r'''<p class="small">Frame 保存 <strong>vertex</strong> 与 <strong>next</strong>：next 是下一项待检查邻接表位置，不是顶点编号、顶点深度或邻居编号。每跳过或访问一个邻接项，next 都前进。</p>''' +
 dfs_player('stack'),
 '第二节 · 深度优先搜索'],

['第三节：广度优先搜索',
 r'<p class="lead">广度优先搜索（Breadth First Search，BFS）先访问近邻，再逐层向外。</p><p>队列保存什么？为什么首次访问就要标记、入队？每一层怎样保证距离非递减？</p><p class="small">本节：BFS 定义 → 队列推演 → 晚标记反例 → 正确性。</p>',
 '第三节 · 广度优先搜索'],

['先处理已经访问的近邻：BFS',
 beside(main_graph(visited={'A'}, current='A', caption='BFS 起点 A：已访问并入队。'), r'''<pre>访问起点 s：visited[s]=true；输出 s
    distance[s]=0；s 入队
只要队列不空：
    u 出队
    对每个尚未访问的邻居 v：
        visited[v]=true；parent[v]=u
        输出 v；distance[v]=distance[u]+1
        v 入队</pre>
 <p class="small"><strong>教材定义（概述）</strong>：广度优先搜索（BFS）先访问近邻，再逐层向外扩展。</p>
 ''') +
 note('输出发生在首次访问时；队列保存已访问、尚未完成邻接扫描的顶点。教材 6.5.2 算法 6.7：访问 w 时立即置 visited[w]=true，随后 w 入队——先标记、再入队。'),
 '第三节 · 广度优先搜索'],

['B 看见 C 时，C 还在队列里',
 '<p class="small">观察：DFS 与 BFS 的访问序列同为 ABCD，但搜索树和深度不同；不能仅凭打印序列判断机制。</p>' + bfs_player(),
 '第三节 · 广度优先搜索'],

['等出队才标记，会怎样？',
 r'''<p>A 已把 B、C 入队；若 C 还未访问，处理 B 时又会把 C 入队。</p><pre>正确位置：访问 v（visited[v]=true）→ 入队 v
错误预测：队列可能出现 C、C</pre><p>标记前移，使每个顶点至多入队一次。</p>''' +
 note('让学生先预测重复项。晚标记并在出队时过滤的另一种算法可能仍得到可达集合，但会重复入队，不能沿用本实现的容量与一次入队论证。此处不把所有晚标记算法都判作不正确。'),
 '第三节 · 广度优先搜索'],

['为什么不重复、不遗漏，而且会结束？',
 r'''<ul><li><strong>不重复</strong>：第 8 页不变量——首次访问即标记；只安排未访问顶点。</li><li>不遗漏：若某可达点漏掉，沿源到它的路径找第一个漏点；其前驱被处理时本应访问它。</li><li>终止：顶点有限，每个顶点只安排一次，邻接枚举也有限。</li></ul>''' +
 note('假设图在搜索中不变，邻接枚举完整且终止。全图无遗漏还需外层扫描。这里只用任务相关的正确性语言，不新增统一证明框架的背诵要求。'),
 '第三节 · 广度优先搜索'],

['第四节：性质、代价与应用',
 r'<p class="lead">为什么正确？代价从哪里来？什么时候不能用？</p><p>比较 DFS 与 BFS 的结果、距离、顺序依赖、全图覆盖和有向边界，再用一个独立任务检验迁移。</p><p class="small">本节：顺序 → 代价 → 距离 → 全图 → 有向边界 → 独立任务。</p>',
 '第四节 · 性质、代价与应用'],

['顺序改变后，哪些结果真的变了？',
 beside(main_graph(caption='固定从 A 出发；邻居按编号降序。'), r'''<p>降序邻接：A:[C,B]　B:[C,A]　C:[D,B,A]　D:[C]</p><p>先写出 DFS 与 BFS 的访问序列、parent 和 D 的 BFS 距离（DFS 另写树深度）；再打开“核对答案与理由”。</p><p class="small">编号：A=0、B=1、C=2、D=3、E=4；可达集合、BFS 距离、parent 哪些会变？</p>''' +
 answer(r'''<table class="compact-table"><thead><tr><th>固定从 A 出发</th><th>DFS</th><th>BFS</th></tr></thead><tbody><tr><td>邻居升序</td><td>A B C D</td><td>A B C D</td></tr><tr><td>邻居降序</td><td>A C D B</td><td>A C B D</td></tr></tbody></table><p class="small">DFS parent：升 -1,0,1,2；降 -1,2,0,2。<br>BFS parent：-1,0,0,2；距离 0,1,1,2；集合不变。</p>''')), '第四节 · 性质、代价与应用'],

['遍历的代价来自哪些扫描？',
 r'''<table><thead><tr><th>完整遍历 n 个顶点</th><th>枚举总工作</th><th>时间</th></tr></thead><tbody><tr><td>邻接矩阵</td><td>每个顶点扫描 n 个位置</td><td>\(O(n^2)\)</td></tr><tr><td>邻接表</td><td>n 个表头及全部邻接项</td><td>\(O(n+m)\)</td></tr></tbody></table><p>空间：visited、parent、distance 与栈/队列均为 \(O(n)\)；不计图与输出。</p><p class="small">m 为边数（教材记 e）；无向图有 2m 个邻接项，有向图有 m 个。</p>''' +
 note('visit 假定 O(1)。单源只到达 r 个顶点时：矩阵扫描 rn 格，表扫描可达顶点的出邻接项；本程序初始化 n 个状态另需 O(n)。主例单源矩阵 20 格、表 8 项；全图矩阵 25 格、表仍 8 项。教材 6.5.1/6.5.2 的结论：邻接矩阵 O(n²)，邻接表 O(n+e)。表中用 O 表示上界，与教材 6.5 的写法对齐；对“完整遍历”也可写紧界 Θ，本讲不展开 O/Θ 的区别。'),
 '第四节 · 性质、代价与应用'],

['队列层次能回答哪一种距离？',
 beside(main_graph(visited={'A', 'B', 'C', 'D'}, tree_edges=[('A', 'B'), ('A', 'C'), ('C', 'D')], caption='BFS 树：蓝=已访问，红=树边；E 不可达。', legend=''), r'''<p>主例 BFS：A=0，B=1，C=1，D=2，E=-1。<br>主例 DFS 树深度：A=0，B=1，C=2，D=3。</p><p>BFS 按距离非递减处理顶点；首次访问 v 时，distance[v] 即等于从 A 到 v 的最少边数。<br>若道路耗时不同，最少边数不保证耗时最少。</p><p class="small">红边构成教材的<strong>广度优先生成树</strong>；DFS 的 distance 是搜索树深度，不是最少边数距离。</p>''') +
 note('按层归纳：处理距离 k 的顶点时，新访问的邻居给出 k+1；若它有更短路径，其前驱应更早被处理并访问它，与首次访问矛盾。反例：直达 AD 耗时 10，A→C→D 各 1，则一条边反而更慢。BFS 距离结论适用于无权或每边等代价；D014 处理带权最短路径。E 的 -1 是未到达哨兵，不是负距离。'),
 '第四节 · 性质、代价与应用'],

['一次搜索结束了，为什么 E 还没检查？',
 beside(main_graph(visited={'A', 'B', 'C', 'D'}, tree_edges=[('A', 'B'), ('B', 'C'), ('C', 'D')], caption='从 A 单源 DFS：只覆盖 A–D；E 仍未被访问。'), r'''<pre>初始化一次 visited
for 每个顶点 v（按编号）：
    if v 未访问：
        从 v 开始 DFS 或 BFS</pre><p>无向图：每次新起点对应一个连通分量。<br>从 A 的单源搜索只覆盖 {A,B,C,D}；E 仍灰，不能称为覆盖全图的生成树。<br>外层再以 E 为起点，两棵树合成<strong>生成森林</strong>。</p>''') +
 note(r'本例根 A、E，森林边数 \(n-c=5-2=3\)。不同源之间不重置 visited；下一次独立搜索才重置。教材算法 6.4：每调用一次单源 DFS 就遍历一个连通分量，调用次数即连通分量数。'),
 '第四节 · 性质、代价与应用'],

['搜索森林的树数，就是强连通分量数吗？',
 beside(graph({'B': (120, 90), 'A': (340, 90)}, [('B', 'A')], directed=True,
              caption='有向图 B→A：从 B 可到 A；从 A 不能到 B。'), r'''<p><strong>全图遍历</strong>按外层顶点顺序 A、B：先 A 得到树 {A}，再 B 得到树 {B,A}，共 2 棵树。</p><p>按外层顺序 B、A：先 B 得到树 {B,A}，A 已访问，共 1 棵树。</p>
 <table class="compact-table"><thead><tr><th>外层顺序</th><th>搜索森林</th><th>强连通分量</th></tr></thead><tbody>
 <tr><td>A、B</td><td>{A}、{B,A}（2 棵）</td><td>{A}、{B}</td></tr>
 <tr><td>B、A</td><td>{B,A}（1 棵）</td><td>{A}、{B}</td></tr>
 </tbody></table><p>强连通分量（Strongly Connected Component，SCC）是任意两个顶点互相可达的极大子图。两种顺序下 SCC 都是 {A}、{B}；一棵搜索树可以包含多个 SCC，树数不能当作 SCC 数。</p>'''),
 '第四节 · 性质、代价与应用'],

['先预测，再运行：同序列也可能不同机制',
 r'''<p>写下主例的 DFS/BFS 访问序列、parent 与 D 的 DFS 树深度（BFS 另写距离）；再预测邻接顺序反转、单源改全图后的变化。</p><p>在本讲目录运行：</p><pre>gcc -std=c11 -Wall -Wextra code/traversal_demo.c -o /tmp/d012
/tmp/d012</pre><p class="small">比较 DFS/list 与 DFS/stack，再比较 BFS/list 与 BFS/matrix。</p>''' +
 note('程序四种组合共享输入和编号顺序。学生先保留纸面预测，不以截图替代解释。parent 输出是 0 起编号，-1 表示根或未访问，需结合 visited 与距离区分。'),
 '第四节 · 性质、代价与应用'],

['预测不一致时，先检查什么？',
 r'''<table><thead><tr><th>现象</th><th>优先核对</th></tr></thead><tbody><tr><td>可达集合不同</td><td>方向、遗漏邻接项、标记初始化</td></tr><tr><td>集合相同但顺序不同</td><td>起点、邻接次序、栈/队列规则</td></tr><tr><td>序列相同但树不同</td><td>parent 赋值时机、待处理工作</td></tr><tr><td>扫描数不同</td><td>矩阵格子还是实际邻接项</td></tr></tbody></table><p>再用孤立点、环、单顶点与单向弧检查解释是否成立。</p>''' +
 note('固定回归检查与展示案例分开。不要删断言掩盖输入差异。程序报告通过只覆盖已执行检查，不证明任意实现都正确。'),
 '第四节 · 性质、代价与应用'],

['新任务：网站导航最少需要点击几次？',
 beside(website_graph(), r'''<p>箭头表示可点击方向；链接不保证可以反向点击。</p><ol><li>从图中确认对象、方向与表示，选择搜索策略。</li><li>从 P 手推过程，写 T 的最少点击数、U 的状态。</li><li>交换 P 的邻接顺序，哪些结果可变，哪些不变？</li></ol>''' +
 answer(r'''<p class="small"><strong>有向邻接表</strong>：P:[Q,R]；Q:[S]；R:[S]；S:[T]；T:[]；U:[]。</p><p class="small">BFS 顺序 P Q R S T；T=3，U 不可达。parent：Q=P、R=P、S=Q 或 R、T=S；distance：0,1,1,2,3,-1。</p><p class="small">换序只改 Q/R 的次序与 S 的父；T=3、U 不可达不变。DFS 可判可达，但不能用树深度保证最少点击。</p><p class="small">理由：BFS 逐层，首次访问 T 时距离已最少；U 无入边。</p>''')) +
 note('保留 7 分钟独立作答、2 分钟反馈。最低证据：有向图；稀疏邻接表可枚举；FIFO 与首次访问即标记；PQ R S T 或 PR Q S T，T=3、U 不可达；S 的父可变，距离不变。若选 DFS 求可达可以，但不能用首次访问的树深度保证最少点击。若 7 分钟内多数学生只完成前两问，第 3 问改为口头追问或课后小题，保留建模与 BFS 轨迹；记录实际用时。'),
 '第四节 · 性质、代价与应用'],

['图关系、辅助信息与工作纪律如何配合？',
 r'''<table><thead><tr><th>层次</th><th>本讲作用</th></tr></thead><tbody><tr><td>原图与表示</td><td>保存真实邻接；决定枚举代价</td></tr><tr><td>visited / parent / distance</td><td>积累访问信息与搜索结果</td></tr><tr><td>调用栈 / 显式帧栈</td><td>深入后记得返回并继续</td></tr><tr><td>FIFO 队列</td><td>按最少边数的层次扩展</td></tr></tbody></table><p><strong>不变量</strong>：每个顶点至多被安排一次；visited 只增不减。</p><p>选择策略，要回到任务需要的输出与成立条件。</p>''',
 '第四节 · 性质、代价与应用'],

['补充：扩展存储',
 r'<p class="lead">普通邻接表已经能枚举邻居，为什么还需要其它结构？</p><p>有向图：邻接表容易找出度，找入度要扫全部边表；无向图：一条边在邻接表里有两份记录，边操作要在两处找到同一条边。</p><p class="small">补充板块：十字链表（6.4.3）→ 邻接多重表（6.4.4）→ 回到作业与下一讲。</p>',
 '补充 · 扩展存储'],

['十字链表：同一条弧为什么能从两个入口找到？',
 beside(directed_graph(), r'''<table class="compact-table"><thead><tr><th>弧结点</th><th>tailvex</th><th>headvex</th><th>hlink（同头）</th><th>tlink（同尾）</th></tr></thead><tbody>
 <tr><td>a1</td><td>P</td><td>Q</td><td>—</td><td>a2</td></tr>
 <tr><td>a2</td><td>P</td><td>R</td><td>—</td><td>—</td></tr>
 <tr class="matrix-focus"><td>a3</td><td>Q</td><td>S</td><td>a4</td><td>—</td></tr>
 <tr><td>a4</td><td>R</td><td>S</td><td>—</td><td>—</td></tr>
 </tbody></table>
 <p class="small"><strong>firstin</strong>：P—，Q a1，R a2，S a3。<br><strong>firstout</strong>：P a1，Q a3，R a4，S—。</p>
 <p>a3（Q→S）既在 Q 的 firstout 链上，也在 S 的 firstin 链上；同一条弧，两个入口。</p>''') +
 note('十字链表把邻接表与逆邻接表结合：每条弧一个结点，同时挂在“同尾”和“同头”两条链上。教材 6.4.3：弧结点 tailvex/headvex 是弧尾/弧头位置，hlink 指向弧头相同的下一条弧，tlink 指向弧尾相同的下一条弧；顶点结点 firstin/firstout 分别指向第一条入弧/出弧。本页不展开建表与增删代码。'),
 '补充 · 扩展存储'],

['邻接多重表：一条无向边只存一份记录',
 beside(triangle_graph(), r'''<p>普通无向邻接表把一条边存两份；邻接多重表每条边只建一个结点，同时挂在两个端点的链上。</p>
 <table class="compact-table"><thead><tr><th>边结点</th><th>mark</th><th>ivex</th><th>jvex</th><th>ilink</th><th>jlink</th></tr></thead><tbody>
 <tr class="matrix-focus"><td>e1</td><td>unvisited</td><td>A</td><td>B</td><td>e2</td><td>e3</td></tr>
 <tr><td>e2</td><td>unvisited</td><td>A</td><td>C</td><td>—</td><td>e3</td></tr>
 <tr><td>e3</td><td>unvisited</td><td>B</td><td>C</td><td>—</td><td>—</td></tr>
 </tbody></table>
 <p class="small"><strong>firstedge</strong>：A e1、B e1、C e2。<br>e1（A—B）经 ilink 进 A 的边链、经 jlink 进 B 的边链；同一个边结点被两个端点共享。</p>
 <p class="small">mark 标记“这条边是否被搜索/处理过”，不是顶点访问标志 visited[v]。</p>''') +
 note('教材 6.4.4：边结点 mark 是边标志域，ivex/jvex 是两端点位置，ilink/jlink 分别指向依附两个端点的下一条边；顶点结点 firstedge 指向第一条依附边。邻接多重表与邻接表存储量同阶，但每条边只有一个结点。'),
 '补充 · 扩展存储'],

['课后：教材导航与正式作业',
 r'''<p><strong>教材导航</strong>：精读 6.4.1–6.4.2、6.5；6.4.3–6.4.4 按第 31–32 页自学。</p><p><strong>A. 书本习题</strong>：第 6 章选择题 <strong>(4)(6)(8)(9)(13)(14)</strong>、应用题 <strong>(1)(3)</strong>、算法设计题 <strong>(2)</strong>。写理由、推演或实现过程。</p><p><strong>B. 程序实践</strong>：预测主例 BFS，再加无向边 DE；提交新顺序、parent、从 A 的距离与邻接项扫描数，运行 homework+BFS 核对，解释 E 的变化。</p><div class="submission-note"><strong>提交</strong>：A、B 与 3–5 行过程记录，遵循<a href="../../assignments/homework-guide.md">作业规范</a>。<br><strong>自学不提交</strong>：算法题 (4)(5)；用应用题 (1)(2) 的图练习扩展存储。</div>''' +
 note('A 题号直接采用仓库 D012 清单，不把清单内核心题另降为待确认或选做。教材图未在本课复制，题目以教材原图为准。B 新增 DE 后 BFS=ABCDE，parent=-1,0,0,2,3，距离=0,1,1,2,3；表扫描 10 项，若矩阵单源则 25 格。'),
 '收口 · 作业与下一讲'],

['搜索得到的树，是连接成本最低的树吗？',
 beside(graph({'A': (80, 90), 'B': (320, 60), 'C': (240, 235)}, [('A', 'B'), ('A', 'C'), ('B', 'C')], labels={('A', 'B'): 10, ('A', 'C'): 1, ('B', 'C'): 1}, caption='三角形：AB=10，AC=1，BC=1；位置不表示距离。'), r'''<p>DFS/BFS 记录“第一次如何到达”，形成搜索树。<br>若每条道路有建设成本，换一个搜索顺序就能保证总成本最小吗？</p><p class="lead">D013：最小生成树与并查集。</p>''') +
 note('用三角形边权 AB=10、AC=1、BC=1：按顶点编号升序（不是按权值）DFS 可选 AB、BC，成本 11，另一棵树 AC、BC 成本 2。遍历树不是最小生成树；最少源路径边数也不同于全网最小连接成本。'),
 '收口 · 作业与下一讲'],
]
