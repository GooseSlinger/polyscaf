import typer

from polyscaf_python.commands import register

app = typer.Typer(
    help=(
        "polyscaf: генератор заготовок для FastAPI-проектов.\n\n"
        "Примеры:\n"
        "  polyscaf make-service User --with mr\n\n"
        "make-service --with:\n"
        "  m = model\n"
        "  s = schema\n"
        "  r = route"
    )
)
register(app)


def main() -> None:
    """Точка входа CLI-приложения polyscaf."""
    app()


if __name__ == "__main__":
    main()
