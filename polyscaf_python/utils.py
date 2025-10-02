from pathlib import Path
from typing import Any, cast
import typer
import inflect

from .settings import BASE_DIR

_inflect_engine = inflect.engine()


def pluralize(name: str) -> str:
    """Вернуть множественную форму имени с помощью inflect."""
    return _inflect_engine.plural(cast(Any, name))


def ensure_directory(path: Path) -> None:
    """Создать директорию вместе с родителями, если она отсутствует."""
    path.mkdir(parents=True, exist_ok=True)


def create_folder_with_init(path: Path, *, is_database: bool = False) -> None:
    """Гарантировать наличие папки и файла __init__.py."""
    ensure_directory(path)
    init_path = path / "__init__.py"
    if not init_path.exists():
        if is_database:
            init_path.write_text("from .database import SessionLocal, engine, Base\n")
        else:
            init_path.write_text("# init file\n")


def create_git_ignore(path: Path) -> None:
    """Создать .gitignore с правилом для __pycache__, если его нет."""
    ensure_directory(path)
    ignore_path = path / ".gitignore"
    if not ignore_path.exists():
        ignore_path.write_text("/__pycache__\n")


def check_file_exists(file_path: Path) -> None:
    """Завершить команду, если файл уже существует."""
    if file_path.exists():
        typer.echo(f"❌ Файл уже существует: {file_path}")
        raise typer.Exit()


def camel_to_snake(name: str) -> str:
    """Преобразовать CamelCase в snake_case."""
    snake_case: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index != 0:
            snake_case.append("_")
        snake_case.append(char.lower())
    return "".join(snake_case)


__all__ = [
    "BASE_DIR",
    "camel_to_snake",
    "check_file_exists",
    "create_folder_with_init",
    "create_git_ignore",
    "ensure_directory",
    "pluralize",
]
