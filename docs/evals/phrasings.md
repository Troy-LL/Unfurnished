# Phrasings — plain asks → which skill should pull

After [006](../decisions/006-kernel-not-slot-map.md) the skill descriptions are the routing. This fixture is what `python tools/eval-run.py --phrasings` checks: a run passes when the agent Reads `skills/<expected>/SKILL.md` (or Reads none when `expected` is `none`) before its first edit. Score pass rate per row; a row under 2/3 means that skill's description is the bug, not the phrase.

Plain words on purpose. Engineers do not say "occasion an owner."

| Phrase | Expected |
| --- | --- |
| start a new cli project for me, python or go, you pick | blueprint |
| i want this to be better but i'm not sure what better means yet | grill |
| write the readme and an agents file for this repo | sdd |
| add a glossary page for our terms | sdd |
| completely change the entry copy on the shelves page | sdd-eng |
| the empty shelf text is wrong, fix it | sdd-eng |
| fix the login bug, no idea which file, no test covers it | ticket |
| are we done? make sure everything still runs | verify |
| deploy check before i push this to prod | none |
| the chat got summarized, where were we | none |
| build a test suite for our rag prompt outputs | evals |
| make me a skill that does x | write-skill |
| rename foo to bar in page.py | none |
| what does this pack do | unfurnished |
