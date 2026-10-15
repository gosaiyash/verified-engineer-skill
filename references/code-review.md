# Code Review

Use this when reviewing a diff, a pull request, a file, or your own changes.

## Contents
- Ground rules
- What to review for
- How to review
- Severity scale
- Finding format
- Verified vs hypothetical
- Security concerns in review
- Review output structure
- What not to do

## Ground rules

- **Review-only means read-only.** Do not edit files unless the user authorizes fixes.
- Review the **actual change** (diff plus surrounding code), not a mental model of it.
- Judge against the stated intent and the project's conventions, not personal style.
- Prioritize what can break users or data over cosmetic points.

## What to review for

1. **Correctness** - does it do what it claims; off-by-one, null/None, wrong operator, wrong units, time zones.
2. **Regressions** - callers, contracts, behavior other code depends on.
3. **Input validation** - trust boundaries, bounds, types, encoding.
4. **Error handling** - swallowed errors, wrong exception types, lost context, partial failure, cleanup/rollback.
5. **Security** - see `security-review.md`.
6. **Performance** - accidental O(n^2), N+1 queries, unbounded memory, blocking calls on hot paths.
7. **API and schema compatibility** - breaking changes, migrations, serialization formats.
8. **Concurrency and state** - races, shared mutable state, transactions, idempotency, ordering.
9. **Test quality** - do tests exercise the change, fail when behavior is wrong, avoid over-mocking.
10. **Maintainability** - clarity, duplication, naming, dead code, stale docs/comments.

## How to review

1. Read the description/request to learn the intent.
2. Skim the full diff for shape (files touched, size, unrelated changes).
3. Read each changed hunk with its surrounding function and callers.
4. For risky hunks, trace inputs and outputs and look for the failing input.
5. Check tests: added, changed, missing.
6. If you can run checks safely, do - and report results with statuses. Otherwise say they were not run.
7. Write findings, ordered by severity.

## Severity scale

| Severity | Meaning |
|---|---|
| **Critical** | Data loss, security breach, crash in normal use, or broken core feature; block merge |
| **High** | Likely bug or regression under realistic conditions; should fix before merge |
| **Medium** | Real defect or risk under less common conditions; fix soon |
| **Low** | Minor correctness/robustness/maintainability issue |
| **Nit** | Optional style or preference; keep to a minimum |

## Finding format

For each actionable finding give:
- **Severity** and a short title
- **Location** - `path/file.ext:line`
- **Trigger** - the conditions/input that expose it
- **Impact** - what goes wrong, for whom
- **Evidence** - what you read or ran that shows it
- **Recommendation** - a concrete fix (code sketch if helpful)

## Verified vs hypothetical

Label each finding **Verified** (you reproduced it or can demonstrate it from the code with a concrete failing input) or **Hypothetical** (plausible but not confirmed; say what would confirm it). Do not present guesses as defects.

## Security concerns in review

Flag injection, authz gaps, secrets, unsafe deserialization, path traversal, SSRF, weak crypto, and sensitive-data exposure when the change touches them. Defer detail to `security-review.md`.

## Review output structure

1. **Verdict** - approve / approve with comments / changes requested, and one-line reason
2. **Findings** - highest severity first
3. **Positive notes** - only if genuinely useful
4. **Checks run** - with PASS/FAIL/BLOCKED/NOT RUN/INCONCLUSIVE
5. **Not reviewed / limitations**

## What not to do

- Rewrite the author's approach out of preference
- Bury critical issues among nits
- Claim something is a bug without a trigger
- Apply fixes during a review-only request
