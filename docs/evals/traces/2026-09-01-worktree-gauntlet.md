# Trace

- Dummy: t0-cli + t1-nook + pack contracts (persona-static)
- Arm: always-cheap (local stdlib unittest / pack-check; no picker)
- Date: 2026-09-01
- Model (picker name): n/a (deterministic probes in git worktrees)
- Cost class: included-cheap
- Success: yes (7/7 probes met their expected outcome)
- User turns until accepted: 1 (this eval request)
- Tool calls (total): 7 (one python process per probe, isolated worktrees)
- Extra tool calls (not Grep/Glob/Read or the named native): 0
- Tokens in / out (optional; skip if the dashboard is missing): skipped
- Notes: Overlay of dirty Unfurnished tree onto detached HEAD worktrees; trees force-removed after.

## Arms (worktrees, then deleted)

| Worktree | Use | Result |
| --- | --- | --- |
| contracts | pack-check 91/91 | success |
| contracts | pack-check --strict-install | success *as expected fail* (cache still `cursormax` @ ab5e568) |
| contracts | pack-check unittest (names / glossary twin) | success 5/5 |
| dummies | t0-cli Red must fail (`hi` ≠ `hello`) | success (red health) |
| dummies | t1-nook Red must fail (`Coming soon.` ≠ `No shelves yet.`) | success (red health) |
| personas | beginner / living owner / glossary / grill-before-disk / one-line / alongside / Debug+MCP / README plan-value | success 12/12 contracts |
| softoff | write `scratch/unfurnished-off`; bias still names path | success |

## Failures

None on the deterministic probes. Live Agent sessions were **not** run in the worktrees (no Cursor transcript, no Write of `design.md`).

`--strict-install` still fails in production until Customize re-import. That is a known install-lag fail, scored as expected.

## Spots for improvement

1. **Live t1-nook** — still need a real Agent turn that patches `page.py` + `docs/design.md` without blank-replace; count turns and extra tool calls from that transcript. n ≥ 3 before promoting 004.
2. **Product-word invoke** — static contracts pass; beginner “glossary” / “completely change the entry” still need a live chat (skill descriptions remain engineer jargon).
3. **Missing dummies** — earlier plans named t1-api / t3-spec; those folders stay absent on purpose (fixture lists only t0-cli / t1-nook).
4. **`/poteto-mode` same turn** — alongside by design; no worktree can prove the agent won’t dual-route. Soft-off is the mute.
5. **Guidebook + plugin double-load** — cannot catch with pack-check; README already forbids it.
6. **Re-import** — cache path remains `…/cursormax/ab5e568…`; Unfurnished 1.2.0 is not what live chats load.
