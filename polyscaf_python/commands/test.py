import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_test(name: str) -> None:
    """Сгенерировать заготовку smoke-теста."""
    path = BASE_DIR / "tests"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"test_{snake_name}.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "import unittest\n"
        "from fastapi.testclient import TestClient\n\n"
        "from main import app\n\n"
        "class RootSmokeTest(unittest.TestCase):\n"
        "    def setUp(self):\n"
        "        self.client = TestClient(app)\n\n"
        "    def test_root(self):\n"
        "        response = self.client.get(\"/\")\n"
        "        self.assertEqual(response.status_code, 200)\n"
        "        self.assertEqual(response.json(), {\"detail\": \"Hello World!\"})\n\n"
        "\n"
        "if __name__ == \"__main__\":\n"
        "    unittest.main()\n"
        "\n"
        "# Добавляйте дополнительные тесты по мере развития приложения.\n"
    )
    typer.echo(f"✅ Тест {name} создан")
