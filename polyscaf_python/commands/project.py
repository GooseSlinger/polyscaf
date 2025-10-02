import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import create_folder_with_init, create_git_ignore

FOLDERS = [
    "models",
    "schemas",
    "routes",
    "service",
    "database",
    "storage",
    "scripts",
]

DATABASE_TEMPLATE = (
    "from sqlalchemy import create_engine\n"
    "from sqlalchemy.orm import declarative_base\n"
    "from sqlalchemy.orm import sessionmaker\n"
    "import os\n"
    "from dotenv import load_dotenv\n"
    "load_dotenv()\n\n"
    "SQLALCHEMY_DATABASE_URL = os.getenv('SQL_BASE')\n\n"
    "## для sqlLite\n"
    "## engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={\"check_same_thread\": False})\n\n"
    "## для mySql\n"
    "engine = create_engine(SQLALCHEMY_DATABASE_URL)\n"
    "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
    "Base = declarative_base()\n\n"
    "def get_db():\n"
    "    db = SessionLocal()\n"
    "    try:\n"
    "        yield db\n"
    "    finally:\n"
    "        db.close()\n"
)

MAIN_TEMPLATE = (
    "from fastapi import FastAPI\n"
    "from fastapi.staticfiles import StaticFiles\n"
    "from database import Base, engine\n\n"
    "app = FastAPI()\n\n"
    "# Создание таблиц\n"
    "Base.metadata.create_all(bind=engine)\n\n"
    "# Монтируем папку со статическими файлами\n"
    "app.mount(\"/files\", StaticFiles(directory=\"storage/files\"), name=\"files\")\n\n"
    "# Подключаем роуты\n"
    "app.include_router(Rout.router, prefix=\"/path_name\", tags=[\"User\"])\n\n"
    "@app.get(\"/\")\n"
    "async def root():\n"
    "    return {\"detail\": \"Hello World!\"}\n"
)


def make_project() -> None:
    """Создать структуру проекта и стартовые файлы."""
    for folder in FOLDERS:
        path = BASE_DIR / folder
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            typer.echo(f"✅ Папка {folder} создана")
            create_folder_with_init(path, is_database=(folder == "database"))
            create_git_ignore(path)
        else:
            typer.echo(f"⚠️ Папка {folder} уже существует")

    database_file = BASE_DIR / "database" / "database.py"
    if not database_file.exists():
        database_file.write_text(DATABASE_TEMPLATE)
        typer.echo("✅ Файл database.py создан")
    else:
        typer.echo("⚠️ Файл database.py уже существует")

    main_file = BASE_DIR / "main.py"
    if not main_file.exists():
        main_file.write_text(MAIN_TEMPLATE)
        typer.echo("✅ Файл main.py создан")
    else:
        typer.echo("⚠️ Файл main.py уже существует")

    create_git_ignore(BASE_DIR)
