import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import (
    camel_to_snake,
    check_file_exists,
    create_folder_with_init,
    create_git_ignore,
)


def make_util(name: str) -> None:
    """Сгенерировать заглушку вспомогательного модуля."""
    path = BASE_DIR / "utils"
    create_folder_with_init(path)
    snake_name = camel_to_snake(name)
    file_path = path / f"{snake_name}_util.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(
        f"class {name}Util:\n"
        f"    \"\"\"Вспомогательные методы для {name}.\"\"\"\n\n"
        f"    @staticmethod\n"
        f"    def example() -> str:\n"
        f"        return '{name} util response'\n"
    )
    typer.echo(f"✅ Утилита {name} создана")
