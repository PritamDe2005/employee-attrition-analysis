"""
Streamlit dashboard for the Employee Attrition Analysis project.

This module provides an interactive dashboard for exploring:
- Employee attrition
- Department and job-role patterns
- Salary, age, and tenure
- Satisfaction and overtime
- Additional employee factors
- Correlation between numerical variables
- Raw versus cleaned data quality
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from config import RAW_DATA_FILE
from src.analysis import (
    analyze_age_group,
    analyze_department,
    analyze_job_role,
    analyze_overtime,
    analyze_salary_band,
    analyze_satisfaction,
    analyze_tenure,
    calculate_correlation_matrix,
    create_age_group,
    create_salary_band,
    create_tenure_group,
)
from src.data_loader import load_and_validate_dataset
from src.preprocessing import preprocess_dataset


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Employee Attrition Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


@st.cache_data
def load_raw_data(file_path: Path) -> pd.DataFrame:
    """Load and validate the raw employee attrition dataset."""
    return load_and_validate_dataset(file_path)


@st.cache_data
def load_processed_data(file_path: Path) -> pd.DataFrame:
    """Load and preprocess the employee attrition dataset."""
    raw_dataframe = load_raw_data(file_path)
    return preprocess_dataset(raw_dataframe)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def calculate_overall_attrition_rate(
    dataframe: pd.DataFrame,
) -> float:
    """
    Calculate the overall employee attrition rate.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Employee dataset.

    Returns
    -------
    float
        Overall attrition rate as a percentage.
    """
    if dataframe.empty:
        return 0.0

    return dataframe["Attrition"].eq("Yes").mean() * 100


def format_number(value: float) -> str:
    """Format numerical values for dashboard display."""
    return f"{value:,.0f}"


def format_percentage(value: float) -> str:
    """Format percentage values for dashboard display."""
    return f"{value:.2f}%"


def calculate_data_quality(
    raw_dataframe: pd.DataFrame,
    cleaned_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create a summary comparing raw and cleaned dataset quality.

    Parameters
    ----------
    raw_dataframe : pd.DataFrame
        Original validated dataset before preprocessing.

    cleaned_dataframe : pd.DataFrame
        Dataset after preprocessing.

    Returns
    -------
    pd.DataFrame
        Data-quality comparison table.
    """
    return pd.DataFrame(
        {
            "Metric": [
                "Rows",
                "Missing Cells",
                "Duplicate Rows",
            ],
            "Raw Dataset": [
                len(raw_dataframe),
                int(raw_dataframe.isna().sum().sum()),
                int(raw_dataframe.duplicated().sum()),
            ],
            "Cleaned Dataset": [
                len(cleaned_dataframe),
                int(cleaned_dataframe.isna().sum().sum()),
                int(cleaned_dataframe.duplicated().sum()),
            ],
        }
    )


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Streamlit Employee Attrition Analysis dashboard."""

    st.title("📊 Employee Attrition Analysis")

    st.markdown(
        """
        **HR Analytics Dashboard**

        Explore employee attrition patterns across departments, job roles,
        salary bands, age groups, tenure, satisfaction, overtime, and other
        employee characteristics.
        """
    )

    # -----------------------------------------------------------------------
    # Load data
    # -----------------------------------------------------------------------

    try:
        raw_dataframe = load_raw_data(RAW_DATA_FILE)
        dataframe = load_processed_data(RAW_DATA_FILE)

    except (FileNotFoundError, ValueError, OSError) as error:
        st.error(f"Unable to load the dataset: {error}")
        st.stop()

    # -----------------------------------------------------------------------
    # Sidebar filters
    # -----------------------------------------------------------------------

    st.sidebar.header("🔎 Filters")

    departments = sorted(
        dataframe["Department"].dropna().unique()
    )

    selected_departments = st.sidebar.multiselect(
        "Department",
        options=departments,
        default=departments,
    )

    job_roles = sorted(
        dataframe["JobRole"].dropna().unique()
    )

    selected_job_roles = st.sidebar.multiselect(
        "Job Role",
        options=job_roles,
        default=job_roles,
    )

    overtime_options = sorted(
        dataframe["OverTime"].dropna().unique()
    )

    selected_overtime = st.sidebar.multiselect(
        "OverTime",
        options=overtime_options,
        default=overtime_options,
    )

    gender_options = sorted(
        dataframe["Gender"].dropna().unique()
    )

    selected_gender = st.sidebar.multiselect(
        "Gender",
        options=gender_options,
        default=gender_options,
    )

    # -----------------------------------------------------------------------
    # Apply filters
    # -----------------------------------------------------------------------

    filtered_dataframe = dataframe[
        dataframe["Department"].isin(selected_departments)
        & dataframe["JobRole"].isin(selected_job_roles)
        & dataframe["OverTime"].isin(selected_overtime)
        & dataframe["Gender"].isin(selected_gender)
    ].copy()

    if filtered_dataframe.empty:
        st.warning(
            "No employees match the selected filters. "
            "Please adjust the filters in the sidebar."
        )
        st.stop()

    # -----------------------------------------------------------------------
    # KPI section
    # -----------------------------------------------------------------------

    total_employees = len(filtered_dataframe)

    attrition_count = (
        filtered_dataframe["Attrition"]
        .eq("Yes")
        .sum()
    )

    attrition_rate = calculate_overall_attrition_rate(
        filtered_dataframe
    )

    average_income = filtered_dataframe["MonthlyIncome"].mean()
    average_tenure = filtered_dataframe["YearsAtCompany"].mean()

    st.subheader("📌 Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Employees",
            format_number(total_employees),
        )

    with col2:
        st.metric(
            "Attrition Count",
            format_number(attrition_count),
        )

    with col3:
        st.metric(
            "Attrition Rate",
            format_percentage(attrition_rate),
        )

    with col4:
        st.metric(
            "Average Monthly Income",
            f"₹{average_income:,.0f}",
        )

    with col5:
        st.metric(
            "Average Tenure",
            f"{average_tenure:.1f} years",
        )

    st.divider()

    # -----------------------------------------------------------------------
    # Attrition distribution
    # -----------------------------------------------------------------------

    st.subheader("📈 Attrition Distribution")

    attrition_distribution = (
        filtered_dataframe["Attrition"]
        .value_counts()
        .rename_axis("Attrition")
        .reset_index(name="Employees")
    )

    chart_col, table_col = st.columns([2, 1])

    with chart_col:
        st.bar_chart(
            attrition_distribution.set_index("Attrition"),
            y="Employees",
        )

    with table_col:
        attrition_display = attrition_distribution.copy()

        attrition_display["Percentage"] = (
            attrition_display["Employees"]
            / attrition_display["Employees"].sum()
            * 100
        ).round(2)

        st.dataframe(
            attrition_display,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------------------------
    # Department analysis
    # -----------------------------------------------------------------------

    st.subheader("🏢 Department Analysis")

    department_analysis = analyze_department(
        filtered_dataframe
    )

    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.bar_chart(
            department_analysis.set_index("Department")[
                "AttritionRate"
            ]
        )

    with col2:
        st.dataframe(
            department_analysis,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------------------------
    # Job role analysis
    # -----------------------------------------------------------------------

    st.subheader("💼 Job Role Analysis")

    job_role_analysis = analyze_job_role(
        filtered_dataframe
    )

    st.bar_chart(
        job_role_analysis.set_index("JobRole")[
            "AttritionRate"
        ]
    )

    st.dataframe(
        job_role_analysis,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------------------------
    # Salary analysis
    # -----------------------------------------------------------------------

    st.subheader("💰 Salary Analysis")

    salary_dataframe = create_salary_band(
        filtered_dataframe
    )

    salary_analysis = analyze_salary_band(
        salary_dataframe
    )

    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.bar_chart(
            salary_analysis.set_index("SalaryBand")[
                "AttritionRate"
            ]
        )

    with col2:
        st.dataframe(
            salary_analysis,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------------------------
    # Age and tenure analysis
    # -----------------------------------------------------------------------

    st.subheader("👥 Age & Tenure Analysis")

    age_dataframe = create_age_group(
        filtered_dataframe
    )

    age_analysis = analyze_age_group(
        age_dataframe
    )

    tenure_dataframe = create_tenure_group(
        filtered_dataframe
    )

    tenure_analysis = analyze_tenure(
        tenure_dataframe
    )

    age_col, tenure_col = st.columns(2)

    with age_col:
        st.markdown("**Attrition by Age Group**")

        st.bar_chart(
            age_analysis.set_index("AgeGroup")[
                "AttritionRate"
            ]
        )

        st.dataframe(
            age_analysis,
            use_container_width=True,
            hide_index=True,
        )

    with tenure_col:
        st.markdown("**Attrition by Tenure Group**")

        st.bar_chart(
            tenure_analysis.set_index("TenureGroup")[
                "AttritionRate"
            ]
        )

        st.dataframe(
            tenure_analysis,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------------------------
    # Satisfaction analysis
    # -----------------------------------------------------------------------

    st.subheader("😊 Employee Satisfaction")

    satisfaction_analysis = analyze_satisfaction(
        filtered_dataframe
    )

    satisfaction_types = satisfaction_analysis[
        "SatisfactionType"
    ].unique()

    selected_satisfaction = st.selectbox(
        "Select satisfaction metric",
        options=satisfaction_types,
    )

    selected_satisfaction_data = satisfaction_analysis[
        satisfaction_analysis["SatisfactionType"]
        == selected_satisfaction
    ].copy()

    selected_satisfaction_data = (
        selected_satisfaction_data
        .set_index("SatisfactionLevel")
    )

    st.bar_chart(
        selected_satisfaction_data[
            "AttritionRate"
        ]
    )

    st.dataframe(
        satisfaction_analysis,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------------------------
    # Overtime analysis
    # -----------------------------------------------------------------------

    st.subheader("⏰ Overtime Analysis")

    overtime_analysis = analyze_overtime(
        filtered_dataframe
    )

    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.bar_chart(
            overtime_analysis.set_index("OverTime")[
                "AttritionRate"
            ]
        )

    with col2:
        st.dataframe(
            overtime_analysis,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------------------------
    # Additional employee factors
    # -----------------------------------------------------------------------

    st.subheader("🔍 Additional Employee Factors")

    factor_col1, factor_col2 = st.columns(2)

    with factor_col1:
        business_travel = (
            filtered_dataframe
            .groupby("BusinessTravel")
            .agg(
                Employees=("EmployeeID", "count"),
                Attrition_Count=(
                    "Attrition",
                    lambda values: (values == "Yes").sum(),
                ),
            )
        )

        business_travel["AttritionRate"] = (
            business_travel["Attrition_Count"]
            / business_travel["Employees"]
            * 100
        ).round(2)

        st.markdown("**Business Travel**")

        st.bar_chart(
            business_travel["AttritionRate"]
        )

    with factor_col2:
        remote_work = (
            filtered_dataframe
            .groupby("RemoteWork")
            .agg(
                Employees=("EmployeeID", "count"),
                Attrition_Count=(
                    "Attrition",
                    lambda values: (values == "Yes").sum(),
                ),
            )
        )

        remote_work["AttritionRate"] = (
            remote_work["Attrition_Count"]
            / remote_work["Employees"]
            * 100
        ).round(2)

        st.markdown("**Remote Work**")

        st.bar_chart(
            remote_work["AttritionRate"]
        )

    # -----------------------------------------------------------------------
    # Correlation analysis
    # -----------------------------------------------------------------------

    st.subheader("🔗 Correlation Analysis")

    correlation_matrix = calculate_correlation_matrix(
        filtered_dataframe
    )

    st.dataframe(
        correlation_matrix.round(2),
        use_container_width=True,
    )

    st.caption(
        "Correlation indicates statistical association between numerical "
        "variables. It does not establish causation."
    )

    # -----------------------------------------------------------------------
    # Data quality
    # -----------------------------------------------------------------------

    st.subheader("🧹 Data Quality")

    quality_summary = calculate_data_quality(
        raw_dataframe,
        dataframe,
    )

    st.dataframe(
        quality_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "The dashboard uses the cleaned dataset produced by the project's "
        "modular preprocessing pipeline. Raw and cleaned quality metrics "
        "are shown above for comparison."
    )

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------

    st.divider()

    st.caption(
        "Employee Attrition Analysis | HR Analytics Project"
    )


if __name__ == "__main__":
    main()
