# PR Review & Fix

Perform comprehensive code review: read all changed files, analyze code quality/security/bugs, check existing comments and CI, then fix issues.

**Key requirement:** READ ALL CHANGED FILES and review the actual code, not just existing comments.

## Complete Workflow Summary

1. **Fetch PR Information** - Determine which PR to review
2. **Fetch All PR Data** - Get code changes, comments, CI status
3. **Review Code** - Analyze code quality, security, bugs
4. **Present Review** - Show comprehensive findings
5. **Ask & Fix** - User decides: fix, comment, or approve
6. **Commit & Push** - If fixes were made
7. **Add Review Comment** - Always comment before merging (REQUIRED)
8. **Merge PR** - Squash/merge/rebase (if approved)
9. **Post-Merge Cleanup** - Switch to main, pull, delete branches (CRITICAL)

## Detailed Workflow

### 1. Fetch PR Information

**Determine which PR to review:**

```bash
# If PR number/URL provided by user, use that
# Otherwise, check current branch for associated PR
CURRENT_BRANCH=$(git branch --show-current)
gh pr view --json number,title,url,state,author 2>/dev/null
```

**Priority:**

- User-provided PR number/URL: Use that
- Current branch has PR: Use that PR
- No PR context: List recent open PRs and ask user to select

```bash
# List recent PRs if no context
gh pr list --limit 10 --json number,title,author,updatedAt
```

### 2. Fetch All PR Data & Code Changes

```bash
PR_NUMBER={determined_pr_number}
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# PR overview with commits and reviews
gh pr view $PR_NUMBER --json title,body,state,author,commits,reviews,reviewDecision,url,additions,deletions

# Inline code review comments (line-specific)
gh api repos/$REPO/pulls/$PR_NUMBER/comments

# General conversation comments
gh api repos/$REPO/issues/$PR_NUMBER/comments

# PR checks status
gh pr checks $PR_NUMBER

# Full diff
gh pr diff $PR_NUMBER

# List of changed files
gh pr view $PR_NUMBER --json files -q '.files[].path'
```

**Then read all changed files using Read tool and analyze the code.**

### 3. Review Code & Synthesize Findings

**Your code review - check for:**

- Bugs, security issues, performance problems
- Code quality, best practices, type safety
- Missing tests, poor documentation

**Parse existing comments:**

- Inline comments: path/line + body
- Conversation comments
- Review decisions (APPROVED/CHANGES_REQUESTED/COMMENTED)

**Check CI failures**

**Categorize all issues:**

- 🔴 Critical: Security, bugs, CHANGES_REQUESTED, CI failures
- 🟡 Recommended: Code quality, performance, reviewer suggestions
- 🟢 Optional: Style, docs, minor improvements

### 4. Present Review

**Show summary combining YOUR review + existing comments:**

```
🔍 COMPREHENSIVE PR REVIEW: #{PR_NUMBER} - {Title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PR Status:
  State: {OPEN/MERGED/CLOSED}
  Author: {author}
  Changes: +{additions} -{deletions} across {X} files
  Review Decision: {APPROVED/CHANGES_REQUESTED/REVIEW_REQUIRED}
  URL: {pr_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 FILES CHANGED:
  • {file1.py} (+50 -10)
  • {file2.py} (+100 -0) - New file
  • {file3.py} (+5 -5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 CRITICAL ISSUES ({count}):

  [YOUR REVIEW]
  1. [agent/ai-agent.py:30] Security: Using shell=True is dangerous
     → Allows command injection, use shlex.split() instead

  2. [eval/agent-eval.py:0] Empty file committed
     → File has no implementation, should be removed or implemented

  [EXISTING COMMENTS]
  3. [auth/jwt.py:45] @reviewer1: "JWT secret is hardcoded"

  [CI FAILURES]
  4. Tests failed: test_agent.py::test_bash_command
     → Returns non-zero exit code incorrectly

🟡 RECOMMENDED CHANGES ({count}):

  [YOUR REVIEW]
  1. [agent/ai-agent.py:125] Missing type hints for system_prompt
     → Add type annotation: system_prompt: str

  2. [agent/ai-agent.py:28] No input validation for command parameter
     → Should validate command is not empty

  [EXISTING COMMENTS]
  3. [auth/utils.py:23] @reviewer2: "Consider adding input validation"

🟢 OPTIONAL SUGGESTIONS ({count}):

  [YOUR REVIEW]
  1. [agent/ai-agent.py:1] Documentation header is good but could include usage examples

  [EXISTING COMMENTS]
  2. [agent/ai-agent.py:17] @d-gangz: "hmm looks good"

💬 GENERAL FEEDBACK ({count}):
  - @reviewer2: "Nice work overall! Just a few suggestions."
  - @d-gangz: "look not bad in general"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 CI/CD CHECKS:
  ❌ Tests (3 failed, 15 passed)
  ✅ Lint/Format
  ⚠️  Type Check (2 warnings)
  ✅ Build

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 REVIEW SUMMARY:
  Total Issues Found: {X}
  - From your code review: {Y}
  - From existing comments: {Z}
  - From CI checks: {W}

  Blocking Issues: {count} 🔴
  Requires Action: {count} 🟡
```

### 5. Ask & Fix

**Ask user:** "Fix all critical / Fix specific / Add comment / View only / Approve & merge"

**If fixing:**

1. Apply fixes using Edit tool
2. Run local checks (ruff, mypy)
3. Track what was fixed

### 6. Commit & Push (if fixes were made)

```bash
git add {files}
git commit -m "fix: address PR review feedback

Fixes:
- {issue descriptions}

git push

gh pr comment $PR_NUMBER --body "✅ Addressed review feedback
- {fixes}
```

### 7. Add Review Comment

**Always add a review comment before merging:**

```bash
# For approved PRs
gh pr comment $PR_NUMBER --body "$(cat <<'EOF'
## ✅ Code Review - APPROVED

[Summary of review findings]

### 🌟 Highlights
- [Key positive points]

### 📊 Review Stats
- Files reviewed: {X}
- Code quality: [Excellent/Good/Needs improvement]
- No blocking issues found

Ready to merge! 🚀

---
🤖 Review conducted with [Claude Code](https://claude.com/claude-code)
EOF
)"

# For PRs needing changes
gh pr comment $PR_NUMBER --body "Review feedback provided. Please address the issues listed above."
```

### 8. Merge PR (if approved)

```bash
# Merge with squash (recommended for clean history)
gh pr merge $PR_NUMBER --squash

# Alternative: merge commit (preserves all commits)
gh pr merge $PR_NUMBER --merge

# Alternative: rebase (linear history)
gh pr merge $PR_NUMBER --rebase
```

### 9. Post-Merge Cleanup

**CRITICAL: Always perform cleanup after merging:**

```bash
# 1. Switch to main branch
git checkout main

# 2. Pull latest changes
git pull origin main

# 3. Delete local feature branch
git branch -d {feature-branch-name}

# 4. Delete remote feature branch (if not auto-deleted by GitHub)
git push origin --delete {feature-branch-name}

# Optional: Clean up remote tracking references
git remote prune origin
```

**Note:** GitHub can auto-delete branches after merge if enabled in:
Repository Settings → General → Pull Requests → "Automatically delete head branches"

## Output Format Examples

### Example 1: Comprehensive Review with Code Analysis

```
🔍 COMPREHENSIVE PR REVIEW: #1 - Add AI agent with file system and bash tools
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PR Status:
  State: MERGED ✅
  Author: d-gangz
  Changes: +517 -0 across 5 files
  Review Decision: APPROVED
  URL: https://github.com/d-gangz/pydantic-ai-learn/pull/1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 FILES CHANGED:
  • agent/ai-agent.py (+178) - New agent implementation
  • eval/agent-eval.py (+0) - Empty file
  • eval/simple-eval.py (+65) - Evaluation script
  • learnings/pyai-eval-report.md (+274) - Documentation
  • learnings/pyai-learnings.md (renamed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 CRITICAL ISSUES (2):

  [YOUR REVIEW]
  1. [agent/ai-agent.py:30] Security: shell=True is dangerous
     → Command injection risk. Use shlex.split() or list format instead
     → Impact: User input could execute arbitrary commands

  2. [eval/agent-eval.py:0] Empty file committed
     → File exists but has no implementation
     → Should be removed or implemented

  [EXISTING COMMENTS]
  None marked as critical

  [CI FAILURES]
  None (no CI configured)

🟡 RECOMMENDED CHANGES (3):

  [YOUR REVIEW]
  1. [agent/ai-agent.py:17] No input validation for command parameter
     → Empty command should be rejected before subprocess.run()
     → Prevents confusing error messages

  2. [agent/ai-agent.py:165] Using result.output instead of result.data
     → PydanticAI returns result.data, not result.output
     → Will cause AttributeError at runtime

  3. [agent/ai-agent.py:1] Missing usage examples in docstring
     → Consider adding example commands in documentation header

  [EXISTING COMMENTS]
  None requesting changes

🟢 OPTIONAL SUGGESTIONS (1):

  [YOUR REVIEW]
  1. [agent/ai-agent.py:126] Consider using literal type for model parameter
     → Could use Literal["openai:gpt-4", "openai:gpt-3.5-turbo"] for type safety

  [EXISTING COMMENTS]
  2. [agent/ai-agent.py:17] @d-gangz: "hmm looks good" ✅

💬 GENERAL FEEDBACK (1):
  - @d-gangz: "look not bad in general" ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 CI/CD CHECKS:
  ⚠️  No CI/CD configured
  → Recommend: Add GitHub Actions for testing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 REVIEW SUMMARY:
  Total Issues Found: 6
  - From code review: 5 issues
  - From existing comments: 1 positive feedback
  - From CI checks: 0 (no CI)

  🔴 Blocking: 2 security/implementation issues
  🟡 Should fix: 3 quality improvements
  🟢 Optional: 1 enhancement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  NOTE: PR is already merged, but issues were found
     Would you like to create a follow-up PR to address them?

🤔 What would you like to do?
   1. Create follow-up PR to fix issues
   2. Add comment documenting known issues
   3. No action needed
```

### Example 2: Clean PR Ready to Merge

```
🔍 COMPREHENSIVE PR REVIEW: #2 - docs: add comprehensive Pydantic AI evals guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PR Status:
  State: OPEN
  Author: d-gangz
  Changes: +1316 -1 across 5 files
  Review Decision: REVIEW_REQUIRED
  URL: https://github.com/d-gangz/pydantic-ai-learn/pull/2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 FILES CHANGED:
  • .claude/commands/gh-pr-review.md (+320) - New custom command
  • agent/ai-agent.py (+3) - Added dotenv support
  • learnings/pyai-eval-guide.md (+988) - Comprehensive guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ No critical issues found!

🟢 OPTIONAL SUGGESTIONS (2):
  1. Consider adding .env.example file
  2. Add troubleshooting section to guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 CI/CD CHECKS:
  ⚠️  No CI/CD configured

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 REVIEW SUMMARY:
  Total Issues Found: 0 blocking, 2 optional
  Code quality: Excellent
  Documentation: Outstanding

  ✅ APPROVED - Ready to merge!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤔 What would you like to do?
   1. Add review comment and merge
   2. Add review comment only
   3. Merge without comment (not recommended)
```

## Usage

```bash
/gh-pr-review          # Current branch PR
/gh-pr-review 123      # PR #123
/gh-pr-review {url}    # By URL
```
