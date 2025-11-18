import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import camel_to_snake, create_folder_with_init, create_git_ignore

FOLDERS = [
    "models",
    "schemas",
    "routes",
    "service",
    "database",
    "storage",
    "scripts",
]

BASE_REQUIREMENTS = [
    "fastapi",
    "sqlalchemy",
    "alembic",
    "aiohttp",
    "uvicorn",
    "python-dotenv",
    "dotenv",
    "python-multipart",
    "httpx",
    "inflect",
    "typer",
    "email_validator",
    "cryptography",
    "pydantic",
    "factory-boy",
]

DB_REQUIREMENTS = {
    "mysql": ["aiomysql", "pymysql"],
    "postgres": ["asyncpg", "psycopg[binary]"],
}

ENV_TEMPLATES = {
    "mysql": (
        "# Настройки базы данных (MySQL)\n"
        "# SQL_BASE должен указывать на сервер без имени БД,\n"
        "# например: mysql+pymysql://user:password@localhost:3306\n"
        "SQL_BASE=mysql+pymysql://user:password@localhost:3306\n"
        "SQL_DATABASE={database_name}\n"
    ),
    "postgres": (
        "# Настройки базы данных (PostgreSQL)\n"
        "# SQL_BASE должен указывать на существующую БД (обычно postgres),\n"
        "# например: postgresql+psycopg2://user:password@localhost:5432/postgres\n"
        "SQL_BASE=postgresql+psycopg2://user:password@localhost:5432/postgres\n"
        "SQL_DATABASE={database_name}\n"
    ),
}

DATABASE_TEMPLATES = {
    "mysql": (
        "import os\n"
        "from dotenv import load_dotenv\n"
        "from typing import Optional\n\n"
        "from sqlalchemy import create_engine, text\n"
        "from sqlalchemy.engine.url import make_url\n"
        "from sqlalchemy.orm import declarative_base, sessionmaker\n\n"
        "load_dotenv()\n\n"
        "SQLALCHEMY_DATABASE_URL = os.getenv('SQL_BASE')\n"
        "if not SQLALCHEMY_DATABASE_URL:\n"
        "    raise RuntimeError('Переменная для базы не установлена')\n\n"
        "def _ensure_database_exists(database_url: Optional[str]) -> None:\n"
        "    \"\"\"Создаёт целевую базу MySQL, если она отсутствует.\"\"\"\n"
        "    if not database_url:\n"
        "        return\n\n"
        "    url = make_url(database_url)\n"
        "    database_name = url.database\n\n"
        "    if not database_name or not url.drivername.startswith(\"mysql\"):\n"
        "        return\n\n"
        "    admin_url = url.set(database=\"\")\n"
        "    admin_engine = create_engine(admin_url, isolation_level=\"AUTOCOMMIT\")\n\n"
        "    try:\n"
        "        with admin_engine.connect() as conn:\n"
        "            identifier = f\"`{{database_name.replace('`', '``')}}`\"\n"
        "            conn.execute(text(f\"CREATE DATABASE IF NOT EXISTS {{identifier}}\"))\n"
        "    finally:\n"
        "        admin_engine.dispose()\n\n"
        "_ensure_database_exists(SQLALCHEMY_DATABASE_URL)\n\n"
        "engine = create_engine(SQLALCHEMY_DATABASE_URL)\n"
        "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
        "Base = declarative_base()\n\n"
        "def get_db():\n"
        "    db = SessionLocal()\n"
        "    try:\n"
        "        yield db\n"
        "    finally:\n"
        "        db.close()\n"
    ),
    "postgres": (
        "import os\n"
        "from dotenv import load_dotenv\n"
        "from typing import Optional\n\n"
        "from sqlalchemy import create_engine, text\n"
        "from sqlalchemy.engine.url import make_url\n"
        "from sqlalchemy.orm import declarative_base, sessionmaker\n\n"
        "load_dotenv()\n\n"
        "SQLALCHEMY_DATABASE_URL = os.getenv('SQL_BASE')\n"
        "if not SQLALCHEMY_DATABASE_URL:\n"
        "    raise RuntimeError('Переменная для базы не установлена')\n\n"
        "def _ensure_database_exists(database_url: Optional[str]) -> None:\n"
        "    \"\"\"Создаёт целевую базу PostgreSQL, если она отсутствует.\"\"\"\n"
        "    if not database_url:\n"
        "        return\n\n"
        "    url = make_url(database_url)\n"
        "    database_name = url.database\n\n"
        "    if not database_name or not url.drivername.startswith(\"postgres\"):\n"
        "        return\n\n"
        "    admin_url = url.set(database=\"postgres\")\n"
        "    admin_engine = create_engine(admin_url, isolation_level=\"AUTOCOMMIT\")\n\n"
        "    try:\n"
        "        with admin_engine.connect() as conn:\n"
        "            identifier = f\"\\\"{{database_name.replace('\"', '\"\"')}}\\\"\"\n"
        "            exists = conn.execute(\n"
        "                text(\"SELECT 1 FROM pg_database WHERE datname = :name\"),\n"
        "                {{\"name\": database_name}},\n"
        "            ).scalar()\n"
        "            if not exists:\n"
        "                conn.execute(text(f\"CREATE DATABASE {{identifier}} ENCODING 'UTF8'\"))\n"
        "    finally:\n"
        "        admin_engine.dispose()\n\n"
        "_ensure_database_exists(SQLALCHEMY_DATABASE_URL)\n\n"
        "engine = create_engine(SQLALCHEMY_DATABASE_URL)\n"
        "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
        "Base = declarative_base()\n\n"
        "def get_db():\n"
        "    db = SessionLocal()\n"
        "    try:\n"
        "        yield db\n"
        "    finally:\n"
        "        db.close()\n"
    ),
}

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


def make_project(
    project_name: str = typer.Argument(..., help="Название нового проекта в CamelCase."),
    mysql: bool = typer.Option(
        False,
        "-m",
        "--mysql",
        help="Использовать шаблон базы данных MySQL.",
        is_flag=True,
    ),
    postgres: bool = typer.Option(
        False,
        "-p",
        "--postgres",
        help="Использовать шаблон базы данных PostgreSQL.",
        is_flag=True,
    ),
) -> None:
    """Создать структуру проекта и стартовые файлы."""
    if mysql == postgres:
        typer.echo("❌ Укажите ровно один флаг: -m/--mysql или -p/--postgres")
        raise typer.Exit(code=1)

    db_engine = "mysql" if mysql else "postgres"
    normalized_name = project_name.strip()
    if not normalized_name:
        typer.echo("❌ Укажите название проекта в CamelCase.")
        raise typer.Exit(code=1)
    if any(symbol in normalized_name for symbol in (" ", "-", "_")):
        typer.echo("❌ Название проекта не должно содержать пробелов, дефисов или подчёркиваний.")
        raise typer.Exit(code=1)
    if not normalized_name[0].isalpha() or not normalized_name[0].isupper():
        typer.echo("❌ Название проекта должно начинаться с заглавной буквы.")
        raise typer.Exit(code=1)
    if normalized_name.lower() == normalized_name or normalized_name.upper() == normalized_name:
        typer.echo("❌ Используйте CamelCase для названия проекта (например: MyAwesomeApp).")
        raise typer.Exit(code=1)

    project_name = normalized_name
    project_slug = camel_to_snake(project_name)
    if not project_slug:
        typer.echo("❌ Не удалось определить имя проекта. Проверьте формат CamelCase.")
        raise typer.Exit(code=1)
    project_dir = BASE_DIR
    typer.echo(f"ℹ️ Создание проекта в текущей директории: {project_dir}")

    for folder in FOLDERS:
        path = project_dir / folder
        if not path.exists():
            create_folder_with_init(path, is_database=(folder == "database"))
            typer.echo(f"✅ Папка {folder} создана")
            create_git_ignore(path)
        else:
            typer.echo(f"⚠️ Папка {folder} уже существует")

    database_file = project_dir / "database" / "database.py"
    if not database_file.exists():
        database_file.write_text(DATABASE_TEMPLATES[db_engine].format(database_name=project_slug))
        typer.echo("✅ Файл database.py создан")
    else:
        typer.echo("⚠️ Файл database.py уже существует")

    main_file = project_dir / "main.py"
    if not main_file.exists():
        main_file.write_text(MAIN_TEMPLATE)
        typer.echo("✅ Файл main.py создан")
    else:
        typer.echo("⚠️ Файл main.py уже существует")

    env_file = project_dir / ".env"
    if not env_file.exists():
        env_file.write_text(ENV_TEMPLATES[db_engine].format(database_name=project_slug))
        typer.echo("✅ Файл .env создан")
    else:
        typer.echo("⚠️ Файл .env уже существует")

    requirements_file = project_dir / "requirements.txt"
    if not requirements_file.exists():
        requirements = BASE_REQUIREMENTS + DB_REQUIREMENTS[db_engine]
        requirements_file.write_text("\n".join(requirements) + "\n")
        typer.echo("✅ Файл requirements.txt создан")
    else:
        typer.echo("⚠️ Файл requirements.txt уже существует")

    create_git_ignore(project_dir)
    typer.echo(f"🎉 Проект {project_name} ({project_slug}) готов")
