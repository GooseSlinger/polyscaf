from pathlib import Path
from typing import Any, Optional, cast
import typer
import inflect

from .settings import BASE_DIR

AUTO_SECTION_START = "# polyscaf: auto-managed imports (start)"
AUTO_SECTION_END = "# polyscaf: auto-managed imports (end)"

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
        content = ""
        if is_database:
            content += "from .database import SessionLocal, engine, Base\n\n"
        content += f"{AUTO_SECTION_START}\n{AUTO_SECTION_END}\n"
        init_path.write_text(content)


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


def update_init_exports(
    directory: Path,
    module_name: str,
    symbol_name: str,
    *,
    alias: Optional[str] = None,
) -> None:
    """Добавить экспорт модуля в __init__.py и синхронизировать __all__."""
    ensure_directory(directory)
    init_path = directory / "__init__.py"
    if not init_path.exists():
        create_folder_with_init(directory)

    existing_content = init_path.read_text()
    if AUTO_SECTION_START not in existing_content or AUTO_SECTION_END not in existing_content:
        stripped = existing_content.strip()
        if not stripped or stripped == "# init file":
            existing_content = f"{AUTO_SECTION_START}\n{AUTO_SECTION_END}\n"
            init_path.write_text(existing_content)
        elif stripped.startswith("from .database import"):
            existing_content = existing_content.rstrip() + "\n\n" + f"{AUTO_SECTION_START}\n{AUTO_SECTION_END}\n"
            init_path.write_text(existing_content)
        else:
            # Не вмешиваемся в файлы без наших маркеров и с кастомным содержимым
            return
        existing_content = init_path.read_text()

    start_index = existing_content.index(AUTO_SECTION_START)
    end_index = existing_content.index(AUTO_SECTION_END, start_index)
    managed_segment = existing_content[
        start_index + len(AUTO_SECTION_START) : end_index
    ]

    entries: dict[str, tuple[str, str, Optional[str]]] = {}
    for raw_line in managed_segment.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("__all__"):
            continue
        if line.startswith("from ."):
            parts = line.replace(",", " ").split()
            if len(parts) >= 4 and parts[2] == "import":
                module = parts[1][1:]
                symbol = parts[3]
                import_alias = None
                if "as" in parts:
                    as_index = parts.index("as")
                    if as_index + 1 < len(parts):
                        import_alias = parts[as_index + 1]
                key = (import_alias or symbol).strip()
                entries[key] = (module, symbol.strip(), import_alias)

    key_name = alias or symbol_name
    entries[key_name] = (module_name, symbol_name, alias)

    managed_lines: list[str] = []
    if entries:
        for key in sorted(entries):
            module, symbol, import_alias = entries[key]
            if import_alias:
                managed_lines.append(f"from .{module} import {symbol} as {import_alias}")
            else:
                managed_lines.append(f"from .{module} import {symbol}")
        managed_lines.append("")
        managed_lines.append("__all__ = [")
        for key in sorted(entries):
            managed_lines.append(f'    "{key}",')
        managed_lines.append("]")
    else:
        managed_lines.append("__all__ = []")

    managed_block = "\n".join(managed_lines)
    new_content = (
        existing_content[:start_index]
        + f"{AUTO_SECTION_START}\n{managed_block}\n{AUTO_SECTION_END}"
        + existing_content[end_index + len(AUTO_SECTION_END) :]
    )
    if not new_content.endswith("\n"):
        new_content += "\n"
    init_path.write_text(new_content)


__all__ = [
    "BASE_DIR",
    "camel_to_snake",
    "check_file_exists",
    "create_folder_with_init",
    "create_git_ignore",
    "ensure_directory",
    "update_init_exports",
    "pluralize",
    "AUTO_SECTION_START",
    "AUTO_SECTION_END",
]
