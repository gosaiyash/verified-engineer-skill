# Project Instructions Template (copy into your agent's instruction file)

Use this as the starting point for `AGENTS.md`, `CLAUDE.md`, or whichever project-instruction file your agent reads. Fill in the bracketed parts for your repository. Keep it short: agents follow concise, concrete instructions better than long ones.

```markdown
# Project instructions

## Engineering workflow
Follow the `agentic-coding-engineer` skill (see [SKILL.md](agentic-coding-engineer/SKILL.md)) for
exploring, implementing, debugging, testing, reviewing, and refactoring in this repository.

## Commands
- Install dependencies: `[command]`
- Run all tests: `[command]`
- Run one test file: `[command]`
- Lint / format: `[command]`
- Type check: `[command]`
- Build: `[command]`

## Conventions
- Language/version: [e.g., Python 3.11]
- Style: [formatter, line length, naming]
- Tests live in: [path]; naming: [pattern]
- Do not edit: [generated or vendored paths]

## Rules
- Ask before adding dependencies.
- Never commit, push, or force-push unless asked.
- Never commit secrets; use environment variables.
- Report check results with PASS / FAIL / BLOCKED / NOT RUN / INCONCLUSIVE.
```
