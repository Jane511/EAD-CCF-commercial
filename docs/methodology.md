# Methodology - EAD-CCF-Cashflow-Lending

1. Load or generate synthetic demo data.
2. Standardise borrower, facility, exposure, collateral, and financial fields.
3. Build utilisation, margin, DSCR, leverage, liquidity, working-capital, and collateral coverage features.
4. Run the `ead` engine.
5. Validate and export CSV outputs.

## Output contract

- `outputs/tables/ead_by_facility.csv`
- `outputs/tables/ccf_by_product.csv`
- `outputs/tables/utilisation_uplift_tables.csv`
- `outputs/tables/ead_validation_report.csv`
