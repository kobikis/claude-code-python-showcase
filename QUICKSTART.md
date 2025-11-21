# Quick Start Guide

Get up and running with Claude Code FastAPI infrastructure in 5 minutes.

## Prerequisites

- Python 3.8+
- FastAPI project (or starting a new one)
- pip or poetry
- Claude Code installed

## Installation

### 1. Copy to Your Project

```bash
# Navigate to your Python project
cd /path/to/your-project

# Copy the .claude directory
cp -r /path/to/claude-code-python-showcase/.claude .

# Make hooks executable (Unix/Mac)
chmod +x .claude/hooks/*.py
```

### 2. Install Dependencies

```bash
# Option A: Using pip
pip install -r .claude/hooks/requirements.txt

# Option B: Using poetry
poetry add --group dev mypy ruff
```

### 3. Verify Installation

```bash
# Test the skill activation hook
echo '{"prompt": "I want to add a new FastAPI endpoint", "projectRoot": "."}' | \
  python .claude/hooks/skill-activation-prompt.py
```

Expected output:
```
💡 Relevant Skills Detected

💡 The /backend-dev-guidelines skill provides Python backend patterns...
```

## First Use

### 1. Start Claude Code

Open your project in Claude Code.

### 2. Trigger a Skill

Type in Claude Code:
```
I want to add a new API endpoint
```

You should see a skill suggestion appear automatically!

### 3. Use the Skill

Click or type:
```
/backend-dev-guidelines
```

The skill will load with patterns and best practices.

## Next Steps

✅ **Customize for your project**: Edit `.claude/skills/skill-rules.json` to match your domain and conventions

✅ **Add more skills**: Copy additional skills from the showcase

✅ **Create project-specific skills**: Use `/skill-developer` to create custom skills for your team

✅ **Read the full guide**: See `CLAUDE_INTEGRATION_GUIDE.md` for detailed integration instructions

## Common Issues

**Hook not running?**
- Check Python path: `which python3`
- Verify settings.json syntax
- Make hooks executable: `chmod +x .claude/hooks/*.py`

**Skills not suggested?**
- Verify skill-rules.json is valid JSON
- Check keywords match your prompts (case-insensitive)
- Ensure file paths match your project structure

**Import errors?**
- Install dependencies: `pip install -r .claude/hooks/requirements.txt`

## Need Help?

- Read the [full README](README.md)
- Check the [integration guide](CLAUDE_INTEGRATION_GUIDE.md)
- Review example [dev docs](dev/active/example-feature/)

## What's Next?

After basic setup:
1. Customize skill rules for your project
2. Add agents for specialized tasks
3. Create slash commands for common workflows
4. Share with your team

Happy coding with Claude! 🚀
