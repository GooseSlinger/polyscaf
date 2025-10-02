import typer

from polyscaf_python.settings import BASE_DIR
from polyscaf_python.utils import check_file_exists, create_folder_with_init, create_git_ignore


def make_util(name: str) -> None:
    """Сгенерировать заглушку вспомогательного модуля."""
    path = BASE_DIR / "utils"
    create_folder_with_init(path)
    file_path = path / f"{name}Util.py"
    check_file_exists(file_path)
    create_git_ignore(path)

    file_path.write_text(f"# Util {name}")
    typer.echo(f"✅ Утилита {name} создана")
