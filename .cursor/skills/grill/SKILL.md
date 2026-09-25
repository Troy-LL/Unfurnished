---
name: grill
description: >-
  Relentless frontier interview to lock intent before building. Use when
  there is no checkable done-line, they want to align or stress-test a plan,
  or they say grill / grill docs. Do not use for cheap reversible edits, after
  they already confirmed a shared understanding, or when they named a feature or
  fix against an existing map (that is sdd-eng). Do not use when the
  user attached another pack's skill this turn.
---

# Grill

Interview until the design tree is empty. Do not implement until the user confirms a shared understanding.

## Docs flag

If the user said `/grill docs` or "grill docs": after they confirm, name which durable facts belong in which `/sdd` owner (README, AGENTS.md, architecture, design, eval, one ADR). Then stop. Do not write `CONTEXT.md`. Do not dual-write CLAUDE.md. Hand off to `/sdd`.

## Rounds

Map the work as a design tree. The **frontier** is every decision whose prerequisites are already settled.

Each round:

1. Ask the frontier. Prefer at most five questions this round. Number each. Give your recommended answer.
2. Wait. Do not guess unanswered branches. "You figure it out" is not a skip.
3. Recompute the frontier from their answers. Repeat.

Format:

```
**Q1 — <title>**: <body, choices if needed>

Recommended: <your answer>
```

Finding facts is your job. Do not ask the user anything you can look up. Dispatch a sub-agent for those lookups; ask the rest of the frontier now.

The session is done when the frontier is empty and they confirm. Then name the next `/` (`/sdd`, `/sdd-eng`, or stay and implement). Stop, unless the docs flag applies.
