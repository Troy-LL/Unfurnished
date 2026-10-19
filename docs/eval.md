# Eval — cost class for a repo, and the 004 table

Gold for `blueprint/model-plan.md` in [004](decisions/004-blueprint-routing.md) and for a per-repo class card. Skip this file on ordinary kickoff. Skip unless the EVAL-TASK asks for a cost class or model plan.

`docs/evals/dummies/t0-cli` is a **red-health fixture only** (must start failing). It is not a routing arm.

The first qualifying dummy is `docs/evals/dummies/t1-nook`. Its EVAL-TASK asks for a cost class. Success is that dummy's `Red` command exit 0 after the agent stops, and `docs/design.md` still contains every line it had before the run except the one empty-copy fact.

A landing probe in this guidebook must **restore** `Coming soon.` in `page.py` and `docs/design.md` before yield so the next run still starts red. Record the green run in `docs/evals/traces/`. One in-session landing is not a cost class and is not n ≥ 3.

The 004 table stays EXPERIMENT until t1-nook has n ≥ 3 traces per arm in `docs/evals/traces/` (copy `docs/evals/trace-fixture.md`). Do not promote 004 from t0-cli, from pack-check, or from one landing.

A per-repo class card is the cheapest cost class that hits pass@k on that repo's frozen Red tasks. Same traces fill 004. Map the class to a live picker name at run time. Do not pin a vendor model. Do not wrap Auto.

## Floor

Routed ≥ best fixed arm on **success** (Red exit 0). Prefer the arm with fewer user turns and fewer extra tool calls. Token/cost from the usage dashboard is optional — Cursor often does not show it in-session. Fail: delete the table from `model-plan.md`, keep triage + language interview, record why in 004.

## Scrape

Count from the transcript, not from a missing dashboard:

1. **Turns** until the dummy is accepted (user messages after the task is given). Shorter wins at matched success.
2. **Tool calls** — total, and **extra** (anything that is not Grep, Glob, Read, or the one native the job named: Plan, Task, Debug, Shell for the Red command). Extra probes lose.
3. Success = that dummy's `Red` command exit 0 after the agent stops, plus the design-file keep rule above when the dummy ships a `docs/design.md`.

If a usage-dashboard scrape exists, record tokens as a note. Do not block a trace on missing tokens.

## Sample size

At p ≈ 0.46 and n = 100, the 95% margin is about ±10 points. A result inside that margin needs more samples before a decision. No field claim rests on a pattern with fewer than 20 events unless a deterministic fixture backs it (`pack-check`, `--phrasings`, `--holes`, or a dummy Red command).

## Field sessions

Scrapes of desktop transcripts, a judge such as Jev, and a host globalStorage database are Troy-local. They are not pack product. Drop host-injected user lines and wrapper tags before a turn count. Export composer text only: no corpus in this repo, no keys, no tokens, no settings. Skip a workspace database that only repeats prompts already in the transcript. A judge that saw only failed tool output makes an unverified-claim rate an upper bound. Score a hole probe from its RESULT line. Keep any API key in the environment; do not write it into a trace. Do not add a reader of agent transcripts, globalStorage, `state.vscdb`, or workspace databases.

## Run it

Strings in files are not evidence; `pack-check` only proves the words are there. Runs come from the Cursor CLI, headless:

```bash
python3 tools/eval-run.py --dummy t1-nook --arm always-cheap --model <picker slug> --n 3
python3 tools/eval-run.py --dummy t1-nook --arm routed --n 3        # Auto
python3 tools/eval-run.py --dummy t1-nook --arm soft-off --n 3      # same prompt and model; writes scratch/unfurnished-off
python3 tools/eval-run.py --phrasings                               # docs/evals/phrasings.md
```

Each dummy run copies the fixture into a temp workspace (not `EVAL-TASK.md`), materializes a temp `--plugin-dir` with only the shipped surface (`.cursor/`, `.cursor-plugin/`, `AGENTS.md`, `README.md`, `docs/decisions/`), runs the agent once with the task as the CLI prompt, runs the Red command, checks the design-keep rule, and writes one trace to `docs/evals/traces/` outside that plugin dir (turns = 1 by construction; completed stream-json calls only). Soft-off traces report `pack_loaded` and `pack_read` separately. The 004 gate reads those traces.

### Soft-off on the host

`/unfurnished off` writes `scratch/unfurnished-off`. Bias and the unfurnished skill still stop pack seats (no sdd/verify/…, no seating or minting `docs/design.md` / `AGENTS.md`). Customize and the CLI may still **list** pack skills while that knob is on — the host picker is outside this pack. Score soft-off with `pack_read` (did the agent Read pack text?) plus the knob file; do not treat `pack_loaded` alone as “skills hidden.” This guidebook does not invent a host API that hides the list.

### Answer keys stay out of the agent workspace

`--plugin-dir` is a temp copy without `docs/evals/`, `docs/eval.md`, or `tools/`. Hole workspaces get only this repo’s `AGENTS.md` (plus what the agent writes). Dummy and phrasing workspaces get the fixture files, not `EVAL-TASK.md`, `docs/evals/holes.md`, or traces. The harness reads those keys from the checkout; the agent prompt carries the task text.

[`docs/evals/phrasings.md`](evals/phrasings.md) is the routing fixture: plain asks → the skill that should pull. After [006](decisions/006-kernel-not-slot-map.md) the descriptions are the router, so a phrasing that misses is a description bug. A row under 2/3 means rewrite that skill's `description:`, not the phrase.
