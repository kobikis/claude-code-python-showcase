#!/bin/bash
# Quick component update script for existing installations
# Usage: ./update_component.sh /path/to/target/project [component]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory (showcase directory)
SHOWCASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions
print_header() {
    echo -e "\n${CYAN}================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

create_backup() {
    local target_path=$1
    local component=$2
    local backup_dir="$target_path/.claude_backup/$(date +%Y%m%d_%H%M%S)"

    mkdir -p "$backup_dir"

    if [ "$component" = "all" ]; then
        cp -r "$target_path/.claude" "$backup_dir/"
        [ -f "$target_path/.env" ] && cp "$target_path/.env" "$backup_dir/"
    else
        case $component in
            skills)
                [ -d "$target_path/.claude/skills" ] && cp -r "$target_path/.claude/skills" "$backup_dir/"
                ;;
            agents)
                [ -d "$target_path/.claude/agents" ] && cp -r "$target_path/.claude/agents" "$backup_dir/"
                ;;
            hooks)
                [ -d "$target_path/.claude/hooks" ] && cp -r "$target_path/.claude/hooks" "$backup_dir/"
                ;;
            mcp)
                [ -f "$target_path/.claude/settings.json" ] && cp "$target_path/.claude/settings.json" "$backup_dir/"
                [ -f "$target_path/.env" ] && cp "$target_path/.env" "$backup_dir/"
                ;;
        esac
    fi

    print_success "Backup created at: $backup_dir"
}

update_skills() {
    local target_path=$1
    print_header "Updating Skills"

    # Create skills directory if not exists
    mkdir -p "$target_path/.claude/skills"

    # Copy new skills
    print_info "Copying route-tester skill..."
    cp -r "$SHOWCASE_DIR/.claude/skills/route-tester" "$target_path/.claude/skills/"
    print_success "route-tester installed"

    print_info "Copying error-tracking skill..."
    cp -r "$SHOWCASE_DIR/.claude/skills/error-tracking" "$target_path/.claude/skills/"
    print_success "error-tracking installed"

    # Update skill-rules.json
    print_info "Updating skill-rules.json..."
    cp "$SHOWCASE_DIR/.claude/skills/skill-rules.json" "$target_path/.claude/skills/skill-rules.json"
    print_success "skill-rules.json updated"

    print_success "Skills update complete"
}

update_agents() {
    local target_path=$1
    print_header "Updating Agents"

    # Create agents directory if not exists
    mkdir -p "$target_path/.claude/agents"

    # Copy new agent
    print_info "Copying vapi-ai-expert agent..."
    cp "$SHOWCASE_DIR/.claude/agents/vapi-ai-expert.md" "$target_path/.claude/agents/"
    print_success "vapi-ai-expert installed"

    print_success "Agents update complete"
}

update_hooks() {
    local target_path=$1
    print_header "Updating Hooks"

    # Create hooks directory if not exists
    mkdir -p "$target_path/.claude/hooks"

    # Copy hooks
    print_info "Copying hooks..."
    cp "$SHOWCASE_DIR/.claude/hooks/skill-activation-prompt.py" "$target_path/.claude/hooks/"
    cp "$SHOWCASE_DIR/.claude/hooks/post-tool-use-tracker.py" "$target_path/.claude/hooks/"
    cp "$SHOWCASE_DIR/.claude/hooks/mypy-check.py" "$target_path/.claude/hooks/"
    cp "$SHOWCASE_DIR/.claude/hooks/requirements.txt" "$target_path/.claude/hooks/"
    print_success "Hooks copied"

    # Install requirements
    print_info "Installing hook dependencies..."
    pip install -r "$target_path/.claude/hooks/requirements.txt" --quiet
    print_success "Dependencies installed"

    print_success "Hooks update complete"
}

update_mcp() {
    local target_path=$1
    print_header "Updating MCP Configuration"

    # Check if settings.json exists
    if [ ! -f "$target_path/.claude/settings.json" ]; then
        print_error "settings.json not found. Creating new one..."
        cp "$SHOWCASE_DIR/.claude/settings.json" "$target_path/.claude/settings.json"
        print_warning "Please update database connection strings and other settings"
    else
        print_warning "settings.json exists. You need to manually merge MCP configuration."
        print_info "Add the task-master-ai entry from showcase's settings.json"
        print_info "See UPDATE_TARGET_PROJECT.md for details"
    fi

    # Copy .env.example if not exists
    if [ ! -f "$target_path/.env.example" ]; then
        print_info "Copying .env.example..."
        cp "$SHOWCASE_DIR/.env.example" "$target_path/"
        print_success ".env.example copied"
    fi

    # Check for .env
    if [ ! -f "$target_path/.env" ]; then
        print_warning ".env not found. Create one from .env.example"
        print_info "cp .env.example .env"
        print_info "Then add your API keys"
    fi

    print_success "MCP configuration updated (manual merge may be needed)"
}

update_docs() {
    local target_path=$1
    print_header "Updating Documentation"

    print_info "Copying MCP_SETUP.md..."
    cp "$SHOWCASE_DIR/MCP_SETUP.md" "$target_path/"
    print_success "MCP_SETUP.md copied"

    print_info "Copying UPDATE_TARGET_PROJECT.md..."
    cp "$SHOWCASE_DIR/UPDATE_TARGET_PROJECT.md" "$target_path/"
    print_success "UPDATE_TARGET_PROJECT.md copied"

    if [ -f "$target_path/PROJECT_STRUCTURE.md" ]; then
        print_info "Updating PROJECT_STRUCTURE.md..."
        cp "$SHOWCASE_DIR/PROJECT_STRUCTURE.md" "$target_path/"
        print_success "PROJECT_STRUCTURE.md updated"
    fi

    print_success "Documentation update complete"
}

update_all() {
    local target_path=$1

    print_header "Updating All Components"

    create_backup "$target_path" "all"
    update_skills "$target_path"
    update_agents "$target_path"
    update_hooks "$target_path"
    update_mcp "$target_path"
    update_docs "$target_path"

    print_header "Update Complete!"
    print_info "Next steps:"
    echo "  1. Review .claude/settings.json for MCP configuration"
    echo "  2. Add API keys to .env file"
    echo "  3. Restart Claude Code"
    echo "  4. Test with: 'What MCP servers do you have access to?'"
}

# Main script
main() {
    if [ $# -lt 1 ]; then
        echo "Usage: $0 /path/to/target/project [component]"
        echo ""
        echo "Components:"
        echo "  skills    - Update skills (route-tester, error-tracking)"
        echo "  agents    - Update agents (vapi-ai-expert)"
        echo "  hooks     - Update hooks"
        echo "  mcp       - Update MCP configuration"
        echo "  docs      - Update documentation"
        echo "  all       - Update everything (default)"
        echo ""
        echo "Example:"
        echo "  $0 /path/to/project skills"
        echo "  $0 /path/to/project all"
        exit 1
    fi

    TARGET_PATH="$1"
    COMPONENT="${2:-all}"

    # Validate target path
    if [ ! -d "$TARGET_PATH" ]; then
        print_error "Target path does not exist: $TARGET_PATH"
        exit 1
    fi

    # Create .claude directory if not exists
    mkdir -p "$TARGET_PATH/.claude"

    print_header "Claude Code Infrastructure Update"
    print_info "Showcase: $SHOWCASE_DIR"
    print_info "Target: $TARGET_PATH"
    print_info "Component: $COMPONENT"

    # Execute update based on component
    case $COMPONENT in
        skills)
            create_backup "$TARGET_PATH" "skills"
            update_skills "$TARGET_PATH"
            ;;
        agents)
            create_backup "$TARGET_PATH" "agents"
            update_agents "$TARGET_PATH"
            ;;
        hooks)
            create_backup "$TARGET_PATH" "hooks"
            update_hooks "$TARGET_PATH"
            ;;
        mcp)
            create_backup "$TARGET_PATH" "mcp"
            update_mcp "$TARGET_PATH"
            ;;
        docs)
            update_docs "$TARGET_PATH"
            ;;
        all)
            update_all "$TARGET_PATH"
            ;;
        *)
            print_error "Unknown component: $COMPONENT"
            echo "Valid components: skills, agents, hooks, mcp, docs, all"
            exit 1
            ;;
    esac
}

main "$@"
