# 009: Evidence on done-claims, and Gate 5 in the native Browser

Status: Accepted

## Context

A closeout that says done, fixed, or shipped can be true in the model's head and false on disk. Rendered output can pass lints and tests while the page is wrong. A second browser stack would wrap the native Browser, which [001](001-native-first.md) refuses. The proof clause and the visual check belong in verify, where a done-claim is made.

## Decision

We will:

1. Require each gate line in verify's yield to name its proof in one clause: the command and its exit code, the path, the SHA or PR link, or the native Browser screenshot path. With no proof, that gate line says `not checked`.
2. Keep Gates 1–4 numbered as they are, and add Gate 5 — Visual. When a change alters rendered output, open the page in the native Browser, take a screenshot, compare it to the reference if one exists, and list each visible delta, then fix that delta or name it. When animation code changed, check the start, middle, and end frames. N/A takes one reason, for example "logic-only change". When the native Browser cannot reach the page, say `not checked`.

## Consequences

The check lives in `.cursor/skills/verify/SKILL.md`. Traces record `claims_without_evidence` and `screenshot_before_done` as report-only fields. No Playwright, no Browser MCP, and no wrapper around the native Browser. A field rate from fewer than 20 events is not a pass bar unless a deterministic fixture backs it.
