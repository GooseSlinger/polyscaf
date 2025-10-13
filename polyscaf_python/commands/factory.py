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

    class_name = f"{name}Factory"

    file_path.write_text(
        "import factory\n"
        "from factory.alchemy import SQLAlchemyModelFactory\n\n"
        "from database import SessionLocal\n"
        f"from models.{snake_name}_model import {name}\n\n"
        f"class {class_name}(SQLAlchemyModelFactory):\n"
        "    class Meta:\n"
        f"        model = {name}\n"
        "        sqlalchemy_session = SessionLocal()\n"
        "        sqlalchemy_session_persistence = 'commit'\n\n"
        f"    name = factory.Sequence(lambda n: f\"{snake_name}_{{n}}\")\n"
    )
    typer.echo(f"✅ Фабрика {name} создана")
