# Full Workflow: PRD to Implementation

Two notation conventions used throughout:

- `$` — terminal command (bash)
- `>` — prompt typed inside a Claude Code session (the chat)

---

## Part 1 — One-Time Machine Setup

Do this once per machine. Skip if `~/.claude/` is already populated.

```bash
# Clone the showcase repo
$ git clone <your-claude-code-python-showcase-repo>
$ cd claude-code-python-showcase

# Install personal config globally
$ ./.claude/install.sh --all

# Follow the printed MCP wiring instructions
$ ./.claude/install.sh --mcp
```

What this puts in `~/.claude/` (available in every project):
- 22 general-purpose agents (planner, code-reviewer, tdd-guide, security-reviewer, ...)
- 42 personal skills (python-patterns, postgres-patterns, async-python-patterns, ...)
- 8 global rules (coding-style, testing, security, git-workflow, ...)
- 4 safety hooks (block-dangerous-bash, protect-files, validate-sql, session-context)

---

## Part 2 — Per-Project Setup (new repo)

Do this once per new project.

```bash
# Create and initialise the repo
$ mkdir my-new-project && cd my-new-project
$ git init
$ python -m venv .venv && source .venv/bin/activate
$ pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic

# Install Claude Code project infrastructure
$ python /path/to/claude-code-python-showcase/setup_target_project.py \
    --target . \
    --all

# Compile skill routing rules into CLAUDE.md (Layer 1)
$ python /path/to/claude-code-python-showcase/compile_rules.py \
    --target .

# Preview what CLAUDE.md will contain before writing
$ python /path/to/claude-code-python-showcase/compile_rules.py \
    --target . \
    --dry-run
```

What `--all` installs into `.claude/` inside your project:
- Domain-specific skills with routing rules (`skill-rules.json`)
- Orchestrator agent + 5 specialist agents
- Session-start hook registered in `.claude/settings.json`
- Project slash commands

Verify the install:
```bash
$ ls .claude/
agents/  commands/  hooks/  settings.json  skills/

$ cat CLAUDE.md
# Skill Routing
...routing table compiled from skill-rules.json...
```

---

## Part 3 — Translate PRD into Context Files

The session-start hook injects these files into every Claude session. The better you write them, the less you re-explain the project each time.

```bash
$ mkdir -p dev/active
```

### Option A — Write them yourself (30–60 min)

Create `dev/active/CONTEXT.md`:
```markdown
# Context: <Feature Name>

## Current State
- What already exists (services, models, auth)
- Tech stack (FastAPI 0.104, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL 15)

## Project Structure
app/
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── repositories/ # Data access (BaseRepository pattern)
├── services/     # Business logic
└── routes/       # FastAPI routers

## Conventions
- Services receive repository in constructor
- Raise custom exceptions (NotFoundError, UnauthorizedError)
- model_validate() not from_orm() (Pydantic v2)
- from sqlalchemy import select, func  (func must be explicit)

## Database Schema
(existing tables + planned new tables)

## Related Code Patterns
(paste real route/service examples from your project)
```

Create `dev/active/TASK.md`:
```markdown
# Task: <Feature Name>

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Acceptance Criteria
- [ ] Testable criterion 1
- [ ] Testable criterion 2

## Out of Scope
(what the PRD explicitly defers)
```

Leave `dev/active/PLAN.md` empty or minimal — the planner agent fills it.

### Option B — Let Claude draft from the PRD

```bash
$ claude
```

Inside the session:
```
> Here is our PRD: <paste full PRD text>

  Our tech stack: FastAPI 0.104, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL 15.
  Our project structure: <paste tree output>

  Draft dev/active/CONTEXT.md and dev/active/TASK.md from this.
  Do not write anything yet — show me the drafts first.
```

Review the drafts, correct anything wrong about your project structure, then:
```
> Looks good except <corrections>. Now write both files.
```

### Option C — Fully autonomous via /ralph-prd

```bash
$ claude
```

```
> /ralph-prd <paste PRD title and description>
```

Claude creates a structured PRD document. Then convert it for autonomous execution:
```
> /ralph-prd convert ./docs/prd/feature-name/prd.md
```

This produces a structured JSON that drives autonomous phase execution. See the ralph-prd skill for details.

---

## Part 4 — Implementation Workflow

### Step 1: Open Claude Code in the project

```bash
$ cd my-new-project
$ claude
```

At session start the session-start hook fires automatically and prints:
```
## Active Skill Routes
- webhook-security | keywords: webhook, signature, hmac | agent: webhook-validator
- api-security     | keywords: auth, jwt, api key      | agent: security-auditor
- async-kafka      | keywords: kafka, consumer, dlq    | agent: kafka-optimizer
...

## Active Project Context
### CONTEXT.md
# Context: Post Management API
...

### TASK.md
...
---
Orchestrator: Use Task tool with orchestrator agent for complex tasks.
```

No input needed — routing table and project context are loaded before you type anything.

### Step 2: Plan the implementation

```
> Use the planner agent to create an implementation plan for dev/active/TASK.md.
  Output the plan to dev/active/PLAN.md.
```

The planner agent:
1. Reads CONTEXT.md and TASK.md
2. Breaks work into sequential phases (DB → schemas → repository → service → routes → tests)
3. Lists files affected, rollback steps, and success criteria per phase
4. Writes the result to PLAN.md

**You review PLAN.md before proceeding.** Check:
- Phase order makes sense
- Approach matches your conventions from CONTEXT.md
- No over-engineering for the scope

Edit PLAN.md if anything is wrong, then move to Step 3.

### Step 3: Implement phase by phase (TDD)

For each phase in PLAN.md:

```
> Use tdd-guide agent to implement Phase 1 from dev/active/PLAN.md
```

The tdd-guide agent per phase:
1. Writes interface/signatures (no implementation body)
2. Writes failing tests — RED
3. Writes minimal implementation to pass — GREEN
4. Refactors — IMPROVE
5. Reports coverage

After each phase, run tests yourself:
```bash
$ pytest tests/ -v --cov=app --cov-report=term-missing
```

If tests pass and coverage is ≥80%, proceed to Phase 2:
```
> Phase 1 looks good. Use tdd-guide to implement Phase 2.
```

If something is wrong:
```
> The test for create_post is testing the wrong thing — it should verify
  author_id is set from current_user, not from the request body.
  Fix the test and re-run.
```

### Step 4: Code review after each phase

```
> Use code-reviewer agent on the files created in Phase 1:
  app/models/post.py, app/repositories/post_repository.py
```

The code-reviewer checks against your global rules:
- Immutability — no in-place mutation
- Function size <50 lines, file size <800 lines
- Explicit error handling — no silent swallowing
- Input validation at system boundaries
- No hardcoded values

It outputs CRITICAL / HIGH / MEDIUM / LOW findings. Address CRITICAL and HIGH before continuing.

```
> Fix the CRITICAL finding about the missing authorization check in update_post.
```

### Step 5: Security review before commit

```
> Use security-reviewer agent on app/routes/posts.py and app/services/post_service.py
```

### Step 6: Commit

```bash
# Stage specific files — never `git add .` blindly
$ git add app/models/post.py app/repositories/post_repository.py
$ git add tests/unit/test_post_repository.py
$ git commit -m "feat: add Post model and repository with find_by_author and find_published"

$ git add app/schemas/post.py
$ git commit -m "feat: add PostCreate, PostUpdate, PostResponse schemas (Pydantic v2)"

# Continue per phase
```

### Step 7: Update task progress

Keep TASK.md current — the session-start hook re-injects it each session:
```markdown
## Requirements
- [x] Create Post model with SQLAlchemy       ← done
- [x] Add Alembic migration for posts table   ← done
- [ ] Implement Pydantic schemas              ← in progress
- [ ] Create PostService
```

### Step 8: Pull request

When all phases are complete and tests pass:
```
> /pr
```

The `/pr` command:
1. Analyzes all commits since branching from base
2. Runs `git diff base...HEAD` to see the full changeset
3. Drafts a comprehensive PR title and summary
4. Creates the PR with `gh pr create`

---

## Part 5 — Full Command Reference

### Terminal (bash)

| Command | When |
|---------|------|
| `./.claude/install.sh --all` | One-time: install personal config |
| `python setup_target_project.py --target . --all` | Per project: install infrastructure |
| `python compile_rules.py --target .` | Per project: compile CLAUDE.md routing |
| `python compile_rules.py --target . --dry-run` | Preview routing before writing |
| `claude` | Start interactive session |
| `claude -p "<prompt>"` | Non-interactive single prompt |
| `pytest tests/ -v --cov=app` | Run tests with coverage |
| `ruff check --fix . && black .` | Lint and format |
| `alembic revision --autogenerate -m "..."` | Generate migration |
| `alembic upgrade head` | Apply migration |

### Inside Claude Code session (chat prompts)

| Prompt | What it does |
|--------|-------------|
| `Use planner agent to plan TASK.md` | Generates phased PLAN.md |
| `Use tdd-guide agent to implement Phase N from PLAN.md` | TDD implementation for one phase |
| `Use code-reviewer on <files>` | Reviews against global rules |
| `Use security-reviewer on <files>` | Security audit |
| `Use orchestrator agent to implement TASK.md end-to-end` | Full autonomous chain (see below) |
| `/pr` | Creates GitHub pull request |
| `/compact` | Compact context (do at phase boundaries) |

### Slash commands (Claude Code built-in)

| Command | Effect |
|---------|--------|
| `/compact` | Summarise and compress context |
| `/clear` | Clear session history |
| `/help` | List all available commands |
| `/pr` | Create PR (from your personal config) |

---

## Part 6 — Autonomous Path

If you trust the plan and want to reduce manual prompting:

### Option A: Orchestrator chains all phases

```
> Read dev/active/TASK.md and dev/active/PLAN.md.
  Use orchestrator agent to implement all phases end-to-end:
  dispatch to tdd-guide for each phase, run tests after each phase,
  fix failures, then run code-reviewer on all new files.
  Auto-approve file creation and edits.
```

Enable auto-accept in Claude Code settings (Shift+Tab to toggle permission mode to auto-accept), then start this prompt. You review the final output rather than each phase.

### Option B: /ralph-prd full autonomous execution

```bash
$ claude
```

```
> /ralph-prd convert ./docs/prd/posts/prd.md
```

Ralph-PRD reads the PRD, structures it into phases, and executes them sequentially with minimal human input. Best for well-defined, bounded features.

### When to use each

| Situation | Recommended path |
|-----------|-----------------|
| New feature, unknown complexity | Manual (Steps 1–8 above) |
| Clear spec, familiar domain | Orchestrator chains phases |
| PRD exists as a document | /ralph-prd convert |
| Spike or exploration | Manual only — autonomy needs a clear target |
| Hotfix | Skip planning, go straight to tdd-guide |

---

## Part 7 — Context Compaction Strategy

Long sessions accumulate context. Compact at logical boundaries to avoid mid-task context loss.

```
/compact  ← after plan is written, before implementation starts
/compact  ← after each major phase group (e.g., after DB + schema phases)
/compact  ← after debugging, before continuing new work
```

The session-start hook re-injects CONTEXT.md + TASK.md after every compaction, so project context is always restored. Keep TASK.md updated with completed checkboxes so the re-injected context reflects current progress.

---

## Related

- [QUICKSTART.md](../QUICKSTART.md) — setup commands only
- [README.md](../README.md) — architecture overview
- [dev/active/CONTEXT.md](../dev/active/CONTEXT.md) — example context file
- [dev/active/TASK.md](../dev/active/TASK.md) — example task file
- [dev/active/PLAN.md](../dev/active/PLAN.md) — example plan file
