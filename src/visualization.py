"""
Visualization module for Employee Attrition Analysis.

This module creates and saves the visualizations required for the
employee attrition analysis project.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import FIGURE_DPI, FIGURE_FORMAT
from src.analysis import (
    calculate_attrition_rate,
    calculate_correlation_matrix,
)


def _save_figure(
    figure: plt.Figure,
    output_directory: Path,
    filename: str,
) -> None:
    """
    Save a matplotlib figure to the configured output directory.
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / f"{filename}.{FIGURE_FORMAT}"

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=FIGURE_DPI,
        bbox_inches="tight",
    )

    plt.close(figure)


def plot_attrition_distribution(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create an attrition distribution bar chart.
    """
    if "Attrition" not in dataframe.columns:
        return

    figure, axis = plt.subplots(figsize=(8, 5))

    sns.countplot(
        data=dataframe,
        x="Attrition",
        ax=axis,
    )

    axis.set_title("Employee Attrition Distribution")
    axis.set_xlabel("Attrition")
    axis.set_ylabel("Number of Employees")

    _save_figure(
        figure,
        output_directory,
        "attrition_distribution",
    )


def plot_attrition_by_department(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a bar chart showing attrition rate by department.
    """
    if "Department" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    department_data = calculate_attrition_rate(
        dataframe,
        "Department",
    )

    if department_data.empty:
        return

    figure, axis = plt.subplots(figsize=(9, 5))

    sns.barplot(
        data=department_data,
        x="Department",
        y="AttritionRate",
        ax=axis,
    )

    axis.set_title("Attrition Rate by Department")
    axis.set_xlabel("Department")
    axis.set_ylabel("Attrition Rate (%)")

    axis.tick_params(axis="x", rotation=20)

    _save_figure(
        figure,
        output_directory,
        "attrition_by_department",
    )


def plot_attrition_by_job_role(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a bar chart showing attrition rate by job role.
    """
    if "JobRole" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    role_data = calculate_attrition_rate(
        dataframe,
        "JobRole",
    )

    if role_data.empty:
        return

    role_data = role_data.sort_values("AttritionRate", ascending=False)

    figure, axis = plt.subplots(figsize=(11, 6))

    sns.barplot(
        data=role_data,
        x="AttritionRate",
        y="JobRole",
        ax=axis,
    )

    axis.set_title("Attrition Rate by Job Role")
    axis.set_xlabel("Attrition Rate (%)")
    axis.set_ylabel("Job Role")

    _save_figure(
        figure,
        output_directory,
        "attrition_by_job_role",
    )


def plot_salary_vs_attrition(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a box plot comparing monthly income across attrition groups.
    """
    if "MonthlyIncome" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    figure, axis = plt.subplots(figsize=(9, 5))

    sns.boxplot(
        data=dataframe,
        x="Attrition",
        y="MonthlyIncome",
        ax=axis,
    )

    axis.set_title("Monthly Income vs Attrition")
    axis.set_xlabel("Attrition")
    axis.set_ylabel("Monthly Income")

    _save_figure(
        figure,
        output_directory,
        "salary_vs_attrition",
    )


def plot_age_vs_attrition(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a box plot comparing employee age across attrition groups.
    """
    if "Age" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    figure, axis = plt.subplots(figsize=(9, 5))

    sns.boxplot(
        data=dataframe,
        x="Attrition",
        y="Age",
        ax=axis,
    )

    axis.set_title("Age vs Attrition")
    axis.set_xlabel("Attrition")
    axis.set_ylabel("Age")

    _save_figure(
        figure,
        output_directory,
        "age_vs_attrition",
    )


def plot_tenure_vs_attrition(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a box plot comparing years at company across attrition groups.
    """
    if "YearsAtCompany" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    figure, axis = plt.subplots(figsize=(9, 5))

    sns.boxplot(
        data=dataframe,
        x="Attrition",
        y="YearsAtCompany",
        ax=axis,
    )

    axis.set_title("Years at Company vs Attrition")
    axis.set_xlabel("Attrition")
    axis.set_ylabel("Years at Company")

    _save_figure(
        figure,
        output_directory,
        "tenure_vs_attrition",
    )


def plot_overtime_vs_attrition(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a bar chart showing attrition rate by overtime status.
    """
    if "OverTime" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    overtime_data = calculate_attrition_rate(
        dataframe,
        "OverTime",
    )

    if overtime_data.empty:
        return

    figure, axis = plt.subplots(figsize=(8, 5))

    sns.barplot(
        data=overtime_data,
        x="OverTime",
        y="AttritionRate",
        ax=axis,
    )

    axis.set_title("Attrition Rate by Overtime Status")
    axis.set_xlabel("Overtime")
    axis.set_ylabel("Attrition Rate (%)")

    _save_figure(
        figure,
        output_directory,
        "overtime_vs_attrition",
    )


def plot_satisfaction_vs_attrition(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a bar chart showing attrition rate by job satisfaction level.
    """
    if "JobSatisfaction" not in dataframe.columns or "Attrition" not in dataframe.columns:
        return

    satisfaction_data = calculate_attrition_rate(
        dataframe,
        "JobSatisfaction",
    )

    if satisfaction_data.empty:
        return

    figure, axis = plt.subplots(figsize=(8, 5))

    sns.barplot(
        data=satisfaction_data,
        x="JobSatisfaction",
        y="AttritionRate",
        ax=axis,
    )

    axis.set_title("Attrition Rate by Job Satisfaction")
    axis.set_xlabel("Job Satisfaction Level")
    axis.set_ylabel("Attrition Rate (%)")

    _save_figure(
        figure,
        output_directory,
        "satisfaction_vs_attrition",
    )


def plot_correlation_heatmap(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Create a correlation heatmap for numerical variables.
    """
    correlation_matrix = calculate_correlation_matrix(dataframe)

    if correlation_matrix.empty or correlation_matrix.shape[0] < 2:
        return

    figure, axis = plt.subplots(figsize=(14, 11))

    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=axis,
    )

    axis.set_title("Correlation Heatmap")

    _save_figure(
        figure,
        output_directory,
        "correlation_heatmap",
    )


def generate_all_visualizations(
    dataframe: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Generate all required project visualizations.
    """
    plot_attrition_distribution(
        dataframe,
        output_directory,
    )

    plot_attrition_by_department(
        dataframe,
        output_directory,
    )

    plot_attrition_by_job_role(
        dataframe,
        output_directory,
    )

    plot_salary_vs_attrition(
        dataframe,
        output_directory,
    )

    plot_age_vs_attrition(
        dataframe,
        output_directory,
    )

    plot_tenure_vs_attrition(
        dataframe,
        output_directory,
    )

    plot_overtime_vs_attrition(
        dataframe,
        output_directory,
    )

    plot_satisfaction_vs_attrition(
        dataframe,
        output_directory,
    )

    plot_correlation_heatmap(
        dataframe,
        output_directory,
    )