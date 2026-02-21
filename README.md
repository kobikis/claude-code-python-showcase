# Claude Code Python Showcase

> Production-ready Claude Code infrastructure for Python projects — with automatic skill routing, specialist agents, and personal config management.

## What This Repo Is

Two things in one:

1. **Generator system** — Python scripts that install Claude Code infrastructure (skills, agents, hooks, commands) into any target FastAPI project
2. **Personal config store** — `.claude/` mirrors `~/.claude/`, version-controlled and installable on any machine

---

## Repo Structure

```
claude-code-python-showcase/
│
├── .claude/                    ← Personal config (mirrors ~/.claude/)
│   ├── agents/                 22 agents (planner, code-reviewer, tdd-guide, etc.)
│   ├── commands/               2 slash commands (pr, dev-docs)
│   ├── skills/                 42 skills (python-patterns, postgres, docker, etc.)
│   ├── hooks/                  4 hook scripts (block-dangerous-bash, protect-files, etc.)
│   ├── scripts/                pg-mcp.sh (PostgreSQL MCP bridge)
│   ├── rules/common/           8 global coding rules
│   ├── mcp/                    MCP server configs + hooks config
│   ├── settings.json           Project Claude settings
│   └── install.sh              ← Install personal config to ~/.claude/
│
├── setup_target_project.py     ← Install infrastructure into a target project
├── compile_rules.py            ← Compile skill-rules.json → CLAUDE.md
├── agents_generator.py         Agent template definitions
├── commands_generator.py       Command template definitions
├── hooks_generator.py          Hook script templates
├── skills_generator.py         Skill directory + rules generator
├── skills_content.py           AI/ML skill content (PyTorch, HuggingFace)
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

---

## Use Case 2: Install Infrastructure Into a Target Project

```bash
python setup_target_project.py --target /path/to/your/project --all
```

This installs into the target project's `.claude/`:

| Component | What gets installed |
|-----------|-------------------|
| **Skills** | webhook-security, api-security, resilience-patterns, async-kafka, pytorch-patterns, huggingface-models, model-optimization |
| **Agents** | orchestrator, webhook-validator, kafka-optimizer, security-auditor, async-converter, ai-engineer |
| **Commands** | /check-prod-readiness, /kafka-health, /webhook-test, /security-scan, /migrate-pydantic-v2 |
| **Hooks** | pre-commit (ruff/mypy/bandit), complexity-detector, session-start (skill routing), dependency-checker |

Then compile skill routing rules into `CLAUDE.md`:
```bash
python compile_rules.py --target /path/to/your/project
```

Or install individual components:
```bash
python setup_target_project.py --target /path/to/project --component skills
python setup_target_project.py --target /path/to/project --component agents
```

---

## The 3-Layer Skill Routing Architecture

The core innovation: skills activate automatically based on intent, not manual invocation.

```
Layer 1 — CLAUDE.md (native, always loaded)
  compile_rules.py reads skill-rules.json and writes routing instructions
  into CLAUDE.md. Claude reads this natively every session.

Layer 2 — SessionStart hook (injected at session start)
  session-start.py prints the active routing table + project context
  (CONTEXT.md, TASK.md) into every session automatically.

Layer 3 — Orchestrator agent (explicit routing)
  Reads intent → matches routing table → loads skill SKILL.md →
  dispatches to specialist agent via Task tool.
```

**Routing table** (from `skill-rules.json`):

| Intent keywords | Skill loaded | Agent invoked |
|----------------|-------------|---------------|
| webhook, signature, hmac | `webhook-security` | `webhook-validator` |
| auth, jwt, api key, rate limit | `api-security` | `security-auditor` |
| kafka, consumer, producer, dlq | `async-kafka` + `resilience-patterns` | `kafka-optimizer` |
| circuit breaker, retry, backoff | `resilience-patterns` | `kafka-optimizer` |
| pytorch, training, gpu, cuda | `pytorch-patterns` | `ai-engineer` |
| huggingface, transformers | `huggingface-models` | `ai-engineer` |

---

## Personal Config: What's Included

### Agents (22)
General-purpose: `planner`, `architect`, `code-reviewer`, `security-reviewer`, `tdd-guide`, `refactor-cleaner`, `doc-updater`, `e2e-runner`, `build-error-resolver`

Language-specific: `python-reviewer`, `python-pro`, `go-reviewer`, `go-build-resolver`

Domain-specific: `api-designer`, `backend-developer`, `database-reviewer`, `database-optimizer`, `qa-expert`

### Skills (42)
Python: `python-patterns` (sickn33 2025), `async-python-patterns`, `python-testing-patterns`, `python-testing`

Infrastructure: `postgres-patterns`, `docker-patterns`, `deployment-patterns`, `database-migrations`

AI/Web search: `perplexity-deep-search` (ericsantos bash impl)

And more: `api-design`, `backend-patterns`, `security-review`, `tdd-workflow`, `frontend-patterns`, `design-doc-mermaid`, `cost-aware-llm-pipeline`, ...

### Hooks (4 active)
| Hook | Event | Purpose |
|------|-------|---------|
| `block-dangerous-bash.sh` | `PreToolUse (Bash)` | Blocks `rm -rf /`, `curl\|bash` |
| `protect-files.sh` | `PreToolUse (Edit/Write)` | Blocks `.env`, `*.pem` edits |
| `session-context.sh` | `SessionStart` | Re-injects project context |
| `validate-sql.py` | `PreToolUse (MCP postgres)` | Validates SQL before execution |

### MCP Servers
| Name | Purpose |
|------|---------|
| `cmem` | Session memory + lesson tracking |
| `atlassian` | Jira + Confluence (SSE) |
| `mermaid` | Mermaid diagram live preview |
| `postgres-customer` | Customer DB read-only access |
| `postgres-processing` | Processing DB read-only access |

### Rules (8)
`coding-style`, `git-workflow`, `testing`, `security`, `performance`, `patterns`, `agents`, `hooks`

---

## Key Design Principles

**Skills as knowledge libraries** — SKILL.md files contain patterns, checklists, and code templates. They don't execute; agents load and apply them.

**Agents as domain experts** — Each agent has explicit activation patterns and a mandatory first step: load its domain skill before any analysis.

**Generator = source of truth** — Infrastructure is generated from Python templates. Edit the generators, regenerate; don't edit generated files directly.

**500-line rule** — SKILL.md stays under 500 lines. Detailed content lives in `resources/*.md`, loaded on demand to avoid context explosion.

---

## Docs

| Doc | Contents |
|-----|----------|
| [docs/workflow.md](docs/workflow.md) | PRD to implementation — who does what, why it's not fully autonomous, how to increase autonomy |

---

## License

MIT
