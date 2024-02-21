import typer
import rich.console
import rich.theme

app = typer.Typer(no_args_is_help=True)

rich.reconfigure(
    theme=rich.theme.Theme(
        {
            "critical": "bold reverse red",
            "debug": "green",
            "error": "bold red",
            "info": "blue",
            "notset": "dim",
            "warning": "red",
        }
    )
)
