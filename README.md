# agentic-coding-engineer

A portable **Agent Skill** that guides an AI coding agent through the full software-engineering lifecycle in the style of modern coding agents: understand the request, explore the repository, plan, implement, debug, test, review, refactor, inspect Git changes, check security, and report **only what was actually verified**.

The goal is reliable engineering behavior, not fast code generation.

## What it covers

Explore a repository - plan changes - implement features - debug systematically - write and run tests - review code - refactor safely - Git safety - security review - release-readiness assessment - honest completion reports.

## Package structure

```
agentic-coding-engineer/
├── SKILL.md                      Orchestration layer (the agent reads this first)
├── README.md                     This file
├── references/                   Detailed guidance, loaded on demand
│   ├── repository-analysis.md
│   ├── planning-and-implementation.md
│   ├── systematic-debugging.md
│   ├── testing-and-verification.md
│   ├── code-review.md
│   ├── safe-refactoring.md
│   ├── git-safety.md
│   ├── security-review.md
│   └── completion-report.md
├── workflows/                    Step-by-step procedures per mode
│   ├── explore-repository.md
│   ├── implement-feature.md
│   ├── debug-and-fix.md
│   ├── test-and-verify.md
│   ├── review-changes.md
│   ├── refactor-code.md
│   └── release-readiness.md
├── integrations/                 OPTIONAL host-specific notes
│   ├── claude-code.md
│   └── generic-agents.md
├── templates/
│   └── project-instructions.md   Snippet for AGENTS.md / CLAUDE.md-style files
├── scripts/
│   └── validate_skill.py         Package validator (stdlib only, read-only)
├── tests/
│   └── test_validate_skill.py    Unit tests for the validator (unittest)
└── evals/
    └── behavior-tests.md         Manual behavior scenarios for host agents
```

## Main workflow

1. **Capability detection** - the agent determines which tools it actually has (files, search, edit, shell, Git, network) and adapts when something is missing.
2. **Intent classification** - Explain, Explore, Plan, Implement, Debug, Test, Review, Refactor, Git, Documentation, Security audit, or Release readiness. The smallest sufficient procedure is chosen. Review-only modes never modify files.
3. **Investigate** - read project instructions, detect the toolchain from files, trace relevant code, check Git state.
4. **Plan** (when the change warrants it) - requirements, acceptance criteria, approach, edge cases, test strategy, risks, rollback.
5. **Implement or debug** - minimal coherent change following project conventions; root-cause debugging with evidence.
6. **Verify** - run the smallest relevant check first, then widen. Each check is reported as `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, or `INCONCLUSIVE`.
7. **Report** - summary, files changed, decisions, exact checks and results, limitations, remaining work.

The core files are vendor-neutral. Host-specific notes live only under `integrations/`.

## Installing

Installation differs by agent. Paths, permissions, slash commands, custom agents, and script execution all depend on the receiving platform, so no single procedure is correct everywhere.

- **Agent with Agent Skills support:** copy the whole `agentic-coding-engineer/` directory into the location that agent loads skills from (see its documentation). The directory name should equal the `name` in the `SKILL.md` frontmatter.
- **Claude Code:** see `integrations/claude-code.md`.
- **Other agents:** see `integrations/generic-agents.md` for skill-capable, instruction-file-only, and chat-only options.

After installing, give the agent a small real task and watch whether it loads `SKILL.md`, follows the workflow, and reports honestly.

## Validating the package and running the tests

Requires Python 3.8+ and nothing else.

```bash
# Validate the package (default: the package containing the script)
python scripts/validate_skill.py

# Validate another copy (use --allow-dir-mismatch if the folder was renamed)
python scripts/validate_skill.py /path/to/agentic-coding-engineer
python scripts/validate_skill.py /path/to/copy --allow-dir-mismatch

# Treat warnings as failures / machine-readable output
python scripts/validate_skill.py --strict
python scripts/validate_skill.py --format json

# Unit tests for the validator
python -m unittest discover -s tests -v
```

Exit codes: `0` pass, `1` validation failure, `2` usage problem or internal error. The validator never modifies files.

### What validation does and does not prove

Validation checks the package's **structure**: required files, frontmatter fields and naming rules, non-empty content, required sections in workflows, local Markdown links, and some portability hints. It uses a small, documented subset of YAML parsing (see the docstring in `scripts/validate_skill.py`), so exotic YAML is not fully interpreted.

It does **not** show that an AI agent follows the skill. That requires the manual scenarios in `evals/behavior-tests.md`, which have not been run for you. Treat any claim about agent behavior as unproven until you measure it on your agent.

## Customizing

- **Workflows:** edit files in `workflows/`. Keep the ten required sections (Purpose, When to use, Required inputs, Preconditions, Procedure, Conditional decisions, Failure handling, Safety checks, Expected output, Completion criteria) - the validator enforces them.
- **Add a workflow or reference:** create the file, link it from the routing table or reference index in `SKILL.md` so agents know when to load it, and add it to `REQUIRED_FILES` in the validator if it should be mandatory.
- **Project conventions:** keep them in your agent's project-instruction file (`templates/project-instructions.md`) rather than editing the core skill.
- **Keep `SKILL.md` lean:** the validator warns above ~500 lines. Move detail into `references/`.
- **Description tuning:** the frontmatter `description` is what hosts use to decide when to load the skill. If it triggers too rarely or too often, adjust the wording, then re-test.

## Adapting scripts to another environment

`validate_skill.py` is plain Python with no third-party dependencies and no network access. To adapt it: edit `REQUIRED_FILES`, `WORKFLOW_REQUIRED_SECTIONS`, `VENDOR_TERMS`, and the size constants at the top. If your environment lacks Python, validate on a machine that has it; the skill's instructions do not call the script.

## Known limitations and compatibility

- Works only with agents that support Agent Skills or can load Markdown instructions from files; this is **not** a claim of universal compatibility.
- Instructions guide behavior; they are not a security boundary. Sandboxing, permissions, and approval prompts are enforced by the host platform.
- Agent behavior is non-deterministic and model-dependent; quality varies across agents.
- Some hosts apply additional frontmatter restrictions or ignore optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`).
- Reference and workflow files are loaded only if the agent chooses to read them; weaker agents may skip them.
- The validator's YAML handling and link checking are intentionally limited (see above).
- No behavioral evaluation results are included.

## License

MIT (declared in the `SKILL.md` frontmatter). Add a `LICENSE` file if you redistribute.
