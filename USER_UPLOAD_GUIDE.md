# 📤 File Upload & Data Preparation Guidelines

This guide explains how to prepare, format, and upload your employee dataset into the **Employee Attrition Analysis** platform.

The platform includes an **intelligent ingestion engine** that automatically cleans data, reconciles inconsistent column names, and adapts dashboards to your dataset's available dimensions.

---

## 📌 Summary Checklist

Before uploading your file, verify:

- [x] **File Extension**: Saved as `.csv`, `.xlsx`, or `.xls`.
- [x] **Single Header Row**: The first row contains column headers (no merged headers or multi-row titles).
- [x] **Mandatory Column**: Contains an **`Attrition`** column (or recognizable synonym like `left`, `turnover`, `status`).
- [x] **No Extra Entities**: Contains no extra columns/entities outside the sample CSV schema.
- [x] **One Row per Employee**: Each row represents an individual employee record.
- [x] **No Summary Rows**: Remove any `Total`, `Average`, or `Subtotal` rows at the bottom of the spreadsheet.

---

## 📁 1. Supported File Formats & Encodings

| Format | Extension | Notes |
| :--- | :--- | :--- |
| **CSV** | `.csv` | Encoded in `UTF-8`, `UTF-8-SIG`, `Latin-1`, or `CP1252` (automatically detected). |
| **Microsoft Excel** | `.xlsx`, `.xls` | Standard single-sheet or active first-sheet workbook. |

*File size limit: Up to 200MB (standard Streamlit upload threshold).*

---

## 🎯 2. The Mandatory Target Column: `Attrition`

The platform only requires **one mandatory column**: the target variable indicating whether an employee left or stayed.

### Recognized Column Names for Attrition:
You do not need to name it exactly `Attrition`. Any of the following synonyms are automatically mapped:
- `Attrition`
- `left` or `left_company` or `left_org`
- `turnover`
- `churn`
- `status` or `employment_status`
- `resigned`
- `separated` or `voluntary_separation`
- `exit`

### Accepted Values for Attrition:
The system automatically translates all standard representations of binary attrition:

| Outcome | Recognized Input Values (Case-Insensitive) |
| :--- | :--- |
| **Employee Left (Yes)** | `Yes`, `1`, `True`, `left`, `terminated`, `resigned`, `separated`, `voluntarily separated`, `attrited`, `exit` |
| **Employee Stayed (No)**| `No`, `0`, `False`, `stayed`, `active`, `current`, `retained`, `employed`, `working` |

---

## 🧩 3. Optional Columns & Automatic Column Aliases

All other columns are **completely optional**. If a column is present in your dataset, the platform will automatically unlock the corresponding analysis. If absent, the engine gracefully skips that section without crashing.

The engine uses a **4-tier matching algorithm** (Exact $\rightarrow$ Normalized $\rightarrow$ Synonyms $\rightarrow$ Fuzzy matching). You do not need to rename your columns:

| Analysis Dimension | Canonical Column | Synonyms & Headers Automatically Detected |
| :--- | :--- | :--- |
| **Employee ID** | `EmployeeID` | `emp_id`, `id`, `staff_id`, `emp_no`, `emp_num`, `badge_id`, `employee_number` |
| **Department** | `Department` | `dept`, `dept_name`, `division`, `business_unit`, `team`, `functional_area` |
| **Job Role** | `JobRole` | `role`, `work_role`, `job_title`, `title`, `position`, `designation`, `job` |
| **Salary / Compensation**| `MonthlyIncome` | `salary`, `monthly_salary`, `monthly_income`, `income`, `earnings`, `pay`, `base_pay`, `gross_salary`, `salary_in_inr`, `salary_amount` |
| **Tenure** | `YearsAtCompany` | `tenure`, `company_tenure`, `years_with_company`, `length_of_service`, `years_at_company` |
| **Age** | `Age` | `age`, `employee_age`, `age_years` |
| **Overtime** | `OverTime` | `overtime`, `over_time`, `ot`, `extra_hours` (`Yes`/`No`) |
| **Work-Life Balance** | `WorkLifeBalance` | `wlb`, `worklife_balance`, `balance` (Rating 1–4) |
| **Job Satisfaction** | `JobSatisfaction` | `job_satisfaction`, `satisfaction`, `job_satisfaction_score` (Rating 1–4) |
| **Environment Satisfaction**| `EnvironmentSatisfaction`| `work_environment`, `environment_satisfaction`, `environment_score` (Rating 1–4) |
| **Relationship Satisfaction**| `RelationshipSatisfaction`| `relationship_satisfaction`, `team_satisfaction`, `peers_satisfaction` (Rating 1–4) |
| **Travel Frequency** | `BusinessTravel` | `business_travel`, `travel_frequency`, `travel` (`Non-Travel`, `Travel_Rarely`, `Travel_Frequently`) |
| **Remote Work** | `RemoteWork` | `remote_work`, `is_remote`, `work_from_home`, `wfh` (`Yes`/`No`) |
| **Total Experience** | `TotalWorkingYears` | `total_working_years`, `total_experience`, `total_tenure`, `experience_years` |
| **Education Level** | `Education` | `education`, `education_level`, `qualification`, `degree` (1–5 or Text like `Bachelor`, `Master`) |

> 🛑 **STRICT SCHEMA RULE — NO EXTRA ENTITIES:**  
> The uploaded file **must not contain any extra entities/columns** with respect to the sample CSV.  
> If any unexpected or unrecognized entity is detected (e.g., `Bonus`, `Country`, `Hobbies`), the system will halt execution immediately and display a detailed error listing every extra entity found along with the allowed sample schema.

---

## 🤖 4. What the System Cleans Automatically

You don't need to spend hours cleaning your spreadsheet before uploading! The platform automatically performs:

1. **Whitespace & Casing Standardization**: Strips accidental leading/trailing spaces (e.g. `" Sales "` $\rightarrow$ `"Sales"`, `"MALE"` $\rightarrow$ `"Male"`).
2. **Deduplication**: Detects and drops duplicate rows and duplicate employee IDs.
3. **Outlier Filtering**: Clamps impossible numbers (e.g., negative tenure, age $< 18$ or $> 100$).
4. **Missing Value Imputation**:
   - Numbers (Salary, Age, Tenure) are imputed using the **column median**.
   - Categories (Department, Job Role, Overtime) are imputed using the **column mode**.
5. **Dynamic Binning**: Groups continuous variables into meaningful HR cohorts:
   - *Salary Bands*: `< ₹3k`, `₹3k–₹5k`, `₹5k–₹10k`, `₹10k–₹15k`, `₹15k+`
   - *Age Groups*: `< 25`, `25–34`, `35–44`, `45–54`, `55+`
   - *Tenure Groups*: `0–2 Years`, `3–5 Years`, `6–10 Years`, `11–20 Years`, `20+ Years`

---

## ⚠️ 5. Best Practices: Do's and Don'ts

### ✅ DO:
- **Do keep one header row**: The very first row of your CSV/Excel file should contain column names.
- **Do provide an Attrition column**: Even a minimal dataset with just `Department` and `Attrition` will produce full department turnover analytics!
- **Do use consistent categories**: While casing is normalized, having standard departmental names (`Sales`, `Engineering`, `HR`) produces cleaner charts.

### ❌ DON'T:
- **Don't merge cells in Excel**: Avoid merged headers or summary cells across columns.
- **Don't include formulas with errors**: Ensure cells with Excel formulas do not evaluate to `#REF!`, `#VALUE!`, or `#N/A`.
- **Don't include totals or subtotals**: Remove footer rows calculating `Total Count` or `Average`, as they will be treated as employee records.
- **Don't worry about column ordering**: Place columns in any sequence; the mapper matches them by name.

---

## 📥 6. How to Download the Sample Template

If you want a pre-formatted spreadsheet to fill in:
1. Launch the dashboard: `streamlit run app.py`
2. In the left sidebar, select **"Upload Custom Dataset (CSV/Excel)"**.
3. Click the **"📥 Download Template (CSV)"** button.
4. Open the template in Excel or Google Sheets, add your data, save, and upload!

---

## 🖥️ 7. How to Upload

### Option A: Via the Streamlit Dashboard
1. Open the dashboard (`streamlit run app.py`).
2. Select **"Upload Custom Dataset (CSV/Excel)"** in the sidebar.
3. Drag and drop your file into the file uploader.
4. Expand **"🗂️ Detected Column Mapping & Schema"** to verify that your columns were recognized.
5. Explore the interactive KPIs, charts, and adaptive filters!

### Option B: Via the Batch CLI Runner
To run batch analytics on your custom file and export tables/figures directly to disk:
```bash
python main.py --input path/to/your_file.xlsx
```
Processed outputs will be saved to `outputs/tables/` and `outputs/figures/`.
