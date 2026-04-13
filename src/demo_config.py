from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
REPO_NAME='EAD-CCF-Cashflow-Lending'
PIPELINE_KIND='ead'
EXPECTED_OUTPUTS=['ead_by_facility.csv', 'ccf_by_product.csv', 'utilisation_uplift_tables.csv', 'ead_validation_report.csv']
