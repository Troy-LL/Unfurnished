---
name: sdd-eng
description: >-
  Implements a behavior change in a product that already has (or is getting) an
  SDD map: edit the owning durable file and the code it points at, load only
  what this turn needs, and do not mint a per-feature spec/plan/tasks tree. Use
  when the user is coding a feature, fix, or refactor against an existing
  README, architecture, design, eval, or ADR, including when that file is on
  disk and not yet a map bullet, and including empty-shelf / empty-copy UI
  copy against a living docs/design.md. Do not use when creating or omitting
  product docs, distilling a PRD or idea dump, promoting scratch or a
  Proposed line, scaffolding Spec Kit / OpenSpec / Kiro, dual-writing
  CLAUDE.md, writing a markdown twin of OpenAPI or schema, or deciding
  whether a new durable file should exist. Do not use for a one-line edit,
  rename, or format pass. Do not use when the user attached another pack's
  skill this turn.
---

A change. `/sdd-eng`. Load stays on the product `AGENTS.md`. Authoring is `/sdd`.

Import this file into a product. Do not copy the guidebook.

## Steps

1. **Name the change.** One falsifiable sentence. Pause. Put that intent in the file you will edit. Do not start `spec.md` / `plan.md` / `tasks.md`.
2. **Owner or handoff.** Name the existing path: a map bullet, or the file already on disk. Dump / RFC / spike / `Proposed:` / spec tree, or no owner on disk and no map bullet → stop; that is `/sdd`.
3. **Load.** Read the product `AGENTS.md`. Open only the owner this turn needs. If the owner is `AGENTS.md`, Read [map.md](../sdd/map.md) as one extra. If loading more than one extra, pin README → architecture → design → eval. An ADR counts as one extra. Ceiling: this map + at most 2, or +3 if this turn needs `eval.md`. Skip unused. Cite paths. Do not paste. Do not open `docs/files.md` in a product.
4. **Edit.** Patch that owner in place and the code, schema, or tests it points at. Merge the fact this change needs; keep every other fact until the user deletes it on purpose. On a non-empty owner, use in-place patch edits only — a full-file replace fails this step. If this change names a thing, seat the synonym in that owner. When the user restates an already-agreed product decision, seat it in the existing owner this turn (`docs/design.md`, `docs/architecture.md`, or one ADR). A request to re-run something is not a decision. Do not create `CONTEXT.md` or `GLOSSARY.md`. No markdown twin. Do not mint `docs/glossary.md`. Thinking goes in `scratch/` (or the PR body). Do not map scratch, even if they asked. Do not delete a do-not-map line to satisfy a map request.
5. **Re-occasion.** If this turn made a job true whose owner path does not exist yet → `/sdd` for that file only. Stop.
6. **Verify.** Run the check the product `AGENTS.md` names. Do not skip.
