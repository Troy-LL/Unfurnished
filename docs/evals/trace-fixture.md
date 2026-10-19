# Trace

- Dummy: t0-cli / t1-nook
- Arm: routed / always-cheap / always-frontier / soft-off
- Date:
- Model (picker name):
- Cost class (included-cheap / included-standard / included-flagship / api-rate):
- Success: yes / no (dummy Red command exit 0)
- User turns until accepted:
- Tool calls (total):
- Extra tool calls (not Grep/Glob/Read or the named native):
- claims_without_evidence: count of bare done-words in the final message when no qualifying proof follows the last Write or StrReplace (report-only)
- screenshot_before_done: yes / no / N/A
- dev_server_launches:
- EADDRINUSE:
- correction_turns: observational count of user turns that correct the previous turn. A headless dummy has one prompt, so the count is 0. A pass claim needs a scripted 2-turn fixture.
- final_reply_chars: observational character count of the final assistant message. Not a length budget and not a pass field.
- pack_loaded: yes / no
- pack_read: yes / no
- pack_version: release from the table below, or `unknown`
- Tokens in / out (optional; skip if the dashboard is missing):
- Notes (one line):

`soft-off` pairs with `routed` on the same dummy, prompt, and model. The arm writes `scratch/unfurnished-off` (one line: `off`) in the temp workspace before the agent starts. The other arms leave that file absent.

Shipped dummies are only `t0-cli` (red-health) and `t1-nook` (routing). Do not invent `t1-api` or `t3-spec` folders for a plan that still names them.

## Field tags

`pack_read` is `yes` when the session Read `unfurnished-bias.mdc` or a `.cursor/skills/*/SKILL.md`. The off knob does not change this field.

`pack_loaded` is `yes` when `pack_read` is `yes` and `scratch/unfurnished-off` was absent. Otherwise `no`. Soft-off runs with a real pack Read score `pack_loaded: no` and `pack_read: yes`. A Grep of those paths does not count. Plugin attachment alone does not count.

Host limit: the Cursor CLI may still list pack skills while the knob is on. Soft-off is interpretable via `pack_read` (did the agent Read pack text?) plus the knob; the harness cannot force the host to hide skills from the picker.

`pack_version` is the latest row on or before the session date. Two rows on that date, a missing date, or a date before the first row is `unknown`. A later date stays on the last row until a release adds one. These tags are for Troy-local field scoring. This pack does not ship a transcript scraper.

| Version | Release date |
| --- | --- |
| 1.0.0 | 2026-08-16 |
| 1.1.0 | 2026-09-01 |
| 1.2.0 | 2026-09-02 |
| 1.3.0 | 2026-09-02 |
| 1.4.0 | 2026-09-25 |

1.2.0 and 1.3.0 share 2026-09-02 (01:13 +0800 and 16:39 +0800). A date-only session that day is `unknown`.
