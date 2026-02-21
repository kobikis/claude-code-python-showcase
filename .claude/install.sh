#!/usr/bin/env bash
# .claude/install.sh
#
# Installs Claude Code personal config from this repo into ~/.claude/
#
# Usage:
#   ./.claude/install.sh              # interactive
#   ./.claude/install.sh --all        # install everything
#   ./.claude/install.sh --agents     # agents only
#   ./.claude/install.sh --skills     # skills only
#   ./.claude/install.sh --hooks      # hook scripts + scripts/
#   ./.claude/install.sh --commands   # commands only
#   ./.claude/install.sh --rules      # coding rules only
#   ./.claude/install.sh --mcp        # show MCP + hooks setup instructions
#   ./.claude/install.sh --dry-run    # preview without writing

set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"   # this .claude/ directory
DST="${HOME}/.claude"
DRY_RUN=false

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'

log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC}  $1"; }
log_info() { echo -e "${CYAN}ℹ${NC}  $1"; }
log_err()  { echo -e "${RED}✗${NC} $1"; }
log_head() { echo -e "\n${BOLD}── $1 ──${NC}"; }

# ── Helpers ───────────────────────────────────────────────────────────────────
copy_file() {
    local src="$1" dst="$2"
    if [[ "$DRY_RUN" == true ]]; then
        echo "  [dry] $(basename "$src") → $dst"
        return
    fi
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    log_ok "$(basename "$src")"
}

copy_dir() {
    local src="$1" dst="$2"
    if [[ "$DRY_RUN" == true ]]; then
        echo "  [dry] $(basename "$src")/ → $dst/"
        return
    fi
    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
    log_ok "$(basename "$src")/"
}

count_files() { ls "$1" 2>/dev/null | wc -l | tr -d ' '; }
count_dirs()  { ls -d "$1"/*/ 2>/dev/null | wc -l | tr -d ' '; }

# ── Installers ────────────────────────────────────────────────────────────────
install_agents() {
    log_head "Agents ($(count_files "$SRC/agents") files) → ${DST}/agents/"
    mkdir -p "${DST}/agents"
    for f in "${SRC}/agents/"*.md; do
        [[ -f "$f" ]] || continue
        copy_file "$f" "${DST}/agents/$(basename "$f")"
    done
}

install_commands() {
    log_head "Commands ($(count_files "$SRC/commands") files) → ${DST}/commands/"
    mkdir -p "${DST}/commands"
    for f in "${SRC}/commands/"*.md; do
        [[ -f "$f" ]] || continue
        copy_file "$f" "${DST}/commands/$(basename "$f")"
    done
}

install_skills() {
    log_head "Skills ($(count_dirs "$SRC/skills") dirs) → ${DST}/skills/"
    mkdir -p "${DST}/skills"
    for dir in "${SRC}/skills/"/*/; do
        [[ -d "$dir" ]] || continue
        name="$(basename "$dir")"
        copy_dir "$dir" "${DST}/skills/${name}"
    done
}

install_hooks() {
    log_head "Hook scripts → ${DST}/hooks/ + ${DST}/scripts/"
    mkdir -p "${DST}/hooks" "${DST}/scripts"
    for f in "${SRC}/hooks/"*; do
        [[ -f "$f" ]] || continue
        copy_file "$f" "${DST}/hooks/$(basename "$f")"
        [[ "$DRY_RUN" == false ]] && chmod +x "${DST}/hooks/$(basename "$f")" || true
    done
    for f in "${SRC}/scripts/"*; do
        [[ -f "$f" ]] || continue
        copy_file "$f" "${DST}/scripts/$(basename "$f")"
        [[ "$DRY_RUN" == false ]] && chmod +x "${DST}/scripts/$(basename "$f")" || true
    done
}

install_rules() {
    log_head "Rules → ${DST}/rules/common/"
    mkdir -p "${DST}/rules/common"
    for f in "${SRC}/rules/common/"*.md; do
        [[ -f "$f" ]] || continue
        copy_file "$f" "${DST}/rules/common/$(basename "$f")"
    done
}

install_mcp() {
    log_head "MCP Servers"
    echo ""
    echo "MCP config lives in ~/.claude.json (outside ~/.claude/)."
    echo "Reference: ${SRC}/mcp/mcp-servers.json"
    echo ""
    echo "Add these entries under 'mcpServers' in ~/.claude.json:"
    echo ""
    python3 -c "
import json, os
d = json.load(open('${SRC}/mcp/mcp-servers.json'))
for name, cfg in d.get('mcpServers', {}).items():
    print(f'  \"{name}\": {json.dumps(cfg, indent=4)}')
    print()
" 2>/dev/null || cat "${SRC}/mcp/mcp-servers.json"
    echo ""
    log_warn "Replace \${CLAUDE_DIR} with ${DST}/ and \${PROJECT_DIR} with your project root"
    echo ""
    echo "Required tools:"
    echo "  cmem           → npm install -g cmem"
    echo "  claude-mermaid → npm install -g claude-mermaid"
    echo "  atlassian      → SSE, no install needed"
    echo ""

    log_head "Hooks Configuration"
    echo ""
    echo "Merge hooks from ${SRC}/mcp/hooks-config.json into ~/.claude/settings.json"
    echo ""
    echo "Quick merge:"
    cat << 'PYEOF'
    python3 - << 'EOF'
import json
s_path = os.path.expanduser("~/.claude/settings.json")
h_path = "${SRC}/mcp/hooks-config.json"
s = json.load(open(s_path)) if os.path.exists(s_path) else {}
h = json.load(open(h_path))
s["hooks"] = h
json.dump(s, open(s_path, "w"), indent=2)
print("✓ Hooks merged into settings.json")
EOF
PYEOF
}

# ── Sync back to repo ─────────────────────────────────────────────────────────
sync_from_local() {
    log_head "Sync ~/.claude → repo .claude/"
    log_warn "This overwrites repo files with your local ~/.claude/ content"
    read -rp "Continue? (y/N) " confirm
    [[ "$confirm" != "y" && "$confirm" != "Y" ]] && { log_info "Cancelled"; return; }

    # agents
    for f in "${DST}/agents/"*.md; do
        [[ -f "$f" ]] && cp "$f" "${SRC}/agents/" && log_ok "agents/$(basename "$f")"
    done
    # commands
    for f in "${DST}/commands/"*.md; do
        [[ -f "$f" ]] && cp "$f" "${SRC}/commands/" && log_ok "commands/$(basename "$f")"
    done
    # skills (skip plugin cache - only user-managed)
    for dir in "${DST}/skills/"/*/; do
        [[ -d "$dir" ]] || continue
        name="$(basename "$dir")"
        mkdir -p "${SRC}/skills/${name}"
        cp -r "$dir/." "${SRC}/skills/${name}/" && log_ok "skills/${name}/"
    done
    # hooks + scripts
    for f in "${DST}/hooks/"*; do [[ -f "$f" ]] && cp "$f" "${SRC}/hooks/"; done
    for f in "${DST}/scripts/"*; do [[ -f "$f" ]] && cp "$f" "${SRC}/scripts/"; done
    # rules
    for f in "${DST}/rules/common/"*.md; do
        [[ -f "$f" ]] && cp "$f" "${SRC}/rules/common/" && log_ok "rules/$(basename "$f")"
    done
    log_ok "Sync complete — review changes with: git diff .claude/"
}

# ── Argument parsing ──────────────────────────────────────────────────────────
COMPONENTS=()
INSTALL_ALL=false
SYNC=false

for arg in "$@"; do
    case "$arg" in
        --dry-run)  DRY_RUN=true ;;
        --all)      INSTALL_ALL=true ;;
        --sync)     SYNC=true ;;
        --agents)   COMPONENTS+=(agents) ;;
        --commands) COMPONENTS+=(commands) ;;
        --skills)   COMPONENTS+=(skills) ;;
        --hooks)    COMPONENTS+=(hooks) ;;
        --rules)    COMPONENTS+=(rules) ;;
        --mcp)      COMPONENTS+=(mcp) ;;
        *) log_err "Unknown option: $arg"; exit 1 ;;
    esac
done

[[ "$DRY_RUN" == true ]] && log_warn "DRY RUN — no files will be written"

# ── Run ───────────────────────────────────────────────────────────────────────
if [[ "$SYNC" == true ]]; then
    sync_from_local
elif [[ "$INSTALL_ALL" == true ]]; then
    install_agents
    install_commands
    install_skills
    install_hooks
    install_rules
    install_mcp
elif [[ ${#COMPONENTS[@]} -gt 0 ]]; then
    for c in "${COMPONENTS[@]}"; do
        case "$c" in
            agents)   install_agents ;;
            commands) install_commands ;;
            skills)   install_skills ;;
            hooks)    install_hooks ;;
            rules)    install_rules ;;
            mcp)      install_mcp ;;
        esac
    done
else
    # ── Interactive menu ──────────────────────────────────────────────────────
    echo -e "\n${BOLD}Personal Claude Code Config Installer${NC}"
    echo "Source : ${SRC}"
    echo "Target : ${DST}"
    echo ""
    printf "  1. Agents   (%s files)\n"    "$(count_files "$SRC/agents")"
    printf "  2. Commands (%s files)\n"    "$(count_files "$SRC/commands")"
    printf "  3. Skills   (%s dirs)\n"     "$(count_dirs  "$SRC/skills")"
    printf "  4. Hooks + scripts\n"
    printf "  5. Rules    (%s files)\n"    "$(count_files "$SRC/rules/common")"
    printf "  6. MCP + hooks setup\n"
    printf "  7. All of the above\n"
    printf "  8. Sync local → repo\n"
    printf "  0. Exit\n\n"
    read -rp "Choice: " choice
    case "$choice" in
        1) install_agents ;;
        2) install_commands ;;
        3) install_skills ;;
        4) install_hooks ;;
        5) install_rules ;;
        6) install_mcp ;;
        7) install_agents; install_commands; install_skills
           install_hooks; install_rules; install_mcp ;;
        8) sync_from_local ;;
        0) exit 0 ;;
        *) log_err "Invalid choice"; exit 1 ;;
    esac
fi

echo ""
log_ok "Done."
