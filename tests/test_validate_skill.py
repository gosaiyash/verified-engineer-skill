"""Unit tests for scripts/validate_skill.py (stdlib unittest only).

These tests build throwaway skill packages in temporary directories. They need
no network, credentials, or AI model. They verify the VALIDATOR, not whether an
agent follows the skill (see evals/behavior-tests.md for that).

Run from the package root:
    python -m unittest discover -s tests -v
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PACKAGE_ROOT, "scripts"))

import validate_skill as vs  # noqa: E402

SKILL_NAME = "agentic-coding-engineer"
FILLER = (
    "This sentence is deliberate filler content used to make a fixture file "
    "substantive enough for the validator. "
) * 6

WORKFLOW_BODY = "\n".join(
    "## %s\n%s\n" % (title, FILLER)
    for title in (
        "Purpose",
        "When to use",
        "Required inputs",
        "Preconditions",
        "Procedure",
        "Conditional decisions",
        "Failure handling",
        "Safety checks",
        "Expected output",
        "Completion criteria",
    )
)

VALID_FRONTMATTER = (
    "---\n"
    "name: %s\n"
    "description: Helps agents do engineering work. Use when building or fixing code.\n"
    "---\n" % SKILL_NAME
)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_valid_package(parent, name=SKILL_NAME):
    """Create a minimal package that should pass validation. Returns its root."""
    root = os.path.join(parent, name)
    links = "\n".join(
        "- [%s](%s)" % (rel, rel)
        for rel in vs.REQUIRED_FILES
        if rel.startswith(("references/", "workflows/"))
    )
    skill_md = VALID_FRONTMATTER.replace(SKILL_NAME, name) + "\n# Skill\n\n" + FILLER + "\n\n" + links + "\n"
    write(os.path.join(root, "SKILL.md"), skill_md)
    for rel in vs.REQUIRED_FILES:
        if rel == "SKILL.md":
            continue
        body = WORKFLOW_BODY if rel.startswith("workflows/") else "# %s\n\n%s\n" % (rel, FILLER)
        write(os.path.join(root, *rel.split("/")), body)
    return root


def tree_digest(root):
    digest = hashlib.sha256()
    for current, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(current, name)
            digest.update(os.path.relpath(full, root).encode("utf-8"))
            with open(full, "rb") as handle:
                digest.update(handle.read())
        for name in dirs:
            digest.update(("dir:" + os.path.relpath(os.path.join(current, name), root)).encode("utf-8"))
    return digest.hexdigest()


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = vs.main(argv)
    return code, out.getvalue(), err.getvalue()


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="skill-test-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = build_valid_package(self.tmp)

    def messages(self, report):
        return [item["message"] for item in report.errors]


class TestValidPackage(ValidatorTestCase):
    def test_valid_package_passes(self):
        report = vs.validate_package(self.root)
        self.assertEqual(report.errors, [], report.errors)
        self.assertTrue(report.ok)

    def test_main_returns_zero_for_valid_package(self):
        code, out, _ = run_main([self.root])
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)

    def test_json_output_is_parseable(self):
        code, out, _ = run_main([self.root, "--format", "json"])
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertTrue(data["ok"])
        self.assertEqual(data["errors"], [])

    def test_validation_does_not_modify_package(self):
        before = tree_digest(self.root)
        vs.validate_package(self.root)
        run_main([self.root])
        self.assertEqual(before, tree_digest(self.root))

    def test_validation_does_not_modify_a_broken_package_either(self):
        os.remove(os.path.join(self.root, "references", "git-safety.md"))
        write(os.path.join(self.root, "SKILL.md"), "no frontmatter here")
        before = tree_digest(self.root)
        run_main([self.root])
        self.assertEqual(before, tree_digest(self.root))


class TestRequiredFiles(ValidatorTestCase):
    def test_missing_reference_file_fails(self):
        os.remove(os.path.join(self.root, "references", "security-review.md"))
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)
        paths = [item["path"] for item in report.errors]
        self.assertIn("references/security-review.md", paths)

    def test_missing_skill_md_fails(self):
        os.remove(os.path.join(self.root, "SKILL.md"))
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)
        self.assertIn("SKILL.md", [item["path"] for item in report.errors])

    def test_missing_workflow_directory_fails(self):
        shutil.rmtree(os.path.join(self.root, "workflows"))
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)
        missing = [i["path"] for i in report.errors if "missing" in i["message"]]
        self.assertTrue(any(p.startswith("workflows/") for p in missing))

    def test_required_path_that_is_a_directory_fails(self):
        target = os.path.join(self.root, "README.md")
        os.remove(target)
        os.mkdir(target)
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)


class TestFrontmatter(ValidatorTestCase):
    def set_skill(self, text):
        write(os.path.join(self.root, "SKILL.md"), text)

    def test_missing_frontmatter_fails(self):
        self.set_skill("# Just a heading\n\n" + FILLER)
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)
        self.assertTrue(any("frontmatter" in m for m in self.messages(report)))

    def test_unclosed_frontmatter_fails(self):
        self.set_skill("---\nname: %s\ndescription: x\n\n# body" % SKILL_NAME)
        report = vs.validate_package(self.root)
        self.assertTrue(any("not closed" in m for m in self.messages(report)))

    def test_missing_name_fails(self):
        self.set_skill("---\ndescription: Use when testing.\n---\n\nbody " + FILLER)
        report = vs.validate_package(self.root)
        self.assertTrue(any("'name'" in m for m in self.messages(report)))

    def test_missing_description_fails(self):
        self.set_skill("---\nname: %s\n---\n\nbody %s" % (SKILL_NAME, FILLER))
        report = vs.validate_package(self.root)
        self.assertTrue(any("'description'" in m for m in self.messages(report)))

    def test_invalid_name_values_fail(self):
        for bad in ("Agentic-Coding", "-leading", "trailing-", "double--hyphen", "has space", "under_score"):
            with self.subTest(name=bad):
                self.set_skill("---\nname: %s\ndescription: Use when testing.\n---\n\n%s" % (bad, FILLER))
                report = vs.validate_package(self.root, allow_dir_mismatch=True)
                self.assertTrue(
                    any("lowercase letters" in m for m in self.messages(report)), bad
                )

    def test_name_too_long_fails(self):
        long_name = "a" * (vs.NAME_MAX + 1)
        self.set_skill("---\nname: %s\ndescription: Use when testing.\n---\n\n%s" % (long_name, FILLER))
        report = vs.validate_package(self.root, allow_dir_mismatch=True)
        self.assertTrue(any("exceeds" in m for m in self.messages(report)))

    def test_description_too_long_fails(self):
        desc = "Use when testing. " + "x" * vs.DESCRIPTION_MAX
        self.set_skill("---\nname: %s\ndescription: %s\n---\n\n%s" % (SKILL_NAME, desc, FILLER))
        report = vs.validate_package(self.root)
        self.assertTrue(any("maximum" in m for m in self.messages(report)))

    def test_name_directory_mismatch_is_error_unless_allowed(self):
        other = build_valid_package(self.tmp, name="agentic-coding-engineer-copy")
        write(os.path.join(other, "SKILL.md"), VALID_FRONTMATTER + "\n" + FILLER)
        strict = vs.validate_package(other)
        lenient = vs.validate_package(other, allow_dir_mismatch=True)
        self.assertTrue(any("directory name" in m for m in self.messages(strict)))
        self.assertFalse(any("directory name" in m for m in self.messages(lenient)))
        self.assertTrue(any("directory name" in w["message"] for w in lenient.warnings))

    def test_folded_and_quoted_values_parse(self):
        self.set_skill(
            "---\nname: \"%s\"\ndescription: >\n  Helps agents.\n  Use when testing.\n"
            "metadata:\n  version: \"1.0\"\n---\n\n%s" % (SKILL_NAME, FILLER)
        )
        report = vs.validate_package(self.root)
        self.assertEqual(self.messages(report), [])

    def test_duplicate_key_is_reported(self):
        self.set_skill("---\nname: a\nname: b\ndescription: Use when x.\n---\n\n" + FILLER)
        report = vs.validate_package(self.root)
        self.assertTrue(any("duplicate" in m for m in self.messages(report)))

    def test_unknown_key_is_warning_not_error(self):
        self.set_skill(
            "---\nname: %s\ndescription: Use when testing.\nfancy: yes\n---\n\n%s" % (SKILL_NAME, FILLER)
        )
        report = vs.validate_package(self.root)
        self.assertEqual(self.messages(report), [])
        self.assertTrue(any("fancy" in w["message"] for w in report.warnings))


class TestSubstance(ValidatorTestCase):
    def test_empty_supporting_file_is_detected(self):
        write(os.path.join(self.root, "references", "code-review.md"), "")
        report = vs.validate_package(self.root)
        self.assertTrue(
            any(i["path"] == "references/code-review.md" and "empty" in i["message"] for i in report.errors)
        )

    def test_whitespace_only_file_is_detected(self):
        write(os.path.join(self.root, "workflows", "refactor-code.md"), "   \n\n\t\n")
        report = vs.validate_package(self.root)
        self.assertTrue(any(i["path"] == "workflows/refactor-code.md" for i in report.errors))

    def test_placeholder_file_is_detected(self):
        write(os.path.join(self.root, "references", "git-safety.md"), "# TODO\n")
        report = vs.validate_package(self.root)
        self.assertTrue(any("too little content" in i["message"] for i in report.errors))

    def test_workflow_missing_required_section_fails(self):
        body = WORKFLOW_BODY.replace("## Safety checks", "## Something else")
        write(os.path.join(self.root, "workflows", "debug-and-fix.md"), body)
        report = vs.validate_package(self.root)
        self.assertTrue(any("safety checks" in m for m in self.messages(report)))


class TestLinks(ValidatorTestCase):
    def append_to_skill(self, text):
        path = os.path.join(self.root, "SKILL.md")
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("\n" + text + "\n")

    def test_broken_local_link_is_reported(self):
        self.append_to_skill("See [missing](references/does-not-exist.md).")
        report = vs.validate_package(self.root)
        self.assertTrue(any("broken local link" in m for m in self.messages(report)))

    def test_valid_link_with_anchor_passes(self):
        self.append_to_skill("See [ok](references/code-review.md#severity-scale).")
        report = vs.validate_package(self.root)
        self.assertEqual(self.messages(report), [])

    def test_external_and_anchor_links_are_ignored(self):
        self.append_to_skill("[a](https://example.com/x) [b](#top) [c](mailto:a@b.c)")
        report = vs.validate_package(self.root)
        self.assertEqual(self.messages(report), [])

    def test_links_inside_code_are_ignored(self):
        self.append_to_skill("```\n[fake](nope.md)\n```\nInline `[fake](nope2.md)` too.")
        report = vs.validate_package(self.root)
        self.assertEqual(self.messages(report), [])

    def test_link_escaping_package_root_is_reported(self):
        self.append_to_skill("[out](../outside.md)")
        write(os.path.join(self.tmp, "outside.md"), "x")
        report = vs.validate_package(self.root)
        self.assertTrue(any("escapes the package root" in m for m in self.messages(report)))


class TestMalformedInput(ValidatorTestCase):
    def test_binary_skill_md_gives_error_not_crash(self):
        with open(os.path.join(self.root, "SKILL.md"), "wb") as handle:
            handle.write(b"\xff\xfe\x00\x00 not utf8 \x80\x81")
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)
        self.assertTrue(any("UTF-8" in m for m in self.messages(report)))

    def test_nonexistent_root_gives_error_not_crash(self):
        report = vs.validate_package(os.path.join(self.tmp, "nope"))
        self.assertFalse(report.ok)
        self.assertTrue(any("does not exist" in m for m in self.messages(report)))

    def test_root_that_is_a_file_gives_error(self):
        file_path = os.path.join(self.tmp, "afile")
        write(file_path, "x")
        report = vs.validate_package(file_path)
        self.assertTrue(any("not a directory" in m for m in self.messages(report)))

    def test_completely_empty_directory(self):
        empty = os.path.join(self.tmp, "empty-skill")
        os.mkdir(empty)
        report = vs.validate_package(empty, allow_dir_mismatch=True)
        self.assertFalse(report.ok)
        self.assertGreaterEqual(len(report.errors), len(vs.REQUIRED_FILES))

    def test_garbled_frontmatter_line_gives_error(self):
        write(os.path.join(self.root, "SKILL.md"), "---\nthis is: : not [valid\n  weird\n---\n" + FILLER)
        report = vs.validate_package(self.root)
        self.assertFalse(report.ok)


class TestExitCodes(ValidatorTestCase):
    def test_failure_exit_code_is_one(self):
        os.remove(os.path.join(self.root, "references", "code-review.md"))
        code, out, _ = run_main([self.root])
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)

    def test_missing_root_exit_code_is_two(self):
        code, _, _ = run_main([os.path.join(self.tmp, "does-not-exist")])
        self.assertEqual(code, 2)

    def test_bad_arguments_exit_code_is_two(self):
        code, _, _ = run_main(["--format", "yaml"])
        self.assertEqual(code, 2)

    def test_strict_mode_turns_warnings_into_failure(self):
        write(
            os.path.join(self.root, "SKILL.md"),
            VALID_FRONTMATTER
            + "\nMentions Cursor once. "
            + FILLER
            + "\n"
            + "\n".join(
                "- [%s](%s)" % (r, r)
                for r in vs.REQUIRED_FILES
                if r.startswith(("references/", "workflows/"))
            ),
        )
        lenient, _, _ = run_main([self.root])
        strict, _, _ = run_main([self.root, "--strict"])
        self.assertEqual(lenient, 0)
        self.assertEqual(strict, 1)

    def test_unlinked_reference_is_warning(self):
        write(os.path.join(self.root, "SKILL.md"), VALID_FRONTMATTER + "\n" + FILLER)
        report = vs.validate_package(self.root)
        self.assertEqual(self.messages(report), [])
        self.assertTrue(any("not mentioned in SKILL.md" in w["message"] for w in report.warnings))


class TestRealPackage(unittest.TestCase):
    """The shipped package should validate cleanly (strict)."""

    def test_shipped_package_passes_strict(self):
        report = vs.validate_package(PACKAGE_ROOT, allow_dir_mismatch=True)
        self.assertEqual(report.errors, [], report.errors)
        self.assertEqual(report.warnings, [], report.warnings)


if __name__ == "__main__":
    unittest.main()
