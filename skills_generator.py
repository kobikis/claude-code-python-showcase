"""
Skills Generator Module

Copies skill directories from the .claude/skills/ source and generates
skill-rules.json routing metadata.
"""

import json
import shutil
from pathlib import Path


SKILL_NAMES = [
    "python-patterns",
    "async-python-patterns",
    "python-testing",
    "tdd-workflow",
    "postgres-patterns",
    "docker-patterns",
    "deployment-patterns",
    "security-review",
    "design-doc-mermaid",
    "perplexity-deep-search",
    "verification-loop",
    "strategic-compact",
    "skill-architect",
    "pr-review",
]

# Routing metadata for skill-rules.json generation.
# Each entry defines keywords, intent patterns, and file paths used by
# compile_rules.py to build the CLAUDE.md routing table.
SKILL_METADATA: dict[str, dict] = {
    "python-patterns": {
        "description": "Python principles, framework selection, async patterns, type hints",
        "keywords": ["python", "framework", "type hints", "project structure"],
        "intent_patterns": [
            "(python|pythonic).*?(pattern|best practice|architecture)",
            "(project|code).*?structure",
            "type.*?hint",
        ],
        "file_paths": ["**/*.py"],
    },
    "async-python-patterns": {
        "description": "Asyncio, concurrent programming, async/await patterns",
        "keywords": ["async", "await", "asyncio", "concurrent", "httpx"],
        "intent_patterns": [
            "(async|await|asyncio).*?(pattern|convert|optimize)",
            "(blocking|sync).*?(to async|convert)",
            "concurrent.*?(programming|task)",
        ],
        "file_paths": ["**/*async*.py", "**/*concurrent*.py"],
    },
    "python-testing": {
        "description": "Pytest, TDD, fixtures, mocking, parametrization, 80%+ coverage",
        "keywords": ["pytest", "test", "fixture", "mock", "coverage"],
        "intent_patterns": [
            "(test|testing).*?(python|pytest|coverage)",
            "(fixture|mock|parametr).*?(test|setup)",
            "coverage.*?(report|check|increase)",
        ],
        "file_paths": ["**/tests/**/*.py", "**/test_*.py", "**/*_test.py"],
    },
    "tdd-workflow": {
        "description": "Test-first development, RED-GREEN-IMPROVE cycle",
        "keywords": ["tdd", "test first", "red green", "test driven"],
        "intent_patterns": [
            "(tdd|test.driven).*?(develop|workflow|approach)",
            "(write|create).*?test.*?first",
            "red.*?green.*?refactor",
        ],
        "file_paths": ["**/tests/**/*.py"],
    },
    "postgres-patterns": {
        "description": "PostgreSQL optimization, schema design, indexing",
        "keywords": ["postgres", "sql", "schema", "index", "query optimization"],
        "intent_patterns": [
            "(postgres|postgresql|sql).*?(optimize|schema|index)",
            "(query|database).*?(performance|slow|optimize)",
            "(schema|migration).*?design",
        ],
        "file_paths": ["**/models/**/*.py", "**/migrations/**/*.py", "**/*schema*.py"],
    },
    "docker-patterns": {
        "description": "Docker, Docker Compose, container security, volumes",
        "keywords": ["docker", "container", "dockerfile", "compose"],
        "intent_patterns": [
            "(docker|container).*?(build|optimize|secure)",
            "dockerfile.*?(create|review|optimize)",
            "(compose|multi.container).*?setup",
        ],
        "file_paths": ["**/Dockerfile*", "**/docker-compose*.yml", "**/.dockerignore"],
    },
    "deployment-patterns": {
        "description": "CI/CD, containerization, health checks, rollback strategies",
        "keywords": ["deploy", "ci/cd", "health check", "rollback", "kubernetes"],
        "intent_patterns": [
            "(deploy|deployment).*?(pattern|strategy|pipeline)",
            "(ci|cd|cicd).*?(pipeline|workflow|setup)",
            "(health.*?check|readiness|liveness)",
        ],
        "file_paths": [
            "**/.github/workflows/*.yml",
            "**/k8s/**/*.yaml",
            "**/helm/**/*",
        ],
    },
    "security-review": {
        "description": "Auth, secrets, API endpoints, security audit patterns",
        "keywords": ["security", "auth", "vulnerability", "owasp", "secrets"],
        "intent_patterns": [
            "(security|secure).*?(review|audit|scan)",
            "(auth|authentication|authorization).*?(implement|review)",
            "(vulnerability|owasp|injection).*?(check|prevent)",
        ],
        "file_paths": [
            "**/auth/**/*.py",
            "**/security/**/*.py",
            "**/middleware/**/*.py",
        ],
    },
    "design-doc-mermaid": {
        "description": "Mermaid diagrams for architecture, sequence, deployment docs",
        "keywords": ["mermaid", "diagram", "architecture", "sequence diagram"],
        "intent_patterns": [
            "(mermaid|diagram).*?(create|generate|design)",
            "(architecture|sequence|deployment).*?diagram",
            "(design.*?doc|technical.*?doc).*?(create|generate)",
        ],
        "file_paths": ["**/*.md", "**/docs/**/*"],
    },
    "perplexity-deep-search": {
        "description": "Deep search via Perplexity API for research tasks",
        "keywords": ["search", "research", "perplexity", "deep search"],
        "intent_patterns": [
            "(deep|thorough).*?search",
            "(research|investigate).*?(topic|question)",
            "perplexity.*?(search|api)",
        ],
        "file_paths": [],
    },
    "verification-loop": {
        "description": "Comprehensive verification and validation system",
        "keywords": ["verify", "validate", "check", "verification"],
        "intent_patterns": [
            "(verify|validate|check).*?(implementation|code|result)",
            "verification.*?(loop|cycle|process)",
        ],
        "file_paths": [],
    },
    "strategic-compact": {
        "description": "Manual context compaction at logical intervals",
        "keywords": ["compact", "context", "summarize"],
        "intent_patterns": [
            "(compact|compress).*?context",
            "strategic.*?(compact|summary)",
        ],
        "file_paths": [],
    },
    "skill-architect": {
        "description": "Build reusable Claude Code skills (SKILL.md files) from workflow descriptions",
        "keywords": [
            "create skill",
            "build skill",
            "encode workflow",
            "skill architect",
        ],
        "intent_patterns": [
            "(create|build|write|make).*?skill",
            "encode.*?(workflow|process|task)",
            "skill.*?(template|architect|framework)",
        ],
        "file_paths": [".claude/skills/**/*"],
    },
    "pr-review": {
        "description": "Reviews a GitHub PR diff for correctness, security, Python best practices, and test coverage",
        "keywords": ["pr review", "pull request", "code review", "review pr", "gh pr"],
        "intent_patterns": [
            "(review|check|analyze).*?(pr|pull.request)",
            "pr.*?(review|feedback|comments)",
            "(what.*?wrong|issues).*?(pr|pull.request)",
        ],
        "file_paths": [],
    },
}


def get_source_skills_dir() -> Path:
    """Get the source .claude/skills/ directory."""
    return Path(__file__).parent / ".claude" / "skills"


def copy_skill(skill_name: str, target_dir: Path) -> Path:
    """Copy a skill directory from source to target.

    Args:
        skill_name: Name of the skill directory.
        target_dir: Target .claude/skills/ directory.

    Returns:
        Path to the copied skill directory.

    Raises:
        FileNotFoundError: If the source skill directory does not exist.
    """
    source_dir = get_source_skills_dir() / skill_name
    if not source_dir.exists():
        raise FileNotFoundError(f"Skill source not found: {source_dir}")

    target_skill_dir = target_dir / skill_name
    if target_skill_dir.exists():
        shutil.rmtree(target_skill_dir)

    shutil.copytree(source_dir, target_skill_dir)
    return target_skill_dir


def copy_all_skills(target_dir: Path) -> list[Path]:
    """Copy all skills from source to target directory.

    Args:
        target_dir: Target .claude/skills/ directory.

    Returns:
        List of paths to copied skill directories.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in SKILL_NAMES:
        path = copy_skill(name, target_dir)
        copied.append(path)
    return copied


def generate_skill_rules(skill_names: list[str], rules_file: Path) -> dict:
    """Generate skill-rules.json from SKILL_METADATA.

    Builds the rules dict immutably via comprehension, then writes to disk.

    Args:
        skill_names: List of skill names to include.
        rules_file: Path to write skill-rules.json.

    Returns:
        The generated rules dictionary.
    """
    skills = [
        {
            "name": skill_name,
            "type": "suggest",
            "priority": "high",
            "description": SKILL_METADATA.get(skill_name, {}).get("description", ""),
            "keywords": SKILL_METADATA.get(skill_name, {}).get("keywords", []),
            "intentPatterns": SKILL_METADATA.get(skill_name, {}).get(
                "intent_patterns", []
            ),
            "filePaths": SKILL_METADATA.get(skill_name, {}).get("file_paths", []),
            "message": f"Consider using the `{skill_name}` skill for this task.",
        }
        for skill_name in skill_names
    ]

    rules = {
        "version": "2.0",
        "description": "Skill activation rules - auto-generated from .claude/skills/",
        "skills": skills,
        "globalSettings": {
            "enableSkillSuggestions": True,
            "maxSuggestionsPerPrompt": 2,
            "priorityOrder": ["critical", "high", "medium", "low"],
        },
    }

    rules_file.parent.mkdir(parents=True, exist_ok=True)
    with open(rules_file, "w") as f:
        json.dump(rules, f, indent=2)

    return rules
