"""
Commands Generator Module

Copies command files from the .claude/commands/ source directory.
"""

import shutil
from pathlib import Path


COMMAND_NAMES = [
    "pr",
    "plan",
    "tdd",
    "code-review",
    "build-fix",
    "test-coverage",
    "verify",
    "update-docs",
    "orchestrate",
    "pipecat-rca",
    "create-subagent",
    "create-command",
]


def get_source_commands_dir() -> Path:
    """Get the source .claude/commands/ directory."""
    return Path(__file__).parent / ".claude" / "commands"


def copy_command(command_name: str, target_dir: Path) -> Path:
    """Copy a command markdown file from source to target.

    Args:
        command_name: Name of the command (without .md extension).
        target_dir: Target .claude/commands/ directory.

    Returns:
        Path to the copied command file.

    Raises:
        FileNotFoundError: If the source command file does not exist.
    """
    source_file = get_source_commands_dir() / f"{command_name}.md"
    if not source_file.exists():
        raise FileNotFoundError(f"Command source not found: {source_file}")

    target_file = target_dir / f"{command_name}.md"
    shutil.copy2(source_file, target_file)
    return target_file


def copy_all_commands(target_dir: Path) -> list[Path]:
    """Copy all commands from source to target directory.

    Args:
        target_dir: Target .claude/commands/ directory.

    Returns:
        List of paths to copied command files.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    return [copy_command(name, target_dir) for name in COMMAND_NAMES]
