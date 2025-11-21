#!/usr/bin/env python3
"""
Post-Tool-Use Tracker Hook for Claude Code

Tracks file edits and suggests improvements based on patterns.
Helps maintain code quality and consistency.

Input: JSON from stdin with tool usage data
Output: Suggestions for code improvements or additional actions
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def analyze_edit_patterns(tool_data: Dict[str, Any]) -> List[str]:
    """Analyze edit patterns and suggest improvements"""
    suggestions = []
    tool_name = tool_data.get("tool", "")
    file_path = tool_data.get("file_path", "")

    if not file_path:
        return suggestions

    path = Path(file_path)

    # Python-specific checks
    if path.suffix == ".py":
        suggestions.extend(check_python_file(tool_data, path))

    # Test file checks
    if "test" in path.name or path.parent.name == "tests":
        suggestions.extend(check_test_file(tool_data, path))

    # Configuration file checks
    if path.name in ["pyproject.toml", "setup.py", "requirements.txt"]:
        suggestions.extend(check_config_file(tool_data, path))

    return suggestions


def check_python_file(tool_data: Dict[str, Any], path: Path) -> List[str]:
    """Check Python file edits and suggest improvements"""
    suggestions = []
    content = tool_data.get("new_content", "") or tool_data.get("content", "")

    # Check for type hints
    if "def " in content and "->" not in content:
        suggestions.append(
            "💡 Consider adding type hints to function signatures for better IDE support and type checking"
        )

    # Check for docstrings
    if "def " in content or "class " in content:
        if '"""' not in content and "'''" not in content:
            suggestions.append(
                "📝 Consider adding docstrings to document your functions and classes"
            )

    # Check for imports that might need sorting
    import_count = content.count("import ") + content.count("from ")
    if import_count > 5:
        suggestions.append(
            "🔧 Consider running `ruff check --select I` or `isort` to organize imports"
        )

    # Check for potential SQLAlchemy models
    if "class " in content and "Base" in content:
        if "__tablename__" not in content:
            suggestions.append(
                "🗄️ SQLAlchemy model detected - ensure __tablename__ is defined"
            )

    # Check for FastAPI routes
    if "@app." in content or "@router." in content:
        if "response_model" not in content:
            suggestions.append(
                "🚀 FastAPI route detected - consider adding response_model for better docs"
            )

    return suggestions


def check_test_file(tool_data: Dict[str, Any], path: Path) -> List[str]:
    """Check test file edits and suggest improvements"""
    suggestions = []
    content = tool_data.get("new_content", "") or tool_data.get("content", "")

    # Check for pytest fixtures
    if "def test_" in content and "@pytest.fixture" not in content:
        suggestions.append(
            "🧪 Consider using pytest fixtures for test setup and teardown"
        )

    # Check for assertions
    if "def test_" in content and "assert " not in content:
        suggestions.append(
            "⚠️ Test function without assertions detected - ensure proper validation"
        )

    # Check for test coverage
    suggestions.append(
        "📊 Remember to run `pytest --cov` to check test coverage after adding tests"
    )

    return suggestions


def check_config_file(tool_data: Dict[str, Any], path: Path) -> List[str]:
    """Check configuration file edits"""
    suggestions = []

    if path.name == "requirements.txt":
        suggestions.append(
            "📦 requirements.txt updated - run `pip install -r requirements.txt` to update dependencies"
        )
    elif path.name == "pyproject.toml":
        suggestions.append(
            "📦 pyproject.toml updated - run `poetry install` or `pip install -e .` to update"
        )
    elif path.name == "setup.py":
        suggestions.append(
            "📦 setup.py updated - run `pip install -e .` to install in editable mode"
        )

    return suggestions


def track_edit_statistics(tool_data: Dict[str, Any]) -> Dict[str, Any]:
    """Track statistics about edits (for future analysis)"""
    stats = {
        "file_type": Path(tool_data.get("file_path", "")).suffix,
        "tool_used": tool_data.get("tool", ""),
        "timestamp": tool_data.get("timestamp", "")
    }
    return stats


def format_suggestions(suggestions: List[str]) -> str:
    """Format suggestions for display"""
    if not suggestions:
        return ""

    output_lines = ["\n💡 Post-Edit Suggestions:\n"]
    output_lines.extend([f"  {s}" for s in suggestions[:3]])  # Limit to 3 suggestions

    return "\n".join(output_lines)


def main():
    """Main entry point for the hook"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Analyze edit patterns
        suggestions = analyze_edit_patterns(input_data)

        # Format and output suggestions
        output = format_suggestions(suggestions)

        if output:
            print(output)

        # Exit successfully
        sys.exit(0)

    except Exception as e:
        # Log error but don't block the user
        print(f"⚠️ Post-tool-use tracker error: {str(e)}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
