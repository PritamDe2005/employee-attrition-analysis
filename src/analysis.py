"""
Analysis module for Employee Attrition Analysis.

This module contains reusable functions for:
- Attrition distribution
- Department analysis
- Job role analysis
- Salary-band analysis
- Age-group analysis
- Tenure analysis
- Satisfaction analysis
- Overtime analysis
- Correlation analysis
"""

import pandas as pd

from config import (
    AGE_BINS,
    AGE_LABELS,
    ATTRITION_BINARY_MAPPING,
    ID_COLUMN,
    SALARY_BINS,
    SALARY_LABELS,
    SATISFACTION_COLUMNS,
    TENURE_BINS,
    TENURE_LABELS,
)


# ---------------------------------------------------------------------------
# General helper
# ---------------------------------------------------------------------------

def calculate_attrition_rate(
    dataframe: pd.DataFrame,
    group_column: str,
) -> pd.DataFrame:
    """
    Calculate employee count, attrition count, and attrition rate
    for a specified categorical column.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Cleaned employee dataset.

    group_column : str
        Column used to group employees.

    Returns
    -------
    pd.DataFrame
        Grouped attrition statistics.
    """
    if group_column not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    count_col = ID_COLUMN if ID_COLUMN in dataframe.columns else "Attrition"

    result = (
        dataframe.groupby(group_column, dropna=False)
        .agg(
            EmployeeCount=(count_col, "count"),
            AttritionCount=(
                "Attrition",
                lambda values: (values == "Yes").sum(),
            ),
        )
        .reset_index()
    )

    result["AttritionRate"] = (
        result["AttritionCount"]
        / result["EmployeeCount"]
        * 100
    )

    result["AttritionRate"] = result["AttritionRate"].round(2)

    return result


# ---------------------------------------------------------------------------
# Attrition distribution
# ---------------------------------------------------------------------------

def analyze_attrition_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the overall employee attrition distribution.

    Returns
    -------
    pd.DataFrame
        Attrition count and percentage.
    """
    result = (
        dataframe["Attrition"]
        .value_counts(dropna=False)
        .rename_axis("Attrition")
        .reset_index(name="EmployeeCount")
    )

    total_employees = len(dataframe)

    result["Percentage"] = (
        result["EmployeeCount"]
        / total_employees
        * 100
    ).round(2)

    return result


# ---------------------------------------------------------------------------
# Department analysis
# ---------------------------------------------------------------------------

def analyze_department(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze employee attrition across departments.

    Includes:
    - Employee count
    - Attrition count
    - Attrition percentage
    - Average monthly income (if available)
    - Average job satisfaction (if available)
    """
    if "Department" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    count_col = ID_COLUMN if ID_COLUMN in dataframe.columns else "Attrition"
    agg_dict: dict = {
        "EmployeeCount": (count_col, "count"),
        "AttritionCount": (
            "Attrition",
            lambda values: (values == "Yes").sum(),
        ),
    }

    if "MonthlyIncome" in dataframe.columns:
        agg_dict["AverageMonthlyIncome"] = ("MonthlyIncome", "mean")
    if "JobSatisfaction" in dataframe.columns:
        agg_dict["AverageJobSatisfaction"] = ("JobSatisfaction", "mean")

    result = dataframe.groupby("Department").agg(**agg_dict).reset_index()

    result["AttritionRate"] = (
        result["AttritionCount"]
        / result["EmployeeCount"]
        * 100
    ).round(2)

    if "AverageMonthlyIncome" in result.columns:
        result["AverageMonthlyIncome"] = (
            result["AverageMonthlyIncome"].round(2)
        )

    if "AverageJobSatisfaction" in result.columns:
        result["AverageJobSatisfaction"] = (
            result["AverageJobSatisfaction"].round(2)
        )

    return result


# ---------------------------------------------------------------------------
# Job role analysis
# ---------------------------------------------------------------------------

def analyze_job_role(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze employee attrition across job roles.

    Includes:
    - Employee count
    - Attrition count
    - Attrition rate
    - Average monthly income (if available)
    """
    if "JobRole" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    count_col = ID_COLUMN if ID_COLUMN in dataframe.columns else "Attrition"
    agg_dict: dict = {
        "EmployeeCount": (count_col, "count"),
        "AttritionCount": (
            "Attrition",
            lambda values: (values == "Yes").sum(),
        ),
    }

    if "MonthlyIncome" in dataframe.columns:
        agg_dict["AverageMonthlyIncome"] = ("MonthlyIncome", "mean")

    result = dataframe.groupby("JobRole").agg(**agg_dict).reset_index()

    result["AttritionRate"] = (
        result["AttritionCount"]
        / result["EmployeeCount"]
        * 100
    ).round(2)

    if "AverageMonthlyIncome" in result.columns:
        result["AverageMonthlyIncome"] = (
            result["AverageMonthlyIncome"].round(2)
        )

    return result.sort_values(
        "AttritionRate",
        ascending=False,
    ).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Salary analysis
# ---------------------------------------------------------------------------

def create_salary_band(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a salary-band column based on configured salary ranges.

    Returns
    -------
    pd.DataFrame
        Dataset containing SalaryBand.
    """
    dataframe = dataframe.copy()

    if "MonthlyIncome" in dataframe.columns:
        dataframe["SalaryBand"] = pd.cut(
            dataframe["MonthlyIncome"],
            bins=SALARY_BINS,
            labels=SALARY_LABELS,
            include_lowest=True,
        )

    return dataframe


def analyze_salary_band(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze attrition across salary bands.
    """
    if "MonthlyIncome" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    dataframe = create_salary_band(dataframe)

    return calculate_attrition_rate(
        dataframe,
        "SalaryBand",
    )


# ---------------------------------------------------------------------------
# Age analysis
# ---------------------------------------------------------------------------

def create_age_group(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add an age-group column using configured age ranges.
    """
    dataframe = dataframe.copy()

    if "Age" in dataframe.columns:
        dataframe["AgeGroup"] = pd.cut(
            dataframe["Age"],
            bins=AGE_BINS,
            labels=AGE_LABELS,
            include_lowest=True,
        )

    return dataframe


def analyze_age_group(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze attrition across age groups.
    """
    if "Age" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    dataframe = create_age_group(dataframe)

    return calculate_attrition_rate(
        dataframe,
        "AgeGroup",
    )


# ---------------------------------------------------------------------------
# Tenure analysis
# ---------------------------------------------------------------------------

def create_tenure_group(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a tenure-group column using YearsAtCompany.
    """
    dataframe = dataframe.copy()

    if "YearsAtCompany" in dataframe.columns:
        dataframe["TenureGroup"] = pd.cut(
            dataframe["YearsAtCompany"],
            bins=TENURE_BINS,
            labels=TENURE_LABELS,
            include_lowest=True,
        )

    return dataframe


def analyze_tenure(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze attrition across employee tenure groups.
    """
    if "YearsAtCompany" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    dataframe = create_tenure_group(dataframe)

    return calculate_attrition_rate(
        dataframe,
        "TenureGroup",
    )


# ---------------------------------------------------------------------------
# Satisfaction analysis
# ---------------------------------------------------------------------------

def analyze_satisfaction(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate attrition statistics for satisfaction measures.

    Includes:
    - Job satisfaction
    - Environment satisfaction
    - Relationship satisfaction
    - Work-life balance
    """
    results = []
    present_cols = [
        col for col in SATISFACTION_COLUMNS if col in dataframe.columns
    ]

    if not present_cols or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    count_col = ID_COLUMN if ID_COLUMN in dataframe.columns else "Attrition"

    for column in present_cols:
        grouped = (
            dataframe.groupby(column)
            .agg(
                EmployeeCount=(count_col, "count"),
                AttritionCount=(
                    "Attrition",
                    lambda values: (values == "Yes").sum(),
                ),
            )
            .reset_index()
        )

        grouped["AttritionRate"] = (
            grouped["AttritionCount"]
            / grouped["EmployeeCount"]
            * 100
        ).round(2)

        grouped["SatisfactionType"] = column

        grouped = grouped.rename(
            columns={column: "SatisfactionLevel"}
        )

        results.append(grouped)

    return pd.concat(
        results,
        ignore_index=True,
    )


# ---------------------------------------------------------------------------
# Overtime analysis
# ---------------------------------------------------------------------------

def analyze_overtime(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze employee attrition based on overtime status.
    """
    if "OverTime" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    return calculate_attrition_rate(
        dataframe,
        "OverTime",
    )


# ---------------------------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------------------------

def calculate_correlation_matrix(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate the Pearson correlation matrix for numerical variables.

    EmployeeID is excluded because it is an identifier rather than
    an analytical numerical variable.

    The Attrition column is converted to a binary representation:
    Yes = 1
    No = 0

    Returns
    -------
    pd.DataFrame
        Correlation matrix excluding EmployeeID.
    """
    if "Attrition" not in dataframe.columns:
        return pd.DataFrame()

    correlation_data = dataframe.copy()

    correlation_data["AttritionBinary"] = (
        correlation_data["Attrition"]
        .map(ATTRITION_BINARY_MAPPING)
    )

    numerical_data = correlation_data.select_dtypes(
        include="number"
    ).drop(
        columns=[ID_COLUMN],
        errors="ignore",
    )

    if numerical_data.empty or len(numerical_data.columns) < 2:
        return pd.DataFrame()

    return numerical_data.corr().round(3)


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def generate_summary_tables(
    dataframe: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate all major summary tables available based on the columns
    present in the dataset.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing named analysis tables for available dimensions.
    """
    tables: dict[str, pd.DataFrame] = {}

    if "Attrition" in dataframe.columns:
        tables["attrition"] = analyze_attrition_distribution(dataframe)

    if "Department" in dataframe.columns and "Attrition" in dataframe.columns:
        tables["department"] = analyze_department(dataframe)

    if "JobRole" in dataframe.columns and "Attrition" in dataframe.columns:
        tables["job_role"] = analyze_job_role(dataframe)

    if "MonthlyIncome" in dataframe.columns and "Attrition" in dataframe.columns:
        tables["salary_band"] = analyze_salary_band(dataframe)

    if "Age" in dataframe.columns and "Attrition" in dataframe.columns:
        tables["age_group"] = analyze_age_group(dataframe)

    if "YearsAtCompany" in dataframe.columns and "Attrition" in dataframe.columns:
        tables["tenure_group"] = analyze_tenure(dataframe)

    if any(col in dataframe.columns for col in SATISFACTION_COLUMNS) and "Attrition" in dataframe.columns:
        tables["satisfaction"] = analyze_satisfaction(dataframe)

    if "OverTime" in dataframe.columns and "Attrition" in dataframe.columns:
        tables["overtime"] = analyze_overtime(dataframe)

    if len(dataframe.select_dtypes(include="number").columns) > 1 and "Attrition" in dataframe.columns:
        corr_table = calculate_correlation_matrix(dataframe)
        if not corr_table.empty:
            tables["correlation"] = corr_table

    return tables