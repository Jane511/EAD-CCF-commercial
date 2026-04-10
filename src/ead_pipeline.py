from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MANUAL_DIR = DATA_DIR / "manual"

RAW_EXPOSURE_PATH = RAW_DIR / "exposure_master.csv"
RAW_HISTORY_PATH = RAW_DIR / "facility_balance_history.csv"
RULES_PATH = MANUAL_DIR / "ccf_rules.csv"
PREPARED_EXPOSURE_PATH = PROCESSED_DIR / "prepared_exposure.csv"
CCF_SAMPLE_PATH = PROCESSED_DIR / "ccf_sample.csv"
EAD_OUTPUT_PATH = PROCESSED_DIR / "ead_output.csv"
VALIDATION_REPORT_PATH = PROCESSED_DIR / "ead_validation_report.csv"

REQUIRED_EXPOSURE_COLUMNS = [
    "exposure_id",
    "borrower_id",
    "facility_type",
    "product_type",
    "segment",
    "drawn_balance",
    "current_limit",
    "undrawn_limit",
    "collateral_value",
    "industry",
    "default_flag",
    "default_date",
]

ALLOWED_FACILITY_TYPES = {"term_loan", "revolver", "development", "trade"}


def ensure_directories() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, MANUAL_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _normalise_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalise_key(value: object) -> str:
    return _normalise_text(value).lower().replace(" ", "_")


def _check_required_columns(df: pd.DataFrame, required: Iterable[str], name: str) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def _classify_facility_type(row: pd.Series) -> str:
    existing_type = _normalise_key(row.get("facility_type"))
    if existing_type in ALLOWED_FACILITY_TYPES:
        return existing_type

    product_type = _normalise_key(row.get("product_type"))
    if any(keyword in product_type for keyword in ("term", "amortis", "amortiz")):
        return "term_loan"
    if any(keyword in product_type for keyword in ("overdraft", "revolv", "working_capital", "cash_flow")):
        return "revolver"
    if any(keyword in product_type for keyword in ("construct", "develop", "land_subdivision", "project")):
        return "development"
    if "trade" in product_type:
        return "trade"
    return "revolver"


def _assign_ead_method(facility_type: str) -> str:
    return "balance_only" if facility_type == "term_loan" else "balance_plus_ccf"


def load_exposures(path: Path = RAW_EXPOSURE_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Exposure file not found: {path}")
    df = pd.read_csv(path)
    _check_required_columns(df, REQUIRED_EXPOSURE_COLUMNS, "exposure_master.csv")
    return df


def prepare_exposures(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared = prepared.drop_duplicates(subset=["exposure_id"], keep="first").reset_index(drop=True)

    numeric_columns = ["drawn_balance", "current_limit", "undrawn_limit", "collateral_value"]
    for column in numeric_columns:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0.0)
        prepared[column] = prepared[column].clip(lower=0)

    prepared["default_flag"] = pd.to_numeric(prepared["default_flag"], errors="coerce").fillna(0).astype(int)
    prepared["default_date"] = pd.to_datetime(prepared["default_date"], errors="coerce")

    prepared["facility_type"] = prepared.apply(_classify_facility_type, axis=1)
    prepared["segment"] = prepared["segment"].map(_normalise_text)
    prepared["product_type"] = prepared["product_type"].map(_normalise_text)
    prepared["industry"] = prepared["industry"].map(_normalise_text)

    prepared["undrawn_limit"] = (prepared["current_limit"] - prepared["drawn_balance"]).clip(lower=0)
    prepared["utilisation"] = 0.0
    positive_limit = prepared["current_limit"] > 0
    prepared.loc[positive_limit, "utilisation"] = (
        prepared.loc[positive_limit, "drawn_balance"] / prepared.loc[positive_limit, "current_limit"]
    )
    prepared["utilisation"] = prepared["utilisation"].clip(lower=0, upper=1)
    prepared["ead_method"] = prepared["facility_type"].map(_assign_ead_method)

    if "development_stage" not in prepared.columns:
        prepared["development_stage"] = ""
    prepared["development_stage"] = prepared["development_stage"].fillna("").map(_normalise_key)

    return prepared


def write_prepared_exposures(df: pd.DataFrame, path: Path = PREPARED_EXPOSURE_PATH) -> Path:
    ensure_directories()
    output = df.copy()
    output["default_date"] = output["default_date"].dt.strftime("%Y-%m-%d")
    output.to_csv(path, index=False)
    return path


def _empty_ccf_sample() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "exposure_id",
            "facility_type",
            "segment",
            "observation_date",
            "default_date",
            "drawn_balance_before_default",
            "undrawn_limit_before_default",
            "ead_at_default",
            "observed_ccf",
        ]
    )


def build_ccf_sample(
    prepared_df: pd.DataFrame,
    history_path: Path = RAW_HISTORY_PATH,
) -> pd.DataFrame:
    if not history_path.exists():
        return _empty_ccf_sample()

    history = pd.read_csv(history_path)
    required_history_columns = ["exposure_id", "as_of_date", "drawn_balance", "current_limit"]
    _check_required_columns(history, required_history_columns, "facility_balance_history.csv")

    history["as_of_date"] = pd.to_datetime(history["as_of_date"], errors="coerce")
    history["drawn_balance"] = pd.to_numeric(history["drawn_balance"], errors="coerce").fillna(0).clip(lower=0)
    history["current_limit"] = pd.to_numeric(history["current_limit"], errors="coerce").fillna(0).clip(lower=0)
    history["undrawn_limit"] = (history["current_limit"] - history["drawn_balance"]).clip(lower=0)

    defaults = prepared_df.loc[
        (prepared_df["default_flag"] == 1) & prepared_df["default_date"].notna(),
        ["exposure_id", "facility_type", "segment", "default_date"],
    ]
    if defaults.empty:
        return _empty_ccf_sample()

    sample_rows: list[dict[str, object]] = []
    for default_row in defaults.itertuples(index=False):
        exposure_history = history.loc[history["exposure_id"] == default_row.exposure_id].sort_values("as_of_date")
        if exposure_history.empty:
            continue

        observation_candidates = exposure_history.loc[
            (exposure_history["as_of_date"] < default_row.default_date)
            & (exposure_history["as_of_date"] >= default_row.default_date - pd.Timedelta(days=180))
        ]
        if observation_candidates.empty:
            continue

        observation = observation_candidates.iloc[-1]
        default_snapshot = exposure_history.loc[exposure_history["as_of_date"] <= default_row.default_date]
        if default_snapshot.empty:
            continue
        default_snapshot = default_snapshot.iloc[-1]

        undrawn_before_default = float(observation["undrawn_limit"])
        if undrawn_before_default <= 0:
            observed_ccf = 0.0
        else:
            observed_ccf = (
                (float(default_snapshot["drawn_balance"]) - float(observation["drawn_balance"]))
                / undrawn_before_default
            )
        observed_ccf = max(0.0, min(1.0, observed_ccf))

        sample_rows.append(
            {
                "exposure_id": default_row.exposure_id,
                "facility_type": default_row.facility_type,
                "segment": default_row.segment,
                "observation_date": observation["as_of_date"].strftime("%Y-%m-%d"),
                "default_date": default_row.default_date.strftime("%Y-%m-%d"),
                "drawn_balance_before_default": round(float(observation["drawn_balance"]), 2),
                "undrawn_limit_before_default": round(undrawn_before_default, 2),
                "ead_at_default": round(float(default_snapshot["drawn_balance"]), 2),
                "observed_ccf": round(observed_ccf, 4),
            }
        )

    if not sample_rows:
        return _empty_ccf_sample()
    return pd.DataFrame(sample_rows)


def write_ccf_sample(df: pd.DataFrame, path: Path = CCF_SAMPLE_PATH) -> Path:
    ensure_directories()
    df.to_csv(path, index=False)
    return path


def load_ccf_rules(path: Path = RULES_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CCF rules file not found: {path}")
    rules = pd.read_csv(path)
    required_rule_columns = ["facility_type", "segment", "ccf_central", "ccf_downturn"]
    _check_required_columns(rules, required_rule_columns, "ccf_rules.csv")
    rules["facility_type"] = rules["facility_type"].map(_normalise_key)
    rules["segment"] = rules["segment"].map(_normalise_text)
    rules["ccf_central"] = pd.to_numeric(rules["ccf_central"], errors="coerce").fillna(0).clip(lower=0, upper=1)
    rules["ccf_downturn"] = pd.to_numeric(rules["ccf_downturn"], errors="coerce").fillna(0).clip(lower=0, upper=1)
    return rules


def _utilisation_band(utilisation: float) -> str:
    if utilisation < 0.30:
        return "low"
    if utilisation > 0.70:
        return "high"
    return "base"


def _band_adjustment(facility_type: str, utilisation: float) -> tuple[float, float, str]:
    band = _utilisation_band(utilisation)
    if facility_type == "revolver":
        adjustments = {"low": (-0.10, -0.05), "base": (0.0, 0.0), "high": (0.10, 0.05)}
        central_adjustment, downturn_adjustment = adjustments[band]
        return central_adjustment, downturn_adjustment, f"utilisation_{band}"
    if facility_type == "trade":
        adjustments = {"low": (-0.05, -0.05), "base": (0.0, 0.0), "high": (0.05, 0.05)}
        central_adjustment, downturn_adjustment = adjustments[band]
        return central_adjustment, downturn_adjustment, f"utilisation_{band}"
    return 0.0, 0.0, "base_rule"


def _stage_adjustment(stage: str) -> tuple[float, float, str]:
    adjustments = {
        "early": (-0.10, -0.05),
        "mid": (0.0, 0.0),
        "middle": (0.0, 0.0),
        "late": (0.10, 0.05),
        "": (0.05, 0.05),
    }
    central_adjustment, downturn_adjustment = adjustments.get(stage, (0.05, 0.05))
    label = stage if stage else "conservative_missing_stage"
    return central_adjustment, downturn_adjustment, label


def estimate_ccf(prepared_df: pd.DataFrame, rules_df: pd.DataFrame) -> pd.DataFrame:
    exposures = prepared_df.copy()
    rules = rules_df.copy()

    exposures["facility_type"] = exposures["facility_type"].map(_normalise_key)
    exposures["segment"] = exposures["segment"].map(_normalise_text)
    if "development_stage" not in exposures.columns:
        exposures["development_stage"] = ""
    exposures["development_stage"] = exposures["development_stage"].fillna("").map(_normalise_key)
    exposures["utilisation"] = pd.to_numeric(exposures["utilisation"], errors="coerce").fillna(0.0).clip(0, 1)

    exposures = exposures.merge(
        rules.rename(columns={"ccf_central": "base_ccf_central", "ccf_downturn": "base_ccf_downturn"}),
        on=["facility_type", "segment"],
        how="left",
    )

    facility_level_fallback = (
        rules.groupby("facility_type", as_index=False)[["ccf_central", "ccf_downturn"]]
        .mean()
        .rename(columns={"ccf_central": "facility_fallback_central", "ccf_downturn": "facility_fallback_downturn"})
    )
    exposures = exposures.merge(facility_level_fallback, on="facility_type", how="left")

    exposures["base_ccf_central"] = exposures["base_ccf_central"].fillna(exposures["facility_fallback_central"])
    exposures["base_ccf_downturn"] = exposures["base_ccf_downturn"].fillna(exposures["facility_fallback_downturn"])
    exposures["base_ccf_central"] = exposures["base_ccf_central"].fillna(0.0)
    exposures["base_ccf_downturn"] = exposures["base_ccf_downturn"].fillna(0.0)

    central_adjustments: list[float] = []
    downturn_adjustments: list[float] = []
    ccf_notes: list[str] = []

    for row in exposures.itertuples(index=False):
        if row.facility_type == "development":
            central_adjustment, downturn_adjustment, note = _stage_adjustment(row.development_stage)
        else:
            central_adjustment, downturn_adjustment, note = _band_adjustment(row.facility_type, row.utilisation)
        central_adjustments.append(central_adjustment)
        downturn_adjustments.append(downturn_adjustment)
        ccf_notes.append(note)

    exposures["ccf_central"] = (exposures["base_ccf_central"] + pd.Series(central_adjustments)).clip(0, 1)
    exposures["ccf_downturn"] = (exposures["base_ccf_downturn"] + pd.Series(downturn_adjustments)).clip(0, 1)
    exposures["ccf_note"] = ccf_notes
    exposures["ccf_assigned_flag"] = exposures[["ccf_central", "ccf_downturn"]].notna().all(axis=1)

    return exposures


def calculate_ead(exposures_with_ccf: pd.DataFrame) -> pd.DataFrame:
    ead = exposures_with_ccf.copy()
    ead["ead_central"] = ead["drawn_balance"] + (ead["undrawn_limit"] * ead["ccf_central"])
    ead["ead_downturn"] = ead["drawn_balance"] + (ead["undrawn_limit"] * ead["ccf_downturn"])

    ead = ead[
        [
            "exposure_id",
            "facility_type",
            "segment",
            "drawn_balance",
            "undrawn_limit",
            "ccf_central",
            "ccf_downturn",
            "ead_central",
            "ead_downturn",
        ]
    ].copy()

    for column in ["drawn_balance", "undrawn_limit", "ccf_central", "ccf_downturn", "ead_central", "ead_downturn"]:
        ead[column] = ead[column].round(2)

    return ead


def write_ead_output(df: pd.DataFrame, path: Path = EAD_OUTPUT_PATH) -> Path:
    ensure_directories()
    df.to_csv(path, index=False)
    return path


def validate_ead(ead_df: pd.DataFrame, prepared_df: pd.DataFrame) -> pd.DataFrame:
    validation_base = ead_df.merge(
        prepared_df[["exposure_id", "current_limit"]],
        on="exposure_id",
        how="left",
    )

    checks = {
        "no_negative_balances": validation_base["drawn_balance"] >= 0,
        "no_negative_limits": validation_base["current_limit"] >= 0,
        "undrawn_non_negative": validation_base["undrawn_limit"] >= 0,
        "ccf_between_zero_and_one": validation_base["ccf_central"].between(0, 1)
        & validation_base["ccf_downturn"].between(0, 1),
        "ead_not_below_drawn": (validation_base["ead_central"] >= validation_base["drawn_balance"])
        & (validation_base["ead_downturn"] >= validation_base["drawn_balance"]),
        "ead_within_limit": (validation_base["ead_central"] <= validation_base["current_limit"])
        & (validation_base["ead_downturn"] <= validation_base["current_limit"]),
        "all_exposures_assigned_ccf": validation_base["ccf_central"].notna() & validation_base["ccf_downturn"].notna(),
    }

    report_rows: list[dict[str, object]] = []
    for check_name, result in checks.items():
        failed_exposures = validation_base.loc[~result, "exposure_id"].tolist()
        report_rows.append(
            {
                "check_name": check_name,
                "status": "PASS" if not failed_exposures else "FAIL",
                "failed_count": len(failed_exposures),
                "failed_exposures": ", ".join(failed_exposures[:10]),
            }
        )

    return pd.DataFrame(report_rows)


def write_validation_report(df: pd.DataFrame, path: Path = VALIDATION_REPORT_PATH) -> Path:
    ensure_directories()
    df.to_csv(path, index=False)
    return path
