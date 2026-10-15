# Workflow: Test and Verify

## Purpose
Establish what is actually working by selecting, running, and honestly reporting the relevant checks, or by adding tests where coverage is missing.

## When to use
- "Run the tests", "does this work?", "add tests for X"
- After any code change, before declaring completion
- Before review or release

## Required inputs
- The change or behavior to verify
- Knowledge of (or ability to discover) the project's test, lint, type, and build commands

## Preconditions
- Ability to run commands, or acceptance that checks will be reported as NOT RUN/BLOCKED with commands for the user
- Dependencies installed, or permission to note them as missing

## Procedure
1. Identify what changed (diff) and what behavior must be proven.
2. Discover the project's real commands (manifests, task runner, CI config).
3. Choose checks by risk: smallest relevant test first, then module, then type/lint/build, then broader suites, then end-to-end/manual.
4. If coverage is missing, write tests: behavior-focused, deterministic, following the existing style; include edge and error cases.
5. For new tests, confirm they can fail (run against absent/old behavior when practical).
6. Run checks non-interactively; capture exit code and the key output; confirm tests were actually collected and executed.
7. On failure, classify: caused by your change / pre-existing / environment / flaky / test is wrong. Act accordingly.
8. Fix and rerun; do not rely on stale results.
9. Record each check's status: PASS, FAIL, BLOCKED, NOT RUN, or INCONCLUSIVE.
10. Summarize with exact commands.

## Conditional decisions
- **Test runner unknown** -> search config and CI; if still unknown, ask the user.
- **Missing dependency/tool** -> BLOCKED; state what is missing and how to install it; do not install globally without permission.
- **Zero tests collected** -> INCONCLUSIVE; investigate the selector/path.
- **Full suite too slow** -> run the targeted subset and state that the full suite was NOT RUN.
- **Baseline already red** -> report pre-existing failures separately.

## Failure handling
- Flaky results: rerun to measure; investigate nondeterminism.
- Timeouts: narrow scope; report as INCONCLUSIVE or BLOCKED with the reason.
- Environment mismatch: report versions and differences; do not "fix" by changing project config without agreement.

## Safety checks
- Do not run tests that hit production services, real payments, or destructive operations
- Use temp directories and test data; clean up what you create
- Do not modify tests to hide failures
- Keep credentials out of commands and output

## Expected output
A verification table: check -> command -> status -> notes, plus a list of unverified items and why.

## Completion criteria
- Every relevant check has an honest status
- Failures are explained or reported as outstanding
- Nothing is called PASS without a run you observed after the last change
