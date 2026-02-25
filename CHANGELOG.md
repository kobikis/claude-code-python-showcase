# Changelog

All notable changes to this project are documented here.

---

## [4.0.0] — 2026-02-25

### Changed

**Generators: inline templates → file-copy from `.claude/` source**

The generator system was overhauled to copy files from the `.claude/` directory
(source of truth) instead of embedding ~7,700 lines of duplicated markdown as
Python string templates. This eliminates the maintenance burden of keeping
generators in sync with the personal config.

- `agents_generator.py` (~778 → ~55 lines) — `shutil.copy2` from `.claude/agents/`
- `commands_generator.py` (~655 → ~55 lines) — `shutil.copy2` from `.claude/commands/`
- `skills_generator.py` (~743 → ~170 lines) — `shutil.copytree` from `.claude/skills/` + `SKILL_METADATA` for routing
- `hooks_generator.py` (~488 → ~120 lines) — copies shell hooks, JS hooks, and JS library modules
- `examples_generator.py` — 5 new examples aligned with current skills (repository_pattern, pydantic_v2_models, health_endpoints, async_service, base_service)
- `compile_rules.py` — updated skill→agent routing map (12 skills → 10 agents)
- `setup_target_project.py` — added `setup_rules()`, `setup_scripts()`, removed `setup_orchestrator()`; updated all component lists
- `update_component.sh` — added `update_commands()`, `update_rules()`; updated all component lists

### Removed

- `skills_content.py` — PyTorch, HuggingFace, model-optimization content no longer needed
- Old example templates (circuit_breaker, idempotency, webhook_verifier, async_kafka) — replaced with current-skill-aligned examples
- Old agent templates (orchestrator, webhook-validator, kafka-optimizer, security-auditor, async-converter, ai-engineer) — replaced by file-copy of 10 current agents
- Old command templates (check-prod-readiness, kafka-health, webhook-test, security-scan, migrate-pydantic-v2) — replaced by file-copy of 9 current commands
- Old skill templates (webhook-security, api-security, resilience-patterns, pytorch-patterns, huggingface-models, model-optimization) — replaced by file-copy of 12 current skills

---

## [3.0.0] — 2026-02-25

### Added

**Slash Commands (7 new)**
- `.claude/commands/plan.md` — restate requirements, assess risks, create step-by-step implementation plan
- `.claude/commands/tdd.md` — enforce test-driven development workflow with 80%+ coverage
- `.claude/commands/code-review.md` — run code review on changed files
- `.claude/commands/build-fix.md` — build project and fix errors iteratively
- `.claude/commands/test-coverage.md` — analyze and report test coverage
- `.claude/commands/verify.md` — run verification checks
- `.claude/commands/update-docs.md` — update documentation
- `.claude/commands/orchestrate.md` — orchestrate multi-agent workflows

**Specialist Agents (5 new)**
- `aws-specialist.md` — AWS services: Lambda, SQS, IoT Core, RDS, S3, CloudWatch, boto3/aiobotocore
- `fastapi-specialist.md` — FastAPI framework: DI, Pydantic v2 models, middleware, WebSocket, OAuth2/JWT, background tasks
- `k8s-specialist.md` — Kubernetes & containers: Deployments, Helm, Dockerfile, HPA, probes, RBAC, network policies
- `python-database-expert.md` — PostgreSQL + SQLAlchemy + Alembic: schema design, query optimization, migrations (replaces database-reviewer + database-optimizer)
- `python-debugger.md` — Root cause analysis: pdb, profiling, tracing, memory analysis, hypothesis-driven debugging

**Python-Specific Rules (5 new)**
- `.claude/rules/python/coding-style.md` — Python coding conventions
- `.claude/rules/python/hooks.md` — Python hook patterns
- `.claude/rules/python/patterns.md` — Python design patterns
- `.claude/rules/python/security.md` — Python security rules
- `.claude/rules/python/testing.md` — Python testing conventions

**JS Hook Scripts (5 new)**
- `.claude/scripts/hooks/session-start.js` — inject context at session start
- `.claude/scripts/hooks/session-end.js` — cleanup and session summary
- `.claude/scripts/hooks/evaluate-session.js` — post-session evaluation
- `.claude/scripts/hooks/pre-compact.js` — save state before context compaction
- `.claude/scripts/hooks/suggest-compact.js` — suggest compaction at logical boundaries

**JS Utility Libraries (4 new)**
- `.claude/scripts/lib/package-manager.js` — package manager detection and operations
- `.claude/scripts/lib/session-aliases.js` — session alias management
- `.claude/scripts/lib/session-manager.js` — session lifecycle management
- `.claude/scripts/lib/utils.js` — common utilities
- TypeScript declarations (`.d.ts`) included for all modules

### Changed

**Agents (22 → 10) — consolidated and focused**
- Updated `architect.md` — streamlined system design agent
- Updated `code-reviewer.md` — rewritten for Python-focused review
- Updated `tdd-guide.md` — updated TDD workflow

**Documentation**
- `README.md` — updated component counts, added commands/JS scripts/rules sections, removed 3-layer routing table
- `QUICKSTART.md` — updated component inventory table, added JS hooks and libraries
- `docs/workflow.md` — updated agent counts, added new slash commands to reference tables

### Removed

**Agents (12 removed)**
- `api-designer.md`, `backend-developer.md`, `build-error-resolver.md` — superseded by specialist agents
- `database-optimizer.md`, `database-reviewer.md` — merged into `python-database-expert.md`
- `doc-updater.md`, `e2e-runner.md`, `refactor-cleaner.md` — low-value generalist agents
- `go-build-resolver.md`, `go-reviewer.md` — Go-specific agents removed (Python focus)
- `python-pro.md`, `python-reviewer.md` — merged into `code-reviewer.md`
- `qa-expert.md` — merged into `tdd-guide.md`
- `perplexity-research.md` — superseded by `perplexity-deep-search` skill
- `vapi-ai-expert.md` — domain-specific, not general-purpose

**Commands (1 removed)**
- `dev-docs.md` — replaced by `/update-docs`

**Skills (30 removed) — massive cleanup**
- Language-specific: `cpp-coding-standards`, `cpp-testing`, `golang-patterns`, `golang-testing`, `java-coding-standards`, `jpa-patterns`
- Backend frameworks: `backend-dev-guidelines` (+ resources), `backend-patterns`, `route-tester`
- Domain-specific: `clickhouse-io`, `nutrient-document-processing`, `error-tracking`, `ralph-prd` (+ references/scripts)
- Architecture: `api-design`, `content-hash-cache-pattern`, `cost-aware-llm-pipeline`, `iterative-retrieval`, `regex-vs-llm-structured-text`
- Infrastructure: `database-migrations`, `e2e-testing`, `frontend-patterns`, `eval-harness`
- Meta: `skill-developer`, `configure-ecc`, `project-guidelines-example`, `security-scan`
- Git: `git` (+ workflows)
- Learning: `continuous-learning`, `continuous-learning-v2` (+ agents/hooks/scripts/config)
- Testing: `python-testing-patterns` (+ resources) — replaced by `python-testing` skill

**Other**
- `.claude/skills/skill-rules.json` — removed from personal config (routing table only applies to target projects via `setup_target_project.py`)

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
