# Project Structure - FastAPI Infrastructure Showcase

Complete file structure of the Claude Code FastAPI Infrastructure Showcase.

## Directory Tree

```
claude-code-python-showcase/
├── README.md                           # Main documentation
├── QUICKSTART.md                       # 5-minute quick start guide
├── CLAUDE_INTEGRATION_GUIDE.md         # Detailed integration instructions
├── MCP_SETUP.md                        # MCP server setup and configuration guide
├── PROJECT_STRUCTURE.md                # This file
├── LICENSE                             # MIT License
├── .gitignore                          # Git ignore patterns
├── .env.example                        # Environment variables template
│
├── .claude/                            # Claude Code configuration
│   ├── settings.json                   # Main settings
│   ├── settings.local.json             # Local overrides (gitignored)
│   │
│   ├── hooks/                          # Python hooks for automation
│   │   ├── README.md                   # Hook documentation
│   │   ├── skill-activation-prompt.py  # Auto-suggest skills (Essential)
│   │   ├── post-tool-use-tracker.py    # Post-edit suggestions (Essential)
│   │   ├── mypy-check.py               # Type checking on stop (Optional)
│   │   └── requirements.txt            # Hook dependencies
│   │
│   ├── skills/                         # Skill definitions
│   │   ├── skill-rules.json            # Activation rules for all skills
│   │   │
│   │   ├── backend-dev-guidelines/     # FastAPI patterns exclusively
│   │   │   ├── SKILL.md                # Main guide (~500 lines)
│   │   │   └── resources/              # Detailed sub-topics
│   │   │       ├── fastapi-patterns.md
│   │   │       ├── pytest-guide.md
│   │   │       ├── sqlalchemy-async-guide.md (planned)
│   │   │       ├── alembic-guide.md (planned)
│   │   │       ├── auth-patterns.md (planned)
│   │   │       └── background-tasks.md (planned)
│   │   │
│   │   ├── skill-developer/            # Meta-skill for creating skills
│   │   │   ├── SKILL.md                # Skill creation guide
│   │   │   └── resources/ (planned)
│   │   │
│   │   ├── route-tester/               # pytest-asyncio testing patterns
│   │   │   └── SKILL.md                # Complete testing guide
│   │   │
│   │   └── error-tracking/             # Sentry + FastAPI middleware
│   │       └── SKILL.md                # Complete error tracking guide
│   │
│   ├── agents/                         # Specialized agent configs
│   │   ├── README.md                   # Agent documentation
│   │   ├── architecture-reviewer.md    # Review system architecture
│   │   ├── refactor-planner.md         # Plan large refactorings
│   │   ├── vapi-ai-expert.md           # Vapi.ai voice AI integration
│   │   ├── code-refactor-master.md (planned)
│   │   ├── python-code-reviewer.md (planned)
│   │   ├── auto-error-resolver.md (planned)
│   │   ├── api-debugger.md (planned)
│   │   ├── documentation-architect.md (planned)
│   │   ├── api-documenter.md (planned)
│   │   ├── test-coverage-improver.md (planned)
│   │   └── api-tester.md (planned)
│   │
│   └── commands/                       # Slash commands
│       ├── README.md                   # Command documentation
│       ├── dev-docs.md                 # Create dev documentation structure
│       ├── api-spec.md (planned)       # Generate OpenAPI specs
│       └── test-coverage.md (planned)  # Coverage analysis
│
├── dev/                                # Development documentation
│   └── active/                         # Active feature development
│       └── example-feature/            # Example feature documentation
│           ├── TASK.md                 # What and why
│           ├── CONTEXT.md              # Current state and constraints
│           └── PLAN.md                 # How to implement
│
└── examples/                           # Example code (planned)
    ├── fastapi-crud-api/
    ├── fastapi-microservice/
    └── fastapi-with-celery/
```

## File Counts

- **Hooks**: 3 Python implementations + README + requirements.txt
- **Skills**: 5 skills (4 fully implemented, 1 planned)
- **Agents**: 11 agent configs (3 implemented, 8 planned)
- **Commands**: 3 slash commands (1 implemented, 2 planned)
- **Documentation**: 9 markdown files (including MCP_SETUP.md)
- **MCP Servers**: 4 configured (PostgreSQL, Sequential Thinking, Playwright, Task Master AI)
- **Configuration**: .env.example with MCP and FastAPI settings
- **Examples**: 1 complete example (dev/active/example-feature)

## Implementation Status

### ✅ Complete

**Core Infrastructure**:
- Settings and configuration
- Python hooks (skill activation, post-tool-use tracker, mypy check)
- Skill rules configuration
- Integration guides
- MCP server configuration (4 servers)
- Environment variable templates

**Skills**:
- backend-dev-guidelines (main + 2 resources)
- skill-developer (complete)
- route-tester (complete testing guide)
- error-tracking (complete error tracking guide)

**Agents**:
- architecture-reviewer
- refactor-planner
- vapi-ai-expert

**Commands**:
- dev-docs

**MCP Servers**:
- Task Master AI (task management, PRD parsing, AI research)
- PostgreSQL (database access)
- Sequential Thinking (enhanced reasoning)
- Playwright (browser automation)

**Documentation**:
- MCP_SETUP.md (complete setup guide)
- .env.example (environment configuration)

**Examples**:
- Complete feature development example (TASK/CONTEXT/PLAN)

### 📝 Planned (Easy to Add)

**Skills**:
- frontend-dev-guidelines

**Resources**:
- sqlalchemy-guide.md
- alembic-guide.md
- auth-patterns.md
- django-patterns.md
- async-patterns.md
- db-optimization.md

**Agents**:
- code-refactor-master
- python-code-reviewer
- auto-error-resolver
- api-debugger
- documentation-architect
- api-documenter
- test-coverage-improver
- api-tester

**Commands**:
- api-spec
- test-coverage

**Examples**:
- fastapi-project
- django-project
- flask-project

## Key Components Explained

### Essential Files (Must Have)

1. **`.claude/settings.json`**: Main configuration
2. **`.claude/hooks/skill-activation-prompt.py`**: Auto-suggests skills
3. **`.claude/skills/skill-rules.json`**: Defines when skills activate
4. **`.claude/skills/backend-dev-guidelines/SKILL.md`**: Core patterns

### Optional but Recommended

1. **`.claude/hooks/post-tool-use-tracker.py`**: Post-edit suggestions
2. **`.claude/agents/`**: For complex tasks
3. **`.claude/commands/`**: For common workflows
4. **`dev/active/`**: For feature documentation

### Customization Points

1. **`skill-rules.json`**: Add your frameworks, file paths, keywords
2. **`SKILL.md` files**: Customize patterns for your team
3. **Agent configs**: Add project-specific agents
4. **Commands**: Create workflow shortcuts

## File Size Guidelines

- **SKILL.md**: Keep under 500 lines
- **Resource files**: No limit (progressive disclosure)
- **Hooks**: Keep fast (< 200ms execution)
- **Agent configs**: Comprehensive (they run autonomously)

## Adding New Components

### Add a Skill

```bash
mkdir -p .claude/skills/my-skill/resources
touch .claude/skills/my-skill/SKILL.md
# Add entry to skill-rules.json
```

### Add an Agent

```bash
touch .claude/agents/my-agent.md
# Define agent role and capabilities
```

### Add a Command

```bash
touch .claude/commands/my-command.md
# Document command behavior
```

## Navigation Tips

**Starting point**: `README.md`
**Quick setup**: `QUICKSTART.md`
**Detailed integration**: `CLAUDE_INTEGRATION_GUIDE.md`
**MCP server setup**: `MCP_SETUP.md`
**Environment config**: `.env.example`
**Creating skills**: `.claude/skills/skill-developer/SKILL.md`
**Hook details**: `.claude/hooks/README.md`
**Example feature**: `dev/active/example-feature/`

## Maintenance

### Regular Updates

- Keep skill patterns current with framework updates
- Update keywords in skill-rules.json as your team's vocabulary evolves
- Add new skills for emerging patterns
- Archive old dev/active/ docs to dev/archive/

### Team Collaboration

- Commit `.claude/` directory to git
- Exclude `settings.local.json` (in .gitignore)
- Exclude `dev/active/` (in .gitignore)
- Document customizations in comments

## Size and Performance

- **Total files**: ~30 files (with planned additions: ~50)
- **Disk space**: < 1 MB
- **Hook overhead**: ~100-200ms per prompt
- **Memory usage**: Minimal (hooks are stateless)

## License

All files: MIT License (see LICENSE file)
