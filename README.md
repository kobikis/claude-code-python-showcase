# Claude Code Python Infrastructure Showcase

> **Production-tested patterns for Claude Code in FastAPI projects**
> Extracted from real-world FastAPI microservices development

## What This Is

This is a **reference library**, not a working application. It contains reusable infrastructure components that solve the fundamental Claude Code challenge: **skills don't activate automatically**.

After 6 months of FastAPI development with Claude Code, these patterns emerged as essential for maintaining efficient, context-aware AI assistance.

## The Core Problem It Solves

**Without this infrastructure:**
- You manually invoke skills: `/backend-guidelines`, `/test-pattern`, etc.
- Claude doesn't know your project's conventions
- You repeat the same instructions every session
- Skills sit unused while you forget they exist

**With this infrastructure:**
- Skills activate when you need them, not when you remember them
- Claude suggests relevant patterns based on your prompt and file context
- Your project conventions become enforceable guardrails
- Development patterns stay consistent across your team

## What's Included

### Essential Components (Start Here)

**1. Auto-Activation System**
- Hooks analyze prompts and file paths to suggest relevant skills
- Configured via `.claude/skills/skill-rules.json`
- Works with Python file patterns: `**/api/**/*.py`, `**/tests/**/*.py`, etc.

**2. Production Skills**
- **backend-dev-guidelines**: FastAPI patterns, SQLAlchemy, Alembic, Kafka, async/await, testing
- **skill-developer**: Meta-skill for creating new skills
- **route-tester**: pytest patterns for FastAPI testing
- **error-tracking**: Sentry integration for FastAPI

**3. Core Hooks**
- **skill-activation-prompt**: Suggests skills based on context (Python implementation)
- **post-tool-use-tracker**: Tracks edit patterns and suggests improvements
- **mypy-check**: Type checking on session stop
- **pytest-runner**: Test validation hooks

### Advanced Components

**10 Specialized Agents**
- Architecture reviewers for Python services
- Refactoring experts for legacy Python code
- Vapi.ai voice AI integration expert
- Documentation generators
- Error resolution specialists

**Slash Commands**
- `/dev-docs`: Structured development documentation
- `/api-spec`: OpenAPI/Swagger generation
- `/test-coverage`: Coverage analysis and improvement

**MCP Server Integration** 🆕
- **Task Master AI**: AI-powered task management, PRD parsing, and research
- **PostgreSQL**: Direct database access for queries and schema inspection
- **Sequential Thinking**: Enhanced reasoning for complex problems
- **Playwright**: Browser automation and E2E testing

See [MCP_SETUP.md](MCP_SETUP.md) for full setup guide and usage examples.

## Quick Integration Guide

### Phase 1: Core Hooks (15 minutes)

1. Copy `.claude/hooks/skill-activation-prompt.py` to your project
2. Copy `.claude/hooks/post-tool-use-tracker.py` to your project
3. Update `.claude/settings.json` to enable hooks
4. Install Python dependencies: `pip install -r .claude/hooks/requirements.txt`

### Phase 2: First Skill (10 minutes)

1. Choose a skill that matches your stack (FastAPI, Django, Flask)
2. Copy the skill directory to `.claude/skills/`
3. Customize the skill rules in `skill-rules.json`
4. Test by typing a prompt that should trigger it

### Phase 3: Verification (5 minutes)

Type: "I need to add a new API endpoint"
- Expected: Claude suggests `/backend-dev-guidelines` skill
- If not working: Check hook execution in settings

### Phase 4: Expand (Optional)

Add agents, commands, or create custom skills using the skill-developer pattern.

## Updating an Existing Installation

If you've already installed this infrastructure and want to update:

### Quick Update

```bash
# Update all components (creates automatic backup)
./update_component.sh /path/to/your/target/project all

# Update only specific components
./update_component.sh /path/to/your/target/project skills
./update_component.sh /path/to/your/target/project agents
./update_component.sh /path/to/your/target/project mcp
```

### What's New
- ✅ **New Skills**: route-tester (pytest patterns), error-tracking (Sentry)
- ✅ **New Agent**: vapi-ai-expert (Voice AI integration)
- ✅ **MCP Support**: Task Master AI for task management and research
- ✅ **Documentation**: MCP_SETUP.md, UPDATE_TARGET_PROJECT.md

See [UPDATE_TARGET_PROJECT.md](UPDATE_TARGET_PROJECT.md) for detailed update instructions and manual update steps.

## Key Patterns

### The 500-Line Rule

Skills follow a modular structure:
- Main `SKILL.md` file stays under 500 lines (overview + navigation)
- Detailed patterns go in `resources/*.md` files
- Claude loads content progressively, avoiding context limits

### Progressive Disclosure

```
User Prompt → Hook Analysis → Skill Suggestion → Load Main Guide → Load Specific Resource
```

This prevents "context explosion" while keeping all knowledge accessible.

### FastAPI-Specific Conventions

All patterns are adapted for FastAPI:
- Async/await patterns
- Pydantic v2 for validation
- Dependency injection
- SQLAlchemy 2.0 with async support
- Kafka event streaming (aiokafka)
- pytest with pytest-asyncio
- Type hints everywhere
- OpenAPI/Swagger documentation
- Background tasks
- ASGI deployment

## Integration Example

```json
// .claude/settings.json
{
  "hooks": {
    "UserPromptSubmit": "python .claude/hooks/skill-activation-prompt.py",
    "PostToolUse": "python .claude/hooks/post-tool-use-tracker.py",
    "Stop": "python .claude/hooks/mypy-check.py"
  }
}
```

```json
// .claude/skills/skill-rules.json (excerpt)
{
  "skills": [
    {
      "name": "backend-dev-guidelines",
      "type": "suggest",
      "priority": "high",
      "keywords": ["fastapi", "endpoint", "router", "async", "pydantic", "sqlalchemy"],
      "intentPatterns": [
        "(create|add|implement).*?(route|endpoint|api)",
        "(async|asynchronous).*?(function|endpoint)"
      ],
      "filePaths": ["**/api/**/*.py", "**/routers/**/*.py", "**/routes/**/*.py"]
    }
  ]
}
```

## File Structure

```
.claude/
├── settings.json              # Main configuration
├── settings.local.json        # Environment-specific overrides
├── hooks/
│   ├── skill-activation-prompt.py
│   ├── post-tool-use-tracker.py
│   ├── mypy-check.py
│   └── requirements.txt
├── skills/
│   ├── skill-rules.json
│   ├── backend-dev-guidelines/
│   │   ├── SKILL.md
│   │   └── resources/
│   ├── frontend-dev-guidelines/
│   ├── skill-developer/
│   ├── route-tester/
│   └── error-tracking/
├── agents/
│   ├── architecture-reviewer.md
│   ├── refactor-planner.md
│   └── ...
└── commands/
    ├── dev-docs.md
    └── api-spec.md

dev/
└── active/
    └── current-feature/
        ├── TASK.md
        ├── CONTEXT.md
        └── PLAN.md
```

## Customization Guide

### Adapt for Your Domain

1. **Update Keywords**: Edit `skill-rules.json` with your domain entities and business logic terms
2. **File Patterns**: Match your project structure (`src/`, `app/`, `api/`)
3. **Code Examples**: Add your domain-specific examples to skills
4. **Project Patterns**: Create custom skills for your unique workflows

### Example Domain

The skills use a generic blog API (Post/Comment/User) for teaching purposes. Replace with your domain:

```python
# Blog domain example:
class Post(Base):
    __tablename__ = "posts"
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)

# Your domain example (e-commerce):
class Product(Base):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
```

## Important Notes

**This is NOT a copy-paste solution**. The `settings.json` uses example structures. You must:
- Match your actual directory layout (app/ vs src/ vs api/)
- Use your domain entities and business logic
- Customize keywords and file patterns
- Adapt for your team's conventions

**Token Management**: The modular design keeps Claude's context under control. Even large FastAPI codebases stay manageable.

**Hook Performance**: Python hooks add ~100-200ms per prompt. Perfect for FastAPI development workflows.

## Integration Timeline

- **Phase 1**: 15 minutes (essential hooks)
- **Phase 2**: 10 minutes (first skill)
- **Phase 3**: 5 minutes (testing)
- **Phase 4**: As needed (advanced features)

## Support & Contributions

This is a living reference library. Patterns evolve as Claude Code capabilities expand.

**Feedback**: Open issues for pattern improvements or Python-specific edge cases

**Contributions**: PRs welcome for new skills, agents, or hooks

## License

MIT - Use freely in your projects

---

**Ready to integrate?** Start with `CLAUDE_INTEGRATION_GUIDE.md` for step-by-step AI-assisted setup.
