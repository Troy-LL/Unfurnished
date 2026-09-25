# First-shot correctness is the efficiency strategy

Status: Accepted

## Context

Token-efficient packs compress prompts, force terse output, and trim context every turn. That scores the wrong loop. A wrong first attempt burns the window twice and the human's reread. Per-message golf looks cheap and pays on the retry.

One-shot perfection is not the claim. A pack will miss. The bar is the first few attempts being the accepted ones, out of the box, without knowing slash names, on whatever model the host picked. A loop that only works after a slash name fails this.

Always-on lean can still win on a rename, a format pass, or a throwaway script. More upfront context can still lose when docs are stale or rules contradict. The thesis is a bias, not a law. A per-repo glossary looks like shared vocabulary; Evans's ubiquitous language lives in the model, the owners, and the conversation — a dictionary document gathers dust and then contradicts the files it was meant to align.

## Decision

We optimize for the first few attempts being accepted, net of context tax, on a cold install. That is the question every intake prompt inherits.

How:

1. Expertise is on-demand. A skill or Manual `@` loads when the task matches. It is not an always-on tax.
2. `AGENTS.md` stays a map. The agent reads this file and at most two owners. Disposable thinking stays in `scratch/` and is not mapped, even if they asked.
3. A `/` command or prompt we keep must carry enough intent that a clarifying round is rare. Defaults are armed: the user should not have to know the slash for the path to run.
4. Skills stay model-agnostic. No model name in a skill body. Per-call routing stays with Auto.

A short always-on prior (tens of words) is allowed for one job: maximize Cursor natives, pick one accurate slot (less inferential drift), skip extra probes. It is not a catalog. Other plugins may run alongside; `/unfurnished off` mutes this pack. A terse-output pack is not. See [001-native-first.md](001-native-first.md) for what we refuse to clone.

This does not apply to cheap reversible work: one-line edits, renames, format/lint, throwaway scripts, or a session where the user is already in the loop and will correct immediately. Do not load a skill or a second owner for those.

## Consequences

`.cursor/` stays the small set we ship. New rules, commands, and skills must beat a blank project on few-first-shot rate, not on tokens in the first message. If two owners disagree, delete or fix the stale one — do not add a third file to "clarify." A per-repo `docs/glossary.md` is that third file: names live in the owner that owns the job (and in the code). A dictionary document drifts, goes unused, and invites a remake of design or architecture to "match" it.

Future audits ask: does this raise the probability the first few attempts are accepted, net of tax, on a cold install, on an arbitrary model? Cursor often hides token counts. Score **user turns until accepted** and **extra tool calls** (probes the job did not need). Do not wait on the usage dashboard.
