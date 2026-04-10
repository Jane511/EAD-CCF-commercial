# Data Dictionary - EAD-CCF-Cashflow-Lending

| Field | Description |
| --- | --- |
| `borrower_id` | Synthetic borrower identifier. |
| `facility_id` | Synthetic facility identifier. |
| `segment` | Portfolio segment. |
| `industry` | Australian industry grouping. |
| `product_type` | Facility or product type. |
| `limit` | Approved or committed exposure limit. |
| `drawn` | Current drawn balance. |
| `pd` | Demonstration PD input. |
| `lgd` | Demonstration LGD input. |
| `ead` | Demonstration EAD input. |

## Output files

- `outputs/tables/ead_by_facility.csv`
- `outputs/tables/ccf_by_product.csv`
- `outputs/tables/utilisation_uplift_tables.csv`
- `outputs/tables/ead_validation_report.csv`
