from .ead_pipeline import (
    CCF_SAMPLE_PATH,
    PREPARED_EXPOSURE_PATH,
    RAW_HISTORY_PATH,
    build_ccf_sample,
    write_ccf_sample,
)

import pandas as pd


def main() -> None:
    prepared = pd.read_csv(PREPARED_EXPOSURE_PATH, parse_dates=["default_date"])
    ccf_sample = build_ccf_sample(prepared, RAW_HISTORY_PATH)
    output_path = write_ccf_sample(ccf_sample, CCF_SAMPLE_PATH)
    print(f"CCF sample written to {output_path}")


if __name__ == "__main__":
    main()
