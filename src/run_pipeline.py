from build_ccf_sample import main as build_ccf_sample_main
from calculate_ead import main as calculate_ead_main
from prepare_exposures import main as prepare_exposures_main
from validate_ead import main as validate_ead_main


def main() -> None:
    prepare_exposures_main()
    build_ccf_sample_main()
    calculate_ead_main()
    validate_ead_main()


if __name__ == "__main__":
    main()
