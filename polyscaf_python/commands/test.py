import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_test(name: str) -> None:
    """Сгенерировать заготовку API-теста на pytest."""
    path = BASE_DIR / "tests"
    create_folder_with_init(path)
    file_path = path / f"test_{name}.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "import pytest\n"
        "from httpx import AsyncClient, ASGITransport\n"
        "from main import app\n\n"
        "transport = ASGITransport(app=app)\n"
        "base_url = \"http://test\"\n\n"
        "@pytest.mark.asyncio\n"
        "async def test_create_user_success():\n"
        "    async with AsyncClient(transport=transport, base_url=base_url) as ac:\n"
        "        response = await ac.post(\"/user/create\", json={\n"
        "            \"name\": \"Тест\",\n"
        "            \"email\": \"newuser@example.com\"\n"
        "        })\n"
        "    assert response.status_code == 200\n"
        "    assert \"успешно\" in response.text\n\n"
        "@pytest.mark.asyncio\n"
        "async def test_create_user_invalid_email():\n"
        "    async with AsyncClient(transport=transport, base_url=base_url) as ac:\n"
        "        response = await ac.post(\"/user/create\", json={\n"
        "            \"name\": \"Тест\",\n"
        "            \"email\": \"notanemail\"\n"
        "        })\n"
        "    assert response.status_code == 422\n\n"
        "# @pytest.mark.asyncio\n"
        "# async def test_upload_avatar_without_token():\n"
        "#    async with AsyncClient(transport=transport, base_url=base_url) as ac:\n"
        "#        with open(\"tests/test_image.jpg\", \"rb\") as file:\n"
        "#            files = {\"file\": (\"test.jpg\", file, \"image/jpeg\") }\n"
        "#            response = await ac.post(\"/user/1/upload_avatar\", files=files)\n"
        "#    assert response.status_code == 401\n"
        "#    assert \"Требуется токен\" in response.text\n"
    )
    typer.echo(f"✅ Тест {name} создан")
