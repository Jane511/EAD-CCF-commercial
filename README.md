# Commercial EAD & CCF Project

This repository is the Exposure at Default and Credit Conversion Factor layer in the commercial credit-risk stack. It uses synthetic facility data, utilisation assumptions, and product-level CCF logic to estimate funded and unfunded exposure under a bank-style lending workflow. The main outputs are facility-level EAD tables, product-level CCF views, and validation artifacts that feed downstream expected loss, stress testing, pricing, and capital analysis.

## What this repo is

This project demonstrates how a commercial lending portfolio can be translated into Exposure at Default measures using transparent, recruiter-friendly logic. It is built as a portfolio project rather than a production bank engine, so the assumptions are explainable and the data is synthetic where internal usage and drawdown history would normally be required.

## Where it sits in the stack

Upstream inputs:
- facility and borrower portfolio data
- product limit and drawn-balance information
- utilisation and CCF assumptions where detailed behavioural history is unavailable

Downstream consumers:
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- `RAROC-pricing-and-return-hurdle`
- `RWA-capital-commercial`

## Key outputs

- `outputs/tables/ead_by_facility.csv`
- `outputs/tables/ccf_by_product.csv`
- `outputs/tables/utilisation_uplift_tables.csv`
- `outputs/tables/ead_validation_report.csv`
- `outputs/tables/pipeline_validation_report.csv`

## Repo structure

- `data/`: raw, interim, processed, and external demo inputs
- `src/`: reusable EAD and CCF pipeline logic
- `scripts/`: wrapper scripts for running the pipeline
- `docs/`: methodology, assumptions, data dictionary, and validation notes
- `notebooks/`: reviewer-facing walkthrough notebooks
- `outputs/`: exported tables, reports, and sample artifacts
- `tests/`: validation and regression checks

## How to run

```powershell
python -m src.codex_run_pipeline
```

Or:

```powershell
python scripts/run_codex_pipeline.py
```

## Limitations / Demo-Only Note

- All portfolio inputs are synthetic and are included for demonstration only.
- CCF and utilisation behaviour is modelled with simplified, transparent assumptions rather than internal behavioural datasets.
- The repo is intended for portfolio presentation and workflow demonstration, not for production limit management or regulatory reporting.
