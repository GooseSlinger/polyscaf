from importlib.metadata import version

import typer

from polyscaf_python.commands import register

app = typer.Typer(
    help=(
        "polyscaf: генератор заготовок для FastAPI-проектов.\n\n"
        "Примеры:\n"
        "  polyscaf make-project MyApp\n"
        "  polyscaf make-service User --with msr\n\n"
        "make-service --with:\n"
        "  m = model\n"
        "  s = schema\n"
        "  r = route"
    )
)
register(app)


@app.callback(invoke_without_command=True)
def show_version(
    ctx: typer.Context,
    version_flag: bool = typer.Option(
        False, "--version", help="Показать установленную версию polyscaf.", is_eager=True
    ),
) -> None:
    if version_flag:
        typer.echo(f"polyscaf {version('polyscaf')}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


def main() -> None:
    """Точка входа CLI-приложения polyscaf."""
    app()


if __name__ == "__main__":
    main()
