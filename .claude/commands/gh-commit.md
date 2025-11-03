# Smart Commit + PR Command

You are a commit specialist that creates well-organized, logical commits following conventional commit standards.

## Workflow

### 1. Safety & Branch Check

```bash
git branch --show-current
```

**If on main/master:**

🛑 **STOP IMMEDIATELY - DO NOT PROCEED WITH COMMITS**

**Never commit directly to main/master under any circumstances.**

Required actions:
1. Ask user: "What feature/fix are you working on?"
2. Create feature branch: `git checkout -b {type}/{description}` (e.g., `feat/add-yaml-support`, `docs/tracing-learnings`)
3. Confirm branch switch: `git branch --show-current`
4. **ONLY proceed to step 2 after confirming you are on a feature branch**

**If on feature branch:**

✅ Proceed to step 2

**Check for changes:**

```bash
git status --porcelain
git diff --stat
```

**If no uncommitted changes:**

- Check if there are unpushed commits: `git log origin/main..HEAD`
- If yes: Skip to step 5 (Push & PR Workflow) with existing commits
- If no: Inform user there's nothing to commit

### 2. Analyze & Batch Changes

**Read user's request** to understand purpose (feature, fix, refactor, docs, etc.)

**Categorize changes** by type and scope:

- **feat/fix**: Core implementation, main logic
- **test**: Test files, test updates
- **docs**: README, docstrings, documentation
- **refactor**: Code cleanup without behavior change
- **chore**: Dependencies, build config, tooling

**Batching rules:**

- Keep related changes together
- Separate concerns (don't mix unrelated code)
- Each commit should be atomic
- If test depends on implementation, commit together

### 3. Create Commits

For each batch:

**Add files by group:**

```bash
git add file1.py file2.py file3.py
```

- ✅ Add files for this batch only
- ❌ Never `git add .`

**Commit with conventional format:**

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Optional body explaining why this change was made.
EOF
)"
```

**Types:** feat, fix, docs, test, refactor, style, perf, chore, ci

**Scope examples:** anthropic, openai, validation, streaming, cli, docs

**Description rules:**

- Imperative mood: "add feature" not "added feature"
- Concise but descriptive
- No ending period
- Simple, clear language

### 4. Summary & Next Steps

```bash
# Show commits created
git log main..HEAD --oneline

# Show diff summary
git diff main...HEAD --stat
```

**Report:**

- List commits created
- Explain batching rationale

### 5. Push & PR Workflow

After creating commits, check PR status and offer next steps:

```bash
# Check if PR exists for this branch
gh pr view --json number,title,url 2>/dev/null

# Check if branch is pushed
git rev-parse --verify origin/$(git branch --show-current) 2>/dev/null
```

**Decision tree:**

**If NO commits were created (no changes):**

- Stop, inform user there's nothing to commit

**If commits were created:**

**Ask user using AskUserQuestion tool:**

- Question: "Ready to push and create/update PR?"
- Options: "Yes, push and create/update PR" or "No, keep commits local"

**If user selects "Yes":**

1. **Check if PR already exists:**

   ```bash
   PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null)
   ```

   **If PR exists:**

   - Push commits: `git push`
   - Add comment to PR with new commits summary:

     ```bash
     gh pr comment $PR_NUMBER --body "$(cat <<'EOF'
     📝 Updates pushed

     New commits:
     - commit message 1
     - commit message 2

     Ready for re-review!
     EOF
     )"
     ```

   - Report: "Pushed to existing PR #123"

   **If NO PR exists:**

   - Push branch: `git push -u origin $(git branch --show-current)`
   - Generate PR title and description from commits
   - Create PR:

     ```bash
     gh pr create --title "{generated-title}" --body "$(cat <<'EOF'
     ## Summary
     {bullet points of what was added/changed}

     ## Commits
     {list all commits}

     ## Test Plan
     - [ ] {relevant test items}
     EOF
     )"
     ```

   - Report: "Created PR #123: {url}"

**If user selects "No":**

- Stop, inform user commits are ready locally
- Suggest: "Run /gh-commit again when ready to push"

**PR Title Generation Rules:**

- If all commits same type: Use that type with combined scope
  - Example: `feat(agents): add simple agent implementation and tests`
- If mixed types: Use overall feature description
  - Example: `Add pydantic AI learning examples`

**PR Description Generation:**

```markdown
## Summary

- {High-level bullet points of changes}

## Commits

- {List all commits in this PR}

## Test Plan

- [ ] {Relevant test items based on changes}
```

## Commit Message Examples

```
feat(anthropic): add support for Claude 3.5 Sonnet

Implements client wrapper with streaming and function calling.
```

```
fix(validation): handle empty response arrays

Previously crashed on empty arrays. Now returns empty list.
```

```
test(gemini): add validation tests for JSON mode
```

```
docs(README): update installation instructions

Add UV installation method and Python 3.9+ requirement.
```

## PR Description Example

```markdown
## Summary

- Added MD_YAML mode for YAML extraction from markdown
- Implemented comprehensive test suite for YAML parsing
- Updated documentation with usage examples and API reference

## Commits

- feat(yaml): add MD_YAML mode for YAML extraction
- feat(yaml): implement YAML parser with validation
- test(yaml): add tests for MD_YAML mode
- test(yaml): add edge case tests for malformed YAML
- docs(yaml): document MD_YAML usage
- docs(yaml): add API reference for YAML functions

## Test Plan

- [x] Run all existing tests
- [x] Test YAML extraction with various markdown formats
- [x] Verify error handling for invalid YAML
- [ ] Manual testing with real-world examples
```

## Special Cases

**Multiple features:** Ask if separate commits or together

**Breaking changes:** Add `BREAKING CHANGE:` in body or use `feat!:`

**Large refactoring:** Ask user for batching preferences

**Pre-commit hooks fail:** Show output, ask if fixes should be in same or separate commit

## Project Awareness

Check before committing:

```bash
git log --oneline -10  # Follow existing patterns
```

Read if exists: `CLAUDE.md`, `CONTRIBUTING.md`, `.gitmessage`

## Output Format

```
🔍 Analyzing changes...

Branch: feat/add-yaml-support
Changed: 8 files

📦 Batches:
  1. Core (3 files) - feat(yaml)
  2. Tests (3 files) - test(yaml)
  3. Docs (2 files) - docs(yaml)

✅ Creating commits...

📝 feat(yaml): add MD_YAML mode for YAML extraction
   Files: instructor/mode.py, instructor/client_openai.py, instructor/yaml_handler.py
   ✓ abc123f

📝 test(yaml): add tests for MD_YAML mode
   Files: tests/test_yaml.py, tests/fixtures/yaml_samples.py
   ✓ def456a

📝 docs(yaml): document MD_YAML usage
   Files: README.md, docs/concepts/yaml-mode.md
   ✓ ghi789b

✨ Summary: 3 commits, 8 files changed

📦 Ready to push and create PR?
   [Prompt user with AskUserQuestion]

# If user selects "Yes" and NO PR exists:
🚀 Pushing branch...
✅ Pushed to origin/feat/add-yaml-support

📝 Creating PR...
✅ Created PR #42: https://github.com/user/repo/pull/42
   Title: "feat(yaml): add MD_YAML mode for YAML extraction and tests"

# If user selects "Yes" and PR exists:
🚀 Pushing commits...
✅ Pushed to origin/feat/add-yaml-support

💬 Added comment to PR #42
✅ PR updated: https://github.com/user/repo/pull/42

# If user selects "No":
✅ Commits ready locally. Run /gh-commit again when ready to push.
```

## Usage

```bash
/commit-pr                    # Analyze, commit and create PR
/commit-pr "description"      # Use description to inform messages
```
