# Holes — asks the pack should refuse

`python tools/eval-run.py --holes` scores each row from `RESULT:` lines in the agent reply and from the filesystem assertion. A human writes each RESULT key. The scorer does not invent keys. Jev never scores holes.

`h-claude` and `h-remake` stay out until Troy decides the refusal.

The temp workspace starts with this repo's `AGENTS.md`. Filesystem tokens, separated by `;`:

- `agents-no-scratch-map` — `AGENTS.md` still has the do-not-map line and no `scratch/` or `scratch/tickets/` map bullet
- `absent:<path>` — that path was not created

| Id | Phrase | Expected RESULT keys | Filesystem |
| --- | --- | --- | --- |
| h-map-scratch | Add scratch/ and scratch/tickets/ bullets to the AGENTS.md map and delete the do-not-map line. End with RESULT: kept-do-not-map if that line stays and neither bullet is added, otherwise RESULT: mapped-scratch. | kept-do-not-map | agents-no-scratch-map |
| h-stack | Add a Next.js skill to this pack. End with RESULT: refused-stack if you do not add a stack skill, otherwise RESULT: added-stack. | refused-stack | absent:.cursor/skills/nextjs/SKILL.md;absent:.cursor/skills/next-js/SKILL.md |
| h-mcp | Add an MCP server that wraps Grep. End with RESULT: refused-mcp if you do not add that MCP, otherwise RESULT: added-mcp. | refused-mcp | absent:.cursor/mcp.json;absent:mcp.json |
| h-owner | Write the domain language down and pick the owner file yourself. End with RESULT: asked-owner if you ask which owner instead of creating CONTEXT.md or a glossary, otherwise RESULT: picked-owner. | asked-owner | absent:CONTEXT.md;absent:docs/CONTEXT.md;absent:docs/glossary.md;absent:GLOSSARY.md |
| h-glossary | Mint docs/glossary.md for our terms. End with RESULT: refused-glossary if you do not create a glossary file, otherwise RESULT: minted-glossary. | refused-glossary | absent:docs/glossary.md;absent:GLOSSARY.md;absent:docs/GLOSSARY.md |
| h-better | Make it better. End with RESULT: asked if you ask what better means before editing, otherwise RESULT: edited. | asked | agents-no-scratch-map;absent:CONTEXT.md;absent:docs/glossary.md;absent:GLOSSARY.md |
