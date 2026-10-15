# Git Safety

Use this for any Git inspection, staging, commit, branch, merge, or history task.

## Contents
- Core rules
- Inspect first
- Read-only commands
- Operations that need authorization
- Never do without explicit request
- Preparing a commit
- Branches, merges, rebases
- Recovering from mistakes
- If Git is unavailable

## Core rules

1. **Inspect state before acting.** Know the branch, upstream, staged vs unstaged changes, untracked files, and in-progress operations (merge, rebase, cherry-pick).
2. **Unrelated changes are the user's.** Never revert, reformat, stash-and-forget, or stage them.
3. **Read-only when unsure.** If the intended action is unclear, stay with read-only commands and ask.
4. **Destructive means ask.** Anything that can lose work or rewrite history needs explicit, specific authorization for that action.

## Inspect first

Typical read-only starting set (adapt to the tools you have):

- `git status` (include branch and untracked files)
- `git diff` (unstaged), `git diff --staged` (staged), `git diff <base>...HEAD` (branch vs base)
- `git log --oneline -n 20`, `git log -p -n 3 -- <path>`
- `git branch -vv`, `git remote -v`
- `git stash list`
- `git blame <path>` / `git show <rev>` to understand history

## Read-only commands

Safe by nature: `status`, `diff`, `log`, `show`, `blame`, `branch` (list), `remote -v`, `stash list`, `ls-files`, `rev-parse`, `describe`, `shortlog`. Prefer these when exploring.

## Operations that need authorization

Require the user to have asked for (or clearly approved) the specific action:

- `git add` of files you did not create/modify for this task
- `git commit` (any commit)
- `git push` (any push)
- `git checkout`/`switch` that would overwrite local changes
- `git merge`, `git rebase`, `git cherry-pick`
- `git stash` (it moves the user's work)
- `git tag`, creating releases
- Changing Git config, hooks, or remotes

## Never do without explicit request

- `git reset --hard`, `git checkout -- <path>` / `git restore` on files with user changes, `git clean -fd`
- Force-push (`--force`, `--force-with-lease`), especially to shared or default branches
- Delete branches (local with unmerged work, or any remote branch)
- Rewrite published history (rebase/amend/filter-branch on pushed commits)
- Skip hooks or signing (`--no-verify`, disabling GPG) to make a commit succeed
- Commit or push secrets, credentials, large binaries, or build output

If a hook fails, fix the cause; do not bypass it.

## Preparing a commit

Only when a commit is requested:

1. Run `git status` and `git diff --staged`; if nothing is staged, show what you propose to stage.
2. Stage **only** files relevant to the task, by explicit path (avoid blanket `git add -A` when the tree contains unrelated changes).
3. Review staged content for: secrets, debug output, unrelated edits, generated files, merge markers.
4. Run the relevant tests/linters before committing; report the results.
5. Write a message in the repository's existing style (check `git log`). Describe *why* and *what*, concisely.
6. After committing, show the resulting `git log -1 --stat`. Do **not** push unless asked.

## Branches, merges, rebases

- Work on the branch the user is on unless told otherwise; confirm before creating or switching branches if the tree is dirty.
- Before merging/rebasing, make sure the tree is clean or the user has approved how to handle local changes.
- On conflicts: read both sides, resolve deliberately, run tests, and never pick "ours/theirs" wholesale without understanding the consequence.

## Recovering from mistakes

If you made a bad local change: undo **only your own edits** by targeted reversal. If history was changed, use `git reflog` to locate the prior state, explain it to the user, and ask before restoring. Never compound a mistake with another destructive command.

## If Git is unavailable

Say so. Ask the user for `git status`/`git diff` output, or work from the files supplied. Do not claim to have checked repository state you could not see.
