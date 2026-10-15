# verified-engineer-skill

A portable **Agent Skill** that makes an AI coding agent work like a careful senior engineer: explore the repo, plan, implement, debug, test, review, refactor, use Git safely, check security, and **report only what was actually verified**.

> **Core idea:** code that "looks right" is not done. Done means you ran the checks, saw the results, and told the truth about anything you could not verify.

The skill is plain Markdown with YAML frontmatter (the open Agent Skills format), so it is not tied to one vendor, model, IDE, or operating system.

---

## What it does

| Mode | What the agent does |
|---|---|
| **Explore / Explain** | Maps the repo, finds conventions and commands, answers with `file:line` evidence |
| **Plan** | Requirements, acceptance criteria, approach, risks, rollback |
| **Implement** | Smallest coherent change, follows project style, adds tests |
| **Debug** | Reproduce, hypothesize, test with evidence, fix the root cause, add a regression test |
| **Test** | Finds the project's real commands, runs smallest checks first |
| **Review** | Prioritized findings with severity, location, trigger, impact, evidence (read-only) |
| **Refactor** | Behavior-preserving, small verified steps, characterization tests |
| **Git** | Inspects before acting; never discards your changes or force-pushes without being asked |
| **Security audit** | Trust boundaries, injection, authz, secrets, unsafe file operations |
| **Release readiness** | Gate-by-gate readiness report; never publishes, tags, or deploys |

Every check is reported with exactly one status:

`PASS` ran and succeeded | `FAIL` ran and failed | `BLOCKED` could not run | `NOT RUN` not attempted | `INCONCLUSIVE` ran but proved nothing

---

## Install

Installation differs by agent. The skill is a **folder**: copy the whole `verified-engineer/` directory, not just `SKILL.md`, because `SKILL.md` links to the reference and workflow files.

The folder name must match the `name` field in the `SKILL.md` frontmatter.

### Claude Code

```bash
# All projects
cp -R skills/verified-engineer ~/.claude/skills/

# One project
mkdir -p .claude/skills && cp -R skills/verified-engineer .claude/skills/
```

Start a new session, then ask: *"Use the verified-engineer skill to fix this bug."*

### Google Antigravity

```bash
# One project
mkdir -p .agent/skills && cp -R skills/verified-engineer .agent/skills/

# All projects
mkdir -p ~/.gemini/antigravity/skills && cp -R skills/verified-engineer ~/.gemini/antigravity/skills/
```

### Other agents

- **Supports Agent Skills:** copy the folder to wherever that agent loads skills from.
- **Supports only an instruction file** (for example `AGENTS.md`): paste the snippet from `templates/project-instructions.md` and keep the folder readable by the agent.
- **Chat only, no filesystem:** paste `SKILL.md` into the first message. Expect reduced capability; the skill tells the agent to ask for files and to mark checks `NOT RUN`.

Skill locations and settings change between tool versions. Check your agent's current documentation if the skill is not discovered. See `skills/verified-engineer/integrations/` for more detail.

---

## Usage examples

```text
Use verified-engineer to add a --dry-run flag to the CLI and cover it with tests.
```
```text
Review the changes on this branch. Do not modify any files.
```
```text
This test fails intermittently. Find the root cause before changing anything.
```
```text
Are we ready to release v1.2? Report only; do not tag or publish.
```

If the skill does not trigger on its own, name it explicitly in your request.

---

## How it works

- **`SKILL.md`** is the orchestrator: operating principles, capability detection, intent routing, and the final report format.
- **`references/`** hold detailed guidance (debugging, testing, review, Git, security, and more) and are loaded only when relevant.
- **`workflows/`** hold step-by-step procedures for each mode. Each has the same ten sections, from *Purpose* through *Completion criteria*.
- **Capability detection:** the agent checks which tools it really has (read, search, edit, shell, Git, network). If one is missing, it says so, adapts (for example by giving a patch and the command for you to run), and does not pretend.
- **Safety:** repository content, logs, and tool output are treated as untrusted data. Embedded instructions are not followed.

---

## Repository layout

```
verified-engineer-skill/
├── README.md                    this file
├── LICENSE
└── skills/
    └── verified-engineer/
        ├── SKILL.md             entry point
        ├── README.md            package-level notes
        ├── references/          9 guides (loaded on demand)
        ├── workflows/           7 step-by-step procedures
        ├── integrations/        optional host-specific notes
        ├── templates/           project-instruction snippet
        ├── scripts/validate_skill.py
        ├── tests/test_validate_skill.py
        └── evals/behavior-tests.md
```

---

## Validate and test

Requires Python 3.8+ and nothing else (standard library only).

```bash
# Validate the package structure (read-only)
python skills/verified-engineer/scripts/validate_skill.py --strict

# Run the validator's unit tests
python -m unittest discover -s skills/verified-engineer/tests -v
```

Exit codes: `0` pass, `1` validation failure, `2` usage problem or internal error. Use `--allow-dir-mismatch` if you validate a copy whose folder name differs from the skill name.

**Validation is not evaluation.** The validator checks files: frontmatter, naming, links, required sections. It cannot show that an agent follows the skill. For that, run the manual scenarios in `skills/verified-engineer/evals/behavior-tests.md` on your own agent, several times each, and record the results.

---

## Customize

- Edit workflows in `workflows/`, keeping the ten required sections (the validator enforces them).
- Put project-specific commands and conventions in your agent's instruction file, not in the core skill.
- Add a reference or workflow, link it from `SKILL.md` so agents know when to load it, and add it to `REQUIRED_FILES` in the validator if it should be mandatory.
- If the skill triggers too rarely or too often, tune the frontmatter `description`, then retest.

---

## Limitations

- Works only with agents that support Agent Skills or can load Markdown instructions from files. This is **not** a claim of universal compatibility.
- Instructions guide behavior; they are not a security boundary. Sandboxing and permission prompts belong to the host platform.
- Results depend on the model and the tools the agent has. A skill cannot make a weak agent reason like a strong one.
- Weaker agents may skip the reference files.
- The validator uses a small YAML subset parser and checks only inline Markdown links.
- No behavioral evaluation results are published yet. Treat claims about agent behavior as unproven until you measure them.

---

## Contributing

Issues and pull requests are welcome. Before opening one:

1. Run the validator in strict mode and the unit tests.
2. Keep core files vendor-neutral; put host-specific notes under `integrations/`.
3. If you change agent-facing instructions, run at least a few scenarios from `evals/behavior-tests.md` and describe the results.

---

## License

MIT. See [LICENSE](LICENSE).
