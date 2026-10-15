# Planning and Implementation

Use this when turning a request into working, verified code.

## Contents
- Requirement analysis
- Acceptance criteria
- Choosing an approach
- Decomposition
- Plan template
- Implementation discipline
- Handling ambiguity
- Documentation changes
- Definition of done

## Requirement analysis

Extract from the request:
- **Goal** - what outcome the user wants.
- **Scope** - what is in and explicitly out.
- **Constraints** - language/version, compatibility, performance, style, deadlines, no-new-dependency rules.
- **Interfaces** - public APIs, CLI flags, schemas, file formats that must stay stable.

If the request is underspecified, check the repository for answers first (existing patterns, tests, docs). Ask the user only when the answer changes the design and is not discoverable.

## Acceptance criteria

Write criteria that are **observable and testable**:
- Given/when/then, or input -> expected output pairs
- Error and edge behavior (empty, null, huge, malformed, concurrent, unicode, timezone, permission denied)
- Non-functional limits when stated (latency, memory)
- Backward compatibility expectations

Criteria you cannot verify in this environment must be flagged up front as "unverifiable here" so the final report can say so.

## Choosing an approach

1. Look for an existing pattern in the repo that solves a similar problem. Prefer extending it.
2. Consider at least one alternative; note why you rejected it (one line is enough).
3. Prefer the approach with the smaller blast radius and easier rollback.
4. Prefer standard library / existing dependencies. A new dependency needs a reason you can state in one sentence and the user's awareness.

## Decomposition

Split work into steps that each:
- change one concern,
- can be verified independently (a test, a type-check, a manual check),
- leaves the codebase in a working state where practical.

Order steps so risky or uncertain parts come first (spike, then build).

## Plan template

```
Problem:           <one or two sentences>
Requirements:      <bullets>
Acceptance:        <testable bullets>
Relevant files:    <paths and why>
Approach:          <short description>; rejected: <alternative and why>
Edge cases:        <list>
Compatibility:     <APIs, data, versions, dependencies>
Test strategy:     <what tests to add/run, smallest first>
Risks:             <list>
Recovery:          <how to undo>
Steps:             1) ... 2) ... 3) ...
```

Scale it: a small change may need three lines; a migration needs the whole template.

## Implementation discipline

- One logical change at a time; keep diffs reviewable.
- Match surrounding style exactly (naming, imports ordering, error handling, logging, typing).
- Validate inputs at trust boundaries; fail with clear, actionable errors; never swallow exceptions silently.
- Avoid magic numbers; reuse constants/config conventions already present.
- Keep functions focused; avoid premature abstraction (rule of three).
- Do not leave debugging output, commented-out code, TODOs you introduced without telling the user, or unused imports.
- Update docs/comments/types that your change makes stale.
- Backward compatibility: if you change a public signature, schema, or file format, find and update all callers or provide a migration path - and tell the user.
- After each step, run the narrowest relevant check.

## Handling ambiguity

| Situation | Action |
|---|---|
| Missing detail that does not affect design | State assumption, proceed |
| Missing detail that changes design | Ask one concise question with a recommended default |
| Conflicting requirements | Point out the conflict, propose a resolution, wait if the choice is consequential |
| Request seems to require something harmful or risky | Explain the concern, offer a safer alternative |

## Documentation changes

When asked to document: read the code first; document actual behavior (verified), not intended behavior; include examples you have confirmed run; keep to the repo's doc style and location.

## Definition of done

- Acceptance criteria met **and verified** (or explicitly marked unverified)
- Tests added/updated and run
- No unrelated changes in the diff
- Lint/type/build checks relevant to the change run
- Diff self-reviewed
- Final report written truthfully
