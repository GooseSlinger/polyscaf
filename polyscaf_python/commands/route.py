import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
    update_init_exports,
)


def make_route(name: str) -> None:
    """Сгенерировать модуль маршрутов FastAPI."""
    path = BASE_DIR / "routes"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_route.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from fastapi import APIRouter\n\n"
        "router = APIRouter()\n\n"
        f"# Пример endpoint'а для этого ресурса:\n"
        f"# @router.get('/{snake_name}')\n"
        f"# async def read_{snake_name}():\n"
        f"#     return {{\"detail\": \"Implement {name} endpoints here\"}}\n"
    )
    update_init_exports(
        path,
        f"{snake_name}_route",
        "router",
        alias=f"{name}Router",
    )
    typer.echo(f"✅ Путь {name} создан")
