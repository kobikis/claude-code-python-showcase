---
name: skill-architect
description: "Build reusable Claude Code skills (SKILL.md files). Encodes workflows into permanent, executable skill prompts ready to drop into .claude/skills/<name>/."
allowed-tools: Read, Write, Glob
---

# Skill Architect

Turns a described workflow into a production-ready `SKILL.md` file for this repository.

## When to Activate

- `/create-skill` command invoked
- User says "create a skill for X", "build a skill that does Y", "encode this workflow"
- Existing skill needs restructuring or is over 500 lines

---

## Workflow

### Step 1 — Gather Input

Collect from the user (ask only if critical info is missing):

| Field | Required | Default |
|-------|----------|---------|
| Workflow to encode | Yes | — |
| Skill name (slug) | No | Inferred from workflow |
| Specialist agent to pair with | No | Inferred from domain |
| Existing examples / preferences | No | None |

### Step 2 — Analyze the Workflow

Break the workflow into:
- **Discrete steps** (ordered operations)
- **Decision points** (if/then branches)
- **Constants** (always the same) vs **variables** (change per use)
- **Quality criteria** (what "done" looks like)
- **Edge cases** (incomplete inputs, unusual scenarios)

### Step 3 — Map to Skill Architecture

Determine:
- **Trigger patterns** — regex / intent phrases that activate this skill
- **File path patterns** — which files indicate this skill is relevant
- **Paired agent** — which specialist agent should load this skill (see routing table in CLAUDE.md)
- **Resource files needed** — if content exceeds 500 lines, split into `resources/*.md`

### Step 4 — Write the SKILL.md

Follow the template below. Keep SKILL.md ≤ 500 lines. Move verbose examples, extended checklists, or reference tables to `resources/` and link them with:
```
> Extended reference: load `resources/<file>.md` on demand
```

### Step 5 — Generate `skill-rules.json` Entry

Produce the metadata block to add to `SKILL_METADATA` in `skills_generator.py`:

```python
"<skill-name>": {
    "description": "<one sentence>",
    "keywords": ["<kw1>", "<kw2>", "<kw3>", "<kw4>"],
    "intent_patterns": [
        "<regex pattern 1>",
        "<regex pattern 2>",
    ],
    "file_paths": ["<glob pattern>"],
},
```

### Step 6 — Output Checklist

Before delivering, verify:
- [ ] SKILL.md frontmatter has `name`, `description`, `allowed-tools`
- [ ] "When to Activate" section is specific (not generic)
- [ ] Every workflow step produces a concrete artifact
- [ ] Decision logic covers the 3 most common variations
- [ ] At least 2 concrete examples with input → output
- [ ] File is ≤ 500 lines
- [ ] `SKILL_METADATA` block is included

---

## SKILL.md Template

```markdown
---
name: <skill-name>
description: "<One sentence: what this skill does and when to use it.>"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# <Skill Title>

> <One-line summary of the skill's purpose.>

## When to Activate

- <Specific trigger condition 1>
- <Specific trigger condition 2>
- <Specific trigger condition 3>

---

## Workflow

### Step 1 — <Action>
- What: <specific action>
- How: <concrete method>
- Output: <artifact produced>

### Step 2 — <Action>
[...]

---

## Decision Logic

**IF** <condition>:
→ <action>

**IF** <condition>:
→ <action>

**DEFAULT**:
→ <fallback>

---

## Quality Standards

Every output must:
- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] <Criterion 3>

Never:
- <Anti-pattern 1>
- <Anti-pattern 2>

---

## Output Format

<Exact structure for the deliverable — headers, sections, code blocks, etc.>

---

## Examples

**Input**: <brief description>
**Output**:
<example output>

---

**Input**: <brief description>
**Output**:
<example output>

---

## Edge Cases

| Scenario | Response |
|----------|----------|
| <Missing input X> | <Ask for it / use default Y> |
| <Ambiguous requirement> | <How to resolve> |
| <Oversized output> | <Split into resources/> |
```

---

## Decision Logic

**IF** the user provides a workflow description with clear steps:
→ Proceed directly to Step 4, infer name and agent from domain

**IF** the user provides only a goal ("create a skill for code review"):
→ Ask one clarifying question: "What are the 3-5 steps in this workflow?"

**IF** the resulting SKILL.md would exceed 500 lines:
→ Extract verbose sections into `resources/<topic>.md`, add on-demand load note

**IF** the skill clearly maps to an existing agent (e.g., postgres → `python-database-expert`):
→ Include that agent in the `SKILL_METADATA` entry and note it in SKILL.md

**IF** no paired agent is obvious:
→ Omit agent from metadata; leave pairing to the user

---

## Quality Standards

Every skill produced must:
- [ ] Be immediately usable — copy `SKILL.md` into `.claude/skills/<name>/` and it works
- [ ] Have decision logic that covers at least 3 scenario branches
- [ ] Include 2+ concrete examples with real inputs and outputs
- [ ] Stay ≤ 500 lines in `SKILL.md`
- [ ] Include the `SKILL_METADATA` Python snippet for `skills_generator.py`
- [ ] Use specific language ("Run `ruff check`") not vague language ("check code quality")

Never:
- Produce a skill that only paraphrases the user's description
- Leave decision points unresolved (every branch must have an action)
- Omit the `SKILL_METADATA` block (routing won't work without it)

---

## Examples

**Input**: "Create a skill for writing git commit messages in conventional commits format"

**Output** (excerpt):
```markdown
---
name: git-commit-writer
description: "Generates conventional commit messages from staged changes or a description of work done."
allowed-tools: Bash, Read
---

# Git Commit Writer

## When to Activate
- User says "write a commit message", "commit this", "generate commit"
- After code changes are staged and ready to commit

## Workflow
### Step 1 — Read Staged Changes
Run `git diff --cached` and `git status` to understand what changed.
Output: list of changed files + diff summary

### Step 2 — Classify Change Type
...
```

---

**Input**: "A skill that reviews PRs and outputs a structured report"

**Output** (excerpt):
```markdown
---
name: pr-reviewer
description: "Reviews pull request diffs and produces a structured report covering correctness, security, and style."
allowed-tools: Bash, Read, Grep
---
...
```