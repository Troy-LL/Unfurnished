# Owners

What belongs inside each durable file. Open the heading you are writing. Delete the file the day the job dies, and drop the map bullet the same day.

When the user names a thing, write that name next to the fact it names in this file. If two owners could claim the word, ask once, then seat. Even if they asked for a glossary, seat here and say why. Do not mint `docs/glossary.md` or `GLOSSARY.md`. Aliases that already live here sit on the same heading as the fact — not a twin Names file.

## README.md

What it is, who it is for, how to run (install, command, config path, port, health), limits operators hit. Exact strings. Library: install + one usage snippet. Relative links to sibling docs.

## docs/architecture.md

Data flow, processes, sockets, replica counts, one line pointing at the schema file in code. C4 context + containers. Where a model sits, which tools it may call, how retrieval is wired — topology, same as any other process.

A sentence you can regenerate from DDL, OpenAPI, or a test does not belong here.

## docs/design.md

Operator or user UI: poll, badges, empty copy, keyboard, retry, backoff, focus. Omit on a headless service.

## docs/eval.md

Gold command and where it writes, sample floor, scrape (user turns and extra tool calls when tokens are missing), metric prefix, alert files. Omit if tests already fail the booleans. Gold stays rigid. Prompt text lives in `prompts/` as code. Dated scores live in `evals/`.

## docs/decisions/NNN-title.md

Title, Status, Context, Decision (“We will…”), Consequences. One decision. Keep superseded files. Map it iff violating it would look right.

## Contract (in code)

The schema. Comments on the types if a field needs narrative. Architecture points. Agents Read the types file.
