"""
Intelligent column mapping and schema reconciliation module.

Responsible for:
- Normalizing user-supplied column names.
- Matching raw column names to canonical schema via aliases and fuzzy search.
- Detecting which analytical dimensions are available in a dataset.
"""

from difflib import get_close_matches
import re

import pandas as pd

from config import (
    COLUMN_ALIASES,
    EXPECTED_COLUMNS,
    MANDATORY_COLUMNS,
    SATISFACTION_COLUMNS,
)


def normalize_column_name(name: str) -> str:
    """
    Normalize a column string by trimming, lowercasing, and replacing
    spaces or non-alphanumeric characters with single underscores.
    """
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", str(name).strip().lower())
    return clean.strip("_")


def resolve_column_mapping(
    columns: list[str],
    fuzzy_cutoff: float = 0.85,
) -> tuple[dict[str, str], list[str]]:
    """
    Map raw column headers to canonical project columns.

    Priority:
    1. Exact match with canonical column names.
    2. Exact normalized match with canonical column names.
    3. Alias match against configured synonyms.
    4. Fuzzy match against normalized canonical names and aliases.

    Parameters
    ----------
    columns : list[str]
        List of column headers from the uploaded file.
    fuzzy_cutoff : float
        Similarity threshold for fuzzy matching (default: 0.85).

    Returns
    -------
    tuple[dict[str, str], list[str]]
        - mapping: dictionary mapping {raw_column: canonical_column}
        - unmapped: list of raw columns that could not be mapped
    """
    mapping: dict[str, str] = {}
    mapped_canonicals: set[str] = set()

    # Precompute normalized canonical names
    canonical_normalized_map = {
        normalize_column_name(col): col for col in EXPECTED_COLUMNS
    }

    # Precompute normalized alias lookup: alias -> canonical
    alias_lookup: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            alias_lookup[normalize_column_name(alias)] = canonical

    # Pass 1: Exact matches
    for raw_col in columns:
        if raw_col in EXPECTED_COLUMNS and raw_col not in mapped_canonicals:
            mapping[raw_col] = raw_col
            mapped_canonicals.add(raw_col)

    # Pass 2: Normalized exact matches
    for raw_col in columns:
        if raw_col in mapping:
            continue
        norm = normalize_column_name(raw_col)
        if norm in canonical_normalized_map:
            canonical = canonical_normalized_map[norm]
            if canonical not in mapped_canonicals:
                mapping[raw_col] = canonical
                mapped_canonicals.add(canonical)

    # Pass 3: Alias lookup
    for raw_col in columns:
        if raw_col in mapping:
            continue
        norm = normalize_column_name(raw_col)
        if norm in alias_lookup:
            canonical = alias_lookup[norm]
            if canonical not in mapped_canonicals:
                mapping[raw_col] = canonical
                mapped_canonicals.add(canonical)

    # Pass 4: Fuzzy matching against normalized aliases and canonical names
    candidates_pool = {**canonical_normalized_map, **alias_lookup}
    for raw_col in columns:
        if raw_col in mapping:
            continue
        norm = normalize_column_name(raw_col)
        matches = get_close_matches(
            norm,
            candidates_pool.keys(),
            n=1,
            cutoff=fuzzy_cutoff,
        )
        if matches:
            best_match = matches[0]
            canonical = candidates_pool[best_match]
            if canonical not in mapped_canonicals:
                mapping[raw_col] = canonical
                mapped_canonicals.add(canonical)

    unmapped = [col for col in columns if col not in mapping]
    return mapping, unmapped


def apply_column_mapping(
    dataframe: pd.DataFrame,
    mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Apply column mapping dictionary to rename dataframe columns.
    """
    return dataframe.rename(columns=mapping)


def detect_available_dimensions(columns: list[str]) -> dict[str, bool]:
    """
    Detect which analytical dimensions can be computed based on
    columns present in the dataset.
    """
    col_set = set(columns)
    return {
        "attrition": "Attrition" in col_set,
        "department": "Department" in col_set,
        "job_role": "JobRole" in col_set,
        "salary": "MonthlyIncome" in col_set,
        "age": "Age" in col_set,
        "tenure": "YearsAtCompany" in col_set,
        "satisfaction": any(col in col_set for col in SATISFACTION_COLUMNS),
        "overtime": "OverTime" in col_set,
        "business_travel": "BusinessTravel" in col_set,
        "remote_work": "RemoteWork" in col_set,
        "education": "Education" in col_set,
        "correlation": len(col_set) > 2 and "Attrition" in col_set,
    }
