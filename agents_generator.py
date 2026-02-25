"""
Agents Generator Module

Copies agent files from the .claude/agents/ source directory.
"""

import shutil
from pathlib import Path


AGENT_NAMES = [
    "planner",
    "architect",
    "tdd-guide",
    "code-reviewer",
    "security-reviewer",
    "fastapi-specialist",
    "aws-specialist",
    "k8s-specialist",
    "python-database-expert",
    "python-debugger",
]


def get_source_agents_dir() -> Path:
    """Get the source .claude/agents/ directory."""
    return Path(__file__).parent / ".claude" / "agents"


def copy_agent(agent_name: str, target_dir: Path) -> Path:
    """Copy an agent markdown file from source to target.

    Args:
        agent_name: Name of the agent (without .md extension).
        target_dir: Target .claude/agents/ directory.

    Returns:
        Path to the copied agent file.

    Raises:
        FileNotFoundError: If the source agent file does not exist.
    """
    source_file = get_source_agents_dir() / f"{agent_name}.md"
    if not source_file.exists():
        raise FileNotFoundError(f"Agent source not found: {source_file}")

    target_file = target_dir / f"{agent_name}.md"
    shutil.copy2(source_file, target_file)
    return target_file


def copy_all_agents(target_dir: Path) -> list[Path]:
    """Copy all agents from source to target directory.

    Args:
        target_dir: Target .claude/agents/ directory.

    Returns:
        List of paths to copied agent files.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    return [copy_agent(name, target_dir) for name in AGENT_NAMES]
