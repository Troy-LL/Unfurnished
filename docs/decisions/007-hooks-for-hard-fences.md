# 007: Hard fences are hooks, not prose

Status: Accepted

## Context

Two rules in this pack must never be crossed: a living durable owner (README, AGENTS.md, `docs/architecture|design|eval.md`, one ADR) is patched in place, never blank-replaced; and `scratch/` never enters git history. Both were enforced by repeating the sentence in the prior, the map, and five skills. The README already says rules do not block `git reset --hard`. Harness research agrees: the Agentic Harness Engineering ablation ([arXiv 2604.25850](https://arxiv.org/html/2604.25850v3)) put the gain in tools and middleware; the prompt-only arm regressed. Cursor's middleware is `hooks.json` ([001](001-native-first.md) allows it: hooks are a native, not a wrapper).

## Decision

We will enforce the two hard fences with one command hook, `.cursor/hooks/fence.py`, invoked via `.cursor/hooks/run-fence.sh` (resolves `python3` then `python`) in `.cursor/hooks.json` and shipped by `plugin.json`: `preToolUse` on `Write` denies a full-file write to a non-empty durable owner; `beforeShellExecution` denies `git add` / `git commit` that would put `scratch/` in history unless `scratch/` is gitignored. The hook fails open (neither interpreter, crash, timeout → allow) so a product without Python is not bricked; `pack-check` fails closed if neither `python3` nor `python` is on PATH so common images do not silently ship a dead fence. The one-line prose fence stays in the kernel as the fallback. We will not add hooks for soft preferences.

## Consequences

The sentence "patch in place; never blank-replace" lives once in `unfurnished-bias` and once in the adopted troysdd skills (upstream text, [003](003-workflow-not-stack.md)); pack-owned files cite it instead of repeating it. `pack-check.py unittest` runs the fence against a temp git repo. Plugin hook path resolution is checked after a Customize re-import (`--strict-install`).
