# AI Infra Notes · Understanding Compute Systems

**English** | [简体中文](README_CN.md)

Learning notes on GPU resource pools, resource scheduling, and inference serving, starting with practical questions.

First question: **How can several teams share 100 GPUs efficiently while ensuring critical workloads get the resources they need?**

## Start Here

No GPU or Kubernetes cluster is required. Read the first three notes in order, then try the paper exercise. Product names and configuration fields can wait until the implementation comparison.

The notes and lab linked below are currently in Simplified Chinese.

| Step | Note | What you will learn |
|---|---|---|
| 1 | [GPU Resource Pools and Unified Training and Inference](gpu-systems/01-unified-resource-pool.md) | How do a logical pool, physical clusters, and queues differ? |
| 2 | [Resource Scheduling and Traffic Scheduling](gpu-systems/02-resource-and-traffic-scheduling.md) | Who allocates GPUs, and who routes requests? |
| 3 | [Quotas, Borrowing, Reclamation, and Preemption](scheduling/01-quota-borrowing-reclaim-preemption.md) | Why can a queue with a 40-GPU entitlement use 80 GPUs? |
| 4 | [Lab: Allocate 100 GPUs](labs/01-share-100-gpus.md) | When should you borrow, reclaim, or wait? |
| 5 | [Volcano and Kueue: A Concept Comparison](scheduling/02-volcano-and-kueue.md) | How do familiar concepts map to real systems? |
| 6 | [Other Resource Elasticity Strategies](scheduling/03-elasticity-strategies.md) | What problems do fair sharing, backfill, and autoscaling solve? |

## One Example Throughout

There are 100 identical GPUs. Team A is entitled to 60, and Team B to 40. Both may borrow unused shares, both have a usage limit of 100, and neither has an exclusive reservation.

| Scenario | A allocated | B allocated | Pool idle | What happened |
|---|---:|---:|---:|---|
| A has low demand | 20 | 80 | 0 | B uses 40 GPUs beyond its own share |
| A's demand rises to 50 | 50 | 50 | 0 | Reclaim 30 from B; B still borrows 10 |
| A's demand rises to 60 | 60 | 40 | 0 | Reclaim another 10; both return to their entitlements |

This teaching model leaves out whole-machine allocation, GPU differences, network topology, indivisible jobs, and resource release delays. Real scheduling must account for these constraints before evicting workloads.

## Repository Layout

```text
ai-infra-notes/
├── README.md          # English introduction
├── README_CN.md       # Chinese introduction
├── AGENTS.md          # Guidelines for maintaining the notes
├── gpu-systems/       # Resource pools and how they support training and inference
├── scheduling/        # Resource allocation, borrowing, reclamation, and preemption
└── labs/              # Small exercises, starting with a paper simulation
```

## How to Use These Notes

Each note starts with a question, explains it through examples, and ends with a self-check and references. Try answering in your own words before expanding the suggested answer. If you get stuck, revisit the example before memorizing configuration fields.

The notes distinguish three kinds of content: **teaching models** simplify a problem for learning; **system facts** rely on official sources with a version or verification date; **engineering judgments** explain tradeoffs and should not be treated as a product's default behavior.

These notes do not claim to verify any company's production architecture. When comparing them with a real platform, record observed behavior and keep unanswered questions explicit.
