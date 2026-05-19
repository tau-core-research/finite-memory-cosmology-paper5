#!/usr/bin/env python3
"""Run or guard the source-split likelihood-native null scorecard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EVIDENCE = ROOT / "evidence"
EXTERNAL_K1_READINESS = EVIDENCE / "source_split_external_k1_export_readiness.csv"
OUT = EVIDENCE / "source_split_likelihood_native_null_scorecard_readiness.csv"
SCORECARD = EVIDENCE / "source_split_likelihood_native_null_scorecard.csv"
EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"


def external_k1_allowed() -> tuple[bool, str]:
    if not EXTERNAL_K1_READINESS.exists():
        return False, "external_k1_readiness_missing"
    external = pd.read_csv(EXTERNAL_K1_READINESS)
    allowed = bool(
        not external.empty
        and external.get("AllowedForPrimaryK1", pd.Series([False])).astype(str).str.lower().eq("true").all()
    )
    blocker = str(external.get("BlockingIssue", pd.Series([""])).iloc[0])
    return allowed, blocker


def sign_stable_violations(pred: np.ndarray, y: np.ndarray, stable: np.ndarray) -> int:
    if not np.any(stable):
        return 0
    return int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))


def run_scorecard() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    data = external.merge(
        target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    sigma = data["K1Sigma"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    models: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_LOCKED_RHO4", w_k2_locked(x, rho=4.0) * k1, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        models.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))

    rows = []
    cov = np.diag(sigma * sigma)
    for model_id, pred, k, model_class in models:
        c2 = chi2(y, pred, cov)
        rows.append(
            {
                "Dataset": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_PREFLIGHT",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "Chi2DiagProxy": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "SignStableViolations": sign_stable_violations(pred, y, stable),
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "CovarianceClass": "declared_shrinkage_benchmark_covariance_not_public_full_covariance",
                "Status": "PREFLIGHT_SCORE_NOT_MEASUREMENT_VALIDATION",
                "ClaimBoundary": "likelihood_native_null_scorecard_preflight_only",
            }
        )
    pd.DataFrame(rows).to_csv(SCORECARD, index=False)


def main() -> None:
    allowed, blocker = external_k1_allowed()
    if allowed:
        run_scorecard()
    pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_NULL_SCORECARD_GUARD",
                "ScorecardAllowed": allowed,
                "WouldWrite": str(SCORECARD.relative_to(ROOT)),
                "ExternalK1Allowed": allowed,
                "ExternalK1BlockingIssue": blocker,
                "NextAction": (
                    "Inspect likelihood-native preflight null scorecard; do not treat as measurement validation."
                    if allowed
                    else "Validate a primary likelihood-native K1 export before scoring null comparators."
                ),
                "ClaimBoundary": "null_scorecard_guard_only_no_measurement_validation",
            }
        ]
    ).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")
    if allowed:
        print(f"Wrote {SCORECARD}")


if __name__ == "__main__":
    main()
