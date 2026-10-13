"""Small positive-weight Huffman examples with explicit merge/decode snapshots."""

def merge_states(weights):
    if len(weights) < 2 or any(not isinstance(w, int) or w <= 0 for w in weights):
        raise ValueError('At least two positive integer weights are required')
    nodes = {i: dict(weight=w, left=None, right=None, symbol=chr(65+i)) for i,w in enumerate(weights)}
    roots = list(nodes)
    states = []
    cost = 0
    def save(action, selected=()):
        states.append(dict(nodes={k:v.copy() for k,v in nodes.items()}, roots=roots.copy(),
                           selected=list(selected), cost=cost, action=action))
    save('每个符号先是一棵树；预测本轮最小的两项。')
    while len(roots)>1:
        roots.sort(key=lambda k:(nodes[k]['weight'], k))
        a,b=roots[:2]
        save('选出当前根权值最小的两棵树。', (a,b))
        k=len(nodes)
        nodes[k]=dict(weight=nodes[a]['weight']+nodes[b]['weight'],left=a,right=b,symbol='')
        cost+=nodes[k]['weight']
        roots=roots[2:]+[k]
        save('合成新根并放回待选集合；子树保持完整。' if len(roots)>1 else '只剩一棵树，构造完成。', (k,))
    return states


def decode_states(nodes, root, bits):
    """Requires a valid full binary tree produced by merge_states."""
    if any(b not in '01' for b in bits):
        raise ValueError('Bits must contain only 0 and 1')
    current=root
    output=''
    states=[dict(read=0,current=root,output='',action='从根开始；先预测第一个码字在哪里结束。',edge=None)]
    for i,bit in enumerate(bits,1):
        parent=current
        current=nodes[parent]['left' if bit=='0' else 'right']
        states.append(dict(read=i,current=current,output=output,action=f'读入第 {i} 位 {bit}，沿对应边移动。',edge=(parent,current)))
        if nodes[current]['symbol']:
            output+=nodes[current]['symbol']
            states.append(dict(read=i,current=current,output=output,action='到达叶子，输出该符号。',edge=None))
            current=root
            states.append(dict(read=i,current=current,output=output,action='回到根，准备读取下一个码字。',edge=None))
    states.append(dict(read=len(bits),current=current,output=output,
                       action='输入结束且位于根，译码完成。' if current==root else '输入结束但停在内部结点：末尾码字不完整。',edge=None))
    return states
