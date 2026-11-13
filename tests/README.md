# 🧪 `tests/` - Automated Testing Suite & QA Guide

This directory houses the automated test suite for the **Employee Attrition Analysis** platform, built using `pytest`.

---

## 🗂️ Test Architecture

```text
tests/
├── __init__.py                    # (Optional) Test package namespace
├── test_dynamic_ingestion.py      # Multi-format ingestion, column auto-mapping, partial schema, CLI
├── test_phase2_remediation.py     # Schema fixes, DRY compliance, education ordinal mapping
├── test_preprocessing.py          # Data cleaning, deduplication, imputation, range checks
└── README.md                      # This test suite guide
```

---

## ⚙️ Configuration (`pytest.ini`)

Test discovery and execution parameters are defined in the repository root:

```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

*Note: `pythonpath = .` guarantees that imports like `import config` and `from src.analysis import ...` resolve reliably without requiring manual environment variable hacks.*

---

## 📋 Test Modules Overview (52 Tests Total)

### 1. `test_dynamic_ingestion.py` (36 Tests)
Verifies multi-format file reading, column mapping intelligence, dynamic schema resilience, and strict schema validation:
- **Column Normalization & Mapping**: Tests `normalize_column_name()`, exact matches, 4-tier resolution (exact $\rightarrow$ normalized $\rightarrow$ alias $\rightarrow$ fuzzy), and unmapped header categorization.
- **Strict Schema Enforcement (No Extra Entities)**: Tests `test_validate_dynamic_schema_extra_entities`, `test_validate_dynamic_schema_multiple_extra_entities`, and `test_cli_rejects_file_with_extra_entities` verifying that files with unexpected extra columns (e.g. `Bonus`, `Country`, `Hobbies`) fail validation immediately with detailed error diagnostics.
- **Dynamic Ingestion (CSV & Excel)**:
  - Reads CSVs from file paths, `io.StringIO`, and `io.BytesIO`.
  - Tests UTF-8 and Latin-1 fallback decoding.
  - Reads Excel `.xlsx` files from disk and bytes buffers.
  - Rejects unsupported extensions (`.parquet`, etc.) with informative `ValueError`.
- **Dynamic Schema Validation**:
  - Passes when mandatory `Attrition` column is present.
  - Fails when `Attrition` is absent.
- **Flexible Target Standardization**: Parameterized tests verifying that varied attrition values (`Yes`/`No`, `1`/`0`, `True`/`False`, `left`/`stayed`, `terminated`/`employed`, `voluntarily separated`/`active`) are accurately converted to `"Yes"` and `"No"`.
- **Partial-Schema Resiliency**: Verifies that analytical functions (`analyze_department`, `analyze_job_role`, `generate_summary_tables`) and visualization routines gracefully skip missing columns without raising `KeyError`.
- **CLI Batch Processing**: Subprocess integration tests executing `main.py --input <custom_csv>` and `main.py --input <custom_excel>`.

### 2. `test_preprocessing.py` (8 Tests)
Verifies the deterministic 8-step data cleaning pipeline:
- `test_standardize_categorical_values`: Trims whitespace and standardizes casing.
- `test_remove_duplicate_rows`: Drops identical duplicate records.
- `test_remove_duplicate_employee_ids`: Eliminates duplicate `EmployeeID` entries.
- `test_handle_invalid_numerical_values`: Replaces out-of-range numerical anomalies with `NaN`.
- `test_handle_missing_target`: Drops rows with missing or unparseable target values.
- `test_handle_missing_values`: Validates median imputation for numbers and mode imputation for categories.
- `test_preprocess_dataset`: Verifies end-to-end cleaning pipeline execution.
- `test_required_columns_are_preserved`: Ensures no features are accidentally dropped.

### 3. `test_phase2_remediation.py` (8 Tests)
Verifies architectural fixes, schema rectifications, and DRY remediations:
- `test_education_classification_and_mapping`: Validates ordinal numerical mapping (1–5) for `Education`.
- `test_education_invalid_range_handling`: Validates invalid education levels are clamped.
- `test_satisfaction_columns_centralized`: Verifies single source of truth for satisfaction features.
- `test_attrition_binary_encoding_centralized`: Tests binary 1/0 mapping for correlations.
- `test_get_dataset_info_utility`: Verifies health check statistics helper.
- `test_direct_binning_analysis`: Verifies dynamic bins in `analysis.py` (`SalaryBand`, `AgeGroup`, `TenureGroup`).
- `test_visualization_reuse_and_heatmap_refactoring`: Verifies DRY reuse of analysis helper functions inside visualization routines.

---

## 🏃 How to Run the Tests

### 1. Run Complete Test Suite
From the repository root:
```bash
pytest -v
```

### 2. Run a Single Test Module
```bash
pytest tests/test_dynamic_ingestion.py -v
```

### 3. Run a Specific Test Function
```bash
pytest tests/test_dynamic_ingestion.py -k "test_cli_custom_input_csv" -v
```

### 4. Run with Output Printing (`-s`)
```bash
pytest -s -v
```

---

## ✍️ Guidelines for Adding New Tests

1. **Use Pytest Fixtures**: Utilize built-in fixtures like `tmp_path` for temporary file creation to avoid polluting project directories.
2. **Defensive Assertions**: When testing custom schema behaviors, assert both the presence of valid outputs and the absence of exceptions for missing columns.
3. **Parametrize Variations**: Use `@pytest.mark.parametrize` when testing multi-value mappings (e.g., target encodings or column aliases).
4. **Never Modify `data/raw/`**: Unit tests should build mock DataFrames in-memory or write temporary files to `tmp_path`.
