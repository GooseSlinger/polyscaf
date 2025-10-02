import typer

from .factory import make_factory
from .model import make_model
from .project import make_project
from .route import make_route
from .schema import make_schema
from .script import make_script
from .service import make_service
from .test import make_test
from .util import make_util


def register(app: typer.Typer) -> None:
    """Подключить все команды Typer к переданному приложению."""
    app.command()(make_project)
    app.command()(make_model)
    app.command()(make_schema)
    app.command()(make_route)
    app.command()(make_service)
    app.command()(make_util)
    app.command()(make_factory)
    app.command()(make_script)
    app.command()(make_test)


__all__ = ["register"]
