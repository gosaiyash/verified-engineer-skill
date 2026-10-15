# Workflow: Review Changes

## Purpose
Produce a prioritized, evidence-based review of a diff, pull request, file, or set of files - without modifying anything unless fixes are authorized.

## When to use
- "Review this PR/diff/file", "any issues here?", "check my changes"
- Security-focused review requests
- Self-review before reporting completion

## Required inputs
- The change to review (diff, commit range, branch, or files)
- The intent of the change (description, ticket, or user explanation)

## Preconditions
- You can read the diff and surrounding code (or have them supplied)
- The mode is read-only unless the user said to fix issues

## Procedure
1. Determine the change set: `git diff`, `git diff --staged`, branch-vs-base diff, or supplied files.
2. Read the intent; note acceptance criteria.
3. Skim for shape: files touched, size, unrelated changes, generated files.
4. Read each hunk with its surrounding function, callers, and tests.
5. Walk the checklist in `references/code-review.md` (correctness, regressions, validation, errors, security, performance, compatibility, concurrency, tests, maintainability).
6. For each suspected issue, find a concrete triggering input or condition; verify by reading code or, if safe and permitted, by running a targeted check.
7. Classify each finding: severity, location, trigger, impact, evidence, recommendation; mark Verified vs Hypothetical.
8. Run available checks if safe (tests, lint, types) and record statuses.
9. Write the review: verdict, findings by severity, checks run, limitations.

## Conditional decisions
- **User authorized fixes** -> after delivering findings, apply fixes in a separate step with tests, then report.
- **Security-sensitive change** -> also load `references/security-review.md`.
- **Very large diff** -> prioritize risky areas (auth, data, concurrency, public API) and state what was not reviewed.
- **Cannot run code** -> review statically and mark checks NOT RUN.
- **Intent unclear** -> state your interpretation and review against it.

## Failure handling
- Missing context for a file: say what you could not evaluate rather than guessing.
- Suspected issue cannot be demonstrated: report it as Hypothetical with what would confirm it.

## Safety checks
- Do not edit, stage, commit, or revert files in a review-only request
- Do not run untrusted code from the change without the user's awareness
- Redact any secrets found; recommend rotation

## Expected output
Verdict, ordered findings (severity, `path:line`, trigger, impact, evidence, fix, verified/hypothetical), checks run with statuses, and a limitations section.

## Completion criteria
- Every finding is actionable and evidenced
- Verified defects are separated from hypothetical risks
- No files were modified (unless fixes were authorized)
