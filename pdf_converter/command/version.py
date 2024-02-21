import typer
import pdf_converter.args

__version__ = "0.1.0"


def version_callback(value: bool):
    if value:
        print(f"Awesome CLI Version: {__version__}")
        raise typer.Exit()


@pdf_converter.args.app.callback()
def common(
    version: bool = typer.Option(
        None, "--version", help="Print version and exit.", callback=version_callback
    ),
):
    # Utility function to display the version of the CLI.
    pass
