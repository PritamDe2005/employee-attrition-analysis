# 📦 `src/` - Core Application Architecture & Modules

This directory contains the modular Python packages powering the **Employee Attrition Analysis** platform.

Every module follows single-responsibility principles, strict type hinting, and defensive coding against partial schemas.

---

## 🗂️ Module Map

```text
src/
├── __init__.py           # Package initializer
├── column_mapper.py      # Column normalization, synonym matching, and fuzzy resolution
├── data_loader.py        # Multi-format data loading, encodings, and schema validation
├── preprocessing.py      # Data cleaning, type conversion, range checks, and imputation
├── analysis.py           # Statistical aggregation, attrition rates, and dynamic binning
├── visualization.py      # Publication-ready Matplotlib & Seaborn chart generators
├── utils.py              # Directory management, application logging, and file exports
└── README.md             # This document
```

---

## 🔬 Detailed Module Documentation

### 1. `column_mapper.py` — Intelligent Schema Reconciliation

Handles raw, unpredictable column names from user spreadsheets and maps them to canonical project column names.

#### Key Functions:
- **`normalize_column_name(name: str) -> str`**:
  Lowercases text, trims edges, and replaces all non-alphanumeric characters with single underscores.
  - *Example*: `"  Monthly Income ($) "` $\rightarrow$ `"monthly_income"`
- **`resolve_column_mapping(columns: list[str], fuzzy_cutoff: float = 0.85) -> tuple[dict[str, str], list[str]]`**:
  Executes a 4-tier column resolution pipeline:
  1. *Tier 1 (Exact Match)*: Direct canonical match (`Department` $\rightarrow$ `Department`).
  2. *Tier 2 (Normalized Match)*: Normalized canonical match (`department` $\rightarrow$ `Department`).
  3. *Tier 3 (Alias Lookup)*: Checks against `COLUMN_ALIASES` in `config.py` (`salary` $\rightarrow$ `MonthlyIncome`, `left` $\rightarrow$ `Attrition`).
  4. *Tier 4 (Fuzzy Match)*: Uses `difflib.get_close_matches` with similarity cutoff 0.85.
  - *Returns*: `(mapping_dict, unmapped_columns)`.
- **`apply_column_mapping(dataframe: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame`**:
  Renames recognized columns while preserving unmapped custom columns.
- **`detect_available_dimensions(dataframe: pd.DataFrame) -> dict[str, bool]`**:
  Checks for presence of canonical columns and returns boolean flags for available analytical sections (`department`, `job_role`, `salary`, `age`, `tenure`, `satisfaction`, `overtime`, `correlation`).

---

### 2. `data_loader.py` — Multi-Format Ingestion & Dynamic Validation

Provides format-agnostic data loading and schema validation.

#### Key Functions:
- **`load_dataset_from_source(source: str | Path | Any, filename: str | None = None) -> pd.DataFrame`**:
  - Accepts a file path (`str` or `Path`), a file-like stream (`io.BytesIO`, `io.StringIO`), or Streamlit's `UploadedFile`.
  - Determines format using file extension (`.csv`, `.xlsx`, `.xls`).
  - Reads Excel files via `openpyxl`.
  - Reads CSV files with automatic multi-encoding fallback (`utf-8`, `utf-8-sig`, `latin-1`, `cp1252`).
  - Raises `ValueError` for unsupported extensions or empty datasets.
- **`validate_dynamic_schema(dataframe: pd.DataFrame) -> dict`**:
  - Validates that mandatory columns (`Attrition`) exist.
  - Enforces the **Strict Schema Rule**: rejects unexpected extra entities/columns not in `EXPECTED_COLUMNS`.
  - Summarizes present vs. missing optional columns.
  - Raises `ValueError` if `Attrition` is missing or if unexpected extra entities are present.
- **`get_dataset_info(dataframe: pd.DataFrame) -> dict`**:
  - Calculates basic dataset health: row count, column count, missing cell count, and duplicate row count.
- **`load_and_validate_dataset(file_path: Path) -> pd.DataFrame`**:
  - Legacy loader for backward-compatible pipeline execution against `data/raw/`.

---

### 3. `preprocessing.py` — Deterministic Data Cleaning Pipeline

Implements an 8-step cleaning pipeline configured via `config.py`.

#### Pipeline Execution Sequence:
1. **`standardize_categorical_values(df)`**: Cleans string whitespace, harmonizes casing (e.g. `MALE` $\rightarrow$ `Male`), and standardizes `Attrition` using `FLEXIBLE_ATTRITION_MAPPING` (maps `1`, `true`, `left`, `terminated` to `"Yes"` and `0`, `false`, `stayed`, `employed` to `"No"`).
2. **`convert_data_types(df)`**: Converts numeric features to `int64`/`float64`, categorical features to `string`, and maps `Education` strings (`Bachelor`, `Master`, etc.) to ordinal numbers `1`–`5`.
3. **`remove_duplicate_rows(df)`**: Drops exact row duplicates.
4. **`remove_duplicate_employee_ids(df)`**: Drops duplicate `EmployeeID` values, keeping the first occurrence.
5. **`handle_invalid_numerical_values(df)`**: Checks numerical ranges against bounds defined in `config.py` (e.g. `Age`: 18–100, `MonthlyIncome`: 1000–50000) and replaces invalid outliers with `NaN`.
6. **`handle_missing_target(df)`**: Drops rows where `Attrition` is missing or unparseable.
7. **`handle_missing_values(df)`**: Imputes missing values without data leakage:
   - Numerical columns $\rightarrow$ Imputed with column **median**.
   - Categorical columns $\rightarrow$ Imputed with column **mode**.
8. **`validate_cleaned_data(df)`**: Asserts that no `NaN` values remain in the cleaned dataset.

Master entrypoint: **`preprocess_dataset(dataframe: pd.DataFrame) -> pd.DataFrame`**.

---

### 4. `analysis.py` — Analytical Engine & Dynamic Binning

Computes descriptive statistics, rates, and aggregations. All functions are **defensive** against missing columns.

#### Key Functions:
- **`calculate_attrition_rate(dataframe: pd.DataFrame, group_column: str) -> pd.DataFrame`**:
  Calculates `Employees`, `Attrition_Count`, and `AttritionRate` (percentage rounded to 2 decimals).
  - *Dynamic Count Column*: Uses `EmployeeID` if present, falling back to `"Attrition"` count if `EmployeeID` is missing.
- **`analyze_attrition_distribution(dataframe)`**: Returns total counts and percentage split between `"Yes"` and `"No"`.
- **`analyze_department(dataframe)`**: Returns attrition breakdown by department.
- **`analyze_job_role(dataframe)`**: Returns attrition breakdown by job role, sorted by highest turnover.
- **`create_salary_band(dataframe)` / `analyze_salary_band(dataframe)`**: Dynamically cuts `MonthlyIncome` using `SALARY_BINS` (`< 3k`, `3k-5k`, etc.) and computes cohort turnover.
- **`create_age_group(dataframe)` / `analyze_age_group(dataframe)`**: Dynamically cuts `Age` using `AGE_BINS` (`< 25`, `25-34`, etc.).
- **`create_tenure_group(dataframe)` / `analyze_tenure(dataframe)`**: Dynamically cuts `YearsAtCompany` using `TENURE_BINS` (`0-2 Years`, `3-5 Years`, etc.).
- **`analyze_satisfaction(dataframe)`**: Melts survey columns (`JobSatisfaction`, `EnvironmentSatisfaction`, `RelationshipSatisfaction`, `WorkLifeBalance`) and computes turnover per rating (1–4).
- **`analyze_overtime(dataframe)`**: Computes turnover split for overtime vs non-overtime staff.
- **`calculate_correlation_matrix(dataframe) -> pd.DataFrame`**: Encodes `Attrition` to `AttritionBinary` (1/0) and returns a Pearson correlation matrix for all numeric columns.
- **`generate_summary_tables(dataframe) -> dict[str, pd.DataFrame]`**: Produces a dictionary of all available summary tables for batch export or dashboard rendering.

---

### 5. `visualization.py` — Publication-Ready Chart Generators

Renders Matplotlib and Seaborn charts. Guarded against missing dimensions (returns `None` gracefully if required columns are absent).

#### Key Functions:
- `plot_attrition_distribution(df, output_directory)`
- `plot_attrition_by_department(df, output_directory)`
- `plot_attrition_by_job_role(df, output_directory)`
- `plot_salary_vs_attrition(df, output_directory)`
- `plot_attrition_by_salary_band(df, output_directory)`
- `plot_age_vs_attrition(df, output_directory)`
- `plot_tenure_vs_attrition(df, output_directory)`
- `plot_satisfaction_vs_attrition(df, output_directory)`
- `plot_overtime_vs_attrition(df, output_directory)`
- `plot_correlation_heatmap(df, output_directory)`: Visualizes the Pearson correlation matrix using Seaborn heatmap.
- **`generate_all_visualizations(df, output_directory)`**: Orchestrator that generates all available plots and saves them as PNGs (DPI=150).

---

### 6. `utils.py` — Reusable Engineering Helpers

- **`create_project_directories(directories: list[Path]) -> None`**: Ensures required directory tree exists (`mkdir -p`).
- **`configure_logging(level: int = logging.INFO) -> None`**: Sets up standardized ISO-formatted application logging.
- **`save_dataframe(dataframe: pd.DataFrame, output_directory: Path, filename: str) -> Path`**: Saves a DataFrame as CSV and returns the output path.

---

## 🛠️ Developer Extension Guide

### How to Add a New Dimension (e.g. `PerformanceRating`):
1. **Define Aliases & Bounds in `config.py`**:
   ```python
   # In config.py:
   COLUMN_ALIASES["PerformanceRating"] = ["performance_rating", "rating", "performance"]
   ```
2. **Add Analysis Function in `src/analysis.py`**:
   ```python
   def analyze_performance(dataframe: pd.DataFrame) -> pd.DataFrame:
       if "PerformanceRating" not in dataframe.columns or "Attrition" not in dataframe.columns:
           return pd.DataFrame()
       return calculate_attrition_rate(dataframe, "PerformanceRating")
   ```
3. **Add Visualization in `src/visualization.py`**:
   ```python
   def plot_performance_vs_attrition(dataframe: pd.DataFrame, output_directory: Path) -> None:
       if "PerformanceRating" not in dataframe.columns or "Attrition" not in dataframe.columns:
           return
       # Generate plot and save via _save_figure()
   ```
4. **Register in `generate_summary_tables()` & Dashboard (`app.py`)**.
5. **Add Test in `tests/test_dynamic_ingestion.py`**.
