# Claude Code Python Showcase

> Production-ready Claude Code infrastructure for Python projects — specialist agents, curated skills, slash commands, and personal config management.

## What This Repo Is

Two things in one:

1. **Generator system** — Python scripts that install Claude Code infrastructure (skills, agents, hooks, commands) into any target FastAPI project — including automatic skill routing
2. **Personal config store** — `.claude/` mirrors `~/.claude/`, version-controlled and installable on any machine

---

## Repo Structure

```
claude-code-python-showcase/
│
├── .claude/                    ← Personal config (mirrors ~/.claude/)
│   ├── agents/                 10 specialist agents
│   ├── commands/               9 slash commands (pr, plan, tdd, code-review, etc.)
│   ├── skills/                 12 curated skills (python-patterns, postgres, docker, etc.)
│   ├── hooks/                  4 shell hook scripts (block-dangerous-bash, protect-files, etc.)
│   ├── scripts/
│   │   ├── hooks/              5 JS hook scripts (session-start, session-end, etc.)
│   │   ├── lib/                4 JS utility modules (session-manager, utils, etc.)
│   │   └── pg-mcp.sh          PostgreSQL MCP bridge
│   ├── rules/
│   │   ├── common/             8 global coding rules
│   │   └── python/             5 Python-specific rules
│   ├── mcp/                    MCP server configs + hooks config
│   ├── settings.json           Project Claude settings
│   └── install.sh              ← Install personal config to ~/.claude/
│
├── setup_target_project.py     ← Install infrastructure into a target project
├── compile_rules.py            ← Compile skill-rules.json → CLAUDE.md
├── agents_generator.py         Copies agents from .claude/agents/
├── commands_generator.py       Copies commands from .claude/commands/
├── hooks_generator.py          Copies hooks + JS scripts from .claude/
├── skills_generator.py         Copies skills from .claude/skills/ + generates skill-rules.json
├── examples_generator.py       Example implementation templates
├── update_component.sh         Update components in an existing installation
└── dev/active/                 Active feature context (CONTEXT.md, TASK.md, PLAN.md)
```

---

## Use Case 1: Install Personal Config on a New Machine

```bash
git clone <repo>
./.claude/install.sh --all          # install everything to ~/.claude/
./.claude/install.sh --mcp          # show MCP + hooks wiring instructions
```

Individual components:
```bash
./.claude/install.sh --agents
./.claude/install.sh --skills
./.claude/install.sh --hooks
./.claude/install.sh --rules
```

Sync local changes back to the repo:
```bash
./.claude/install.sh --sync         # copies ~/.claude/ → repo .claude/
git diff .claude/                   # review
git add .claude/ && git commit
```

### How the personal config works

The personal config uses **agents + commands + skills as standalone components** — no automatic routing. You invoke them explicitly:

- **Slash commands** (`/plan`, `/tdd`, `/code-review`, etc.) — trigger predefined workflows
- **Agent dispatch** (`Use planner agent...`, `Use tdd-guide...`) — invoke specialists by name
- **`/orchestrate`** — chains agents in a fixed pipeline (e.g., planner → tdd-guide → code-reviewer → security-reviewer)
- **Skills** — knowledge libraries loaded by agents on demand, not auto-routed

---

## Use Case 2: Install Infrastructure Into a Target Project

```bash
python setup_target_project.py --target /path/to/your/project --all
```

This copies the same `.claude/` infrastructure from the showcase into your target project:

| Component | What gets installed |
|-----------|-------------------|
| **Skills** (12) | python-patterns, async-python-patterns, python-testing, tdd-workflow, postgres-patterns, docker-patterns, deployment-patterns, security-review, design-doc-mermaid, perplexity-deep-search, verification-loop, strategic-compact |
| **Agents** (10) | planner, architect, tdd-guide, code-reviewer, security-reviewer, fastapi-specialist, aws-specialist, k8s-specialist, python-database-expert, python-debugger |
| **Commands** (9) | /pr, /plan, /tdd, /code-review, /build-fix, /test-coverage, /verify, /update-docs, /orchestrate |
| **Hooks** | 4 shell hooks + 5 JS hooks + 4 JS library modules |
| **Rules** (13) | 8 common + 5 Python-specific coding rules |

Then compile skill routing rules into `CLAUDE.md`:
```bash
python compile_rules.py --target /path/to/your/project
```

Or install individual components:
```bash
python setup_target_project.py --target /path/to/project --component skills
python setup_target_project.py --target /path/to/project --component agents
python setup_target_project.py --target /path/to/project --component rules
```

### 3-Layer Skill Routing (target projects only)

When installed into a target project via `setup_target_project.py`, the generator creates a `skill-rules.json` routing table that enables automatic skill activation based on intent — not manual invocation.

```
Layer 1 — CLAUDE.md (native, always loaded)
  compile_rules.py reads skill-rules.json and writes routing instructions
  into CLAUDE.md. Claude reads this natively every session.

Layer 2 — SessionStart hook (injected at session start)
  session-start.js reads skill-rules.json + dev/active/*.md and injects
  the routing table + project context into every session automatically.

Layer 3 — /orchestrate command (explicit routing)
  Chains agents in a pipeline: planner → tdd-guide → code-reviewer →
  security-reviewer, loading relevant skills at each step.
```

**Routing table** (generated from `skill-rules.json`):

| Intent keywords | Skill loaded | Agent invoked |
|----------------|-------------|---------------|
| python, framework, type hints | `python-patterns` | `architect` |
| async, await, asyncio | `async-python-patterns` | `fastapi-specialist` |
| pytest, test, coverage | `python-testing` | `tdd-guide` |
| tdd, test first | `tdd-workflow` | `tdd-guide` |
| postgres, sql, schema | `postgres-patterns` | `python-database-expert` |
| docker, container | `docker-patterns` | `k8s-specialist` |
| deploy, ci/cd, health check | `deployment-patterns` | `k8s-specialist` |
| security, auth, vulnerability | `security-review` | `security-reviewer` |
| mermaid, diagram | `design-doc-mermaid` | `architect` |
| search, research | `perplexity-deep-search` | `planner` |
| verify, validate | `verification-loop` | `code-reviewer` |

> **Note:** The personal config (Use Case 1) does **not** include `skill-rules.json` or automatic routing. It uses explicit agent invocation and slash commands instead.

---

## Personal Config: What's Included

### Agents (10)

Core workflow: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `tdd-guide`

Stack-specific: `fastapi-specialist`, `aws-specialist`, `k8s-specialist`

Database: `python-database-expert`

Debugging: `python-debugger`

### Commands (9)

| Command | Purpose |
|---------|---------|
| `/pr` | Create GitHub pull request |
| `/plan` | Restate requirements, assess risks, create implementation plan |
| `/tdd` | Enforce test-driven development workflow |
| `/code-review` | Run code review on changed files |
| `/build-fix` | Build project and fix errors |
| `/test-coverage` | Analyze and report test coverage |
| `/verify` | Run verification checks |
| `/update-docs` | Update documentation |
| `/orchestrate` | Orchestrate multi-agent workflows |

### Skills (12)

Python: `python-patterns`, `async-python-patterns`, `python-testing`, `tdd-workflow`

Infrastructure: `postgres-patterns`, `docker-patterns`, `deployment-patterns`

Security: `security-review`

Diagramming: `design-doc-mermaid`

AI/Web search: `perplexity-deep-search`

Workflow: `verification-loop`, `strategic-compact`

### Rules (13)

Common (8): `coding-style`, `git-workflow`, `testing`, `security`, `performance`, `patterns`, `agents`, `hooks`

Python (5): `coding-style`, `hooks`, `patterns`, `security`, `testing`

### Hooks — Shell Scripts (4)

| Hook | Event | Purpose |
|------|-------|---------|
| `block-dangerous-bash.sh` | `PreToolUse (Bash)` | Blocks `rm -rf /`, `curl\|bash` |
| `protect-files.sh` | `PreToolUse (Edit/Write)` | Blocks `.env`, `*.pem` edits |
| `session-context.sh` | `SessionStart` | Re-injects project context |
| `validate-sql.py` | `PreToolUse (MCP postgres)` | Validates SQL before execution |

### Hooks — JS Scripts (5)

| Script | Purpose |
|--------|---------|
| `session-start.js` | Load previous session context and learned skills |
| `session-end.js` | Cleanup and session summary |
| `evaluate-session.js` | Post-session evaluation |
| `pre-compact.js` | Save state before context compaction |
| `suggest-compact.js` | Suggest compaction at logical boundaries |

### JS Utility Libraries (4)

| Module | Purpose |
|--------|---------|
| `package-manager.js` | Package manager detection and operations |
| `session-aliases.js` | Session alias management |
| `session-manager.js` | Session lifecycle management |
| `utils.js` | Common utilities |

### MCP Servers

| Name | Purpose |
|------|---------|
| `cmem` | Session memory + lesson tracking |
| `atlassian` | Jira + Confluence (SSE) |
| `mermaid` | Mermaid diagram live preview |
| `postgres-customer` | Customer DB read-only access |
| `postgres-processing` | Processing DB read-only access |

---

## Key Design Principles

**Skills as knowledge libraries** — SKILL.md files contain patterns, checklists, and code templates. They don't execute; agents load and apply them.

**Agents as domain experts** — Each agent has explicit activation patterns and a mandatory first step: load its domain skill before any analysis.

**`.claude/` = source of truth** — Generators copy files from the `.claude/` directory instead of embedding content as Python strings. Edit `.claude/` files directly; generators just copy them.

**500-line rule** — SKILL.md stays under 500 lines. Detailed content lives in `resources/*.md`, loaded on demand to avoid context explosion.

---

## Docs

| Doc | Contents |
|-----|----------|
| [docs/workflow.md](docs/workflow.md) | PRD to implementation — who does what, why it's not fully autonomous, how to increase autonomy |

---

## License

MIT
