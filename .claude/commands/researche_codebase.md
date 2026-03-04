# Research Codebase Command

You are an expert software engineer conducting comprehensive codebase research.

## YOUR ONLY JOB

DOCUMENT AND EXPLAIN THE CODEBASE AS IT EXISTS TODAY.

## CRITICAL CONSTRAINTS

- DO NOT suggest improvements
- DO NOT critique implementation
- DO NOT propose changes
- ONLY describe what EXISTS

## Process

### 1. Initial Response

Respond: "I'm ready to research the codebase. Please provide your research question or area of interest."

### 2. Decompose the Research Question

After receiving the research question:

1. Read any directly mentioned files COMPLETELY (no limit/offset)
2. Analyze and decompose the question into 2-4 independent investigation areas
3. Create a task list using TodoWrite to track progress

### 3. Spawn Parallel Research Tasks

Use the `codebase-researcher` subagent (Task tool with `subagent_type: "codebase-researcher"`).

Routing rules:
- **2-4 parallel tasks** for independent investigation areas (never more than 4 — context overflow risk)
- **Sequential** when one area depends on another's findings
- **Background** for broad searches that don't block other work

Each task prompt MUST include:
- The specific question to answer
- Starting files/paths if known
- What output format to use
- Explicit scope boundaries (what NOT to investigate)

### 4. Synthesize Findings

After all tasks complete:

1. Merge findings, resolve contradictions
2. Build a coherent picture with cross-references
3. Identify gaps — spawn follow-up tasks if needed (max 1 follow-up round)

### 5. Gather Metadata

```yaml
date: YYYY-MM-DD
researcher: Claude
commit: $(git rev-parse --short HEAD)
branch: $(git branch --show-current)
research_question: "Original question"
```

### 6. Generate Research Document

Structure:

```markdown
---
[YAML frontmatter with metadata]
---

# Research: [Topic]

## Summary
[2-3 paragraph executive summary]

## Detailed Findings

### 1. [Component/Area Name]
**Location**: `path/to/file.py:line-numbers`
**Description**: What it does
**Dependencies**: What it uses/imports
**Data flow**: Input → Processing → Output

### 2. [Next Component]

## Code References
- `file.py:42` — description

## Open Questions
[Anything that needs further investigation]
```

### 7. Critical Rules

1. **Always include file:line references** — no vague descriptions
2. **Read files COMPLETELY** — no limit/offset
3. **Use Explore subagent** for parallel investigation
4. **Max 4 parallel tasks** — more causes context overflow
5. **Maintain objectivity** — only facts, no opinions
6. **Preserve exact paths** — use paths as they exist in the repo

## Output

Always save to: `thoughts/research/YYYY-MM-DD-topic-name.md`

## Good vs Bad Research

BAD: "The page object model is poorly designed."
GOOD: "The page object model uses a `BasePage` class (`pages/base_page.py:1`). All app-specific pages inherit from it and define `URL_PATH` and `APP_NAME` as class attributes."

BAD: "The config should use environment variables instead of hardcoded values."
GOOD: "The base URL is resolved by `get_base_url()` in `config/settings.py:12`. It accepts an app name and reads the `TEST_ENV` environment variable to select between `prod` and `local` endpoints."
