# Skill Developer - Meta Skill for Creating Skills

**Status**: ✅ Complete | **Purpose**: Guide for creating well-structured Claude Code skills

## What is a Skill?

A skill is a specialized knowledge domain that Claude can invoke during development. Skills help Claude:
- Apply consistent patterns
- Remember project conventions
- Suggest best practices
- Enforce guardrails

## Skill Anatomy

Every skill has:
1. **SKILL.md** - Main guide (keep under 500 lines)
2. **resources/*.md** - Detailed sub-topics
3. **Entry in skill-rules.json** - Activation rules

## Creating a New Skill

### Step 1: Define the Skill

Answer these questions:
- What domain does it cover? (e.g., "API testing with pytest")
- When should it activate? (keywords, file patterns)
- What problems does it solve?
- What are the core principles?

### Step 2: Create Directory Structure

```bash
mkdir -p .claude/skills/my-skill/resources
touch .claude/skills/my-skill/SKILL.md
```

### Step 3: Write SKILL.md

Template:
```markdown
# Skill Name - Brief Description

**Status**: ✅ Complete | **Applies to**: Technologies/frameworks

## Quick Start Checklists

### Common Task 1
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

### Common Task 2
- [ ] Step 1
- [ ] Step 2

---

## Core Principles

### 1. Principle Name (Mandatory/Recommended)

**✅ DO:**
```python
# Good example
```

**❌ DON'T:**
```python
# Bad example
```

### 2. Another Principle

...

---

## Navigation Guide

| Topic | Resource File |
|-------|---------------|
| Detailed topic 1 | `resources/topic1.md` |
| Detailed topic 2 | `resources/topic2.md` |

---

## Summary

- Core principle 1
- Core principle 2
- Core principle 3
```

### Step 4: Add to skill-rules.json

```json
{
  "name": "my-skill",
  "type": "suggest",
  "priority": "high",
  "description": "Brief description of what the skill does",
  "keywords": [
    "keyword1",
    "keyword2",
    "framework-name"
  ],
  "intentPatterns": [
    "(create|add|implement).*?keyword",
    "how.*?do-something"
  ],
  "filePaths": [
    "**/path/to/**/*.py",
    "**/tests/**/*.py"
  ],
  "message": "💡 Consider using `/my-skill` for [specific use case]"
}
```

### Step 5: Create Resource Files

For topics that need deep dives (over 100 lines):

```markdown
# Resource Topic Name

## Overview

Brief explanation of what this covers.

## Pattern 1

```python
# Complete working example
```

## Pattern 2

```python
# Another example
```

## Common Pitfalls

- Pitfall 1
- Pitfall 2

See also:
- `related-resource.md` for related topic
```

## Skill Types

### 1. Suggest (Most Common)

Non-blocking suggestion that Claude can choose to use:

```json
{
  "type": "suggest",
  "message": "💡 Consider using `/my-skill`"
}
```

### 2. Block (Guardrails)

Blocks execution until skill is invoked:

```json
{
  "type": "block",
  "blockMessage": "⚠️ BLOCKED - Required Action\n\nPlease use `/my-skill` before proceeding.",
  "skipMarkers": ["# @skip-my-skill"],
  "skipEnvVar": "SKIP_MY_SKILL"
}
```

### 3. Warn

Shows warning but allows continuation:

```json
{
  "type": "warn",
  "message": "⚠️ Warning: Consider using `/my-skill`"
}
```

## Priority Levels

- **critical**: Life/death, security issues
- **high**: Important patterns, best practices
- **medium**: Nice to have, optimization
- **low**: Optional suggestions

## Best Practices

### DO:

✅ Keep main SKILL.md under 500 lines
✅ Use clear, actionable checklists
✅ Provide working code examples
✅ Show both good and bad patterns
✅ Link to resource files for deep dives
✅ Use consistent formatting
✅ Test activation rules

### DON'T:

❌ Put everything in one file
❌ Use vague descriptions
❌ Forget to add activation rules
❌ Skip code examples
❌ Use broken links to resources
❌ Make it too generic

## Testing Your Skill

1. **Test activation**:
```bash
echo '{"prompt": "I want to test my skill activation", "projectRoot": "."}' | \
  python .claude/hooks/skill-activation-prompt.py
```

2. **Test with Claude**:
- Type a prompt that should trigger it
- Verify the suggestion appears
- Invoke the skill manually: `/my-skill`
- Check that content is helpful

3. **Test file pattern matching**:
- Open a file that matches filePaths
- Make an edit
- Verify skill is suggested

## Example Skills to Study

1. **backend-dev-guidelines**: Comprehensive patterns for FastAPI/Django
2. **route-tester**: Focused on pytest patterns
3. **error-tracking**: Integration patterns for Sentry

## Common Patterns

### Configuration-Heavy Skills

For skills about tool configuration (Docker, CI/CD):
- Show complete config files
- Explain each section
- Provide templates

### Pattern Library Skills

For skills about design patterns:
- Multiple examples of each pattern
- When to use vs. avoid
- Common variations

### Testing Skills

For skills about testing:
- Fixture examples
- Test structure
- Coverage strategies

## Iteration and Improvement

Skills should evolve:
1. Start with core patterns
2. Add resources as needed
3. Refine activation rules
4. Gather feedback
5. Update examples

## Anti-Patterns

### ❌ Too Broad

```json
{
  "name": "python-development",
  "keywords": ["python"]  // Will match everything!
}
```

Better: Create focused skills (fastapi-dev, django-dev, pytest-patterns)

### ❌ Too Specific

```json
{
  "name": "fix-bug-123",
  "keywords": ["bug 123"]  // One-time use
}
```

Better: Create reusable patterns for bug categories

### ❌ No Examples

```markdown
# Use dependency injection

It's better.  // Not helpful!
```

Better: Show working code examples

## Summary

Creating a good skill:
1. ✅ Solve a specific, recurring problem
2. ✅ Keep main guide under 500 lines
3. ✅ Use progressive disclosure with resources
4. ✅ Provide working examples
5. ✅ Test activation rules
6. ✅ Show both good and bad patterns
7. ✅ Update based on usage

The goal: Make Claude's suggestions consistently helpful.
