# Commercial Exposure at Default & CCF Project

This repository is the EAD and Credit Conversion Factor layer in the public commercial credit-risk stack. It uses synthetic facility data, utilisation assumptions, and product-level CCF logic to estimate funded and unfunded exposure under lending workflows that are relevant to both bank-style risk frameworks and practical lending decisioning. The main outputs feed downstream expected loss, stress testing, pricing, and capital analysis.

## What this repo is

This project demonstrates how a commercial lending portfolio can be translated into Exposure at Default measures using transparent, recruiter-friendly logic. It is built as a portfolio project rather than a production bank engine, so the assumptions are explainable and the data is synthetic where internal usage and drawdown history would normally be required.

## Where it sits in the stack

Upstream inputs:
- facility and limit inputs staged under `data/`
- product utilisation and CCF assumptions maintained in-repo

Downstream consumers:
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- `RAROC-pricing-and-return-hurdle`
- `RWA-capital-commercial`

## How this is used in practice

This project can be applied in:

### Bank / Institutional context

- EAD estimation for expected loss, stress testing, and capital-style frameworks
- Portfolio exposure measurement across funded and unfunded facilities
- Utilisation and limit analysis for structured risk review

### Non-bank / Fintech context

- Exposure measurement for pricing and approval strategy on revolving or contingent products
- Limit-usage assumptions for portfolio performance and risk-adjusted decisioning
- Early portfolio monitoring of drawn versus undrawn exposure risk

## Example input files (already in the repo)

- `data/raw/exposure_master.csv`: demo facility-level limits and drawn balances (funded + unfunded)
- `data/raw/demo_portfolio.csv`: lightweight portfolio extract used by the demo pipeline
- `data/manual/ccf_rules.csv`: product-level CCF rules and utilisation assumptions

## Example output files (already in the repo)

- `outputs/tables/ead_by_facility.csv`: facility-level EAD view used downstream
- `outputs/tables/ccf_by_product.csv`: product-level CCF summary (sanity-check friendly)
- `outputs/tables/utilisation_uplift_tables.csv`: utilisation and uplift curves used by the EAD build
- `outputs/tables/pipeline_validation_report.csv`: pass/fail checks for required fields and totals
- `outputs/reports/pipeline_summary.md`: short run summary and file index
- `outputs/samples/demo_input.csv`: small sample input for quick reviewer inspection

## Example business use case

A credit portfolio team needs a consistent “exposure at default” view before building expected loss, stress tests, pricing packs, or capital summaries. This repo turns limits + drawn balances into a facility-level EAD dataset with a clear, reviewable CCF contract.

## How these outputs feed downstream repos

- `expected-loss-engine-commercial`: uses `outputs/tables/ead_by_facility.csv` as the exposure leg of EL.
- `stress-testing-commercial`: uses `outputs/tables/ead_by_facility.csv` as the base EAD input before applying scenario uplifts.
- `RAROC-pricing-and-return-hurdle`: uses EAD-derived exposure to translate EL and stress into cost-of-risk and hurdle pricing.
- `RWA-capital-commercial`: uses `outputs/tables/ead_by_facility.csv` as the exposure input for RWA and capital summaries.

## Key inputs

- facility and borrower portfolio data
- product limit, drawn-balance, and limit-utilisation information
- CCF and utilisation assumptions where detailed behavioural history is unavailable

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

Quick start:

```powershell
pip install -r requirements.txt
python -m src.run_pipeline
```

After the run, start with:

- `outputs/reports/pipeline_summary.md`
- `outputs/tables/ead_by_facility.csv`
- `outputs/tables/pipeline_validation_report.csv`

Run validation tests:

```powershell
python -m pytest
```

Alternative (wrapper script):

```powershell
python scripts/run_demo_pipeline.py
```

## Testing and validation

- `tests/test_demo_pipeline.py` runs a minimal demo pipeline and asserts the expected output files are written.
- `outputs/tables/pipeline_validation_report.csv` captures the same checks in a reviewer-friendly table.

## Limitations / Demo-Only Note

- All portfolio inputs are synthetic and are included for demonstration only.
- CCF and utilisation behaviour is modelled with simplified, transparent assumptions rather than internal behavioural datasets.
- The repo is intended for portfolio presentation and workflow demonstration, not for production limit management or regulatory reporting.
