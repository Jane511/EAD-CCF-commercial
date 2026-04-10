import pandas as pd

from ead_pipeline import PREPARED_EXPOSURE_PATH, RULES_PATH, estimate_ccf, load_ccf_rules


def main() -> None:
    prepared = pd.read_csv(PREPARED_EXPOSURE_PATH, parse_dates=["default_date"])
    rules = load_ccf_rules(RULES_PATH)
    exposures_with_ccf = estimate_ccf(prepared, rules)
    columns_to_show = [
        "exposure_id",
        "facility_type",
        "segment",
        "utilisation",
        "ccf_central",
        "ccf_downturn",
        "ccf_note",
    ]
    print(exposures_with_ccf[columns_to_show].to_string(index=False))


if __name__ == "__main__":
    main()
