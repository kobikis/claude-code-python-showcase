# Claude Code Integration Guide - FastAPI Projects

**AI-Assisted Setup**: This guide is designed to be executed with Claude Code for automated integration.

## Overview

This guide walks through integrating the Claude Code FastAPI infrastructure into your existing project. Total time: ~30 minutes.

## Prerequisites

- FastAPI project (Python 3.8+)
- Claude Code installed
- Git repository (recommended)

## Phase 1: Essential Hooks (15 minutes)

### Goal
Enable automatic skill activation based on your prompts and file context.

### Steps

#### 1. Copy Hook Files

```bash
# From this showcase repository
cp -r .claude/hooks/ /path/to/your-project/.claude/hooks/

# Make executable (Unix/Mac)
chmod +x /path/to/your-project/.claude/hooks/*.py
```

#### 2. Install Dependencies

```bash
cd /path/to/your-project

# Install hook dependencies
pip install -r .claude/hooks/requirements.txt

# Or if using poetry
poetry add --group dev mypy ruff
```

#### 3. Update settings.json

Create or update `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": "python .claude/hooks/skill-activation-prompt.py",
    "PostToolUse": "python .claude/hooks/post-tool-use-tracker.py"
  },
  "permissions": {
    "edit": "allow",
    "write": "allow",
    "bash": "allow"
  }
}
```

#### 4. Test Hook Installation

```bash
# Test skill activation hook
echo '{"prompt": "I want to add a new FastAPI endpoint", "projectRoot": "."}' | \
  python .claude/hooks/skill-activation-prompt.py
```

Expected output:
```
💡 Relevant Skills Detected

💡 The /backend-dev-guidelines skill provides Python backend patterns...
```

### Checkpoint 1

✅ Hooks copied and executable
✅ Dependencies installed
✅ settings.json configured
✅ Test command shows skill suggestions

---

## Phase 2: First Skill (10 minutes)

### Goal
Add the backend-dev-guidelines skill for FastAPI best practices.

### Copy the Skill

```bash
cp -r .claude/skills/backend-dev-guidelines /path/to/your-project/.claude/skills/
```

### Configure Skill Rules

Create `.claude/skills/skill-rules.json` (or copy from showcase):

```json
{
  "version": "1.0",
  "skills": [
    {
      "name": "backend-dev-guidelines",
      "type": "suggest",
      "priority": "high",
      "keywords": [
        "fastapi",
        "endpoint",
        "route",
        "api",
        "sqlalchemy"
      ],
      "intentPatterns": [
        "(create|add|implement).*?(endpoint|route|api)"
      ],
      "filePaths": [
        "**/api/**/*.py",
        "**/routes/**/*.py",
        "**/app/**/*.py"
      ],
      "message": "💡 The /backend-dev-guidelines skill provides Python backend patterns including FastAPI best practices."
    }
  ]
}
```

### Customize for Your Project

Update `skill-rules.json`:

1. **Keywords**: Add domain-specific terms
   ```json
   "keywords": ["fastapi", "your-domain-entity", "your-business-logic"]
   ```

2. **File Paths**: Match your directory structure (app/ vs src/ vs api/)
   ```json
   "filePaths": [
     "**/your-api-dir/**/*.py",
     "**/your-services-dir/**/*.py",
     "**/your-routers-dir/**/*.py"
   ]
   ```

3. **Intent Patterns**: Add your common phrases
   ```json
   "intentPatterns": [
     "how do I.*?in this project",
     "create.*?following our patterns",
     "(async|asynchronous).*?(endpoint|task)"
   ]
   ```

### Test Skill Activation

In Claude Code, type:
```
I want to add a new API endpoint for posts
```

Expected: Claude suggests `/backend-dev-guidelines` skill

### Checkpoint 2

✅ Skill directory copied
✅ skill-rules.json configured
✅ Skill activates on relevant prompts
✅ Skill content is relevant to your stack

---

## Phase 3: Verification (5 minutes)

### Test Complete Workflow

1. **Test Auto-Activation**:
   ```
   Prompt: "I need to add a new FastAPI route"
   Expected: Skill suggestion appears
   ```

2. **Test Manual Invocation**:
   ```
   /backend-dev-guidelines
   Expected: Skill content loads
   ```

3. **Test File-Based Activation**:
   - Open a file matching your file patterns (e.g., `app/routes/posts.py`)
   - Type a relevant prompt
   - Expected: Skill suggestion appears

4. **Test Post-Edit Suggestions**:
   - Edit a Python file
   - Expected: Post-tool-use tracker suggests improvements

### Common Issues

**Hook not running**:
```bash
# Check Python executable
which python3

# Test hook directly
python3 .claude/hooks/skill-activation-prompt.py
```

**Skill not suggested**:
```bash
# Verify skill-rules.json is valid JSON
python3 -c "import json; print(json.load(open('.claude/skills/skill-rules.json')))"

# Check keyword matches (they're case-insensitive)
```

**Import errors**:
```bash
# Ensure all dependencies installed
pip list | grep -E "(mypy|ruff)"
```

### Checkpoint 3

✅ Auto-activation works
✅ Manual invocation works
✅ File-based activation works
✅ Post-edit suggestions appear

---

## Phase 4: Expand (Optional)

### Add More Skills

```bash
# Copy additional skills as needed
cp -r .claude/skills/skill-developer /path/to/your-project/.claude/skills/
cp -r .claude/skills/route-tester /path/to/your-project/.claude/skills/

# Update skill-rules.json with new entries
```

### Add Agents

```bash
cp -r .claude/agents/ /path/to/your-project/.claude/agents/
```

### Add Slash Commands

```bash
cp -r .claude/commands/ /path/to/your-project/.claude/commands/
```

### Add Type Checking Hook (Optional)

Update `.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": "python .claude/hooks/skill-activation-prompt.py",
    "PostToolUse": "python .claude/hooks/post-tool-use-tracker.py",
    "Stop": "python .claude/hooks/mypy-check.py"
  }
}
```

Create `mypy.ini` or add to `pyproject.toml`:
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

---

## Customization Examples

### Example 1: E-commerce FastAPI Project

Update `skill-rules.json`:
```json
{
  "keywords": [
    "fastapi",
    "order",
    "product",
    "cart",
    "checkout",
    "payment",
    "inventory"
  ],
  "filePaths": [
    "**/api/orders/**/*.py",
    "**/api/products/**/*.py",
    "**/services/payment/**/*.py"
  ]
}
```

### Example 2: Add Project-Specific Patterns

Create a new skill:
```bash
mkdir -p .claude/skills/project-patterns
```

`.claude/skills/project-patterns/SKILL.md`:
```markdown
# Project-Specific Patterns

## Our Conventions

### 1. Service Classes
All services must inherit from BaseService...

### 2. Error Handling
We use custom exceptions...

### 3. Database Transactions
Always use @transaction.atomic...
```

Add to `skill-rules.json`:
```json
{
  "name": "project-patterns",
  "type": "block",
  "priority": "critical",
  "keywords": ["service", "create", "new"],
  "message": "⚠️ Please review /project-patterns before creating new services"
}
```

---

## Git Integration

### Add to .gitignore

```bash
# .gitignore
.claude/settings.local.json
.claude/hooks/__pycache__/
dev/active/
```

### Commit Infrastructure

```bash
git add .claude/
git commit -m "Add Claude Code infrastructure

- Python hooks for skill activation
- Backend development guidelines skill
- Agent configurations
- Slash commands

Enables automatic skill suggestions based on context."
```

---

## Team Rollout

### 1. Share with Team

```bash
# Create quick start for team
cat > CLAUDE_QUICKSTART.md << 'EOF'
# Claude Code Quick Start

1. Ensure Python 3.8+ installed
2. Run: `pip install -r .claude/hooks/requirements.txt`
3. Open project in Claude Code
4. Try: "I want to add a new endpoint"
5. Follow skill suggestions

See CLAUDE_INTEGRATION_GUIDE.md for details.
EOF
```

### 2. Customize for Team Conventions

Update skills with your team's:
- Naming conventions
- Code style preferences
- Testing patterns
- Deployment procedures

### 3. Create Team-Specific Skills

Example:
```bash
mkdir .claude/skills/deployment-guide
```

Document your deployment process as a skill so Claude can guide developers through it.

---

## Troubleshooting

### Hook Execution Errors

```bash
# Enable debug logging
export CLAUDE_HOOK_DEBUG=1

# Check hook output
python3 .claude/hooks/skill-activation-prompt.py < test-input.json
```

### Performance Issues

If hooks are slow:
1. Check Python version (3.10+ is faster)
2. Consider using compiled regex in hooks
3. Limit skill-rules.json size

### Skills Not Loading

```bash
# Verify file exists
ls -la .claude/skills/*/SKILL.md

# Check skill-rules.json syntax
python3 -m json.tool .claude/skills/skill-rules.json
```

---

## Success Metrics

After integration, you should see:
- ✅ Skill suggestions appear automatically
- ✅ Fewer repeated questions about patterns
- ✅ Consistent code structure across features
- ✅ Faster onboarding for new developers
- ✅ Self-documenting development practices

---

## Next Steps

1. ✅ Complete Phase 1-3 integration
2. Create project-specific skills
3. Share with team
4. Iterate on patterns based on usage
5. Contribute improvements back to showcase

## Support

For issues or questions:
- Check `README.md` for patterns
- Review `.claude/hooks/README.md` for hook details
- Consult `.claude/skills/skill-developer/` for creating skills

---

**Ready to start?** Copy and paste this entire guide into Claude Code and say "Help me integrate Phase 1" to begin with AI assistance.
