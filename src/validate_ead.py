import pandas as pd

from .ead_pipeline import (
    EAD_OUTPUT_PATH,
    PREPARED_EXPOSURE_PATH,
    VALIDATION_REPORT_PATH,
    validate_ead,
    write_validation_report,
)


def main() -> None:
    prepared = pd.read_csv(PREPARED_EXPOSURE_PATH)
    ead_output = pd.read_csv(EAD_OUTPUT_PATH)
    validation_report = validate_ead(ead_output, prepared)
    output_path = write_validation_report(validation_report, VALIDATION_REPORT_PATH)
    print(f"Validation report written to {output_path}")
    print(validation_report.to_string(index=False))


if __name__ == "__main__":
    main()
