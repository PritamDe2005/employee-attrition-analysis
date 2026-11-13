"""
Main execution pipeline for Employee Attrition Analysis.

Pipeline:
1. Create required directories.
2. Configure logging.
3. Load and validate the raw dataset.
4. Preprocess the dataset.
5. Save the cleaned dataset.
6. Generate analysis summary tables.
7. Save summary tables.
8. Generate visualizations.
"""

import argparse
import logging
from pathlib import Path

from config import (
    DATA_DIR,
    FIGURES_DIR,
    OUTPUTS_DIR,
    PROCESSED_DATA_FILE,
    RAW_DATA_FILE,
    REPORTS_DIR,
    TABLES_DIR,
)
from src.analysis import generate_summary_tables
from src.column_mapper import apply_column_mapping, resolve_column_mapping
from src.data_loader import (
    get_dataset_info,
    load_and_validate_dataset,
    load_dataset_from_source,
    validate_dynamic_schema,
)
from src.preprocessing import preprocess_dataset
from src.utils import (
    configure_logging,
    create_project_directories,
    save_dataframe,
)
from src.visualization import generate_all_visualizations


logger = logging.getLogger(__name__)


def main() -> None:
    """Run the complete employee attrition analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Employee Attrition Analysis Pipeline"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        help="Path to custom CSV or Excel dataset (.csv, .xlsx, .xls).",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # 1. Create required directories
    # ------------------------------------------------------------------

    create_project_directories(
        [
            DATA_DIR,
            PROCESSED_DATA_FILE.parent,
            OUTPUTS_DIR,
            FIGURES_DIR,
            TABLES_DIR,
            REPORTS_DIR,
        ]
    )

    # ------------------------------------------------------------------
    # 2. Configure logging
    # ------------------------------------------------------------------

    configure_logging()

    input_path = Path(args.input) if args.input else RAW_DATA_FILE
    logger.info("Starting Employee Attrition Analysis.")
    logger.info("Dataset source: %s", input_path)

    try:
        # --------------------------------------------------------------
        # 3. Load and validate raw dataset
        # --------------------------------------------------------------

        if args.input:
            dataframe = load_dataset_from_source(input_path)
            mapping, unmapped = resolve_column_mapping(list(dataframe.columns))
            dataframe = apply_column_mapping(dataframe, mapping)
            validate_dynamic_schema(dataframe)
        else:
            dataframe = load_and_validate_dataset(input_path)

        raw_info = get_dataset_info(dataframe)

        logger.info(
            "Raw dataset loaded successfully: %d rows, %d columns, "
            "%d missing cells, %d duplicate rows.",
            raw_info["rows"],
            raw_info["columns"],
            raw_info["missing_cells"],
            raw_info["duplicate_rows"],
        )

        # --------------------------------------------------------------
        # 4. Preprocess dataset
        # --------------------------------------------------------------

        cleaned_dataframe = preprocess_dataset(dataframe)
        cleaned_info = get_dataset_info(cleaned_dataframe)

        logger.info(
            "Cleaned dataset ready: %d rows, %d columns, "
            "%d missing cells, %d duplicate rows.",
            cleaned_info["rows"],
            cleaned_info["columns"],
            cleaned_info["missing_cells"],
            cleaned_info["duplicate_rows"],
        )

        # --------------------------------------------------------------
        # 5. Save cleaned dataset
        # --------------------------------------------------------------

        cleaned_dataframe.to_csv(
            PROCESSED_DATA_FILE,
            index=False,
        )

        logger.info(
            "Cleaned dataset saved to: %s",
            PROCESSED_DATA_FILE,
        )

        # --------------------------------------------------------------
        # 6. Generate analysis tables
        # --------------------------------------------------------------

        summary_tables = generate_summary_tables(
            cleaned_dataframe
        )

        logger.info(
            "Generated %d analysis tables.",
            len(summary_tables),
        )

        # --------------------------------------------------------------
        # 7. Save analysis tables
        # --------------------------------------------------------------

        for table_name, table in summary_tables.items():
            output_filename = f"{table_name}_summary.csv"

            output_path = save_dataframe(
                table,
                TABLES_DIR,
                output_filename,
            )

            logger.info(
                "Saved table: %s",
                output_path,
            )

        # --------------------------------------------------------------
        # 8. Generate visualizations
        # --------------------------------------------------------------

        generate_all_visualizations(
            cleaned_dataframe,
            FIGURES_DIR,
        )

        logger.info(
            "All visualizations generated successfully."
        )

        logger.info(
            "Employee Attrition Analysis completed successfully."
        )

    except (FileNotFoundError, ValueError, OSError) as error:
        logger.error(
            "Pipeline failed: %s",
            error,
        )

        raise


if __name__ == "__main__":
    main()