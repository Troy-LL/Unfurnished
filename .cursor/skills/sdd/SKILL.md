---
name: sdd
description: >-
  Applies Troy's SDD: create README, AGENTS.md, architecture, design, eval, or one
  ADR only when that job is true; distill a PRD or ideation dump into those owners;
  park thinking in scratch and promote residue. Use when adding product docs, an
  agent map, a Spec Kit / OpenSpec / Kiro tree, a markdown twin of OpenAPI or
  schema, dual-writing CLAUDE.md, an RFC, spike, design week, a Proposed line in
  architecture, or a jumbled PRD / idea / spec file to distill. Do not use when
  implementing a feature, fix, or refactor while the matching owner already
  exists on disk — that is `/sdd-eng` (merge into the living file).
---

Authoring. `/sdd`. Classify, then Read the matching file. Load stays on the product `AGENTS.md`. A behavior change is `/sdd-eng`.

If this workspace is the guidebook, Read `docs/files.md` only when the disclosed file is not enough.

After compaction or `/summarize`, re-Read `AGENTS.md` then the owning file before seating names. Do not create `CONTEXT.md` as a glossary re-anchor — seat words in the living owner.

## Steps

1. **Classify.** User pointed at a dump (PRD, idea note, spec paste) → [distill.md](distill.md). Matching owner already on disk → `/sdd-eng` unless this is distill or promote. A glossary / Names dump is not a missing owner — seat the words in the matching owner. Durable file whose job is true now and the path is missing → [occasion.md](occasion.md). Still many-valued (RFC, spike, design week, `plan.md`/`tasks.md`, `Proposed:`) → [promote.md](promote.md). Spec/plan/tasks tree → promote, then occasion for residue. Done when exactly one of those files is open.
2. **Follow it.** Stop when that file’s completion criterion is met.
