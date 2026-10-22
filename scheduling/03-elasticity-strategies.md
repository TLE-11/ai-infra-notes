# 03 · 资源弹性还有哪些办法

> 核心问题：除了“谁来抢谁的卡”，还能怎样提高资源使用效率？

“弹性”可以发生在不同层次：调整队列可用份额、调整工作负载大小，或者增加与减少实际机器。先明确改变的对象，再比较策略。

## 在已有资源里，决定怎样分

| 策略 | 直观例子 | 需要关注什么 |
|---|---|---|
| 固定上限、严格隔离 | A 最多 60、B 最多 40，不共享 | 简单可控，但可能一边空闲、一边排队 |
| 空闲借用与份额回收 | A 少用时 B 多用，A 需要时让回来 | 共享范围、退出成本和回收速度 |
| 按权重公平共享 | 多个队列竞争可借资源，按权重平衡占用 | 权重和公平性的具体定义 |
| 按服务等级抢占 | 紧急作业可以打断某类可延期作业 | 谁能抢谁、保护时间、饥饿风险 |
| 层级队列 | 部门内先共享，再按规则处理更大范围的竞争 | 父子份额、上限与回收边界 |

这里关注 Kueue 基于抢占的 Fair Sharing：它会考虑队列权重和借用资源份额，不等于“每个队列最后拿到相同卡数”，更不等于每个任务都有相同吞吐。[Kueue 抢占算法 v0.20](https://kueue.sigs.k8s.io/v0.20/docs/concepts/preemption/#preemption-algorithms)

Kueue 另有按历史用量影响准入顺序的 Admission Fair Sharing。看到“公平共享”时，先确认说的是哪种机制。[Kueue Fair Sharing 概览](https://kueue.sigs.k8s.io/v0.20/docs/concepts/fair_sharing/)

Slurm 的 QOS 可以配置允许抢占的服务等级关系。这说明优先级抢占可以作为独立策略，不必都解释成收回队列份额。[Slurm QOS](https://slurm.schedmd.com/qos.html)

层级组织也有实际实现，例如 YuniKorn 的父子队列、资源保障和上限设置。[YuniKorn Queue Configuration](https://yunikorn.apache.org/docs/user_guide/queue_config/)

## 回填：利用大任务启动前的空档

假设现在只有 8 张空闲卡，高优任务需要 16 张，预计 20 分钟后其他任务退出，才凑得齐。

如果另一个低优小任务只需要 4 张、可靠预计 5 分钟能完成，就可能先运行它。关键条件是：**不会推迟高优任务预计的启动时间**。这就是回填调度的一种直观情形；它依赖合理的运行时长估计，不能把“先塞进去，之后再杀掉”都叫回填。[Slurm Backfill](https://slurm.schedmd.com/sched_config.html)

## 改变工作负载有多大

推理服务可以按需求调整副本数，例如从 2 个副本增加到 4 个，负载下降后再缩回去。Kubernetes HPA 就用于按指标调整目标工作负载副本数。[Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)

某些训练框架也支持调整 worker 数，但能否在线调整、是否需要重启、训练语义如何保持，要查框架能力；不能从“有空闲 GPU”推定一个固定规模训练任务能自动多用几张卡。

## 改变资源池有多大

如果现有节点根本装不下待运行 Pod，节点自动扩缩容可以尝试增加机器，需求减少时再整合或缩减节点。Kubernetes 生态中的 Cluster Autoscaler、Karpenter 属于这一层。[Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)

这还受到云端供给、预算、配额和启动时间约束。在固定采购的集群里，调整队列权益本身不会凭空增加 GPU。

## 自测：先判断在改哪一层

1. B 从使用 40 张变成使用 80 张，但集群机器没变。
2. 推理服务从 2 个副本变成 4 个。
3. 集群新增两台 GPU 机器。

<details>
<summary>展开参考答案</summary>

1. 队列分配层，可能发生了借用。
2. 工作负载规模层，还需要实际资源承载新增副本。
3. 节点容量层，增加了实际资源；但可否立即接请求仍取决于工作负载启动和就绪。

</details>

“配额保障、借用、回收、公平共享”等机制在多个成熟系统中都有实现，因此可以称为常见方案之一。这里没有做市场占有率调查，也不认为某一个产品或某种组合适用于所有训推场景。

资料核对：2026-10-22。案例为教学推演，未运行集群实验。

[上一篇：系统对照](02-volcano-and-kueue.md) · [练习：分配 100 张 GPU](../labs/01-share-100-gpus.md) · [返回知识地图](../README.md)
