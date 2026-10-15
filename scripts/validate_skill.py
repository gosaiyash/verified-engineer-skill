#!/usr/bin/env python3
"""Validate the structure of an Agent Skills package (read-only, stdlib only).

Usage:
    python validate_skill.py [PACKAGE_ROOT] [--strict] [--format text|json]
                             [--allow-dir-mismatch]

Exit codes:
    0  validation passed (warnings allowed unless --strict)
    1  validation failed (errors, or warnings under --strict)
    2  usage problem or unexpected internal error (e.g. root is not a directory)

What this checks:
    * required files and directories exist and are non-trivial
    * SKILL.md has YAML frontmatter with a valid `name` and `description`
    * the name follows the Agent Skills naming rules and matches the directory
    * local Markdown links resolve inside the package
    * workflow files contain the required sections
    * portability hints (vendor-specific names in core files)

Limitations (by design):
    * The frontmatter reader is a deliberately small parser. It handles the
      common forms (plain, quoted, folded `>` and literal `|` scalars, and one
      level of nested mapping such as `metadata:`). It does NOT implement full
      YAML: anchors, flow collections, multi-document streams and exotic
      escapes are not interpreted. Use a real YAML parser for strict checks.
    * Link checking covers inline Markdown links `[text](path)` outside code
      blocks. Reference-style links and HTML links are not checked, and
      `#anchor` fragments are not verified.
    * This validates package STRUCTURE. It cannot tell you whether an AI agent
      actually follows the instructions; see evals/behavior-tests.md.
    * The validator never writes to the package.
"""

from __future__ import print_function

import argparse
import json
import os
import re
import sys

NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
SKILL_BODY_SOFT_LIMIT = 500  # lines
MIN_SUBSTANTIVE_CHARS = 300

ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "references/repository-analysis.md",
    "references/planning-and-implementation.md",
    "references/systematic-debugging.md",
    "references/testing-and-verification.md",
    "references/code-review.md",
    "references/safe-refactoring.md",
    "references/git-safety.md",
    "references/security-review.md",
    "references/completion-report.md",
    "workflows/explore-repository.md",
    "workflows/implement-feature.md",
    "workflows/debug-and-fix.md",
    "workflows/test-and-verify.md",
    "workflows/review-changes.md",
    "workflows/refactor-code.md",
    "workflows/release-readiness.md",
    "scripts/validate_skill.py",
    "tests/test_validate_skill.py",
    "evals/behavior-tests.md",
]

# Files that must have real content (not just exist).
SUBSTANTIVE_PREFIXES = ("references/", "workflows/")
SUBSTANTIVE_FILES = ["SKILL.md", "README.md", "evals/behavior-tests.md"]

# Each workflow must contain a heading that includes each of these phrases.
WORKFLOW_REQUIRED_SECTIONS = [
    "purpose",
    "when to use",
    "required inputs",
    "preconditions",
    "procedure",
    "conditional decisions",
    "failure handling",
    "safety checks",
    "expected output",
    "completion criteria",
]

# Core files should stay vendor-neutral. Optional integrations/README may mention these.
VENDOR_TERMS = [
    "claude code",
    "cursor",
    "copilot",
    "codex",
    "gemini cli",
    "windsurf",
    "aider",
    "openai",
    "anthropic",
]
PORTABILITY_SCAN_PREFIXES = ("references/", "workflows/")
PORTABILITY_SCAN_FILES = ["SKILL.md"]
# Neutral phrases that legitimately contain a vendor term in core files.
PORTABILITY_ALLOWLIST = []

LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def error(self, message, path=None):
        self.errors.append({"path": path, "message": message})

    def warn(self, message, path=None):
        self.warnings.append({"path": path, "message": message})

    def info(self, message, path=None):
        self.infos.append({"path": path, "message": message})

    @property
    def ok(self):
        return not self.errors


# ---------------------------------------------------------------------------
# Reading helpers (never raise on bad input; report instead)
# ---------------------------------------------------------------------------

def read_text(path, report, rel):
    """Return file text, or None after recording an error."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except (IOError, OSError) as exc:
        report.error("cannot read file: %s" % exc, rel)
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        report.error("file is not valid UTF-8 text", rel)
        return None
    if text.startswith("\ufeff"):
        text = text[1:]
    return text


def substantive_length(text):
    return len("".join(text.split()))


# ---------------------------------------------------------------------------
# Frontmatter parsing (small, documented subset of YAML)
# ---------------------------------------------------------------------------

class FrontmatterError(Exception):
    pass


def split_frontmatter(text):
    """Return (frontmatter_text, body_text). Raises FrontmatterError."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("SKILL.md must begin with a '---' frontmatter line")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    raise FrontmatterError("frontmatter is not closed with a '---' line")


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        inner = value[1:-1]
        if value[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        else:
            inner = inner.replace("''", "'")
        return inner
    return value


def _strip_comment(value):
    """Remove a trailing ' # comment' from an unquoted scalar."""
    stripped = value.strip()
    if stripped and stripped[0] in ("'", '"'):
        return stripped
    match = re.search(r"\s#", stripped)
    if match:
        return stripped[: match.start()].rstrip()
    return stripped


def parse_frontmatter(fm_text):
    """Parse a small subset of YAML into a dict. Raises FrontmatterError."""
    data = {}
    lines = fm_text.split("\n")
    i = 0
    key_re = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_\-]*)\s*:(?:\s+(.*)|\s*)$")
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in (" ", "\t"):
            raise FrontmatterError(
                "unexpected indented line in frontmatter: %r" % line.strip()
            )
        match = key_re.match(line)
        if not match:
            raise FrontmatterError("cannot parse frontmatter line: %r" % line)
        key, rest = match.group(1), (match.group(2) or "")
        if key in data:
            raise FrontmatterError("duplicate frontmatter key: %s" % key)
        rest_stripped = rest.strip()
        i += 1
        if rest_stripped in (">", "|", ">-", "|-", ">+", "|+"):
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i][0] in (" ", "\t")):
                block.append(lines[i].strip())
                i += 1
            joiner = " " if rest_stripped.startswith(">") else "\n"
            data[key] = joiner.join(part for part in block).strip()
        elif rest_stripped == "":
            nested = {}
            while i < len(lines) and (not lines[i].strip() or lines[i][0] in (" ", "\t")):
                sub = lines[i].strip()
                i += 1
                if not sub or sub.startswith("#"):
                    continue
                sub_match = key_re.match(sub)
                if not sub_match:
                    raise FrontmatterError("cannot parse nested line under %s: %r" % (key, sub))
                nested[sub_match.group(1)] = _unquote(_strip_comment(sub_match.group(2) or ""))
            data[key] = nested
        else:
            data[key] = _unquote(_strip_comment(rest_stripped))
    return data


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_required_files(root, report):
    for rel in REQUIRED_FILES:
        full = os.path.join(root, *rel.split("/"))
        if not os.path.exists(full):
            report.error("required file is missing", rel)
        elif not os.path.isfile(full):
            report.error("expected a file but found something else", rel)


def check_substantive(root, report):
    targets = list(SUBSTANTIVE_FILES)
    for rel in REQUIRED_FILES:
        if rel.startswith(SUBSTANTIVE_PREFIXES):
            targets.append(rel)
    for rel in sorted(set(targets)):
        full = os.path.join(root, *rel.split("/"))
        if not os.path.isfile(full):
            continue  # already reported as missing
        text = read_text(full, report, rel)
        if text is None:
            continue
        if not text.strip():
            report.error("file is empty", rel)
        elif substantive_length(text) < MIN_SUBSTANTIVE_CHARS:
            report.error(
                "file has too little content (<%d non-space characters); "
                "placeholders are not allowed" % MIN_SUBSTANTIVE_CHARS,
                rel,
            )


def check_skill_md(root, report, allow_dir_mismatch):
    rel = "SKILL.md"
    full = os.path.join(root, rel)
    if not os.path.isfile(full):
        return None
    text = read_text(full, report, rel)
    if text is None:
        return None
    if not text.strip():
        report.error("SKILL.md is empty", rel)
        return None
    try:
        fm_text, body = split_frontmatter(text)
    except FrontmatterError as exc:
        report.error(str(exc), rel)
        return None
    try:
        meta = parse_frontmatter(fm_text)
    except FrontmatterError as exc:
        report.error("invalid frontmatter: %s" % exc, rel)
        return None

    # name
    name = meta.get("name")
    if name is None:
        report.error("frontmatter is missing required field 'name'", rel)
    elif not isinstance(name, str) or not name.strip():
        report.error("'name' must be a non-empty string", rel)
    else:
        if len(name) > NAME_MAX:
            report.error("'name' exceeds %d characters" % NAME_MAX, rel)
        if not NAME_RE.match(name):
            report.error(
                "'name' must use lowercase letters, digits and single hyphens, "
                "with no leading, trailing or consecutive hyphens: %r" % name,
                rel,
            )
        dir_name = os.path.basename(os.path.abspath(root))
        if name != dir_name:
            message = "'name' (%s) does not match the directory name (%s)" % (name, dir_name)
            if allow_dir_mismatch:
                report.warn(message, rel)
            else:
                report.error(message + "; use --allow-dir-mismatch to downgrade", rel)

    # description
    description = meta.get("description")
    if description is None:
        report.error("frontmatter is missing required field 'description'", rel)
    elif not isinstance(description, str) or not description.strip():
        report.error("'description' must be a non-empty string", rel)
    else:
        if len(description) > DESCRIPTION_MAX:
            report.error(
                "'description' is %d characters; the maximum is %d"
                % (len(description), DESCRIPTION_MAX),
                rel,
            )
        if "<" in description or ">" in description:
            report.warn("'description' contains angle brackets; some hosts reject them", rel)
        if "use when" not in description.lower() and "use whenever" not in description.lower():
            report.warn(
                "'description' should say what the skill does AND when to use it "
                "(e.g. 'Use when ...')",
                rel,
            )

    # optional fields
    compat = meta.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            report.error("'compatibility' must be a string", rel)
        elif len(compat) > COMPATIBILITY_MAX:
            report.error("'compatibility' exceeds %d characters" % COMPATIBILITY_MAX, rel)
    if "metadata" in meta and not isinstance(meta["metadata"], dict):
        report.error("'metadata' must be a mapping of string keys to string values", rel)
    for key in meta:
        if key not in ALLOWED_FRONTMATTER_KEYS:
            report.warn("unrecognized frontmatter field %r (ignored by the spec)" % key, rel)

    body_lines = body.count("\n") + 1
    if body_lines > SKILL_BODY_SOFT_LIMIT:
        report.warn(
            "SKILL.md body has %d lines; keep it under ~%d and move detail into references"
            % (body_lines, SKILL_BODY_SOFT_LIMIT),
            rel,
        )
    return meta


def iter_markdown_files(root):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__pycache__")
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                full = os.path.join(current, filename)
                yield full, os.path.relpath(full, root).replace(os.sep, "/")


def extract_links(text):
    """Return list of (line_number, target) for inline links outside code."""
    results = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        cleaned = INLINE_CODE_RE.sub("", line)
        for match in LINK_RE.finditer(cleaned):
            results.append((number, match.group(1)))
    return results


def is_external(target):
    lowered = target.lower()
    return bool(re.match(r"^[a-z][a-z0-9+.\-]*:", lowered)) or lowered.startswith("//")


def check_links(root, report):
    root_real = os.path.realpath(root)
    for full, rel in iter_markdown_files(root):
        text = read_text(full, report, rel)
        if text is None:
            continue
        for line_no, target in extract_links(text):
            if target.startswith("#") or is_external(target):
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            resolved = os.path.realpath(os.path.join(os.path.dirname(full), path_part))
            location = "%s:%d" % (rel, line_no)
            if resolved != root_real and not resolved.startswith(root_real + os.sep):
                report.error("link escapes the package root: %s" % target, location)
            elif not os.path.exists(resolved):
                report.error("broken local link: %s" % target, location)


def heading_texts(text):
    headings = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#{1,6}\s+\S", line):
            headings.append(re.sub(r"^#{1,6}\s+", "", line).strip().lower())
    return headings


def check_workflow_sections(root, report):
    for rel in REQUIRED_FILES:
        if not rel.startswith("workflows/"):
            continue
        full = os.path.join(root, *rel.split("/"))
        if not os.path.isfile(full):
            continue
        text = read_text(full, report, rel)
        if text is None:
            continue
        headings = heading_texts(text)
        for section in WORKFLOW_REQUIRED_SECTIONS:
            if not any(section in heading for heading in headings):
                report.error("workflow is missing required section: %s" % section, rel)


def check_skill_references_files(root, report):
    """Warn when a references/ or workflows/ file is never linked or named from SKILL.md."""
    full = os.path.join(root, "SKILL.md")
    if not os.path.isfile(full):
        return
    try:
        with open(full, "rb") as handle:
            text = handle.read().decode("utf-8", "replace")
    except (IOError, OSError):
        return
    for rel in REQUIRED_FILES:
        if rel.startswith(("references/", "workflows/")) and rel not in text:
            report.warn("not mentioned in SKILL.md, so agents may never load it", rel)


def check_portability(root, report):
    targets = list(PORTABILITY_SCAN_FILES)
    for rel in REQUIRED_FILES:
        if rel.startswith(PORTABILITY_SCAN_PREFIXES):
            targets.append(rel)
    for rel in sorted(set(targets)):
        full = os.path.join(root, *rel.split("/"))
        if not os.path.isfile(full):
            continue
        try:
            with open(full, "rb") as handle:
                lowered = handle.read().decode("utf-8", "replace").lower()
        except (IOError, OSError):
            continue
        for term in VENDOR_TERMS:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, lowered) and term not in PORTABILITY_ALLOWLIST:
                report.warn(
                    "mentions vendor/product name %r; keep core files vendor-neutral "
                    "(put host-specific notes under integrations/)" % term,
                    rel,
                )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def validate_package(root, allow_dir_mismatch=False):
    """Validate the package at `root`; returns a Report. Never modifies files."""
    report = Report()
    if not os.path.exists(root):
        report.error("package root does not exist: %s" % root)
        return report
    if not os.path.isdir(root):
        report.error("package root is not a directory: %s" % root)
        return report

    check_required_files(root, report)
    check_skill_md(root, report, allow_dir_mismatch)
    check_substantive(root, report)
    check_workflow_sections(root, report)
    check_links(root, report)
    check_skill_references_files(root, report)
    check_portability(root, report)
    return report


def format_text(report, root):
    out = []
    out.append("Validating skill package: %s" % root)
    for label, items in (("ERROR", report.errors), ("WARNING", report.warnings)):
        for item in items:
            where = (" [%s]" % item["path"]) if item["path"] else ""
            out.append("%s%s: %s" % (label, where, item["message"]))
    out.append(
        "Result: %s (%d error(s), %d warning(s))"
        % ("PASS" if report.ok else "FAIL", len(report.errors), len(report.warnings))
    )
    return "\n".join(out)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Validate an Agent Skills package (read-only).",
    )
    default_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser.add_argument(
        "root",
        nargs="?",
        default=default_root,
        help="package root directory (default: the package containing this script)",
    )
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--allow-dir-mismatch",
        action="store_true",
        help="warn instead of fail when the directory name differs from the skill name",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits with 2 on usage errors
        return exc.code if isinstance(exc.code, int) else 2

    try:
        report = validate_package(args.root, allow_dir_mismatch=args.allow_dir_mismatch)
    except Exception as exc:  # defensive: never crash with a traceback
        print("INTERNAL ERROR: validator crashed: %s: %s" % (type(exc).__name__, exc),
              file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({
            "root": args.root,
            "ok": report.ok and not (args.strict and report.warnings),
            "errors": report.errors,
            "warnings": report.warnings,
        }, indent=2))
    else:
        print(format_text(report, args.root))

    if not os.path.isdir(args.root):
        return 2
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
