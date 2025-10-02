import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
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

    file_path = path / f"{name}Factory.py"
    check_file_exists(file_path)

    file_path.write_text(
        "import factory\n"
        "from factory.alchemy import SQLAlchemyModelFactory\n"
        "from models import SomeModel\n"
        "from database import SessionLocal\n\n"
        f"class {name}(SQLAlchemyModelFactory):\n"
        "    class Meta:\n"
        "        model = SomeModel\n"
        "        sqlalchemy_session = SessionLocal()\n"
        "        sqlalchemy_session_persistence = 'commit'\n\n"
        "    name = factory.Iterator([ # колонка в таблице\n"
        "        'data1', # данные для колонки\n"
        "        'data2', \n"
        "        'data3', \n"
        "    ])"
    )
    typer.echo(f"✅ Фабрика {name} создана")
