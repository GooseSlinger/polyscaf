import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import check_file_exists, create_folder_with_init, create_git_ignore


def make_schema(name: str) -> None:
    """Сгенерировать Pydantic-схему."""
    path = BASE_DIR / "schemas"
    create_folder_with_init(path)
    file_path = path / f"{name}Schema.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from pydantic import BaseModel, Field\n"
        "from typing import Optional\n\n"
        f"class {name}Schema(BaseModel):\n"
        f"    name: str\n"
    )
    typer.echo(f"✅ Схема {name} создана")
