import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("packager", ROOT / "scripts/package_skills.py")
        cls.packager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.packager)

    def test_standalone_archive_contains_approved_content_and_manual_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            self.packager.package(ROOT, output)
            with zipfile.ZipFile(output / "masters-lenses.zip") as archive:
                self.assertEqual(len(archive.namelist()), 18)
                for name in ("design", "feedback", "evolve", "simplicity", "reliability", "performance"):
                    expected_license = (ROOT / "LICENSE").read_bytes()
                    self.assertEqual(archive.read(f"{name}/LICENSE"), expected_license)
                    self.assertEqual((output / f"skills/{name}/LICENSE").read_bytes(), expected_license)
                    body = archive.read(f"{name}/SKILL.md").decode("utf-8")
                    self.assertIn("\nlicense: MIT\n", body)
                    for source in (ROOT / "drafts/common.md", ROOT / f"drafts/{name}.md"):
                        approved = source.read_text(encoding="utf-8").strip().split("\n", 1)[1].strip()
                        self.assertIn(approved, body)
                    policy = archive.read(f"{name}/agents/openai.yaml").decode("utf-8")
                    self.assertIn("allow_implicit_invocation: false", policy)

    def test_check_detects_edited_skill_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            self.packager.package(ROOT, output)
            target = output / "skills/design/SKILL.md"
            target.write_text("unexpected manual edit", encoding="utf-8")
            with self.assertRaises(ValueError):
                self.packager.package(ROOT, output, check=True)
            self.assertEqual(target.read_text(encoding="utf-8"), "unexpected manual edit")

    def test_check_detects_changed_archive_and_build_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            self.packager.package(ROOT, output)
            archive = output / "masters-lenses.zip"
            original = archive.read_bytes()
            self.packager.package(ROOT, output)
            self.assertEqual(original, archive.read_bytes())
            archive.write_bytes(b"broken archive")
            with self.assertRaises(ValueError):
                self.packager.package(ROOT, output, check=True)


if __name__ == "__main__":
    unittest.main()
