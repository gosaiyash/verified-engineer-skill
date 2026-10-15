# Workflow: Refactor Code

## Purpose
Improve code structure while preserving observable behavior, using small verified steps.

## When to use
- "Clean up", "restructure", "extract", "rename", "reduce duplication"
- Preparing code for a later feature (as a separate, behavior-neutral step)

## Required inputs
- The refactoring goal and scope
- Access to the code, its callers, and its tests

## Preconditions
- Git state inspected; unrelated user changes identified
- Baseline test results known (green, or pre-existing failures documented)
- Public contracts identified

## Procedure
1. Confirm the goal and boundaries; list what will **not** change.
2. Find all callers and dynamic references (strings, reflection, config, docs).
3. Run existing tests to record the baseline.
4. If coverage is weak, add characterization tests capturing current behavior; verify they pass before changing code.
5. Plan the sequence of small mechanical steps.
6. Apply one step; run targeted tests; proceed only on green.
7. If a step fails, undo that step and reassess (do not stack fixes).
8. After the last step, run module tests, type check, lint, and build as relevant.
9. Review the full diff: only structural change, no accidental behavior change, no unrelated formatting.
10. Report what changed, what was preserved, and the checks run.

## Conditional decisions
- **Behavior change discovered as necessary** -> stop; split into refactor then behavior change; tell the user.
- **Public API affected** -> keep a compatibility layer or get approval; update callers.
- **No tests and cannot add any** -> report the risk; proceed only with user approval and very small steps.
- **Scope creeping** -> pause and confirm the expanded scope.

## Failure handling
- Red baseline: report before starting.
- Test failure after a step: revert your step, analyze the difference in behavior, retry smaller.
- Hidden dependency found (dynamic call, plugin): stop and report.

## Safety checks
- Preserve unrelated working-tree changes
- No destructive Git operations; no commits without authorization
- Do not edit generated or vendored files
- Keep formatting-only changes out of structural changes

## Expected output
A summary of structural changes, confirmation of behavior preservation with evidence (tests run), files changed, and limitations.

## Completion criteria
- Tests that passed before still pass; characterization tests (if added) pass
- Public behavior and contracts unchanged, or changes explicitly reported
- Diff is limited to the agreed scope
