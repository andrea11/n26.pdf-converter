import pandas as pd
import pathlib
from pdf_converter.journaling import read_journal


def save(df: pd.DataFrame, filepath: pathlib.Path):
    """
    Read a journal file and return a pandas DataFrame.
    It tries multiple formats and encodings to read the file.
    """
    suffix = filepath.suffix.lstrip(".")

    try:
        if suffix not in [type.value for type in read_journal.SupportedType]:
            raise ValueError(f"Unsupported file type: {suffix}")
        getattr(df, f"to_{suffix}")(filepath)
    except Exception as e:
        raise ValueError(
            f"Could not save file {filepath}: {e}",
        )
