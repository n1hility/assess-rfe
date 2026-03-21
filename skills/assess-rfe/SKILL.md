---
name: assess-rfe
description: Assess an RFE against quality criteria. Pass a Jira key, URL, or raw text.
---

## Usage
```
/assess-rfe:assess-rfe RHAIRFE-1234
/assess-rfe:assess-rfe RHAIRFE-*
/assess-rfe:assess-rfe https://some-url-to-a-document
```

## Instructions

### Architecture

Each agent both **fetches** and **scores** a single issue. No separate fetcher phase.

#### Single issue (`RHAIRFE-1234`)

1. Spawn one background agent (model: opus, run_in_background: true).
2. The agent calls `mcp__atlassian__getJiraIssue` to fetch the issue, extracts title + description, scores it against the rubric below, and returns the scorer output.
3. Coordinator wraps the result with a header and presents it.

#### Bulk (`RHAIRFE-*`)

**Phase 1: Discover keys.**
- Coordinator calls `mcp__atlassian__searchJiraIssuesUsingJql` with `project = RHAIRFE ORDER BY key DESC`, `maxResults=1`, `fields=["summary"]` to get the highest key number.
- The key range is 1 to N (where N is the number from the highest key like `RHAIRFE-N`). Many keys will be missing (moved/deleted) — agents handle that gracefully.

**Phase 2: Assess with a pipeline of 20 concurrent agents.**
- Spawn agents for keys 1 through N, but never more than **20 running at once**.
- Each agent (model: opus, run_in_background: true):
  1. Calls `mcp__atlassian__getJiraIssue` with key `RHAIRFE-{n}`, cloudId `https://redhat.atlassian.net`.
  2. If the issue doesn't exist or errors, returns "SKIP" and nothing else.
  3. If the issue exists, extracts summary and description, scores against the rubric, returns the scorer output format below.
- As agents complete, the coordinator collects results and spawns new agents to keep the pipeline full at 20, until all keys are covered.
- IMPORTANT: When an agent completes, immediately launch the next pending key to keep the pipeline at 20. Do not wait for all 20 to finish before launching the next batch.

**Phase 3: Coordinator presents results.**
- Collect all non-SKIP results and produce the consolidated report with summary table.

### Agent Prompt Template

Use this exact prompt for each agent (substitute `{KEY}` with the actual key like `RHAIRFE-42`):

```
You are an RFE quality assessor. Fetch and score one Jira issue.

1. Call `mcp__atlassian__getJiraIssue` with issueIdOrKey="{KEY}", cloudId="https://redhat.atlassian.net".
2. If the issue does not exist or returns an error, respond with exactly: SKIP
3. If the issue exists, extract its summary (title) and description, then score it using the rubric below.

## Scoring Rubric

### Context
- RHAIRFE (PM-authored): describes WHAT is needed and WHY — the business need
- RHAISTRAT (engineering-authored): describes HOW — a feature that implements one or more RFEs
- RHOAIENG: epics and stories that deliver the feature
RFEs ideally map to ~1 RHAISTRAT feature.

### Criteria (0-2 each, /10 total)

1. WHAT — Clear customer need?
   Technical terms OK for precision. (0=vague/unclear, 1=ambiguous, 2=clear and specific)

2. WHY — Named customers, revenue, market data?
   - 0 = No justification, or circular reasoning, or hype-chasing with no business case
   - 1 = Generic segments, market positioning, analyst references, competitive gaps — plausible but no customer-level evidence
   - 2 = Named customer accounts, specific revenue/deal impact, or analyst ratings with demonstrated customer consequences
   Score based on the strongest evidence present. Take stated evidence at face value.

3. Open to HOW — Leaves architecture to engineering?
   Customer-facing surfaces (API endpoints, CLI flags, CRD fields, UI elements) are WHAT. Internal architecture (pipeline design, database choices, repos, language choices) is HOW.
   - 0 = Mandates implementation: specific frameworks/repos/components, or links PRDs/design docs as "the solution"
   - 1 = Leans into implementation but doesn't fully mandate
   - 2 = Describes the need without prescribing architecture; examples OK

4. Not a task — Business need, not activity?
   (0=task/chore/tech debt, 1=borderline, 2=clear business need)

5. Right-sized — Maps to ~1 strategy feature?
   (0=needs 3+ features, 1=slightly broad at 1-2, 2=focused single need)

### Smell Tests
- "Can engineering propose a different architecture?" (HOW)
- "Can you write one strategy-feature summary for this?" (Right-sized)
- "Is there a customer who asked for this?" (WHY)
- "Would this make sense filed as an engineering task?" (Not a task)

### Pass/Fail
- Pass: Total >= 7/10 AND no zeros on any criterion
- Fail: Total < 7 OR any zero (automatic fail regardless of total)

## Output Format
Return ONLY this (no preamble, no extra text):

TITLE: [issue summary]

| Criterion | Score | Notes |
|-----------|-------|-------|
| WHAT      | X/2   | ... |
| WHY       | X/2   | ... |
| Open to HOW | X/2 | ... |
| Not a task | X/2  | ... |
| Right-sized | X/2 | ... |
| **Total** | **X/10** | **PASS/FAIL** |

### Verdict
[One sentence]

### Feedback
[If fail: actionable suggestions, focus on zero-scored criteria first]
```

### Coordinator Output Format

Single issue — wrap agent output with a header:
```
## RFE Assessment: RHAIRFE-1234
[agent output]
```

Bulk — after all agents complete, produce a summary table:
```
| ID | Title | WHAT | WHY | HOW | Task | Size | Total | P/F |
```
With totals: assessed, passed, failed, pass rate.
