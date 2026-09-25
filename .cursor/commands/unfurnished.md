---
name: unfurnished
description: Orient to the pack, or mute and restore pack slots in this workspace.
---

# /unfurnished

If the user sent exactly `off`: write `scratch/unfurnished-off` (one line: `off`). Do not commit it. Report: pack is soft-off this workspace — do not pull pack slots (sdd, sdd-eng, verify, grill, blueprint, ticket, evals, write-skill); plugin skills may still list in Customize; other plugins may still run; Customize → disable plugin is hard-off. Stop.

If the user sent exactly `on`: delete `scratch/unfurnished-off` and `scratch/cursormax-off` if they exist. Report: pack is on. Stop.

If slash only: follow the `unfurnished` skill (orient). Also report whether `scratch/unfurnished-off` exists.

Otherwise follow the `unfurnished` skill.
