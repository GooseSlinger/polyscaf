import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_schema(name: str) -> None:
    """Сгенерировать Pydantic-схему."""
    path = BASE_DIR / "schemas"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_schema.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from pydantic import BaseModel\n\n"
        f"class {name}Schema(BaseModel):\n"
        f"    name: str\n"
    )
    typer.echo(f"✅ Схема {name} создана")
