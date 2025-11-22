#!/usr/bin/env python3
"""
Skill Activation Hook for Claude Code (Python Implementation)

This hook analyzes user prompts and file context to automatically suggest
relevant skills based on keywords, intent patterns, and file paths.

Input: JSON from stdin with session metadata and user prompt
Output: Formatted suggestion to use relevant skills
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class SkillMatch:
    """Represents a matched skill with its metadata"""
    name: str
    type: str
    priority: str
    message: str
    matched_by: List[str]


def load_skill_rules(project_root: Path) -> Dict[str, Any]:
    """Load skill rules from skill-rules.json"""
    rules_path = project_root / ".claude" / "skills" / "skill-rules.json"

    if not rules_path.exists():
        return {"skills": []}

    with open(rules_path, "r") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """Normalize text for matching (lowercase, strip whitespace)"""
    return text.lower().strip()


def match_keywords(prompt: str, keywords: List[str]) -> List[str]:
    """Check if any keywords are present in the prompt"""
    normalized_prompt = normalize_text(prompt)
    matched = []

    for keyword in keywords:
        if normalize_text(keyword) in normalized_prompt:
            matched.append(keyword)

    return matched


def match_intent_patterns(prompt: str, patterns: List[str]) -> List[str]:
    """Check if prompt matches any intent patterns (regex)"""
    matched = []

    for pattern in patterns:
        try:
            if re.search(pattern, prompt, re.IGNORECASE):
                matched.append(pattern)
        except re.error:
            # Skip invalid regex patterns
            continue

    return matched


def match_file_paths(active_file: str, file_patterns: List[str]) -> List[str]:
    """Check if active file matches any file path patterns"""
    if not active_file:
        return []

    matched = []
    active_path = Path(active_file)

    for pattern in file_patterns:
        # Convert glob pattern to regex
        try:
            if active_path.match(pattern):
                matched.append(pattern)
        except Exception:
            continue

    return matched


def analyze_prompt(
    prompt: str,
    active_file: str,
    skills: List[Dict[str, Any]]
) -> List[SkillMatch]:
    """Analyze prompt and return matching skills"""
    matches = []

    for skill in skills:
        matched_by = []

        # Check keywords
        keyword_matches = match_keywords(
            prompt,
            skill.get("keywords", [])
        )
        if keyword_matches:
            matched_by.extend([f"keyword:{k}" for k in keyword_matches])

        # Check intent patterns
        pattern_matches = match_intent_patterns(
            prompt,
            skill.get("intentPatterns", [])
        )
        if pattern_matches:
            matched_by.extend([f"pattern:{p}" for p in pattern_matches])

        # Check file paths
        file_matches = match_file_paths(
            active_file,
            skill.get("filePaths", [])
        )
        if file_matches:
            matched_by.extend([f"file:{f}" for f in file_matches])

        # If any matches found, add to results
        if matched_by:
            matches.append(SkillMatch(
                name=skill["name"],
                type=skill.get("type", "suggest"),
                priority=skill.get("priority", "medium"),
                message=skill.get("message", f"Consider using /{skill['name']}"),
                matched_by=matched_by
            ))

    return matches


def format_output(matches: List[SkillMatch]) -> str:
    """Format matched skills for display"""
    if not matches:
        return ""

    # Group by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    matches_sorted = sorted(
        matches,
        key=lambda m: priority_order.get(m.priority, 99)
    )

    # Separate blocking vs suggesting skills
    blocking = [m for m in matches_sorted if m.type == "block"]
    suggesting = [m for m in matches_sorted if m.type != "block"]

    output_lines = []

    # Handle blocking skills first
    if blocking:
        output_lines.append("\n🛑 BLOCKED - Required Skill Activation\n")
        for match in blocking:
            output_lines.append(match.message)
            output_lines.append(f"\nUse the Skill tool to invoke `/{match.name}` before proceeding.\n")
        return "\n".join(output_lines)

    # Suggest relevant skills
    if suggesting:
        output_lines.append("\n💡 Relevant Skills Detected\n")

        for match in suggesting[:2]:  # Limit to top 2 suggestions
            output_lines.append(match.message)

        output_lines.append(
            f"\nUse the Skill tool to invoke these skills (e.g., `/{suggesting[0].name}`)."
        )

    return "\n".join(output_lines)


def main():
    """Main entry point for the hook"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Extract relevant data
        prompt = input_data.get("prompt", "")
        active_file = input_data.get("activeFile", "")
        project_root = Path(input_data.get("projectRoot", "."))

        # Load skill rules
        rules = load_skill_rules(project_root)
        skills = rules.get("skills", [])

        # Analyze prompt and find matches
        matches = analyze_prompt(prompt, active_file, skills)

        # Format and output results
        output = format_output(matches)

        if output:
            print(output)
            sys.exit(0)

        # No matches, exit silently
        sys.exit(0)

    except Exception as e:
        # Log error but don't block the user
        print(f"⚠️ Skill activation hook error: {str(e)}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
