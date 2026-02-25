#!/usr/bin/env python3
"""
Claude Code Infrastructure Setup Script

Copies production-ready Claude Code infrastructure from .claude/ source into
your Python/FastAPI project. All content is copied from source files — no
inline templates.

Usage:
    python setup_target_project.py --target /path/to/your/project
    python setup_target_project.py --target /path/to/your/project --component skills
    python setup_target_project.py --target /path/to/your/project --all
    python setup_target_project.py --target /path/to/your/project --all --non-interactive
"""

import sys
import json
import shutil
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional

from agents_generator import copy_all_agents
from commands_generator import copy_all_commands
from compile_rules import load_rules, compile_to_claude_md
from examples_generator import EXAMPLE_TEMPLATES, create_example
from hooks_generator import copy_all_hooks_and_scripts
from skills_generator import SKILL_NAMES, copy_all_skills, generate_skill_rules


# Color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(message: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(message: str):
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")


def print_warning(message: str):
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {message}")


def print_error(message: str):
    print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")


def print_info(message: str):
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {message}")


class ProjectSetup:
    """Main setup orchestrator — copies from .claude/ source of truth."""

    def __init__(self, target_path: str, source_path: Optional[str] = None):
        self.target = Path(target_path).resolve()
        self.source = (
            Path(source_path).resolve() if source_path else Path(__file__).parent
        )
        self.backup_dir = (
            self.target / ".claude_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        if not self.target.exists():
            raise ValueError(f"Target project not found: {self.target}")
        if not self.source.exists():
            raise ValueError(f"Source path not found: {self.source}")

        self.claude_dir = self.target / ".claude"
        self.claude_dir.mkdir(exist_ok=True)

    def create_backup(self, paths: list[Path]):
        """Create backup of existing files."""
        if not paths:
            return

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        for path in paths:
            if not path.exists():
                continue

            relative_path = path.relative_to(self.target)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            if path.is_file():
                shutil.copy2(path, backup_path)
            else:
                shutil.copytree(path, backup_path, dirs_exist_ok=True)

        print_success(f"Backup created at: {self.backup_dir}")

    def setup_skills(self):
        """Copy skill directories from source."""
        print_header("Installing Skills")

        skills_dir = self.claude_dir / "skills"
        skills_dir.mkdir(exist_ok=True)

        copied = copy_all_skills(skills_dir)
        for path in copied:
            print_success(f"Skill copied: {path.name}")

        # Generate skill-rules.json
        rules_file = skills_dir / "skill-rules.json"
        generate_skill_rules(SKILL_NAMES, rules_file)
        print_success(f"skill-rules.json generated with {len(SKILL_NAMES)} entries")

        print_success("Skills installation complete")

    def setup_agents(self):
        """Copy agent files from source."""
        print_header("Installing Agents")

        agents_dir = self.claude_dir / "agents"
        copied = copy_all_agents(agents_dir)
        for path in copied:
            print_success(f"Agent copied: {path.name}")

        print_success("Agents installation complete")

    def setup_commands(self):
        """Copy slash command files from source."""
        print_header("Installing Slash Commands")

        commands_dir = self.claude_dir / "commands"
        copied = copy_all_commands(commands_dir)
        for path in copied:
            print_success(f"Command copied: /{path.stem}")

        print_success("Commands installation complete")

    def setup_hooks(self):
        """Copy hook scripts and JS hooks/libs from source."""
        print_header("Installing Hooks & Scripts")

        copied, skipped = copy_all_hooks_and_scripts(self.claude_dir)
        for path in copied:
            relative = path.relative_to(self.claude_dir)
            print_success(f"Copied: {relative}")

        for filename in skipped:
            print_warning(f"Source not found, skipped: {filename}")

        print_success("Hooks & scripts installation complete")

    def setup_rules(self):
        """Copy rule files from source."""
        print_header("Installing Rules")

        source_rules = self.source / ".claude" / "rules"
        if not source_rules.exists():
            print_warning("Source rules directory not found — skipping")
            return

        target_rules = self.claude_dir / "rules"

        # Copy common rules
        common_src = source_rules / "common"
        if common_src.exists():
            common_dst = target_rules / "common"
            if common_dst.exists():
                shutil.rmtree(common_dst)
            shutil.copytree(common_src, common_dst)
            count = len(list(common_dst.glob("*.md")))
            print_success(f"Common rules copied: {count} files")

        # Copy python rules
        python_src = source_rules / "python"
        if python_src.exists():
            python_dst = target_rules / "python"
            if python_dst.exists():
                shutil.rmtree(python_dst)
            shutil.copytree(python_src, python_dst)
            count = len(list(python_dst.glob("*.md")))
            print_success(f"Python rules copied: {count} files")

        print_success("Rules installation complete")

    def setup_examples(self):
        """Create example implementations."""
        print_header("Creating Example Implementations")

        examples_dir = self.target / "examples" / "claude_patterns"
        examples_dir.mkdir(parents=True, exist_ok=True)

        for example_name in EXAMPLE_TEMPLATES:
            print_info(f"Creating example: {example_name}")
            example_file = examples_dir / f"{example_name}.py"
            create_example(example_name, example_file)
            print_success(f"Example created: {example_name}.py")

        print_success("Examples installation complete")

    def update_dependencies(self):
        """Update requirements.txt with recommended packages."""
        print_header("Updating Dependencies")

        req_file = self.target / "requirements.txt"

        if req_file.exists():
            self.create_backup([req_file])

        new_deps = [
            "\n# Added by Claude Code setup",
            "# Async HTTP",
            "httpx>=0.27.0",
            "",
            "# Web Framework",
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.30.0",
            "",
            "# Database",
            "sqlalchemy[asyncio]>=2.0.0",
            "asyncpg>=0.29.0",
            "alembic>=1.13.0",
            "",
            "# Validation & Settings",
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
            "",
            "# Observability",
            "structlog>=23.1.0",
            "",
            "# Security",
            "python-jose[cryptography]>=3.3.0",
            "",
            "# Caching",
            "redis[hiredis]>=5.0.0",
            "",
            "# Testing",
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "faker>=20.0.0",
            "",
            "# Code Quality",
            "ruff>=0.4.0",
            "mypy>=1.8.0",
            "",
            "# Security Scanning",
            "bandit>=1.7.5",
            "",
        ]

        with open(req_file, "a") as f:
            f.write("\n".join(new_deps))

        print_success("Dependencies updated in requirements.txt")
        print_warning("Run: pip install -r requirements.txt")

    def install_session_hook(self):
        """Register session-start hook in settings.json.

        Builds a new settings dict immutably rather than mutating in place.
        """
        print_header("Registering Session Hook")

        hook_path = self.claude_dir / "scripts" / "hooks" / "session-start.js"
        if not hook_path.exists():
            print_warning("session-start.js not found — run setup_hooks() first")
            return

        settings_path = self.claude_dir / "settings.json"
        settings: dict = {}
        if settings_path.exists():
            with open(settings_path) as f:
                settings = json.load(f)

        existing_hooks = settings.get("hooks", {})
        existing_session_hooks = existing_hooks.get("SessionStart", [])

        already_registered = any(
            any(
                h.get("command", "").endswith("session-start.js")
                for h in entry.get("hooks", [])
            )
            for entry in existing_session_hooks
        )

        if already_registered:
            print_info("Session hook already registered — skipping")
            return

        hook_entry = {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": f"node {hook_path}",
                    "description": "Inject skill routing rules and project context at session start",
                }
            ],
        }

        # Build new settings immutably
        updated_session_hooks = [*existing_session_hooks, hook_entry]
        updated_hooks = {**existing_hooks, "SessionStart": updated_session_hooks}
        updated_settings = {**settings, "hooks": updated_hooks}

        with open(settings_path, "w") as f:
            json.dump(updated_settings, f, indent=2)
        print_success(f"Session hook registered in: {settings_path}")

    def compile_rules_to_claude_md(self):
        """Compile skill-rules.json into CLAUDE.md routing instructions."""
        print_header("Compiling Skill Routes → CLAUDE.md")

        rules_file = self.claude_dir / "skills" / "skill-rules.json"
        if not rules_file.exists():
            print_warning("skill-rules.json not found — run setup_skills() first")
            return

        rules = load_rules(rules_file)
        claude_md_file = self.target / "CLAUDE.md"
        compile_to_claude_md(rules, claude_md_file)
        print_success(f"Skill routing rules compiled into: {claude_md_file}")

    def create_readme(self):
        """Create README for Claude Code setup."""
        readme_path = self.claude_dir / "README.md"

        readme_content = f"""# Claude Code Infrastructure

This directory contains Claude Code infrastructure copied from the
claude-code-python-showcase source of truth.

## Installation Date
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Components Installed

### Skills (12)
Pattern libraries copied from source `.claude/skills/`:
python-patterns, async-python-patterns, python-testing, tdd-workflow,
postgres-patterns, docker-patterns, deployment-patterns, security-review,
design-doc-mermaid, perplexity-deep-search, verification-loop, strategic-compact

### Agents (10)
Specialist agents copied from source `.claude/agents/`:
planner, architect, tdd-guide, code-reviewer, security-reviewer,
fastapi-specialist, aws-specialist, k8s-specialist, python-database-expert,
python-debugger

### Commands (9)
Slash commands copied from source `.claude/commands/`:
/pr, /plan, /tdd, /code-review, /build-fix, /test-coverage, /verify,
/update-docs, /orchestrate

### Hooks & Scripts
- Shell/Python hooks in `.claude/hooks/`
- JS hook scripts in `.claude/scripts/hooks/`
- JS library modules in `.claude/scripts/lib/`

### Rules (13)
- 8 common rules in `.claude/rules/common/`
- 5 Python-specific rules in `.claude/rules/python/`

## Usage

### Activating Skills
Skills activate automatically based on intent patterns and file paths.

### Running Commands
- `/orchestrate` - Multi-agent workflow orchestration
- `/plan` - Create implementation plan
- `/tdd` - Test-driven development workflow
- `/code-review` - Code quality review
- `/pr` - Create pull request with summary
- `/verify` - Run verification checks
- `/test-coverage` - Analyze test coverage
- `/build-fix` - Troubleshoot build failures
- `/update-docs` - Update documentation

### Using Agents
Agents are invoked via the Task tool based on routing rules in CLAUDE.md.

## Updating

To update components from the showcase:
```bash
./update_component.sh /path/to/this/project [skills|agents|commands|hooks|rules|all]
```

## Backup

Original files backed up in `.claude_backup/`
"""

        with open(readme_path, "w") as f:
            f.write(readme_content)

        print_success(f"README created at: {readme_path}")


def interactive_menu(setup: ProjectSetup):
    """Interactive installation menu."""
    print_header("Claude Code Infrastructure Setup")
    print(f"Target Project: {setup.target}")
    print(f"Source: {setup.source}\n")

    print("Select components to install:")
    print("  1. Skills (12 pattern libraries)")
    print("  2. Agents (10 specialist agents)")
    print("  3. Slash Commands (9 commands)")
    print("  4. Hooks & Scripts (shell hooks + JS hooks + JS libs)")
    print("  5. Rules (8 common + 5 Python-specific)")
    print("  6. Example Implementations")
    print("  7. Update Dependencies")
    print("  8. All of the above (recommended)")
    print("  ---")
    print("  9. Session Start Hook only")
    print("  10. Compile Rules → CLAUDE.md only")
    print("  0. Exit")

    choice = input("\nEnter your choice (0-10): ").strip()

    if choice == "0":
        print_info("Setup cancelled")
        return

    if choice in ("1", "8"):
        setup.setup_skills()

    if choice in ("2", "8"):
        setup.setup_agents()

    if choice in ("3", "8"):
        setup.setup_commands()

    if choice in ("4", "8"):
        setup.setup_hooks()

    if choice in ("5", "8"):
        setup.setup_rules()

    if choice in ("8", "9"):
        setup.install_session_hook()

    if choice in ("8", "10"):
        setup.compile_rules_to_claude_md()

    if choice in ("6", "8"):
        setup.setup_examples()

    if choice in ("7", "8"):
        setup.update_dependencies()

    if choice == "8":
        setup.create_readme()

    print_header("Setup Complete")
    print_success("Claude Code infrastructure installed successfully!")
    print_info(f"Backup location: {setup.backup_dir}")
    print_info("\nNext steps:")
    print("  1. pip install -r requirements.txt")
    print("  2. Review .claude/README.md")
    print("  3. Use /orchestrate to route tasks to specialist agents")


def main():
    parser = argparse.ArgumentParser(
        description="Setup Claude Code infrastructure for Python projects"
    )
    parser.add_argument("--target", required=True, help="Target project path")
    parser.add_argument("--source", help="Source path (defaults to script directory)")
    parser.add_argument(
        "--component",
        choices=[
            "skills",
            "agents",
            "commands",
            "hooks",
            "rules",
            "examples",
            "deps",
        ],
        help="Install specific component",
    )
    parser.add_argument("--all", action="store_true", help="Install all components")
    parser.add_argument(
        "--non-interactive", action="store_true", help="Run without prompts"
    )

    args = parser.parse_args()

    try:
        setup = ProjectSetup(args.target, args.source)

        if args.non_interactive or args.all or args.component:
            if args.all:
                setup.setup_skills()
                setup.setup_agents()
                setup.setup_commands()
                setup.setup_hooks()
                setup.setup_rules()
                setup.install_session_hook()
                setup.compile_rules_to_claude_md()
                setup.setup_examples()
                setup.update_dependencies()
                setup.create_readme()
            elif args.component == "skills":
                setup.setup_skills()
            elif args.component == "agents":
                setup.setup_agents()
            elif args.component == "commands":
                setup.setup_commands()
            elif args.component == "hooks":
                setup.setup_hooks()
            elif args.component == "rules":
                setup.setup_rules()
            elif args.component == "examples":
                setup.setup_examples()
            elif args.component == "deps":
                setup.update_dependencies()

            print_header("Setup Complete")
            print_success("Installation completed successfully!")
        else:
            interactive_menu(setup)

    except Exception as e:
        print_error(f"Setup failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
