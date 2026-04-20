# Tasks: Title Quality Scoring

**Input**: Design documents from `specs/001-title-quality-scoring/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Not requested. Manual validation via `/assess-rfe` against sample RFEs.

**Organization**: Tasks are grouped by user story. US1 is the MVP; US2 and US3 depend on US1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: User Story 1 - Scorer agent assesses title quality (Priority: P1) MVP

**Goal**: Add Title Quality criterion to the rubric so scorer agents produce a title score in every assessment.

**Independent Test**: Run `/assess-rfe RHAIRFE-XXXX` against a single RFE. Verify the result file contains a `Title Quality *(advisory)*` row with a 0-2 score, rationale, and that the Total remains X/10.

### Implementation for User Story 1

- [x] T001 [US1] Add Title Quality criterion definition (item 6) after Right-sized in scripts/agent_prompt.md
- [x] T002 [US1] Add Title Quality scoring levels (0, 1, 2) with definitions in scripts/agent_prompt.md
- [x] T003 [US1] Add reference to HOW criterion's technology exception for titles in scripts/agent_prompt.md
- [x] T004 [US1] Add Title Quality calibration examples (8+ examples covering 0, 1, 2 scores including platform-vocabulary borderline cases) in scripts/agent_prompt.md
- [x] T005 [US1] Add title smell tests to the Smell Tests section in scripts/agent_prompt.md
- [x] T006 [US1] Add `Title Quality *(advisory)*` row to output format between Right-sized and Total in scripts/agent_prompt.md

**Checkpoint**: Scorer agents now produce title quality scores. Total remains X/10, pass/fail unaffected.

---

## Phase 2: User Story 2 - Title length warning (Priority: P2)

**Goal**: Add length-based warnings and score caps to the title quality criterion.

**Independent Test**: Assess an RFE with a title over 160 characters. Verify the title score is capped at 1 and the warning is present. Assess an RFE with a 90-character title and verify the warning appears but the score is content-based.

**Depends on**: US1 (criterion must exist before adding length rules)

### Implementation for User Story 2

- [x] T007 [US2] Add length handling rules to the Title Quality criterion: 80-char warning, 150-char score cap at 1 in scripts/agent_prompt.md
- [x] T008 [US2] Add length-related calibration example (title over 150 chars capped at 1) in scripts/agent_prompt.md

**Checkpoint**: Title scoring now includes length awareness. Titles over 150 chars are capped at 1.

---

## Phase 3: User Story 3 - CSV and summary include title quality (Priority: P3)

**Goal**: Parser extracts title quality into CSV; summary script reports title quality statistics.

**Independent Test**: Run `parse_results.py` on a run directory with result files that include Title Quality rows. Verify `Title_Quality` column appears in CSV. Run `summarize_run.py` and verify title quality stats appear. Also test with a result file missing the Title Quality row (backward compat).

**Depends on**: US1 (result files must contain title quality rows to parse)

### Implementation for User Story 3

- [x] T009 [P] [US3] Add title quality extraction logic to `extract_scores()` in scripts/parse_results.py: match `"title"` keyword in criterion cell, store as `title_quality`, return in scores dict (empty string if not found)
- [x] T010 [P] [US3] Add `Title_Quality` to CSV fieldnames (after `Size`, before `Total`) in scripts/parse_results.py
- [x] T011 [US3] Handle `Title_Quality` column in `load_scores()` in scripts/summarize_run.py: convert to int if present, None if missing
- [x] T012 [US3] Add "Title Quality (Advisory)" statistics section after Criteria Averages in `summarize()` in scripts/summarize_run.py: distribution (0/1/2 counts), average score

**Checkpoint**: Bulk assessment pipeline fully supports title quality from scoring through CSV to summary.

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 1)**: No dependencies, start immediately. This is the MVP.
- **US2 (Phase 2)**: Depends on US1 (same file, extends the criterion)
- **US3 (Phase 3)**: Depends on US1 (needs result files with title scores to parse). Independent of US2.

### Within Each User Story

- US1: T001-T006 are sequential (same file, building up the criterion incrementally)
- US2: T007-T008 are sequential (same file, extending the criterion)
- US3: T009+T010 can run in parallel (different functions in parse_results.py), then T011+T012 sequential (summarize_run.py)

### Parallel Opportunities

- US2 and US3 can run in parallel after US1 is complete (different files)
- Within US3: T009 and T010 can run in parallel (different functions in same file)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: US1 (T001-T006) in scripts/agent_prompt.md
2. **STOP and VALIDATE**: Run `/assess-rfe` against a sample RFE, verify title quality row appears
3. Title scoring is live, even without CSV/summary support

### Incremental Delivery

1. US1 complete -> scorer agents produce title scores (MVP)
2. US2 complete -> length warnings and caps active
3. US3 complete -> bulk pipeline fully supports title quality

### Parallel Strategy

After US1 completes:
- Agent A: US2 (scripts/agent_prompt.md length rules)
- Agent B: US3 (scripts/parse_results.py + scripts/summarize_run.py)

---

## Notes

- All US1 and US2 tasks modify the same file (scripts/agent_prompt.md), so they must be sequential
- US3 modifies two different files (parse_results.py, summarize_run.py) so has some parallelism
- No setup or foundational phase needed; this feature modifies existing files only
- Commit after each user story for clean rollback points
