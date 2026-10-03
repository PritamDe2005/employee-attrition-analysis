"""
Utility functions for the Employee Attrition Analysis project.

This module contains reusable helpers for:
- Creating project directories
- Configuring application logging
- Saving analysis tables
"""

import logging
from pathlib import Path

import pandas as pd


def create_project_directories(
    directories: list[Path],
) -> None:
    """
    Create project directories if they do not already exist.

    Parameters
    ----------
    directories : list[Path]
        Directories that should exist before the application runs.
    """
    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


def configure_logging(
    level: int = logging.INFO,
) -> None:
    """
    Configure application-wide logging.

    Parameters
    ----------
    level : int
        Logging level used by the application.
    """
    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def save_dataframe(
    dataframe: pd.DataFrame,
    output_directory: Path,
    filename: str,
) -> Path:
    """
    Save a DataFrame as a CSV file.

    Parameters
    ----------
    dataframe : pd.DataFrame
        DataFrame to save.

    output_directory : Path
        Directory where the CSV should be saved.

    filename : str
        Output filename.

    Returns
    -------
    Path
        Path of the saved CSV file.
    """
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_directory / filename

    dataframe.to_csv(
        output_path,
        index=False,
    )

    return output_path