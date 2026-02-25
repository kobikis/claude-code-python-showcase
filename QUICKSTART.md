# Quick Start

## Use Case 1: Restore personal config on a new machine

```bash
git clone <repo>
cd claude-code-python-showcase

# Install everything to ~/.claude/
./.claude/install.sh --all

# Then follow MCP wiring instructions
./.claude/install.sh --mcp
```

Individual components:
```bash
./.claude/install.sh --agents
./.claude/install.sh --skills
./.claude/install.sh --hooks
./.claude/install.sh --rules
```

Keep local changes synced back to the repo:
```bash
./.claude/install.sh --sync    # copies ~/.claude/ → repo .claude/
git add .claude/ && git commit
```

---

## Use Case 2: Install infrastructure into a target project

```bash
# Install all components (skills, agents, commands, hooks, rules)
python setup_target_project.py --target /path/to/your-project --all

# Compile skill routing rules into CLAUDE.md
python compile_rules.py --target /path/to/your-project
```

Individual components:
```bash
python setup_target_project.py --target /path/to/project --component skills
python setup_target_project.py --target /path/to/project --component agents
python setup_target_project.py --target /path/to/project --component rules
python setup_target_project.py --target /path/to/project --component hooks
python setup_target_project.py --target /path/to/project --component commands
```

---

## Common operations

| Task | Command |
|------|---------|
| Install all (non-interactive) | `python setup_target_project.py --target /path --all --non-interactive` |
| Update single component | `./update_component.sh /path/to/project skills` |
| Preview CLAUDE.md output | `python compile_rules.py --target /path --dry-run` |
| Reinstall personal hooks | `./.claude/install.sh --hooks` |

---

## What's included

| Component | Count | Highlights |
|-----------|-------|------------|
| Agents | 10 | planner, architect, tdd-guide, fastapi-specialist, aws-specialist, k8s-specialist, python-debugger |
| Commands | 9 | /pr, /plan, /tdd, /code-review, /build-fix, /verify, /test-coverage, /update-docs, /orchestrate |
| Skills | 12 | python-patterns, async-python-patterns, postgres-patterns, docker-patterns, security-review, tdd-workflow |
| Rules | 13 | 8 common (coding-style, testing, security, ...) + 5 Python-specific |
| Shell hooks | 4 | block-dangerous-bash, protect-files, session-context, validate-sql |
| JS hook scripts | 5 | session-start, session-end, evaluate-session, pre-compact, suggest-compact |
| JS libraries | 4 | package-manager, session-aliases, session-manager, utils |

---

## How skill routing works

After install, skills activate automatically via 3 layers:

1. **CLAUDE.md** — routing table compiled from `skill-rules.json`, loaded every session natively
2. **SessionStart hook** — re-injects routing table + `dev/active/` context at session start
3. **`/orchestrate` command** — chains agents in a pipeline, loading relevant skills at each step

To customize routing for your project, edit `.claude/skills/skill-rules.json` then recompile:
```bash
python compile_rules.py --target /path/to/your-project
```
