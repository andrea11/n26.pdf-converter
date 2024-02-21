import pathlib
import typing

import typer
import pdf_converter.columns
import pdf_converter.args
import pdf_converter.processing.pdf_parser
import pdf_converter.processing.df_formatter
import pdf_converter.processing.df_category_matcher
import pdf_converter.journaling.read_journal


@pdf_converter.args.app.command(name="process")
def run(
    filepath: typing.Annotated[
        pathlib.Path,
        typer.Argument(show_default=False, help="The path to the PDF file"),
    ],
    output_file_path: typing.Annotated[
        typing.Optional[pathlib.Path],
        typer.Option(
            "--output-file-path",
            "-o",
            help="The path to the output CSV file. Defaults to the input file path with a .csv extension.",
            show_default=False,
        ),
    ] = None,
    journal_filepath: typing.Annotated[
        typing.Optional[pathlib.Path],
        typer.Option("--journal-filepath", "-j", show_default=False),
    ] = None,
    columns: typing.Annotated[
        list[pdf_converter.columns.ExportableColumnHeaders],
        typer.Option(
            "--columns", "-cols", help="The columns to use in the output CSV file."
        ),
    ] = [column.value for column in pdf_converter.columns.ExportableColumnHeaders],
):
    if output_file_path is None:
        output_file_path = filepath.with_suffix(".csv")

    df = pdf_converter.processing.pdf_parser.read_pdf(filepath)
    df = pdf_converter.processing.df_formatter.format(df)
    df = pdf_converter.processing.df_formatter.rearrange_columns(df, columns)

    if journal_filepath is not None and journal_filepath.exists():
        df_journal = pdf_converter.journaling.read_journal.read(journal_filepath)
        df = pdf_converter.processing.df_category_matcher.match_category_with_journal(
            df, df_journal
        )

    df.to_csv(output_file_path, index=False)
