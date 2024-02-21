import pathlib
import typing
import pandas as pd
import rich
import rich.progress
import typer
import pdf_converter.journaling.read_journal
import pdf_converter.journaling.transform_journal
import pdf_converter.journaling.save_journal


@pdf_converter.args.app.command(
    name="journal", help="Import and process journal files."
)
def run(
    filepaths: typing.Annotated[
        list[pathlib.Path],
        typer.Argument(help="The path to the CSV file", show_default=False),
    ],
    output_file_path: typing.Annotated[
        pathlib.Path,
        typer.Argument(
            help="The path to the output file. The file extension will be overwritten by the output format.",
            show_default=False,
        ),
    ],
):
    """
    Import one or more journal files,
    process it to remove duplicates and summarize categories,
    and save the result to a new file.
    """
    if filepaths is None:
        rich.print("[error]At least one journal file is required[/error]")
        raise typer.Exit()

    if output_file_path is None:
        rich.print("[error]An output file path is required[/error]")
        raise typer.Exit()

    allowed_suffixes = [
        type.value for type in pdf_converter.journaling.read_journal.SupportedType
    ]
    suffix = output_file_path.suffix.lstrip(".")
    if suffix and suffix not in allowed_suffixes:
        rich.print(f"[error]Unsupported output file type: [i]{suffix}[/i][/error]")
        raise typer.Exit()

    suffix = suffix or pdf_converter.journaling.read_journal.SupportedType.feather.value

    df = __parse_input_files(filepaths)
    df = pdf_converter.journaling.transform_journal.cleanup(df)
    df = pdf_converter.journaling.transform_journal.compact(df)
    pdf_converter.journaling.save_journal.save(
        df, output_file_path.with_suffix(f".{suffix}")
    )


def __parse_input_files(filepaths: list[pathlib.Path]) -> pd.DataFrame:
    number_of_files = len(filepaths)
    loaded_files = 0
    failed_files = 0

    dfs: list[pd.DataFrame] = []

    with rich.progress.Progress() as progress:
        task = progress.add_task("Reading journal files...", total=number_of_files)

        for filepath in filepaths:
            try:
                df = pdf_converter.journaling.read_journal.read(filepath)
                loaded_files += 1
                dfs.append(df)
                progress.console.print(
                    f"Processed [b]{loaded_files}/{number_of_files}[/b]."
                )
            except ValueError as e:
                failed_files += 1
                progress.console.print(
                    f"[warning]Failed to process [b]{filepath}[/b]: {e}[/warning]"
                )
            progress.update(task, advance=1)

    if failed_files == 0:
        rich.print("[successful]All files were processed successfully[/successful]")
    if failed_files > 0:
        rich.print(
            f"Processed [b]{loaded_files}[/b] files. [warning]Failed to process [b]{failed_files}[/b] files.[/warning]"
        )

    if len(dfs) == 0:
        rich.print("[error]No files were processed[/error]")
        raise typer.Exit()

    return pd.concat(dfs, ignore_index=True)
