import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_factory(name: str) -> None:
    """Сгенерировать фабрику для заполнения стартовыми данными."""
    database_path = BASE_DIR / "database"
    create_folder_with_init(database_path, is_database=True)
    create_git_ignore(database_path)

    path = database_path / "factories"
    create_folder_with_init(path)
    create_git_ignore(path)

    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_factory.py"
    check_file_exists(file_path)

    file_path.write_text(
        f"# {name}Factory scaffold.\n"
        "# Этот шаблон оставлен как заготовка, потому что async-стек проекта\n"
        "# не даёт простого безопасного SessionLocal для factory-boy.\n"
        "# Если вам реально нужны фабрики, добавьте отдельную sync-сессию вручную.\n"
    )
    typer.echo(f"✅ Фабрика {name} создана")
