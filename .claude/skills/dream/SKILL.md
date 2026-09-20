---
name: dream
description: Log, analyze, and record the response to a dream in wiki/dreams/. Use when Scott says "log this dream", "log dream", "analyze my dream", "analyze wiki/dreams/<file>", pastes a dream, or gives a clicks/partial/miss verdict on a dream analysis.
---

# Dream workflow

Three phases, gated. Never skip a gate. Entries live in `wiki/dreams/YYYY-MM-DD-keyword.md` and follow `_templates/dream.md` (Templater syntax there — write resolved values, not `<% %>`).

`status` tracks the phase: `unanalyzed` → `associated` → `analyzed` → `responded`.

## Phase 1 — LOG (`log this dream` / pasted dream / `log dreams` = process `wiki/dreams/inbox.md`)

0. **Follow-up first.** If the previous entry has a *Waking Action* and no `action_done`, ask in one line whether he did it, and record the answer there.

1. Create the entry from the template. Filename keyword: 2–5 words naming the core images. Record the dream text verbatim in *The Dream* (light cleanup of transcription errors only; mark uncertain words `[?]`).
2. Pull Conscious Situation, Associations, Feeling-Tone, Day Residue from whatever Scott gave. Don't invent.
3. **Association gate.** Identify the 3–7 load-bearing images (named people, odd objects, places, the affect peaks). For each one without a personal association, ask a single short question. Also ask for Conscious Situation if missing. Send the questions as one numbered list and **stop**. Don't write analysis yet.
   - For `log dreams`: each `## YYYY-MM-DD` block in the inbox becomes an entry (`ctx:` lines go to Conscious Situation). Run the gate for all of them in one list, then clear the processed blocks from the inbox.
   - Read `wiki/dreams/dreamer-context.md` first (biography + recurring figures); never re-ask what's there. Check [[dream-threads]] and grep `wiki/dreams/` for the recurring figures/places first. If a person or place already has associations in an earlier entry, reuse them and skip the question ("Niky — per 07-11, current partner").
4. When Scott answers, write the answers into *Waking Associations* / *Conscious Situation* (and add any recurring figure to `dreamer-context.md`), set `status: associated`, then go to Phase 2.
   - Scott can override: "skip, just analyze" → proceed, but put `> Analyzed without associations — lower confidence.` at the top of the analysis and list the unanswered questions under *Open Questions*.

## Phase 2 — ANALYZE (`analyze my dream` / after the gate)

Read before writing: the entry, `dreamer-context.md`, [[dream-threads]], the last ~5 entries, and the Agency section of [[longitudinal-study]].

Fill the Jungian Analysis sections:

- **Series Context** — first section. Which threads this dream continues (by name as in dream-threads), with the prior instances as wikilinks, and what *changed* this time ("4th water dream: frozen 06-28 → flood 07-23 → now...). Jung: the series interprets itself — a reading that contradicts the series needs a stated reason.
- **Symbols & Amplification** — personal association first, then amplification. Amplification must be cited (see Citations). An unsourced archetypal claim is either cut or marked `(uncited)`.
- **Competing Reading** (after Compensation, matching the template's section order) — the strongest alternative interpretation in 2–4 lines (e.g. reductive/personal vs. archetypal, or a different figure as the dream-ego's counterpart). State which one you favor and why. The dreamer's verdict decides between them over time.
- **Archetypal Figures**, **Compensation** (explicitly against the Conscious Situation — what one-sidedness is being corrected), **Movement Toward Individuation**.
- **Agency** — score 1–5 using the SDA rubric in longitudinal-study, one line of justification. Write it to frontmatter `agency:`.
- **Open Questions** — include anything unresolved from the association gate.
- **Sources** — list every citation used.
- **Waking Action** — one concrete thing to do: an active-imagination prompt addressed to a specific figure, a conversation, or a waking move the dream points at. Not homework-generic.

Then set frontmatter `figures` and `motifs` (**controlled vocab only**, from `wiki/dreams/motifs.md`; add new tags there first), `archetypes`, `symbols` (kebab-case, reuse existing symbol names — grep other entries first so Dataview grouping works), `related` (dream-threads, longitudinal-study, prior dreams cited, concept pages), `status: analyzed`, `updated`.

End the chat reply by asking: **"Clicks, partial, or miss?"**

### Citations

In priority order:
1. **CW paragraphs** — grep `individuation-app/data/cw8/chunks.jsonl` and `individuation-app/data/cw9i/chunks.jsonl` (each line has a `header` like `CW 8 — On the Nature of Dreams — paras. 560-564` and `[N]`-marked paragraph text). Cite as `CW 8 ¶305`. Quote ≤ one short line.
2. **Vault pages** — `wiki/concepts/`, `wiki/sources/`, `wiki/entities/` (von Franz, Edinger, the Dream Analysis seminar, etc.). Cite as a wikilink plus the page's own source citation where it has one.
3. Nothing found → mark `(uncited)`. Don't fabricate paragraph numbers.

## Phase 3 — UPDATE THE SERIES (same pass as Phase 2)

- [[dream-threads]]: add the entry to `related`, and append a dated line to each thread it advances. New motif seen in ≥2 dreams → new thread.
- [[longitudinal-study]]: append a row to the *Agency Over Time* table. Every ~10 new rows since the last phase write-up, tell Scott a phase update is due (don't auto-write it).
- Link the entry from the most recent prior entry's `related` only if they're thematically paired.

## Phase 4 — RESPONSE (Scott's verdict)

When Scott says clicks / partial / miss (or reacts in prose):

- Write his reaction into *Dreamer Response* — his words, lightly cleaned. Set `response:` and `status: responded`.
- On **miss** or **partial**: ask what's off in one question, then revise the analysis section that missed, keeping the original under a `> Revised YYYY-MM-DD — original reading: ...` note. Don't defend the original.
- Jung's rule: the interpretation that doesn't click for the dreamer is wrong, however elegant.

## Backlog re-analysis (`re-analyze the backlog`)

Source: `wiki/dreams/backlog-associations.md`. For each dream with new `A:` answers (Part A answers apply to every dream featuring that figure; Part B fills Conscious Situation by date): write the answers into the entry, re-run Phase 2 with citations, keep the prior reading under a `> Prior reading (pre-associations)` collapsed callout rather than deleting it, and re-score agency if the reading changed. Do dreams in batches of ~5, oldest first, and update dream-threads once per batch. Mark answered questions in the worksheet `✓ filed`.

## Style

Scott holds the concepts. Plain, direct, no over-explaining archetypes. Interpretation leads with what the dream is *doing*, not a symbol dictionary. Personal dream work is a real goal, not drift — don't redirect him to income work mid-analysis.
