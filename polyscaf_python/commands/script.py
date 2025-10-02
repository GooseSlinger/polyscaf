import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_script(name: str) -> None:
    """Сгенерировать скрипт для загрузки стартовых данных."""
    path = BASE_DIR / "scripts"
    create_folder_with_init(path)
    file_path = path / f"{name}Script.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        "from database import SessionLocal, engine\n"
        "from models import SomeMOdel\n"
        "from database.factories.SomeFactory import SomeFactory\n\n"
        f"def {name}Script():\n"
        "    db = SessionLocal()\n"
        "    try:\n"
        "        existing = db.query(SomeMOdel).count()\n\n"
        "        if existing > 0:\n"
        "            print('Стартовые данные уже существуют')\n"
        "            return\n\n"
        "        SomeFactory.create_batch(7)\n\n"
        "        print('Данные загружены успешно')\n"
        "    except Exception as e:\n"
        "        print(f\"Произошла ошибка в загрузке данных: {e}\")\n"
        "        db.rollback()\n"
        "    finally:\n"
        "        db.close()\n\n"
        "if __name__ == '__main__':\n"
        f"    {name}Script()\n"
    )
    typer.echo(f"✅ скрипт {name} создан")
