---
description: Create a GitHub pull request then immediately review it. Chains /pr + /pr-review in one command.
---

# PR Ship

Creates a pull request and then runs a full code review on it in one step.

## Steps

### Phase 1 — Create the PR

1. **Verify prerequisites**
   - Check `gh auth status` — abort with clear message if not authenticated
   - Confirm current branch is not `main` or `master`

2. **Gather branch context**
   - Run `git status` to check for uncommitted changes (warn if any)
   - Run `git log main...HEAD --oneline` (fall back to `master` if `main` not found)
   - Run `git diff main...HEAD --stat` to see changed files
   - Detect base branch automatically (`main` → `master` → `develop` fallback)

3. **Analyze all changes**
   - Review ALL commits in the branch (not just the latest)
   - Identify the type of change: feat / fix / refactor / docs / test / chore
   - Summarize what changed and why

4. **Push branch if needed**
   - Check if remote tracking branch exists
   - If not, push with `git push -u origin HEAD`

5. **Create the PR** using `gh pr create` with:
   - Short title (under 70 chars) following conventional commits style
   - Structured body:

```
## Summary
- <bullet: what was changed>
- <bullet: why / motivation>

## Changes
- <file or area>: <what changed>

## Test plan
- [ ] <specific thing to verify>
- [ ] All existing tests pass

## Notes
<optional: breaking changes, deployment steps>
```

6. **Capture PR number** from `gh pr create` output
   - Run `gh pr view --json number` to get the PR number reliably

---

### Phase 2 — Review the PR

Load `.claude/skills/pr-review/SKILL.md` and apply the full review workflow:

7. **Fetch the diff**
   ```bash
   gh pr diff <number>
   gh pr view <number> --json title,body,additions,deletions,changedFiles,baseRefName,headRefName
   ```

8. **Analyze across 5 dimensions** for every changed Python file:
   - **Correctness** — logic errors, None handling, edge cases
   - **Security** — hardcoded secrets, SQL injection, unsanitized input, unsafe deserialization
   - **Python best practices** — mutable defaults, bare except, missing type hints, functions >50 lines, files >800 lines
   - **Test coverage** — new functions covered? edge cases tested? external calls mocked?
   - **Code quality** — naming, duplication, deep nesting (>4 levels), commented-out code

9. **Output structured review report**

---

## Output Format

```
## PR Created

**URL**: <pr_url>
**Title**: <title>
**Branch**: `<head>` → `<base>`

---

## PR Review: <title> (#<number>)

**Changes**: +<additions> / -<deletions> across <N> files

### 🚨 Critical Issues
(Security or correctness blockers — must fix before merge)
- `path/to/file.py:42` — <issue description>

### ⚠️ Warnings
(Should fix — missing tests, non-critical bugs, best practice violations)
- `path/to/file.py:17` — <issue description>

### 💡 Suggestions
(Nice to have — style, naming, minor improvements)
- `path/to/file.py:88` — <suggestion>

### ✅ Looks Good
- <what was done well>

### Summary
| Dimension        | Status |
|------------------|--------|
| Correctness      | ✅ / ⚠️ / 🚨 |
| Security         | ✅ / ⚠️ / 🚨 |
| Python Practices | ✅ / ⚠️ / 🚨 |
| Test Coverage    | ✅ / ⚠️ / 🚨 |
| Code Quality     | ✅ / ⚠️ / 🚨 |

**Verdict**: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
```

## Example Usage

```
/pr-ship
/pr-ship "feat: add payment endpoint"
```

If an argument is provided, use it as the PR title (skip title generation).

## Rules

- NEVER force-push or modify existing commits
- NEVER push directly to `main` or `master`
- If `gh` is not installed or authenticated, show clear error and stop
- If no commits differ from base branch, abort with message
- Phase 2 (review) always runs after Phase 1 (create) — even if there are warnings
- If Critical Issues are found in the review, call them out prominently and suggest fixing before requesting reviewers