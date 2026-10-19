"""Headless eval runs for docs/eval.md. Needs the Cursor CLI `agent` on PATH.

  python tools/eval-run.py --dummy t1-nook --arm always-cheap --model <slug> --n 3
  python tools/eval-run.py --dummy t1-nook --arm routed --n 3           # no --model = Auto
  python tools/eval-run.py --dummy t1-nook --arm soft-off --n 3         # same prompt; writes the off knob
  python tools/eval-run.py --phrasings                                  # docs/evals/phrasings.md
  python tools/eval-run.py --holes                                      # docs/evals/holes.md

Each dummy run: copy the dummy to a temp dir, run the agent with this repo as --plugin-dir,
run the dummy's Red command, check the design-keep rule, write one trace file from
docs/evals/trace-fixture.md. Turns are 1 by construction (one prompt); tool calls are
counted from stream-json events. claims_without_evidence, screenshot_before_done,
dev_server_launches, the EADDRINUSE count, correction_turns, and final_reply_chars are
report-only. --arm soft-off writes scratch/unfurnished-off in that temp workspace.
Jev never scores holes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
DUMMIES = ROOT / "docs" / "evals" / "dummies"
TRACES = ROOT / "docs" / "evals" / "traces"
ARMS = ("routed", "always-cheap", "always-frontier", "soft-off")
_RELEASE_DATES = (
    (dt.date(2026, 8, 16), "1.0.0"),
    (dt.date(2026, 9, 1), "1.1.0"),
    (dt.date(2026, 9, 2), "1.2.0"),
    (dt.date(2026, 9, 2), "1.3.0"),
    (dt.date(2026, 9, 25), "1.4.0"),
)
_PACK_SKILL = re.compile(r"(?:^|/)\.cursor/skills/[^/]+/SKILL\.md$")
NATIVE = {"Read", "Grep", "Glob", "Shell", "StrReplace", "Write"}
RED = re.compile(r"^Red:\s*`([^`]+)`", re.M)
DONE_WORD = re.compile(r"\b(?:works now|done|fixed|verified|passed|pushed|shipped)\b", re.I)
PR_URL = re.compile(r"https://github\.com/[^\s/]+/[^\s/]+/pull/\d+")
_SCRATCH_BULLET = re.compile(r"^`?scratch/(?:tickets/)?`?(?:\s|$)")
_TOOL_KEYS = (
    ("shellToolCall", "Shell"),
    ("readLintsToolCall", "ReadLints"),
    ("writeToolCall", "Write"),
    ("strReplaceToolCall", "StrReplace"),
    ("browserTakeScreenshotToolCall", "browser_take_screenshot"),
    ("readToolCall", "Read"),
)


class Call(NamedTuple):
    name: str
    command: str = ""
    exit_code: int | None = None
    output: str = ""
    path: str = ""


_UI_FILE = re.compile(r"\.(?:css|tsx|html|svg)$", re.I)
_DEV_SERVER = re.compile(
    r"(?:^|[;&|`(]\s*)(?:"
    r"(?:npm|pnpm|yarn|bun)(?:\s+run)?\s+(?:dev|start)\b"
    r"|npx\s+(?:next|vite|nuxt|astro)\b"
    r"|(?:next|nuxt|astro)\s+dev\b"
    r"|vite(?:\s+dev)?(?=\s|$)"
    r"|(?:flask|gunicorn|hypercorn)\s+run\b"
    r"|uvicorn\b"
    r"|python(?:3)?\s+-m\s+http\.server\b"
    r"|php\s+-S\b"
    r"|rails\s+s(?:erver)?\b"
    r")",
    re.I | re.M,
)


def _norm_tool(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 80):start]
    cut = re.search(r"[.!?]\s*([^.!?]*)$", prefix)
    clause = cut.group(1) if cut else prefix
    if "," in clause:
        clause = clause.rsplit(",", 1)[-1]
    tokens = re.findall(r"[A-Za-z']+", clause.lower())
    if any(t.endswith("n't") or t in {"not", "never", "cannot", "without"} for t in tokens[-4:]):
        return True
    return bool(tokens) and tokens[-1] == "no"


def _done_words(message: str) -> int:
    return sum(1 for m in DONE_WORD.finditer(message) if not _negated(message, m.start()))


def _qualifying(call: Call) -> bool:
    name = _norm_tool(call.name)
    if name == "readlints":
        return True
    if name == "browsertakescreenshot":
        return True
    if PR_URL.search(call.output) and call.exit_code in (0, None):
        return True
    if name != "shell":
        return False
    if call.exit_code == 0:
        return True
    return bool(
        call.exit_code is None
        and re.search(r"\bgit push\b", call.command)
        and re.search(r"->\s+\S+", call.output)
    )


def _is_write(call: Call) -> bool:
    return _norm_tool(call.name) in {"write", "strreplace"}


def _is_browser_screenshot(call: Call) -> bool:
    return _norm_tool(call.name) == "browsertakescreenshot"


def _ui_edit(call: Call) -> bool:
    if not _is_write(call):
        return False
    clean = call.path.split("?", 1)[0].replace("\\", "/").rstrip("/")
    return bool(_UI_FILE.search(clean))


def screenshot_before_done(calls: list[Call]) -> str:
    """yes when a native Browser screenshot follows the last .css/.tsx/.html/.svg edit; else no. N/A if none of those changed."""
    last_ui = -1
    for i, call in enumerate(calls):
        if _ui_edit(call):
            last_ui = i
    if last_ui < 0:
        return "N/A"
    if any(_is_browser_screenshot(call) for call in calls[last_ui + 1:]):
        return "yes"
    return "no"


def dev_server_launches(calls: list[Call]) -> int:
    """How many dev-server start commands appear in Shell calls."""
    return sum(
        len(_DEV_SERVER.findall(call.command))
        for call in calls
        if _norm_tool(call.name) == "shell"
    )


def eaddrinuse_count(calls: list[Call]) -> int:
    return sum(call.output.count("EADDRINUSE") for call in calls if _norm_tool(call.name) == "shell")


def trace_field_names() -> tuple[str, ...]:
    return (
        "claims_without_evidence",
        "screenshot_before_done",
        "dev_server_launches",
        "EADDRINUSE",
        "correction_turns",
        "final_reply_chars",
        "pack_loaded",
        "pack_version",
    )


def pack_version(when: dt.date | None) -> str:
    """Latest release on or before when. Two rows on that day, or no row, is unknown."""
    if type(when) is not dt.date:
        return "unknown"
    if sum(day == when for day, _name in _RELEASE_DATES) > 1:
        return "unknown"
    found = "unknown"
    for day, name in _RELEASE_DATES:
        if day <= when:
            found = name
        else:
            break
    return found


def pack_loaded(calls: list[Call], workspace: Path) -> str:
    """yes when a Read hit unfurnished-bias or a pack SKILL.md and the off knob is absent."""
    if (workspace / "scratch" / "unfurnished-off").exists():
        return "no"
    for call in calls:
        if _norm_tool(call.name) != "read":
            continue
        path = call.path.replace("\\", "/")
        if path.endswith("unfurnished-bias.mdc") or _PACK_SKILL.search(path):
            return "yes"
    return "no"


def seed_workspace(src: Path, dest: Path, arm: str) -> None:
    shutil.copytree(src, dest)
    subprocess.run(["git", "init", "-q"], cwd=dest, check=False)
    if arm == "soft-off":
        knob = dest / "scratch" / "unfurnished-off"
        knob.parent.mkdir(parents=True, exist_ok=True)
        knob.write_text("off\n", encoding="utf-8")


def claims_without_evidence(message: str, calls: list[Call]) -> int:
    """Count bare done-words when no qualifying call follows the last Write or StrReplace."""
    last_write = -1
    for i, call in enumerate(calls):
        if _is_write(call):
            last_write = i
    evidenced = bool(PR_URL.search(message)) or any(
        _qualifying(call) for i, call in enumerate(calls) if i > last_write
    )
    if evidenced:
        return 0
    return _done_words(message)


def agents_scratch_fence(agents: str) -> bool:
    """True when the do-not-map line stays and no scratch map bullet was added."""
    folded = agents.lower().replace("`", "").replace("-", " ")
    if "do not map" not in folded:
        return False
    for line in agents.splitlines():
        body = line.strip()
        if not body or body[0] not in "-*":
            continue
        if _SCRATCH_BULLET.match(body[1:].strip()):
            return False
    return True


def result_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"RESULT:\s*(.*)$", line.strip())
        if not match:
            continue
        keys.update(part for part in re.split(r"[\s,]+", match.group(1).strip()) if part)
    return keys


def filesystem_holds(workspace: Path, spec: str) -> bool:
    tokens = [token.strip() for token in spec.split(";") if token.strip()]
    if not tokens:
        return False
    for token in tokens:
        if token == "agents-no-scratch-map":
            path = workspace / "AGENTS.md"
            if not path.is_file() or not agents_scratch_fence(path.read_text(encoding="utf-8")):
                return False
            continue
        if token.startswith("absent:"):
            rel = token[len("absent:"):].strip()
            if not rel or (workspace / rel).exists():
                return False
            continue
        return False
    return True


def score_hole(reply: str, workspace: Path, expected: str, filesystem: str) -> tuple[bool, str]:
    """Score one hole from RESULT lines and a filesystem assertion. No judge."""
    wanted = [key for key in expected.split() if key]
    found = result_keys(reply)
    if not wanted or any(key not in found for key in wanted):
        return False, f"RESULT wanted {wanted} found {sorted(found)}"
    if not filesystem_holds(workspace, filesystem):
        return False, f"filesystem failed: {filesystem}"
    return True, "ok"


def hole_rows(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in {"Id", "---"} or set(cells[0]) <= {"-", " "}:
            continue
        rows.append({
            "id": cells[0],
            "phrase": cells[1],
            "result": cells[2],
            "filesystem": cells[3],
        })
    return rows


def _as_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    if isinstance(value, int):
        return value
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return None


def _call_from_mapping(name: str, args: object, result: object) -> Call:
    command = ""
    path = ""
    if isinstance(args, dict):
        command = str(args.get("command") or args.get("cmd") or "")
        path = str(args.get("path") or args.get("file_path") or args.get("filePath") or "")
    exit_code = None
    chunks: list[str] = []
    if isinstance(result, dict):
        exit_code = _as_int(result.get("exitCode", result.get("exit_code", result.get("code"))))
        for key in ("stdout", "output", "content", "stderr"):
            value = result.get(key)
            if isinstance(value, str) and value:
                chunks.append(value)
    return Call(name=name, command=command, exit_code=exit_code, output="\n".join(chunks), path=path)


def call_from_tool_event(event: dict) -> Call | None:
    if event.get("type") not in {"tool_call", "tool_use"}:
        return None
    if event.get("type") == "tool_call" and event.get("subtype") not in {None, "completed"}:
        return None
    tool_call = event.get("tool_call") if isinstance(event.get("tool_call"), dict) else event
    if not isinstance(tool_call, dict):
        return None
    for key, name in _TOOL_KEYS:
        block = tool_call.get(key)
        if isinstance(block, dict):
            return _call_from_mapping(
                name,
                block.get("args") or block.get("input") or {},
                block.get("result") or {},
            )
    name = str(tool_call.get("name") or event.get("name") or "")
    if not name:
        return None
    args = tool_call.get("args") or tool_call.get("input") or event.get("input") or {}
    result = tool_call.get("result") or event.get("result") or {}
    return _call_from_mapping(name, args if isinstance(args, dict) else {}, result if isinstance(result, dict) else {})


def calls_from_events(events: list[dict]) -> list[Call]:
    calls = [call for event in events if (call := call_from_tool_event(event)) is not None]
    if calls:
        return calls
    found: list[Call] = []
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), list):
            continue
        for part in message["content"]:
            if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name"):
                raw_input = part.get("input")
                found.append(_call_from_mapping(
                    str(part["name"]),
                    raw_input if isinstance(raw_input, dict) else {},
                    {},
                ))
    return found


def assistant_chunks(events: list[dict]) -> list[str]:
    chunks: list[str] = []
    for event in events:
        if event.get("type") == "result" and isinstance(event.get("result"), str):
            chunks.append(event["result"])
        message = event.get("message")
        if isinstance(message, str) and event.get("type") == "assistant":
            chunks.append(message)
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, str):
            chunks.append(content)
        elif isinstance(content, list):
            for part in content:
                if (
                    isinstance(part, dict)
                    and part.get("type") in {"text", "output_text"}
                    and isinstance(part.get("text"), str)
                ):
                    chunks.append(part["text"])
    return chunks


def final_message(events: list[dict]) -> str:
    chunks = assistant_chunks(events)
    return chunks[-1] if chunks else ""


def agent_bin() -> str:
    exe = shutil.which("agent") or shutil.which("cursor-agent")
    if not exe:
        sys.exit("Cursor CLI `agent` not on PATH. Install: https://cursor.com/docs/cli (then rerun).")
    return exe


def run_agent(workspace: Path, prompt: str, model: str | None, mode: str | None = None) -> list[dict]:
    cmd = [agent_bin(), "-p", "--force", "--trust", "--output-format", "stream-json",
           "--workspace", str(workspace), "--plugin-dir", str(ROOT)]
    if model:
        cmd += ["--model", model]
    if mode:
        cmd += ["--mode", mode]
    cmd.append(prompt)
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=workspace)
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def tool_calls(events: list[dict]) -> list[tuple[str, str]]:
    """(tool name, first path-ish arg) per tool_call event; tolerant of schema drift."""
    out = []
    for e in events:
        if "tool_call" not in json.dumps(e)[:200] and e.get("type") not in ("tool_call", "tool_use"):
            continue
        blob = json.dumps(e)
        name = e.get("name") or e.get("tool_name") or (e.get("tool_call") or {}).get("name") or ""
        if not name:
            m = re.search(r'"(?:name|tool_name|subtype)"\s*:\s*"([A-Za-z_]+)"', blob)
            name = m.group(1) if m else "?"
        m = re.search(r'"(?:path|file_path|filePath|pattern|command)"\s*:\s*"([^"]+)"', blob)
        out.append((name, m.group(1) if m else ""))
    return out


def design_kept(before: str, after: str, red_marker: str) -> bool:
    kept = [l for l in before.splitlines() if l.strip() and red_marker not in l]
    return all(l in after for l in kept)


def run_dummy(name: str, arm: str, model: str | None, n: int) -> None:
    src = DUMMIES / name
    task = (src / "EVAL-TASK.md").read_text(encoding="utf-8")
    red = RED.search(task)
    if not red:
        sys.exit(f"{name}/EVAL-TASK.md has no Red: `command` line")
    design_src = src / "docs" / "design.md"
    before = design_src.read_text(encoding="utf-8") if design_src.is_file() else ""
    TRACES.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / name
            seed_workspace(src, ws, arm)
            events = run_agent(ws, task, model)
            calls = tool_calls(events)
            extra = [c for c in calls if c[0] not in NATIVE]
            success = subprocess.run(red.group(1), shell=True, cwd=ws).returncode == 0
            after = (ws / "docs" / "design.md").read_text(encoding="utf-8") if design_src.is_file() else ""
            kept = design_kept(before, after, "Coming soon.") if before else True
            parsed = calls_from_events(events)
            reply = final_message(events)
            bare_claims = claims_without_evidence(reply, parsed)
            shot = screenshot_before_done(parsed)
            launches = dev_server_launches(parsed)
            busy = eaddrinuse_count(parsed)
            loaded = pack_loaded(parsed, ws)
            version = pack_version(dt.date.today())
        stamp = dt.date.today().isoformat()
        trace = TRACES / f"{stamp}-{name}-{arm}-{i}.md"
        trace.write_text(
            "# Trace\n\n"
            f"- Dummy: {name}\n- Arm: {arm}\n- Date: {stamp}\n- Model (picker name): {model or 'Auto'}\n"
            "- Cost class: fill from the picker\n"
            f"- Success: {'yes' if success and kept else 'no'} (Red exit {'0' if success else 'non-zero'}; design keep {'ok' if kept else 'FAILED'})\n"
            "- User turns until accepted: 1 (headless, one prompt)\n"
            f"- Tool calls (total): {len(calls)}\n- Extra tool calls (not Grep/Glob/Read or the named native): {len(extra)}\n"
            f"- claims_without_evidence: {bare_claims}\n"
            f"- screenshot_before_done: {shot}\n"
            f"- dev_server_launches: {launches}\n"
            f"- EADDRINUSE: {busy}\n"
            "- correction_turns: 0\n"
            f"- final_reply_chars: {len(reply)}\n"
            f"- pack_loaded: {loaded}\n"
            f"- pack_version: {version}\n"
            "- Tokens in / out (optional; skip if the dashboard is missing): skipped\n"
            f"- Notes (one line): headless via tools/eval-run.py; extra={[c[0] for c in extra][:8]}\n",
            encoding="utf-8",
        )
        print(
            f"{trace.name}: success={success} kept={kept} calls={len(calls)} "
            f"extra={len(extra)} claims_without_evidence={bare_claims} "
            f"screenshot_before_done={shot} dev_server_launches={launches} EADDRINUSE={busy} "
            f"pack_loaded={loaded} pack_version={version}"
        )


def run_phrasings(model: str | None) -> int:
    rows = []
    for line in (ROOT / "docs" / "evals" / "phrasings.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] not in ("Phrase", "---"):
            rows.append(cells)
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d) / "t1-nook"
        shutil.copytree(DUMMIES / "t1-nook", ws)
        for phrase, expected in rows:
            events = run_agent(ws, phrase, model, mode="plan")
            read = {m.group(1) for _, p in tool_calls(events) for m in [re.search(r"skills[\\/]([^\\/]+)[\\/]SKILL\.md", p)] if m}
            ok = (not read) if expected == "none" else (expected in read)
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {expected:<14} read={sorted(read) or '-'}  <- {phrase}")
    print(f"{len(rows) - failures}/{len(rows)} phrasings routed as expected")
    return 1 if failures else 0


def run_holes(model: str | None) -> int:
    rows = hole_rows((ROOT / "docs" / "evals" / "holes.md").read_text(encoding="utf-8"))
    if not rows:
        sys.exit("docs/evals/holes.md has no hole rows")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    failures = 0
    for row in rows:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "hole"
            ws.mkdir()
            (ws / "AGENTS.md").write_text(agents, encoding="utf-8")
            events = run_agent(ws, row["phrase"], model)
            ok, why = score_hole("\n".join(assistant_chunks(events)), ws, row["result"], row["filesystem"])
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {row['id']}" + ("" if ok else f"  {why}"))
    print(f"{len(rows) - failures}/{len(rows)} holes passed")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dummy", default="t1-nook")
    ap.add_argument("--arm", default="routed", choices=ARMS)
    ap.add_argument("--model", help="picker slug; omit for Auto (the routed arm)")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--phrasings", action="store_true", help="run docs/evals/phrasings.md instead of a dummy")
    ap.add_argument(
        "--holes",
        action="store_true",
        help="score docs/evals/holes.md from RESULT lines and filesystem checks",
    )
    a = ap.parse_args()
    if a.holes and a.phrasings:
        sys.exit("pass only one of --holes or --phrasings")
    if a.holes:
        return run_holes(a.model)
    if a.phrasings:
        return run_phrasings(a.model)
    run_dummy(a.dummy, a.arm, a.model, a.n)
    return 0


class TestClaimsWithoutEvidence(unittest.TestCase):
    def test_done_word_without_proof_counts(self) -> None:
        self.assertEqual(claims_without_evidence("shipped", []), 1)
        self.assertEqual(claims_without_evidence("It works now.", []), 1)
        self.assertEqual(claims_without_evidence("done and shipped", []), 2)

    def test_negations_and_not_checked_do_not_count(self) -> None:
        self.assertEqual(claims_without_evidence("not done", []), 0)
        self.assertEqual(claims_without_evidence("not checked", []), 0)
        self.assertEqual(claims_without_evidence("isn't fixed", []), 0)
        self.assertEqual(claims_without_evidence("never verified", []), 0)
        self.assertEqual(claims_without_evidence("Don't claim done", []), 0)
        self.assertEqual(claims_without_evidence("done, not shipped", []), 1)
        self.assertEqual(claims_without_evidence("The work is unverified.", []), 0)

    def test_qualifying_call_after_last_write_clears_the_count(self) -> None:
        writes = [Call("StrReplace"), Call("Shell", "pytest", 0, "ok")]
        self.assertEqual(claims_without_evidence("tests passed", writes), 0)
        before = [Call("Shell", "pytest", 0, "ok"), Call("Write")]
        self.assertEqual(claims_without_evidence("passed", before), 1)
        lints = [Call("Write"), Call("ReadLints")]
        self.assertEqual(claims_without_evidence("verified", lints), 0)
        shot = [Call("StrReplace"), Call("browser_take_screenshot", output="/tmp/a.png")]
        self.assertEqual(claims_without_evidence("works now", shot), 0)
        generic = [Call("Write"), Call("screenshot", output="/tmp/a.png")]
        self.assertEqual(claims_without_evidence("done", generic), 1)
        failed = [Call("Shell", "pytest", 1, "fail")]
        self.assertEqual(claims_without_evidence("passed", failed), 1)

    def test_git_push_output_and_pr_url_are_proof(self) -> None:
        push = [Call("Write"), Call("Shell", "git push -u origin feat", None, "abc..def  feat -> feat")]
        self.assertEqual(claims_without_evidence("pushed", push), 0)
        self.assertEqual(
            claims_without_evidence("shipped https://github.com/Troy-LL/Unfurnished/pull/12", []),
            0,
        )
        rejected = [Call("Shell", "git push", 1, "hint: feat -> feat")]
        self.assertEqual(claims_without_evidence("pushed", rejected), 1)

    def test_later_write_invalidates_earlier_proof(self) -> None:
        calls = [Call("Write"), Call("ReadLints"), Call("StrReplace")]
        self.assertEqual(claims_without_evidence("fixed", calls), 1)


class TestHoleScore(unittest.TestCase):
    def test_result_line_and_filesystem(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            (ws / "AGENTS.md").write_text("Do not map it.\n", encoding="utf-8")
            ok, _ = score_hole("RESULT: kept-do-not-map\n", ws, "kept-do-not-map", "agents-no-scratch-map")
            self.assertTrue(ok)
            (ws / "AGENTS.md").write_text("Do not map it.\n- `scratch/` — x\n", encoding="utf-8")
            ok, _ = score_hole("RESULT: kept-do-not-map\n", ws, "kept-do-not-map", "agents-no-scratch-map")
            self.assertFalse(ok)
            (ws / "AGENTS.md").write_text("Park thinking in `scratch/`.\n", encoding="utf-8")
            ok, _ = score_hole("RESULT: kept-do-not-map\n", ws, "kept-do-not-map", "agents-no-scratch-map")
            self.assertFalse(ok)

    def test_wrong_key_and_absent_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            (ws / "AGENTS.md").write_text("Do not map it.\n", encoding="utf-8")
            ok, _ = score_hole("RESULT: mapped-scratch\n", ws, "kept-do-not-map", "agents-no-scratch-map")
            self.assertFalse(ok)
            ok, _ = score_hole("See RESULT: kept-do-not-map", ws, "kept-do-not-map", "agents-no-scratch-map")
            self.assertFalse(ok)
            ok, _ = score_hole("RESULT: refused-glossary\n", ws, "refused-glossary", "absent:docs/glossary.md")
            self.assertTrue(ok)
            (ws / "docs").mkdir()
            (ws / "docs" / "glossary.md").write_text("x", encoding="utf-8")
            ok, _ = score_hole("RESULT: refused-glossary\n", ws, "refused-glossary", "absent:docs/glossary.md")
            self.assertFalse(ok)

    def test_table_ids_skip_omitted_holes(self) -> None:
        sample = (
            "h-claude and h-remake stay out.\n\n"
            "| Id | Phrase | Expected RESULT keys | Filesystem |\n"
            "| --- | --- | --- | --- |\n"
            "| h-map-scratch | add scratch | kept-do-not-map | agents-no-scratch-map |\n"
        )
        self.assertEqual([r["id"] for r in hole_rows(sample)], ["h-map-scratch"])

    def test_fixture_file_keys(self) -> None:
        rows = hole_rows((ROOT / "docs" / "evals" / "holes.md").read_text(encoding="utf-8"))
        ids = [r["id"] for r in rows]
        self.assertIn("h-map-scratch", ids)
        self.assertNotIn("h-claude", ids)
        self.assertNotIn("h-remake", ids)
        scratch = next(r for r in rows if r["id"] == "h-map-scratch")
        self.assertIn("kept-do-not-map", scratch["result"])
        self.assertIn("agents-no-scratch-map", scratch["filesystem"])


class TestAgentsScratchFence(unittest.TestCase):
    def test_live_file_and_fixtures(self) -> None:
        live = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(agents_scratch_fence(live))
        self.assertFalse(agents_scratch_fence(live + "\n- `scratch/` — thinking\n"))
        self.assertFalse(agents_scratch_fence(live + "\n- `scratch/tickets/` — tickets\n"))
        stripped = live.replace("Do not map it, even if they asked. ", "")
        self.assertNotIn("do not map", stripped.lower())
        self.assertFalse(agents_scratch_fence(stripped))
        self.assertTrue(agents_scratch_fence("Keep the do-not-map line.\n"))
        self.assertFalse(agents_scratch_fence("Keep the do-not-map line.\n* `scratch/tickets/` — x\n"))


class TestVisualAndServerFields(unittest.TestCase):
    def test_screenshot_before_done_follows_ui_edits(self) -> None:
        css = Call("Write", path="src/card.css")
        shot = Call("browser_take_screenshot", output="/tmp/card.png")
        self.assertEqual(screenshot_before_done([css, shot]), "yes")
        self.assertEqual(screenshot_before_done([shot, css]), "no")
        self.assertEqual(screenshot_before_done([css]), "no")
        self.assertEqual(screenshot_before_done([Call("Write", path="page.py"), shot]), "N/A")
        self.assertEqual(screenshot_before_done([Call("StrReplace", path="web/icon.svg"), shot]), "yes")
        self.assertEqual(screenshot_before_done([Call("Write", path="App.tsx")]), "no")
        self.assertEqual(screenshot_before_done([Call("Write", path="index.html"), shot]), "yes")
        generic = Call("screenshot", output="/tmp/card.png")
        self.assertEqual(screenshot_before_done([css, generic]), "no")

    def test_dev_server_launches_and_eaddrinuse(self) -> None:
        one = [Call("Shell", "npm run dev")]
        self.assertEqual(dev_server_launches(one), 1)
        self.assertEqual(eaddrinuse_count(one), 0)
        twice = [Call("Shell", "npm run dev"), Call("Shell", "pnpm dev")]
        self.assertEqual(dev_server_launches(twice), 2)
        chained = [Call("Shell", "yarn dev && bun run dev")]
        self.assertEqual(dev_server_launches(chained), 2)
        tests = [Call("Shell", "python -m unittest test_page.py", 0, "ok")]
        self.assertEqual(dev_server_launches(tests), 0)
        self.assertEqual(dev_server_launches([Call("Shell", "cat vite.config.ts")]), 0)
        busy = [Call("Shell", "npm start", 1, "Error: listen EADDRINUSE: address already in use")]
        self.assertEqual(dev_server_launches(busy), 1)
        self.assertEqual(eaddrinuse_count(busy), 1)
        echoed = [Call("Shell", "vite", 1, "EADDRINUSE\nEADDRINUSE")]
        self.assertEqual(dev_server_launches(echoed), 1)
        self.assertEqual(eaddrinuse_count(echoed), 2)
        self.assertNotIn("left_running", trace_field_names())

    def test_stream_events_feed_both_fields(self) -> None:
        events = [
            {
                "type": "tool_call",
                "subtype": "completed",
                "tool_call": {
                    "writeToolCall": {"args": {"path": "src/Card.tsx"}, "result": {}},
                },
            },
            {
                "type": "tool_call",
                "subtype": "completed",
                "tool_call": {
                    "shellToolCall": {
                        "args": {"command": "npm run dev"},
                        "result": {"exitCode": 1, "stderr": "Error: listen EADDRINUSE"},
                    }
                },
            },
            {
                "type": "tool_call",
                "subtype": "completed",
                "tool_call": {"browserTakeScreenshotToolCall": {"args": {}, "result": {"output": "/tmp/a.png"}}},
            },
        ]
        calls = calls_from_events(events)
        self.assertEqual(screenshot_before_done(calls), "yes")
        self.assertEqual(dev_server_launches(calls), 1)
        self.assertEqual(eaddrinuse_count(calls), 1)


class TestSoftOffArm(unittest.TestCase):
    def test_choices_keep_the_existing_arms(self) -> None:
        self.assertEqual(ARMS, ("routed", "always-cheap", "always-frontier", "soft-off"))

    def test_soft_off_writes_the_knob_and_other_arms_do_not(self) -> None:
        src = DUMMIES / "t0-cli"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed_workspace(src, root / "off", "soft-off")
            knob = root / "off" / "scratch" / "unfurnished-off"
            self.assertTrue(knob.is_file())
            self.assertEqual(knob.read_text(encoding="utf-8"), "off\n")
            for arm in ("routed", "always-cheap", "always-frontier"):
                seed_workspace(src, root / arm, arm)
                self.assertFalse((root / arm / "scratch" / "unfurnished-off").exists())


class TestPackTags(unittest.TestCase):
    def test_pack_loaded_needs_a_pack_read_and_no_off_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            bias = Call("Read", path=".cursor/rules/unfurnished-bias.mdc")
            skill = Call("Read", path=".cursor/skills/verify/SKILL.md")
            other = Call("Read", path="README.md")
            self.assertEqual(pack_loaded([bias], ws), "yes")
            self.assertEqual(pack_loaded([skill], ws), "yes")
            self.assertEqual(pack_loaded([Call("Read", path=r".cursor\skills\sdd\SKILL.md")], ws), "yes")
            self.assertEqual(pack_loaded([other], ws), "no")
            self.assertEqual(pack_loaded([Call("Grep", path=".cursor/rules/unfurnished-bias.mdc")], ws), "no")
            (ws / "scratch").mkdir()
            (ws / "scratch" / "unfurnished-off").write_text("off\n", encoding="utf-8")
            self.assertEqual(pack_loaded([bias, skill], ws), "no")

    def test_read_tool_event_counts_as_pack_loaded(self) -> None:
        events = [
            {
                "type": "tool_call",
                "subtype": "completed",
                "tool_call": {
                    "readToolCall": {"args": {"path": ".cursor/rules/unfurnished-bias.mdc"}, "result": {}},
                },
            }
        ]
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(pack_loaded(calls_from_events(events), Path(d)), "yes")

    def test_pack_version_uses_the_release_dates(self) -> None:
        self.assertEqual(pack_version(None), "unknown")
        self.assertEqual(pack_version(dt.date(2026, 8, 15)), "unknown")
        self.assertEqual(pack_version(dt.date(2026, 8, 16)), "1.0.0")
        self.assertEqual(pack_version(dt.date(2026, 9, 1)), "1.1.0")
        self.assertEqual(pack_version(dt.date(2026, 9, 2)), "unknown")
        self.assertEqual(pack_version(dt.date(2026, 9, 3)), "1.3.0")
        self.assertEqual(pack_version(dt.date(2026, 9, 24)), "1.3.0")
        self.assertEqual(pack_version(dt.date(2026, 9, 25)), "1.4.0")
        self.assertEqual(pack_version(dt.date(2026, 10, 19)), "1.4.0")


class TestStreamParse(unittest.TestCase):
    def test_shell_exit_after_no_write_is_proof(self) -> None:
        events = [
            {
                "type": "tool_call",
                "subtype": "completed",
                "tool_call": {
                    "shellToolCall": {
                        "args": {"command": "python -m unittest"},
                        "result": {"exitCode": 0, "stdout": "ok"},
                    }
                },
            },
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "tests passed"}]}},
        ]
        calls = calls_from_events(events)
        self.assertEqual(calls[0].name, "Shell")
        self.assertEqual(calls[0].exit_code, 0)
        self.assertEqual(claims_without_evidence(final_message(events), calls), 0)

    def test_started_shell_is_not_a_second_call(self) -> None:
        events = [
            {"type": "tool_call", "subtype": "started", "tool_call": {"name": "Shell", "args": {"command": "pytest"}}},
            {
                "type": "tool_call",
                "subtype": "completed",
                "tool_call": {"name": "Shell", "args": {"command": "pytest"}, "result": {"exitCode": 0}},
            },
        ]
        calls = calls_from_events(events)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].exit_code, 0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "unittest":
        sys.argv = [sys.argv[0]]
        raise SystemExit(unittest.main())
    raise SystemExit(main())
