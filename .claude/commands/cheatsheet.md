Output a quick-reference cheatsheet of all workflow stages and commands from `docs/ai-workflow.md`.

Format it as plain text with sections. Do not use agents or read any files — output the cheatsheet directly from the information below.

---

## AI Workflow Cheatsheet

### LIFECYCLE STAGES

```
 #   Stage                 Command
─────────────────────────────────────────────────────────────
 0   Requirements Review   /requirements_review <slug> <req>
 1   Test Plan             /test_plan <slug>
 2   Explore Codebase      /explore_codebase
 3   Design                /design_tests <slug> <description>
 4   Implement             /implement_tests <slug>
 5   Run Tests             /run_tests <scope>
 6   Debug                 /debug [<output>]
 7   Apply Fixes           /apply_fixes <scope>
 7   Review                /review <scope>
 8   Commit & PR           /open_pr
 9   CI Execution          /ci [<pr-number>]
10   Reporting             /reporting <scope>
11   Maintenance           /maintenance <app> <what changed>
12   Optimization          /optimization <scope>
```

---

### COMMAND REFERENCE

```
/requirements_review <slug> <requirement>
  Stage 0 — Is this testable?
  Output: thoughts/requirements/YYYY-MM-DD-<slug>.md
  Verdict: READY | NEEDS CLARIFICATION | NOT TESTABLE

/test_plan <slug>
  Stage 1 — What to test and why?
  Output: thoughts/test-plans/YYYY-MM-DD-<slug>.md
  Gate: Engineer approves scope + scenarios + priorities

/explore_codebase
  Stage 2 — What already exists?
  Output: thoughts/research/YYYY-MM-DD-<topic>.md

/design_tests <slug> <description>
  Stage 3 — Plan the page object + tests
  Output: thoughts/test-designs/YYYY-MM-DD-<slug>.md
  Gate: Engineer approves design before any code is written

/implement_tests <slug>
  Stage 4 — Write the code
  Output: pages/ and tests/
  Gate: review=APPROVED + all tests pass per phase

/run_tests <scope>
  Stage 5 — Run the suite
  Scope: app name | test file | marker | node ID
  Output: thoughts/runs/YYYY-MM-DD-<scope-slug>.txt

/debug [<output>]
  Stage 6 — Classify failures
  Output: thoughts/debug/YYYY-MM-DD-<slug>.md
  Classes: SELECTOR|TIMING|LOGIC|FIXTURE|ASSERTION|IMPORT|CONFIG|FLAKY|ENVIRONMENT

/apply_fixes <scope>
  Stage 7 — Apply diagnosed fixes + rerun
  Gate: all previously failing tests now pass

/review <scope>
  Stage 7 — Final POM/AAA/FIRST check
  Scope: app name | file | slug | (omit = git diff)
  Gate: no HIGH severity issues before /open_pr

/open_pr
  Stage 8 — Stage, commit, push, open PR
  Gate: Engineer approves commit message + PR description
  Output: PR URL

/ci [<pr-number>]
  Stage 9 — Monitor pipeline, diagnose failures
  Output: thoughts/debug/YYYY-MM-DD-ci-<slug>.md

/reporting <scope>
  Stage 10 — Summary report
  Scope: all | app name | marker
  Output: thoughts/reports/YYYY-MM-DD-<scope>.md

/maintenance <app> <what changed>
  Stage 11 — Fix broken tests after app changes
  Output: thoughts/maintenance/YYYY-MM-DD-<slug>.md

/optimization <scope>
  Stage 12 — Suite health check
  Scope: all | app name | quick
  Output: thoughts/optimization/YYYY-MM-DD-<scope>.md
```

---

### SEQUENCES

**New feature (manual):**
```
/requirements_review <slug> <req>
/test_plan <slug>
/explore_codebase
/design_tests <slug> <description>
/implement_tests <slug>
/run_tests <scope>
/debug
/apply_fixes <scope>
/review <scope>
/open_pr
/ci
/reporting <scope>
```

**New feature (autonomous):**
```
/autorun <slug> <requirement>   ← runs stages 0–6
/review <scope>
/open_pr
```

**Something broke:**
```
/run_tests <scope>
/debug
/apply_fixes <scope>
/reporting <scope>
```

**App UI changed:**
```
/maintenance <app> "<what changed>"
```

**Monthly health check:**
```
/optimization all
```

---

### QUALITY GATES

```
Requirements Review  →  verdict = READY
Test Plan            →  Engineer approves
Design               →  Engineer approves
Implement (phase)    →  review=APPROVED + tests pass
Run Tests            →  all pass (else → /debug)
Debug                →  every failure diagnosed MEDIUM|HIGH confidence
Apply Fixes          →  all previously failing tests pass
Commit & PR          →  Engineer approves message + PR description
CI                   →  all jobs pass (else → /debug with CI log)
Maintenance          →  affected tests pass after update
```

---

### AUTORUN STOPS IF

- Requirement is NOT TESTABLE
- Design fails after 2 attempts
- Phase fails review/fix after 3 cycles
- Failure confidence < MEDIUM
- Tests still fail after 2 debug/fix cycles
