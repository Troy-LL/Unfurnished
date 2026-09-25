# Unfurnished pack

Portable constitution. Use this when the guidebook repo files are not in the workspace (plugin install). If `docs/decisions/001-native-first.md` exists here, prefer those owners over this file.

## Constitution

- Gap or out. Do not add graph, session, memory, or auto-routing tools. Cursor already searches, remembers, routes, checkpoints, and compact.
- First few attempts accepted, net of tax, out of the box, on whatever model the host picked. Expertise is on-demand. `AGENTS.md` (the host repo) stays a map: read it, then at most two owners. Do not paste.
- Workflow, not stack. A piece must work unchanged on a project we have never seen. Adopt a battle-tested upstream with attribution; do not rewrite it.
- A new add must name a gap Cursor does not ship.
- Always-on is a kernel (natives, one slot, no extra probes). Skills pull on match. Do not freeze a slot map in the prior. Do not clone a Claude workflow runtime.

## Catalog

Who can reach it is the split. Model-invoked: the agent may pull it when the task matches; you can still type `/`. User-invoked: only the human starts it.

**Model-invoked**

| Skill | What |
|-------|------|
| `unfurnished` | Orient, or intake a pasted job. `on` / `off` is the workspace pack knob (default on). Runs alongside other plugins |
| `sdd` | Product docs (adopted from troysdd) |
| `sdd-eng` | Behavior change against the map (adopted from troysdd) |
| `grill` | Frontier interview when there is no checkable done-line. `/grill docs` then `sdd` |
| `blueprint` | Whole-job kickoff. Not mid-task. Model plan only if they asked about cost |
| `verify` | In-turn Definition-of-Done verification gate |
| `ticket` | Local TDD pointer in `scratch/tickets/`. Not a GitHub/Linear wrap |
| `evals` | Pipeline evals, traces, cost class for this repo. Do not pin a vendor model |
| `write-skill` | Author a skill. Do not wrap `/create-skill` |

**User-invoked**

| Skill / knob | What |
|--------------|------|
| `/voice` | `plain` \| `ste` \| `off` |

**Always-on / opt-in priors**

| Prior | What |
|-------|------|
| `yagni-bias` | Always-on, ~40 words |
| `comments-belong-in-docs` | Always-on. Intent lives in the docs. A narration comment leaves with the edit |
| `reply-shape` | Always-on. Outcome first, in affirmative language. Detail when they asked |
| `unfurnished-bias` | Always-on kernel, not a slot map. Maximize natives, one slot, no extra probes. On unless `scratch/unfurnished-off` exists. Alongside other plugins. Owns the scratch and living-owner fences |
| `fence.py` hook | Hard stop: blocks a full-file Write to a living durable owner and any `git add`/`commit` that would ship `scratch/`. Fails open |
| `@yagni` | 7-rung ladder |
| `tdd` | Red-green on a feature or fix. Skip only if you say why |
| `@blast-radius` | Said → cited → walked → ran |

Product docs: `/sdd`. Implementation: `/sdd-eng`. A living owner on disk stays a merge — never blank-replace. Both ship here from [Troy-LL/troysdd](https://github.com/Troy-LL/troysdd). Do not rewrite them in this tree.

## Cursor surface

Type the native. Do not wrap it.

| Type this | When |
|-----------|------|
| Plan / Ask / Debug | Design gate, lookup, or red-repro. Agent is the default loop. |
| Task, `/create-subagent` | Fresh context, isolated implementer or reviewer |
| `/best-of-n`, `/worktree` | Parallel attempts; pick a winner |
| `/loop`, Cloud Agents, Automations | Unattended or recurring |
| Bugbot, Security Review | Review a diff out of this chat |
| `/rewind`, checkpoints | Undo an agent turn |
| `/summarize` | Compact the window |
| Browser, `/canvas`, Design Mode | Click the app or a mock |
| `/babysit` | Watch a PR |
| `/create-skill`, `/create-rule`, `/commands` | Author a slot. Then `write-skill` if it is a workflow. |
| `/create-hook`, `hooks.json` | Hard stop, not a rule |
| Explore, Grep, Glob, Read | Find code. No graph plugin. |

`/unfurnished` offers the one or two rows that match. It does not pick. It does not stay on.

## Task matrix

Spawn with Task. Pick the type. Do not invent a named agent. Do not wrap Bugbot or Security Review in a skill.

| Job | Type | Model |
|-----|------|-------|
| Map a tree, find files | `explore` | inherit. Fast only if they asked for cheap fan-out. |
| One command, git, install | `shell` | inherit |
| "In Cursor, how do I…?" | `cursor-guide` | inherit |
| One failing PR check | `ci-investigator` | inherit |
| Bug review of a diff | `bugbot` | inherit |
| Security review of a diff | `security-review` | inherit |
| Isolated parallel attempts | `best-of-n-runner` | inherit |
| Multi-step research or implement | `generalPurpose` | inherit |

`inherit` is Auto: same model as this chat. Pass another `model` only when the user named a slug or asked for a class (fast fan-out vs deep); take the slug from the Task tool list in this session. If it is not listed, say unavailable. Do not substitute. Slugs rot; types do not; this file names no slug.

## Task prompt

The type is not enough. Write the `prompt` before spawn. Do not paste a playbook. Do not tell them to read a router skill first.

Every spawn, in this order:

1. **Job** — one sentence. The user's actual job, not a template. Do not invent files, bugs, or folders they did not name. If those are unknown, spawn `explore` first or say unknown.
2. **Read** — paths or owners. Cite. Do not paste. If paths are unknown, write "discover then cite" or spawn `explore` first. Do not invent paths.
3. **Done** — one checkable line.
4. **Return** — the shape (table, paths, verdict). No transcript dump.
5. **Stop** — do not spawn children. Do not commit unless the job says so. Parallel workers in the same tree: no git, no root manifests.

Type extras:

| Type | Extra in the prompt |
|------|---------------------|
| `explore` | Find. Do not edit. Thoroughness: quick / medium / very thorough. |
| `shell` | Commands only. Report exit codes. |
| `cursor-guide` | Product how-to. No repo edits. |
| `ci-investigator` | One failing check. Root cause, not a fix tour. |
| `bugbot` / `security-review` | Use those Task types. Do not rewrite their rubric. Diff via `git status --short` and `git diff`. No implementer rationale. |
| `best-of-n-runner` | Same job, isolated tree. |
| `generalPurpose` | If they implement: failing test first when `tdd` is on. If they only survey: say so. |

A blank "look at this repo" prompt is a miss. Improve it, then spawn.

## Leave out

If Cursor ships it, do not wrap it: graph/codegraph, session or memory plugins, auto-routers, hook frameworks, checkpoint wrappers, cost CLIs, compact packs, output-style plugins, statusline themes, permission MCP, worktree managers, review-agent packs, Ralph loops, a second skill marketplace, rule or slash-command authoring playbooks, Browser/Playwright MCP, canvas taste packs, Plan wrappers, `/babysit` loops.

If it assumes a stack, leave it out: framework guides, service integrations, language-specific runners. If a battle-tested upstream already passes, adopt it; do not rewrite it.
