import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
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
        "from fastapi import APIRouter, Depends\n"
        "from sqlalchemy.orm import Session\n\n"
        "from database import get_db\n"
        f"from schemas.{snake_name}_schema import {name}Schema\n"
        f"from service.{snake_name}_service import {name}Service\n\n"
        "router = APIRouter()\n\n"
        f"def get_{snake_name}_service(db: Session = Depends(get_db)):\n"
        f"    return {name}Service(db)\n\n"
        f"# @router.get('/{snake_name}')\n"
        f"# async def create_{snake_name}(data: {name}Schema, service: {name}Service = Depends(get_{snake_name}_service)):\n"
        f"#     return await service.create_{snake_name}(data)\n"
    )
    typer.echo(f"✅ Путь {name} создан")
