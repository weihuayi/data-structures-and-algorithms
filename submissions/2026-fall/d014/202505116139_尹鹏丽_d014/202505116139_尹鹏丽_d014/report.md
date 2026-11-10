# D014 程序实践
学号：202505116139
姓名：尹鹏丽
周数：第十周

## 预测
CD边权修改为0，起点A
- D：距离2，路径 A→C→D
- E：距离5，路径 A→C→D→E

## 运行命令
./spdemo --trace homework

## 程序trace输出
confirm A: distance=0
edge A->B weight=3 candidate=3 old=INF update
edge A->C weight=2 candidate=2 old=INF update
confirm C: distance=2
edge C->B weight=4 candidate=4 old=3 keep
edge C->D weight=0 candidate=2 old=INF update
confirm D: distance=2
edge D->B weight=1 candidate=3 old=3 keep
edge D->E weight=3 candidate=5 old=INF update
confirm B: distance=3
edge B->E weight=7 candidate=10 old=5 keep
confirm E: distance=5

homework: source=A order=ACDBE
A distance=0 path=A
B distance=3 path=A->C->D->B
C distance=2 path=A->C
D distance=2 path=A->C->D
E distance=5 path=A->C->D->E

## 更新依据（松弛操作）
对应输出：edge C->D weight=0 candidate=2 old=INF update
解析：顶点C已经被算法确认最短距离d(C)=2。访问邻边C→D，计算候选距离2+0=2；D之前距离为无穷大，满足松弛条件，于是把D的距离更新为2。

## 确认依据
对应输出：confirm D: distance=2
解析：在全部尚未确认的顶点当中，D的临时距离是最小的。按照Dijkstra规则，此时确认D，D的最短距离固定为2，后续不会再被修改。