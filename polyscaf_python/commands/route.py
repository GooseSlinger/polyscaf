import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import check_file_exists, create_folder_with_init, create_git_ignore


def make_route(name: str) -> None:
    """Сгенерировать модуль маршрутов FastAPI."""
    path = BASE_DIR / "routes"
    create_folder_with_init(path)
    file_path = path / f"{name}Route.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from fastapi import APIRouter, Depends\n\n"
        "from database import get_db\n"
        "from sqlalchemy.orm import Session\n"
        f"from service.{name}Service import {name}Service\n\n"
        "router = APIRouter()\n\n"
        f"def get_{name.lower()}_service(db: Session = Depends(get_db)):\n"
        f"  return {name}Service(db)\n\n"
        f"# @router.get('/{name.lower()}')\n"
        f"# async def create_{name.lower()}(data: пайдентик модель, service: {name}Service = Depends(get_{name.lower()}_service)):\n"
        f"#     return await service.create_{name.lower()}(data)\n"
    )
    typer.echo(f"✅ Путь {name} создан")
