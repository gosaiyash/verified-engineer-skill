# Workflow: Implement Feature

## Purpose
Deliver a new behavior or change as the smallest coherent, tested, verified modification that follows project conventions.

## When to use
- "Add X", "support Y", "change Z to do W"
- Enhancements that touch one or more files and need tests

## Required inputs
- The requested behavior and any constraints
- Acceptance criteria (or enough information to derive them)
- Repository access with write permission (otherwise produce patches)

## Preconditions
- You understand the requirement; ambiguities that change the design are resolved or assumptions stated
- Git state inspected; unrelated user changes identified and left alone
- You know how to run the project's tests (or know that you cannot)

## Procedure
1. Clarify the goal, scope, and acceptance criteria. Ask only questions whose answers change the design.
2. Investigate: relevant modules, similar existing features, interfaces, callers, tests, conventions (see `explore-repository.md` for depth).
3. For non-trivial work, write a short plan (problem, approach, files, edge cases, test strategy, risks, rollback). For trivial work, skip it.
4. Break the work into small, verifiable steps; track them in a checklist.
5. Implement one step at a time, matching existing style and patterns.
6. Handle expected errors and edge cases; validate at trust boundaries.
7. Add or update tests alongside the code (happy path, edges, errors).
8. After each step, run the narrowest relevant check; fix issues before moving on.
9. Run broader checks (module tests, type check, lint, build) proportional to risk.
10. Review your own diff: unrelated changes, leftover debug code, missing docs/types, secrets.
11. Produce the final report per `references/completion-report.md`.

## Conditional decisions
- **A similar feature exists** -> extend its pattern rather than inventing a new one.
- **New dependency seems needed** -> look for a standard-library/existing alternative first; if still needed, surface it to the user before adding.
- **Public API/schema change** -> find and update all callers, add migration/compat notes, tell the user.
- **Requirement is bigger than expected** -> pause, report, and propose splitting.
- **Cannot run tests** -> still write tests; mark checks NOT RUN/BLOCKED and give exact commands.
- **No write access** -> output complete patches or file contents with paths.

## Failure handling
- Test failures: analyze per `references/testing-and-verification.md`; do not weaken tests to pass.
- Repeated failure (2-3 attempts): stop, re-read the evidence, reconsider the approach, and tell the user if still blocked.
- Discover a pre-existing bug: report it; fix only if it blocks the task or the user agrees.

## Safety checks
- No destructive commands, no commits/pushes without authorization
- No secrets in code, logs, or tests
- Do not touch generated/vendored files by hand
- Preserve unrelated working-tree changes

## Expected output
Working code plus tests, and a report listing the summary, files changed, key decisions, exact checks with statuses, limitations, and remaining work.

## Completion criteria
- Acceptance criteria met and verified, or clearly marked unverified with reasons
- Diff contains only intended changes
- Relevant tests/lint/type/build checks run and honestly reported
