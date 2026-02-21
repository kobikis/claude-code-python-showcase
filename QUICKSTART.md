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
# Install all components (skills, agents, commands, hooks, orchestrator)
python setup_target_project.py --target /path/to/your-project --all

# Compile skill routing rules into CLAUDE.md
python compile_rules.py --target /path/to/your-project
```

Individual components:
```bash
python setup_target_project.py --target /path/to/project --component skills
python setup_target_project.py --target /path/to/project --component agents
python setup_target_project.py --target /path/to/project --component hooks
```

---

## Common operations

| Task | Command |
|------|---------|
| Dry-run install (preview) | `python setup_target_project.py --target /path --all --dry-run` |
| Update single component | `./update_component.sh hooks /path/to/project` |
| Preview CLAUDE.md output | `python compile_rules.py --target /path --dry-run` |
| Reinstall personal hooks | `./.claude/install.sh --hooks` |

---

## How skill routing works

After install, skills activate automatically via 3 layers:

1. **CLAUDE.md** — routing table compiled from `skill-rules.json`, loaded every session natively
2. **SessionStart hook** — re-injects routing table + `dev/active/` context at session start
3. **Orchestrator agent** — reads intent, loads the matching skill, dispatches to specialist agent

To customize routing for your project, edit `.claude/skills/skill-rules.json` then recompile:
```bash
python compile_rules.py --target /path/to/your-project
```
