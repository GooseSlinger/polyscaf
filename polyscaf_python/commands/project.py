from textwrap import dedent

import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import camel_to_snake, create_folder_with_init, create_git_ignore

FOLDERS = [
    "models",
    "schemas",
    "routes",
    "service",
    "database",
    "scripts",
]

BASE_REQUIREMENTS = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy",
    "alembic",
    "python-dotenv",
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
        "# например: postgresql+psycopg://user:password@localhost:5432/postgres\n"
        "SQL_BASE=postgresql+psycopg://user:password@localhost:5432/postgres\n"
        "SQL_DATABASE={database_name}\n"
    ),
}

MYSQL_DATABASE_TEMPLATE = dedent(
    """
    import os
    from typing import Optional

    from dotenv import load_dotenv
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine.url import URL, make_url
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import declarative_base

    load_dotenv()

    SQL_BASE = os.getenv("SQL_BASE")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    if not SQL_BASE:
        raise RuntimeError("Переменная SQL_BASE не установлена")


    def _resolve_database_url(sql_base: str, sql_database: Optional[str]) -> URL:
        parsed = make_url(sql_base)

        if parsed.drivername == "mysql":
            parsed = parsed.set(drivername="mysql+pymysql")

        if parsed.database:
            return parsed

        if not sql_database:
            raise RuntimeError("В SQL_BASE не указано имя базы и отсутствует SQL_DATABASE")

        return parsed.set(database=sql_database)


    def _to_async_database_url(sync_url: URL) -> URL:
        drivername = sync_url.drivername
        if drivername.startswith("mysql"):
            return sync_url.set(drivername="mysql+aiomysql")
        return sync_url


    def _get_async_engine_kwargs(database_url: URL) -> dict:
        if database_url.drivername.startswith("mysql"):
            return {"connect_args": {"init_command": "SET time_zone = '+03:00'"}}
        return {}


    SQLALCHEMY_DATABASE_SYNC_URL = _resolve_database_url(SQL_BASE, SQL_DATABASE)
    SQLALCHEMY_DATABASE_ASYNC_URL = _to_async_database_url(SQLALCHEMY_DATABASE_SYNC_URL)


    def _ensure_database_exists(database_url: URL) -> None:
        database_name = database_url.database

        if not database_name or not database_url.drivername.startswith("mysql"):
            return

        admin_url = database_url.set(database="")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

        try:
            with admin_engine.connect() as conn:
                identifier = f"`{database_name.replace('`', '``')}`"
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {identifier}"))
        finally:
            admin_engine.dispose()


    _ensure_database_exists(SQLALCHEMY_DATABASE_SYNC_URL)

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_ASYNC_URL,
        **_get_async_engine_kwargs(SQLALCHEMY_DATABASE_ASYNC_URL),
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    Base = declarative_base()


    async def get_db():
        db = AsyncSessionLocal()
        try:
            yield db
        finally:
            await db.close()
    """
).strip()

POSTGRES_DATABASE_TEMPLATE = dedent(
    """
    import os
    from typing import Optional

    from dotenv import load_dotenv
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine.url import URL, make_url
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import declarative_base

    load_dotenv()

    SQL_BASE = os.getenv("SQL_BASE")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    if not SQL_BASE:
        raise RuntimeError("Переменная SQL_BASE не установлена")


    def _resolve_database_url(sql_base: str, sql_database: Optional[str]) -> URL:
        parsed = make_url(sql_base)

        if parsed.drivername == "postgresql":
            parsed = parsed.set(drivername="postgresql+psycopg")

        if parsed.database:
            return parsed

        if not sql_database:
            raise RuntimeError("В SQL_BASE не указано имя базы и отсутствует SQL_DATABASE")

        return parsed.set(database=sql_database)


    def _to_async_database_url(sync_url: URL) -> URL:
        drivername = sync_url.drivername
        if drivername.startswith("postgresql"):
            return sync_url.set(drivername="postgresql+asyncpg")
        return sync_url


    SQLALCHEMY_DATABASE_SYNC_URL = _resolve_database_url(SQL_BASE, SQL_DATABASE)
    SQLALCHEMY_DATABASE_ASYNC_URL = _to_async_database_url(SQLALCHEMY_DATABASE_SYNC_URL)


    def _ensure_database_exists(database_url: URL) -> None:
        database_name = database_url.database

        if not database_name or not database_url.drivername.startswith("postgresql"):
            return

        admin_url = database_url.set(database="postgres")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

        try:
            with admin_engine.connect() as conn:
                exists = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": database_name},
                ).scalar()
                if not exists:
                    identifier = f'"{database_name.replace(\'"\', \'""\')}"'
                    conn.execute(text(f"CREATE DATABASE {identifier}"))
        finally:
            admin_engine.dispose()


    _ensure_database_exists(SQLALCHEMY_DATABASE_SYNC_URL)

    engine = create_async_engine(SQLALCHEMY_DATABASE_ASYNC_URL)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    Base = declarative_base()


    async def get_db():
        db = AsyncSessionLocal()
        try:
            yield db
        finally:
            await db.close()
    """
).strip()


def _build_main_template(project_name: str) -> str:
    return dedent(
        f"""
        from fastapi import FastAPI

        import database  # noqa: F401  # Инициализация БД при старте приложения.

        app = FastAPI(title="{project_name}")

        # Здесь подключайте свои роуты, когда начнёте добавлять модули.
        # from routes.user_route import router as user_router
        # app.include_router(user_router, prefix="/users", tags=["users"])

        @app.get("/")
        async def root():
            return {{"detail": "Hello World!"}}
        """
    ).strip()


def _build_database_template(db_engine: str) -> str:
    if db_engine == "mysql":
        return MYSQL_DATABASE_TEMPLATE
    return POSTGRES_DATABASE_TEMPLATE


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
        existed = path.exists()
        create_folder_with_init(path, is_database=(folder == "database"))
        if not existed:
            typer.echo(f"✅ Папка {folder} создана")
        else:
            typer.echo(f"⚠️ Папка {folder} уже существует")
        create_git_ignore(path)

    database_file = project_dir / "database" / "database.py"
    if not database_file.exists():
        database_file.write_text(_build_database_template(db_engine))
        typer.echo("✅ Файл database.py создан")
    else:
        typer.echo("⚠️ Файл database.py уже существует")

    main_file = project_dir / "main.py"
    if not main_file.exists():
        main_file.write_text(_build_main_template(project_name))
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

    root_ignore = project_dir / ".gitignore"
    if not root_ignore.exists():
        root_ignore.write_text(".env\n.venv\nvenv\n__pycache__/\n*.pyc\n")
        typer.echo("✅ Файл .gitignore создан")
    else:
        typer.echo("⚠️ Файл .gitignore уже существует")
    typer.echo(f"🎉 Проект {project_name} ({project_slug}) готов")
