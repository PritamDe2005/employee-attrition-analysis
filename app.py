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

from config import (
    EXPECTED_COLUMNS,
    ID_COLUMN,
    RAW_DATA_FILE,
    SATISFACTION_COLUMNS,
)
from src.analysis import (
    analyze_age_group,
    analyze_department,
    analyze_job_role,
    analyze_overtime,
    analyze_salary_band,
    analyze_satisfaction,
    analyze_tenure,
    calculate_correlation_matrix,
)
from src.column_mapper import apply_column_mapping, resolve_column_mapping
from src.data_loader import (
    get_dataset_info,
    load_and_validate_dataset,
    load_dataset_from_source,
    validate_dynamic_schema,
)
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
    raw_info = get_dataset_info(raw_dataframe)
    cleaned_info = get_dataset_info(cleaned_dataframe)

    return pd.DataFrame(
        {
            "Metric": [
                "Rows",
                "Missing Cells",
                "Duplicate Rows",
            ],
            "Raw Dataset": [
                raw_info["rows"],
                raw_info["missing_cells"],
                raw_info["duplicate_rows"],
            ],
            "Cleaned Dataset": [
                cleaned_info["rows"],
                cleaned_info["missing_cells"],
                cleaned_info["duplicate_rows"],
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
    # Data source selection
    # -----------------------------------------------------------------------

    st.sidebar.header("📁 Data Source")
    data_source_mode = st.sidebar.radio(
        "Choose dataset source",
        options=[
            "Sample HR Dataset (8,040 rows)",
            "Upload Custom Dataset (CSV/Excel)",
        ],
        index=0,
    )

    uploaded_file = None
    if data_source_mode == "Upload Custom Dataset (CSV/Excel)":
        uploaded_file = st.sidebar.file_uploader(
            "Upload employee dataset",
            type=["csv", "xlsx", "xls"],
            help="Upload your own employee dataset in CSV or Excel format.",
        )

        try:
            with open(RAW_DATA_FILE, "rb") as template_file:
                st.sidebar.download_button(
                    label="📥 Download Template (CSV)",
                    data=template_file,
                    file_name="employee_attrition_template.csv",
                    mime="text/csv",
                    help="Download standard HR dataset template for reference.",
                )
        except OSError:
            pass

    # -----------------------------------------------------------------------
    # Load data
    # -----------------------------------------------------------------------

    try:
        if data_source_mode == "Upload Custom Dataset (CSV/Excel)":
            if uploaded_file is None:
                st.info(
                    "👋 **Welcome!** Please upload your HR dataset using the file uploader "
                    "in the sidebar (`.csv`, `.xlsx`, or `.xls`) to begin analysis."
                )

                st.subheader("📋 Guidelines for Uploading Your Dataset")

                guide_col1, guide_col2 = st.columns(2)

                with guide_col1:
                    st.markdown(
                        """
                        ### 1. 📁 Supported File Formats
                        - **CSV (`.csv`)**: Encoded in UTF-8, Latin-1, or standard text.
                        - **Excel (`.xlsx`, `.xls`)**: Single-sheet standard workbook.

                        ### 2. 🎯 Only 1 Mandatory Column
                        - **Target Column (`Attrition`)**: The dataset must contain an attrition indicator.
                        - **Recognized Column Names**: `Attrition`, `left`, `left_company`, `turnover`, `churn`, `status`, `resigned`, `separated`.
                        - **Accepted Target Values**:
                          - **Positive (Left)**: `Yes`, `1`, `True`, `left`, `terminated`, `resigned`, `voluntarily separated`
                          - **Negative (Stayed)**: `No`, `0`, `False`, `stayed`, `active`, `retained`, `employed`
                        """
                    )

                with guide_col2:
                    st.markdown(
                        """
                        ### 3. 🧩 Optional Columns & Auto-Mapping
                        You do not need to rename your columns manually. The system automatically detects synonyms:
                        - **Department**: `dept`, `division`, `business_unit`, `team`
                        - **Job Role**: `role`, `work_role`, `job_title`, `position`
                        - **Salary**: `salary`, `monthly_income`, `income`, `pay`, `base_pay`
                        - **Tenure**: `tenure`, `years_at_company`, `company_tenure`
                        - **Age**: `age`, `employee_age`, `age_years`
                        - **Overtime**: `overtime`, `ot`, `extra_hours`
                        - **Satisfaction**: `job_satisfaction`, `environment_satisfaction`, `work_life_balance`

                        ### 4. 🤖 Automated Data Cleaning
                        The platform automatically:
                        - Strips irregular whitespaces and normalizes letter casing.
                        - Deduplicates exact duplicate rows and duplicate IDs.
                        - Imputes missing numerical values with the **median**.
                        - Imputes missing categorical values with the **mode**.
                        - Gracefully adapts dashboards if some optional columns are missing!
                        """
                    )

                st.divider()

                st.markdown(
                    """
                    💡 **Need a starting point?** Download our pre-formatted sample template 
                    from the sidebar (**"📥 Download Template (CSV)"**) to see the exact structure.
                    """
                )
                st.stop()

            raw_dataframe = load_dataset_from_source(
                uploaded_file,
                filename=uploaded_file.name,
            )
            mapping, unmapped = resolve_column_mapping(
                list(raw_dataframe.columns)
            )
            mapped_dataframe = apply_column_mapping(raw_dataframe, mapping)

            if unmapped:
                st.error(
                    f"### ❌ Schema Validation Error: Unexpected Extra Entity/Column(s) Detected!\n\n"
                    f"The uploaded file contains **{len(unmapped)} extra entity/column(s)** that do not exist "
                    f"in the sample HR dataset:\n\n"
                    + "\n".join([f"- ⚠️ **`{col}`**" for col in unmapped])
                    + "\n\n"
                    f"**Strict Schema Rule:** The uploaded file must not have any extra entities with respect to the sample CSV.\n\n"
                    f"**Action Required:** Please remove these extra columns from your spreadsheet (or rename them if they represent standard attributes) and re-upload."
                )
                with st.expander("📋 View Sample CSV Allowed Entities / Schema (29 Attributes)", expanded=True):
                    st.markdown("Your uploaded file may only contain columns from these 29 sample attributes:")
                    st.dataframe(pd.DataFrame({"Allowed Sample Entities": EXPECTED_COLUMNS}), use_container_width=True)
                st.stop()

            validate_dynamic_schema(mapped_dataframe)

            with st.expander("🗂️ Detected Column Mapping & Schema", expanded=False):
                st.markdown("**Mapped Canonical Columns**")
                mapping_display = pd.DataFrame(
                    [
                        {"Uploaded Header": k, "Mapped Attribute": v}
                        for k, v in mapping.items()
                    ]
                )
                st.dataframe(mapping_display, hide_index=True, use_container_width=True)
                st.success("All uploaded columns match the sample CSV schema!")

            dataframe = preprocess_dataset(mapped_dataframe)
        else:
            raw_dataframe = load_raw_data(RAW_DATA_FILE)
            dataframe = load_processed_data(RAW_DATA_FILE)

    except (FileNotFoundError, ValueError, OSError) as error:
        st.error(f"Unable to load or process dataset: {error}")
        st.stop()

    # -----------------------------------------------------------------------
    # Sidebar filters (adaptive to available columns)
    # -----------------------------------------------------------------------

    st.sidebar.header("🔎 Filters")

    filter_mask = pd.Series(True, index=dataframe.index)

    if "Department" in dataframe.columns:
        departments = sorted(dataframe["Department"].dropna().unique())
        if departments:
            selected_departments = st.sidebar.multiselect(
                "Department",
                options=departments,
                default=departments,
            )
            filter_mask &= dataframe["Department"].isin(selected_departments)

    if "JobRole" in dataframe.columns:
        job_roles = sorted(dataframe["JobRole"].dropna().unique())
        if job_roles:
            selected_job_roles = st.sidebar.multiselect(
                "Job Role",
                options=job_roles,
                default=job_roles,
            )
            filter_mask &= dataframe["JobRole"].isin(selected_job_roles)

    if "OverTime" in dataframe.columns:
        overtime_options = sorted(dataframe["OverTime"].dropna().unique())
        if overtime_options:
            selected_overtime = st.sidebar.multiselect(
                "OverTime",
                options=overtime_options,
                default=overtime_options,
            )
            filter_mask &= dataframe["OverTime"].isin(selected_overtime)

    if "Gender" in dataframe.columns:
        gender_options = sorted(dataframe["Gender"].dropna().unique())
        if gender_options:
            selected_gender = st.sidebar.multiselect(
                "Gender",
                options=gender_options,
                default=gender_options,
            )
            filter_mask &= dataframe["Gender"].isin(selected_gender)

    if "Age" in dataframe.columns and not dataframe["Age"].dropna().empty:
        min_age = int(dataframe["Age"].min())
        max_age = int(dataframe["Age"].max())
        if min_age < max_age:
            selected_age = st.sidebar.slider(
                "Age Range",
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age),
            )
            filter_mask &= dataframe["Age"].between(
                selected_age[0],
                selected_age[1],
            )

    if "MonthlyIncome" in dataframe.columns and not dataframe["MonthlyIncome"].dropna().empty:
        min_income = int(dataframe["MonthlyIncome"].min())
        max_income = int(dataframe["MonthlyIncome"].max())
        if min_income < max_income:
            selected_income = st.sidebar.slider(
                "Monthly Income Range (₹)",
                min_value=min_income,
                max_value=max_income,
                value=(min_income, max_income),
            )
            filter_mask &= dataframe["MonthlyIncome"].between(
                selected_income[0],
                selected_income[1],
            )

    # -----------------------------------------------------------------------
    # Apply filters
    # -----------------------------------------------------------------------

    filtered_dataframe = dataframe.loc[filter_mask].copy()

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

    st.subheader("📌 Overview")

    kpi_items = [
        ("Total Employees", format_number(total_employees)),
        ("Attrition Count", format_number(attrition_count)),
        ("Attrition Rate", format_percentage(attrition_rate)),
    ]

    if "MonthlyIncome" in filtered_dataframe.columns:
        average_income = filtered_dataframe["MonthlyIncome"].mean()
        kpi_items.append(("Average Monthly Income", f"₹{average_income:,.0f}"))

    if "YearsAtCompany" in filtered_dataframe.columns:
        average_tenure = filtered_dataframe["YearsAtCompany"].mean()
        kpi_items.append(("Average Tenure", f"{average_tenure:.1f} years"))

    cols = st.columns(len(kpi_items))
    for col, (label, val) in zip(cols, kpi_items):
        with col:
            st.metric(label, val)

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

    if "Department" in filtered_dataframe.columns:
        st.subheader("🏢 Department Analysis")

        department_analysis = analyze_department(
            filtered_dataframe
        )

        if not department_analysis.empty and "Department" in department_analysis.columns:
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

    if "JobRole" in filtered_dataframe.columns:
        st.subheader("💼 Job Role Analysis")

        job_role_analysis = analyze_job_role(
            filtered_dataframe
        )

        if not job_role_analysis.empty and "JobRole" in job_role_analysis.columns:
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

    if "MonthlyIncome" in filtered_dataframe.columns or "SalaryBand" in filtered_dataframe.columns:
        st.subheader("💰 Salary Analysis")

        salary_analysis = analyze_salary_band(
            filtered_dataframe
        )

        if not salary_analysis.empty and "SalaryBand" in salary_analysis.columns:
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

    has_age = "Age" in filtered_dataframe.columns or "AgeGroup" in filtered_dataframe.columns
    has_tenure = "YearsAtCompany" in filtered_dataframe.columns or "TenureGroup" in filtered_dataframe.columns

    if has_age or has_tenure:
        st.subheader("👥 Age & Tenure Analysis")

        age_analysis = analyze_age_group(filtered_dataframe) if has_age else pd.DataFrame()
        tenure_analysis = analyze_tenure(filtered_dataframe) if has_tenure else pd.DataFrame()

        if has_age and has_tenure:
            age_col, tenure_col = st.columns(2)

            with age_col:
                st.markdown("**Attrition by Age Group**")
                if not age_analysis.empty and "AgeGroup" in age_analysis.columns:
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
                if not tenure_analysis.empty and "TenureGroup" in tenure_analysis.columns:
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
        elif has_age:
            st.markdown("**Attrition by Age Group**")
            if not age_analysis.empty and "AgeGroup" in age_analysis.columns:
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
        else:
            st.markdown("**Attrition by Tenure Group**")
            if not tenure_analysis.empty and "TenureGroup" in tenure_analysis.columns:
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

    has_sat = any(c in filtered_dataframe.columns for c in SATISFACTION_COLUMNS)
    if has_sat:
        satisfaction_analysis = analyze_satisfaction(
            filtered_dataframe
        )

        if not satisfaction_analysis.empty and "SatisfactionType" in satisfaction_analysis.columns:
            st.subheader("😊 Employee Satisfaction")

            satisfaction_types = satisfaction_analysis[
                "SatisfactionType"
            ].unique()

            if len(satisfaction_types) > 0:
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

    if "OverTime" in filtered_dataframe.columns:
        st.subheader("⏰ Overtime Analysis")

        overtime_analysis = analyze_overtime(
            filtered_dataframe
        )

        if not overtime_analysis.empty and "OverTime" in overtime_analysis.columns:
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

    has_bt = "BusinessTravel" in filtered_dataframe.columns
    has_rw = "RemoteWork" in filtered_dataframe.columns
    count_col = ID_COLUMN if ID_COLUMN in filtered_dataframe.columns else "Attrition"

    if has_bt or has_rw:
        st.subheader("🔍 Additional Employee Factors")

        if has_bt and has_rw:
            factor_col1, factor_col2 = st.columns(2)

            with factor_col1:
                business_travel = (
                    filtered_dataframe
                    .groupby("BusinessTravel")
                    .agg(
                        Employees=(count_col, "count"),
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
                        Employees=(count_col, "count"),
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
        elif has_bt:
            business_travel = (
                filtered_dataframe
                .groupby("BusinessTravel")
                .agg(
                    Employees=(count_col, "count"),
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
        else:
            remote_work = (
                filtered_dataframe
                .groupby("RemoteWork")
                .agg(
                    Employees=(count_col, "count"),
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

    numerical_cols = filtered_dataframe.select_dtypes(include="number").columns
    if len(numerical_cols) >= 2:
        correlation_matrix = calculate_correlation_matrix(
            filtered_dataframe
        )

        if not correlation_matrix.empty and len(correlation_matrix.columns) >= 2:
            st.subheader("🔗 Correlation Analysis")

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
