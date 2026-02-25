#!/bin/bash
# Quick component update script for existing installations.
# Copies components from the showcase .claude/ source of truth.
#
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
        [ -d "$target_path/.claude" ] && cp -r "$target_path/.claude" "$backup_dir/"
    else
        case $component in
            skills)
                [ -d "$target_path/.claude/skills" ] && cp -r "$target_path/.claude/skills" "$backup_dir/"
                ;;
            agents)
                [ -d "$target_path/.claude/agents" ] && cp -r "$target_path/.claude/agents" "$backup_dir/"
                ;;
            commands)
                [ -d "$target_path/.claude/commands" ] && cp -r "$target_path/.claude/commands" "$backup_dir/"
                ;;
            hooks)
                [ -d "$target_path/.claude/hooks" ] && cp -r "$target_path/.claude/hooks" "$backup_dir/"
                [ -d "$target_path/.claude/scripts" ] && cp -r "$target_path/.claude/scripts" "$backup_dir/"
                ;;
            rules)
                [ -d "$target_path/.claude/rules" ] && cp -r "$target_path/.claude/rules" "$backup_dir/"
                ;;
        esac
    fi

    print_success "Backup created at: $backup_dir"
}

update_skills() {
    local target_path=$1
    print_header "Updating Skills"

    local skills=(
        python-patterns
        async-python-patterns
        python-testing
        tdd-workflow
        postgres-patterns
        docker-patterns
        deployment-patterns
        security-review
        design-doc-mermaid
        perplexity-deep-search
        verification-loop
        strategic-compact
    )

    mkdir -p "$target_path/.claude/skills"

    for skill in "${skills[@]}"; do
        if [ -d "$SHOWCASE_DIR/.claude/skills/$skill" ]; then
            print_info "Copying skill: $skill"
            rm -rf "$target_path/.claude/skills/$skill"
            cp -r "$SHOWCASE_DIR/.claude/skills/$skill" "$target_path/.claude/skills/"
            print_success "$skill installed"
        else
            print_warning "Source skill not found: $skill"
        fi
    done

    # Generate skill-rules.json via Python
    print_info "Generating skill-rules.json..."
    SHOWCASE_DIR="$SHOWCASE_DIR" TARGET_PATH="$target_path" python3 - <<'PYEOF'
import sys, os
sys.path.insert(0, os.environ["SHOWCASE_DIR"])
from skills_generator import SKILL_NAMES, generate_skill_rules
from pathlib import Path
generate_skill_rules(SKILL_NAMES, Path(os.environ["TARGET_PATH"]) / ".claude/skills/skill-rules.json")
print("skill-rules.json generated")
PYEOF
    print_success "Skills update complete (${#skills[@]} skills)"
}

update_agents() {
    local target_path=$1
    print_header "Updating Agents"

    local agents=(
        planner
        architect
        tdd-guide
        code-reviewer
        security-reviewer
        fastapi-specialist
        aws-specialist
        k8s-specialist
        python-database-expert
        python-debugger
    )

    mkdir -p "$target_path/.claude/agents"

    for agent in "${agents[@]}"; do
        if [ -f "$SHOWCASE_DIR/.claude/agents/${agent}.md" ]; then
            print_info "Copying agent: $agent"
            cp "$SHOWCASE_DIR/.claude/agents/${agent}.md" "$target_path/.claude/agents/"
            print_success "$agent installed"
        else
            print_warning "Source agent not found: $agent"
        fi
    done

    print_success "Agents update complete (${#agents[@]} agents)"
}

update_commands() {
    local target_path=$1
    print_header "Updating Commands"

    local commands=(
        pr
        plan
        tdd
        code-review
        build-fix
        test-coverage
        verify
        update-docs
        orchestrate
    )

    mkdir -p "$target_path/.claude/commands"

    for cmd in "${commands[@]}"; do
        if [ -f "$SHOWCASE_DIR/.claude/commands/${cmd}.md" ]; then
            print_info "Copying command: /$cmd"
            cp "$SHOWCASE_DIR/.claude/commands/${cmd}.md" "$target_path/.claude/commands/"
            print_success "/$cmd installed"
        else
            print_warning "Source command not found: $cmd"
        fi
    done

    print_success "Commands update complete (${#commands[@]} commands)"
}

update_hooks() {
    local target_path=$1
    print_header "Updating Hooks & Scripts"

    # Shell/Python hooks
    mkdir -p "$target_path/.claude/hooks"
    if [ -d "$SHOWCASE_DIR/.claude/hooks" ]; then
        print_info "Copying shell/Python hooks..."
        cp "$SHOWCASE_DIR/.claude/hooks/"* "$target_path/.claude/hooks/" 2>/dev/null || true
        print_success "Shell/Python hooks copied"
    fi

    # JS hook scripts
    mkdir -p "$target_path/.claude/scripts/hooks"
    if [ -d "$SHOWCASE_DIR/.claude/scripts/hooks" ]; then
        print_info "Copying JS hook scripts..."
        cp "$SHOWCASE_DIR/.claude/scripts/hooks/"* "$target_path/.claude/scripts/hooks/" 2>/dev/null || true
        print_success "JS hook scripts copied"
    fi

    # JS library modules
    mkdir -p "$target_path/.claude/scripts/lib"
    if [ -d "$SHOWCASE_DIR/.claude/scripts/lib" ]; then
        print_info "Copying JS library modules..."
        cp "$SHOWCASE_DIR/.claude/scripts/lib/"* "$target_path/.claude/scripts/lib/" 2>/dev/null || true
        print_success "JS library modules copied"
    fi

    print_success "Hooks & scripts update complete"
}

update_rules() {
    local target_path=$1
    print_header "Updating Rules"

    # Common rules
    if [ -d "$SHOWCASE_DIR/.claude/rules/common" ]; then
        mkdir -p "$target_path/.claude/rules/common"
        print_info "Copying common rules..."
        cp "$SHOWCASE_DIR/.claude/rules/common/"*.md "$target_path/.claude/rules/common/" 2>/dev/null || true
        local count=$(ls -1 "$target_path/.claude/rules/common/"*.md 2>/dev/null | wc -l | tr -d ' ')
        print_success "Common rules copied: $count files"
    fi

    # Python rules
    if [ -d "$SHOWCASE_DIR/.claude/rules/python" ]; then
        mkdir -p "$target_path/.claude/rules/python"
        print_info "Copying Python rules..."
        cp "$SHOWCASE_DIR/.claude/rules/python/"*.md "$target_path/.claude/rules/python/" 2>/dev/null || true
        local count=$(ls -1 "$target_path/.claude/rules/python/"*.md 2>/dev/null | wc -l | tr -d ' ')
        print_success "Python rules copied: $count files"
    fi

    print_success "Rules update complete"
}

update_all() {
    local target_path=$1

    print_header "Updating All Components"

    create_backup "$target_path" "all"
    update_skills "$target_path"
    update_agents "$target_path"
    update_commands "$target_path"
    update_hooks "$target_path"
    update_rules "$target_path"

    print_header "Update Complete!"
    print_info "Next steps:"
    echo "  1. Review changes in .claude/"
    echo "  2. Run: python compile_rules.py --target \"$target_path\""
    echo "  3. Restart Claude Code"
}

# Main script
main() {
    if [ $# -lt 1 ]; then
        echo "Usage: $0 /path/to/target/project [component]"
        echo ""
        echo "Components:"
        echo "  skills    - Update 12 skill directories"
        echo "  agents    - Update 10 specialist agents"
        echo "  commands  - Update 9 slash commands"
        echo "  hooks     - Update hooks + JS scripts + JS libs"
        echo "  rules     - Update common + Python rules"
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
        commands)
            create_backup "$TARGET_PATH" "commands"
            update_commands "$TARGET_PATH"
            ;;
        hooks)
            create_backup "$TARGET_PATH" "hooks"
            update_hooks "$TARGET_PATH"
            ;;
        rules)
            create_backup "$TARGET_PATH" "rules"
            update_rules "$TARGET_PATH"
            ;;
        all)
            update_all "$TARGET_PATH"
            ;;
        *)
            print_error "Unknown component: $COMPONENT"
            echo "Valid components: skills, agents, commands, hooks, rules, all"
            exit 1
            ;;
    esac
}

main "$@"
