---
type: domain
title: "AI / Machine Learning"
domain: ai-ml
status: developing
created: 2026-06-27
updated: 2026-06-27
tags:
  - domain
  - ai-ml
  - machine-learning
related:
  - "[[quantitative-finance]]"
  - "[[business]]"
subdomain_of: ""
page_count: 6
---

# AI / Machine Learning

Foundational AI/ML research not specific to finance. Overlaps with [[quantitative-finance]] (ML applied to markets) and [[business]] (LLMs applied to consulting work).

Navigation: [[index]] | [[domains/_index]]

---

## Scope in This Vault

Architecture research, optimization methods, and world model theory. Sources ingested from arXiv.

---

## Sub-areas

| Sub-area | Description | Sources in vault |
|----------|-------------|-----------------|
| World models | Neural nets learning environment dynamics from observation | [[facemind-looped-world-models-2026]] |
| Looped / parameter-efficient architectures | Same transformer block applied iteratively; 100× efficiency | [[facemind-looped-world-models-2026]] |
| LLM optimization | Iterate averaging, EMA weights, PACE optimizer | [[training-model-you-return-iterate-averaging]] |

---

## Key Concepts (in vault)

- [[World Models]] — neural networks learning environment evolution from observations and actions
- [[Looped Transformers]] — parameter-efficient architectures; same block applied N times
- [[Adaptive Depth]] — dynamic computation allocation; simple inputs exit early
- [[Deferred Decoding]] — refine latent state before decoding; improves reasoning quality

---

## Relationship to Other Domains

- **→ Quantitative Finance**: ML applied to asset prediction, portfolio optimization. Pages in this domain when the application is financial.
- **→ Business**: LLM pipelines for consulting workflows, client automation, content generation.

---

## Sources

- [[facemind-looped-world-models-2026]] — arXiv 2506.XXXX | FaceMind 2026 | Looped world models, 34-page survey
- [[training-model-you-return-iterate-averaging]] — arXiv 2606.25086 | Au, Block 2026 | PACE optimizer, EMA weight averaging for LLMs
