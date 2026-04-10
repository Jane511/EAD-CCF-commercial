from ead_pipeline import RAW_EXPOSURE_PATH, load_exposures, prepare_exposures, write_prepared_exposures


def main() -> None:
    exposures = load_exposures(RAW_EXPOSURE_PATH)
    prepared = prepare_exposures(exposures)
    output_path = write_prepared_exposures(prepared)
    print(f"Prepared exposure data written to {output_path}")


if __name__ == "__main__":
    main()
