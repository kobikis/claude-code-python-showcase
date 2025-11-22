"""
Hooks Generator Module

Generates Claude Code hook scripts.
"""

from pathlib import Path


HOOK_TEMPLATES = {
    "pre-commit": '''#!/usr/bin/env python3
"""
Pre-commit Hook

Runs quality checks before allowing commits.
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\\n🔍 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    """Run pre-commit checks"""
    print("=" * 60)
    print("Running Pre-Commit Checks")
    print("=" * 60)

    checks = [
        ("ruff check app/ --fix", "Code linting (ruff)"),
        ("ruff format app/", "Code formatting (ruff)"),
        ("mypy app/ --ignore-missing-imports", "Type checking (mypy)"),
        ("bandit -r app/ -ll", "Security scan (bandit)"),
    ]

    all_passed = True

    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False

    print("\\n" + "=" * 60)

    if all_passed:
        print("✅ All pre-commit checks passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some checks failed. Please fix and try again.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
''',

    "complexity-detector": '''#!/usr/bin/env python3
"""
Complexity Detector Hook

Analyzes code complexity after edits and suggests refactoring.
"""

import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple


class ComplexityAnalyzer(ast.NodeVisitor):
    """Calculate cyclomatic complexity"""

    def __init__(self):
        self.complexity = 1
        self.functions = []

    def visit_FunctionDef(self, node):
        func_complexity = self._calculate_function_complexity(node)
        self.functions.append({
            "name": node.name,
            "complexity": func_complexity,
            "line": node.lineno
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def _calculate_function_complexity(self, node):
        """Calculate complexity for a function"""
        complexity = 1

        for child in ast.walk(node):
            # Add complexity for control flow
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


def analyze_file(filepath: Path) -> Dict:
    """Analyze a Python file for complexity"""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())

        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)

        return {
            "file": str(filepath),
            "functions": analyzer.functions,
            "max_complexity": max((f["complexity"] for f in analyzer.functions), default=0)
        }
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return None


def main():
    """Analyze modified Python files"""
    # Get modified files from Claude context
    # In practice, this would be passed via environment or args
    import os
    modified_files = os.getenv("CLAUDE_MODIFIED_FILES", "").split(",")

    if not modified_files or modified_files == [""]:
        return 0

    print("\\n🔍 Analyzing code complexity...")
    high_complexity_functions = []

    for filepath in modified_files:
        if not filepath.endswith(".py"):
            continue

        path = Path(filepath)
        if not path.exists():
            continue

        result = analyze_file(path)
        if not result:
            continue

        # Flag functions with complexity > 10
        for func in result["functions"]:
            if func["complexity"] > 10:
                high_complexity_functions.append({
                    "file": result["file"],
                    "function": func["name"],
                    "complexity": func["complexity"],
                    "line": func["line"]
                })

    if high_complexity_functions:
        print("\\n⚠️  High complexity functions detected:")
        for item in high_complexity_functions:
            print(f"  - {item['file']}:{item['line']} - {item['function']}() "
                  f"(complexity: {item['complexity']})")
        print("\\n💡 Consider refactoring functions with complexity > 10")

    return 0


if __name__ == "__main__":
    sys.exit(main())
''',

    "dependency-checker": '''#!/usr/bin/env python3
"""
Dependency Checker Hook

Checks for vulnerabilities and outdated packages when requirements.txt changes.
"""

import sys
import subprocess
import json
from pathlib import Path


def run_safety_check():
    """Run safety check for known vulnerabilities"""
    print("🔍 Checking for known vulnerabilities...")

    try:
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print("✅ No known vulnerabilities found")
            return True
        else:
            vulnerabilities = json.loads(result.stdout)
            print(f"❌ Found {len(vulnerabilities)} vulnerabilities:")

            for vuln in vulnerabilities[:5]:  # Show first 5
                print(f"  - {vuln.get('package', 'Unknown')}: "
                      f"{vuln.get('vulnerability', 'No description')}")

            if len(vulnerabilities) > 5:
                print(f"  ... and {len(vulnerabilities) - 5} more")

            return False

    except FileNotFoundError:
        print("⚠️  safety not installed. Run: pip install safety")
        return True
    except Exception as e:
        print(f"⚠️  Error running safety: {e}")
        return True


def run_pip_audit():
    """Run pip-audit for comprehensive vulnerability scanning"""
    print("\\n🔍 Running comprehensive dependency audit...")

    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print("✅ Dependency audit passed")
            return True
        else:
            try:
                issues = json.loads(result.stdout)
                print(f"❌ Found dependency issues:")

                for issue in issues.get("dependencies", [])[:5]:
                    print(f"  - {issue.get('name', 'Unknown')}: "
                          f"{issue.get('version', 'Unknown version')}")
                    for vuln in issue.get("vulns", [])[:2]:
                        print(f"    CVE: {vuln.get('id', 'Unknown')}")

                return False
            except json.JSONDecodeError:
                print("⚠️  Could not parse pip-audit output")
                return True

    except FileNotFoundError:
        print("⚠️  pip-audit not installed. Run: pip install pip-audit")
        return True
    except Exception as e:
        print(f"⚠️  Error running pip-audit: {e}")
        return True


def check_outdated_packages():
    """Check for outdated packages"""
    print("\\n🔍 Checking for outdated packages...")

    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )

        outdated = json.loads(result.stdout)

        if not outdated:
            print("✅ All packages are up to date")
            return True

        # Only show major version updates
        major_updates = [
            pkg for pkg in outdated
            if pkg["latest_version"].split(".")[0] != pkg["version"].split(".")[0]
        ]

        if major_updates:
            print(f"⚠️  {len(major_updates)} packages have major version updates:")
            for pkg in major_updates[:5]:
                print(f"  - {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")

        return True

    except Exception as e:
        print(f"⚠️  Error checking outdated packages: {e}")
        return True


def main():
    """Run dependency checks"""
    import os

    # Check if requirements.txt was modified
    modified_files = os.getenv("CLAUDE_MODIFIED_FILES", "").split(",")

    if "requirements.txt" not in modified_files:
        return 0

    print("=" * 60)
    print("Dependency Security Check")
    print("=" * 60)

    all_passed = True

    if not run_safety_check():
        all_passed = False

    if not run_pip_audit():
        all_passed = False

    check_outdated_packages()

    print("\\n" + "=" * 60)

    if all_passed:
        print("✅ Dependency checks passed")
    else:
        print("❌ Dependency vulnerabilities found!")
        print("💡 Review and update vulnerable packages")

    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
'''
}


def create_hook(hook_name: str, hook_file: Path):
    """Create a hook Python file"""
    hook_file.parent.mkdir(parents=True, exist_ok=True)

    content = HOOK_TEMPLATES.get(
        hook_name,
        f'''#!/usr/bin/env python3
"""
{hook_name.replace('-', ' ').title()} Hook
"""

import sys

def main():
    print(f"Running {hook_name} hook...")
    # Hook implementation to be added
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    )

    with open(hook_file, 'w') as f:
        f.write(content)

    # Make executable
    hook_file.chmod(0o755)
