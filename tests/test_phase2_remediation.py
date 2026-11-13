"""
Regression and verification tests for Phase 2: Schema Rectification and DRY Remediation.
"""

from pathlib import Path
import tempfile

import pandas as pd

from config import (
    ATTRITION_BINARY_MAPPING,
    EDUCATION_MAPPING,
    ID_COLUMN,
    NUMERICAL_COLUMNS,
    ORDINAL_COLUMNS,
    SATISFACTION_COLUMNS,
)
from src.analysis import (
    analyze_age_group,
    analyze_salary_band,
    analyze_tenure,
    calculate_attrition_rate,
    calculate_correlation_matrix,
)
from src.data_loader import get_dataset_info
from src.preprocessing import (
    convert_data_types,
    handle_invalid_numerical_values,
    handle_missing_values,
    preprocess_dataset,
)
from src.visualization import (
    plot_attrition_by_department,
    plot_attrition_by_job_role,
    plot_correlation_heatmap,
    plot_overtime_vs_attrition,
    plot_satisfaction_vs_attrition,
)


def test_education_classification_and_mapping():
    """Verify Education is classified as numerical/ordinal and converts degree strings."""
    assert "Education" in NUMERICAL_COLUMNS
    assert "Education" in ORDINAL_COLUMNS
    assert ID_COLUMN == "EmployeeID"

    # Test conversion of string degrees and numeric strings
    df = pd.DataFrame(
        {
            "Education": ["Bachelor", "Master", "5", "InvalidDegree"],
        }
    )
    converted = convert_data_types(df)
    assert converted.loc[0, "Education"] == 3.0
    assert converted.loc[1, "Education"] == 4.0
    assert converted.loc[2, "Education"] == 5.0
    assert pd.isna(converted.loc[3, "Education"])


def test_education_invalid_range_handling():
    """Verify Education out-of-range values (<1 or >5) are replaced with NaN."""
    df = pd.DataFrame(
        {
            "Education": [1, 5, 0, 6, -2],
        }
    )
    handled = handle_invalid_numerical_values(df)
    assert handled.loc[0, "Education"] == 1
    assert handled.loc[1, "Education"] == 5
    assert pd.isna(handled.loc[2, "Education"])
    assert pd.isna(handled.loc[3, "Education"])
    assert pd.isna(handled.loc[4, "Education"])


def test_satisfaction_columns_centralized():
    """Verify SATISFACTION_COLUMNS is centralized and used in preprocessing."""
    assert len(SATISFACTION_COLUMNS) == 4
    assert "JobSatisfaction" in SATISFACTION_COLUMNS
    assert "EnvironmentSatisfaction" in SATISFACTION_COLUMNS
    assert "RelationshipSatisfaction" in SATISFACTION_COLUMNS
    assert "WorkLifeBalance" in SATISFACTION_COLUMNS

    df = pd.DataFrame(
        {
            col: [1, 4, 0, 5] for col in SATISFACTION_COLUMNS
        }
    )
    handled = handle_invalid_numerical_values(df)
    for col in SATISFACTION_COLUMNS:
        assert handled.loc[0, col] == 1
        assert handled.loc[1, col] == 4
        assert pd.isna(handled.loc[2, col])
        assert pd.isna(handled.loc[3, col])


def test_attrition_binary_encoding_centralized():
    """Verify Attrition binary mapping is centralized and used in correlation matrix."""
    assert ATTRITION_BINARY_MAPPING == {"Yes": 1, "No": 0}

    df = pd.DataFrame(
        {
            ID_COLUMN: [1, 2, 3, 4],
            "Age": [25, 30, 35, 40],
            "Education": [1, 2, 3, 4],
            "MonthlyIncome": [3000, 4000, 5000, 6000],
            "Attrition": ["Yes", "No", "Yes", "No"],
        }
    )
    corr = calculate_correlation_matrix(df)
    assert ID_COLUMN not in corr.columns
    assert "AttritionBinary" in corr.columns
    assert "Education" in corr.columns
    assert corr.loc["AttritionBinary", "AttritionBinary"] == 1.0


def test_get_dataset_info_utility():
    """Verify get_dataset_info returns accurate dataset metrics."""
    df = pd.DataFrame(
        {
            "A": [1, 2, 2, None],
            "B": ["x", "y", "y", "z"],
        }
    )
    info = get_dataset_info(df)
    assert info["rows"] == 4
    assert info["columns"] == 2
    assert info["missing_cells"] == 1
    assert info["duplicate_rows"] == 1


def test_direct_binning_analysis():
    """Verify analyze_* functions accept raw/un-binned data without pre-binning."""
    df = pd.DataFrame(
        {
            ID_COLUMN: [1, 2, 3, 4],
            "MonthlyIncome": [2000, 4500, 8000, 15000],
            "Age": [22, 30, 40, 58],
            "YearsAtCompany": [1, 4, 8, 22],
            "Attrition": ["Yes", "No", "No", "Yes"],
        }
    )
    salary_res = analyze_salary_band(df)
    assert "SalaryBand" in salary_res.columns
    assert "AttritionRate" in salary_res.columns

    age_res = analyze_age_group(df)
    assert "AgeGroup" in age_res.columns
    assert "AttritionRate" in age_res.columns

    tenure_res = analyze_tenure(df)
    assert "TenureGroup" in tenure_res.columns
    assert "AttritionRate" in tenure_res.columns


def test_visualization_reuse_and_heatmap_refactoring():
    """Verify visualizations execute cleanly using shared analysis functions."""
    df = pd.DataFrame(
        {
            ID_COLUMN: [1, 2, 3, 4],
            "Department": ["Sales", "Sales", "IT", "IT"],
            "JobRole": ["Manager", "Rep", "Dev", "Lead"],
            "OverTime": ["Yes", "No", "Yes", "No"],
            "JobSatisfaction": [1, 2, 3, 4],
            "Age": [25, 30, 35, 40],
            "Education": [2, 3, 4, 5],
            "MonthlyIncome": [3000, 4000, 5000, 6000],
            "Attrition": ["Yes", "No", "No", "Yes"],
        }
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        plot_attrition_by_department(df, tmp_path)
        plot_attrition_by_job_role(df, tmp_path)
        plot_overtime_vs_attrition(df, tmp_path)
        plot_satisfaction_vs_attrition(df, tmp_path)
        plot_correlation_heatmap(df, tmp_path)

        assert (tmp_path / "attrition_by_department.png").exists()
        assert (tmp_path / "attrition_by_job_role.png").exists()
        assert (tmp_path / "overtime_vs_attrition.png").exists()
        assert (tmp_path / "satisfaction_vs_attrition.png").exists()
        assert (tmp_path / "correlation_heatmap.png").exists()
