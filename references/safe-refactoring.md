# Safe Refactoring

Use this when changing code structure without changing observable behavior.

## Contents
- Definition and scope
- Pre-flight checks
- Characterization tests
- Incremental technique
- Common refactorings and their risks
- Verification after each step
- When behavior must change
- Stop conditions

## Definition and scope

A refactor changes **structure**, not **behavior**. Confirm the user's goal (readability, duplication, testability, performance, module boundaries). Keep scope to what was asked; do not rename or reorganize the world.

## Pre-flight checks

1. Inspect Git state; know which changes are not yours.
2. Find all **callers**, importers, and dynamic uses (reflection, string-based lookups, config references, serialization, templates, docs).
3. Identify the **contracts**: public signatures, return types, exceptions, side effects, logging, ordering, performance characteristics others rely on.
4. Find the existing tests and run them to establish a green **baseline**. If the baseline is red, tell the user before starting.
5. Check for generated code, vendored code, or files owned by others.

## Characterization tests

If coverage of the area is thin, write tests that capture **current** behavior (even odd behavior) before refactoring. Run them against the unmodified code to prove they pass. These tests are your safety net; keep them focused and deterministic.

## Incremental technique

- One mechanical step at a time: extract function, inline, rename, move, split, replace conditional, introduce parameter object.
- Run targeted tests after **each** step. If red, revert **that step** (undo your own edit), do not push forward.
- Keep each step small enough that a failure is obviously attributable.
- Separate commits/steps for mechanical moves versus logic edits.
- Do not mix formatting-only changes with structural changes.
- Prefer the language/IDE-safe rename approach (search all references) over blind text replace.

## Common refactorings and their risks

| Refactoring | Hidden risk to check |
|---|---|
| Rename | string references, reflection, serialization keys, public API, docs |
| Extract function | variables captured/mutated, early returns, exceptions, `this/self` |
| Move module | import cycles, relative paths, packaging, entry points |
| Replace conditional/loop | short-circuit order, off-by-one, empty cases, laziness |
| Remove "dead" code | dynamic callers, plugins, public API, config-driven use |
| Change data structure | ordering, mutability/aliasing, equality semantics, performance |
| Dedupe | subtle differences between "similar" copies |

## Verification after each step

Run: the targeted tests, then module tests, then type check/lint/build as relevant. At the end, review the full diff to confirm it contains **only** structural changes. Compare public API surface before/after when feasible.

## When behavior must change

Stop and split the work: first the behavior-preserving refactor (verified), then the behavior change as its own step with its own tests. Tell the user which is which.

## Stop conditions

Pause and report if: baseline tests are red, callers cannot be found reliably, the area has no tests and you cannot write characterization tests, or the refactor keeps expanding beyond the requested scope.
