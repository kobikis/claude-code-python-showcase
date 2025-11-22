#!/usr/bin/env python3
"""
Claude Code Infrastructure Setup Script

Applies production-ready Claude Code infrastructure to your FastAPI project.
This script creates skills, agents, hooks, and example implementations.

Usage:
    python setup_target_project.py --target /path/to/your/project
    python setup_target_project.py --target /path/to/your/project --component skills
    python setup_target_project.py --target /path/to/your/project --all
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
    """Main setup orchestrator"""

    def __init__(self, target_path: str, source_path: Optional[str] = None):
        self.target = Path(target_path).resolve()
        self.source = Path(source_path).resolve() if source_path else Path(__file__).parent
        self.backup_dir = self.target / ".claude_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")

        # Validate paths
        if not self.target.exists():
            raise ValueError(f"Target project not found: {self.target}")
        if not self.source.exists():
            raise ValueError(f"Source path not found: {self.source}")

        self.claude_dir = self.target / ".claude"
        self.claude_dir.mkdir(exist_ok=True)

    def create_backup(self, paths: List[Path]):
        """Create backup of existing files"""
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

    def setup_skills(self, skill_names: Optional[List[str]] = None):
        """Install Claude Code skills"""
        print_header("Installing Skills")

        skills_to_install = skill_names or [
            "webhook-security",
            "api-security",
            "resilience-patterns",
            "async-kafka",
            "pydantic-v2-migration",
            "event-driven-patterns"
        ]

        skills_dir = self.claude_dir / "skills"
        skills_dir.mkdir(exist_ok=True)

        for skill_name in skills_to_install:
            print_info(f"Creating skill: {skill_name}")
            self._create_skill(skill_name)
            print_success(f"Skill created: {skill_name}")

        # Update skill-rules.json
        self._update_skill_rules(skills_to_install)
        print_success("Skills installation complete")

    def setup_agents(self):
        """Install custom agents"""
        print_header("Installing Custom Agents")

        agents_dir = self.claude_dir / "agents"
        agents_dir.mkdir(exist_ok=True)

        agents = [
            "webhook-validator",
            "kafka-optimizer",
            "security-auditor",
            "async-converter"
        ]

        for agent_name in agents:
            print_info(f"Creating agent: {agent_name}")
            self._create_agent(agent_name)
            print_success(f"Agent created: {agent_name}")

        print_success("Agents installation complete")

    def setup_commands(self):
        """Install slash commands"""
        print_header("Installing Slash Commands")

        commands_dir = self.claude_dir / "commands"
        commands_dir.mkdir(exist_ok=True)

        commands = [
            "check-prod-readiness",
            "kafka-health",
            "webhook-test",
            "security-scan",
            "migrate-pydantic-v2"
        ]

        for command_name in commands:
            print_info(f"Creating command: {command_name}")
            self._create_command(command_name)
            print_success(f"Command created: /{command_name}")

        print_success("Commands installation complete")

    def setup_hooks(self):
        """Install additional hooks"""
        print_header("Installing Additional Hooks")

        hooks_dir = self.claude_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        hooks = [
            "pre-commit",
            "complexity-detector",
            "dependency-checker"
        ]

        for hook_name in hooks:
            print_info(f"Creating hook: {hook_name}")
            self._create_hook(hook_name)
            print_success(f"Hook created: {hook_name}.py")

        print_success("Hooks installation complete")

    def setup_examples(self):
        """Create example implementations"""
        print_header("Creating Example Implementations")

        examples_dir = self.target / "examples" / "claude_patterns"
        examples_dir.mkdir(parents=True, exist_ok=True)

        examples = [
            "circuit_breaker",
            "idempotency",
            "webhook_verifier",
            "async_kafka",
            "base_service"
        ]

        for example_name in examples:
            print_info(f"Creating example: {example_name}")
            self._create_example(example_name)
            print_success(f"Example created: {example_name}.py")

        print_success("Examples installation complete")

    def update_dependencies(self):
        """Update requirements.txt"""
        print_header("Updating Dependencies")

        req_file = self.target / "requirements.txt"

        if req_file.exists():
            self.create_backup([req_file])

        new_deps = [
            "\n# Added by Claude Code setup",
            "# Async Kafka",
            "aiokafka>=0.10.0",
            "",
            "# Resilience",
            "tenacity>=8.2.0",
            "pybreaker>=1.0.0",
            "",
            "# Security",
            "python-jose[cryptography]>=3.3.0",
            "slowapi>=0.1.9",
            "",
            "# Observability",
            "structlog>=23.1.0",
            "",
            "# Caching & Idempotency",
            "redis[hiredis]>=5.0.0",
            "",
            "# Testing",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "faker>=20.0.0",
            "",
            "# Security scanning",
            "bandit>=1.7.5",
            "safety>=2.3.0",
        ]

        with open(req_file, 'a') as f:
            f.write('\n'.join(new_deps))

        print_success("Dependencies updated in requirements.txt")
        print_warning("Run: pip install -r requirements.txt")

    def _create_skill(self, skill_name: str):
        """Create a skill directory and files"""
        from skills_generator import create_skill
        skill_dir = self.claude_dir / "skills" / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        create_skill(skill_name, skill_dir)

    def _create_agent(self, agent_name: str):
        """Create an agent file"""
        from agents_generator import create_agent
        agent_file = self.claude_dir / "agents" / f"{agent_name}.md"
        create_agent(agent_name, agent_file)

    def _create_command(self, command_name: str):
        """Create a slash command file"""
        from commands_generator import create_command
        command_file = self.claude_dir / "commands" / f"{command_name}.md"
        create_command(command_name, command_file)

    def _create_hook(self, hook_name: str):
        """Create a hook file"""
        from hooks_generator import create_hook
        hook_file = self.claude_dir / "hooks" / f"{hook_name}.py"
        create_hook(hook_name, hook_file)

    def _create_example(self, example_name: str):
        """Create an example implementation"""
        from examples_generator import create_example
        example_file = self.target / "examples" / "claude_patterns" / f"{example_name}.py"
        create_example(example_name, example_file)

    def _update_skill_rules(self, skill_names: List[str]):
        """Update skill-rules.json with new skills"""
        from skills_generator import generate_skill_rules
        rules_file = self.claude_dir / "skills" / "skill-rules.json"
        generate_skill_rules(skill_names, rules_file)

    def create_readme(self):
        """Create README for Claude Code setup"""
        readme_path = self.claude_dir / "README.md"

        readme_content = f"""# Claude Code Infrastructure

This directory contains Claude Code infrastructure for your project.

## Installation Date
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Components Installed

### Skills
Custom skills for FastAPI, webhooks, and microservices patterns.

### Agents
Specialized agents for security, optimization, and validation.

### Commands
Slash commands for common operations.

### Hooks
Automated hooks for quality assurance and validation.

## Usage

### Activating Skills
Skills activate automatically based on your prompts and files you're editing.

### Running Commands
- `/check-prod-readiness` - Check production readiness
- `/kafka-health` - Check Kafka health
- `/webhook-test` - Generate webhook tests
- `/security-scan` - Run security scans

### Using Agents
Agents are invoked automatically by Claude based on context.

## Examples

Example implementations are available in `examples/claude_patterns/`

## Backup

Original files backed up in `.claude_backup/`

## Next Steps

1. Review the skills in `.claude/skills/`
2. Install dependencies: `pip install -r requirements.txt`
3. Test with: "I need to add webhook signature verification"
4. Review examples in `examples/claude_patterns/`

## Documentation

- Skills follow the 500-line rule (main SKILL.md + resources/)
- Hooks are Python scripts executed on events
- Commands are markdown files with prompts
- Agents are markdown files with specialized instructions
"""

        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print_success(f"README created at: {readme_path}")


def interactive_menu(setup: ProjectSetup):
    """Interactive installation menu"""
    print_header("Claude Code Infrastructure Setup")
    print(f"Target Project: {setup.target}")
    print(f"Source: {setup.source}\n")

    print("Select components to install:")
    print("  1. Skills (webhook-security, api-security, etc.)")
    print("  2. Agents (webhook-validator, security-auditor, etc.)")
    print("  3. Slash Commands (/check-prod-readiness, etc.)")
    print("  4. Hooks (pre-commit, complexity-detector, etc.)")
    print("  5. Example Implementations")
    print("  6. Update Dependencies")
    print("  7. All of the above")
    print("  0. Exit")

    choice = input("\nEnter your choice (0-7): ").strip()

    if choice == "0":
        print_info("Setup cancelled")
        return

    if choice == "1" or choice == "7":
        setup.setup_skills()

    if choice == "2" or choice == "7":
        setup.setup_agents()

    if choice == "3" or choice == "7":
        setup.setup_commands()

    if choice == "4" or choice == "7":
        setup.setup_hooks()

    if choice == "5" or choice == "7":
        setup.setup_examples()

    if choice == "6" or choice == "7":
        setup.update_dependencies()

    if choice == "7":
        setup.create_readme()

    print_header("Setup Complete")
    print_success("Claude Code infrastructure installed successfully!")
    print_info(f"Backup location: {setup.backup_dir}")
    print_info("\nNext steps:")
    print("  1. pip install -r requirements.txt")
    print("  2. Review .claude/README.md")
    print("  3. Test with: 'I need to add webhook signature verification'")


def main():
    parser = argparse.ArgumentParser(
        description="Setup Claude Code infrastructure for FastAPI projects"
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target project path"
    )
    parser.add_argument(
        "--source",
        help="Source path (defaults to script directory)"
    )
    parser.add_argument(
        "--component",
        choices=["skills", "agents", "commands", "hooks", "examples", "deps"],
        help="Install specific component"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install all components"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without prompts"
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
