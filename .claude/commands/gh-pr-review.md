# PR Review & Fix

Perform comprehensive code review: read all changed files, analyze code quality/security/bugs, check existing comments and CI, then fix issues.

**Key requirement:** READ ALL CHANGED FILES and review the actual code, not just existing comments.

## Workflow

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

**Ask user:** "Fix all critical / Fix specific / Add comment / View only"

**If fixing:**

1. Apply fixes using Edit tool
2. Run local checks (ruff, mypy)
3. Track what was fixed

### 6. Commit & Push

```bash
git add {files}
git commit -m "fix: address PR review feedback

Fixes:
- {issue descriptions}

git push

gh pr comment $PR_NUMBER --body "✅ Addressed review feedback
- {fixes}
```

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
   [User can select from options]
```

### Example 2: No Issues Found

```
🔍 Analyzing PR #45: Update documentation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PR Status:
  State: OPEN
  Review: APPROVED ✅

📋 Comments: 3 comments (all positive feedback)

💬 Recent Comments:
  - @reviewer1: "LGTM! Nice documentation improvements."
  - @reviewer2: "Approved. Clear and concise."
  - @reviewer3: "Thanks for updating this!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ No action items found!

This PR is approved and ready to merge.
Would you like to merge it now? [Yes/No]
```

## Usage

```bash
/gh-pr-review          # Current branch PR
/gh-pr-review 123      # PR #123
/gh-pr-review {url}    # By URL
```
