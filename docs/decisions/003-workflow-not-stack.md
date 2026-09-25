# Workflow, not stack: stack-agnostic pack and adopt-first doctrine

Status: Accepted

## Context

We do not know the user's stack. We never will. A Supabase guide, a Stripe integration skill, or a Postgres optimization prompt assumes a specific project. On any other project, stack-bound tools are dead context—worse, wrong context that taxes the session window ([002-first-shot-efficiency.md](002-first-shot-efficiency.md)) for tools that are not there.

What survives every project is the **workflow layer**: reviewing, planning, frontier questioning, red-green verification, adversarial auditing, and intent alignment. That is the only layer Unfurnished ships.

When community workflow skills are already battle-tested in the wild, rewriting them from scratch throws away edge-case fixes and isolates us from upstream maintenance. Extraction was designed as an escape hatch for salvaging good ideas from broken packs, not as a default intake strategy.

## Decision

### 1. The Workflow Litmus Test

Unfurnished ships only stack-agnostic workflow tools. A skill, command, or rule must work identically whether the project is a Rust CLI, a Next.js SaaS, a Python data pipeline, or embedded firmware.

A stack-agnostic skill remains specific not through tool names, but through:
- **Process sequence**: Strict operational order (e.g. observe failing test before code, 4-gate verification before turn yield).
- **Frontier questioning**: Mapping settled prerequisites vs. open decisions without guessing (e.g. `grill`).
- **Adversarial invariant rubrics**: Exact inspection angles (e.g. tenant `user_id` filtering, unhandled async promises, unbounded memory scans, race conditions).
- **Deterministic stop conditions**: Hard exit gates (0 linter diagnostics, clean compiler exit codes, 0 unhandled TODO stubs, clean dev server runtime logs).

### 2. Adopt-First Doctrine

When a workflow skill is already proven, we adopt it verbatim with attribution and a pointer to upstream. We do not rewrite it out of pride.

**Battle-tested definition**:
1. Sustained real-world usage across projects with active community adoption.
2. Maintained upstream with responsive issue resolution.
3. Operates unchanged in Cursor without foreign runtime dependencies or tool-wrapper bloat.
4. Complies with [001-native-first.md](001-native-first.md), [002-first-shot-efficiency.md](002-first-shot-efficiency.md), and the workflow litmus test.

**Eviction triggers**:
- *Constitutional drift*: Upstream adds always-on context bloat, routers, or duplicate Cursor builtins (violates 001/002).
- *Stack contamination*: Upstream introduces hardcoded framework or vendor dependencies.
- *Upstream rot*: Upstream becomes unmaintained, abandoned, or broken under current model/IDE releases.

If an upstream fails our bar but contains an isolated durable workflow insight, extract only that insight with attribution. Otherwise, adopt verbatim or leave it out.

### 3. Named Boundary Rulings

| Area | Workflow (In) | Stack (Out) |
|---|---|---|
| **Testing** | Language-agnostic red-green cycle (`tdd.mdc`); local TDD pointer (`ticket`) | Pytest / Vitest / Jest runner assertions or mock helpers |
| **Verification & Deploy** | Compiler exit code, anti-stub scan (`verify`) | Vercel CLI deploy scripts, AWS CDK stacks, Dockerfiles, secret scans, `.env.example` parity |
| **Security & Audits** | Auth boundary checks, tenant isolation, race condition checks (Task `bugbot` / `security-review`; the pack's own review skill was retired in [008](008-no-command-twins.md)) | Supabase RLS policy templates, Prisma schema migrations |
| **Evals** | Calibrated binary LLM-as-a-judge rubrics, trace-to-fixture distillation (`evals`) | Vendor SDK clients, LangChain pipeline scaffolds |
| **Architecture** | Interface narrowing (`blast-radius.mdc`) | React state management patterns, Tailwind design systems |

### 4. Inherited Intake Questions

Every future intake or audit sweep must answer two questions:
1. **Does this piece work unchanged on a project we have never seen?** If it requires a specific language, framework, database, or vendor, it is out.
2. **Is this already battle-tested upstream?** If yes and it passes 001, 002, and the workflow litmus, adopt verbatim with attribution. Do not extract; do not rewrite.

## Consequences

- Unfurnished remains a universal pack with zero dead-weight stack context.
- App-specific rules and framework guides belong in project-level `.cursor/rules/` (via `/create-rule` or `cursor-directory`), never in this pack.
- Upstream improvements flow directly into adopted skills; rotting upstreams are evicted or extracted on failure.
