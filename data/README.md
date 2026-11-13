# 📂 `data/` - Dataset Specifications & Schema Reference

This directory manages the raw and processed datasets utilized by the **Employee Attrition Analysis** platform.

---

## 🗂️ Directory Structure

```text
data/
├── raw/                                      # Immutable raw input datasets
│   └── employee_attrition_messy_8040.csv     # Bundled benchmark dataset (8,040 rows, 29 cols)
├── processed/                                # Pipeline output directory
│   └── employee_attrition_cleaned.csv        # Sanitized, deduplicated, and imputed dataset
└── README.md                                 # This specification guide
```

---

> 💡 **Uploading your own file?** See the step-by-step [User Upload Guide](../USER_UPLOAD_GUIDE.md) for quick checklist, column auto-mapping rules, and do's & don'ts.

---

## 🔒 Immutability Rule

> **CRITICAL RULE**: Files inside `data/raw/` are treated as strictly **read-only**.
> The automated pipeline (`main.py`) and Streamlit application (`app.py`) **never** overwrite or mutate raw data. Sanitized datasets are always written to `data/processed/`.

---

## 📋 Canonical Schema Specification

The platform expects or maps columns into the following **29 canonical attributes**:

### 1. Mandatory Column

| Canonical Column | Type | Allowed / Recognized Values | Description |
| :--- | :--- | :--- | :--- |
| **`Attrition`** | String / Bool / Int | `"Yes"`, `"No"`, `1`, `0`, `True`, `False`, `"left"`, `"stayed"`, `"terminated"`, `"employed"` | Primary target variable indicating employee turnover. |

*Note: Only `Attrition` is strictly required. Any dataset containing `Attrition` will be processed, but **no extra entities/columns outside these 29 canonical attributes are permitted**. Any unrecognized extra entities will trigger an immediate schema error with details.*

---

### 2. Optional Demographics & Personal Attributes

| Canonical Column | Type | Valid Range / Categories | Common Aliases |
| :--- | :--- | :--- | :--- |
| **`EmployeeID`** | Integer / String | Positive integer / unique identifier | `id`, `emp_id`, `staff_id`, `badge_id`, `emp_no` |
| **`Age`** | Integer | 18 to 100 years | `age`, `employee_age`, `age_years` |
| **`Gender`** | String | `"Male"`, `"Female"` | `gender`, `sex` |
| **`MaritalStatus`** | String | `"Single"`, `"Married"`, `"Divorced"` | `marital_status`, `marital` |
| **`Education`** | Ordinal (1–5) / String | `1` / `"Below College"`, `2` / `"College"`, `3` / `"Bachelor"`, `4` / `"Master"`, `5` / `"Doctor"` | `education`, `education_level`, `qualification`, `degree` |
| **`EducationField`** | String | `"Life Sciences"`, `"Medical"`, `"Marketing"`, `"Technical Degree"`, `"Human Resources"`, `"Other"` | `education_field`, `field_of_study`, `major` |

---

### 3. Optional Organizational & Role Attributes

| Canonical Column | Type | Valid Range / Categories | Common Aliases |
| :--- | :--- | :--- | :--- |
| **`Department`** | String | `"Research & Development"`, `"Sales"`, `"Human Resources"` | `dept`, `dept_name`, `division`, `business_unit` |
| **`JobRole`** | String | `"Sales Executive"`, `"Research Scientist"`, `"Laboratory Technician"`, `"Manufacturing Director"`, `"Healthcare Representative"`, `"Manager"`, etc. | `role`, `work_role`, `job_title`, `title`, `position` |
| **`JobLevel`** | Integer | 1 to 5 | `job_level`, `grade`, `seniority_level` |
| **`MonthlyIncome`** | Float / Integer | ₹1,000 to ₹50,000 (INR or standard currency) | `salary`, `monthly_salary`, `income`, `pay`, `base_pay` |
| **`StockOptionLevel`**| Integer | 0 to 3 | `stock_options`, `equity_tier` |
| **`PercentSalaryHike`**| Float | 0% to 50% | `salary_hike`, `hike_percent`, `raise_percentage` |

---

### 4. Optional Work Patterns & Satisfaction Survey Scores

| Canonical Column | Type | Valid Range / Categories | Common Aliases |
| :--- | :--- | :--- | :--- |
| **`OverTime`** | String | `"Yes"`, `"No"` | `overtime`, `ot`, `extra_hours` |
| **`BusinessTravel`** | String | `"Travel_Rarely"`, `"Travel_Frequently"`, `"Non-Travel"` | `travel_frequency`, `travel` |
| **`RemoteWork`** | String | `"Yes"`, `"No"` | `is_remote`, `work_from_home`, `wfh` |
| **`AverageWeeklyHours`**| Float | 20 to 80 hours | `weekly_hours`, `hours_per_week` |
| **`JobSatisfaction`** | Integer (1–4) | 1 (Low), 2 (Medium), 3 (High), 4 (Very High) | `job_satisfaction`, `job_satisfaction_score` |
| **`EnvironmentSatisfaction`** | Integer (1–4) | 1 (Low), 2 (Medium), 3 (High), 4 (Very High) | `work_environment`, `environment_score` |
| **`RelationshipSatisfaction`** | Integer (1–4) | 1 (Low), 2 (Medium), 3 (High), 4 (Very High) | `team_satisfaction`, `peers_satisfaction` |
| **`WorkLifeBalance`** | Integer (1–4) | 1 (Bad), 2 (Good), 3 (Better), 4 (Best) | `wlb`, `worklife_balance`, `balance` |
| **`PerformanceRating`**| Integer | 1 to 5 | `rating`, `performance`, `appraisal_rating` |

---

### 5. Optional History & Experience Attributes

| Canonical Column | Type | Valid Range / Categories | Common Aliases |
| :--- | :--- | :--- | :--- |
| **`YearsAtCompany`** | Integer | 0 to 45 years | `tenure`, `company_tenure`, `years_with_company` |
| **`YearsInCurrentRole`**| Integer | 0 to 45 years | `role_tenure`, `years_in_role` |
| **`TotalWorkingYears`**| Integer | 0 to 50 years | `total_experience`, `total_tenure` |
| **`NumCompaniesWorked`**| Integer | 0 to 15 | `companies_worked`, `prior_employers` |
| **`NumProjects`** | Integer | 1 to 15 | `projects_count`, `projects` |
| **`DistanceFromHome`** | Float | 0 to 100 km / miles | `commute_distance`, `distance` |
| **`TrainingTimesLastYear`**| Integer | 0 to 10 | `training_hours`, `trainings` |

---

## 📤 Supported Input Formats & Encodings

The ingestion engine supports:
- **Comma-Separated Values (`.csv`)**
  - Automatic encoding detection: `utf-8`, `utf-8-sig`, `latin-1`, `cp1252`.
- **Microsoft Excel (`.xlsx`, `.xls`)**
  - Parsed using `openpyxl`.

---

## 📝 Sample CSV Template

Below is a minimum viable sample format:

```csv
EmployeeID,Attrition,Department,JobRole,MonthlyIncome,Age,YearsAtCompany,OverTime
1001,No,Research & Development,Research Scientist,6500,34,5,No
1002,Yes,Sales,Sales Executive,4200,28,2,Yes
1003,No,Human Resources,HR Specialist,5100,41,8,No
1004,Yes,Research & Development,Laboratory Technician,3800,24,1,Yes
```

*(You can also download a comprehensive ready-to-use template directly from the Streamlit dashboard sidebar).*
