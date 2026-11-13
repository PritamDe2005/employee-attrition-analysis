"""
Data loading and validation module.

Responsible for:
- Loading the raw employee attrition dataset.
- Validating the presence of expected columns.
- Providing basic dataset information.
"""

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    CSV_ENCODING,
    EXPECTED_COLUMNS,
    MANDATORY_COLUMNS,
    RAW_DATA_FILE,
    SUPPORTED_FILE_EXTENSIONS,
)


def load_dataset_from_source(
    source: Any,
    filename: str | None = None,
) -> pd.DataFrame:
    """
    Load an employee dataset from a file path, BytesIO, or uploaded file object.
    Supports CSV and Excel (.xlsx, .xls) files with automatic encoding fallbacks.

    Parameters
    ----------
    source : Path, str, BytesIO, or file-like object
        The data source to read.
    filename : str, optional
        Filename or path used to infer file extension if source is a stream.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.

    Raises
    ------
    FileNotFoundError
        If a file path does not exist.
    ValueError
        If the file format is unsupported, cannot be parsed, or is empty.
    """
    # Resolve name/extension
    inferred_name = ""
    if filename:
        inferred_name = str(filename)
    elif hasattr(source, "name"):
        inferred_name = str(source.name)
    elif isinstance(source, (str, Path)):
        inferred_name = str(source)

    lower_name = inferred_name.lower()
    if lower_name:
        ext = Path(lower_name).suffix
        if ext and ext not in SUPPORTED_FILE_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported formats are: {SUPPORTED_FILE_EXTENSIONS}"
            )

    is_excel = lower_name.endswith((".xlsx", ".xls"))
    is_csv = lower_name.endswith(".csv") or not is_excel

    # Handle path-based sources
    if isinstance(source, (str, Path)):
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

    # Read Excel
    if is_excel:
        try:
            dataframe = pd.read_excel(source)
        except Exception as error:
            raise ValueError(f"Unable to parse Excel dataset: {error}") from error
    else:
        # Read CSV with multi-encoding fallback
        encodings = [CSV_ENCODING, "utf-8-sig", "latin-1", "cp1252"]
        dataframe = None
        last_error = None

        for encoding in encodings:
            try:
                if hasattr(source, "seek"):
                    source.seek(0)
                dataframe = pd.read_csv(source, encoding=encoding)
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as err:
                last_error = err
                continue

        if dataframe is None:
            raise ValueError(
                f"Unable to parse CSV dataset. Failed with tested encodings: {last_error}"
            )

    if dataframe.empty:
        raise ValueError("The dataset is empty.")

    return dataframe


def validate_dynamic_schema(dataframe: pd.DataFrame) -> dict:
    """
    Validate that mandatory columns are present, ensure no unexpected extra entities/columns
    exist with respect to the sample CSV schema, and summarize present vs missing optional columns.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataset to check.

    Returns
    -------
    dict
        Dictionary containing:
        - "is_valid": bool
        - "mandatory_present": list[str]
        - "mandatory_missing": list[str]
        - "present_columns": list[str]
        - "missing_optional": list[str]
        - "extra_columns": list[str]

    Raises
    ------
    ValueError
        If any mandatory columns (e.g. Attrition) are missing or if unexpected extra entities are present.
    """
    actual_cols = set(dataframe.columns)
    mandatory_missing = [col for col in MANDATORY_COLUMNS if col not in actual_cols]

    if mandatory_missing:
        raise ValueError(
            "The dataset is missing mandatory column(s): "
            f"{mandatory_missing}. "
            "An 'Attrition' target column (or recognizable alias) is required."
        )

    # Detect any extra entities/columns not in the sample CSV schema
    extra_entities = sorted([col for col in dataframe.columns if col not in EXPECTED_COLUMNS])
    if extra_entities:
        raise ValueError(
            f"The uploaded dataset contains {len(extra_entities)} unexpected extra entity/column(s) "
            f"with respect to the sample CSV: {extra_entities}. "
            "The dataset must not contain any extra entities. "
            f"Allowed entities from the sample CSV are: {EXPECTED_COLUMNS}."
        )

    present_cols = [col for col in EXPECTED_COLUMNS if col in actual_cols]
    missing_optional = [col for col in EXPECTED_COLUMNS if col not in actual_cols]

    return {
        "is_valid": True,
        "mandatory_present": [col for col in MANDATORY_COLUMNS if col in actual_cols],
        "mandatory_missing": mandatory_missing,
        "present_columns": present_cols,
        "missing_optional": missing_optional,
        "extra_columns": [],
    }


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