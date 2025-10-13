import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
    pluralize,
)


def make_model(name: str) -> None:
    """Сгенерировать файл модели SQLAlchemy."""
    path = BASE_DIR / "models"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_model.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    table_name = camel_to_snake(name)

    file_path.write_text(
        "from database import Base\n"
        "from sqlalchemy import Column, Integer, String, DateTime\n"
        "from sqlalchemy.sql import func\n"
        "from sqlalchemy.orm import relationship\n\n"
        f"class {name}(Base):\n"
        f"    __tablename__ = '{pluralize(table_name.lower())}'\n\n"
        f"    id = Column(Integer, primary_key=True, index=True)\n"
        f"    name = Column(String, index=True)\n"
        f"    created_at = Column(DateTime(timezone=True), server_default=func.now())\n"
        f"    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)\n"
    )
    typer.echo(f"✅ Модель {name} создана")
