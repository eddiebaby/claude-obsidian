---
type: concept
title: "DragonScale Memory"
complexity: advanced
domain: knowledge-management
aliases:
  - "DragonScale"
  - "DragonScale Architecture"
  - "Fractal Memory"
created: 2026-04-23
updated: 2026-04-23
tags:
  - concept
  - knowledge-management
  - memory
  - architecture
  - fractal
status: proposed
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Hot Cache]]"
  - "[[concepts/_index]]"
sources:
---

# DragonScale Memory

A memory-layer design for LLM wiki vaults, inspired by the Heighway dragon curve. Four mechanisms (fold operator, content-addressable paths, semantic tiling, boundary-first attention) give an LLM-maintained wiki a principled way to grow, compact, and stay coherent without ad-hoc rules. Not a reasoning architecture. Only a memory-layer spec.

---

## Scope Boundary

DragonScale is a **memory architecture**, not an agent framework. It governs how a wiki grows, compacts, and is addressed. It does **not** govern how an agent reasons, searches solutions, or branches hypotheses.

Attempts to force binary exploration-vs-validation branching on agent loops underperform variable-width search (Tree of Thoughts with BFS/DFS/beam search, Yao et al. 2023). Reasoning is not self-similar across scales. Memory organization is. DragonScale applies the fractal properties that actually hold.

---

## The Core Insight

The Heighway dragon curve has four mathematical properties with direct analogues in LLM memory systems:

| Dragon curve property | Memory analogue |
|---|---|
| Paper-folding recursion: `D_{n+1} = D_n · R · swap(reverse(D_n))` | Append-and-merge compaction (LSM trees; hierarchical summarization) |
| Turn direction derivable from the bits of `n` (regular paperfolding sequence, OEIS A014577) | Content-addressable page paths for prompt-cache stability |
| Tiles the plane with no self-intersection; twindragon is a rep-tile | Canonical-home coverage: one concept, one page |
| Boundary has fractal dimension ≈ 1.523627, interior has dimension 2 | Attention concentrates on the boundary of known pages |

The curve does not choose its turns. The turn at position `n` is determined by the bit just above the lowest 1-bit of `n`. This is the property worth borrowing: **structure derivable from history, not chosen at each step.**

---

## The Four Mechanisms

### 1. Fold Operator

Every `2^k` entries in `wiki/log.md`, run a fold: summarize the last batch into one meta-page, link children back, update the index. Folds stack. After `2^k` folds at level `k`, a level `k+1` fold produces a super-summary.

This is structurally identical to LSM-tree compaction (LevelDB and RocksDB use exponential level sizes, typically 10x per level). In LLM terms, it is automated hierarchical summarization with a fixed cadence instead of a heuristic trigger.

Invariants:
- Idempotent: re-running a fold on the same range is a no-op.
- Reversible: children remain in place; a fold is additive.
- Bounded: at any time, the wiki has at most `log_2(N)` fold levels above leaf pages.

### 2. Content-Addressable Page Paths

Every page gets an address in its frontmatter that encodes its position in the fold tree plus a content hash:

```
address: 0b10110/a7f3c2
```

The bit prefix encodes the page's lineage through folds. The hash suffix is a stability token tied to content. Two outcomes:

- **Deterministic reconstruction.** The page's history is derivable from its address.
- **Cache-stable prefixes.** When the vault is loaded as LLM context, Anthropic prompt caching only rewards breakpoints placed at the end of identical content. Address-anchored pages keep prefix hashes stable across sessions. The cache economics (5-minute TTL, 1.25x write premium, 0.1x read cost, 20-block lookback window) reward this directly.

### 3. Semantic Tiling Lint

The dragon curve tiles the plane without self-intersection. In a wiki, self-intersection is concept duplication. Two pages covering the same idea is a structural defect, not just a style issue.

Add an embedding-based check to `wiki-lint`:

- Compute embeddings for every page (local ollama with `nomic-embed-text`, no API cost).
- For any pair with cosine similarity above 0.85, flag as a tile overlap.
- Do not auto-merge. List for human review.

This is the tiling property enforced as a lint rule.

### 4. Boundary-First Attention

The dragon curve's interior is fully filled (dimension 2). The interesting structure lives on the boundary (dimension ~1.52). Boundary pages in a wiki are the ones with high out-degree relative to in-degree, or the most-recently-touched: the frontier of what the vault knows.

Extend `autoresearch` with a boundary score:

```
boundary_score(page) = (out_degree - in_degree) * recency_weight
```

When `/autoresearch` is invoked without a topic, it reads the top-5 boundary pages and generates research prompts from them. The vault steers itself toward its own unresolved edges.

---

## Mapping to Claude-Obsidian

| Mechanism | New | Extends |
|---|---|---|
| Fold operator | new skill: `wiki-fold` | reads `log.md`, writes `wiki/folds/`, updates `index.md` |
| Address anchors | new frontmatter field | `wiki-ingest` assigns on create; `wiki-lint` validates |
| Semantic tiling | new lint check | `wiki-lint` |
| Boundary-first | new scoring in `autoresearch` | `autoresearch` |

Existing hot → index → domain → page hierarchy already implements **self-similarity across scales**, the one dragon-curve property this vault had for free.

---

## Why This Over Alternatives

| Pattern | What it gives | What DragonScale adds |
|---|---|---|
| MemGPT virtual context (two-tier paging) | Main context ↔ external context swap | Multiple fold levels; deterministic cadence; address scheme |
| Pure LSM tree | Exponential compaction | Semantic tiling (embeddings); boundary scoring |
| Ad-hoc `/save` | Human-triggered filing | Rule-based fold trigger |
| Vector-only RAG | Retrieval | Structure; canonical homes; prompt-cache stability |

DragonScale is a composition of patterns already validated in adjacent systems (LSM compaction in databases, MemGPT paging in agents, Anthropic cache ordering in prompt engineering, embedding similarity in dedup), held together by a design-justification device (the dragon curve) that tells you which knobs to tighten and why.

---

## Open Questions and Limitations

- **Unvalidated at scale.** All four mechanisms are theoretically sound but untested in a real multi-thousand-page vault.
- **Fold cadence tradeoff.** `k=4` (fold every 16 entries) is responsive but produces many meta-pages. `k=5` is sparser but slower to react. Needs empirical tuning.
- **Embedding cost.** Local embeddings are free but slow (~30s for a full vault pass). Cached similarity matrices required to make this practical.
- **Address stability across content edits.** When a page is edited, the content hash changes. Either the bit-prefix stays (preferred, lineage preserved) or the whole address rotates (simpler, less stable). This is the main unresolved design question.
- **Tiling threshold is arbitrary.** 0.85 cosine is a guess. Needs calibration against known duplicates in the existing vault.

---

## Primary Sources

All four mechanisms are backed by primary sources, verified 2026-04-23:

- Dragon curve math and properties: [Dragon curve, Wikipedia](https://en.wikipedia.org/wiki/Dragon_curve); boundary dimension `2·log_2(λ)` where `λ^3 − λ^2 − 2 = 0`, giving 1.523627086.
- Paperfolding sequence (bit-derived turns): [Regular paperfolding sequence, Wikipedia](https://en.wikipedia.org/wiki/Regular_paperfolding_sequence); [OEIS A014577](https://oeis.org/A014577).
- Tiling and rep-tiles: [Wolfram Demonstrations: Tiling Dragons and Rep-tiles of Order Two](https://demonstrations.wolfram.com/TilingDragonsAndRepTilesOfOrderTwo/).
- LSM trees: [How to Grow an LSM-tree? (2025)](https://arxiv.org/abs/2504.17178); LevelDB and RocksDB vertical-scheme 10x level ratio.
- Hierarchical LLM memory: [MemGPT: Towards LLMs as Operating Systems (Packer et al. 2023)](https://arxiv.org/abs/2310.08560); [A-Mem: Agentic Memory for LLM Agents (2025)](https://arxiv.org/abs/2502.12110).
- Prompt caching economics: [Anthropic Prompt Caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).
- Reasoning search (out of scope but cited to justify the scope boundary): [Tree of Thoughts, Yao et al. 2023](https://arxiv.org/abs/2305.10601).

---

## Connections

See [[LLM Wiki Pattern]] for the broader pattern this extends.
See [[Compounding Knowledge]] for why persistent wiki state is the precondition for DragonScale to work.
See [[Hot Cache]] for the existing 500-word session context, which is a level-0 manual fold.
See [[Andrej Karpathy]] for the intellectual lineage (small systems, iterative loops, persistent wikis).
