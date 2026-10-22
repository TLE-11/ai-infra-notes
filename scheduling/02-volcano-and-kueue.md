# 02 · Volcano 与 Kueue：相似的问题，不同的术语

> 核心问题：已经理解的“份额与借用”，在真实系统里叫什么？

Volcano 和 Kueue 是两个项目，不是两种互斥的弹性策略。它们都能表达队列共享与受控抢占，但概念、边界和执行路径不同。

## 先认识各自的角色

Volcano 提供面向批处理等工作负载的 Kubernetes 调度能力；这里关注它的队列资源管理。

Kueue 主要管理工作负载何时获得配额并被准入运行；工作负载准入后，Pod 的具体节点放置仍由 Kubernetes 调度器等组件完成。它的配额分配不等于已经给每个 Pod 找到了节点。[Kueue v0.20 概述](https://kueue.sigs.k8s.io/v0.20/docs/overview/)

## Volcano：份额、上限和专属保留

| 字段 | 学习时怎样理解 |
|---|---|
| `deserved` | 在 capacity 插件下显式设置的应得资源量 |
| `capability` | 队列使用的硬上限 |
| `guarantee` | 专属保留部分，其他队列不能借用 |
| `reclaimable` | 是否允许回收队列超额使用的资源 |
| `weight` | proportion 插件据此计算相对份额 |

要特别区分 `deserved` 和 `guarantee`：前者可用于弹性共享，后者是不可外借的专属保留。教学例子的 60/40 对应应得份额，并没有再各保留 60/40。

显式份额的 capacity 插件与按权重计算份额的 proportion 插件是不同选择，不能把两者当作同时叠加的两套份额。[Volcano Queue](https://volcano.sh/docs/concepts/queue/)

Volcano 的 `preempt` 动作主要处理队列内高优任务抢占，`reclaim` 处理队列间资源回收。读日志或配置时，应按这个产品语境理解。[Volcano 队列资源管理](https://volcano.sh/docs/keyfeatures/queueresourcemanagement/)

## Kueue：配额队列和共享组

| 概念 | 学习时怎样理解 |
|---|---|
| `ClusterQueue` | 管理一组工作负载可用的配额及相关策略 |
| `Cohort` | 允许队列共享配额的分组，可组织层级 |
| `nominalQuota` | 队列自己的名义配额 |
| `borrowingLimit` | 对借入资源数量的限制 |
| `lendingLimit` | 对允许借出配额数量的限制 |

可以把 A、B 放在同一共享组，分别配置 60、40 的名义配额。还要检查借入、借出和资源类型等限制，才能判断是否能复现前文的共享案例。[Kueue ClusterQueue v0.20](https://kueue.sigs.k8s.io/v0.20/docs/concepts/cluster_queue/)

Kueue 将驱逐已准入工作负载以容纳其他工作负载的行为统称为 preemption。队列内按优先级抢占、共享组内回收等规则可以分别控制；有优先级并不自动意味着能驱逐所有低优工作负载。[Kueue Preemption v0.20](https://kueue.sigs.k8s.io/v0.20/docs/concepts/preemption/)

## 只能近似对应，不能机械翻译

| 想表达的意思 | Volcano | Kueue |
|---|---|---|
| 队列的应得权益 | `deserved` 或权重计算份额 | `nominalQuota`，语义与约束仍需分别查看 |
| 队列间共享组织 | 队列及其层级、相关插件与策略 | `Cohort` 及借贷限制 |
| 队列间回收超额占用 | `reclaim` | cohort 内相关 preemption 策略 |

这张表是阅读辅助，不是配置迁移表。不要把 `capability` 直接当成 `borrowingLimit`：一个约束总使用量，一个约束借入量。

## 自测

“Kueue 配额准入成功了，所以 8 个 Pod 已经分别拿到 GPU 并开始运行。”这句话哪里跳了一步？

<details>
<summary>展开参考答案</summary>

跳过了节点放置和实际启动。准入允许工作负载进入运行流程，具体节点是否满足 GPU、拓扑等约束，以及实例是否就绪，还要继续检查。

</details>

资料核对：2026-10-22；Kueue 固定参考 v0.20，Volcano 使用当日公开的 Latest 文档。未运行配置验证，也不据此判断某个平台实际使用了哪种调度器。

[上一篇：配额与共享](01-quota-borrowing-reclaim-preemption.md) · [下一篇：其他弹性策略](03-elasticity-strategies.md) · [返回知识地图](../README.md)
