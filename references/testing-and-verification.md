# Testing and Verification

Use this when choosing, writing, running, or interpreting tests and other checks, and when deciding what you may claim as verified.

## Contents
- Types of verification
- Discovering commands
- Selecting and ordering checks
- Writing good tests
- Running and interpreting
- Failure analysis
- Flaky and environment problems
- Status vocabulary
- Honest reporting rules

## Types of verification

| Type | Purpose |
|---|---|
| Unit test | One function/class in isolation |
| Integration test | Components working together (DB, filesystem, services) |
| End-to-end test | Whole user flow through the real interface |
| Regression test | Reproduces a past bug so it cannot return |
| Type check | Static type consistency |
| Lint / format | Style and common-defect rules |
| Build / compile | The project builds and packages |
| Manual check | A human-style run of the feature, with observed output |

## Discovering commands

Find the real commands in manifests (`scripts`, `tool.*` sections), `Makefile`/task runners, `tox`/`nox`, CI workflow steps, and contributor docs. Use the project's runner and flags. Do not install a different test framework. If commands are unknown and cannot be found, ask - or state what you tried.

## Selecting and ordering checks

1. **Smallest relevant first**: the single new/changed test, then its file.
2. Then the module/package suite.
3. Then type check, lint, and build if the change touches typed/linted/built code.
4. Then the broader or full suite when risk warrants (shared code, public API, config, dependencies).
5. End-to-end/manual checks for user-facing behavior when feasible.

Stop early on the first unexpected failure to analyze it, rather than running everything repeatedly.

## Writing good tests

- Test **behavior**, not implementation details.
- One reason to fail per test; descriptive names stating the scenario and expectation.
- Cover: happy path, boundaries, empty/null, invalid input, error paths, and the specific bug for regressions.
- Deterministic: control time, randomness, network, filesystem (temp dirs), and ordering.
- Independent: no reliance on other tests' state.
- Fast: prefer unit-level coverage; mock only true external boundaries.
- Follow the existing test layout, fixtures, and naming.
- A new test must be shown to **fail when the behavior is absent** whenever practical (otherwise it may prove nothing).

## Running and interpreting

- Run non-interactively; capture exit code and the relevant output.
- Read the failure message and the first failing assertion, not just the summary line.
- Confirm the run actually executed your tests (count, names) - a suite that collected zero tests is **not** a pass.
- Rerun after every change that could affect the result; earlier results are stale.

## Failure analysis

Classify each failure: (a) caused by your change, (b) pre-existing (confirm via baseline or `git stash`-free means such as running on a clean checkout/worktree if available - never by discarding user changes), (c) environment/dependency, (d) flaky, (e) test itself wrong. Fix (a) and (e) as appropriate; report (b), (c), (d) without hiding them.

## Flaky and environment problems

Repeat runs to measure; isolate shared state; check ordering/time/network. Missing tools or dependencies -> mark **BLOCKED**, state what is missing, and give the user the command to run. Do not install system-wide packages or modify the environment without permission.

## Status vocabulary

Report each check using exactly one of:

- **PASS** - ran and succeeded
- **FAIL** - ran and failed
- **BLOCKED** - could not run (say why)
- **NOT RUN** - not attempted (say why)
- **INCONCLUSIVE** - ran but did not establish the requirement (e.g., zero tests collected, test did not exercise the change, output ambiguous)

## Honest reporting rules

1. Written is not run. Run is not passed. Passed earlier is not passed now.
2. Never claim coverage you did not measure.
3. Never edit a test to hide a real failure; if a test is wrong, explain why and get agreement when non-obvious.
4. Report pre-existing failures separately from failures you caused.
5. List what remains unverified and why.
6. Include the exact commands so the user can reproduce your results.
