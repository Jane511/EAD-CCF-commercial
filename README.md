# EAD and CCF Module

This project is a simplified, bank-aligned EAD/CCF framework for portfolio analysis. It is not an APRA-approved IRB model.

The module estimates:

- `CCF (Credit Conversion Factor)`: how much of the undrawn limit is likely to be used before default.
- `EAD (Exposure at Default)`: drawn balance plus the expected conversion of any undrawn limit.

The core formula is:

```text
EAD = Drawn Balance + (Undrawn Limit x CCF)
```

The output is designed to feed later Expected Loss and RWA / capital workflows:

```text
EL = PD x LGD x EAD
```

## Project structure

```text
data/
  raw/
    exposure_master.csv
  processed/
    prepared_exposure.csv
    ccf_sample.csv
    ead_output.csv
    ead_validation_report.csv
  manual/
    ccf_rules.csv
notebooks/
  01_prepare_exposures.ipynb
  02_build_ccf_sample.ipynb
  03_estimate_ccf.ipynb
  04_calculate_ead.ipynb
  05_validation.ipynb
src/
  ead_pipeline.py
  prepare_exposures.py
  build_ccf_sample.py
  estimate_ccf.py
  calculate_ead.py
  validate_ead.py
  run_pipeline.py
README.md
```

## Inputs

Required raw input:

- `data/raw/exposure_master.csv`

Optional raw input for future history-based development:

- `data/raw/facility_balance_history.csv`

Manual rule input:

- `data/manual/ccf_rules.csv`

## Current modelling approach

This build defaults to the rule-based path because no balance history file was provided.

Facility classification is inferred from `facility_type` or `product_type`:

- `term_loan` -> `balance_only`
- `revolver` -> `balance_plus_ccf`
- `development` -> `balance_plus_ccf`
- `trade` -> `balance_plus_ccf`

Rule logic:

- Term loans use `CCF = 0`.
- Revolvers use rule-based CCF with utilisation band adjustments.
- Development facilities use rule-based CCF with development stage adjustments.
- Trade facilities use rule-based CCF with smaller utilisation band adjustments.

Central and downturn EAD are both produced:

- `ead_central = drawn_balance + (undrawn_limit x ccf_central)`
- `ead_downturn = drawn_balance + (undrawn_limit x ccf_downturn)`

## How to run

Run the full pipeline:

```powershell
python src/run_pipeline.py
```

Run individual steps:

```powershell
python src/prepare_exposures.py
python src/build_ccf_sample.py
python src/estimate_ccf.py
python src/calculate_ead.py
python src/validate_ead.py
```

## Outputs

Required outputs:

- `data/manual/ccf_rules.csv`
- `data/processed/ead_output.csv`
- `data/processed/ead_validation_report.csv`

Supporting outputs:

- `data/processed/prepared_exposure.csv`
- `data/processed/ccf_sample.csv`

## Validation checks

The validation report tests the required controls from the instruction PDF:

- no negative balances
- no negative limits
- undrawn limit is non-negative
- CCF is between 0 and 1
- EAD is not below drawn balance
- EAD is within the current limit
- all exposures have an assigned CCF

## Interview summary

I built an EAD and CCF module to estimate exposure at default. For fully drawn term loans, EAD is close to balance. For revolving, trade, and development facilities, I estimate a credit conversion factor on the undrawn portion and add it to the drawn balance. The module produces both central and downturn EAD for use in expected loss and capital modelling.
