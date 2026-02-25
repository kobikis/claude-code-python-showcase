"""
Hooks Generator Module

Copies hook scripts and JS libraries from the .claude/ source directory.
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

# Shell/Python hooks in .claude/hooks/
HOOK_FILES = [
    "protect-files.sh",
    "block-dangerous-bash.sh",
    "session-context.sh",
    "validate-sql.py",
]

# JS hook scripts in .claude/scripts/hooks/
JS_HOOK_FILES = [
    "session-start.js",
    "session-end.js",
    "evaluate-session.js",
    "pre-compact.js",
    "suggest-compact.js",
]

# JS library modules in .claude/scripts/lib/
JS_LIB_FILES = [
    "session-manager.js",
    "session-manager.d.ts",
    "session-aliases.js",
    "session-aliases.d.ts",
    "package-manager.js",
    "package-manager.d.ts",
    "utils.js",
    "utils.d.ts",
]


def get_source_dir() -> Path:
    """Get the source .claude/ directory."""
    return Path(__file__).parent / ".claude"


def _copy_file_list(
    file_list: list[str],
    source_dir: Path,
    target_dir: Path,
    executable_ext: str | None = None,
) -> tuple[list[Path], list[str]]:
    """Copy a list of files from source to target directory.

    Args:
        file_list: Filenames to copy.
        source_dir: Source directory containing the files.
        target_dir: Target directory to copy into.
        executable_ext: If set, files ending with this get chmod 755.

    Returns:
        Tuple of (copied paths, skipped filenames).
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    skipped: list[str] = []

    for filename in file_list:
        source = source_dir / filename
        if not source.exists():
            logger.warning("Hook source file not found, skipping: %s", source)
            skipped.append(filename)
            continue
        target = target_dir / filename
        shutil.copy2(source, target)
        if executable_ext and filename.endswith(executable_ext):
            target.chmod(0o755)
        copied.append(target)

    return copied, skipped


def copy_hooks(target_claude_dir: Path) -> tuple[list[Path], list[str]]:
    """Copy shell/Python hook files to target .claude/hooks/.

    Args:
        target_claude_dir: Target .claude/ directory.

    Returns:
        Tuple of (copied paths, skipped filenames).
    """
    return _copy_file_list(
        HOOK_FILES,
        get_source_dir() / "hooks",
        target_claude_dir / "hooks",
        executable_ext=".sh",
    )


def copy_js_hooks(target_claude_dir: Path) -> tuple[list[Path], list[str]]:
    """Copy JS hook scripts to target .claude/scripts/hooks/.

    Args:
        target_claude_dir: Target .claude/ directory.

    Returns:
        Tuple of (copied paths, skipped filenames).
    """
    return _copy_file_list(
        JS_HOOK_FILES,
        get_source_dir() / "scripts" / "hooks",
        target_claude_dir / "scripts" / "hooks",
    )


def copy_js_libs(target_claude_dir: Path) -> tuple[list[Path], list[str]]:
    """Copy JS library modules to target .claude/scripts/lib/.

    Args:
        target_claude_dir: Target .claude/ directory.

    Returns:
        Tuple of (copied paths, skipped filenames).
    """
    return _copy_file_list(
        JS_LIB_FILES,
        get_source_dir() / "scripts" / "lib",
        target_claude_dir / "scripts" / "lib",
    )


def copy_all_hooks_and_scripts(
    target_claude_dir: Path,
) -> tuple[list[Path], list[str]]:
    """Copy all hooks, JS hooks, and JS libraries to target.

    Args:
        target_claude_dir: Target .claude/ directory.

    Returns:
        Tuple of (all copied paths, all skipped filenames).
    """
    all_copied: list[Path] = []
    all_skipped: list[str] = []

    for copy_fn in (copy_hooks, copy_js_hooks, copy_js_libs):
        copied, skipped = copy_fn(target_claude_dir)
        all_copied.extend(copied)
        all_skipped.extend(skipped)

    return all_copied, all_skipped
