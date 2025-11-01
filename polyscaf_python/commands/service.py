import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
    update_init_exports,
)


def make_service(name: str) -> None:
    """Сгенерировать файл сервиса."""
    path = BASE_DIR / "service"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_service.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from sqlalchemy.orm import Session\n\n"
        f"from models.{snake_name}_model import {name}\n\n"
        f"class {name}Service:\n"
        f"    def __init__(self, db: Session):\n"
        f"        self.db = db\n\n"
        f"    def example_method(self) -> str:\n"
        f"        return 'Hello from {name}'\n"
    )
    update_init_exports(path, f"{snake_name}_service", f"{name}Service")
    typer.echo(f"✅ Сервис {name} создан")
