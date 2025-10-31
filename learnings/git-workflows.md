<!--
Document Type: Process Documentation
Purpose: Comprehensive Git workflow guide for solo development using multi-agent PR review process
Context: Created to document best practices for using Claude Code with a second AI agent for code review
Key Topics: Git branching, PR workflow, multi-agent collaboration, solo development with PRs
Target Use: Reference guide for consistent Git practices across projects
-->

# Git Workflows for Solo Development with Multi-Agent Review

## Overview

This document outlines the Git workflow for solo development using a **two-agent Pull Request (PR) review process**:

1. **Agent 1 (Claude Code)**: Implements features and creates PRs
2. **Agent 2 (Review Agent)**: Reviews code, fixes issues, and merges

## Why Use PRs as a Solo Developer?

### Benefits of the PR Workflow

Even when working alone, using PRs provides significant advantages:

#### 1. **Built-in Code Review**
- Creates a natural checkpoint to review changes before merging
- Allows a second AI agent to catch bugs, improvements, or issues
- Forces you to step back and look at the whole change

#### 2. **Documentation & History**
- PRs document **why** changes were made, not just **what** changed
- Easy to see what was included in each feature/fix
- Future you (or others) can understand the context

#### 3. **Better Commits**
- Encourages atomic, well-organized commits
- `/gh-commit` command helps structure commits logically
- Clean, readable git history

#### 4. **CI/CD Integration**
- Automated tests run on PRs before merging
- Catch issues before they reach main branch
- Build verification happens automatically

#### 5. **Safe Experimentation**
- Work on features in isolation (branches)
- Easy to abandon or restart if approach doesn't work
- Main branch stays stable and deployable

#### 6. **Professional Habits**
- Builds good practices for team projects
- Industry-standard workflow
- Makes collaboration easier when needed later

#### 7. **Multi-Agent Collaboration**
- One agent implements, another reviews
- Separates "creation" from "critique" mindsets
- Catches issues that the coding agent might miss

## Standard Git Workflow Components

### Branch Types

```
main/master          → Production-ready, stable code
feat/<description>   → New features
fix/<description>    → Bug fixes
docs/<description>   → Documentation updates
refactor/<description> → Code improvements without behavior change
chore/<description>  → Dependencies, tooling, config
```

### Conventional Commit Format

```
type(scope): description

Optional body explaining why this change was made.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `perf`, `chore`, `ci`

**Examples:**
```
feat(auth): add JWT authentication
fix(validation): handle empty response arrays
docs(README): update installation instructions
test(api): add integration tests for user endpoints
```

## Multi-Agent PR Workflow (Recommended)

### Phase 1: Implementation (Agent 1 - Claude Code)

#### Step 1.1: Start Clean
```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main
```

#### Step 1.2: Implement Feature
```bash
# Make code changes, implement features
# Agent makes multiple edits, writes tests, etc.
```

#### Step 1.3: Commit Changes
```bash
# Use the /gh-commit slash command
/gh-commit

# This automatically:
# - Creates feature branch if on main
# - Organizes changes into logical commits
# - Follows conventional commit format
# - Adds Claude Code attribution
```

**What `/gh-commit` does:**
- Analyzes all changes
- Groups related files together
- Creates separate commits for:
  - Core implementation (feat/fix)
  - Tests (test)
  - Documentation (docs)
  - Refactoring (refactor)
  - Dependencies (chore)
- Uses proper commit message format

#### Step 1.4: Create Pull Request
```bash
# Push branch to remote
git push -u origin <branch-name>

# Create PR with description
gh pr create --title "Add user authentication" --body "$(cat <<'EOF'
## Summary
- Implement JWT authentication
- Add login/logout endpoints
- Include token refresh mechanism

## Test plan
- [x] Unit tests for auth functions
- [x] Integration tests for endpoints
- [x] Manual testing with Postman

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**PR Creation Result:**
- Shows all commits from your branch
- Displays combined diff of all changes
- Provides link to view on GitHub

### Phase 2: Review & Fix (Agent 2 - Review Agent)

#### Step 2.1: Checkout the PR Branch
```bash
# Get PR number from previous step (e.g., PR #123)
gh pr checkout 123

# This automatically:
# - Fetches the remote branch
# - Checks out the branch locally
# - Sets up tracking
```

#### Step 2.2: Review the Code
```bash
# View PR details
gh pr view 123

# See the diff
gh pr diff 123

# Or review in browser
gh pr view 123 --web
```

**Review Agent checks for:**
- Code quality and best practices
- Error handling
- Edge cases
- Type safety
- Test coverage
- Documentation completeness
- Performance issues
- Security concerns

#### Step 2.3: Make Fixes (if needed)
```bash
# Edit files based on review findings
# Agent makes improvements...

# Commit the fixes
git add <fixed-files>
git commit -m "fix: address review findings

- Improved error handling in auth.py
- Added missing type hints
- Updated tests for edge cases
"

# Push to same branch
git push

# ✨ PR automatically updates with new commits!
```

**Key Point:** Pushing to the same branch automatically updates the PR. No need to create a new PR!

#### Step 2.4: Document Review (Optional but Recommended)
```bash
# Leave a comment documenting what was reviewed/fixed
gh pr review 123 --comment --body "
## Review Complete

### Fixes Applied
- Added comprehensive error handling
- Improved type hints throughout
- Added edge case tests
- Updated docstrings

### Verified
- All tests passing ✅
- No linting errors ✅
- Documentation updated ✅

Ready to merge.
"
```

### Phase 3: Merge

#### Step 3.1: Verify PR is Ready
```bash
# Check PR status
gh pr view 123

# Verify CI/CD checks pass
gh pr checks 123
```

#### Step 3.2: Merge the PR
```bash
# Merge (no approval needed for solo projects)
gh pr merge 123

# Options:
# --merge     (creates merge commit - default)
# --squash    (squashes all commits into one)
# --rebase    (rebases commits onto main)
```

**Merge Strategy Recommendations:**
- `--merge`: Keep full commit history (good for documentation)
- `--squash`: Clean history, one commit per feature (simpler)
- `--rebase`: Linear history (advanced, can be complex)

#### Step 3.3: Cleanup
```bash
# Switch back to main
git checkout main

# Pull the merged changes
git pull origin main

# Delete the feature branch locally
git branch -d <branch-name>

# Delete remote branch (if not auto-deleted)
git push origin --delete <branch-name>
```

## Quick Reference Commands

### Branch Management
```bash
# Check current branch
git branch --show-current

# List all branches
git branch -a

# Create new branch
git checkout -b feat/feature-name

# Switch branches
git checkout branch-name

# Delete local branch
git branch -d branch-name
```

### Viewing Changes
```bash
# See uncommitted changes
git status
git diff

# See commit history
git log --oneline
git log main..HEAD  # Commits on current branch not in main

# Compare branches
git diff main...HEAD --stat
```

### PR Management
```bash
# List PRs
gh pr list

# View specific PR
gh pr view 123

# Check out PR locally
gh pr checkout 123

# View PR diff
gh pr diff 123

# View in browser
gh pr view 123 --web

# Check CI/CD status
gh pr checks 123
```

### Commit Management
```bash
# View recent commits
git log --oneline -10

# View files changed in last commit
git show --name-only

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Amend last commit (only if not pushed!)
git commit --amend
```

## Common Scenarios

### Scenario 1: Simple Feature Implementation

```bash
# Agent 1: Implement
/gh-commit "Add user profile feature"
gh pr create --title "Add user profiles" --body "..."

# Agent 2: Review
gh pr checkout 123
# Review code, make fixes if needed
git commit -am "fix: review improvements"
git push

# Merge
gh pr merge 123
```

### Scenario 2: Multiple Fixes After Review

```bash
# Agent 2 finds several issues
gh pr checkout 123

# Fix issue 1
git add file1.py
git commit -m "fix: improve error handling"
git push

# Fix issue 2
git add file2.py
git commit -m "fix: add type hints"
git push

# Fix issue 3
git add file3.py test_file3.py
git commit -m "test: add edge case tests"
git push

# All commits appear in the same PR automatically!
# Then merge
gh pr merge 123
```

### Scenario 3: Large Refactoring

```bash
# Agent 1: Use /gh-commit for organized commits
/gh-commit

# Creates multiple commits:
# - refactor(core): extract helper functions
# - refactor(core): simplify validation logic
# - test(core): update tests for refactored code
# - docs(core): update docstrings

gh pr create --title "Refactor core validation" --body "..."

# Agent 2: Review all commits together in the PR
gh pr checkout 123
# Verify refactoring didn't break anything
# Make any necessary adjustments
gh pr merge 123 --squash  # Squash into single commit
```

### Scenario 4: Abandoned Feature

```bash
# Started feature but decided not to continue
git checkout main  # Switch back to main

# Delete the feature branch
git branch -D feat/abandoned-feature

# If already pushed, delete remote too
git push origin --delete feat/abandoned-feature

# If PR exists, close it
gh pr close 123
```

## Tips & Best Practices

### 1. Commit Often, Push When Ready
- Make small, logical commits as you work
- Push to remote when you want to create/update PR
- Don't worry about "perfect" commits initially - `/gh-commit` organizes them

### 2. Use Descriptive Branch Names
- ✅ `feat/add-user-authentication`
- ✅ `fix/login-validation-error`
- ❌ `feature1`
- ❌ `my-changes`

### 3. Write Meaningful PR Descriptions
Include:
- What changed
- Why it changed
- How to test
- Any breaking changes

### 4. Keep PRs Focused
- One feature/fix per PR
- Easier to review
- Easier to revert if needed
- Cleaner history

### 5. Review Your Own Code First
Before handing to review agent:
- Read through the diff
- Check for debug code, console.logs, commented code
- Verify tests pass
- Run linter

### 6. Keep Main Branch Stable
- Never commit directly to main
- Always use feature branches
- Merge only after review
- Main should always be deployable

### 7. Clean Up Merged Branches
- Delete branches after merging
- Keeps branch list manageable
- Prevents confusion about active work

### 8. Use PR Templates (Optional)
Create `.github/pull_request_template.md`:
```markdown
## Summary
<!-- Brief description of changes -->

## Changes
-
-

## Test Plan
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Documentation updated

## Checklist
- [ ] Code follows project style
- [ ] Tests pass
- [ ] No new warnings
- [ ] Breaking changes documented
```

## Troubleshooting

### PR Not Updating After Push
```bash
# Verify you're on the correct branch
git branch --show-current

# Verify you pushed to the right remote
git remote -v
git push origin <branch-name>
```

### Can't Merge PR
```bash
# Check for merge conflicts
gh pr view 123

# If conflicts, update from main
git checkout <branch-name>
git pull origin main
# Resolve conflicts
git add .
git commit -m "fix: resolve merge conflicts"
git push
```

### Lost Track of Changes
```bash
# See all changes in current branch vs main
git diff main...HEAD

# See all commits in current branch
git log main..HEAD --oneline
```

### Accidentally Committed to Main
```bash
# Move the commit to a new branch
git branch feat/new-branch  # Creates branch with current commits
git reset --hard origin/main  # Resets main to match remote
git checkout feat/new-branch  # Switch to new branch
```

## Summary

**Your Multi-Agent Workflow:**

1. **Claude Code** → Implement → `/gh-commit` → Create PR
2. **Review Agent** → Checkout PR → Review → Fix → Push (PR updates)
3. **Merge** → `gh pr merge` (no approval needed)
4. **Cleanup** → Delete branch, back to main

**Key Benefits:**
- Organized, professional commit history
- Built-in code review by second agent
- Documentation of all changes
- Safe, isolated feature development
- Easy to revert if needed
- Good habits for future collaboration

**Remember:**
- Commits = checkpoints (small, frequent)
- Branches = isolation (one per feature)
- PRs = review + documentation (before merging to main)
- Main = always stable and deployable
