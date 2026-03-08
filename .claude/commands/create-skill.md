---
description: "Build a new Claude Code skill (SKILL.md) from a workflow description. Loads the skill-architect skill and produces a ready-to-install skill package."
---

# Create Skill

Turns a workflow description into a production-ready skill package for this repository.

## What This Command Does

1. Loads `.claude/skills/skill-architect/SKILL.md`
2. Collects your workflow description (asks one question if input is missing)
3. Produces a complete `SKILL.md` ready to drop into `.claude/skills/<name>/`
4. Produces the `SKILL_METADATA` Python snippet to add to `skills_generator.py`

## How to Use

```
/create-skill <workflow or goal description>
```

**Examples:**
```
/create-skill write conventional git commit messages from staged changes
/create-skill review PRs and output a structured quality report
/create-skill analyze a FastAPI endpoint for security issues
```

If you run `/create-skill` with no arguments, it will ask: _"What workflow should this skill encode?"_

## Output

After running, you will receive:

1. **`SKILL.md`** — complete skill file, ready to install at:
   ```
   .claude/skills/<skill-name>/SKILL.md
   ```

2. **`SKILL_METADATA` block** — Python dict entry to add to `skills_generator.py` under `SKILL_METADATA`

3. **Installation instructions** — exact steps to register the skill in the routing system

## Installation Steps (after receiving output)

```bash
# 1. Create skill directory
mkdir -p .claude/skills/<skill-name>

# 2. Save the SKILL.md output to that directory

# 3. Add the SKILL_METADATA block to skills_generator.py
#    (under the SKILL_METADATA dict and SKILL_NAMES list)

# 4. Regenerate routing
python compile_rules.py --target . --dry-run   # preview
python compile_rules.py --target .             # apply
```

## Related

- Skill source of truth: `.claude/skills/skill-architect/SKILL.md`
- Routing metadata: `skills_generator.py` → `SKILL_METADATA`, `SKILL_NAMES`
- Routing table: compiled into `CLAUDE.md` by `compile_rules.py`