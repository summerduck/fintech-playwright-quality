# Review Tests Command

You are coordinating the final quality review of implemented E2E tests before commit.

**Core principle:** The QA Engineer makes the final call. AI surfaces issues; Engineers decide what ships.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — scope: app name, test file path, or feature slug
  - Examples: `acceptapayment`, `tests/accept_a_payment/test_card.py`, `card`
- If omitted, review all recently changed test files (use `git diff --name-only` to find them)

---

## Phase 2: Identify Files to Review

1. If a file path is given, use it directly.
2. If an app name or slug is given, find matching files under `tests/` and `pages/`.
3. If nothing given, run:

```bash
git diff --name-only HEAD
```

List the files that will be reviewed and confirm with the user before proceeding.

---

## Phase 3: Spawn Review Agent

Spawn the `review` subagent (Agent tool with `subagent_type: "review"`):

Pass:
- List of files to review
- Contents of `.claude/agent-memory-local/plan.md` (if it exists)
- Contents of `.claude/agent-memory-local/design.md` (if it exists)
- Instruction: check POM structure, AAA pattern, FIRST principles, Playwright best practices, naming conventions, Allure decorators, locator quality

Wait for the agent to complete.

---

## Phase 4: Present Review Results

Present findings to the user:

```
Review — <scope> — <date>

Status: APPROVED | CHANGES REQUIRED

Issues found: <N>
  HIGH:   <count> — must fix before commit
  MEDIUM: <count> — should fix
  LOW:    <count> — optional

<list of issues with file:line references>
```

If status is `APPROVED`:
> All checks passed. Ready to commit. Run `/open_pr` to stage and open a PR.

If status is `CHANGES REQUIRED`:
> Show the issue list and ask:
> Should I fix these issues automatically, or will you fix them manually?

---

## Phase 5: Apply Fixes (if approved by user)

If user approves automatic fixes:
1. Spawn `implement` subagent with the review issues as fix instructions.
2. Re-run the review agent on the same files.
3. If now `APPROVED` → present final summary.
4. If still `CHANGES REQUIRED` → show remaining issues and escalate to user.
