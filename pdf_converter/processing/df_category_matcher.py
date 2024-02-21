import difflib
import pandas as pd
import pdf_converter.columns as columns


def match_category_with_journal(df: pd.DataFrame, journal: pd.DataFrame, threshold=0.8):
    for row in df.itertuples():
        for hist_row in journal.itertuples():
            ratio = compare_text(row.Payee, hist_row.Payee)
            if ratio > threshold:
                df.at[row.Index, columns.ExportableColumnHeaders.CATEGORY.value] = (
                    journal.at[
                        hist_row.Index, columns.ExportableColumnHeaders.CATEGORY.value
                    ]
                )

    return df


def compare_text(text1, text2):
    """
    Compare two texts and return the ratio of similarity
    """
    return difflib.SequenceMatcher(None, text1, text2).ratio()
