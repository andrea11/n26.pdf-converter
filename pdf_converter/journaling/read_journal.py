import enum
import pandas as pd
import pathlib
import pdf_converter.columns as columns


class SupportedType(enum.Enum):
    csv = "csv"
    excel = "excel"
    json = "json"
    pickle = "pickle"
    parquet = "parquet"
    feather = "feather"
    hdf = "hdf"


def __validate_journal(journal: pd.DataFrame):
    """
    Validate the journal DataFrame.
    """
    required_columns = [
        columns.ExportableColumnHeaders.CATEGORY.value,
        columns.ExportableColumnHeaders.DATE.value,
    ]

    for required_column in required_columns:
        if required_column not in journal.columns:
            raise ValueError(
                f"Journal file must contain a column named '{required_column}'"
            )


def read(filepath: pathlib.Path) -> pd.DataFrame:
    """
    Read a journal file and return a pandas DataFrame.
    It tries multiple formats and encodings to read the file.
    """
    suffix = filepath.suffix.lstrip(".")

    try:
        if suffix not in [type.value for type in SupportedType]:
            raise ValueError(f"Unsupported file type: {suffix}")

        df = getattr(pd, f"read_{suffix}")(filepath)
    except Exception:
        raise ValueError(f"Could not read file {filepath}")

    __validate_journal(df)
    return df
