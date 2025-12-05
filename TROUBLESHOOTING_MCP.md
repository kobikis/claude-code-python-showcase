# Troubleshooting MCP "Not Found" Issues

If Claude Code says "I don't see X MCP server", follow this guide.

## Issue: MCP Server Not Found

**Symptom**: Claude Code doesn't recognize MCP servers even though they're configured.

### Checklist

1. **Is it in settings.json?**
   ```bash
   cd /path/to/your/target/project
   cat .claude/settings.json | grep "mcpServers"
   ```

   Should show:
   ```json
   "mcpServers": {
     "task-master-ai": { ... },
     ...
   }
   ```

2. **Do you have .env with API keys?**
   ```bash
   cat .env | grep ANTHROPIC_API_KEY
   ```

   Should show:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Did you restart Claude Code?**
   - Exit completely (not just close chat)
   - Reopen in your project directory
   - Wait 5-10 seconds for MCP servers to initialize

4. **Is Node.js installed?**
   ```bash
   node --version
   # Should show v16+ or higher
   ```

5. **Check Claude Code logs**
   Look for MCP initialization messages

## Step-by-Step Fix

### Step 1: Ensure Proper File Location

The `.claude/settings.json` file MUST be in your project root:

```
your-project/
├── .claude/
│   └── settings.json  ← MCP config here
├── .env               ← API keys here
└── ... your code ...
```

### Step 2: Verify settings.json Content

Open `.claude/settings.json` and ensure it has:

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "TASK_MASTER_TOOLS": "standard"
      }
    }
  }
}
```

**Common mistake**: Missing comma if you have other settings:
```json
{
  "mcpServers": { ... },  ← Need comma here
  "permissions": { ... }
}
```

### Step 3: Verify .env File

Create `.env` in your project root (same level as `.claude/`):

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here  # Optional
```

**Common mistakes**:
- ❌ Quotes around values: `ANTHROPIC_API_KEY="sk-ant..."` (wrong)
- ✅ No quotes: `ANTHROPIC_API_KEY=sk-ant...` (correct)
- ❌ Spaces: `ANTHROPIC_API_KEY = sk-ant...` (wrong)
- ✅ No spaces: `ANTHROPIC_API_KEY=sk-ant...` (correct)

### Step 4: Complete Restart

1. **Exit Claude Code**: Cmd+Q (Mac) or Alt+F4 (Windows/Linux)
2. **Wait 5 seconds**
3. **Reopen**: `code .` or open from Applications
4. **Wait for initialization**: Look for MCP loading messages

### Step 5: Test MCP Availability

```
"List all available MCP tools"
```

or

```
"What MCP servers do you have access to?"
```

Should show:
- `task-master-ai` tools (if configured)
- Any other MCP servers you configured

## Still Not Working?

### Check MCP Server Installation

Task Master AI installs automatically via `npx`, but you can test manually:

```bash
# Test if it can be installed
npx -y task-master-ai --help
```

### Check Environment Variables

In Claude Code, test if env vars are loaded:

```
"Show me the value of ANTHROPIC_API_KEY (just confirm it exists, don't show the full key)"
```

### Check for JSON Syntax Errors

```bash
# Validate JSON syntax
python3 -m json.tool .claude/settings.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

If invalid, fix the syntax errors (missing commas, brackets, etc.)

### Check Internet Connection

MCP servers download via npm/npx, so you need internet access for first run.

```bash
# Test npm connectivity
npm ping
```

## Manual MCP Configuration

If automatic setup isn't working, manually create the files:

### 1. Create .claude/settings.json

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "TASK_MASTER_TOOLS": "standard"
      }
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  },
  "permissions": {
    "edit": "allow",
    "write": "allow",
    "bash": "allow"
  }
}
```

### 2. Create .env

```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key
PERPLEXITY_API_KEY=pplx-your-key-optional
```

### 3. Restart Claude Code

Complete exit and reopen.

## Testing Individual MCP Servers

### Test Task Master AI

```
"Initialize taskmaster-ai in this project"
```

Expected: Creates `.taskmaster/` directory

### Test Sequential Thinking

```
"Use sequential thinking to break down how to implement user authentication"
```

Expected: Shows step-by-step reasoning

### Test Playwright

```
"Use playwright to take a screenshot of https://example.com"
```

Expected: Browser automation works

## Common Error Messages

### "No valid API key found"

**Fix**: Add `ANTHROPIC_API_KEY` to `.env` file

### "MCP server failed to start"

**Fix**:
1. Check Node.js version: `node --version` (need v16+)
2. Check internet connection
3. Try manual installation: `npx -y task-master-ai`

### "Could not connect to MCP server"

**Fix**: Restart Claude Code completely

### "Environment variable not found"

**Fix**:
1. Check `.env` file exists in project root
2. Ensure no syntax errors in `.env`
3. Restart Claude Code to reload environment

## Getting More Help

If still not working:

1. **Check logs**: Look for MCP-related error messages in Claude Code
2. **Verify API key**: Test it works with curl:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   ```

3. **Try minimal config**: Start with just task-master-ai, add others later

4. **Reinstall showcase**: Download latest version and run update again

---

## Quick Reference

### File Locations
```
your-project/
├── .claude/
│   └── settings.json    # MCP servers config
├── .env                 # API keys
└── .taskmaster/         # Created by task-master-ai
```

### Minimum Required Files

**.claude/settings.json**:
```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

**.env**:
```
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Restart Command
```bash
# Mac
killall "Claude Code"
code .

# Or just: Cmd+Q and reopen
```
