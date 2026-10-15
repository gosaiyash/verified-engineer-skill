# Completion Report

Use this to close out any substantial task. The goal: give the user an accurate, scannable account of what changed and what was actually verified.

## Contents
- Principles
- Standard structure
- Check status vocabulary
- Scaling the report
- Examples
- Reporting blockers and failures
- Anti-patterns

## Principles

1. **Truth over polish.** Report only what you did and observed.
2. **Evidence attached.** Name the exact commands and their outcomes.
3. **Failures first-class.** Failing, blocked, and skipped checks are reported as prominently as passes.
4. **Brief by default.** Detail scales with task complexity and risk.

## Standard structure

1. **Summary** - what was done and why, in one to three sentences.
2. **Files changed** - path and one-line description each.
3. **Key decisions** - design choices, assumptions, alternatives rejected, anything the user may want to veto (new dependency, API change).
4. **Checks executed** - command -> status (PASS / FAIL / BLOCKED / NOT RUN / INCONCLUSIVE), with a note for anything not PASS.
5. **Known limitations** - what is unverified or incomplete, and why.
6. **Remaining work / next steps** - only real follow-ups, including failures that persist.

## Check status vocabulary

- **PASS** - executed and succeeded
- **FAIL** - executed and failed
- **BLOCKED** - could not run; give the reason
- **NOT RUN** - not attempted; give the reason
- **INCONCLUSIVE** - ran but did not establish the requirement

Never use PASS for: tests merely written, commands merely started, results from before the final edit, or a suite that ran zero relevant tests.

## Scaling the report

| Task size | Report |
|---|---|
| Trivial (typo, one-liner) | One or two sentences naming the change and the check run |
| Small (single bug/feature) | Summary, files, checks, limitations |
| Large (multi-file, risky, migration) | Full structure, plus rollback notes and a verification matrix against acceptance criteria |

## Examples

Small:

> Fixed the off-by-one in `paginate()` (`src/pager.py:42`) that dropped the last item. Added `test_last_page_includes_final_item` in `tests/test_pager.py`.
> Checks: `pytest tests/test_pager.py` -> PASS (6 passed; new test failed before the fix). Full suite not run.

Large (abbreviated):

> **Summary:** Added rate limiting to the login endpoint (5 attempts/min/IP).
> **Files:** `auth/limiter.py` (new), `auth/routes.py` (apply limiter), `tests/test_limiter.py` (new).
> **Decisions:** In-memory store (no new dependency); resets on restart - flagging this as a limitation.
> **Checks:** `pytest tests/test_limiter.py` -> PASS; `pytest` (full) -> FAIL (2 pre-existing failures in `test_export.py`, unrelated; same on baseline); `ruff check` -> PASS; integration test against real Redis -> NOT RUN (not used).
> **Limitations:** Not safe across multiple server processes. **Next:** shared store if you scale horizontally.

## Reporting blockers and failures

State: what failed or could not run, the exact error (trimmed), what you tried, and what is needed to proceed (a permission, a dependency, user input). Offer the exact command for the user to run when you could not.

## Anti-patterns

- "All tests pass" without having run them
- Hiding pre-existing failures or lumping them with your own
- Vague claims ("should work", "looks good") standing in for evidence
- Listing intended features as completed
- Omitting that you changed or skipped something unexpected
