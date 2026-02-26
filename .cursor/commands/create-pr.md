---
description: Create a GitHub PR from the current branch with an auto-generated description
---

1. Run `git branch --show-current` to get the current branch name. Abort if on `main`.
2. Run `git diff main...HEAD` to get all changes on this branch.
3. Run `git log main..HEAD --oneline` to get the commit history.
4. Read the PR template at `.github/pull_request_template.md`.
5. Generate a PR title following Conventional Commits (e.g., `feat: add trace viewer scripts`). Derive the type and scope from the commits/diff.
6. Generate a PR description that follows the template format exactly (What / Why / How / What's NOT included / Testing).
   - **What**: One sentence.
   - **Why**: One sentence with a link to a roadmap item or issue if obvious from the diff.
   - **How**: 2–4 bullet points on key decisions, not a line-by-line changelog.
   - **What's NOT included**: 1–2 bullets on explicit scope boundaries.
   - **Testing**: Commands to verify (e.g., `task test`, `task lint`), or note what was run.
7. Show the generated title and body to the user for review before proceeding.
8. Push the branch to origin: `git push -u origin HEAD`.
9. Generate a PR title that follow Conventional Commits
10. Create the PR: `gh pr create --title "<title>" --body "<body>"`. Use a HEREDOC for the body to preserve formatting.
11. Output the PR URL.
