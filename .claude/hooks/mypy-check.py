#!/usr/bin/env python3
"""
Mypy Type Check Hook for Claude Code

Runs mypy type checking on session stop to ensure type safety.

Input: JSON from stdin with session data
Output: Type checking results or errors
"""

import json
import sys
import subprocess
from pathlib import Path


def run_mypy(project_root: Path) -> tuple[int, str, str]:
    """Run mypy type checker"""
    try:
        result = subprocess.run(
            ["mypy", "."],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", "mypy not found - install with: pip install mypy"
    except subprocess.TimeoutExpired:
        return 1, "", "mypy check timed out after 30 seconds"
    except Exception as e:
        return 1, "", f"Error running mypy: {str(e)}"


def format_output(returncode: int, stdout: str, stderr: str) -> str:
    """Format mypy output for display"""
    if returncode == 0:
        return "\n✅ Type checking passed - no mypy errors\n"

    output_lines = ["\n⚠️ Type Checking Issues Found:\n"]

    if stderr:
        output_lines.append(f"Error: {stderr}\n")

    if stdout:
        # Show first 10 lines of errors
        lines = stdout.split("\n")[:10]
        output_lines.extend(lines)

        if len(stdout.split("\n")) > 10:
            output_lines.append("\n... (additional errors omitted)")

    output_lines.append("\nRun `mypy .` to see full details")

    return "\n".join(output_lines)


def main():
    """Main entry point for the hook"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        project_root = Path(input_data.get("projectRoot", "."))

        # Check if mypy.ini or pyproject.toml exists
        if not (project_root / "mypy.ini").exists() and \
           not (project_root / "pyproject.toml").exists():
            print("\n⚠️ No mypy configuration found - skipping type check")
            print("Create mypy.ini or add [tool.mypy] to pyproject.toml to enable\n")
            sys.exit(0)

        # Run mypy
        returncode, stdout, stderr = run_mypy(project_root)

        # Format and output results
        output = format_output(returncode, stdout, stderr)
        print(output)

        # Exit with mypy's return code
        sys.exit(returncode)

    except Exception as e:
        print(f"⚠️ Mypy hook error: {str(e)}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
