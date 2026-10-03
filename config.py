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
# Expected dataset columns
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "EmployeeID",
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
# Numerical columns
# ---------------------------------------------------------------------------

NUMERICAL_COLUMNS = [
    "Age",
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
# Categorical standardization
# ---------------------------------------------------------------------------

ATTRITION_VALUES = ["Yes", "No"]

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