# Workflow: Release Readiness

## Purpose
Assess whether a codebase or change set is ready to release, and report the gaps. This workflow **never publishes, tags, deploys, or pushes**; it informs a human decision.

## When to use
- "Are we ready to ship?", "pre-release check", "what's left before v2?"
- Before cutting a release candidate

## Required inputs
- The target (branch, commit range, version) and release criteria if the project defines them
- Knowledge of the project's release process (docs, CI config) when available

## Preconditions
- Read access to the repository and its release/CI documentation
- Ability to run checks, or acceptance that they will be reported as NOT RUN/BLOCKED

## Procedure
1. Identify the release target and baseline (previous tag/release) using read-only Git commands.
2. Inspect repository state: branch, clean/dirty tree, unpushed commits, in-progress merges.
3. Summarize the change set since the baseline (`git log`, diff stat); flag risky areas (migrations, public API, dependencies, security).
4. Read the project's release checklist/process if one exists; otherwise use the checklist below.
5. Run or confirm the quality gates: full tests, type check, lint, build, packaging.
6. Check versioning and metadata: version bump, changelog/release notes, license, documentation updates, migration notes.
7. Check dependencies: lockfile consistency, known-vulnerability audit if available, unpinned or new packages.
8. Check security basics: no secrets in the tree/history you can see, no debug flags, safe defaults.
9. Check compatibility: breaking changes documented, upgrade/rollback path noted.
10. Compile a readiness report with a status for each gate.

## Conditional decisions
- **A required gate cannot run** -> mark BLOCKED; the overall verdict cannot be "ready" without noting it.
- **Dirty working tree** -> report it; do not clean or commit it.
- **Failing tests** -> verdict is "not ready" unless the user explicitly accepts known failures.
- **Project has its own release checklist** -> it takes precedence; map results to it.
- **User then asks to publish/tag/deploy** -> treat as a new, explicitly authorized action; confirm the exact operation and target first.

## Failure handling
- CI results unavailable: say so; run local equivalents where possible.
- Tooling missing offline (audit, build): BLOCKED with the command for the user to run.

## Safety checks
- Do not push, tag, publish packages, deploy, or send notifications
- Do not bump versions or edit changelogs unless asked
- Do not expose secrets found during checks; redact in the report

## Expected output
A readiness report: verdict (Ready / Ready with caveats / Not ready / Cannot determine), a gate table with PASS/FAIL/BLOCKED/NOT RUN/INCONCLUSIVE, risks, blockers, and recommended next actions for a human to decide.

## Completion criteria
- Every gate has an honest status with evidence
- Blockers and caveats are explicit
- No publish/deploy/tag/push action was taken
