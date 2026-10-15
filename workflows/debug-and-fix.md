# Workflow: Debug and Fix

## Purpose
Find the root cause of a defect with evidence, fix it narrowly, and prove the fix with a regression test and verification.

## When to use
- Errors, crashes, wrong output, failing or flaky tests, performance regressions
- "Why does this fail?" or "fix this bug"

## Required inputs
- Description of expected vs actual behavior
- Exact error output, logs, or reproduction steps (obtain them if missing)
- Access to run the code, or supplied traces and files

## Preconditions
- Git state inspected so your changes are distinguishable from the user's
- You know how to run the failing case, or you have stated that you cannot

## Procedure
1. Record expected vs actual behavior and the exact error.
2. Reproduce with the smallest command, test, or input. Note the result.
3. Establish a baseline: run the relevant existing tests; record pre-existing failures.
4. Trace the failure from the symptom back through the code path, reading the actual code.
5. List 2-4 ranked hypotheses and the observation that would confirm or refute each.
6. Test hypotheses one at a time using the cheapest decisive experiment (log, assertion, debugger, minimal repro, targeted test, recent-change inspection).
7. Identify the root cause; label it **confirmed** or **unconfirmed** with evidence.
8. Implement the smallest fix addressing the cause.
9. Add a regression test that fails before the fix and passes after, where practical.
10. Remove temporary instrumentation.
11. Rerun: the repro, the regression test, the surrounding tests, then broader checks by risk.
12. Compare with the baseline; inspect the diff for side effects; search for the same pattern elsewhere and report (do not silently widen scope).
13. Report evidence, fix, checks, and remaining uncertainty.

## Conditional decisions
- **Cannot reproduce** -> say so; add diagnostics or request more data; do not claim a fix.
- **Flaky** -> measure frequency; find the nondeterminism; do not add sleeps/retries as the fix.
- **Cause is outside the codebase (dependency, environment, data)** -> report with evidence and propose a workaround; avoid editing vendored code.
- **Fix requires a behavior/API change** -> confirm with the user first.
- **Multiple independent bugs** -> separate them; fix one at a time.
- **Two or three failed fixes** -> stop, re-read evidence, rebuild the hypothesis list.

## Failure handling
- Regression test passes without the fix -> it is not testing the bug; rewrite it.
- New failures after the fix -> compare with baseline; revert your own change if needed and reassess.
- Tools unavailable -> mark checks BLOCKED and provide exact commands.

## Safety checks
- Never silence errors with broad try/except as a "fix"
- Never delete or loosen the failing test to get green
- Never discard user changes to "get a clean state"
- Redact secrets that appear in logs

## Expected output
A report with: symptom, reproduction, root cause (confirmed/unconfirmed + evidence), the fix, the regression test, checks with statuses, and remaining uncertainty.

## Completion criteria
- The original failure no longer occurs (verified), or the report states it could not be verified
- A regression test exists or its absence is justified
- No unexplained new failures versus baseline
- Root cause claims match the evidence
