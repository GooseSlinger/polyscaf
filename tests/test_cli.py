import subprocess
import sys
import tempfile
import unittest
from importlib.metadata import version
from pathlib import Path


MAIN = Path(__file__).resolve().parents[1] / "main.py"


class CliGenerationTest(unittest.TestCase):
    def run_cli(self, directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MAIN), *args],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_invalid_names_create_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "project"
            project.mkdir()
            for args in (
                ("make-script", "../../Outside"),
                ("make-service", "User-Profile", "--with", "msr"),
                ("make-project", 'My"App'),
                ("make-model", "class"),
            ):
                with self.subTest(args=args):
                    result = self.run_cli(project, *args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(list(project.iterdir()), [])
                    self.assertFalse((root / "_outside_script.py").exists())

    def test_version_option_reports_installed_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "--version")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, f"polyscaf {version('polyscaf')}\n")

    def test_generated_project_and_exports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.assertEqual(self.run_cli(project, "make-project", "MyApp").returncode, 0)
            self.assertEqual(
                self.run_cli(project, "make-service", "User", "--with", "msr").returncode,
                0,
            )
            self.assertEqual(self.run_cli(project, "make-test", "Health").returncode, 0)
            requirements = (project / "requirements.txt").read_text()
            self.assertIn("httpx2\n", requirements)
            self.assertNotIn("asyncpg", requirements)
            for directory, symbol in (
                ("models", "User"),
                ("schemas", "UserSchema"),
                ("routes", "UserRouter"),
                ("service", "UserService"),
            ):
                init_file = project / directory / "__init__.py"
                init_file.write_text(init_file.read_text() + "\n# custom code\n")
                self.assertEqual(init_file.read_text().count(f'"{symbol}"'), 1)
            service_file = project / "service" / "user_service.py"
            service_file.write_text(service_file.read_text() + "\n# custom code\n")
            self.assertEqual(
                self.run_cli(project, "make-service", "User", "--with", "msr").returncode,
                0,
            )
            self.assertTrue(service_file.read_text().endswith("# custom code\n"))
            for directory, symbol in (
                ("models", "User"),
                ("schemas", "UserSchema"),
                ("routes", "UserRouter"),
                ("service", "UserService"),
            ):
                init_content = (project / directory / "__init__.py").read_text()
                self.assertEqual(init_content.count(f'"{symbol}"'), 1)
                self.assertTrue(init_content.endswith("# custom code\n"))
            for file_path in project.rglob("*.py"):
                compile(file_path.read_text(), str(file_path), "exec")

    def test_existing_file_returns_failure_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.assertEqual(self.run_cli(project, "make-model", "User").returncode, 0)
            model = project / "models" / "user_model.py"
            model.write_text(model.read_text() + "\n# custom code\n")
            result = self.run_cli(project, "make-model", "User")
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(model.read_text().endswith("# custom code\n"))


if __name__ == "__main__":
    unittest.main()
