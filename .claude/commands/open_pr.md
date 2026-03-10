# Commit & PR Command

You are coordinating the commit and pull request stage.

**Core principle:** Nothing is committed or pushed without the QA Engineer's explicit approval of both the commit message and the PR description.

---

## Phase 1: Check Working State

Run:

```bash
git status
git diff --stat HEAD
```

If there are no staged or unstaged changes:
> Nothing to commit. All changes are already committed.

List the changed files and confirm with the user:
> These files will be staged and committed:
> - <file list>
> Proceed?

Wait for confirmation.

---

## Phase 2: Propose Commit Message

1. Read the changed files to understand what was added or modified.
2. Check recent commit history for style:

```bash
git log --oneline -10
```

3. Draft a commit message following the repository's style.

Present to the user:

```
Proposed commit message:

<type>: <short summary>

<optional body with what changed and why>
```

Ask:
> Approve this message, or provide your own?

Wait for approval or edited message. Use exactly what the user approves.

---

## Phase 3: Stage and Commit

Stage the relevant files (prefer specific paths over `git add .`):

```bash
git add <file1> <file2> ...
```

Commit using the approved message:

```bash
git commit -m "$(cat <<'EOF'
<approved message>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

If the commit fails due to a pre-commit hook:
- Show the hook output to the user
- Do NOT use `--no-verify`
- Fix the reported issue and re-attempt

---

## Phase 4: Propose PR Description

Draft a pull request title and body based on the committed changes.

Present to the user:

```
Proposed PR:

Title: <short title under 70 characters>

Body:
## Summary
- <bullet points>

## Test plan
- [ ] <what to verify>
```

Ask:
> Approve this PR description, or provide your own?

Wait for approval or edited description. Use exactly what the user approves.

---

## Phase 5: Push and Open PR

Push the branch:

```bash
git push -u origin HEAD
```

Create the PR using the approved title and body:

```bash
gh pr create --title "<approved title>" --body "$(cat <<'EOF'
<approved body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL to the user.
