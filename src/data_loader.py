"""
Data loading and validation module.

Responsible for:
- Loading the raw employee attrition dataset.
- Validating the presence of expected columns.
- Providing basic dataset information.
"""

from pathlib import Path

import pandas as pd

from config import (
    CSV_ENCODING,
    EXPECTED_COLUMNS,
    RAW_DATA_FILE,
)


def load_dataset(file_path: Path = RAW_DATA_FILE) -> pd.DataFrame:
    """
    Load the employee attrition dataset from a CSV file.

    Parameters
    ----------
    file_path : Path
        Path to the raw CSV dataset.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.

    Raises
    ------
    FileNotFoundError
        If the dataset file does not exist.
    ValueError
        If the CSV file cannot be loaded or is empty.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    try:
        dataframe = pd.read_csv(
    file_path,
    encoding=CSV_ENCODING,
)
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(
            f"Unable to parse dataset: {file_path}"
        ) from error

    if dataframe.empty:
        raise ValueError(
            f"The dataset is empty: {file_path}"
        )

    return dataframe


def validate_columns(
    dataframe: pd.DataFrame,
    expected_columns: list[str] = EXPECTED_COLUMNS,
) -> None:
    """
    Validate that the dataset contains all expected columns.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to validate.

    expected_columns : list[str]
        Columns required by the project.

    Raises
    ------
    ValueError
        If one or more expected columns are missing.
    """
    actual_columns = set(dataframe.columns)
    expected_column_set = set(expected_columns)

    missing_columns = sorted(
        expected_column_set - actual_columns
    )

    if missing_columns:
        raise ValueError(
            "The dataset is missing required columns: "
            f"{missing_columns}"
        )


def get_dataset_info(dataframe: pd.DataFrame) -> dict:
    """
    Return basic information about the loaded dataset.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to inspect.

    Returns
    -------
    dict
        Basic dataset statistics.
    """
    return {
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "missing_cells": int(dataframe.isna().sum().sum()),
        "duplicate_rows": int(dataframe.duplicated().sum()),
    }


def load_and_validate_dataset(
    file_path: Path = RAW_DATA_FILE,
) -> pd.DataFrame:
    """
    Load the dataset and validate its required columns.

    Parameters
    ----------
    file_path : Path
        Path to the raw CSV dataset.

    Returns
    -------
    pd.DataFrame
        Validated dataset.
    """
    dataframe = load_dataset(file_path)
    validate_columns(dataframe)

    return dataframe