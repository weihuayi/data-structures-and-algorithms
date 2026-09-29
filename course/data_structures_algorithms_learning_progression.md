# 《数据结构与算法》课程 Learning Progression / 认知主线图

- **版本**：v0.2
- **状态**：候选认知基线
- **形成方式**：基于当前课程整体设计、D001–D007 教学资产及其认知覆盖矩阵压力测试反向提炼
- **适用范围**：课程总体设计、Deck 设计与修订、作业与评价设计、课堂观测及后续课程演化
- **当前证据边界**：D001–D004 已存在明确课堂运行记录；D005–D007 当前主要依据已形成的 Deck、代码、交互与作业设计。除已有课堂记录外，不据此推断学生已经形成相应理解。

## 一、Learning Progression 的对象

本课程的 Learning Progression 不是教材章节、知识点或 Deck 的顺序表。

例如：

```text
线性表
→ 栈与队列
→ 串
→ 树
→ 图
→ 查找
→ 排序
```

主要描述的是**教学内容的先后组织**。

Learning Progression 更关心：

> 学习者面对计算问题时，对计算对象、表示、操作、结构、算法、正确性和计算代价的理解怎样逐步变化，并最终形成能够分析、选择、设计、验证和迁移的能力。

因此，本课程建设的主要对象不是“越来越完整的知识目录”，而是：

$$
\boxed{
\text{学习者认知结构与问题解决能力的持续变化}
}
$$

## 二、当前课程认知结构不宜理解为一条单向流水线

v0.1 曾暂时表示为：

$$
\text{问题}
\rightarrow
\text{对象}
\rightarrow
\text{操作}
\rightarrow
\text{表示}
\rightarrow
\text{不变量}
\rightarrow
\text{算法}
\rightarrow
\text{正确性}
\rightarrow
\text{代价}
\rightarrow
\text{验证}
\rightarrow
\text{判断}
\rightarrow
\text{迁移}.
$$

D001–D007 压力测试表明，这个表达过于线性，也使不同证据强度的认知要素看起来具有同等成熟度。

当前更符合课程实际的结构是：

$$
\text{Problem}
\rightarrow
\text{Object}
\rightarrow
\left\{
\begin{array}{c}
\text{Operations}\\
\text{Representation}
\end{array}
\right.
$$

随后围绕计算对象反复发生：

$$
\text{Representation / Constraint}
\leftrightarrow
\text{Invariant / Information}
\leftrightarrow
\text{Algorithm},
$$

并持续接受：

$$
\text{Correctness}
+
\text{Cost}
+
\text{Verification}
\rightarrow
\text{Judgment}.
$$

最后，已有判断再次进入新的问题：

$$
\text{Judgment}
\rightarrow
\text{New Problem}.
$$

因此，整个课程更接近一个不断扩张和回收的认知网络，而不是一条只向前推进的知识链。

## 三、第一层：当前已经具有较强证据的稳定认知主干

### 3.1 主干一：问题 → 对象 → 表示

当前课程最稳定的第一条认知主干是：

$$
\boxed{
\text{Problem}
\rightarrow
\text{Object}
\rightarrow
\text{Representation}
}
$$

其核心问题依次是：

1. 我们究竟要解决什么问题？
2. 问题中有哪些计算对象？
3. 哪些信息和关系必须保留？
4. 它们如何进入计算机？
5. 当前表示保留了什么，又丢掉了什么？

这条主线在 D001 中建立问题入口，在 D002 中进入数据、关系和组织，在 D003–D004 中进入具体内存表示。

学生应逐步从：

> “题目给我以后开始写程序”

转向：

> “先判断计算对象是什么，以及为了当前任务必须保留哪些信息和关系。”

### 3.2 主干二：表示 → 能力 → 代价 → 选择

第二条已经较为稳定的主干是：

$$
\boxed{
\text{Representation}
\rightarrow
\text{Capability}
\rightarrow
\text{Cost}
\rightarrow
\text{Trade-off}
}
$$

它回答：

> 为什么不同的数据结构具有不同性能，而不是只让学生记住复杂度结论？

例如顺序表示：

$$
LOC(a_i)=base+(i-1)L
$$

直接带来：

$$
\text{随机访问}=O(1),
$$

而维持连续表示又使中间插入和删除产生元素移动。

链式表示放弃由地址直接计算逻辑位置的能力，却获得局部链接修改的灵活性。

因此：

> 优势和劣势通常来自同一个设计选择。

学习目标不应停留在：

> “数组查找快，链表插入快。”

而应推进到：

> “哪个表示机制产生了这种能力和代价？当前任务真正需要哪一种能力？”

### 3.3 主干三：抽象对象与具体表示分离

这一认识在前几讲中逐步准备，在 D004 中首次明确建立：

$$
\boxed{
\text{Abstract Object}
\neq
\text{Representation}
}
$$

同一个线性表可以采用：

$$
\text{Sequential Representation}
$$

也可以采用：

$$
\text{Linked Representation}.
$$

它们所支持的抽象操作可以相近，但实现机制和计算代价不同。

这一认知跨越是后续树、图、Hash、优先队列等内容的重要基础：

> 不应该把某种具体代码结构直接等同于计算对象本身。

### 3.4 主干四：预测 → 运行 → 检查

当前最稳定的学习行为主线是：

$$
\boxed{
\text{Prediction}
\rightarrow
\text{Execution}
\rightarrow
\text{Check}
}
$$

其价值不只是代码练习。

“先预测”迫使学生显式暴露当前内部模型；

“再运行”让现实执行成为外部反馈；

“再检查”要求学生解释预测与现实之间的关系。

因此它实际上形成：

$$
\text{Internal Model}
\rightarrow
\text{Prediction}
\rightarrow
\text{Observation}
\rightarrow
\text{Revision}.
$$

后续课程应继续保留这一基本方法，同时逐步增加：

> 程序即使按预测运行，其输出是否真正回答了原来的问题？

使检查从程序内部一致性逐渐扩展到问题适用性。

## 四、第二层：已经出现但尚不能冻结为全课程主线的候选认知

### 4.1 候选主线一：不变量

D003 已经明确建立：

> 操作改变对象状态，但某些结构性质必须保持。

例如顺序表示中：

$$
LOC(a_i)=base+(i-1)L
$$

必须在插入和删除之后继续成立。

因此元素移动不是附带的实现麻烦，而是在恢复表示成立所需的结构条件。

D004 中链接修改顺序、D005 中接口限制与状态维护都与这一思想存在直接联系。

但当前还没有充分证据表明学生已经形成统一的“不变量思维”。

因此当前定位应是：

$$
\boxed{\text{高潜力候选纵向主线}}
$$

未来树、BST、AVL、Heap、并查集、最短路径等内容应继续检验：

> “在变化中必须保持什么不变？”

是否真的具有跨对象解释力。

### 4.2 候选主线二：信息利用

D002 已经出现：

$$
\text{组织}
\rightarrow
\text{新的可利用信息}
\rightarrow
\text{减少搜索}.
$$

D007 又出现：

> 已匹配的信息不应该被浪费。

因此 KMP 可以被理解为：

$$
\text{Already Known Information}
\rightarrow
\text{Less Recalculation}.
$$

这一视角很有潜力解释后续内容：

- BST 利用有序关系；
- Heap 维护部分顺序信息；
- Hash 构造映射信息；
- 排序主动创造顺序信息；
- 图算法不断积累可用于排除和选择的信息。

但在 D003–D006 中，这一主线尚未被连续显式回收。

因此目前只能表达为：

> D002 和 D007 已经形成两个强认知锚点，后续课程需继续验证其统一解释力。

### 4.3 候选主线三：正确性

D001–D007 已经反复出现“为什么成立”的局部问题：

- 为什么不会漏掉一对商品？
- 为什么移动某个索引是安全的？
- 为什么移动元素后顺序表仍然成立？
- 为什么链接修改顺序不能交换？
- 为什么循环队列的判空与判满条件不同？
- 为什么递归一定会结束？
- 为什么 KMP 中主串位置不需要退回？

所以：

$$
\boxed{
\text{Correctness Awareness}
}
$$

已经明显存在。

但学生目前面对的是不同对象上的局部正确性语言，尚未形成统一框架。

未来是否能逐步形成：

$$
\text{Precondition}
+
\text{Invariant}
+
\text{Progress}
+
\text{Termination}
\Rightarrow
\text{Correctness}
$$

仍需根据后续课程实践判断。

### 4.4 候选主线四：迁移

课程已经设计了多种迁移活动：

- 改变输入后重新预测；
- 为错误方法构造反例；
- 在顺序表与链表之间做选择；
- 从显式栈迁移到系统调用栈；
- 将环形字符串问题转化为线性字符串问题；
- 将已有算法用于新的问题情境。

这些已经构成迁移的起点。

但当前强制性作业仍主要集中在已经学习过的对象和相近问题。

因此尚不能认为：

$$
\text{Independent Transfer}
$$

已经成为稳定课程结果。

真正成熟的迁移证据需要学生面对：

> 一个课堂没有完整示范过的新问题。

## 五、第三层：D001–D007 的主要认知跨越

课程不应要求每个 Deck 机械重复完整认知链。

每个 Deck 更适合承担一个或少量主要认知跨越。

### D001：从“写程序”转向“先理解计算对象”

初始直觉：

> 给定问题以后开始编程。

期望变化：

$$
\boxed{
\text{Problem}
\rightarrow
\text{Object}
\rightarrow
\text{Information}
\rightarrow
\text{Representation}
\rightarrow
\text{Program}
}
$$

学生第一次认识到：

$$
\text{Problem}\neq\text{Program}.
$$

### D002：从“保存数据”转向“结构能够提供计算信息”

初始认识：

> 数据结构主要负责保存数据。

期望变化：

$$
\boxed{
\text{Organization}
\rightarrow
\text{Information}
\rightarrow
\text{Algorithmic Opportunity}
}
$$

排序以后，一个比较可能排除一批候选。

因此：

> 数据怎样组织，会改变算法能够利用什么信息。

### D003：从“复杂度是结论”转向“复杂度来自表示机制”

初始认识：

> 数组访问是 $O(1)$，插入是 $O(n)$。

期望变化：

$$
\boxed{
\text{Representation Mechanism}
\rightarrow
\text{Operation Mechanism}
\rightarrow
\text{Cost}
}
$$

同时首次强烈引入：

$$
\text{Representation Invariant}.
$$

### D004：从“数据结构就是某种实现”转向“抽象对象与表示分离”

这是目前课程中一个重要认知分水岭：

$$
\boxed{
\text{Abstract Object}
\neq
\text{Physical Representation}
}
$$

同一个抽象对象可以具有不同实现。

从这里开始，“选择数据结构”才真正成为有意义的问题。

### D005：从“关系决定结构”转向“操作约束也形成语义”

初始认识：

> 数据结构由数据之间的关系决定。

期望变化：

$$
\boxed{
\text{Restricted Operations}
\rightarrow
\text{Behavioral Semantics}
}
$$

例如：

$$
\text{Stack}\Rightarrow \text{LIFO},
$$

$$
\text{Queue}\Rightarrow \text{FIFO}.
$$

学生开始理解：

> 限制不是单纯损失自由，也可以主动换取语义、简单性和可维护性。

### D006：从“数据结构是被程序处理的对象”转向“数据结构也组织程序执行”

调用栈带来的核心变化是：

$$
\boxed{
\text{Data Structure}
\rightarrow
\text{Program Execution Mechanism}
}
$$

递归进一步形成：

$$
\text{Recursive Definition}
+
\text{Call Stack}
\rightarrow
\text{Recursive Execution}.
$$

学生开始把源程序与实际执行过程区分开。

### D007：从“算法是一串步骤”转向“算法主动利用已有信息”

BF 与 KMP 的核心差别可以压缩为：

$$
\boxed{
\text{Known Information}
\rightarrow
\text{Reduced Recalculation}
}
$$

因此算法开始从：

$$
\text{Algorithm}=\text{Steps}
$$

提升为：

$$
\text{Algorithm}
=
\text{Structured Use of Information}.
$$

同时出现：

$$
\text{Preprocessing}
\leftrightarrow
\text{Execution Cost}
$$

这一重要权衡。

## 六、D001–D007 的当前整体进阶

可以把目前已经形成的七次主要跨越压缩为：

```text
D001
不是马上写程序，
而是先确定计算对象与表示。
        ↓
D002
表示与组织不是被动存储，
它们能够创造可利用的信息。
        ↓
D003
表示机制决定操作机制，
操作机制产生计算代价。
        ↓
D004
抽象计算对象不是它的某一种表示。
        ↓
D005
除了表示方式，
操作限制本身也能够定义结构语义。
        ↓
D006
数据结构不仅表示外部对象，
也组织程序自己的执行。
        ↓
D007
算法不仅执行步骤，
还应主动利用已经获得的信息。
```

这比：

```text
序言
线性表
栈
队列
串
```

更能表达当前课程真正发生的认知推进。

## 七、第四层：Learning Progression 必须具有学习证据接口

Learning Progression 只有同时回答两个问题才完整：

1. 希望学生形成什么理解？
2. 我们如何知道这种理解真的形成了？

因此每一项重要认知都应该对应可观察行为。

| 认知对象 | 较弱证据 | 较强证据 |
|---|---|---|
| 计算对象 | 能复述案例中的对象 | 能从新问题中自行识别对象、信息和关系 |
| 表示 | 会画数组、链表 | 能提出两种表示并说明各自保留的信息 |
| ADT / 操作 | 会背操作名称 | 能先确定行为需求，再选择表示 |
| 不变量 | 能复述教师给出的不变量 | 能自己指出操作前后必须维持的性质 |
| 算法 | 能重复步骤 | 能解释每一步利用了什么结构或信息 |
| 正确性 | 给定样例得到正确输出 | 能解释不会漏、不重复、会终止以及边界条件 |
| 复杂度 | 会写大 $O$ | 能从表示和操作机制推导代价 |
| Trade-off | 会背优缺点 | 能根据真实操作分布说明为什么选某种方案 |
| 验证 | 能运行代码 | 能预测、运行、构造边界情况并解释差异 |
| 迁移 | 会做同型题 | 能在未讲过的新问题中重新完成对象—表示—算法判断 |

## 八、当前课程最大的证据缺口

当前已经拥有：

$$
\text{Teaching Intent}
$$

即教师希望学生形成什么理解；

也拥有大量：

$$
\text{Designed Learner Behavior}
$$

例如：

- 解释；
- 推演；
- 预测；
- 修改；
- 比较；
- 构造反例；
- 选择方案。

但是：

$$
\boxed{
\text{Designed Learner Behavior}
\neq
\text{Observed Learner Change}
}
$$

当前系统性不足的是：

$$
\text{Learner Evidence}.
$$

因此现阶段更准确的表述是：

> D001–D007 已经形成较清晰的 Teaching Progression，并开始建立 Learner Progression 的证据接口；但尚不足以证明学习者已经按照该认知路径稳定发展。

## 九、后续 Deck 的设计原则

D008–D020 不应简单继续增加知识内容，而应同时承担三类任务。

### 9.1 推进新的主要认知跨越

每个 Deck 应回答：

> 学生在这一讲之后，对计算对象的理解与之前相比究竟改变了什么？

而不仅是：

> 这一讲要覆盖哪些教材知识点？

### 9.2 回收已经建立的稳定主干

后续 Deck 应自然回收：

$$
\text{Problem}
\rightarrow
\text{Object}
\rightarrow
\text{Representation},
$$

以及：

$$
\text{Representation}
\rightarrow
\text{Capability}
\rightarrow
\text{Cost}
\rightarrow
\text{Choice}.
$$

但不要求机械重复相同页面结构。

### 9.3 检验候选纵向主线

特别需要观察：

#### 不变量

树、BST、AVL、Heap、图算法中：

> 在对象变化过程中，什么性质必须保持？

#### 信息

查找、Hash、排序、最短路径中：

> 当前结构已经告诉了算法什么？哪些计算因此可以避免？

#### 正确性

学生是否逐渐从：

> “程序跑出来了”

过渡到：

> “我能够解释算法为什么不会漏、为什么终止、为什么得到正确结果。”

## 十、课程最终希望形成的内部问题解决循环

如果整个 Learning Progression 最终有效，学生面对一个陌生问题时，应逐渐形成下面的内部工作流：

```text
问题到底是什么？
        ↓
计算对象是什么？
        ↓
必须保留哪些信息和关系？
        ↓
需要支持哪些操作？
        ↓
可以怎样表示？
        ↓
不同表示分别获得什么能力？
        ↓
必须保持什么结构性质？
        ↓
算法能够利用哪些已有信息？
        ↓
为什么算法成立？
        ↓
时间和空间代价是什么？
        ↓
还有哪些候选方案？
        ↓
为什么选择当前方案？
        ↓
怎样预测、测试、构造边界情况和反例？
        ↓
结果是否真正回答了原来的问题？
```

最终课程希望形成的不是固定答案，而是一种稳定的计算判断习惯。

## 十一、当前认知主线图

```text
                         真实问题
                            │
                            ▼
                       计算对象
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
            行为 / 操作需求         信息与关系
                 │                     │
                 └──────────┬──────────┘
                            ▼
                         计算表示
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
                能力              约束
                   │                 │
                   └───────┬─────────┘
                           ▼
                  不变量 / 可利用信息
                           │
                           ▼
                         算法
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           正确性         代价         实现
              │            │            │
              └────────────┼────────────┘
                           ▼
                   预测 / 运行 / 检查
                           │
                           ▼
                       判断与选择
                           │
                           ▼
                        新问题
```

其中当前证据强度并不相同：

```text
稳定主干：
问题 → 对象 → 表示
表示 → 能力 → 代价 → 选择
预测 → 运行 → 检查

已建立的重要认知跨越：
抽象对象 ≠ 具体表示

候选纵向主线：
不变量
信息利用
统一正确性语言
陌生问题迁移
```

## 十二、当前阶段判断

从课程建设角度，D001–D007 已经不再只是若干独立课件。

它们已经开始形成一个具有连续认知推进的课程前半段：

$$
\text{Program}
\rightarrow
\text{Representation}
\rightarrow
\text{Structure}
\rightarrow
\text{Abstraction}
\rightarrow
\text{Constraint}
\rightarrow
\text{Execution}
\rightarrow
\text{Information-Aware Algorithm}.
$$

但当前最值得继续建设的对象已经发生变化。

前一个阶段的主要问题是：

> 每一讲应该讲什么、怎样讲清楚？

下一阶段更重要的问题开始变成：

> 这些 Deck 是否共同支持学生形成稳定、可迁移的认知结构？我们用什么证据判断这种变化真的发生？

因此，课程建设正在从：

$$
\text{Deck Construction}
$$

逐步转向：

$$
\boxed{
\text{Course-level Cognitive Architecture}
+
\text{Learner Evidence System}
}
$$

这应成为后续 D008–D020 设计与已有 Deck 修订的共同认知基础。
