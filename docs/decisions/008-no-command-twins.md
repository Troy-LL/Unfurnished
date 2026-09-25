# 008: No command twins of skills

Status: Accepted

## Context

Eleven files in `.cursor/commands/` read "Follow the `<name>` skill." Cursor already invokes a skill by `/<name>`; the README said so. A command that only points at a skill is a wrapper of a native, which [001](001-native-first.md) refuses, and it doubles the surface a cold install has to read ([002](002-first-shot-efficiency.md)). `thermonuclear` was the same shape one level up: an in-session review checklist whose own description avoided the Bugbot and Security Review Task types Cursor ships.

## Decision

We will ship a command only when it is a knob with state or arguments a skill cannot carry: `/unfurnished on|off`, `/voice`. Every skill is reachable as `/<skill>`; we will not add a command that restates it. Adversarial review is the `bugbot` and `security-review` Task types (or `/create-subagent`); we will not ship a review skill of our own.

## Consequences

`.cursor/commands/` holds two knobs. `thermonuclear` is deleted; `unfurnished-bias`, README, and `reference.md` point at Task. `pack-check.py` fails if a command file is a skill twin.
