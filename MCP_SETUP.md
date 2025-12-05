# MCP Server Setup Guide

> **Model Context Protocol (MCP) Servers** extend Claude Code with additional capabilities through standardized integrations.

This project includes configurations for multiple MCP servers to enhance your development workflow with databases, testing, task management, and AI research capabilities.

---

## Table of Contents

1. [What are MCP Servers?](#what-are-mcp-servers)
2. [Installed MCP Servers](#installed-mcp-servers)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

---

## What are MCP Servers?

MCP (Model Context Protocol) servers are external tools that Claude Code can communicate with to:
- Access databases and external services
- Execute browser automation
- Manage tasks and project requirements
- Perform AI-powered research
- And much more

Each MCP server runs as a separate process and communicates with Claude Code through a standardized protocol.

---

## Installed MCP Servers

This project includes configuration for **5 MCP servers**:

### 1. PostgreSQL Server
**Purpose**: Direct PostgreSQL database access for queries and schema inspection

**Capabilities**:
- Execute SQL queries
- Inspect database schema
- Manage database migrations
- Query data directly from Claude

**Use Cases**:
- Debugging database issues
- Writing migration scripts
- Analyzing data structure
- Testing queries

### 2. Sequential Thinking Server
**Purpose**: Enhanced reasoning for complex problem-solving

**Capabilities**:
- Step-by-step problem decomposition
- Logical reasoning chains
- Complex planning tasks

**Use Cases**:
- Architectural planning
- Algorithm design
- Complex debugging
- System design decisions

### 3. Playwright Server
**Purpose**: Browser automation and web testing

**Capabilities**:
- Automated browser testing
- Web scraping
- Screenshot capture
- Page interaction automation

**Use Cases**:
- Writing E2E tests
- Testing web applications
- Capturing UI bugs
- Automating web workflows

### 4. Task Master AI ⭐ NEW
**Purpose**: AI-powered task management and research

**Capabilities**:
- Parse PRDs into structured tasks
- Track and organize project tasks
- Conduct AI-powered research with context
- Manage development workflow
- Multi-model support (Claude, GPT, Gemini, Perplexity)

**Use Cases**:
- Converting requirements to tasks
- Project planning and tracking
- Research with project context
- Task prioritization
- Development workflow management

### 5. GitHub ⭐ NEW
**Purpose**: GitHub repository management and API integration

**Capabilities**:
- Repository operations (browse, search, clone)
- File operations (read, create, update, delete)
- Issue and PR management
- Branch and commit operations
- GitHub Actions workflow monitoring
- Code search across repositories
- Organization and team management

**Use Cases**:
- Automated repository management
- Issue and PR creation/updates
- Code review automation
- Repository analysis
- CI/CD pipeline monitoring
- Team collaboration workflows
- Bulk repository operations

---

## Setup Instructions

### Prerequisites

- Node.js and npm installed
- Claude Code CLI installed
- Required API keys for services you want to use

### Step 1: Environment Variables

Create a `.env` file in your project root (or add to existing):

```bash
# Task Master AI (at least ONE required)
ANTHROPIC_API_KEY=sk-ant-xxx          # For Claude models
PERPLEXITY_API_KEY=pplx-xxx           # For research features
OPENAI_API_KEY=sk-xxx                 # Optional: OpenAI models
GOOGLE_API_KEY=xxx                    # Optional: Gemini models

# GitHub (if using GitHub MCP)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx  # Get from: https://github.com/settings/tokens

# Database (if using PostgreSQL MCP)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Step 2: Verify MCP Configuration

The MCP servers are already configured in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:password@localhost/dbname"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    },
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "TASK_MASTER_TOOLS": "standard"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Step 3: Test MCP Servers

Restart Claude Code and verify MCP servers are running:

```bash
# In Claude Code, ask:
# "List available MCP servers"
# or
# "What tools do you have access to?"
```

---

## Configuration

### PostgreSQL Server

**Update connection string** in `settings.json`:

```json
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://username:password@host:5432/database"]
}
```

Or use environment variable:
```json
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
}
```

### Task Master AI

**Tool Loading Modes** (configure via `TASK_MASTER_TOOLS` env var):

| Mode | Tools | Context Usage | Best For |
|------|-------|---------------|----------|
| `core` | 7 tools | ~5,000 tokens | Minimal overhead |
| `standard` | 15 tools | ~10,000 tokens | ✅ **Recommended** |
| `all` | 36 tools | ~21,000 tokens | Maximum features |

**API Keys** (at least one required):
- `ANTHROPIC_API_KEY` - Claude models (recommended)
- `PERPLEXITY_API_KEY` - AI research features
- `OPENAI_API_KEY` - GPT models (optional)
- `GOOGLE_API_KEY` - Gemini models (optional)

**Configuration in settings.json**:
```json
"task-master-ai": {
  "command": "npx",
  "args": ["-y", "task-master-ai"],
  "env": {
    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
    "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
    "TASK_MASTER_TOOLS": "standard"
  }
}
```

### GitHub Server

**Creating a GitHub Personal Access Token**:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `read:org` - Read org and team membership
   - ✅ `workflow` - Update GitHub Action workflows (optional)
4. Generate and copy your token

**Required Scopes**:
- `repo` - Repository operations (required)
- `read:org` - Organization access (required)
- `workflow` - GitHub Actions (optional, for CI/CD features)

**Configuration in settings.json**:
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

**Security Note**: Never commit your GitHub token. Always use environment variables.

---

## Usage Examples

### Task Master AI Examples

#### 1. Initialize Task Master in Your Project

```
"Initialize taskmaster-ai in my project"
```

This creates:
- `.taskmaster/` directory structure
- Configuration files
- PRD template at `.taskmaster/docs/prd.txt`

#### 2. Parse a PRD into Tasks

```
"Can you parse my PRD at .taskmaster/docs/prd.txt?"
```

Converts your Product Requirements Document into structured, trackable tasks.

#### 3. Get Next Task

```
"What's the next task I should work on?"
```

Provides intelligent task prioritization based on dependencies and status.

#### 4. Work on Specific Task

```
"Can you help me implement task 3?"
```

Gets task details and provides implementation guidance.

#### 5. AI Research with Context

```
"Research best practices for FastAPI authentication with my project context"
```

Conducts fresh research while understanding your project structure.

#### 6. Move Tasks Between States

```
"Move task 5 from backlog to in-progress"
```

Updates task status programmatically.

### PostgreSQL Server Examples

```
"Show me the schema for the users table"
"Query the posts table for posts created today"
"Help me write a migration to add an index on user_id"
```

### Sequential Thinking Examples

```
"Help me architect a microservices system for user management"
"Break down the steps to implement OAuth2 authentication"
"Design a caching strategy for this API"
```

### Playwright Server Examples

```
"Write a test to check if the login form works"
"Take a screenshot of the homepage"
"Test if the checkout flow works end-to-end"
```

### GitHub Server Examples

#### Repository Operations
```
"List all repositories in my account"
"Show me the contents of the README.md in my-repo"
"Search for files containing 'authentication' in my-repo"
"Create a new repository called my-new-project"
```

#### File Operations
```
"Read the package.json file from my-repo"
"Create a new file called CONTRIBUTING.md in my-repo"
"Update the README.md with installation instructions"
"Delete the old config file from my-repo"
```

#### Issue Management
```
"Create an issue titled 'Add user authentication' in my-repo"
"List all open issues in my-repo"
"Close issue #42 in my-repo"
"Add a comment to issue #15 saying 'Working on this'"
```

#### Pull Request Operations
```
"Create a PR to merge feature-branch into main"
"List all open pull requests in my-repo"
"Review the changes in PR #23"
"Merge pull request #15"
```

#### Branch Operations
```
"Create a new branch called feature-authentication"
"List all branches in my-repo"
"Delete the old-feature branch"
"Show recent commits on main branch"
```

#### CI/CD & Actions
```
"Show the status of GitHub Actions in my-repo"
"List failed workflow runs"
"Check the build status for the latest commit"
```

---

## Task Master AI Workflow

### Recommended Development Flow

1. **Create PRD**: Write requirements in `.taskmaster/docs/prd.txt`

```markdown
# Feature: User Authentication System

## Requirements
- Email/password authentication
- JWT token generation
- Password reset via email
- OAuth2 support (Google, GitHub)

## Technical Details
- Use FastAPI dependencies
- SQLAlchemy for user model
- Bcrypt for password hashing
- Redis for token blacklist
```

2. **Initialize & Parse**:
```
"Initialize taskmaster-ai and parse my PRD"
```

3. **Review Tasks**:
```
"Show me all tasks"
```

4. **Work on Tasks**:
```
"Help me implement the first task"
```

5. **Track Progress**:
```
"Show me tasks in-progress"
"Mark task 3 as completed"
```

6. **Research**:
```
"Research JWT best practices for my FastAPI project"
```

---

## Troubleshooting

### MCP Server Not Starting

**Symptom**: "MCP server 'X' failed to start"

**Solutions**:
1. Check if Node.js is installed: `node --version`
2. Verify API keys in `.env`
3. Check network connectivity (MCP servers need internet to download)
4. Restart Claude Code

### Task Master AI: Missing API Keys

**Symptom**: "No valid API key found"

**Solution**:
Add at least one API key to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
```

Then restart Claude Code.

### PostgreSQL Connection Failed

**Symptom**: "Could not connect to database"

**Solutions**:
1. Verify database is running: `pg_isready`
2. Check connection string format
3. Ensure credentials are correct
4. Check firewall/network settings

### Task Master AI: Context Too Large

**Symptom**: Token limit warnings

**Solution**:
Reduce tool loading in `settings.json`:
```json
"env": {
  "TASK_MASTER_TOOLS": "core"  // Change from "standard" or "all"
}
```

---

## Adding More MCP Servers

### Available MCP Servers

Explore more at: https://github.com/modelcontextprotocol/servers

Popular servers:
- **Filesystem**: File operations
- **GitHub**: Repository management
- **Brave Search**: Web search
- **Memory**: Persistent memory
- **Slack**: Team communication
- **Google Drive**: File access

### Adding a New Server

1. Find the server on npm or GitHub
2. Add to `.claude/settings.json`:

```json
"mcpServers": {
  "server-name": {
    "command": "npx",
    "args": ["-y", "package-name"],
    "env": {
      "API_KEY": "${YOUR_API_KEY}"
    }
  }
}
```

3. Add required environment variables to `.env`
4. Restart Claude Code

---

## Best Practices

### 1. API Key Management
- ✅ Store API keys in `.env` (gitignored)
- ✅ Use environment variable references in `settings.json`
- ❌ Never commit API keys to git

### 2. Tool Loading Optimization
- Start with `standard` mode for Task Master AI
- Only use `all` mode if you need all features
- Use `core` for minimal overhead

### 3. Database Security
- Use read-only database users when possible
- Don't expose production databases in local dev
- Use connection pooling for better performance

### 4. Task Management
- Keep PRDs in `.taskmaster/docs/`
- Update task status regularly
- Use tags for organization (backlog, in-progress, done)

### 5. Testing
- Test MCP server connectivity after setup
- Verify API keys work before starting development
- Check MCP server logs if issues arise

---

## Environment Variables Template

Create a `.env` file with these variables:

```bash
# ==============================================
# MCP Server Configuration
# ==============================================

# Task Master AI (Required: at least ONE)
ANTHROPIC_API_KEY=sk-ant-xxx
PERPLEXITY_API_KEY=pplx-xxx
OPENAI_API_KEY=sk-xxx                    # Optional
GOOGLE_API_KEY=xxx                       # Optional

# Task Master AI Settings (Optional)
TASK_MASTER_TOOLS=standard               # Options: core, standard, all

# GitHub (Optional - for GitHub MCP)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx     # Get from: https://github.com/settings/tokens

# Database (Optional - for PostgreSQL MCP)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# ==============================================
# Add your project-specific variables below
# ==============================================
```

---

## Additional Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **MCP Server Registry**: https://github.com/modelcontextprotocol/servers
- **Task Master AI**: https://github.com/eyaltoledano/claude-task-master
- **Claude Code Docs**: https://docs.claude.com/claude-code

---

## Support

If you encounter issues:

1. Check this documentation
2. Review Claude Code logs
3. Verify environment variables
4. Restart Claude Code
5. Check MCP server documentation
6. Open an issue on GitHub

---

**Last Updated**: 2025-12-05
**Configured Servers**: PostgreSQL, Sequential Thinking, Playwright, Task Master AI, GitHub
