import logging

import numpy as np
import pandas as pd

from config import (
    CATEGORICAL_COLUMNS,
    EDUCATION_MAPPING,
    FLEXIBLE_ATTRITION_MAPPING,
    ID_COLUMN,
    NUMERICAL_COLUMNS,
    SATISFACTION_COLUMNS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Categorical standardization
# ---------------------------------------------------------------------------

def standardize_categorical_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize categorical values by removing unnecessary whitespace,
    normalizing known variations, and keeping category labels consistent.
    """
    cleaned_dataframe = dataframe.copy()

    categorical_columns = [
        column
        for column in CATEGORICAL_COLUMNS
        if column in cleaned_dataframe.columns
    ]

    for column in categorical_columns:
        cleaned_dataframe[column] = (
            cleaned_dataframe[column]
            .astype("string")
            .str.strip()
        )

    # Known variations introduced by the raw dataset.
    replacements = {
        "Gender": {
            "male": "Male",
            "MALE": "Male",
            "female": "Female",
            "FEMALE": "Female",
        },
        "Department": {
            "hr": "Human Resources",
            "HR": "Human Resources",
            "human resources": "Human Resources",
            "research & development": "Research & Development",
            "Research & development": "Research & Development",
            "Research and Development": "Research & Development",
            "sales": "Sales",
        },
        "OverTime": {
            "yes": "Yes",
            "YES": "Yes",
            "no": "No",
            "NO": "No",
        },
        "Attrition": {
            "yes": "Yes",
            "YES": "Yes",
            "no": "No",
            "NO": "No",
        },
    }

    for column, mapping in replacements.items():
        if column in cleaned_dataframe.columns:
            cleaned_dataframe[column] = (
                cleaned_dataframe[column]
                .replace(mapping)
            )

    # Flexible normalization for Attrition (Yes/No, 1/0, True/False, Left/Stayed)
    if "Attrition" in cleaned_dataframe.columns:
        attrition_norm = (
            cleaned_dataframe["Attrition"]
            .astype("string")
            .str.strip()
            .str.lower()
        )
        mapped_target = attrition_norm.map(FLEXIBLE_ATTRITION_MAPPING)
        cleaned_dataframe["Attrition"] = mapped_target.fillna(
            cleaned_dataframe["Attrition"]
        )

    return cleaned_dataframe


# ---------------------------------------------------------------------------
# Data type conversion
# ---------------------------------------------------------------------------

def convert_data_types(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Convert configured numerical columns to numeric data types.

    Invalid numeric strings are converted to NaN so that they can be
    handled by the missing-value processing stage.
    """
    cleaned_dataframe = dataframe.copy()

    # Map text education degrees to ordinal integers if string values exist
    if "Education" in cleaned_dataframe.columns:
        cleaned_dataframe["Education"] = (
            cleaned_dataframe["Education"].replace(EDUCATION_MAPPING)
        )

    for column in NUMERICAL_COLUMNS:
        if column in cleaned_dataframe.columns:
            cleaned_dataframe[column] = pd.to_numeric(
                cleaned_dataframe[column],
                errors="coerce",
            )

    if ID_COLUMN in cleaned_dataframe.columns:
        cleaned_dataframe[ID_COLUMN] = pd.to_numeric(
            cleaned_dataframe[ID_COLUMN],
            errors="coerce",
        )

    return cleaned_dataframe


# ---------------------------------------------------------------------------
# Duplicate handling
# ---------------------------------------------------------------------------

def remove_duplicate_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Remove exact duplicate rows from the dataset.
    """
    cleaned_dataframe = dataframe.copy()

    duplicate_count = int(cleaned_dataframe.duplicated().sum())

    if duplicate_count:
        logger.info(
            "Removing %d exact duplicate rows.",
            duplicate_count,
        )

        cleaned_dataframe = cleaned_dataframe.drop_duplicates(
            keep="first"
        )

    return cleaned_dataframe


def remove_duplicate_employee_ids(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove duplicate EmployeeID records.

    The first occurrence of an EmployeeID is retained.
    """
    cleaned_dataframe = dataframe.copy()

    if ID_COLUMN not in cleaned_dataframe.columns:
        return cleaned_dataframe

    duplicate_id_mask = cleaned_dataframe[ID_COLUMN].duplicated(
        keep="first"
    )

    duplicate_id_count = int(duplicate_id_mask.sum())

    if duplicate_id_count:
        logger.warning(
            "Found %d duplicate %s records. "
            "Keeping the first occurrence.",
            duplicate_id_count,
            ID_COLUMN,
        )

        cleaned_dataframe = cleaned_dataframe.loc[
            ~duplicate_id_mask
        ].copy()

    return cleaned_dataframe


# ---------------------------------------------------------------------------
# Invalid numerical values
# ---------------------------------------------------------------------------

def handle_invalid_numerical_values(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Replace impossible or suspicious numerical values with NaN.

    The ranges are based on the HR attributes represented in the project
    dataset and are kept here as explicit validation rules.
    """
    cleaned_dataframe = dataframe.copy()

    def replace_invalid(
        column: str,
        condition: pd.Series,
    ) -> None:
        """Replace values matching a condition with NaN."""
        if column not in cleaned_dataframe.columns:
            return

        invalid_count = int(condition.sum())

        if invalid_count:
            logger.info(
                "Replacing %d invalid values in %s with NaN.",
                invalid_count,
                column,
            )

            cleaned_dataframe.loc[condition, column] = np.nan

    # Age
    if "Age" in cleaned_dataframe.columns:
        replace_invalid(
            "Age",
            (cleaned_dataframe["Age"] < 18)
            | (cleaned_dataframe["Age"] > 65),
        )

    # Monthly income
    if "MonthlyIncome" in cleaned_dataframe.columns:
        replace_invalid(
            "MonthlyIncome",
            cleaned_dataframe["MonthlyIncome"] <= 0,
        )

    # Distance from home
    if "DistanceFromHome" in cleaned_dataframe.columns:
        replace_invalid(
            "DistanceFromHome",
            cleaned_dataframe["DistanceFromHome"] < 1,
        )

    # Non-negative HR metrics
    non_negative_columns = [
        "TrainingTimesLastYear",
        "YearsAtCompany",
        "YearsInCurrentRole",
        "TotalWorkingYears",
        "NumCompaniesWorked",
        "NumProjects",
        "AverageWeeklyHours",
    ]

    for column in non_negative_columns:
        if column in cleaned_dataframe.columns:
            replace_invalid(
                column,
                cleaned_dataframe[column] < 0,
            )

    # Satisfaction scores
    for column in SATISFACTION_COLUMNS:
        if column in cleaned_dataframe.columns:
            replace_invalid(
                column,
                (cleaned_dataframe[column] < 1)
                | (cleaned_dataframe[column] > 4),
            )

    # Education level (1-5)
    if "Education" in cleaned_dataframe.columns:
        replace_invalid(
            "Education",
            (cleaned_dataframe["Education"] < 1)
            | (cleaned_dataframe["Education"] > 5),
        )

    # Job level
    if "JobLevel" in cleaned_dataframe.columns:
        replace_invalid(
            "JobLevel",
            (cleaned_dataframe["JobLevel"] < 1)
            | (cleaned_dataframe["JobLevel"] > 5),
        )

    # Performance rating
    if "PerformanceRating" in cleaned_dataframe.columns:
        replace_invalid(
            "PerformanceRating",
            (cleaned_dataframe["PerformanceRating"] < 1)
            | (cleaned_dataframe["PerformanceRating"] > 5),
        )

    return cleaned_dataframe


# ---------------------------------------------------------------------------
# Missing-value handling
# ---------------------------------------------------------------------------

def handle_missing_target(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Handle missing Attrition values.

    Attrition is the target variable, so missing target labels are removed
    rather than imputed with the most common class.
    """
    cleaned_dataframe = dataframe.copy()

    if "Attrition" not in cleaned_dataframe.columns:
        return cleaned_dataframe

    missing_target_count = int(
        cleaned_dataframe["Attrition"].isna().sum()
    )

    if missing_target_count:
        logger.warning(
            "Removing %d rows with missing Attrition labels.",
            missing_target_count,
        )

        cleaned_dataframe = cleaned_dataframe.dropna(
            subset=["Attrition"]
        )

    return cleaned_dataframe


def handle_missing_values(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fill missing feature values.

    Numerical columns use the median.
    Categorical columns use the mode.

    Attrition is excluded because it is the target variable and is handled
    separately.
    """
    cleaned_dataframe = dataframe.copy()

    # Numerical feature imputation
    for column in NUMERICAL_COLUMNS:
        if column not in cleaned_dataframe.columns:
            continue

        missing_count = int(
            cleaned_dataframe[column].isna().sum()
        )

        if missing_count:
            median_value = cleaned_dataframe[column].median()

            if pd.isna(median_value):
                logger.warning(
                    "Unable to calculate median for %s.",
                    column,
                )
                continue

            cleaned_dataframe[column] = (
                cleaned_dataframe[column]
                .fillna(median_value)
            )

            logger.info(
                "Filled %d missing values in %s using median.",
                missing_count,
                column,
            )

    # Categorical feature imputation
    categorical_feature_columns = [
        column
        for column in CATEGORICAL_COLUMNS
        if column != "Attrition"
        and column in cleaned_dataframe.columns
    ]

    for column in categorical_feature_columns:
        missing_count = int(
            cleaned_dataframe[column].isna().sum()
        )

        if not missing_count:
            continue

        mode_values = cleaned_dataframe[column].mode(
            dropna=True
        )

        if mode_values.empty:
            logger.warning(
                "Unable to calculate mode for %s.",
                column,
            )
            continue

        mode_value = mode_values.iloc[0]

        cleaned_dataframe[column] = (
            cleaned_dataframe[column]
            .fillna(mode_value)
        )

        logger.info(
            "Filled %d missing values in %s using mode.",
            missing_count,
            column,
        )

    return cleaned_dataframe


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_cleaned_data(
    dataframe: pd.DataFrame,
) -> None:
    """
    Validate that the cleaned dataset satisfies the project's
    basic data-quality requirements.
    """
    if dataframe.empty:
        raise ValueError(
            "The cleaned dataset is empty."
        )

    missing_cells = int(
        dataframe.isna().sum().sum()
    )

    if missing_cells:
        missing_columns = (
            dataframe.isna()
            .sum()
            .loc[lambda values: values > 0]
            .to_dict()
        )

        raise ValueError(
            "Missing values remain after preprocessing: "
            f"{missing_columns}"
        )

    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    if duplicate_rows:
        raise ValueError(
            f"{duplicate_rows} duplicate rows remain after preprocessing."
        )

    if ID_COLUMN in dataframe.columns:
        duplicate_employee_ids = int(
            dataframe[ID_COLUMN].duplicated().sum()
        )

        if duplicate_employee_ids:
            raise ValueError(
                f"{duplicate_employee_ids} duplicate {ID_COLUMN} values "
                "remain after preprocessing."
            )

    if "Attrition" in dataframe.columns:
        invalid_attrition_values = set(
            dataframe["Attrition"].dropna().unique()
        ) - {"Yes", "No"}

        if invalid_attrition_values:
            raise ValueError(
                "Unexpected Attrition values found: "
                f"{sorted(invalid_attrition_values)}"
            )

    logger.info(
        "Cleaned dataset validation completed successfully."
    )


# ---------------------------------------------------------------------------
# Complete preprocessing pipeline
# ---------------------------------------------------------------------------

def preprocess_dataset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Execute the complete employee attrition preprocessing pipeline.

    Processing order:
        1. Standardize categorical values
        2. Convert data types
        3. Remove exact duplicate rows
        4. Remove duplicate EmployeeIDs
        5. Handle invalid numerical values
        6. Handle missing Attrition labels
        7. Impute missing feature values
        8. Validate the cleaned dataset
    """
    logger.info(
        "Starting data preprocessing: %d rows, %d columns.",
        len(dataframe),
        len(dataframe.columns),
    )

    cleaned_dataframe = standardize_categorical_values(
        dataframe
    )

    cleaned_dataframe = convert_data_types(
        cleaned_dataframe
    )

    cleaned_dataframe = remove_duplicate_rows(
        cleaned_dataframe
    )

    cleaned_dataframe = remove_duplicate_employee_ids(
        cleaned_dataframe
    )

    cleaned_dataframe = handle_invalid_numerical_values(
        cleaned_dataframe
    )

    cleaned_dataframe = handle_missing_target(
        cleaned_dataframe
    )

    cleaned_dataframe = handle_missing_values(
        cleaned_dataframe
    )

    validate_cleaned_data(
        cleaned_dataframe
    )

    logger.info(
        "Preprocessing completed: %d rows, %d columns.",
        len(cleaned_dataframe),
        len(cleaned_dataframe.columns),
    )

    return cleaned_dataframe