# Systematic Debugging

Use this for any bug, crash, wrong output, performance regression, or failing/flaky test.

## Contents
- Principles
- Step 1: Capture the problem
- Step 2: Reproduce and baseline
- Step 3: Trace the failure
- Step 4: Hypotheses
- Step 5: Test hypotheses
- Step 6: Root cause
- Step 7: Fix and regression test
- Step 8: Verify and check side effects
- Reading stack traces
- Special cases
- Anti-patterns
- Reporting

## Principles

1. **Reproduce first.** A bug you cannot reproduce is a bug you cannot confirm fixed.
2. **Change one thing at a time** and observe.
3. **Evidence beats intuition.** Every claim about cause should point to something you observed.
4. **Fix causes, not symptoms.** Suppressing an exception or special-casing an input is not a fix.
5. **Know when to step back.** After two or three failed attempts, re-read the evidence and revise your mental model.

## Step 1: Capture the problem

Record: expected behavior, actual behavior, exact error text/stack trace/logs, inputs, environment (versions, OS, config), frequency (always/intermittent), and when it started (recent change?). If any of this is missing and obtainable, get it (run the code, read logs) or ask the user.

## Step 2: Reproduce and baseline

- Produce the smallest command/test/input that triggers the failure.
- Run the relevant existing tests to establish a **baseline**: which pass, which already fail. Pre-existing failures must not be blamed on, or silently fixed with, your change.
- If you cannot run code, say so, and reason from the supplied trace and code; label conclusions as unreproduced.

## Step 3: Trace the failure

Follow the path from the symptom backward: failing line -> its inputs -> where those values came from -> where an assumption first breaks. Read the actual code on the path; do not guess what a function does from its name.

## Step 4: Hypotheses

List 2-4 plausible causes, ranked by likelihood and by cheapness to test. Include "environment/config/data" and "recent change" candidates. Write what observation would **confirm** or **refute** each.

## Step 5: Test hypotheses

Use the cheapest decisive experiment: a targeted print/log, a debugger, an assertion, a minimal repro script, a focused unit test, `git bisect` / diff of recent changes (read-only inspection first). Remove temporary instrumentation afterwards.

## Step 6: Root cause

State the root cause with its evidence, or say explicitly "most likely cause (unconfirmed)". Explain *why* the failing input triggers it and *why* it was not caught earlier.

## Step 7: Fix and regression test

- Apply the smallest change that removes the cause.
- Add a regression test that **fails without the fix and passes with it** where practical. If you can, demonstrate the failing state first.
- If a test is impractical (e.g., needs infrastructure), describe the manual verification instead.
- Look for the same defect pattern elsewhere (search similar call sites) and report - but do not silently expand scope.

## Step 8: Verify and check side effects

Rerun: the repro, the new regression test, the surrounding test file/module, then broader checks proportional to risk. Compare against the baseline. Inspect your diff for unintended behavior changes.

## Reading stack traces

- Find the **first frame in project code** nearest the top of the failure; library frames show where it surfaced, project frames show what you did wrong.
- For chained exceptions ("caused by"), the **deepest cause** usually matters most.
- Note types, values, and line numbers; verify the line in the *current* file version (it may have changed).
- For async/concurrent traces, identify which task/thread/request the failure belongs to.

## Special cases

| Case | Approach |
|---|---|
| Flaky test | Run repeatedly to measure rate; look for time, ordering, shared state, randomness, concurrency, network; make it deterministic rather than adding retries or sleeps |
| Works locally, fails in CI | Diff environments: versions, env vars, OS, locale/timezone, filesystem case-sensitivity, test ordering, parallelism |
| Performance issue | Measure first (profile/timing), find the hotspot, change one thing, re-measure |
| Dependency/build failure | Read the first error, not the last; check versions and lockfile; avoid blanket upgrades |
| Intermittent data bug | Log inputs at the boundary; look for races and stale caches |
| No reproduction possible | State that; add logging/assertions the user can run; do not claim a fix |

## Anti-patterns

- Editing several things at once
- Wrapping failing code in broad try/except
- Deleting or loosening the failing test
- "Fixing" by retrying/sleeping
- Declaring victory after a single green run of a flaky test
- Claiming a cause you did not test

## Reporting

Report: symptom, reproduction, root cause (confirmed/unconfirmed + evidence), fix, regression test, checks run with statuses, remaining uncertainty.
