"""
Configuration module for Employee Attrition Analysis.

This module centralizes project paths, dataset configuration,
expected columns, and analysis settings so that values are not
hard-coded throughout the project.
"""

from pathlib import Path


# ---------------------------------------------------------------------------
# Project directories
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
REPORTS_DIR = OUTPUTS_DIR / "reports"


# ---------------------------------------------------------------------------
# Dataset configuration
# ---------------------------------------------------------------------------

RAW_DATA_FILE = RAW_DATA_DIR / "employee_attrition_messy_8040.csv"

PROCESSED_DATA_FILE = (
    PROCESSED_DATA_DIR / "employee_attrition_cleaned.csv"
)


# ---------------------------------------------------------------------------
# Identifier column
# ---------------------------------------------------------------------------

ID_COLUMN = "EmployeeID"


# ---------------------------------------------------------------------------
# Expected dataset columns
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    ID_COLUMN,
    "Age",
    "Gender",
    "MaritalStatus",
    "Education",
    "EducationField",
    "Department",
    "JobRole",
    "JobLevel",
    "MonthlyIncome",
    "OverTime",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
    "PerformanceRating",
    "DistanceFromHome",
    "TrainingTimesLastYear",
    "StockOptionLevel",
    "PercentSalaryHike",
    "NumCompaniesWorked",
    "NumProjects",
    "BusinessTravel",
    "RemoteWork",
    "AverageWeeklyHours",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "TotalWorkingYears",
    "Attrition",
]


# ---------------------------------------------------------------------------
# Categorical columns
# ---------------------------------------------------------------------------

CATEGORICAL_COLUMNS = [
    "Gender",
    "MaritalStatus",
    "EducationField",
    "Department",
    "JobRole",
    "OverTime",
    "BusinessTravel",
    "RemoteWork",
    "Attrition",
]


# ---------------------------------------------------------------------------
# Numerical columns (including ordinal features)
# ---------------------------------------------------------------------------

NUMERICAL_COLUMNS = [
    "Age",
    "Education",
    "JobLevel",
    "MonthlyIncome",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
    "PerformanceRating",
    "DistanceFromHome",
    "TrainingTimesLastYear",
    "StockOptionLevel",
    "PercentSalaryHike",
    "NumCompaniesWorked",
    "NumProjects",
    "AverageWeeklyHours",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "TotalWorkingYears",
]


# ---------------------------------------------------------------------------
# Ordinal feature classifications and mappings
# ---------------------------------------------------------------------------

ORDINAL_COLUMNS = [
    "Education",
    "JobLevel",
    "PerformanceRating",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
]

EDUCATION_MAPPING = {
    "Below College": 1,
    "College": 2,
    "Bachelor": 3,
    "Master": 4,
    "Doctor": 5,
}


# ---------------------------------------------------------------------------
# Satisfaction survey columns
# ---------------------------------------------------------------------------

SATISFACTION_COLUMNS = [
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
]


# ---------------------------------------------------------------------------
# Categorical standardization & binary encodings
# ---------------------------------------------------------------------------

ATTRITION_VALUES = ["Yes", "No"]

ATTRITION_BINARY_MAPPING = {
    "Yes": 1,
    "No": 0,
}

OVERTIME_VALUES = ["Yes", "No"]

GENDER_VALUES = ["Male", "Female"]


# ---------------------------------------------------------------------------
# Analysis configuration
# ---------------------------------------------------------------------------

SALARY_BINS = [
    0,
    3000,
    6000,
    10000,
    float("inf"),
]

SALARY_LABELS = [
    "Low",
    "Medium",
    "High",
    "Very High",
]


AGE_BINS = [
    0,
    25,
    35,
    45,
    55,
    float("inf"),
]

AGE_LABELS = [
    "Under 25",
    "25-34",
    "35-44",
    "45-54",
    "55+",
]


TENURE_BINS = [
    -1,
    2,
    5,
    10,
    20,
    float("inf"),
]

TENURE_LABELS = [
    "0-2 Years",
    "3-5 Years",
    "6-10 Years",
    "11-20 Years",
    "20+ Years",
]


# ---------------------------------------------------------------------------
# General settings
# ---------------------------------------------------------------------------

CSV_ENCODING = "utf-8"

RANDOM_STATE = 42

FIGURE_DPI = 150

FIGURE_FORMAT = "png"

SUPPORTED_FILE_EXTENSIONS = [".csv", ".xlsx", ".xls"]


# ---------------------------------------------------------------------------
# Dynamic Ingestion & Column Aliases
# ---------------------------------------------------------------------------

MANDATORY_COLUMNS = ["Attrition"]

COLUMN_ALIASES = {
    "EmployeeID": [
        "emp_id",
        "employee_id",
        "id",
        "staff_id",
        "emp_no",
        "emp_num",
        "badge_id",
        "employee_number",
    ],
    "Age": ["age", "employee_age", "age_years"],
    "Gender": ["gender", "sex"],
    "MaritalStatus": ["marital_status", "marital", "marriage_status"],
    "Education": [
        "education",
        "education_level",
        "qualification",
        "degree_level",
    ],
    "EducationField": [
        "education_field",
        "field_of_study",
        "study_field",
        "major",
        "discipline",
    ],
    "Department": [
        "dept",
        "dept_name",
        "department",
        "division",
        "business_unit",
        "team",
        "functional_area",
    ],
    "JobRole": [
        "role",
        "work_role",
        "job_role",
        "job_title",
        "title",
        "position",
        "designation",
        "job",
    ],
    "JobLevel": ["job_level", "grade", "level", "seniority_level"],
    "MonthlyIncome": [
        "salary",
        "monthly_salary",
        "income",
        "monthly_income",
        "earnings",
        "pay",
        "comp",
        "base_pay",
        "salary_in_inr",
        "salary_amount",
    ],
    "OverTime": ["overtime", "over_time", "ot", "extra_hours"],
    "JobSatisfaction": [
        "job_satisfaction",
        "satisfaction",
        "job_satisfaction_score",
    ],
    "EnvironmentSatisfaction": [
        "environment_satisfaction",
        "work_environment",
        "environment_score",
    ],
    "RelationshipSatisfaction": [
        "relationship_satisfaction",
        "team_satisfaction",
        "peers_satisfaction",
    ],
    "WorkLifeBalance": [
        "work_life_balance",
        "wlb",
        "worklife_balance",
        "balance",
    ],
    "PerformanceRating": [
        "performance_rating",
        "rating",
        "performance",
        "appraisal_rating",
    ],
    "DistanceFromHome": [
        "distance_from_home",
        "commute_distance",
        "distance",
        "commute_km",
        "commute_miles",
    ],
    "TrainingTimesLastYear": [
        "training_times_last_year",
        "training_hours",
        "trainings",
        "training_sessions",
    ],
    "StockOptionLevel": [
        "stock_option_level",
        "stock_options",
        "equity_tier",
    ],
    "PercentSalaryHike": [
        "percent_salary_hike",
        "salary_hike",
        "hike_percent",
        "raise_percentage",
        "salary_increase",
    ],
    "NumCompaniesWorked": [
        "num_companies_worked",
        "companies_worked",
        "previous_companies",
        "prior_employers",
    ],
    "NumProjects": ["num_projects", "projects_count", "projects"],
    "BusinessTravel": [
        "business_travel",
        "travel_frequency",
        "travel",
    ],
    "RemoteWork": [
        "remote_work",
        "is_remote",
        "work_from_home",
        "wfh",
    ],
    "AverageWeeklyHours": [
        "average_weekly_hours",
        "weekly_hours",
        "hours_per_week",
        "work_hours",
    ],
    "YearsAtCompany": [
        "years_at_company",
        "tenure",
        "company_tenure",
        "years_with_company",
        "length_of_service",
    ],
    "YearsInCurrentRole": [
        "years_in_current_role",
        "role_tenure",
        "years_in_role",
        "time_in_role",
    ],
    "TotalWorkingYears": [
        "total_working_years",
        "total_experience",
        "total_tenure",
        "experience_years",
    ],
    "Attrition": [
        "attrition",
        "left",
        "left_company",
        "left_org",
        "left_organization",
        "is_attrition",
        "turnover",
        "churn",
        "exit",
        "status",
        "resigned",
        "employment_status",
        "attrited",
        "separated",
        "voluntary_separation",
    ],
}

FLEXIBLE_ATTRITION_MAPPING = {
    # Positive (Yes / Left)
    "yes": "Yes",
    "y": "Yes",
    "1": "Yes",
    "1.0": "Yes",
    "true": "Yes",
    "left": "Yes",
    "resigned": "Yes",
    "terminated": "Yes",
    "attrited": "Yes",
    "exit": "Yes",
    "churn": "Yes",
    "separated": "Yes",
    "voluntarily separated": "Yes",
    "inactive": "Yes",
    # Negative (No / Stayed)
    "no": "No",
    "n": "No",
    "0": "No",
    "0.0": "No",
    "false": "No",
    "active": "No",
    "stayed": "No",
    "current": "No",
    "retained": "No",
    "employed": "No",
    "working": "No",
}