import typer

from polyscaf_python.commands import register

app = typer.Typer(help="polyscaf: генератор заготовок для FastAPI-проектов.")
register(app)


def main() -> None:
    """Точка входа CLI-приложения polyscaf."""
    app()


if __name__ == "__main__":
    main()
