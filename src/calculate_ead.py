import pandas as pd

from ead_pipeline import EAD_OUTPUT_PATH, PREPARED_EXPOSURE_PATH, RULES_PATH, calculate_ead, estimate_ccf, load_ccf_rules, write_ead_output


def main() -> None:
    prepared = pd.read_csv(PREPARED_EXPOSURE_PATH, parse_dates=["default_date"])
    rules = load_ccf_rules(RULES_PATH)
    exposures_with_ccf = estimate_ccf(prepared, rules)
    ead_output = calculate_ead(exposures_with_ccf)
    output_path = write_ead_output(ead_output, EAD_OUTPUT_PATH)
    print(f"EAD output written to {output_path}")


if __name__ == "__main__":
    main()
