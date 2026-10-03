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

import logging

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
from src.data_loader import load_and_validate_dataset
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

    logger.info("Starting Employee Attrition Analysis.")
    logger.info("Raw dataset: %s", RAW_DATA_FILE)

    try:
        # --------------------------------------------------------------
        # 3. Load and validate raw dataset
        # --------------------------------------------------------------

        dataframe = load_and_validate_dataset()

        logger.info(
            "Raw dataset loaded successfully: %d rows, %d columns.",
            len(dataframe),
            len(dataframe.columns),
        )

        # --------------------------------------------------------------
        # 4. Preprocess dataset
        # --------------------------------------------------------------

        cleaned_dataframe = preprocess_dataset(dataframe)

        logger.info(
            "Cleaned dataset contains %d rows, %d columns.",
            len(cleaned_dataframe),
            len(cleaned_dataframe.columns),
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