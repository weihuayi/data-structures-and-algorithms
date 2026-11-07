"""Real normal/failure fixtures for deterministic repository Skill checks."""

from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_skills import check_repository


class SkillCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills" / "example-case"
        self.skill.mkdir(parents=True)
        self.adapter_dir = self.root / ".agents" / "skills"
        self.adapter_dir.mkdir(parents=True)
        self.adapter = self.adapter_dir / "example-case"
        self.adapter.symlink_to("../../skills/example-case", target_is_directory=True)
        self.cases = self.root / "kb" / "design_cases"
        self.cases.mkdir(parents=True)
        self.write("AGENTS.md", "# Instruction\n[skills](skills/README.md)\n")
        self.write("kb/README.md", "[cases](design_cases/README.md)\n")
        self.write("skills/README.md", "[example](example-case/SKILL.md)\n")
        self.write("kb/design_cases/README.md", "[case](example.md)\n")
        self.write("kb/design_cases/example.md", "# A factual case\n")
        self.write("skills/example-case/SKILL.md", "---\nname: example-case\ndescription: Detect grounded cases\n---\n\n# Skill\n[case](../../kb/design_cases/example.md)\n")

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
        return file

    def fail_has(self, needle):
        result = check_repository(self.root)
        self.assertTrue(any(needle in item for item in result), result)

    def test_valid_structure(self):
        self.assertEqual(check_repository(self.root), [])

    def test_cli_exit_codes_are_deterministic(self):
        script = Path(__file__).resolve().parents[1] / "check_skills.py"
        good = subprocess.run([sys.executable, str(script), "--root", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        (self.skill / "SKILL.md").unlink()
        bad = subprocess.run([sys.executable, str(script), "--root", str(self.root)],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)

    def test_missing_skill(self):
        (self.skill / "SKILL.md").unlink()
        self.fail_has("missing SKILL.md")

    def test_missing_frontmatter(self):
        self.write("skills/example-case/SKILL.md", "# Missing metadata\n")
        self.fail_has("missing YAML frontmatter")

    def test_wrong_name_and_missing_description(self):
        self.write("skills/example-case/SKILL.md", "---\nname: other-case\ndescription: |\n---\n")
        errors = check_repository(self.root)
        self.assertTrue(any("invalid Skill name" in x for x in errors), errors)
        self.assertTrue(any("invalid Skill description" in x for x in errors), errors)

    def test_non_string_yaml_descriptions(self):
        for bad in ("null", "Null", "~", "[]", "{}", "true", "false",
                    "yes", "no", "123", "1.5", "# no description",
                    "|", ">", "|-", ">-"):
            with self.subTest(description=bad):
                self.write("skills/example-case/SKILL.md",
                           f"---\nname: example-case\ndescription: {bad}\n---\n")
                self.fail_has("invalid Skill description")

    def test_malformed_yaml_descriptions(self):
        for bad in ("Valid: invalid YAML", 'Not quoted "bad" # trailing',
                    '"unterminated', '"not" valid', "'unterminated",
                    "'bad' trailing", "hello # inline comment", '""', "''",
                    '"\\q"'):
            with self.subTest(description=bad):
                self.write("skills/example-case/SKILL.md",
                           f"---\nname: example-case\ndescription: {bad}\n---\n")
                self.fail_has("invalid Skill description")

    def test_valid_quoted_yaml_descriptions(self):
        for good in ('"Valid: quoted description"', "'We''re describing a case'",
                     '"Text # not an inline comment"', "普通课程案例说明"):
            with self.subTest(description=good):
                self.write("skills/example-case/SKILL.md",
                           f"---\nname: example-case\ndescription: {good}\n---\n")
                self.assertEqual(check_repository(self.root), [])

    def test_duplicate_frontmatter_key(self):
        self.write("skills/example-case/SKILL.md", "---\nname: example-case\nname: extra\ndescription: Valid\n---\n")
        self.fail_has("duplicate frontmatter field")

    def test_broken_discovery_link(self):
        self.adapter.unlink()
        self.adapter.symlink_to("../../skills/does-not-exist", target_is_directory=True)
        self.fail_has("broken or cyclic discovery adapter")

    def test_non_symlink_copy(self):
        self.adapter.unlink()
        self.adapter.mkdir()
        (self.adapter / "SKILL.md").write_text("duplicate body")
        self.fail_has("missing or non-symlink discovery adapter")

    def test_discovery_link_wrong_target(self):
        other = self.root / "skills" / "another"
        other.mkdir()
        self.adapter.unlink()
        self.adapter.symlink_to("../../skills/another", target_is_directory=True)
        self.fail_has("wrong or escaping discovery target")

    def test_discovery_link_escapes_repo(self):
        self.adapter.unlink()
        self.adapter.symlink_to(self.root.parent, target_is_directory=True)
        self.fail_has("absolute discovery link")
        self.fail_has("wrong or escaping discovery target")

    def test_orphan_discovery_adapter(self):
        (self.adapter_dir / "unknown").symlink_to("../../skills/example-case")
        self.fail_has("orphan discovery adapter")

    def test_unindexed_skill(self):
        self.write("skills/README.md", "# Skills\n")
        self.fail_has("unindexed Skill")

    def test_broken_local_link(self):
        self.write("skills/example-case/SKILL.md", "---\nname: example-case\ndescription: Valid\n---\n[bad](../../kb/missing.md)\n")
        self.fail_has("broken local link")

    def test_local_link_escapes_repo(self):
        outside = self.root.parent / (self.root.name + "-outside.md")
        outside.write_text("external")
        self.addCleanup(outside.unlink)
        self.write("skills/example-case/SKILL.md", f"---\nname: example-case\ndescription: Valid\n---\n[out]({outside})\n")
        self.fail_has("out-of-repository link")

    def test_case_index_broken(self):
        self.write("kb/design_cases/README.md", "[missing](missing.md)\n")
        self.fail_has("broken local link")

    def test_empty_local_link_reports_error(self):
        self.write("skills/README.md", "[bad]( )\n")
        self.fail_has("empty local link")

    def test_case_not_indexed(self):
        self.write("kb/design_cases/README.md", "# No case links\n")
        self.fail_has("unindexed design case")


if __name__ == "__main__":
    unittest.main()
