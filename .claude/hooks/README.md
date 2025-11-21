# Claude Code Hooks - Python Implementation

This directory contains Python-based hooks for Claude Code that automate various development workflows.

## Available Hooks

### 1. skill-activation-prompt.py (Essential)

**Trigger**: `UserPromptSubmit`
**Purpose**: Analyzes user prompts and suggests relevant skills automatically

**How it works**:
- Parses user prompts for keywords and intent patterns
- Checks active file paths against skill rules
- Suggests or blocks based on skill configuration
- Respects skip markers and environment variables

**Configuration**: Edit `.claude/skills/skill-rules.json` to customize

### 2. post-tool-use-tracker.py (Essential)

**Trigger**: `PostToolUse`
**Purpose**: Tracks file edits and suggests improvements

**Features**:
- Detects missing type hints in Python functions
- Reminds about test coverage
- Suggests import organization
- Checks for SQLAlchemy and FastAPI patterns
- Prompts for dependency installation after config changes

### 3. mypy-check.py (Optional)

**Trigger**: `Stop`
**Purpose**: Runs type checking when session ends

**Features**:
- Runs mypy on project
- Shows first 10 type errors
- Skips if no mypy configuration found
- Non-blocking (won't prevent session end)

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Make hooks executable** (Unix/Mac):
   ```bash
   chmod +x .claude/hooks/*.py
   ```

3. **Configure in settings.json**:
   ```json
   {
     "hooks": {
       "UserPromptSubmit": "python .claude/hooks/skill-activation-prompt.py",
       "PostToolUse": "python .claude/hooks/post-tool-use-tracker.py",
       "Stop": "python .claude/hooks/mypy-check.py"
     }
   }
   ```

## Testing Hooks

Test skill activation:
```bash
echo '{"prompt": "I want to add a new FastAPI endpoint", "projectRoot": "."}' | \
  python .claude/hooks/skill-activation-prompt.py
```

Test post-tool-use tracker:
```bash
echo '{"tool": "Edit", "file_path": "app/main.py", "new_content": "def hello(): pass"}' | \
  python .claude/hooks/post-tool-use-tracker.py
```

## Customization

### Adding New Checks to post-tool-use-tracker.py

```python
def check_python_file(tool_data, path):
    suggestions = []

    # Add your custom check
    content = tool_data.get("new_content", "")
    if "async def" in content and "await" not in content:
        suggestions.append(
            "⚠️ Async function without await - consider using sync function"
        )

    return suggestions
```

### Adding New Skill Rules

Edit `.claude/skills/skill-rules.json`:

```json
{
  "name": "my-custom-skill",
  "type": "suggest",
  "priority": "high",
  "keywords": ["celery", "task", "queue"],
  "intentPatterns": ["(create|add).*?task"],
  "filePaths": ["**/tasks/**/*.py"]
}
```

## Performance

- **skill-activation-prompt.py**: ~100-200ms per prompt
- **post-tool-use-tracker.py**: ~50-100ms per edit
- **mypy-check.py**: ~2-10s depending on project size

Python hooks are slightly slower than TypeScript equivalents but offer:
- No build step required
- Easier to read and customize
- Native Python tooling integration
- Better type hint analysis

## Troubleshooting

### Hook not running

1. Check hook is executable: `ls -l .claude/hooks/*.py`
2. Verify Python path: `which python3`
3. Check settings.json syntax
4. Look for errors in Claude Code output

### Skill suggestions not appearing

1. Verify skill-rules.json is valid JSON
2. Check keyword matches are lowercase
3. Test regex patterns at regex101.com
4. Enable debug logging in settings.local.json

### Type checking fails

1. Install mypy: `pip install mypy`
2. Create mypy.ini or add to pyproject.toml
3. Ignore slow checks with `# type: ignore` comments

## Examples

See `CONFIG.md` for detailed configuration examples and advanced patterns.

## Migration from TypeScript

If migrating from TypeScript hooks:

1. Both implementations are compatible
2. Python hooks are easier to debug
3. Can mix Python and TypeScript hooks
4. Use Python for Python-specific checks
5. Use TypeScript for speed-critical hooks

## Contributing

When adding new hooks:
- Follow existing naming conventions
- Add error handling (don't block users)
- Keep execution time under 200ms
- Document in this README
- Add tests in examples/

## License

MIT
