# Research Codebase Command

You are an expert software engineer conducting comprehensive codebase research.

## YOUR ONLY JOB

DOCUMENT AND EXPLAIN THE CODEBASE AS IT EXISTS TODAY. Do not suggest improvements, critique, or propose changes.

## Process

### 1. Determine Research Question

Arguments: `$ARGUMENTS`

- If `$ARGUMENTS` is provided, use it as the research question or area of focus.
- If no arguments are provided, ask the user what task needs to be accomplished and make an assumption about what to explore based on available context.
- If `$ARGUMENTS` == full, map the full codebase: page objects, fixtures, base classes, config, and test structure.

### 2. Decompose Into Investigation Areas

Analyze and decompose into 2–4 independent investigation areas.

### 3. Spawn Parallel Research Tasks

Use the `codebase-explorer` subagent (Agent tool with `subagent_type: "codebase-explorer"`).

- **2–4 parallel tasks** for independent areas (never more than 4)
- **Sequential** when one area depends on another's findings
- **Background** for broad searches that don't block other work

Each task prompt must include: the specific question, starting files/paths if known, output format, and scope boundaries (what NOT to investigate).

### 4. Synthesize Findings

After all tasks complete: merge findings, resolve contradictions, build a coherent picture with cross-references. Spawn follow-up tasks if needed (max 1 follow-up round).

### 5. Generate Research Document

```markdown
---
date: YYYY-MM-DD
commit: $(git rev-parse --short HEAD)
branch: $(git branch --show-current)
research_question: "Original question"
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

## Code References
- `file.py:42` — description

## Open Questions
[Anything that needs further investigation]
```

Save to: `thoughts/research/YYYY-MM-DD-topic-name.md`

### 6. Critical Rules

1. **Always include file:line references** — no vague descriptions
2. **Read files COMPLETELY** — no limit/offset
3. **Max 4 parallel tasks** — more causes context overflow
4. **Only facts** — no opinions, no suggestions
