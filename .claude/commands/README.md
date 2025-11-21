# Claude Code Slash Commands

Custom commands for common development workflows.

## Available Commands

### /dev-docs [feature-name]
Creates structured development documentation (TASK.md, CONTEXT.md, PLAN.md) for tracking complex features.

**Usage**: `/dev-docs user-authentication`

**When to use**:
- Starting a complex feature
- Planning a refactoring
- Documenting a tricky bug fix
- Onboarding someone to a feature

### /api-spec [module-name]
Generates OpenAPI/Swagger specification from FastAPI routes or Django views.

**Usage**: `/api-spec posts`

**Output**: OpenAPI YAML/JSON specification

### /test-coverage [module-name]
Analyzes test coverage and suggests improvements for a specific module.

**Usage**: `/test-coverage app.services.post_service`

**Output**: Coverage report + suggestions

## Creating Custom Commands

1. Create a new `.md` file in `.claude/commands/`
2. Define the command behavior
3. Document usage and examples

Example command file:

```markdown
# /my-command - Description

What this command does...

## Usage
\```
/my-command [args]
\```

## Example
\```
/my-command example-input
\```

## Output
What the user should expect
```

## Command Naming Conventions

- Use kebab-case: `/api-spec` not `/apiSpec`
- Keep names short and memorable
- Use verbs for actions: `/generate-docs`, `/run-tests`
- Use nouns for queries: `/coverage`, `/status`
