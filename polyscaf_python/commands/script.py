import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_script(name: str) -> None:
    """Сгенерировать заготовку скрипта."""
    path = BASE_DIR / "scripts"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_script.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        f"def run_{snake_name}_script() -> None:\n"
        f"    \"\"\"Реализуйте здесь логику скрипта {name}.\"\"\"\n"
        "    pass\n\n"
    )
    typer.echo(f"✅ Скрипт {name} создан")
