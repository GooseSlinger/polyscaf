from pathlib import Path

import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    create_folder_with_init,
    create_git_ignore,
    pluralize,
    update_init_exports,
)


def _write_file(path: Path, content: str, label: str) -> None:
    if path.exists():
        typer.echo(f"⚠️ {label} уже существует")
        return

    path.write_text(content)
    typer.echo(f"✅ {label} создан")


def _create_service(name: str) -> None:
    path = BASE_DIR / "service"
    create_folder_with_init(path)
    create_git_ignore(path)

    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_service.py"
    _write_file(
        file_path,
        (
            f"class {name}Service:\n"
            f"    def __init__(self, db):\n"
            f"        self.db = db\n\n"
            f"    async def example_method(self) -> str:\n"
            f"        # Здесь обычно выполняют запросы к БД через self.db.\n"
            f"        return 'Hello from {name}'\n"
        ),
        f"Сервис {name}",
    )
    update_init_exports(path, f"{snake_name}_service", f"{name}Service")


def _create_model(name: str) -> None:
    path = BASE_DIR / "models"
    create_folder_with_init(path)
    create_git_ignore(path)

    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_model.py"
    table_name = camel_to_snake(name)
    _write_file(
        file_path,
        (
            "from datetime import datetime\n"
            "from typing import Optional\n\n"
            "from database import Base\n"
            "from sqlalchemy import DateTime, String, func\n"
            "from sqlalchemy.orm import Mapped, mapped_column\n\n"
            f"class {name}(Base):\n"
            f"    __tablename__ = '{pluralize(table_name.lower())}'\n\n"
            f"    id: Mapped[int] = mapped_column(primary_key=True, index=True)\n"
            f"    name: Mapped[str] = mapped_column(String, index=True)\n"
            f"    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())\n"
            f"    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)\n"
        ),
        f"Модель {name}",
    )
    update_init_exports(path, f"{snake_name}_model", name)


def _create_schema(name: str) -> None:
    path = BASE_DIR / "schemas"
    create_folder_with_init(path)
    create_git_ignore(path)

    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_schema.py"
    _write_file(
        file_path,
        (
            "from pydantic import BaseModel\n\n"
            f"class {name}Schema(BaseModel):\n"
            f"    name: str\n"
        ),
        f"Схема {name}",
    )
    update_init_exports(path, f"{snake_name}_schema", f"{name}Schema")


def _create_route(name: str) -> None:
    path = BASE_DIR / "routes"
    create_folder_with_init(path)
    create_git_ignore(path)

    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_route.py"
    _write_file(
        file_path,
        (
            "from fastapi import APIRouter\n\n"
            "router = APIRouter()\n\n"
            f"# Пример endpoint'а для этого ресурса:\n"
            f"# @router.get('/{snake_name}')\n"
            f"# async def read_{snake_name}():\n"
            f"#     return {{\"detail\": \"Implement {name} endpoints here\"}}\n"
        ),
        f"Путь {name}",
    )
    update_init_exports(
        path,
        f"{snake_name}_route",
        "router",
        alias=f"{name}Router",
    )


def make_service(
    name: str,
    with_: str = typer.Option(
        "",
        "--with",
        help="Буквы для доп. файлов: m=model, s=schema, r=route. Пример: mr",
    ),
) -> None:
    """Сгенерировать service и, опционально, связанные файлы.

    Примеры:
      polyscaf make-service User
      polyscaf make-service User --with m
      polyscaf make-service User --with mr

    Флаги:
      m = model
      s = schema
      r = route
    """
    parts = {char for char in with_.lower() if not char.isspace()}
    invalid = parts - {"m", "s", "r"}
    if invalid:
        typer.echo("❌ Допустимы только буквы: m, s, r")
        raise typer.Exit(code=1)

    _create_service(name)
    if "m" in parts:
        _create_model(name)
    if "s" in parts:
        _create_schema(name)
    if "r" in parts:
        _create_route(name)
    typer.echo(f"🎉 Сборка {name} завершена")
