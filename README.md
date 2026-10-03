# Employee Attrition Analysis

An industry-oriented HR analytics project for exploring employee attrition
patterns and identifying employee characteristics associated with attrition.

The project is implemented entirely using modular Python scripts and provides
both a batch analysis pipeline and an interactive Streamlit dashboard.

---

## 📌 Project Overview

Employee attrition is an important HR analytics problem because organizations
need to understand workforce patterns and identify areas that may require
further investigation.

This project analyzes an employee dataset to explore attrition across:

- Departments
- Job roles
- Salary bands
- Age groups
- Tenure groups
- Employee satisfaction
- Overtime
- Business travel
- Remote work
- Other numerical employee characteristics

The analysis uses descriptive statistics, grouped analysis, correlation
analysis, summary tables, and visualizations.

> **Important:** The analysis identifies statistical associations and patterns.
> It does not establish that a particular factor causes employee attrition.

---

## 🎯 Project Objectives

The project aims to:

1. Load and understand the HR employee dataset.
2. Identify missing, duplicate, inconsistent, and suspicious data.
3. Clean and preprocess the dataset.
4. Analyze the overall employee attrition distribution.
5. Analyze attrition across departments and job roles.
6. Analyze salary bands and attrition.
7. Analyze age and tenure groups.
8. Analyze employee satisfaction levels.
9. Analyze overtime and work-related patterns.
10. Calculate correlations between numerical variables.
11. Generate summary tables and visualizations.
12. Present findings through an interactive dashboard.
13. Provide business-oriented observations based on the analysis.

---

## 🛠️ Technology Stack

### Programming

- Python 3.13+

### Data Analysis

- Pandas
- NumPy

### Visualization

- Matplotlib
- Seaborn
- Streamlit

### Testing

- Pytest

### Development

- Modular Python architecture
- Git / GitHub
- Streamlit deployment

---

## 📂 Project Structure

```text
employee_attrition_analysis/
│
├── app.py
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── employee_attrition_messy_8040.csv
│   │
│   └── processed/
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── reports/
│
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── utils.py
│   └── visualization.py
│
└── tests/
    └── test_preprocessing.py