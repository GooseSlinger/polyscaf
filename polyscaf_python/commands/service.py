import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import check_file_exists, create_folder_with_init, create_git_ignore


def make_service(name: str) -> None:
    """Сгенерировать файл сервиса."""
    path = BASE_DIR / "service"
    create_folder_with_init(path)
    file_path = path / f"{name}Service.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from sqlalchemy.orm import Session\n\n"
        f"class {name}Service:\n"
        f"    def __init__(self, db: Session):\n"
        f"        self.db = db\n\n"
        f"    def example_method(self):\n"
        f"        return 'Hello from {name}'\n"
    )
    typer.echo(f"✅ Сервис {name} создан")
