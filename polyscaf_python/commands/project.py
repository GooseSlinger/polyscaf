from textwrap import dedent

import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import camel_to_snake, create_folder_with_init, create_git_ignore

FOLDERS = ["models", "schemas", "routes", "service", "database", "scripts"]
REQUIREMENTS = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy",
    "alembic",
    "python-dotenv",
    "aiomysql",
    "pymysql",
    "httpx2",
]
ENV_TEMPLATE = (
    "# SQL_BASE: адрес сервера MySQL без имени базы данных.\n"
    "# SQL_DATABASE: имя целевой базы для приложения и скрипта создания.\n"
    "SQL_BASE=mysql+pymysql://user:password@localhost:3306\n"
    "SQL_DATABASE={database_name}\n"
)

DATABASE_TEMPLATE = dedent(
    """
    import os
    from pathlib import Path

    from dotenv import load_dotenv
    from sqlalchemy.engine.url import make_url
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import declarative_base

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    SQL_BASE = os.getenv("SQL_BASE")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    if not SQL_BASE or not SQL_DATABASE:
        raise RuntimeError("Укажите SQL_BASE и SQL_DATABASE в .env")

    server_url = make_url(SQL_BASE)
    if server_url.drivername not in ("mysql", "mysql+pymysql") or server_url.database:
        raise RuntimeError("SQL_BASE должен быть адресом сервера MySQL без имени базы")

    SQLALCHEMY_DATABASE_SYNC_URL = server_url.set(
        drivername="mysql+pymysql", database=SQL_DATABASE
    )
    SQLALCHEMY_DATABASE_ASYNC_URL = SQLALCHEMY_DATABASE_SYNC_URL.set(
        drivername="mysql+aiomysql"
    )

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_ASYNC_URL,
        connect_args={"init_command": "SET time_zone = '+00:00'"},
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    Base = declarative_base()


    async def get_db():
        db = AsyncSessionLocal()
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()
    """
).strip()

CREATE_DATABASE_SCRIPT_TEMPLATE = dedent(
    """
    from pathlib import Path
    import sys

    from sqlalchemy import create_engine, text

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from database.database import SQLALCHEMY_DATABASE_SYNC_URL


    def main() -> None:
        database_name = SQLALCHEMY_DATABASE_SYNC_URL.database
        identifier = "`" + database_name.replace("`", "``") + "`"
        admin_url = SQLALCHEMY_DATABASE_SYNC_URL.set(database="")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        try:
            with admin_engine.connect() as connection:
                connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {identifier}"))
        finally:
            admin_engine.dispose()


    if __name__ == "__main__":
        main()
    """
).strip()


def _build_main_template(project_name: str) -> str:
    return dedent(
        f"""
        from fastapi import FastAPI

        app = FastAPI(title="{project_name}")

        # Подключайте маршруты по мере добавления модулей.
        # from routes.user_route import router as user_router
        # app.include_router(user_router, prefix="/users", tags=["users"])

        @app.get("/")
        async def root():
            return {{"detail": "Hello World!"}}
        """
    ).strip()


def make_project(
    project_name: str = typer.Argument(..., help="Название нового проекта в CamelCase."),
    mysql: bool = typer.Option(
        False,
        "-m",
        "--mysql",
        help="Необязательный флаг для совместимости со старыми вызовами.",
        is_flag=True,
    ),
) -> None:
    """Создать MySQL-каркас проекта в текущей директории."""
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
        typer.echo("❌ Используйте CamelCase для названия проекта (например: MyApp).")
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

    files = {
        project_dir / "database" / "database.py": DATABASE_TEMPLATE + "\n",
        project_dir / "scripts" / "create_database_script.py": CREATE_DATABASE_SCRIPT_TEMPLATE + "\n",
        project_dir / "main.py": _build_main_template(project_name) + "\n",
        project_dir / ".env": ENV_TEMPLATE.format(database_name=project_slug),
        project_dir / "requirements.txt": "\n".join(REQUIREMENTS) + "\n",
        project_dir / ".gitignore": ".env\n.venv\nvenv\n__pycache__/\n*.pyc\n",
    }
    for file_path, content in files.items():
        if file_path.exists():
            typer.echo(f"⚠️ Файл {file_path.name} уже существует")
        else:
            file_path.write_text(content)
            typer.echo(f"✅ Файл {file_path.name} создан")
    typer.echo(f"🎉 Проект {project_name} ({project_slug}) готов")
