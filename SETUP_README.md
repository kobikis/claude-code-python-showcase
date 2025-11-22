# Claude Code Infrastructure Setup Script

Automated setup script to apply production-ready Claude Code infrastructure to your FastAPI projects.

## What This Script Does

This script installs:

1. **Skills** - Domain-specific patterns and guidelines
   - webhook-security
   - api-security
   - resilience-patterns
   - async-kafka
   - pydantic-v2-migration
   - event-driven-patterns

2. **Agents** - Specialized code reviewers
   - webhook-validator
   - kafka-optimizer
   - security-auditor
   - async-converter

3. **Slash Commands** - Productivity commands
   - /check-prod-readiness
   - /kafka-health
   - /webhook-test
   - /security-scan
   - /migrate-pydantic-v2

4. **Hooks** - Automated quality checks
   - pre-commit (linting, formatting, security)
   - complexity-detector (cyclomatic complexity)
   - dependency-checker (vulnerability scanning)

5. **Examples** - Production-ready implementations
   - Circuit breaker pattern
   - Idempotency middleware
   - Webhook signature verification
   - Async Kafka producer
   - Base service pattern

## Quick Start

### Interactive Mode (Recommended)

```bash
python setup_target_project.py --target /path/to/your/project
```

Follow the interactive menu to select components.

### Install Everything

```bash
python setup_target_project.py --target /path/to/your/project --all
```

### Install Specific Components

```bash
# Just skills
python setup_target_project.py --target /path/to/your/project --component skills

# Just agents
python setup_target_project.py --target /path/to/your/project --component agents

# Just commands
python setup_target_project.py --target /path/to/your/project --component commands

# Just hooks
python setup_target_project.py --target /path/to/your/project --component hooks

# Just examples
python setup_target_project.py --target /path/to/your/project --component examples

# Just update dependencies
python setup_target_project.py --target /path/to/your/project --component deps
```

### Non-Interactive Mode

```bash
python setup_target_project.py \
  --target /path/to/your/project \
  --component skills \
  --non-interactive
```

## Requirements

- Python 3.11+
- Target project must exist
- Write access to target project directory

## What Gets Created

```
your-project/
├── .claude/
│   ├── README.md                    # Setup documentation
│   ├── skills/
│   │   ├── skill-rules.json         # Auto-activation rules
│   │   ├── webhook-security/
│   │   │   ├── SKILL.md
│   │   │   └── resources/
│   │   ├── api-security/
│   │   ├── resilience-patterns/
│   │   ├── async-kafka/
│   │   ├── pydantic-v2-migration/
│   │   └── event-driven-patterns/
│   ├── agents/
│   │   ├── webhook-validator.md
│   │   ├── kafka-optimizer.md
│   │   ├── security-auditor.md
│   │   └── async-converter.md
│   ├── commands/
│   │   ├── check-prod-readiness.md
│   │   ├── kafka-health.md
│   │   ├── webhook-test.md
│   │   ├── security-scan.md
│   │   └── migrate-pydantic-v2.md
│   └── hooks/
│       ├── pre-commit.py
│       ├── complexity-detector.py
│       └── dependency-checker.py
├── examples/
│   └── claude_patterns/
│       ├── __init__.py
│       ├── circuit_breaker.py
│       ├── idempotency.py
│       ├── webhook_verifier.py
│       ├── async_kafka.py
│       └── base_service.py
└── requirements.txt                  # Updated with new dependencies
```

## Backup

All changes are automatically backed up to:
```
your-project/.claude_backup/<timestamp>/
```

You can safely rollback changes if needed.

## Post-Installation Steps

1. **Install Dependencies**
   ```bash
   cd /path/to/your/project
   pip install -r requirements.txt
   ```

2. **Review Generated Files**
   ```bash
   cat .claude/README.md
   ```

3. **Test Skill Activation**
   Open Claude Code and type:
   ```
   I need to add webhook signature verification
   ```

   Claude should suggest the webhook-security skill.

4. **Test Commands**
   ```
   /check-prod-readiness
   /kafka-health
   ```

5. **Review Examples**
   ```bash
   ls examples/claude_patterns/
   ```

## Customization

After installation, customize for your project:

### 1. Update Skill Rules

Edit `.claude/skills/skill-rules.json`:
```json
{
  "keywords": ["your", "domain", "specific", "keywords"],
  "intentPatterns": ["your.*patterns"],
  "filePaths": ["your/project/structure/**/*.py"]
}
```

### 2. Customize Skills

Edit skill files in `.claude/skills/*/SKILL.md` to add your domain-specific examples.

### 3. Configure Hooks

Update `.claude/settings.json` to enable/disable hooks:
```json
{
  "hooks": {
    "UserPromptSubmit": "python .claude/hooks/skill-activation-prompt.py",
    "PostToolUse": "python .claude/hooks/post-tool-use-tracker.py",
    "Stop": "python .claude/hooks/mypy-check.py"
  }
}
```

### 4. Add Custom Skills

Use the `/skill-developer` skill to create new custom skills:
```
Create a new skill for our payment processing patterns
```

## Integration with Existing Project

The script is safe to run on existing projects:

- ✅ Preserves existing `.claude` directory structure
- ✅ Backs up before making changes
- ✅ Merges with existing skill-rules.json
- ✅ Appends to requirements.txt (doesn't overwrite)
- ✅ Creates .claude directory if it doesn't exist

## Troubleshooting

### Script Fails with "Target project not found"

Ensure the path is correct and absolute:
```bash
python setup_target_project.py --target "$(pwd)/../my-project"
```

### Import Errors

The generator modules must be in the same directory as the script:
```
claude-code-python-showcase/
├── setup_target_project.py
├── skills_generator.py
├── agents_generator.py
├── commands_generator.py
├── hooks_generator.py
└── examples_generator.py
```

### Permission Errors

Ensure you have write access to the target directory:
```bash
chmod u+w /path/to/your/project/.claude
```

### Hooks Not Executing

1. Check hooks are executable:
   ```bash
   chmod +x .claude/hooks/*.py
   ```

2. Verify Python path in hook shebang:
   ```bash
   which python3
   ```

3. Check `.claude/settings.json` has hooks configured

## Example Run

```bash
$ python setup_target_project.py --target ~/projects/my-api

================================================================================
              Claude Code Infrastructure Setup
================================================================================

Target Project: /Users/you/projects/my-api
Source: /Users/you/claude-code-python-showcase

Select components to install:
  1. Skills (webhook-security, api-security, etc.)
  2. Agents (webhook-validator, security-auditor, etc.)
  3. Slash Commands (/check-prod-readiness, etc.)
  4. Hooks (pre-commit, complexity-detector, etc.)
  5. Example Implementations
  6. Update Dependencies
  7. All of the above
  0. Exit

Enter your choice (0-7): 7

================================================================================
                       Installing Skills
================================================================================

ℹ Creating skill: webhook-security
✓ Skill created: webhook-security
ℹ Creating skill: api-security
✓ Skill created: api-security
...

================================================================================
                    Installing Custom Agents
================================================================================

ℹ Creating agent: webhook-validator
✓ Agent created: webhook-validator
...

================================================================================
                       Setup Complete
================================================================================

✓ Claude Code infrastructure installed successfully!
ℹ Backup location: /Users/you/projects/my-api/.claude_backup/20250122_143022
ℹ Next steps:
  1. pip install -r requirements.txt
  2. Review .claude/README.md
  3. Test with: 'I need to add webhook signature verification'
```

## Support

For issues or questions:
1. Check the generated `.claude/README.md` in your project
2. Review the skills in `.claude/skills/`
3. Open an issue in the showcase repository

## License

MIT - Use freely in your projects
