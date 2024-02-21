import pathlib
import pandas as pd
import tabula
import os


def read_pdf(filepath: pathlib.Path) -> pd.DataFrame:
    """
    Read a PDF file and return a pandas DataFrame.
    """
    df_list = tabula.read_pdf(
        input_path=filepath,
        pages="all",
        pandas_options={"header": None},
        encoding="ISO-8859-1",
        stream=True,
    )

    df = pd.concat(df_list)

    return df
