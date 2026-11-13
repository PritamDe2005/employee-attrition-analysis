"""
Tests for dynamic CSV/Excel file ingestion, column mapping, and partial schema resiliency.
"""

import io
from pathlib import Path
import pandas as pd
import pytest

from config import (
    COLUMN_ALIASES,
    FLEXIBLE_ATTRITION_MAPPING,
    MANDATORY_COLUMNS,
    SUPPORTED_FILE_EXTENSIONS,
)
from src.analysis import (
    analyze_department,
    analyze_job_role,
    analyze_salary_band,
    calculate_attrition_rate,
    calculate_correlation_matrix,
    generate_summary_tables,
)
from src.column_mapper import (
    apply_column_mapping,
    detect_available_dimensions,
    normalize_column_name,
    resolve_column_mapping,
)
from src.data_loader import (
    load_dataset_from_source,
    validate_dynamic_schema,
)
from src.preprocessing import (
    preprocess_dataset,
    standardize_categorical_values,
)
from src.visualization import (
    plot_attrition_by_department,
    plot_correlation_heatmap,
    plot_salary_vs_attrition,
)


# ---------------------------------------------------------------------------
# Test: Column normalization and mapping
# ---------------------------------------------------------------------------

def test_normalize_column_name():
    """Test standardizing column string names."""
    assert normalize_column_name("Monthly Income") == "monthly_income"
    assert normalize_column_name("years_at_company") == "years_at_company"
    assert normalize_column_name("  Job-Role! ") == "job_role"
    assert normalize_column_name("EMP_ID#") == "emp_id"


def test_resolve_column_mapping_exact():
    """Exact column names should map to themselves with 1.0 confidence."""
    columns = ["Attrition", "Department", "MonthlyIncome", "Age"]
    mapping, unmapped = resolve_column_mapping(columns)

    assert mapping["Attrition"] == "Attrition"
    assert mapping["Department"] == "Department"
    assert mapping["MonthlyIncome"] == "MonthlyIncome"
    assert mapping["Age"] == "Age"
    assert len(unmapped) == 0


def test_resolve_column_mapping_aliases_and_fuzzy():
    """Common synonyms and snake_case should map to canonical columns."""
    columns = [
        "left_company",     # alias for Attrition
        "salary",           # alias for MonthlyIncome
        "dept",             # alias for Department
        "tenure",           # alias for YearsAtCompany
        "work_role",        # alias for JobRole
        "custom_notes_col", # unknown column
    ]
    mapping, unmapped = resolve_column_mapping(columns)

    assert mapping["left_company"] == "Attrition"
    assert mapping["salary"] == "MonthlyIncome"
    assert mapping["dept"] == "Department"
    assert mapping["tenure"] == "YearsAtCompany"
    assert mapping["work_role"] == "JobRole"
    assert "custom_notes_col" in unmapped


def test_apply_column_mapping():
    """Applying mapping renames columns and leaves unmapped columns intact."""
    df = pd.DataFrame({
        "salary": [50000, 60000],
        "left": ["Yes", "No"],
        "extra_info": ["A", "B"],
    })
    mapping = {"salary": "MonthlyIncome", "left": "Attrition"}
    mapped_df = apply_column_mapping(df, mapping)

    assert "MonthlyIncome" in mapped_df.columns
    assert "Attrition" in mapped_df.columns
    assert "extra_info" in mapped_df.columns
    assert "salary" not in mapped_df.columns


def test_detect_available_dimensions():
    """Detect available dimensions based on canonical columns present."""
    df = pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "Department": ["Sales", "R&D"],
        "MonthlyIncome": [5000, 6000],
    })
    dims = detect_available_dimensions(df)

    assert dims["attrition"] is True
    assert dims["department"] is True
    assert dims["salary"] is True
    assert dims["job_role"] is False
    assert dims["overtime"] is False
    assert dims["satisfaction"] is False


# ---------------------------------------------------------------------------
# Test: Dynamic schema validation
# ---------------------------------------------------------------------------

def test_validate_dynamic_schema_valid():
    """Schema is valid as long as Attrition is present."""
    df = pd.DataFrame({"Attrition": ["Yes", "No"]})
    # Should not raise
    validate_dynamic_schema(df)


def test_validate_dynamic_schema_missing_attrition():
    """Schema validation raises ValueError if Attrition is missing."""
    df = pd.DataFrame({"Department": ["Sales", "R&D"], "MonthlyIncome": [5000, 6000]})
    with pytest.raises(ValueError, match=r"missing mandatory column.*Attrition"):
        validate_dynamic_schema(df)


# ---------------------------------------------------------------------------
# Test: File loading (CSV encodings & Excel)
# ---------------------------------------------------------------------------

def test_load_dataset_csv_string_and_bytes():
    """Test loading CSV from string path, StringIO, and BytesIO."""
    csv_content = "Attrition,Department,Age\nYes,Sales,35\nNo,R&D,28\n"
    
    # BytesIO
    buffer = io.BytesIO(csv_content.encode("utf-8"))
    df = load_dataset_from_source(buffer, filename="upload.csv")
    assert len(df) == 2
    assert list(df.columns) == ["Attrition", "Department", "Age"]

    # Latin-1 encoded CSV
    latin1_csv = "Attrition,Department,Age\nYes,Café Ops,35\nNo,R&D,28\n".encode("latin-1")
    buffer_latin1 = io.BytesIO(latin1_csv)
    df_latin1 = load_dataset_from_source(buffer_latin1, filename="latin1.csv")
    assert len(df_latin1) == 2


def test_load_dataset_excel(tmp_path: Path):
    """Test loading Excel file (.xlsx) from disk and BytesIO buffer."""
    sample_df = pd.DataFrame({
        "Attrition": ["Yes", "No", "No"],
        "Department": ["Sales", "HR", "R&D"],
        "MonthlyIncome": [4000, 5000, 6000],
    })
    excel_file = tmp_path / "test_data.xlsx"
    sample_df.to_excel(excel_file, index=False)

    # Load from Path
    df_loaded = load_dataset_from_source(excel_file)
    assert len(df_loaded) == 3
    assert set(df_loaded.columns) == {"Attrition", "Department", "MonthlyIncome"}

    # Load from BytesIO buffer
    with open(excel_file, "rb") as f:
        excel_bytes = io.BytesIO(f.read())
    df_buffer = load_dataset_from_source(excel_bytes, filename="test_data.xlsx")
    assert len(df_buffer) == 3


def test_load_dataset_unsupported_format():
    """Unsupported extension raises ValueError."""
    buffer = io.BytesIO(b"data")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        load_dataset_from_source(buffer, filename="data.parquet")


# ---------------------------------------------------------------------------
# Test: Flexible Attrition values mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw_val, expected_val",
    [
        ("yes", "Yes"),
        ("no", "No"),
        ("YES", "Yes"),
        ("NO", "No"),
        ("1", "Yes"),
        ("0", "No"),
        (1, "Yes"),
        (0, "No"),
        ("true", "Yes"),
        ("false", "No"),
        (True, "Yes"),
        (False, "No"),
        ("left", "Yes"),
        ("stayed", "No"),
        ("voluntarily separated", "Yes"),
        ("active", "No"),
        ("terminated", "Yes"),
        ("employed", "No"),
    ],
)
def test_flexible_attrition_values(raw_val, expected_val):
    """All standard representations of binary attrition should map cleanly."""
    df = pd.DataFrame({"Attrition": [raw_val]})
    cleaned = standardize_categorical_values(df)
    assert cleaned["Attrition"].iloc[0] == expected_val


# ---------------------------------------------------------------------------
# Test: Analysis resiliency with partial schemas
# ---------------------------------------------------------------------------

def test_partial_schema_analysis():
    """Pipelines and analysis functions must work on datasets with only a subset of columns."""
    df = pd.DataFrame({
        "Attrition": ["Yes", "No", "Yes", "No"],
        "Department": ["Sales", "Sales", "R&D", "R&D"],
        "MonthlyIncome": [4000, 5000, 7000, 8000],
    })

    # Available dimensions work
    dept_res = analyze_department(df)
    assert not dept_res.empty
    assert "Department" in dept_res.columns
    assert "AttritionRate" in dept_res.columns

    # Missing dimensions return empty DataFrame without throwing KeyError
    job_res = analyze_job_role(df)
    assert job_res.empty

    salary_res = analyze_salary_band(df)
    assert not salary_res.empty
    assert "SalaryBand" in salary_res.columns


def test_generate_summary_tables_partial_schema():
    """generate_summary_tables generates only keys for present dimensions."""
    df = pd.DataFrame({
        "Attrition": ["Yes", "No", "No", "Yes"],
        "Department": ["Sales", "HR", "Sales", "HR"],
    })
    tables = generate_summary_tables(df)

    assert "attrition" in tables
    assert "department" in tables
    assert "job_role" not in tables
    assert "salary_band" not in tables
    assert "satisfaction" not in tables


def test_visualization_partial_schema_resilience(tmp_path: Path):
    """Visualization functions gracefully return None when required column is absent."""
    df = pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "Department": ["Sales", "R&D"],
    })

    # Missing MonthlyIncome should not raise an exception
    fig_salary = plot_salary_vs_attrition(df, output_directory=tmp_path)
    assert fig_salary is None

    # Missing enough numeric columns for heatmap should not raise an exception
    fig_corr = plot_correlation_heatmap(df, output_directory=tmp_path)
    assert fig_corr is None


def test_preprocess_dynamic_dataset():
    """End-to-end preprocessing on a custom dynamic dataset with aliases."""
    raw_df = pd.DataFrame({
        "emp_num": [101, 102, 103, 104],
        "left_org": ["left", "stayed", "left", "stayed"],
        "dept_name": ["Sales", "Sales", "HR", "R&D"],
        "salary_in_inr": [45000, 65000, 55000, 80000],
        "age_years": [25, 42, 38, 51],
    })

    # Map columns
    mapping, _ = resolve_column_mapping(list(raw_df.columns))
    standard_df = apply_column_mapping(raw_df, mapping)
    validate_dynamic_schema(standard_df)

    from src.analysis import create_age_group, create_salary_band

    # Preprocess
    cleaned_df = preprocess_dataset(standard_df)

    assert set(cleaned_df["Attrition"].unique()).issubset({"Yes", "No"})
    assert "Department" in cleaned_df.columns
    assert "MonthlyIncome" in cleaned_df.columns
    assert "Age" in cleaned_df.columns

    # Dynamic binning in analysis
    binned_df = create_salary_band(cleaned_df)
    binned_df = create_age_group(binned_df)
    assert "SalaryBand" in binned_df.columns
    assert "AgeGroup" in binned_df.columns


# ---------------------------------------------------------------------------
# Test: CLI batch execution with --input
# ---------------------------------------------------------------------------

def test_cli_custom_input_csv(tmp_path: Path):
    """Test running main.py with --input flag on a custom CSV."""
    import subprocess
    import sys

    custom_csv = tmp_path / "custom_employees.csv"
    sample_df = pd.DataFrame({
        "staff_id": [1, 2, 3, 4],
        "left": ["Yes", "No", "No", "Yes"],
        "dept": ["Sales", "R&D", "Sales", "HR"],
        "salary": [4000, 7000, 5000, 6000],
    })
    sample_df.to_csv(custom_csv, index=False)

    result = subprocess.run(
        [sys.executable, "main.py", "--input", str(custom_csv)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Employee Attrition Analysis completed successfully" in result.stderr


def test_cli_custom_input_excel(tmp_path: Path):
    """Test running main.py with --input flag on a custom Excel file (.xlsx)."""
    import subprocess
    import sys

    custom_excel = tmp_path / "custom_employees.xlsx"
    sample_df = pd.DataFrame({
        "staff_id": [10, 20, 30, 40],
        "left": ["No", "Yes", "No", "No"],
        "dept": ["Sales", "R&D", "Sales", "HR"],
        "salary": [8000, 9500, 6200, 5800],
    })
    sample_df.to_excel(custom_excel, index=False)

    result = subprocess.run(
        [sys.executable, "main.py", "--input", str(custom_excel)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Employee Attrition Analysis completed successfully" in result.stderr


def test_validate_dynamic_schema_extra_entities():
    """Schema validation raises ValueError if any unexpected extra column/entity is present."""
    df = pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "Department": ["Sales", "R&D"],
        "UnexpectedBonus": [5000, 7000],
    })
    with pytest.raises(ValueError, match=r"unexpected extra entity/column\(s\).*UnexpectedBonus"):
        validate_dynamic_schema(df)


def test_validate_dynamic_schema_multiple_extra_entities():
    """Schema validation details all unexpected extra entities."""
    df = pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "Bonus": [1000, 2000],
        "Country": ["USA", "India"],
        "Hobbies": ["Music", "Chess"],
    })
    with pytest.raises(ValueError) as exc_info:
        validate_dynamic_schema(df)

    err_msg = str(exc_info.value)
    assert "unexpected extra entity/column(s)" in err_msg
    assert "Bonus" in err_msg
    assert "Country" in err_msg
    assert "Hobbies" in err_msg


def test_cli_rejects_file_with_extra_entities(tmp_path: Path):
    """CLI fails and reports error details when uploaded file has extra entities not in sample CSV."""
    import subprocess
    import sys

    bad_csv = tmp_path / "bad_employees.csv"
    bad_df = pd.DataFrame({
        "Attrition": ["Yes", "No"],
        "Department": ["Sales", "HR"],
        "UnknownEntityCol": ["X", "Y"],
    })
    bad_df.to_csv(bad_csv, index=False)

    result = subprocess.run(
        [sys.executable, "main.py", "--input", str(bad_csv)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "unexpected extra entity/column(s)" in result.stderr
    assert "UnknownEntityCol" in result.stderr



