import difflib
import pandas as pd
import pdf_converter.columns as columns


def cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean up the DataFrame by selecting the relevant columns, removing rows with empty values, duplicate rows, and keeping only the most recent row for each payee.
    """
    df = df[
        [
            columns.ExportableColumnHeaders.PAYEE.value,
            columns.ExportableColumnHeaders.DATE.value,
            columns.ExportableColumnHeaders.CATEGORY.value,
        ]
    ]
    df = df.dropna(how="all")
    df = df.drop_duplicates()
    df = df.sort_values(
        columns.ExportableColumnHeaders.DATE.value, ascending=False
    ).drop_duplicates(columns.ExportableColumnHeaders.PAYEE.value)
    df = df.reset_index(drop=True)
    return df


def compact(df: pd.DataFrame, threshold=0.8) -> pd.DataFrame:
    """
    Compact the DataFrame by removing rows with similar payees.
    The most recent row is kept.
    """

    # Initialize an empty DataFrame to store the filtered rows
    filtered_df = pd.DataFrame()

    # Initialize a set to store the indices of the rows that have been processed
    processed_indices = set()

    # Iterate over the DataFrame row by row
    for row in df.itertuples():
        # Skip this row if it has been processed
        if row.Index in processed_indices:
            continue

        # Compute the similarity ratio for every other row
        similarity_ratios = df[columns.ExportableColumnHeaders.PAYEE.value].apply(
            lambda x: compare_text(
                getattr(row, columns.ExportableColumnHeaders.PAYEE.value), x
            )
        )

        # Get the indices where the similarity ratio is greater than the threshold
        above_threshold_indices = similarity_ratios[similarity_ratios > threshold].index

        # If there are any rows above the threshold, compare their date and keep only the most recent one
        if not above_threshold_indices.empty:
            most_recent_row = (
                df.loc[above_threshold_indices]
                .sort_values(
                    columns.ExportableColumnHeaders.DATE.value, ascending=False
                )
                .iloc[0]
            )
            filtered_df = pd.concat([filtered_df, pd.DataFrame([most_recent_row])])

            # Add the index of the most recent row to processed_indices
            processed_indices.update(above_threshold_indices)

    # Reset the index of the filtered DataFrame
    filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df


def compare_text(text1, text2):
    """
    Compare two texts and return the ratio of similarity
    """
    return difflib.SequenceMatcher(None, text1, text2).ratio()
