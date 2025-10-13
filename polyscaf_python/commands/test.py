import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_test(name: str) -> None:
    """Сгенерировать заготовку API-теста на pytest."""
    path = BASE_DIR / "tests"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"test_{snake_name}.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "import pytest\n"
        "from httpx import AsyncClient, ASGITransport\n\n"
        "from main import app\n\n"
        "transport = ASGITransport(app=app)\n"
        "base_url = \"http://test\"\n\n"
        "@pytest.mark.asyncio\n"
        f"async def test_create_{snake_name}_success():\n"
        "    async with AsyncClient(transport=transport, base_url=base_url) as ac:\n"
        f"        response = await ac.post(\"/{snake_name}/create\", json={{\n"
        "            \"name\": \"Тест\",\n"
        "            \"email\": \"newuser@example.com\"\n"
        "        })\n"
        "    assert response.status_code == 200\n"
        "    assert \"успешно\" in response.text\n\n"
        "@pytest.mark.asyncio\n"
        f"async def test_create_{snake_name}_invalid_email():\n"
        "    async with AsyncClient(transport=transport, base_url=base_url) as ac:\n"
        f"        response = await ac.post(\"/{snake_name}/create\", json={{\n"
        "            \"name\": \"Тест\",\n"
        "            \"email\": \"notanemail\"\n"
        "        })\n"
        "    assert response.status_code == 422\n\n"
        "# Добавляйте дополнительные тесты по мере развития приложения.\n"
    )
    typer.echo(f"✅ Тест {name} создан")
