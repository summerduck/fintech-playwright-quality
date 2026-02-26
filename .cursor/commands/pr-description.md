---
description: Generate a PR description from the current branch diff
---

1. Run `git diff main...HEAD` to get all changes on this branch.
2. Run `git log main..HEAD --oneline` to get the commit history.
3. Read the PR template at `.github/pull_request_template.md`.
4. Generate a PR description that follows the template format exactly (What / Why / How / What's NOT included / Testing).
5. Keep it short and human-readable:
   - **What**: One sentence.
   - **Why**: One sentence with a link to a roadmap item or issue if obvious from the diff.
   - **How**: 2–4 bullet points on key decisions, not a line-by-line changelog.
   - **What's NOT included**: 1–2 bullets on explicit scope boundaries.
   - **Testing**: Commands to verify (e.g., `task test`, `task lint`), or note what was run.
6. Output ONLY the markdown body — no fences, no extra commentary.
