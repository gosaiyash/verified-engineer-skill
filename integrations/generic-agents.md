# Using this skill with other agents

The skill is plain Markdown with YAML frontmatter, following the open Agent Skills convention. Whether it works in a given agent depends on that agent's support for skills or for loading Markdown instructions. This package makes **no claim** of universal compatibility.

## Path A: Agent supports Agent Skills natively

1. Find where your agent loads skills from (consult its documentation; locations differ by product).
2. Copy the entire `agentic-coding-engineer/` directory there. Keep the directory name equal to the `name` field.
3. Restart or reload the agent. Confirm the skill appears in its skill list.
4. Test with a small task, then run scenarios from `evals/behavior-tests.md`.

## Path B: Agent supports project-instruction files but not skills

1. Create the agent's project-instruction file (for example `AGENTS.md` or whatever your tool uses).
2. Paste the contents of `templates/project-instructions.md`, which points to this package.
3. Make the package files readable by the agent (commit them to the repository or place them in a known folder) and tell the agent to open `SKILL.md` first and load references on demand.

## Path C: Chat-only agent without filesystem access

1. Paste `SKILL.md` into the system prompt or first message.
2. Paste individual reference or workflow files only when needed.
3. Expect degraded behavior: the agent cannot inspect your repository or run tests, so it must ask for files and output, and should report checks as NOT RUN or BLOCKED. The skill's capability-detection section covers this.

## Checklist for adapting to a new host

- [ ] Frontmatter `name` and `description` are accepted (some hosts impose extra limits)
- [ ] Relative links from `SKILL.md` resolve (the agent can read files from the skill directory)
- [ ] The agent can read, search, and edit files in your repository (or you accept the patch-output mode)
- [ ] You know how the host handles shell permissions, and have set them deliberately
- [ ] Optional scripts run under your Python version (3.8+), or you skip them
- [ ] You have run at least a few behavior scenarios on this host and recorded the results

## Python helper scripts

`scripts/validate_skill.py` only needs a Python 3.8+ interpreter and the standard library. If your host cannot run Python, validate the package on your own machine instead. The skill itself does not call the script.
