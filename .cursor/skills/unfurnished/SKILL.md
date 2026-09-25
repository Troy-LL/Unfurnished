---
name: unfurnished
description: >-
  Orients to the Unfurnished pack and runs a job that arrives after
  /unfurnished — including messy, meta, or vague prompts. Use when the user
  says unfurnished, /unfurnished, cursormax, /cursormax, Cursor Max, Cursor
  Maxxing, asks what this pack ships, or asks what to type next. Do not use
  for a one-line edit, rename, or format pass that never invoked this pack.
  Do not use when /sdd or /sdd-eng is already the slot — those skills load
  themselves.
---

# Unfurnished

This pack is a small Cursor-native kit. It is not a Claude Code pack and not a pstack / poteto-mode orchestra. Don't attach Claude furniture to Cursor. The room looks empty. That is the point.

## Load

1. If `docs/decisions/001-native-first.md` exists in the workspace, read `AGENTS.md`, then at most two owners. Cite paths. Do not paste.
2. Otherwise read `reference.md` beside this skill. That is the portable constitution and catalog.
3. If the host has `AGENTS.md`, still load it as the project map (at most two owners). Do not treat this pack as a second map.

Do not dump those files into the reply. Follow them.

## Coexistence

Other plugins and skills stay. This pack runs alongside other plugins. If they attached another pack's skill this turn, skip pack slots (same list as soft-off), do not pull tdd, and do not wrap their tools. Do not restate this pack's catalog over theirs. `/unfurnished off` mutes Unfurnished for the workspace when they want the other pack alone. Hard off is Customize → disable plugin.

## Entry

Most people type `/unfurnished` and paste a job — often a meta-prompt, a wish list, or noise. That paste **is** the job. Do not ask "what is the job?" when they already gave one. Do not dump the catalog.

| What they sent | Do this |
|----------------|---------|
| Exactly `off` | Already handled in the command. Do not Intake. |
| Exactly `on` | Already handled in the command. Do not Intake. |
| Slash only, no job | Orient in one short line. Report soft-off if `scratch/unfurnished-off` exists. Ask for the job. Stop. |
| Slash + any job text | Run **Intake**, then **Offer**, then work or wait. Do not treat leftover `on`/`off` inside a sentence as the knob. |

### Intake

From the paste, keep the real ask. Drop role-play, "act as", persona stacks, tool inventories, and filler. Restate the job in one sentence before you branch. If you cannot name a checkable done-line, intent is not locked — go to `/grill` (or offer Plan once). Do not invent scope they did not state.

The priors this pack ships are already on or attach on match (`yagni-bias`, `tdd`, `@blast-radius`). Do not restate them.

### Offer

Name the one Cursor native that fits (the `reference.md` Cursor surface table has the list; do not paste it). If they already named it, do that. Otherwise offer the fork once — this chat, or that native — and wait. Do not pick. Do not re-offer every turn. Do not wrap the native. Do not spawn a named-agent roster.

Which pack skill runs is not decided here: the matching skill pulls itself from its own description (ADR 006). If none matches, none runs.

When they pick Task: name the `subagent_type` from the `reference.md` Task matrix, `inherit` the model unless they named one, and write the `prompt` from the Task prompt contract. Do not invent a named agent.

## Slots

| Kind | Use |
|------|-----|
| Skill | Workflow. `/<skill>` invokes it; there is no command twin (ADR 008). Host `.cursor/skills/` for new ones |
| Command | Knob with state. `/voice`, `/unfurnished on` \| `off` |
| Rule | Constraint. `@yagni`, `tdd`, `@blast-radius`. `yagni-bias`, `comments-belong-in-docs`, `reply-shape`, and `unfurnished-bias` are always-on |
| Hook | Hard fence. `.cursor/hooks/fence.py` (ADR 007) |

A new add must name a gap Cursor does not ship, work on a project we have never seen, and beat a rewrite if a battle-tested upstream already exists. No router. No second marketplace. No stack skill. No review skill. `/sdd` and `/sdd-eng` are adopted from troysdd — edit upstream, then re-adopt.

Scratch and living-owner fences: the kernel (`unfurnished-bias`) owns them. Do not restate them here.

## Done

- Slash only: oriented, waiting on a job, no catalog. Soft-off reported if the file exists.
- Exactly `on` / `off`: knob already applied in the command. Stop.
- Slash + job: one-sentence restatement, fork offered once (or skipped), then working or grilling — without restating the README.
