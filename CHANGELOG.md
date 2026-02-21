# Changelog

All notable changes to this project are documented here.

---

## [2.0.0] — 2026-02-21

### Added

**3-Layer Skill Routing Architecture**
- `compile_rules.py` — compiles `.claude/skills/skill-rules.json` into `CLAUDE.md` routing table; idempotent, supports `--dry-run`
- `agents_generator.py` — orchestrator agent added; all 5 specialist agents updated with explicit `Activation Patterns` and `Mandatory First Step: load skill` instructions
- `hooks_generator.py` — `session-start` hook template: reads `skill-rules.json` + `dev/active/*.md` and injects both at every session start
- `setup_target_project.py` — three new install steps: `compile_rules_to_claude_md()`, `setup_orchestrator()`, `install_session_hook()` (settings.json dedup-safe); interactive menu options 8–10

**Personal Config Store (`.claude/`)**
- `.claude/agents/` — 22 agents: planner, architect, code-reviewer, security-reviewer, tdd-guide, refactor-cleaner, doc-updater, e2e-runner, build-error-resolver, python-reviewer, python-pro, go-reviewer, go-build-resolver, api-designer, backend-developer, database-reviewer, database-optimizer, qa-expert + 4 project-specific
- `.claude/skills/` — 42 skills including python-patterns (sickn33), async-python-patterns, python-testing-patterns, perplexity-deep-search (ericsantos), postgres-patterns, docker-patterns, deployment-patterns, design-doc-mermaid, cost-aware-llm-pipeline, and more
- `.claude/hooks/` — 4 active hooks: `block-dangerous-bash.sh`, `protect-files.sh`, `session-context.sh`, `validate-sql.py`
- `.claude/commands/` — `pr.md`, `dev-docs.md`
- `.claude/scripts/pg-mcp.sh` — PostgreSQL MCP bridge script
- `.claude/rules/common/` — 8 global rules: coding-style, git-workflow, testing, security, performance, patterns, agents, hooks
- `.claude/mcp/mcp-servers.json` — portable MCP config with `${CLAUDE_DIR}` placeholders (cmem, atlassian, mermaid, postgres-customer, postgres-processing)
- `.claude/mcp/hooks-config.json` — hooks wiring config
- `.claude/install.sh` — installer: `--all`, `--agents`, `--skills`, `--hooks`, `--rules`, `--mcp`, `--sync`, `--dry-run`, interactive menu

**Example Feature (`dev/active/`)**
- `dev/active/CONTEXT.md` — realistic FastAPI + SQLAlchemy 2.0 async + Pydantic v2 project context; includes Tech Stack Conventions (Pydantic v2 patterns, SQLAlchemy 2.0 imports, optional auth dependency, immutable update pattern)
- `dev/active/TASK.md` — CRUD API task spec with acceptance criteria and success metrics
- `dev/active/PLAN.md` — 6-phase implementation plan with Best Practices Applied table and validated code examples

### Changed

**Documentation**
- `README.md` — full rewrite: dual-purpose description (generator + personal config store), repo structure diagram, both use cases, 3-layer routing architecture with routing table, full component inventory
- `QUICKSTART.md` — full rewrite: accurate instructions for both use cases, common operations table, routing explanation

**Hooks (personal config cleanup)**
- Removed `skill-activation-prompt.py` — used non-existent `UserPromptSubmit` hook event; superseded by session-start + CLAUDE.md
- Removed `post-tool-use-tracker.py` — unregistered, wrong input format, noisy
- Removed `mypy-check.py` — unregistered, ran whole-project mypy at Stop event blocking session end
- Removed `hooks/README.md` and `hooks/requirements.txt` — only documented removed hooks

**Skills (plugin cache cleanup)**
- Removed django-patterns, django-security, django-tdd, django-verification
- Removed springboot-* skills
- Replaced `python-patterns/SKILL.md` with sickn33 version (teaches thinking, not copy-paste)
- Added `async-python-patterns` from sickn33/antigravity-awesome-skills
- Added `python-testing-patterns` from sickn33/antigravity-awesome-skills
- Added `perplexity-deep-search` from ericsantos (openclaw/skills)

**Hook allowlist (everything-claude-code plugin)**
- Added `CHANGELOG`, `MIGRATION`, `SECURITY` to allowed `.md` file creation patterns
- Added `dev/active/` path to bypass allowlist (active context files change frequently)

### Removed

- `SUMMARY.md`, `PROJECT_STRUCTURE.md`, `SETUP_README.md`, `UPDATE_TARGET_PROJECT.md`, `MCP_SETUP.md`, `TROUBLESHOOTING_MCP.md` — obsolete docs
- `.github-ready.txt`, `.env.example` — stale placeholders
- `examples/` — empty directory
- `__pycache__/` — build artifact
- `dev/active/example-feature/` — merged to flat `dev/active/` structure
- `personal-config/` — merged into `.claude/`

### Fixed

**dev/active/ example feature (6 bugs)**
- Files in `dev/active/example-feature/` instead of `dev/active/` (hook reads flat path) — moved
- `from_orm()` deprecated in Pydantic v2 — replaced with `model_validate()` (7 occurrences)
- Schema used `class Config: from_attributes = True` (v1 syntax) — updated to `model_config = ConfigDict(from_attributes=True)`
- Missing `from pydantic import ConfigDict` import
- `func` used in `PostRepository.count_by_author()` without import — added `from sqlalchemy import select, func`
- `get_current_user_optional` referenced in routes but never defined — added implementation

---

## [1.0.0] — 2024-11-21

### Added

- Initial project structure: generator scripts for skills, agents, hooks, commands, examples
- `skills_generator.py` — skill directory and `skill-rules.json` generation
- `agents_generator.py` — 5 specialist agents: webhook-validator, kafka-optimizer, security-auditor, async-converter, ai-engineer
- `hooks_generator.py` — pre-commit (ruff/mypy/bandit), complexity-detector, dependency-checker hook templates
- `commands_generator.py` — `/check-prod-readiness`, `/kafka-health`, `/webhook-test`, `/security-scan`, `/migrate-pydantic-v2`
- `examples_generator.py` — example FastAPI implementation templates
- `setup_target_project.py` — unified installer for target projects (`--all`, `--component`)
- `update_component.sh` — update individual components in existing installations
- `skills_content.py` — AI/ML skill content (PyTorch, HuggingFace, model-optimization)
- Project-specific skills: `webhook-security`, `api-security`, `resilience-patterns`, `async-kafka`, `pytorch-patterns`, `huggingface-models`, `model-optimization`
- `dev/active/example-feature/` — example CONTEXT.md, TASK.md, PLAN.md for feature context
