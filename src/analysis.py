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
    SALARY_BINS,
    SALARY_LABELS,
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
    result = (
        dataframe.groupby(group_column, dropna=False)
        .agg(
            EmployeeCount=("EmployeeID", "count"),
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
    - Average monthly income
    - Average job satisfaction
    """
    result = (
        dataframe.groupby("Department")
        .agg(
            EmployeeCount=("EmployeeID", "count"),
            AttritionCount=(
                "Attrition",
                lambda values: (values == "Yes").sum(),
            ),
            AverageMonthlyIncome=(
                "MonthlyIncome",
                "mean",
            ),
            AverageJobSatisfaction=(
                "JobSatisfaction",
                "mean",
            ),
        )
        .reset_index()
    )

    result["AttritionRate"] = (
        result["AttritionCount"]
        / result["EmployeeCount"]
        * 100
    ).round(2)

    result["AverageMonthlyIncome"] = (
        result["AverageMonthlyIncome"].round(2)
    )

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
    - Average monthly income
    """
    result = (
        dataframe.groupby("JobRole")
        .agg(
            EmployeeCount=("EmployeeID", "count"),
            AttritionCount=(
                "Attrition",
                lambda values: (values == "Yes").sum(),
            ),
            AverageMonthlyIncome=(
                "MonthlyIncome",
                "mean",
            ),
        )
        .reset_index()
    )

    result["AttritionRate"] = (
        result["AttritionCount"]
        / result["EmployeeCount"]
        * 100
    ).round(2)

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
    dataframe = create_salary_band(dataframe)

    result = calculate_attrition_rate(
        dataframe,
        "SalaryBand",
    )

    return result


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
    dataframe = create_age_group(dataframe)

    result = calculate_attrition_rate(
        dataframe,
        "AgeGroup",
    )

    return result


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
    dataframe = create_tenure_group(dataframe)

    result = calculate_attrition_rate(
        dataframe,
        "TenureGroup",
    )

    return result


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
    satisfaction_columns = [
        "JobSatisfaction",
        "EnvironmentSatisfaction",
        "RelationshipSatisfaction",
        "WorkLifeBalance",
    ]

    results = []

    for column in satisfaction_columns:
        grouped = (
            dataframe.groupby(column)
            .agg(
                EmployeeCount=("EmployeeID", "count"),
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
    correlation_data = dataframe.copy()

    correlation_data["AttritionBinary"] = (
        correlation_data["Attrition"]
        .map({"Yes": 1, "No": 0})
    )

    numerical_data = correlation_data.select_dtypes(
        include="number"
    ).drop(
        columns=["EmployeeID"],
        errors="ignore",
    )

    return numerical_data.corr().round(3)


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def generate_summary_tables(
    dataframe: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate all major summary tables required by the project.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing named analysis tables.
    """
    salary_data = create_salary_band(dataframe)
    age_data = create_age_group(dataframe)
    tenure_data = create_tenure_group(dataframe)

    return {
        "attrition": analyze_attrition_distribution(dataframe),
        "department": analyze_department(dataframe),
        "job_role": analyze_job_role(dataframe),
        "salary_band": calculate_attrition_rate(
            salary_data,
            "SalaryBand",
        ),
        "age_group": calculate_attrition_rate(
            age_data,
            "AgeGroup",
        ),
        "tenure_group": calculate_attrition_rate(
            tenure_data,
            "TenureGroup",
        ),
        "satisfaction": analyze_satisfaction(dataframe),
        "overtime": analyze_overtime(dataframe),
        "correlation": calculate_correlation_matrix(dataframe),
    }