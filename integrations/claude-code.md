# Using this skill with Claude Code

This document is **optional and platform-specific**. The core skill (`SKILL.md` and its references and workflows) does not depend on it. Verify details against the current Claude Code documentation, because features, paths, and settings change between versions.

## Installing

Claude Code loads Agent Skills from skill directories. Typical locations (confirm in the official documentation for your version):

- **Personal (all projects):** a `skills/` folder inside your Claude configuration directory, e.g. `~/.claude/skills/agentic-coding-engineer/`
- **Project (shared with a team):** `.claude/skills/agentic-coding-engineer/` inside the repository

Copy the whole `agentic-coding-engineer/` directory (it must contain `SKILL.md`). The directory name must match the `name` in the frontmatter. After copying, start a new session (or reload skills if your version supports it) and check that the skill is listed.

## Invoking

Skills are normally selected automatically from their `description`. You can also ask explicitly, for example: "Use the agentic-coding-engineer skill to fix this bug." Some versions let you invoke skills by name with a slash command; check `/help` in your session.

## Mapping skill concepts to Claude Code features

| Skill concept | Typical Claude Code feature |
|---|---|
| Read / search / edit files | Built-in file, search, and edit tools |
| Run tests, linters, builds, Git | Shell command tool (subject to your permission settings) |
| Task checklist | The built-in to-do/task list, if enabled |
| Project conventions | `CLAUDE.md` in the repo or user config (see `templates/project-instructions.md`) |
| Parallel investigation | Subagents, if your version supports them |
| Plan-then-implement | Plan mode, if available - keeps work read-only until you approve |
| Hard security limits | Permission rules, allow/deny lists, and sandbox settings - **not** this skill |

## Recommended setup

1. Put project-specific commands (test, lint, build) and conventions in `CLAUDE.md` so the skill does not have to rediscover them each session.
2. Keep permission prompts on for destructive shell commands, Git pushes, and network access. The skill tells the agent to ask first, but only the platform's permission system can enforce it.
3. Use plan mode (or an equivalent read-only mode) for reviews, audits, and release-readiness checks.
4. Optionally restrict tools with the `allowed-tools` frontmatter field if your version supports it. The field is experimental and its behavior varies across hosts, so it is deliberately **not** set in this package.

## Limitations

- Skill discovery depends on the `description`. If the skill does not trigger, name it explicitly in your request.
- Subagents and slash commands are optional extras, not required by the skill.
- Instructions guide behavior; they are not enforcement.
