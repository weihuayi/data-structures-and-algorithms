# D015 程序实践
学号：202505116139
姓名：尹鹏丽
周数：第十周

## 预测运行前预测
将主例中活动 D（2→3）的持续时间由 3 改为 2。

事件 2 的最早发生时间：
ve(2) = max(0+5, 3+1) = 5

事件 3 的最早发生时间：
ve(3) = max(3+2, 5+2) = 7

工程总工期：
T = ve(4) = ve(3)+2 = 7+2 = 9

预测关键活动为 B、D、F

关键路径为：0 → 2 → 3 → 4

## 运行命令
gcc dependency_demo.c -o cpmdemo -std=c11
./cpmdemo --trace homework

## trace运行输出
ve[0]=0
ve[1]=3
ve[2]=5
ve[3]=7
ve[4]=9

vl[4]=9
vl[3]=7
vl[2]=5
vl[1]=3
vl[0]=0

活动 slack 与是否关键：
A (0→1): slack=1，no
B (0→2): slack=0，yes
C (1→3): slack=2，no
D (2→3): slack=0，yes
E (1→2): slack=4，no
F (3→4): slack=0，yes

一条关键路径：B D F


## 结果说明
1. ve（事件最早发生时间）：顺着拓扑顺序，ve[j] = max{ve[i]+边<i,j>权值}
2. vl（事件最迟发生时间）：逆拓扑顺序，vl[i] = min{vl[j]-边<i,j>权值}
3. slack = 活动最迟开始时间 − 活动最早开始时间；slack=0为关键活动，决定总工期，不能延期。
