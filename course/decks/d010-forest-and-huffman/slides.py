"""D010: preserving hierarchy through representation; optimizing weighted paths."""
from html import escape
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools' / 'deck'))
from tree_diagram import tree, beside, gallery
from tree_trace import player
from huffman_trace import merge_states, decode_states, selection_scan_states

DECK_ID = 'D010'
TITLE = '树与森林的表示转换、哈夫曼编码'
MATH = True


def note(text):
    return '<details class="teacher-note"><summary>教学注记</summary><p>' + text + '</p></details>'


def code(text):
    return '<pre>' + escape(text) + '</pre>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>' + x + '</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + x + '</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table>'


def definition(text):
    return '<div class="quote compact-quote"><strong>教材定义（概述）</strong><br>' + text + '</div>'



def fold(title, body):
    return '<details><summary>'+title+'</summary>'+body+'</details>'


def task_beside(context, content):
    return beside('<div>'+context+'</div>', content)


def learning_task(body):
    return '<div class="learning-task">'+body+'</div>'


def answer_fold(page, title, body):
    return fold(title, body).replace('<details>', f'<details name="d010-p{page}-support">', 1)



def activity(page, context, task, workspace, supports, teacher):
    feedback='<div class="tree-answer tree-swap"><div class="tree-preview">'+workspace+'</div>'
    feedback+=''.join(answer_fold(page,title,body) for title,body in supports)+'</div>'
    return learning_task(task_beside(context+note(teacher),task+feedback))


def contraction_diagram():
    return tree({'p':(150,35,'a+b',''),'a':(60,170,'a',''),'b':(240,170,'b',''),
                 'q':(470,35,'a+b','')}, [('p','a'),('p','b')],
                caption='左：收缩前的兄弟叶子；右：收缩后的一片叶子',height=240)


def first_merge_record():
    return tree({'p':(300,35,'[4]','weight=4'), 'c':(140,195,'[2]','C：2'),
                 'd':(460,195,'[3]','D：2')},[('p','c'),('p','d')],
                caption='主例首轮：C2、D2 合并；方括号是数组下标',height=270,
                edge_labels={('p','c'):'left',('p','d'):'right'})


def forest(binary=False, caption=None):
    if binary:
        points={'A':(300,35),'B':(180,130),'G':(490,130),'E':(80,230),'C':(280,230),'H':(440,230),'F':(150,330),'D':(350,330)}
        edges=[('A','B'),('A','G'),('B','E'),('B','C'),('G','H'),('E','F'),('C','D')]
        labels=dict(zip(edges,['L','R','L','R','L','R','R']))
    else:
        points={'A':(240,35),'B':(120,160),'C':(270,160),'D':(370,160),'E':(60,300),'F':(180,300),'G':(500,35),'H':(500,160)}
        edges=[('A','B'),('A','C'),('A','D'),('B','E'),('B','F'),('G','H')]
        labels={}
    return tree({k:(*v,k,'') for k,v in points.items()},edges,caption=caption or ('L：第一个孩子；R：下一个兄弟（根也沿 R 串接）' if binary else '根次序 A、G；孩子次序从左到右'),height=380,edge_labels=labels)


def small_forest(binary=False, practice=False):
    """Local teaching inputs, rendered with the shared tree component."""
    if practice:
        points={'P':(180,40),'Q':(100,155),'R':(280,155),'S':(100,280),'T':(480,40)}
        edges=[('P','Q'),('P','R'),('Q','S')]
    else:
        points={'A':(280,40),'B':(110,170),'C':(280,170),'D':(450,170)}
        edges=[('A','B'),('A','C'),('A','D')]
        if binary:
            points={'A':(150,40),'B':(150,140),'C':(310,220),'D':(470,300)}
            edges=[('A','B'),('B','C'),('C','D')]
    labels=dict(zip(edges,['L','R','R'])) if binary else {}
    return tree({k:(*v,k,'') for k,v in points.items()}, edges,
                caption='L：第一个孩子；R：下一个兄弟' if binary else
                        ('根次序 P、T；P 的孩子依次 Q、R；Q 的孩子 S' if practice else '原关系：A 的孩子依次 B、C、D'),
                height=360, edge_labels=labels)


def traversal_example(numbered=False):
    # Both drawings describe A with ordered children B, C.
    points={'a':(145,40,'A','③' if numbered else ''),
            'b':(55,180,'B','①' if numbered else ''),
            'c':(235,180,'C','②' if numbered else ''),
            'x':(405,40,'A','③' if numbered else ''),
            'y':(355,150,'B','①' if numbered else ''),
            'z':(535,260,'C','②' if numbered else '')}
    if numbered:
        coords={'a':(110,25),'b':(40,120),'c':(180,120),'x':(300,25),'y':(260,95),'z':(400,165)}
        points={k:(*coords[k],v[2]+v[3],'') for k,v in points.items()}
    return tree(points,[('a','b'),('a','c'),('x','y'),('y','z')],
                caption=('①②③：左图后根序、右图二叉中序' if numbered else '左：原树；右：二叉表示（L 孩子、R 兄弟）'),
                height=220 if numbered else 340,width=440 if numbered else 600,edge_labels={('x','y'):'L',('y','z'):'R'})


def practice_binary():
    return tree({'P':(150,25,'P',''),'Q':(80,100,'Q',''),
                 'T':(340,100,'T',''),'S':(40,175,'S',''),'R':(220,175,'R','')},
                [('P','Q'),('P','T'),('Q','S'),('Q','R')],
                caption='转换核对：L 孩子，R 兄弟／根',width=400,height=220,
                edge_labels={('P','Q'):'L',('P','T'):'R',('Q','S'):'L',('Q','R'):'R'})


MERGES=merge_states([8,4,2,2])
NODES=MERGES[-1]['nodes']
ROOT=MERGES[-1]['roots'][0]
PRACTICE_MERGES=merge_states([6,3,2,1])
EQUAL_MERGES=merge_states([4,4,4,4])
INDEPENDENT_MERGES=merge_states([5,2,1,1])
ALTERNATIVE_NODES={k:dict(v) for k,v in MERGES[0]['nodes'].items()}
ALTERNATIVE_NODES.update({4:dict(weight=12,left=0,right=1,symbol=''),
                          5:dict(weight=4,left=2,right=3,symbol=''),
                          6:dict(weight=16,left=4,right=5,symbol='')})


def huff_diagram(nodes=NODES, roots=None, selected=(), edge=None, symbols='ABCD', weights=True, caption=None, compact=False):
    roots=[ROOT] if roots is None else roots
    points={}; edges=[]; labels={}; cursor=0
    def place(k,depth):
        nonlocal cursor
        n=nodes[k]
        if n['left'] is None:
            x=(40+cursor*100) if compact else (70+cursor*140); cursor+=1
        else:
            left=place(n['left'],depth+1); right=place(n['right'],depth+1); x=(left+right)/2
            for child,bit in [(n['left'],'0'),(n['right'],'1')]:
                edges.append((k,child)); labels[(k,child)]=bit
        label=symbols[k] if n['symbol'] else (str(n['weight']) if weights else '·')
        points[k]=(x,(25+depth*55) if compact else (35+depth*95),label,str(n['weight']) if n['symbol'] and weights else '')
        return x
    for k in roots: place(k,0)
    return tree(points,edges,caption=caption or ('叶子下方为权值；内部结点为子树权值和；边标 0 / 1' if weights else '原方案：根到叶子的边标组成码字；橙色标出 A、D'),height=250 if compact else 380,width=400 if compact else 600,
                focus=selected,marked_edges=[edge] if edge else [],edge_labels=labels)


def merge_player():
    panels=[]
    for state in MERGES:
        def members(k):
            n=state['nodes'][k]
            return n['symbol'] or members(n['left'])+members(n['right'])
        roots='、'.join(members(k)+str(state['nodes'][k]['weight']) for k in state['roots'])
        body='<p class="trace-action">'+state['action']+'</p><p>待选根：'+roots+'</p><p>累计合并代价：'+str(state['cost'])+'</p><p class="small">规则：每轮选当前最小两根，移除后加入新根；橙色为本步选择／生成。</p>'
        panels.append(beside(huff_diagram(state['nodes'],state['roots'],state['selected']),body))
    return player(panels,'哈夫曼逐轮合并').replace('class="tree-player"', 'class="tree-player tree-spacious"')



def selection_scan_player(*, key_states=False):
    panels=[]
    states=selection_scan_states([8,4,2,2])
    if key_states:
        # End of each scan, then the merge; retain every microstep below.
        states=[states[i] for i in (4,9,10)]
    for state in states:
        rows=[]
        for i, record in enumerate(state['records']):
            classes=[]
            if i == state['current']: classes.append('scan-current')
            if i == state['best']: classes.append('scan-best')
            if record['parent'] is not None: classes.append('scan-inactive')
            label=record['symbol']+('（排除）' if i == state['exclude'] else '')
            cells=[str(i),label,str(record['weight']),str(record['parent'] if record['parent'] is not None else -1)]
            rows.append('<tr class="'+' '.join(classes)+'">'+''.join('<td>'+v+'</td>' for v in cells)+'</tr>')
        phase='第 '+str(state['scan'])+' 遍' if state['scan'] else '合并完成'
        best=state['records'][state['best']]['symbol'] if state['best'] is not None else '无'
        grid='<table class="record-scan"><thead><tr><th>下标</th><th>子树</th><th>weight</th><th>parent</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
        if key_states:
            action={1:'第一遍完整扫描后选 C2；等权先取较早编号。',
                    2:'第二遍仍查全部记录，检查并排除 C 后选 D2。',
                    0:'合并为 CD4；C、D 保留记录，parent 改为 4。'}[state['scan']]
            status=phase+'｜当前最小：'+best
        else:
            action=state['action'] if state['scan'] else '旧记录保留，下轮仍查全部 5 条。'
            status=phase+'｜本轮已查看 '+str(state['inspections'])+' 条'
            if state['scan']: status+='｜当前最小：'+best
        panels.append('<p class="small">'+status+'</p>'+grid+'<p>'+action+'</p>')
    return player(panels,'首轮选择：三个关键状态' if key_states else '首轮选择：两遍完整扫描')


def decode_player():
    bits='010110111'; panels=[]
    for state in decode_states(NODES,ROOT,bits):
        i=state['read']
        body='<p>已读 <code>'+bits[:i]+'</code> ｜ 待读 <code>'+bits[i:]+'</code></p><p class="trace-action">'+state['action']+'</p><p>已输出：<strong>'+(state['output'] or '空')+'</strong></p><p class="small">橙色为当前结点；到叶子才输出，然后回根。</p>'
        panels.append(beside(huff_diagram(selected=[state['current']],edge=state['edge']),body))
    return player(panels,'按位译码')


SLIDES = [
['树与森林的表示转换、哈夫曼编码', '<p class="lead">一种设计改变表示而保留关系，<br>另一种设计改变结构以降低代价。</p><p>数据结构与算法 · D010</p><p class="small">教材接口：5.6–5.7；回收 5.2–5.3 的编码案例</p>', '课程名'],
['给定的树之外，还能设计什么？', '<p>D009：给定一棵树，怎样安排访问顺序？</p>'+table(['今天的两个问题','要解决的困难'],[['一个结点有很多孩子','怎样只用两个链接域保存关系？'],['符号出现次数不同','能否选择树形，减少编码位数？']])+'<p>这两个任务，都需要改变原来的父子关系吗？</p>'+note('先保留学生的判断，第 25 页再回到保持量与改变量。前半讲换表示，后半讲在前缀条件下设计码树。'), '回收留问'],
['多棵互不相交的树，怎样构成森林？', beside(forest(),'<p>先找两棵目录树的根：A、G。<br>把它们合为森林，谁是谁的父结点？</p>'+definition(r'森林是 \(m\)（\(m\geq0\)）棵互不相交的树的集合。')+'<p class="small">本例约定根次序 A、G，孩子从左到右。若原森林无序，先选择次序；这不改变父子归属。</p>')+note('A、G 都是根，不增加共同根，也不增加二者间的父子关系。B 为模型，C 为结果，D 为报告；E、F 为 B 下的网格与参数，H 为 G 下的数据。'), '对象与关系'],
['一个结点有多个孩子，可以怎样保存这些关系？', learning_task(task_beside((forest()+note('用当前图定位操作对象：C 的父为 A；A 的孩子依次 B、C、D。比较记录方式怎样支持操作，第三种的机制留到下一页。')),'<p>① 找结点 C 的父结点。<br>② 按顺序列出 A 的所有孩子。</p>'+table(['表示','记录什么','直接支持'],[['双亲','父结点编号','找父结点'],['孩子','直接孩子列表','列出孩子'],['孩子兄弟','首个孩子、下一兄弟','进入并沿孩子序列继续']])+'<p>只保留两个链接域，怎样仍能列出所有孩子？</p>')), '表示选择'],
['两个链接怎样容纳任意多个孩子？', activity(5,small_forest()+'<p>一个链接进入孩子序列，另一个沿序列继续。</p>',small_forest(True)+'<p>从 A 出发，怎样找到 D？</p>','<p>链接路径：______</p>',[('展开链接路径核对','<p>A 经 L 到 B，再经 R 到 C、D；C、D 的原父仍是 A。孩子数不限定为两个。</p>')],'先让学生对照两图说明每一步链接，区分存储路径与原父子关系。'), '链接机制'],
['换了链接以后，原来的父子关系还在吗？', activity(6,forest(),forest(True,caption='L 首个孩子；R 后续兄弟／根')+'<p class="small">L ↔ first_child；R ↔ next_sibling。</p>','<p>C 的原父是谁？G 是 A 的孩子吗？</p>',[('展开父子关系核对','<p>C 的原父是 A，不是 B；G 是独立的根。<br>A 经 R 到 G 只保存根次序，没有增加父子关系。</p>')],'保持根与孩子次序。让学生在两图中指认同一关系，区分原森林、约定次序与存储链接。'), '转换规则'],
['只看两个链接，能还原原来的森林吗？', activity(7,forest(True),'<p>L：首个孩子；R：后续兄弟／根。</p><p>先还原根序列，再列出 A、B、G 的孩子。</p>',table(['要还原的关系','你的结果'],[['各树的根','______'],['A 的孩子','______'],['B、G 的孩子','______']]),[('需要时，展开恢复提示','<p>从 A 沿 R 找后续根；从 A 沿 L 进入孩子链，再沿孩子的 R 链继续。对各孩子递归重复。</p>'),('作答后，展开关系核对',table(['对象','依次还原'],[['根','A、G'],['A 的孩子','B、C、D'],['B 的孩子','E、F'],['G 的孩子','H']])+'<p>恢复原结点、父子归属与约定次序，才算没有丢失信息。</p>')],'先做一部分再展开核对。表示须无环、无重复归属、无不可达结点；结构验证细节不作为现场附加任务。'), '反向检查'],
['同一组结点，按不同规则会得到什么顺序？', learning_task(task_beside(('<p class="small">回忆 D009：N 访问根，L/R 遍历左/右子树。<br>先序 NLR｜中序 LNR｜后序 LRN</p>'+traversal_example()+note('先让学生回忆规则并保留原始作答，再按需展开提示或核对；折叠区互斥。L/R 在遍历规则中指二叉左右子树，在表示中分别承载首个孩子、下一兄弟。一般森林按各树后根序串接，教材也常称森林中序；二叉先序对应森林先根序。A–H 核对先序 ABEFCDGH、后根序 EFBCDAHG。')),'<p>原树后根：先各孩子子树，后根。</p><div class="tree-answer tree-swap"><div class="tree-preview">'+table(['按哪条规则','写出序列'],[['原树后根序','______'],['二叉中序 LNR','______'],['二叉后序 LRN','______']])+'</div>'+answer_fold(8,'需要时，展开提示','<p>右图 B 的右链接通向兄弟 C。<br>按 LNR 或 LRN 处理以 B 为根的二叉子树时，A 应在什么时候被访问？</p>')+answer_fold(8,'作答后，展开序列核对',table(['规则','访问次序'],[['原树后根','B① C② A③'],['二叉中序 LNR','B① C② A③'],['二叉后序 LRN','C① B② A③']])+'<p>原树的后根序，对应这里的二叉中序；不能照搬成二叉后序。</p>')+answer_fold(8,'展开图上编号与一般理由',traversal_example(True)+'<p>二叉中序：孩子链 → 当前根 → 后续树；每部分递归重复，因此与森林后根序一致。</p>')+'</div>')), '推演遍历'],
['换一个森林，你能独立完成表示转换吗？', learning_task(task_beside(('<p class="small">左链接：第一个孩子；右链接：下一兄弟／根。<br>二叉中序 LNR：左子树 → 根 → 右子树。</p>'+small_forest(practice=True)+note('保留约 3 分钟独立作答，记录是否使用提示。核对时要求解释一条右链接的原关系，以及原结点、父子归属和约定次序为何不变。指针形式：<code>struct CSNode { char id; struct CSNode *first_child, *next_sibling; };</code>。课后预测 A–H 空右链接再运行：D、F、G、H，共 4 个，含根链末尾 G。程序对照与练习答案分开展示。')),'<p>从原森林建立两个链接，判断 R 的原父，再用 LNR 核对。</p><div class="tree-answer tree-swap"><div class="tree-preview"><p>非空链接：______<br>结点 R 的原父结点：______<br>森林后根序／二叉中序：______</p></div>'+answer_fold(9,'需要时，展开提示','<p>先按 P、T 串接根；再从 P 的第一个孩子进入 Q、R 的兄弟链。<br>右链接相连的两个结点，是原来的父子吗？</p>')+answer_fold(9,'作答后，展开转换与遍历核对',practice_binary()+'<p>P.L=Q，P.R=T；Q.L=S，Q.R=R；其余空。</p><p>R 的原父仍为 P；后根序／中序：S Q R P T。</p>')+answer_fold(9,'展开程序表示对照',table(['指针域','数组字段'],[['first_child','first[]'],['next_sibling','next[]'],['NULL（空）','-1（空）']])+'<p>A–H 程序主例：A 是下标 0；first[0]=1 指向 B，next[1]=2 指向 C。下标是记录编号，不是层序位置。</p><p>运行 <a href="code/forest_demo.c">森林程序</a>，核对原关系与遍历。</p>')+'</div>')), '独立转换'],
['出现次数不同，编码长度还必须相同吗？', '<p>一批 16 条状态消息，只有四种类型：</p>'+table(['符号','A','B','C','D'],[['出现次数','8','4','2','2'],['等长编码','00','01','10','11']])+r'<p>等长内容为 \(16\times2=32\) bit。A 少 1 bit 可省 8 bit；D 多 1 bit 只增 2 bit。</p><p>能否总体更省？若长短不同，接收方怎样确定边界？</p><p class="small">教学构造数据；暂不计码表与文件头。</p>', '代价问题'],
['码字变短以后，怎样知道在哪里断开？', activity(11,code('A=0，B=01，C=1\n收到完整位串 01'),'<p>码字各不相同，能确定发送的符号串吗？</p>', '<p>可能的切分与符号：______</p>',[('需要时，展开提示','<p>分别尝试把整段 01 看作一个码字，以及从第一位 0 处分开。</p>'),('展开歧义与前缀条件核对','<p>01 可读成 B，也可切成 0｜1，读成 AC。<br>0 是 01 的前缀，码字互异仍不足以确定边界。</p>'+definition('前缀编码：任何一个字符的编码都不是另一个字符编码的前缀。')+'<p>前缀编码可以从左向右即时确定边界。</p>')],'先发现歧义，再给出定义。前缀条件是唯一译码的充分条件，并非必要条件；本页不展开其他唯一可译码方案。'), '编码条件'],
['为什么把符号放在叶子上，就能得到前缀编码？', beside(huff_diagram(),'<p>根到叶子的边标组成码字：<br>A：<code>0</code>，B：<code>10</code><br>C：<code>110</code>，D：<code>111</code></p><p>叶子不是其他叶子的祖先，因此码字互不为前缀。</p><p>这是一种合法方案，尚未证明最优。怎样比较它与其他方案？</p>')+note('码长等于根到叶子的路径边数，内部结点不放符号。沿用这棵树贯穿后续 WPL、构造和译码。'), '编码树'],
['一套编码到底需要多少 bit？', activity(13,huff_diagram(),'<p>次数 A8、B4、C2、D2；码长数边，根深度为 0。<br>先读图核对码长，再填各项位数与总位数。</p>',table(['符号','次数','码长','位数'],[['A','8','1','____'],['B','4','2','____'],['C','2','3','____'],['D','2','3','____']])+'<p>这批消息共需 ______ bit。</p>',[('① 算完后，核对具体位数',table(['符号','次数 × 码长','位数'],[['A','8 × 1','8'],['B','4 × 2','8'],['C','2 × 3','6'],['D','2 × 3','6']])+r'<p>总位数：\(8\times1+4\times2+2\times3+2\times3=28\) bit。</p>'),('② 从总位数建立 WPL 定义',r'<p>抽象总位数：\(\operatorname{WPL}=\sum_{i=1}^{n}w_i\ell_i\)。</p>'+definition('带权路径长度（Weighted Path Length，WPL）：各叶子权值与根到该叶子路径长度的乘积之和。')+r'<p class="small">\(w_i\)：第 i 个叶子的权值；\(\ell_i\)：根到它的边数；\(n\)：叶子数，本例为 4。</p><p>权值为出现次数，WPL 就是这批消息的编码内容总位数。<br>平均码长 \(\bar\ell=\frac{\operatorname{WPL}}{\sum_iw_i}=\frac{28}{16}=1.75\) bit/符号。</p>')],'先读图、算四个乘积并合计 28，再依次打开①与②，由具体总位数形成数学定义，最后区分总量与平均量。定义与变量解释在学生展开区，不要求回忆前页码表。内部权值不直接计入求和，树高不能代替各叶子的路径长度。'), '建立代价'],
['同一批符号，码长分配怎样改变总代价？', learning_task(task_beside(('<p>次数固定：A8、B4、C2、D2。</p>'+huff_diagram(selected=[0,3],weights=False)+note(r'码树省略权值，只说明路径与码字，不把交换后的内部权值误用为原值。若画带权交换树，内部权值须更新为 16、14、10。变化量 \((8-2)(3-1)=12\)。'+'第 14 页后断开，下一段进入构造。')),table(['方案／码字','A','B','C','D'],[['2-bit 等长','00','01','10','11'],['左图原方案','0','10','110','111'],['交换 A、D','111','10','110','0']])+'<div class="tree-answer tree-swap"><div class="tree-preview"><p>三种方案总位数：____、____、____。<br>交换了什么？树的分支形状变了吗？<br>怎样系统地构造 WPL 最小的编码树？</p></div>'+answer_fold(14,'展开总位数与计算核对',r'<p>等长：\(16\times2=32\)。<br>原方案：\(8\times1+4\times2+2\times3+2\times3=28\)。<br>交换后：\(8\times3+4\times2+2\times3+2\times1=40\)。</p><p>只换符号与码字的对应，树形不变，WPL 却改变；更省还不等于最优。</p>')+answer_fold(14,'从优化目标认识哈夫曼树',definition('给定叶子权值，使带权路径长度 WPL 最小的二叉树称为哈夫曼树（Huffman Tree）。')+'<p class="small">正次数作权值，符号只放叶子，限二元前缀编码。</p>')+'</div>')), '比较与优化'],
['怎样逐步构造一棵最优编码树？', merge_player()+note(r'待选项是尚未并入更大树的根，每个代表完整子树。每轮先问选谁，再前进：移除两根，加入权值和的新根；新树整体参与下轮。正权、\(n\geq2\) 时共 \(n-1\) 轮。主例增量 4、8、16，累计 4、12、28。并列按编号、先选放左只为复现，可有不同最优码表；安全选择的理由见第 18 页。'), '哈夫曼算法'],
['换一组权值，合成项放回后选谁？', learning_task(task_beside(('<p>新练习：权值换为 A6、B3、C2、D1。</p><p class="small">每轮选当前两个最小根，移除它们，加入权值和的新根。</p>'+huff_diagram(PRACTICE_MERGES[2]['nodes'],PRACTICE_MERGES[2]['roots'])+note('当前页独立给出新权值、选择规则与第一轮状态，不要求翻回主例。先确认学生没有重复选择已合并的叶子，再核对后两轮；合成项作为整棵树参与选择，不要求每轮重新排序全部对象。保持本页 4 分钟，第 24 页独立构造仍保留 9 分钟。')),'<p>第一轮后待选：A6、B3、CD3。</p><div class="tree-answer tree-swap"><div class="tree-preview">'+table(['轮次','选哪两根','更新后待选'],[['2','______','______'],['3','______','______']])+'<p>补全过程，并计算 WPL。</p></div>'+answer_fold(16,'需要时，展开提示','<p>只比较当前根 6、3、3；CD3 代表一棵完整子树，C、D 不再单独参与选择。</p>')+answer_fold(16,'作答后，展开状态与结果核对',table(['轮次','合并','更新后待选'],[['1','D1＋C2 → CD3','A6、B3、CD3'],['2','B3＋CD3 → BCD6','A6、BCD6'],['3','A6＋BCD6 → 根12','根12']])+r'<p>\(\operatorname{WPL}=3+6+12=21\)。并列时左右可不同。</p>')+answer_fold(16,'展开最终码树核对','<div class="tree-answer">'+huff_diagram(PRACTICE_MERGES[-1]['nodes'],PRACTICE_MERGES[-1]['roots'],caption='本练习的一棵最优码树',compact=True)+'</div>'+r'<p>根权值为 12，\(\operatorname{WPL}=21\)。</p>')+'</div>')), '示例与补全'],
['为什么合并权值之和恰好等于 WPL？', activity(17,huff_diagram(),'<p>每次合并，两棵子树内的每片叶子都加深一层，增量等于两根权值之和。</p>',table(['主例合并','受影响的叶子','增量'],[['C、D','C2、D2','4'],['B、CD','B4、C2、D2','8'],['A、BCD','A8、B4、C2、D2','16']])+r'<p>\(\operatorname{WPL}=4+8+16=28\)。</p>',[('展开非最小合并的对照树','<div class="tree-answer">'+huff_diagram(ALTERNATIVE_NODES,[6],compact=True,caption='先合并 A8、B4，再合并 C2、D2')+'</div>'+r'<p>增量 \(12+4+16=32\)。两种合并都满足恒等式，代价却不同；恒等式本身不能证明最优。</p>')],'每片叶子权值累计次数恰等于深度。对照树是刻意选用的非最小合并，不标为哈夫曼树。下一页才解释安全选择。'), '代价核对'],
['为什么先合并最小两项是安全的？', activity(18,'<p>正权值、至少两个符号；a、b 是当前最小两权。</p>'+contraction_diagram(),table(['理由','需要建立的关系'],[['交换','可以找到最优树，让最小两权成为最深兄弟'],['收缩','合成权值和，得到较小的同类最优问题']]),r'<p>展开两叶子只增加固定代价 \(a+b\)，可以递归求解。</p>',[('展开交换前后的代价核对',table(['位置','浅处 d','深处 D'],[['交换前','小权 x','大权 y'],['交换后','大权 y','小权 x']])+r'<p>当 \(x\leq y,\ d\leq D\)，变化量 \(\Delta=(x-y)(D-d)\leq0\)。把小权移深、大权移浅不会更差。</p>'),('展开收缩为什么保留最优性','<p>正权下，只有一个孩子的内部结点可以删除而降代价；因此只需考虑每个内部结点有两个孩子的树。</p><p>选最深兄弟，逐次交换把最小两权放到那里，仍能保持最优。</p><p>收缩后若还能改进，展开只多付固定的两权之和，便能改进原树，矛盾。</p>')],'课堂先理解存在安全选择及问题规模缩小，不要求当场独立完成交换证明。两孩子不意味着每层填满；本页没有用样例代替普遍理由。'), '成立理由'],
['合并出来的树，怎样存到 C 数组中？', activity(19,first_merge_record(),r'<p>\(n\) 个符号：0 到 \(n-1\) 是叶子，-1 表示空链接。<br>下标是记录编号，不是层序位置。</p>',code('typedef struct {\n    unsigned long long weight;\n    int parent, left, right;\n} HNode;')+'<p>weight 存子树权值和；parent 用于回溯码字。</p>',[('展开首轮合并后的数组记录',table(['下标','weight','parent','left / right'],[['2（C）','2','4','-1 / -1'],['3（D）','2','4','-1 / -1'],['4（新根）','4','-1','2 / 3']])+'<p>新建记录 4：left=2、right=3；原两叶子的 parent 均改为 4。</p>')],r'先把图上的两条链接对应到数组字段。每个内部结点恰有两个孩子时，\(n\) 个叶子、\(n-1\) 个内部结点，共 \(2n-1\) 条记录；不是完全二叉树的位置公式。'), '计算表示'],
['找出两个最小根，要查看多少条记录？', learning_task(task_beside('<div class="tree-swap"><div class="tree-preview">'+selection_scan_player(key_states=True)+note(r'本页 2 分钟只走三个关键状态与右侧三步归纳：约 45 秒看两次选根及合并，45 秒解释单轮与轮数，30 秒合成平方阶并区分 WPL。完整 11 步、8/10/12 与精确和式均为补充，不要求现场遍历。按编号升序扫描，仅在严格更小时更新；合并后旧记录仍在。沿 parent 生成码字总计 \(O(\sum_i\ell_i)\)，最坏 \(O(n^2)\)；译码 \(O(L)\)。适当最小优先队列构树可达 \(O(n\log n)\)，机制留到 D020。')+'</div>'+answer_fold(20,'补充：完整 11 步逐条扫描',selection_scan_player())+'</div>','<p>怎样选两根？每轮完整扫描已建记录两遍；有双亲或被排除的记录也先检查再跳过。</p><p class="small">橙底：当前记录；蓝框：当前最小权值；灰底：已合并。parent=-1 表示无双亲。</p><div class="tree-swap"><div class="tree-preview">'+table(['工作量','从操作得到的理由'],[[r'单轮 \(O(n)\)',r'每轮两遍，记录数从 n 增至 \(2n-2\)'],[r'共 \(n-1\) 轮','每次合并使根数少 1，从 n 棵到 1 棵'],[r'构树 \(O(n^2)\)',r'上述线性扫描重复 \(n-1\) 轮']])+'<p class="small">这里数当前实现的构树工作；WPL 数编码内容位数。</p></div>'+answer_fold(20,'补充：精确查看次数与一般和式',table(['轮次','根数','已建记录','两遍查看'],[['1','4','4','8'],['2','3','5','10'],['3','2','6','12']])+r'<p>合计 \(8+10+12=30\) 次。</p><p>\(2\sum_{m=n}^{2n-2}m=(n-1)(3n-2)\)。</p><p>计查看记录，不等于权值比较次数；根变少，旧记录仍保留。</p>')+'</div>')), '算法代价'],
['收到 010110111，怎样还原消息？', '<div class="tree-swap"><div class="tree-preview">'+decode_player()+'</div><div class="learning-task"><div class="columns support-options"><div>'+note('先在读完第一位、第三位时暂停，让学生预测叶子输出与回根。展开核对时替换播放器，同时提供同一码树与完整输入；关闭后恢复播放器当前状态。前缀性不自动检测所有传输错误，也不等于纠错。')+'</div><div>'+answer_fold(21,'展开完整切分与输出核对','<div class="tree-answer">'+huff_diagram(compact=True,caption='同一码树：A0、B10、C110、D111')+'</div><p>输入 <code>010110111</code>：切为 <code>0｜10｜110｜111</code>，输出 ABCD。</p><p>到叶子才输出，然后回根；四次输出后均回根。</p>')+answer_fold(21,'输入 11：展开末尾状态核对','<div class="tree-answer">'+huff_diagram(compact=True,selected=[4],caption='从根沿 1、1，停在内部结点 4（橙色）')+'</div><p>输入 <code>11</code> 已结束，尚未到叶子，不输出符号；报告末尾码字不完整。</p>')+'</div></div></div></div>', '译码与边界'],
['符号出现得越不均匀，变长编码有什么机会？', activity(22,table(['出现次数','哈夫曼 WPL','2-bit 等长'],[['8、4、2、2','28','32'],['4、4、4、4','？','32']]),'<p>等频时，需要给谁特别短的码字？</p>','<p>先解释，再运行 <a href="code/huffman_demo.c">哈夫曼程序</a>核对；不要只重算主例。</p>',[('展开等频码树与成本核对','<div class="tree-answer">'+huff_diagram(EQUAL_MERGES[-1]['nodes'],EQUAL_MERGES[-1]['roots'],compact=True,caption='等频方案：四个码长都为 2')+'</div>'+r'<p>\(\operatorname{WPL}=8+8+16=32\)，平均码长为 2，与等长内容位数相同。频率相同，无需偏向某个符号。</p>')],'主例平均码长 1.75。频率差异给短码分配带来机会，并非所有输入都有收益。允许不同最优码表，核对前缀性、WPL 和 ABCD 往返。'), '频率与收益'],
['少了 4 bit，就一定让文件更小吗？', '<p>本例内容从 32 bit 降到 28 bit，节省 \\(12.5\\%\\)。</p><ul><li>解码端还需要知道码表或树。</li><li>28 bit 按整字节保存，填充后就是 32 bit；此外还有长度和文件头。</li><li>短消息的额外开销可能超过节省量。</li></ul><p class="small">哈夫曼在给定权值的二元逐符号前缀编码中最优，不表示对所有压缩方法或完整文件都最优。</p>' + note('码表需与当前编码一致。单符号字母表的结构深度是 0，本演示约定码字为 0，于是线上码长为 1，另行处理。零频符号本演示拒绝，可在建模时移出字母表。'), '适用边界'],
['换一组频率，你能独立优化结构吗？', activity(24,'<p>新输入：P5、Q2、R1、S1。</p><p class="small">每轮选当前最小两根，移除后加入新根。<br>码长数边，根深度为 0。</p>'+r'<p>\(\operatorname{WPL}=\sum_i w_i\ell_i\)<br>\(\bar\ell=\operatorname{WPL}/\sum_i w_i\)</p>','<p>记录候选集合，画树、写码字，计算 WPL 与平均码长，并与 2-bit 等长方案比较。</p>','<p>合并与更新：______<br>码树与码表：______<br>成本比较与优化目标：______</p>',[('需要时，展开过程提示','<p>每个候选根代表完整子树。标出已经并入新树的根，不能再次把它们单独选出；总权值不因合并改变。</p>'),('作答后，展开合并与成本核对',table(['轮次','合并','更新后待选'],[['1','R1＋S1 → RS2','P5、Q2、RS2'],['2','Q2＋RS2 → QRS4','P5、QRS4'],['3','QRS4＋P5 → 根9','根9']])+r'<p>\(\operatorname{WPL}=2+4+9=15\)，平均 \(15/9=5/3\)。等长为 \(9\times2=18\) bit，少 3 bit；优化的是给定权值下的前缀编码内容位数。</p>'),('展开一种码树与码表核对','<div class="tree-answer">'+huff_diagram(INDEPENDENT_MERGES[-1]['nodes'],INDEPENDENT_MERGES[-1]['roots'],symbols='PQRS',compact=True,caption='一种最优码表：P1、Q00、R010、S011')+'</div>')],'保留 7 分钟独立作答、2 分钟核对。提示使用情况另作区分，不能按码字是否逐字一致判错。本题树形与主例相近，不据此宣称掌握任意频率结构。'), '独立构造'],
['今天我们学会了哪两种结构设计？', table(['比较','森林表示转换','哈夫曼编码构造'],[['面对的问题','多个孩子怎样用两个链接表达','频率不同，怎样减少内容位数'],['给定什么','森林、约定的根与孩子次序','符号、权值、前缀编码条件'],['允许改变','存储链接及含义','树形、符号位置与码长'],['必须保持','原结点、父子关系与次序','符号及权值、编码合法性'],['怎样判断','能否还原原森林并核对关系','前缀性、WPL 及最优性依据']])+'<p>二者都使用树，究竟分别在设计什么？</p>'+note('译码是使用既有码树恢复信息的操作，不是第三种结构设计。编码译码往返可检查实现一致性，不能单独证明 WPL 最优。回到第 2 页的判断。'), '结构化收口'],
['课后：教材导航与本周作业', '<p><strong>教材导航</strong>：精读 5.6–5.7，回看 5.2–5.3 的编码案例。</p><p><strong>A. 书本习题（必须提交）</strong>：第 5 章选择题 <strong>(1)(9)(11)(14)</strong>、应用题 <strong>(2)③、(3)</strong>。选择题附理由；应用题给出转换、构造与计算过程。</p><p><strong>B. 扩展作业（必须提交）</strong>：对新权值 A7、B3、C2、D1，先提交合并过程、码表、WPL、平均码长与等长比较；运行 <code>code/huffman_demo.c</code> 核对 homework 输出及 ABCD 往返译码。码字不同须解释是否仍最优。</p><p class="small">按<a href="../../assignments/homework-guide.md">作业规范</a>提交 A、B，附 3–5 行过程记录。<br>自学练习（不提交）：选择题 (6)、应用题 (4)；应 (2)③ 可先借助 D009 的恢复方法画出题设二叉树。</p>', '课后衔接'],
['一个对象可以同时连接多个对象，树还够用吗？', '<p>树与森林中，每个非根结点只有一个父结点。<br>编码树则用路径表达符号，按代价优化树形。</p><p class="lead">道路之间可以成环，一个地点也可能连接多个方向，该怎样表示？</p><p>D011：图与一般关系结构。</p>', '留下问题'],
]
