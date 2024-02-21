import re
import numpy as np
import pandas as pd
import pdf_converter.columns as columns


def join_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Join rows that are split across multiple rows in the original PDF.
    It joins all rows in-between two rows with a date in the second column.
    """
    new_df = pd.DataFrame()
    temp_row = []
    for row in df.itertuples(index=False):
        if (
            pd.to_datetime(row[1], errors="coerce", format="%d.%m.%Y") is not pd.NaT
            and temp_row
        ):
            new_df = pd.concat([new_df, pd.DataFrame([temp_row])], ignore_index=True)
            temp_row = list(row)
        else:
            temp_row.extend(row)
    new_df = pd.concat([new_df, pd.DataFrame([temp_row])], ignore_index=True)
    return new_df


def rearrange_columns(
    df: pd.DataFrame, columns: list[columns.ExportableColumnHeaders]
) -> pd.DataFrame:
    """
    Rearrange the columns in the DataFrame.
    """
    return df[[columns.value for columns in columns]]


def format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the DataFrame to match the expected output.
    """
    headers = [
        columns.ExportableColumnHeaders.PAYEE.value,
        columns.ExportableColumnHeaders.DATE.value,
        columns.ExportableColumnHeaders.AMOUNT.value,
        columns.ExportableColumnHeaders.TRANSACTION_TYPE.value,
        columns.InternalColumnHeaders.ACCOUNT_NAME_OR_ORIGINAL_AMOUNT.value,
        columns.ExportableColumnHeaders.NOTE.value,
    ]
    df = join_rows(df)
    df = __cleanup_columns(df, headers)
    df.columns = headers

    __format_date_column(df)
    __extract_category_column(df)
    __extract_transaction_type_column(df)
    __format_amount_column(df)
    __process_account_name_or_original_amount(df)
    return df


def __process_account_name_or_original_amount(df: pd.DataFrame) -> pd.DataFrame:
    __extract_iban_and_bic(df)
    __extract_original_amount_and_currency(df)

    df.drop(
        columns=[columns.InternalColumnHeaders.ACCOUNT_NAME_OR_ORIGINAL_AMOUNT.value],
        inplace=True,
    )


def __extract_category_column(df: pd.DataFrame):
    df[columns.ExportableColumnHeaders.CATEGORY.value] = df[
        columns.ExportableColumnHeaders.TRANSACTION_TYPE.value
    ].str.split(" â¢ ", expand=True)[1]

    df.loc[
        df[columns.ExportableColumnHeaders.TRANSACTION_TYPE.value].isin(
            ["Income", "Direct Debits"]
        ),
        columns.ExportableColumnHeaders.CATEGORY.value,
    ] = np.nan


def __extract_transaction_type_column(df: pd.DataFrame):
    df[columns.ExportableColumnHeaders.TRANSACTION_TYPE.value] = df[
        columns.ExportableColumnHeaders.TRANSACTION_TYPE.value
    ].str.split(" â¢ ", expand=True)[0]

    df.loc[
        df[columns.ExportableColumnHeaders.TRANSACTION_TYPE.value].isin(
            ["Income", "Direct Debits"]
        ),
        columns.ExportableColumnHeaders.TRANSACTION_TYPE.value,
    ] = np.nan


def __format_amount_column(df: pd.DataFrame):
    df[columns.ExportableColumnHeaders.AMOUNT.value] = (
        df[columns.ExportableColumnHeaders.AMOUNT.value]
        .str.replace("â¬", "")
        .str.replace(".", "")
        .str.replace(",", ".")
        .astype(float)
    )


def __extract_iban_and_bic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract IBAN and BIC from the 'Account name or original amount' column.
    """
    extract_iban_bic = np.nan
    if (
        df[columns.InternalColumnHeaders.ACCOUNT_NAME_OR_ORIGINAL_AMOUNT.value]
        .str.contains("IBAN")
        .any()
    ):
        extract_iban_bic = df[
            columns.InternalColumnHeaders.ACCOUNT_NAME_OR_ORIGINAL_AMOUNT.value
        ].str.extract(r"IBAN: ([\w\d]{0,30}) .+? BIC: ([\w\d]+)")

    df[
        [
            columns.ExportableColumnHeaders.IBAN.value,
            columns.ExportableColumnHeaders.BIC.value,
        ]
    ] = extract_iban_bic


def __extract_original_amount_and_currency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract original amount and currency from the 'Account name or original amount' column.
    """

    if (
        df[columns.InternalColumnHeaders.ACCOUNT_NAME_OR_ORIGINAL_AMOUNT.value]
        .str.contains("Original amount")
        .any()
    ):
        df[
            [
                columns.ExportableColumnHeaders.ORIGINAL_AMOUNT.value,
                columns.ExportableColumnHeaders.ORIGINAL_CURRENCY.value,
                columns.ExportableColumnHeaders.FX_RATE.value,
            ]
        ] = df[
            columns.InternalColumnHeaders.ACCOUNT_NAME_OR_ORIGINAL_AMOUNT.value
        ].str.extract(
            r"Original amount.? ([\d\.]+) (\w+?) .*? Exchange rate.? ([\d\.]+)",
            re.IGNORECASE,
        )
    else:
        df[columns.ExportableColumnHeaders.ORIGINAL_CURRENCY.value] = "EUR"
        df[columns.ExportableColumnHeaders.ORIGINAL_AMOUNT.value] = df[
            columns.ExportableColumnHeaders.AMOUNT.value
        ]
        df[columns.ExportableColumnHeaders.FX_RATE.value] = 1.0


def __cleanup_columns(df: pd.DataFrame, headers: list[str]) -> pd.DataFrame:
    """
    Remove empty columns and columns that are not in the headers list.
    """
    df = df.dropna(how="all", axis=1)
    df = df.drop(columns=list(df.columns[len(headers) :]))
    return df


def __format_date_column(df: pd.DataFrame):
    """
    Format the date column to mm/dd/yyyy.
    """
    df[columns.ExportableColumnHeaders.DATE.value] = pd.to_datetime(
        df[columns.ExportableColumnHeaders.DATE.value],
        format="%d.%m.%Y",
    ).dt.strftime("%m/%d/%Y")
