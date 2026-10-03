import pandas as pd

from src.preprocessing import (
    handle_invalid_numerical_values,
    handle_missing_target,
    handle_missing_values,
    preprocess_dataset,
    remove_duplicate_employee_ids,
    remove_duplicate_rows,
    standardize_categorical_values,
)


def test_standardize_categorical_values():
    dataframe = pd.DataFrame(
        {
            "Gender": ["male", " FEMALE "],
            "Department": [
                "Research & development",
                "human resources",
            ],
            "OverTime": ["YES", " no "],
            "Attrition": ["yes", "NO"],
        }
    )

    result = standardize_categorical_values(dataframe)

    assert result.loc[0, "Gender"] == "Male"
    assert result.loc[1, "Gender"] == "Female"
    assert result.loc[0, "Department"] == "Research & Development"
    assert result.loc[1, "Department"] == "Human Resources"
    assert result.loc[0, "OverTime"] == "Yes"
    assert result.loc[1, "OverTime"] == "No"
    assert result.loc[0, "Attrition"] == "Yes"
    assert result.loc[1, "Attrition"] == "No"


def test_remove_duplicate_rows():
    dataframe = pd.DataFrame(
        {
            "EmployeeID": [1, 2, 2],
            "Age": [25, 30, 30],
        }
    )

    result = remove_duplicate_rows(dataframe)

    assert len(result) == 2


def test_remove_duplicate_employee_ids():
    dataframe = pd.DataFrame(
        {
            "EmployeeID": [1, 2, 2, 3],
            "Age": [25, 30, 35, 40],
        }
    )

    result = remove_duplicate_employee_ids(dataframe)

    assert len(result) == 3
    assert result["EmployeeID"].is_unique


def test_handle_invalid_numerical_values():
    dataframe = pd.DataFrame(
        {
            "Age": [25, -5, 99],
            "MonthlyIncome": [5000, -1000, 0],
            "DistanceFromHome": [5, -3, 0],
            "JobSatisfaction": [3, 0, 5],
        }
    )

    result = handle_invalid_numerical_values(dataframe)

    assert pd.isna(result.loc[1, "Age"])
    assert pd.isna(result.loc[2, "Age"])
    assert pd.isna(result.loc[1, "MonthlyIncome"])
    assert pd.isna(result.loc[2, "MonthlyIncome"])
    assert pd.isna(result.loc[1, "DistanceFromHome"])
    assert pd.isna(result.loc[2, "DistanceFromHome"])
    assert pd.isna(result.loc[1, "JobSatisfaction"])
    assert pd.isna(result.loc[2, "JobSatisfaction"])


def test_handle_missing_target():
    dataframe = pd.DataFrame(
        {
            "EmployeeID": [1, 2, 3],
            "Attrition": ["Yes", None, "No"],
        }
    )

    result = handle_missing_target(dataframe)

    assert len(result) == 2
    assert result["Attrition"].notna().all()


def test_handle_missing_values():
    dataframe = pd.DataFrame(
        {
            "Age": [25, 30, None],
            "MonthlyIncome": [3000, 5000, None],
            "Department": ["IT", "Sales", None],
            "Attrition": ["No", "Yes", "No"],
        }
    )

    result = handle_missing_values(dataframe)

    assert result["Age"].isna().sum() == 0
    assert result["MonthlyIncome"].isna().sum() == 0
    assert result["Department"].isna().sum() == 0


def test_preprocess_dataset():
    dataframe = pd.DataFrame(
        {
            "EmployeeID": [1, 2, 2],
            "Age": [25, 30, 30],
            "Gender": ["male", "FEMALE", "FEMALE"],
            "Department": [
                "Research & development",
                "IT",
                "IT",
            ],
            "JobRole": ["Developer", "Manager", "Manager"],
            "MonthlyIncome": [5000, 6000, 6000],
            "OverTime": ["yes", "NO", "NO"],
            "JobSatisfaction": [3, 4, 4],
            "EnvironmentSatisfaction": [3, 4, 4],
            "WorkLifeBalance": [3, 4, 4],
            "DistanceFromHome": [5, 10, 10],
            "TrainingTimesLastYear": [3, 2, 2],
            "YearsAtCompany": [2, 5, 5],
            "YearsInCurrentRole": [1, 2, 2],
            "TotalWorkingYears": [4, 8, 8],
            "NumCompaniesWorked": [1, 2, 2],
            "NumProjects": [3, 4, 4],
            "AverageWeeklyHours": [40, 45, 45],
            "JobLevel": [1, 2, 2],
            "PerformanceRating": [3, 4, 4],
            "RelationshipSatisfaction": [3, 4, 4],
            "StockOptionLevel": [1, 2, 2],
            "PercentSalaryHike": [10, 12, 12],
            "Education": ["Bachelor", "Master", "Master"],
            "EducationField": ["Life Sciences", "Medical", "Medical"],
            "MaritalStatus": ["Single", "Married", "Married"],
            "BusinessTravel": ["Travel_Rarely", "Travel_Frequently", "Travel_Frequently"],
            "RemoteWork": ["No", "Yes", "Yes"],
            "Attrition": ["Yes", "No", "No"],
        }
    )

    result = preprocess_dataset(dataframe)

    assert not result.empty
    assert result.isna().sum().sum() == 0
    assert result.duplicated().sum() == 0
    assert result["EmployeeID"].is_unique
    assert set(result["Attrition"].unique()) <= {"Yes", "No"}


def test_required_columns_are_preserved():
    dataframe = pd.DataFrame(
        {
            "EmployeeID": [1],
            "Age": [25],
            "Gender": ["Male"],
            "Department": ["IT"],
            "JobRole": ["Developer"],
            "MonthlyIncome": [5000],
            "JobLevel": [1],
            "OverTime": ["No"],
            "JobSatisfaction": [3],
            "EnvironmentSatisfaction": [3],
            "RelationshipSatisfaction": [3],
            "WorkLifeBalance": [3],
            "PerformanceRating": [3],
            "DistanceFromHome": [5],
            "TrainingTimesLastYear": [3],
            "StockOptionLevel": [1],
            "PercentSalaryHike": [10],
            "NumCompaniesWorked": [1],
            "NumProjects": [3],
            "BusinessTravel": ["Travel_Rarely"],
            "RemoteWork": ["No"],
            "AverageWeeklyHours": [40],
            "YearsAtCompany": [2],
            "YearsInCurrentRole": [1],
            "TotalWorkingYears": [4],
            "Education": ["Bachelor"],
            "EducationField": ["Medical"],
            "MaritalStatus": ["Single"],
            "Attrition": ["No"],
        }
    )

    result = preprocess_dataset(dataframe)

    assert list(result.columns) == list(dataframe.columns)