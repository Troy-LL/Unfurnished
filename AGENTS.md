# Agent map

Load this file. Then at most two others this turn. Skip unused. Cite paths. Do not paste.

- `README.md` — what Unfurnished is, what we refuse to clone, and when an `.mdc` exists
- `docs/decisions/001-native-first.md` — a graph, memory, session, or router plugin looks useful; read before installing one
- `docs/decisions/002-first-shot-efficiency.md` — a token-golf or always-on lean pack looks useful; read before adding one
- `docs/decisions/003-workflow-not-stack.md` — a stack-specific skill, framework guide, or rewritten upstream looks useful; read before adding one
- `docs/decisions/005-tickets-as-tdd-pointers.md` — a GitHub or Linear ticket skill looks useful; local scratch pointers instead
- `docs/decisions/006-kernel-not-slot-map.md` — a static slot map, Claude workflow clone, or extra tool-search MCP looks useful; read before adding one
- `docs/decisions/007-hooks-for-hard-fences.md` — a fence needs to actually block, or a new hook looks useful; read before adding prose or a hook
- `docs/decisions/008-no-command-twins.md` — a `/command` for a skill, or a review skill, looks useful; read before adding one
- `docs/eval.md` — a cost class, model plan, routing dummy, or phrasing fixture looks useful; read before promoting 004

Pack is on (`unfurnished-bias`) unless `scratch/unfurnished-off` exists. Other plugins may run alongside. `/unfurnished off` / `on` is the workspace knob. Orientation: `/unfurnished`. Marketplace: `.cursor-plugin/marketplace.json` (plugin: `plugin.json`). Workflow skills: `.cursor/skills/` (`/<skill>` invokes; includes `/sdd` and `/sdd-eng`, adopted from [Troy-LL/troysdd](https://github.com/Troy-LL/troysdd)). Knobs: `.cursor/commands/` (two). Priors: `.cursor/rules/`. Fences: `.cursor/hooks.json`. Pack contract check: `python tools/pack-check.py` (add `--strict-install` after a Customize re-import; `unittest` runs the fence). Eval runs: `python tools/eval-run.py` (needs the Cursor CLI `agent`). Do not add MCP that duplicates Grep, Glob, or Read. Do not add a router skill.

Park thinking in `scratch/`. Do not map it, even if they asked. Do not commit it.
