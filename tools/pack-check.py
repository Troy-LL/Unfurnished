"""Deterministic contracts for the Unfurnished pack. Rerun anytime."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURSOR = ROOT / ".cursor"
PLUGIN = ROOT / ".cursor-plugin" / "plugin.json"

# Slots soft-off / other-pack yield must mute (model-invoked pack work).
SOFT_OFF_SLOTS = (
    "sdd",
    "sdd-eng",
    "verify",
    "grill",
    "blueprint",
    "ticket",
    "evals",
    "write-skill",
)

SKILLS = (
    "blueprint",
    "unfurnished",
    "evals",
    "grill",
    "sdd",
    "sdd-eng",
    "ticket",
    "verify",
    "write-skill",
)

# Knobs only (ADR 008). A skill is already `/<skill>`.
COMMANDS = ("unfurnished", "voice")

RULES = (
    "blast-radius.mdc",
    "comments-belong-in-docs.mdc",
    "reply-shape.mdc",
    "unfurnished-bias.mdc",
    "tdd.mdc",
    "yagni-bias.mdc",
    "yagni.mdc",
)


def text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def check(name: str, ok: bool, detail: str) -> dict:
    return {"id": name, "ok": ok, "detail": detail}


def run_checks(*, strict_install: bool) -> list[dict]:
    rows: list[dict] = []
    bias = text(CURSOR / "rules" / "unfurnished-bias.mdc")
    occasion = text(CURSOR / "skills" / "sdd" / "occasion.md")
    sdd_eng = text(CURSOR / "skills" / "sdd-eng" / "SKILL.md")
    sdd = text(CURSOR / "skills" / "sdd" / "SKILL.md")
    grill = text(CURSOR / "skills" / "grill" / "SKILL.md")
    blueprint = text(CURSOR / "skills" / "blueprint" / "SKILL.md")
    verify = text(CURSOR / "skills" / "verify" / "SKILL.md")
    cm = text(CURSOR / "skills" / "unfurnished" / "SKILL.md")
    agents = text(ROOT / "AGENTS.md")
    adr006 = text(ROOT / "docs" / "decisions" / "006-kernel-not-slot-map.md")
    eval_md = text(ROOT / "docs" / "eval.md")
    t1_task = text(ROOT / "docs" / "evals" / "dummies" / "t1-nook" / "EVAL-TASK.md")
    t1_page = text(ROOT / "docs" / "evals" / "dummies" / "t1-nook" / "page.py")
    t1_design = text(ROOT / "docs" / "evals" / "dummies" / "t1-nook" / "docs" / "design.md")

    rows.append(
        check(
            "bias-kernel-not-slot-map",
            all(
                p not in bias
                for p in (
                    "Kickoff →",
                    "File on disk",
                    "No checkable done-line",
                    "Mint a durable",
                    "Multi-file done",
                    "Ship →",
                )
            )
            and "Docs → sdd" not in bias
            and "do not dump the catalog" in bias.lower()
            and "workflow runtime" in bias.lower(),
            "always-on is a kernel; slot routing is not in the prior",
        )
    )
    rows.append(
        check(
            "skills-hold-slot-triggers",
            "no checkable done-line" in grill.lower()
            and "kickoff" in blueprint.lower()
            and "file already on disk" in sdd_eng.lower()
            and "adr only when" in " ".join(sdd.split()).lower()
            and "multi-file" in verify.lower(),
            "skill descriptions still pull the slots the kernel dropped",
        )
    )
    rows.append(
        check(
            "adr-006-kernel",
            "We will" in adr006
            and "006-kernel-not-slot-map.md" in agents
            and "workflow runtime" in adr006.lower(),
            "006 is mapped; always-on is not a frozen slot map",
        )
    )
    hooks = json.loads(text(CURSOR / "hooks.json") or "{}")
    hook_cmds = [h.get("command", "") for ev in (hooks.get("hooks") or {}).values() for h in ev]
    rows.append(
        check(
            "fence-hook-wired",
            (CURSOR / "hooks" / "fence.py").is_file()
            and "preToolUse" in (hooks.get("hooks") or {})
            and "beforeShellExecution" in (hooks.get("hooks") or {})
            and all("fence.py" in c for c in hook_cmds)
            and "007-hooks-for-hard-fences.md" in agents,
            "ADR 007: fence.py runs on Write and on git add/commit; 007 mapped",
        )
    )
    cmd_dir = sorted(p.stem for p in (CURSOR / "commands").glob("*.md"))
    # A command that shares a skill's name must carry state (a scratch knob); otherwise `/<skill>` already does it.
    twins = [c for c in cmd_dir if c in SKILLS and "scratch/" not in text(CURSOR / "commands" / f"{c}.md")]
    rows.append(
        check(
            "no-command-twins",
            cmd_dir == sorted(COMMANDS)
            and not twins
            and not (CURSOR / "skills" / "thermonuclear").exists()
            and "thermonuclear" not in bias
            and "008-no-command-twins.md" in agents,
            f"ADR 008: commands are knobs only; twins={twins}",
        )
    )
    phrasings = text(ROOT / "docs" / "evals" / "phrasings.md")
    rows.append(
        check(
            "eval-runs-not-strings",
            (ROOT / "tools" / "eval-run.py").is_file()
            and "eval-run" in eval_md
            and "phrasings" in eval_md
            and sum(1 for line in phrasings.splitlines() if line.startswith("| ") and "|" in line[2:]) >= 10,
            "eval.md points at the headless runner and a phrasing fixture with rows",
        )
    )
    rows.append(
        check(
            "bias-soft-off-slots",
            all(s in bias for s in SOFT_OFF_SLOTS),
            "soft-off lists every model-invoked pack slot",
        )
    )
    rows.append(
        check(
            "bias-alongside",
            "alongside" in bias.lower() and "poteto" not in bias.lower(),
            "bias sits beside other plugins; does not name poteto",
        )
    )
    rows.append(
        check(
            "bias-scratch-even-if-asked",
            "even if they asked" in bias.lower()
            and "scratch/" in bias
            and "do-not-map" in bias.lower().replace(" ", "").replace("`", ""),
            "always-on forbids mapping scratch even if they asked",
        )
    )
    rows.append(
        check(
            "bias-yield-attached",
            "attached another pack" in bias.lower() and "poteto" not in bias.lower(),
            "this-turn attached skill skips pack slots; does not name poteto",
        )
    )
    rows.append(
        check(
            "bias-do-not-wrap",
            "do not wrap" in bias.lower() and "do not wrap" in cm.lower(),
            "yielded turn does not wrap the other pack's tools",
        )
    )
    rows.append(
        check(
            "bias-map-before-grep",
            "before a repo-wide" in bias.lower()
            and "do not open" in bias.lower()
            and "do not offer" in bias.lower()
            and "do not pull tdd" in bias.lower(),
            "always-on re-reads AGENTS.md before tree search; no tdd on attached pack",
        )
    )
    rows.append(
        check(
            "sdd-eng-load-map",
            "map.md" in sdd_eng.lower() and "AGENTS.md" in sdd_eng,
            "sdd-eng reads map.md when the owner is AGENTS.md",
        )
    )
    rows.append(
        check(
            "bias-maximize-natives",
            "grep" in bias.lower()
            and "extra-probe" in bias.lower()
            and "mcp" in bias.lower(),
            "always-on maximizes Cursor natives and skips extra probes and MCP clones",
        )
    )
    rows.append(
        check(
            "occasion-merge",
            "If the path already exists" in occasion
            and "full-file replace" in occasion.lower()
            and "**Write the owner.**" not in occasion,
            "occasion seats facts; bans full-file replace; no Write-the-owner step title",
        )
    )
    rows.append(
        check(
            "sdd-eng-disk-owner",
            "file already on disk" in sdd_eng.lower()
            and "Patch that owner" in sdd_eng
            and "full-file replace fails" in sdd_eng.lower(),
            "sdd-eng patches owners on disk; bans full-file replace",
        )
    )
    rows.append(
        check(
            "sdd-hands-off-existing",
            ("matching owner already" in sdd.lower() or "exists on disk" in sdd.lower())
            and "glossary / names dump" in sdd.lower(),
            "sdd hands living owners to sdd-eng; glossary is not a missing owner",
        )
    )
    rows.append(
        check(
            "bias-patch-living",
            "patch in place" in bias.lower() and "blank-replace" in bias.lower(),
            "always-on bias bans blank-replace of living durable files",
        )
    )
    distill = text(CURSOR / "skills" / "sdd" / "distill.md")
    owners = text(CURSOR / "skills" / "sdd" / "owners.md")
    adr002 = text(ROOT / "docs" / "decisions" / "002-first-shot-efficiency.md")
    rows.append(
        check(
            "distill-no-full-replace",
            "full-file replace" in distill.lower() and "patch in place" in distill.lower(),
            "distill merges non-empty owners with patches",
        )
    )
    rows.append(
        check(
            "no-glossary-occasion",
            "glossary" in occasion.lower()
            and "twin" in occasion.lower()
            and "| `docs/glossary.md`" not in occasion
            and "| docs/glossary.md" not in occasion,
            "occasion treats a glossary as a twin, not an owner",
        )
    )
    rows.append(
        check(
            "seat-user-name",
            "names a thing" in owners.lower()
            and "names a thing" in occasion.lower()
            and "glossary.md" in owners.lower(),
            "owners + occasion seat the user's name in the owner; no glossary file",
        )
    )
    rows.append(
        check(
            "ask-once-name",
            "ask once" in owners.lower() or "ask once" in occasion.lower(),
            "ambiguous names: one question, then seat",
        )
    )
    rows.append(
        check(
            "distill-fold-definitions",
            "glossary" in distill.lower() or "definitions" in distill.lower(),
            "distill folds a dump Definitions/Glossary heading into owners",
        )
    )
    rows.append(
        check(
            "sdd-eng-seat-name",
            "names a thing" in sdd_eng.lower() or "seat the" in sdd_eng.lower(),
            "sdd-eng seats a new name in the owner",
        )
    )
    rows.append(
        check(
            "002-no-glossary-twin",
            "glossary" in adr002.lower() and "third file" in adr002.lower(),
            "002 rejects a glossary as a third clarifying file",
        )
    )
    rows.append(
        check(
            "002-always-on-natives",
            "always-on" in adr002.lower()
            and ("natives" in adr002.lower() or "inferential" in adr002.lower()),
            "002 states always-on is for natives and accurate slots",
        )
    )
    rows.append(
        check(
            "pack-no-mint-glossary",
            "do not mint" in owners.lower() and "glossary.md" in owners.lower(),
            "owners.md forbids minting a glossary file",
        )
    )
    rows.append(
        check(
            "map-scratch-even-if-asked",
            "even if they asked" in text(CURSOR / "skills" / "sdd" / "map.md").lower()
            and "scratch/tickets" in text(CURSOR / "skills" / "sdd" / "map.md").lower()
            and "even if they asked" in sdd_eng.lower()
            and "do not map scratch" in sdd_eng.lower(),
            "scratch stays unmapped even if they asked",
        )
    )
    reference = text(CURSOR / "skills" / "unfurnished" / "reference.md")
    rows.append(
        check(
            "catalog-living-owner",
            "living owner" in reference.lower() and "blank-replace" in reference.lower(),
            "catalog states living owners merge; never blank-replace",
        )
    )
    rows.append(
        check(
            "unfurnished-not-pstack",
            "not a pstack" in cm.lower() or "poteto-mode orchestra" in cm.lower(),
            "unfurnished states it is not a pstack orchestra",
        )
    )
    rows.append(
        check(
            "unfurnished-coexist",
            "alongside other" in cm.lower(),
            "unfurnished skill runs alongside other packs",
        )
    )
    rows.append(
        check(
            "unfurnished-no-sdd-pull",
            "already the slot" in cm.lower() or "do not use when /sdd" in cm.lower(),
            "unfurnished does not pull on every sdd-eng job",
        )
    )
    rows.append(
        check(
            "agents-maps-eval",
            "docs/eval.md" in agents,
            "AGENTS.md bullets docs/eval.md",
        )
    )
    rows.append(
        check(
            "eval-t1-nook",
            "t1-nook" in eval_md,
            "eval.md names t1-nook as qualifying dummy",
        )
    )
    rows.append(
        check(
            "eval-session-tools",
            "tool call" in eval_md.lower()
            and ("turn" in eval_md.lower() or "session" in eval_md.lower()),
            "eval.md scores session length and extra tool calls when tokens are missing",
        )
    )
    rows.append(
        check(
            "eval-restore-dummy",
            "restore" in eval_md.lower() and "coming soon" in eval_md.lower(),
            "eval.md restores t1-nook to red after a guidebook landing probe",
        )
    )
    rows.append(
        check(
            "t1-nook-red-start",
            'EMPTY = "Coming soon."' in t1_page and "Coming soon." in t1_design,
            "t1-nook starts red on Coming soon.",
        )
    )
    rows.append(
        check(
            "t1-task-no-keep-leak",
            "Keep every other line" not in t1_task and "keep every" not in t1_task.lower(),
            "EVAL-TASK does not leak the keep-the-file answer",
        )
    )

    for name in SKILLS:
        p = CURSOR / "skills" / name / "SKILL.md"
        rows.append(check(f"skill-{name}", p.is_file(), str(p)))
    for name in COMMANDS:
        p = CURSOR / "commands" / f"{name}.md"
        rows.append(check(f"cmd-{name}", p.is_file(), str(p)))
    for name in RULES:
        p = CURSOR / "rules" / name
        rows.append(check(f"rule-{name}", p.is_file(), str(p)))

    plugin = json.loads(text(PLUGIN) or "{}")
    rows.append(
        check(
            "plugin-id-unfurnished",
            plugin.get("name") == "unfurnished",
            str(plugin.get("name")),
        )
    )
    rows.append(
        check(
            "plugin-display-unfurnished",
            plugin.get("displayName") == "Unfurnished",
            str(plugin.get("displayName")),
        )
    )
    rows.append(
        check(
            "brand-unfurnished",
            text(ROOT / "README.md").startswith("# Unfurnished"),
            "README title is Unfurnished",
        )
    )
    rows.append(
        check(
            "bias-soft-off-path",
            "unfurnished-off" in bias
            and "cursormax-off" in bias
            and "Grep" in bias,
            "soft-off honors unfurnished-off and cursormax-off",
        )
    )
    cmd_list = plugin.get("commands") or []
    rule_list = plugin.get("rules") or []
    rows.append(
        check(
            "plugin-hooks",
            plugin.get("hooks") == "./.cursor/hooks.json" and len(cmd_list) == len(COMMANDS),
            "plugin ships the fence hook and only the two knobs",
        )
    )
    for name in COMMANDS:
        needle = f"./.cursor/commands/{name}.md"
        rows.append(
            check(f"plugin-cmd-{name}", needle in cmd_list, needle)
        )
    for name in RULES:
        needle = f"./.cursor/rules/{name}"
        rows.append(check(f"plugin-rule-{name}", needle in rule_list, needle))

    # Persona / description smoke: model-invoked skills have a use trigger.
    for name in ("sdd", "sdd-eng", "verify", "grill"):
        body = text(CURSOR / "skills" / name / "SKILL.md")
        rows.append(
            check(
                f"desc-{name}",
                body.startswith("---")
                and ("Use when" in body or "use when" in body.lower()),
                "frontmatter description present",
            )
        )

    cache_roots = [
        Path.home() / ".cursor" / "plugins" / "cache" / "troy-ll-unfurnished",
        Path.home() / ".cursor" / "plugins" / "cache" / "troy-ll-cursor-maxxing",
    ]
    stale = False
    detail = "no cache"
    caches: list[Path] = []
    for cache in cache_roots:
        if cache.is_dir():
            caches.extend(cache.glob("unfurnished/*/"))
            caches.extend(cache.glob("cursormax/*/"))
    if caches:
        newest = max(caches, key=lambda p: p.stat().st_mtime)
        c_bias = text(newest / ".cursor" / "rules" / "unfurnished-bias.mdc") or text(
            newest / ".cursor" / "rules" / "cursormax-bias.mdc"
        )
        stale = (
            "cursor-maxxing" in str(newest).replace("\\", "/").lower()
            or newest.parent.name != "unfurnished"
            or "Docs → sdd" in c_bias
            or "Kickoff →" in c_bias
            or "File on disk" in c_bias
        )
        detail = str(newest)
    if strict_install:
        rows.append(
            check(
                "install-matches-repo",
                not stale,
                f"plugin cache must match repo overlays ({detail})",
            )
        )
    else:
        rows.append(
            check(
                "install-lag-noted",
                True,
                f"stale={stale} path={detail} (warn only; re-import to clear)",
            )
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--strict-install",
        action="store_true",
        help="Fail when the installed plugin cache still teaches Docs → sdd",
    )
    args = ap.parse_args()
    rows = run_checks(strict_install=args.strict_install)
    failed = [r for r in rows if not r["ok"]]
    print(json.dumps({"failed": failed, "n": len(rows), "pass": len(rows) - len(failed)}, indent=2))
    return 1 if failed else 0


class TestT1NookRed(unittest.TestCase):
    def test_starts_red(self) -> None:
        import importlib.util

        page_path = ROOT / "docs" / "evals" / "dummies" / "t1-nook" / "page.py"
        spec = importlib.util.spec_from_file_location("t1_page", page_path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.EMPTY, "Coming soon.")


class TestNameSeating(unittest.TestCase):
    """Fail cases: minting a glossary, asking forever, seating in the wrong owner."""

    def _cursor_text(self) -> str:
        parts = []
        for p in (ROOT / ".cursor").rglob("*"):
            if p.suffix in {".md", ".mdc"} and p.is_file():
                parts.append(p.read_text(encoding="utf-8"))
        return "\n".join(parts)

    def test_occasion_table_has_no_glossary_owner(self) -> None:
        occasion = (ROOT / ".cursor" / "skills" / "sdd" / "occasion.md").read_text(
            encoding="utf-8"
        )
        in_table = False
        for line in occasion.splitlines():
            if line.startswith("| Job"):
                in_table = True
                continue
            if in_table and line.startswith("|") and "glossary" in line.lower():
                self.fail(f"occasion table minted a glossary owner: {line}")
            if in_table and not line.startswith("|"):
                in_table = False

    def test_no_skill_use_when_glossary(self) -> None:
        for p in (ROOT / ".cursor" / "skills").glob("*/SKILL.md"):
            body = p.read_text(encoding="utf-8")
            head = body.split("---", 2)
            desc = head[1] if len(head) > 2 else ""
            self.assertNotIn(
                "glossary",
                desc.lower(),
                f"{p.name} description must not pull on glossary",
            )

    def test_create_glossary_only_as_forbid(self) -> None:
        blob = self._cursor_text().lower()
        for needle in (
            "create `docs/glossary.md`",
            "create docs/glossary.md",
            "write docs/glossary.md",
            "mint docs/glossary.md",
        ):
            if needle in blob:
                self.assertIn(
                    "do not mint",
                    blob,
                    f"pack mentions {needle} without a do-not-mint rule",
                )


    def test_persona_fail_matrix(self) -> None:
        owners = (ROOT / ".cursor" / "skills" / "sdd" / "owners.md").read_text(
            encoding="utf-8"
        ).lower()
        occasion = (ROOT / ".cursor" / "skills" / "sdd" / "occasion.md").read_text(
            encoding="utf-8"
        ).lower()
        distill = (ROOT / ".cursor" / "skills" / "sdd" / "distill.md").read_text(
            encoding="utf-8"
        ).lower()
        sdd_eng = (ROOT / ".cursor" / "skills" / "sdd-eng" / "SKILL.md").read_text(
            encoding="utf-8"
        ).lower()
        adr002 = (ROOT / "docs" / "decisions" / "002-first-shot-efficiency.md").read_text(
            encoding="utf-8"
        ).lower()
        # A: "we need a glossary" → not an occasion row
        self.assertNotIn("| `docs/glossary.md`", occasion)
        self.assertIn("a glossary is a twin", occasion)
        # B: user word for UI / topology → seat in that owner, ask once if both
        self.assertIn("names a thing", owners)
        self.assertIn("ask once", owners)
        # C: dump with Definitions heading → fold, don't mint
        self.assertIn("definitions", distill)
        self.assertIn("do not mint", distill)
        # D: feature rename during implement → sdd-eng seats synonym
        self.assertIn("names a thing", sdd_eng)
        # E: glossary as third clarifying file → 002
        self.assertIn("glossary.md", adr002)
        self.assertIn("third file", adr002)
        owners = (ROOT / ".cursor" / "skills" / "sdd" / "owners.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("even if they asked for a glossary", owners.lower())
        sdd = (ROOT / ".cursor" / "skills" / "sdd" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("glossary / names dump is not a missing owner", sdd.lower())
        mapping = (ROOT / ".cursor" / "skills" / "sdd" / "map.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("do not map a glossary", mapping.lower())
        # F: "put scratch in AGENTS.md" → still unmapped, even if they asked
        self.assertIn("even if they asked", mapping.lower())
        self.assertIn("scratch/tickets", mapping.lower())
        self.assertIn("even if they asked", sdd_eng)
        self.assertIn("do not map scratch", sdd_eng)

    def test_live_mitigations(self) -> None:
        """Failures from playground chat 1338ba42: map scratch, fusion, extra-probe."""
        bias = (ROOT / ".cursor" / "rules" / "unfurnished-bias.mdc").read_text(
            encoding="utf-8"
        ).lower()
        sdd_eng = (ROOT / ".cursor" / "skills" / "sdd-eng" / "SKILL.md").read_text(
            encoding="utf-8"
        ).lower()
        cm = (ROOT / ".cursor" / "skills" / "unfurnished" / "SKILL.md").read_text(
            encoding="utf-8"
        ).lower()
        mapping = (ROOT / ".cursor" / "skills" / "sdd" / "map.md").read_text(
            encoding="utf-8"
        ).lower()
        # Always-on must fire without /sdd: do not bullet scratch; do not strip the prior
        self.assertIn("scratch/", bias)
        self.assertIn("even if they asked", bias)
        self.assertIn("do not delete", bias)
        self.assertIn("do-not-map", bias.replace(" ", "").replace("`", ""))
        # 006: kernel, not an if-then slot map
        self.assertNotIn("kickoff →", bias)
        self.assertNotIn("file on disk", bias)
        self.assertNotIn("no checkable done-line", bias)
        self.assertIn("workflow runtime", bias)
        # Attached other orchestra this turn → skip slots; do not name poteto
        self.assertIn("attached another pack", bias)
        self.assertNotIn("poteto", bias)
        # Living AGENTS.md edits load map.md
        self.assertIn("agents.md", sdd_eng)
        self.assertIn("map.md", sdd_eng)
        self.assertIn("do not delete", mapping or sdd_eng)
        # Coexistence: skip slots when another pack's skill is attached
        self.assertIn("attached another pack", cm)
        # Live 31023fcd: re-read AGENTS.md before tree search; honor skip lines; no rewrite offer
        self.assertIn("before a repo-wide", bias)
        self.assertIn("do not open", bias)
        self.assertIn("do not offer", bias)
        self.assertIn("do not pull tdd", bias)
        self.assertIn("do not wrap", bias)
        self.assertIn("do not wrap", cm)


class TestFence(unittest.TestCase):
    """ADR 007: the two hard fences run as hooks, not prose."""

    FENCE = CURSOR / "hooks" / "fence.py"

    def fence(self, payload: dict, cwd: Path = ROOT) -> dict:
        proc = subprocess.run(
            [sys.executable, str(self.FENCE)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        self.assertIn(proc.returncode, (0, 2), proc.stderr)
        return json.loads(proc.stdout or "{}")

    def write(self, path: str, cwd: Path = ROOT) -> dict:
        return self.fence(
            {
                "hook_event_name": "preToolUse",
                "tool_name": "Write",
                "tool_input": {"path": path, "contents": "x"},
                "cwd": str(cwd),
                "workspace_roots": [str(cwd)],
            },
            cwd,
        )

    def shell(self, command: str, cwd: Path) -> dict:
        return self.fence(
            {"hook_event_name": "beforeShellExecution", "command": command, "cwd": str(cwd)},
            cwd,
        )

    def test_write_living_owner_denied(self) -> None:
        for p in ("README.md", "AGENTS.md", "docs/eval.md", "docs/decisions/001-native-first.md"):
            out = self.write(str(ROOT / p))
            self.assertEqual(out["permission"], "deny", p)
            self.assertIn("patch in place", out["agent_message"].lower())

    def test_write_missing_or_non_owner_allowed(self) -> None:
        self.assertEqual(self.write(str(ROOT / "docs" / "decisions" / "999-nope.md"))["permission"], "allow")
        self.assertEqual(self.write(str(ROOT / "tools" / "pack-check.py"))["permission"], "allow")
        self.assertEqual(self.write("scratch/notes.md")["permission"], "allow")

    def test_git_scratch_fence(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            git = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
            git("init", "-q")
            git("config", "user.email", "t@t")
            git("config", "user.name", "t")
            (repo / "scratch").mkdir()
            (repo / "scratch" / "a.md").write_text("x", encoding="utf-8")
            (repo / "ok.md").write_text("x", encoding="utf-8")
            self.assertEqual(self.shell("git add scratch/a.md", repo)["permission"], "deny")
            self.assertEqual(self.shell("git add .", repo)["permission"], "deny")
            self.assertEqual(self.shell("git add ok.md", repo)["permission"], "allow")
            git("add", "-f", "scratch/a.md")
            self.assertEqual(self.shell('git commit -m "x"', repo)["permission"], "deny")
            git("reset", "-q", "scratch/a.md")
            git("add", "ok.md")
            self.assertEqual(self.shell('git commit -m "x"', repo)["permission"], "allow")
            (repo / ".gitignore").write_text("scratch/\n", encoding="utf-8")
            self.assertEqual(self.shell("git add .", repo)["permission"], "allow")
            self.assertEqual(self.shell("git status", repo)["permission"], "allow")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "unittest":
        sys.argv = [sys.argv[0]]
        raise SystemExit(unittest.main())
    raise SystemExit(main())
