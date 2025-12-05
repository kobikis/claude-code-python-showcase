# Updating Your Target Project

> **Guide for updating an existing Claude Code infrastructure installation**

This guide helps you update a target project that already has Claude Code infrastructure installed from a previous `setup_target_project.py` run.

---

## Table of Contents

1. [Quick Update (Recommended)](#quick-update-recommended)
2. [Manual Update Steps](#manual-update-steps)
3. [Component-Specific Updates](#component-specific-updates)
4. [Verifying Updates](#verifying-updates)
5. [Rollback Instructions](#rollback-instructions)

---

## Quick Update (Recommended)

### Option 1: Re-run Setup Script with Backup

The setup script **automatically creates backups** before overwriting files.

```bash
# Navigate to the showcase directory
cd /path/to/claude-code-python-showcase

# Re-run setup on your target project
python setup_target_project.py --target /path/to/your/target/project --all

# Backups are created at: /path/to/your/target/project/.claude_backup/YYYYMMDD_HHMMSS/
```

**What gets updated:**
- ✅ New skills (route-tester, error-tracking)
- ✅ New agents (vapi-ai-expert)
- ✅ MCP server configuration
- ✅ Updated hooks
- ✅ New commands
- ⚠️ **Your customizations are backed up but will be overwritten**

### Option 2: Selective Update (Preserve Customizations)

Update specific components without touching others:

```bash
# Update only skills
python setup_target_project.py --target /path/to/your/target/project --component skills

# Update only agents
python setup_target_project.py --target /path/to/your/target/project --component agents

# Update only hooks
python setup_target_project.py --target /path/to/your/target/project --component hooks
```

---

## Manual Update Steps

If you've customized your infrastructure, use manual updates to preserve your changes.

### Step 1: Backup Your Current Setup

```bash
# Navigate to your target project
cd /path/to/your/target/project

# Create a backup
cp -r .claude .claude_backup_$(date +%Y%m%d_%H%M%S)

# Backup environment file if you have one
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)
```

### Step 2: Update MCP Configuration

Add new MCP servers to your `.claude/settings.json`:

```bash
# Open your target project's settings.json
# /path/to/your/target/project/.claude/settings.json
```

Add the Task Master AI MCP server:

```json
{
  "mcpServers": {
    // ... your existing MCP servers ...
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

### Step 3: Add New Skills

Copy new skills from the showcase to your target project:

```bash
# Navigate to showcase directory
cd /path/to/claude-code-python-showcase

# Copy route-tester skill
cp -r .claude/skills/route-tester /path/to/your/target/project/.claude/skills/

# Copy error-tracking skill
cp -r .claude/skills/error-tracking /path/to/your/target/project/.claude/skills/
```

Update your `skill-rules.json`:

```bash
# Copy the new entries from showcase's skill-rules.json
# to your target project's .claude/skills/skill-rules.json

# Or replace the entire file:
cp .claude/skills/skill-rules.json /path/to/your/target/project/.claude/skills/skill-rules.json
```

### Step 4: Add New Agents

```bash
# Copy vapi-ai-expert agent
cp .claude/agents/vapi-ai-expert.md /path/to/your/target/project/.claude/agents/
```

### Step 5: Update Environment Variables

```bash
# Copy new environment template
cp .env.example /path/to/your/target/project/.env.example

# Merge new variables into your existing .env
# Add at minimum:
# ANTHROPIC_API_KEY=your-key
# PERPLEXITY_API_KEY=your-key
```

### Step 6: Copy Documentation (Optional)

```bash
# Copy MCP setup guide
cp MCP_SETUP.md /path/to/your/target/project/

# Update PROJECT_STRUCTURE.md if you're using it
cp PROJECT_STRUCTURE.md /path/to/your/target/project/
```

---

## Component-Specific Updates

### Update Only Skills

**New Skills Available:**
- `route-tester` - pytest patterns for FastAPI
- `error-tracking` - Sentry integration and error handling

**Steps:**

```bash
cd /path/to/claude-code-python-showcase

# Copy new skills
cp -r .claude/skills/route-tester /path/to/your/target/project/.claude/skills/
cp -r .claude/skills/error-tracking /path/to/your/target/project/.claude/skills/

# Update skill-rules.json
# Manually merge or replace:
cp .claude/skills/skill-rules.json /path/to/your/target/project/.claude/skills/
```

### Update Only Agents

**New Agents Available:**
- `vapi-ai-expert` - Vapi.ai voice AI integration expert

**Steps:**

```bash
cd /path/to/claude-code-python-showcase

# Copy new agent
cp .claude/agents/vapi-ai-expert.md /path/to/your/target/project/.claude/agents/
```

### Update MCP Servers

**New MCP Server:**
- `task-master-ai` - Task management and AI research

**Steps:**

1. Edit `/path/to/your/target/project/.claude/settings.json`
2. Add the `task-master-ai` entry to `mcpServers` object
3. Create `.env` file with API keys
4. Restart Claude Code

### Update Hooks

If hooks were updated in the showcase:

```bash
cd /path/to/claude-code-python-showcase

# Copy updated hooks (backup first!)
cp .claude/hooks/skill-activation-prompt.py /path/to/your/target/project/.claude/hooks/
cp .claude/hooks/post-tool-use-tracker.py /path/to/your/target/project/.claude/hooks/
cp .claude/hooks/mypy-check.py /path/to/your/target/project/.claude/hooks/

# Update requirements if needed
cp .claude/hooks/requirements.txt /path/to/your/target/project/.claude/hooks/
pip install -r /path/to/your/target/project/.claude/hooks/requirements.txt
```

---

## Verifying Updates

### 1. Check File Structure

```bash
cd /path/to/your/target/project

# List new skills
ls -la .claude/skills/

# List new agents
ls -la .claude/agents/

# Check MCP config
cat .claude/settings.json | grep -A 5 "task-master-ai"
```

### 2. Test MCP Servers

Restart Claude Code in your target project and ask:

```
"What MCP servers do you have access to?"
```

You should see:
- postgres (or your database server)
- sequential-thinking
- playwright
- task-master-ai ← NEW

### 3. Test New Skills

In Claude Code, type:

```
"I need to write tests for my API endpoints"
```

Expected: Claude should suggest the `/route-tester` skill

```
"I need to add error tracking with Sentry"
```

Expected: Claude should suggest the `/error-tracking` skill

### 4. Test New Agent

```
"I need help integrating Vapi.ai for voice calls"
```

Claude can now use the vapi-ai-expert agent for guidance.

### 5. Test Task Master AI

```
"Initialize taskmaster-ai in my project"
```

This should create `.taskmaster/` directory and configuration.

---

## Rollback Instructions

If something goes wrong, you can rollback to your previous configuration.

### Rollback from Automatic Backup

```bash
cd /path/to/your/target/project

# List available backups
ls -la .claude_backup/

# Restore from a specific backup
cp -r .claude_backup/YYYYMMDD_HHMMSS/.claude ./

# Restart Claude Code
```

### Rollback from Manual Backup

```bash
cd /path/to/your/target/project

# Restore .claude directory
rm -rf .claude
mv .claude_backup_YYYYMMDD_HHMMSS .claude

# Restore .env if needed
mv .env.backup_YYYYMMDD_HHMMSS .env

# Restart Claude Code
```

---

## Merging Custom Changes

If you've customized your infrastructure and want to preserve changes:

### 1. Compare Files

```bash
# Compare skill-rules.json
diff .claude_backup/YYYYMMDD_HHMMSS/.claude/skills/skill-rules.json .claude/skills/skill-rules.json

# Compare settings.json
diff .claude_backup/YYYYMMDD_HHMMSS/.claude/settings.json .claude/settings.json
```

### 2. Merge Manually

For `skill-rules.json`:
- Keep your custom keywords
- Add new skill entries
- Preserve your file path patterns

For `settings.json`:
- Keep your custom hook configurations
- Add new MCP servers
- Preserve your database connection strings

### 3. Test After Merge

Always test after manual merging:
1. Restart Claude Code
2. Verify all skills activate correctly
3. Check MCP servers are accessible
4. Test hooks are working

---

## Update Checklist

Use this checklist when updating:

### Before Update
- [ ] Backup `.claude/` directory
- [ ] Backup `.env` file
- [ ] Note any custom modifications you've made
- [ ] Close Claude Code

### During Update
- [ ] Copy new skills (route-tester, error-tracking)
- [ ] Copy new agents (vapi-ai-expert)
- [ ] Update `skill-rules.json`
- [ ] Update `.claude/settings.json` with MCP config
- [ ] Merge `.env` with new variables
- [ ] Copy documentation if needed

### After Update
- [ ] Restart Claude Code
- [ ] Test MCP servers: `"What MCP servers do you have?"`
- [ ] Test new skills: Type relevant prompts
- [ ] Test task-master-ai: `"Initialize taskmaster-ai"`
- [ ] Verify hooks are working
- [ ] Check for any errors in Claude Code logs

---

## Common Issues

### Issue: MCP Server Not Starting

**Symptom**: "MCP server 'task-master-ai' failed to start"

**Solution**:
1. Check API keys in `.env`
2. Verify Node.js is installed: `node --version`
3. Check internet connectivity
4. Restart Claude Code

### Issue: Skill Not Activating

**Symptom**: New skills don't show up in suggestions

**Solution**:
1. Verify skill directory exists: `.claude/skills/route-tester/`
2. Check `skill-rules.json` includes the skill
3. Restart Claude Code
4. Check hook is configured: `UserPromptSubmit` in settings

### Issue: API Key Error

**Symptom**: "No valid API key found"

**Solution**:
1. Check `.env` file exists in project root
2. Verify `ANTHROPIC_API_KEY` is set
3. Restart Claude Code to reload environment variables

### Issue: Custom Changes Lost

**Symptom**: Your customizations were overwritten

**Solution**:
1. Restore from backup: `.claude_backup/YYYYMMDD_HHMMSS/`
2. Use manual update steps next time
3. Merge changes carefully

---

## Best Practices for Future Updates

### 1. Document Your Customizations

Keep a `CUSTOMIZATIONS.md` file in your `.claude/` directory:

```markdown
# Custom Modifications

## skill-rules.json
- Added custom keywords for our domain
- Changed file patterns to match our structure

## settings.json
- Custom database connection string
- Added custom MCP servers
```

### 2. Version Control

Commit your `.claude/` directory to git:

```bash
git add .claude/
git commit -m "Update Claude Code infrastructure"
```

### 3. Test in Dev First

If you have multiple environments:
1. Update dev environment first
2. Test thoroughly
3. Then update staging/production

### 4. Keep Backups

Always backup before updates:
```bash
./backup_claude_config.sh  # Create your own backup script
```

---

## Getting Help

If you encounter issues:

1. Check this guide's [Common Issues](#common-issues) section
2. Review [MCP_SETUP.md](MCP_SETUP.md) for MCP-specific problems
3. Check Claude Code logs for error messages
4. Restore from backup if needed
5. Open an issue on GitHub with details

---

## What's New in This Update

### New Skills
- **route-tester**: Complete pytest guide with AsyncClient, fixtures, parametrized tests
- **error-tracking**: Sentry integration, custom exceptions, error middleware

### New Agents
- **vapi-ai-expert**: Voice AI integration with webhook security, function calling, testing

### New MCP Servers
- **task-master-ai**: AI-powered task management, PRD parsing, research capabilities

### New Documentation
- **MCP_SETUP.md**: Comprehensive MCP server setup guide
- **.env.example**: Complete environment variable template
- **UPDATE_TARGET_PROJECT.md**: This guide!

### Updated Files
- **README.md**: Added MCP section
- **PROJECT_STRUCTURE.md**: Updated with new components
- **.claude/settings.json**: Added task-master-ai MCP server
- **.claude/skills/skill-rules.json**: Already included rules for new skills

---

**Last Updated**: 2025-12-05
**Compatible With**: Claude Code v1.0+
