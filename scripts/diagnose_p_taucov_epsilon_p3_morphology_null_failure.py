#!/usr/bin/env python3
"""Diagnose why epsilon-P3 loses to the morphology-null comparator."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_p_taucov_epsilon_p3_null_survival_suite.py"
P5C_V0 = ROOT / "scripts/run_p5c_kernel_covariance_scorecard_v0.py"
OUT_FOLDS = ROOT / "evidence/p_taucov_epsilon_p3_morphology_null_diagnostic_folds.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_morphology_null_diagnostic_summary.csv"
DOC = ROOT / "docs/p_taucov_epsilon_p3_morphology_null_diagnostic.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_EPSILON_P3_MORPHOLOGY_NULL_FAILURE_DIAGNOSTIC_v1"
CLAIM_BOUNDARY = "post_failure_diagnostic_no_new_scoring_claim"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def kernel_corr(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    if float(np.linalg.norm(av)) == 0.0 or float(np.linalg.norm(bv)) == 0.0:
        return float("nan")
    return float(np.corrcoef(av, bv)[0, 1])


def main() -> int:
    runner = load_module(RUNNER, "ptaucov_runner")
    p5c_v0 = load_module(P5C_V0, "p5c_v0")
    p5c_v0.AUDIT_ID = AUDIT_ID
    p5c_v0.PROTOCOL_ID = PROTOCOL_ID
    p5c_v0.CLAIM_BOUNDARY = CLAIM_BOUNDARY

    tau_ids, delta = runner.matrix_from_long(runner.BRANCH_WEIGHTS, "DeltaCTau")
    bridge_ids, bridge = runner.load_bridge(tau_ids)
    rows = p5c_v0.load_rows()
    if bridge_ids != rows["RowID"].astype(str).tolist():
        raise RuntimeError("Bridge row order mismatch.")

    tau_index = {cid: i for i, cid in enumerate(tau_ids)}
    m_idx = tau_index.get("TEMPLATE_M_PARENT_MORPHOLOGY")
    if m_idx is None:
        raise RuntimeError("Missing TEMPLATE_M_PARENT_MORPHOLOGY coordinate.")

    primary_kernel = runner.project(bridge, delta)
    morph_delta = delta.copy()
    morph_delta[m_idx, :] = 0.0
    morph_delta[:, m_idx] = 0.0
    morphology_kernel = runner.project(bridge, morph_delta)

    _, primary_oos = p5c_v0.score_all(rows, primary_kernel, "TAU_EPSILON_P3_PRIMARY")
    _, morph_oos = p5c_v0.score_all(rows, morphology_kernel, "MORPHOLOGY_NULL")
    keep = [
        "FoldID",
        "FoldClass",
        "PrimaryOOS",
        "TestRows",
        "TestFamilies",
        "TestClockBlocks",
        "Alpha",
        "DeltaNLL_BaselineMinusKernel",
    ]
    merged = primary_oos[keep].merge(
        morph_oos[keep],
        on=["FoldID", "FoldClass", "PrimaryOOS", "TestRows", "TestFamilies", "TestClockBlocks"],
        suffixes=("_Primary", "_MorphologyNull"),
    )
    merged["MorphologyMinusPrimaryDeltaNLL"] = (
        merged["DeltaNLL_BaselineMinusKernel_MorphologyNull"]
        - merged["DeltaNLL_BaselineMinusKernel_Primary"]
    )
    merged["PrimaryMinusMorphologyDeltaNLL"] = -merged["MorphologyMinusPrimaryDeltaNLL"]
    merged.insert(0, "AuditID", AUDIT_ID)
    merged.insert(0, "ProtocolID", PROTOCOL_ID)
    merged["ClaimBoundary"] = CLAIM_BOUNDARY
    merged.to_csv(OUT_FOLDS, index=False)

    primary = merged[merged["PrimaryOOS"]]
    lofo = primary[primary["FoldClass"].eq("primary_leave_one_family_out")]
    clock = primary[primary["FoldClass"].eq("primary_contiguous_clock_block")]
    lofo_sorted = lofo.sort_values("MorphologyMinusPrimaryDeltaNLL", ascending=False)
    strongest_family = lofo_sorted.iloc[0] if not lofo_sorted.empty else None
    primary_positive = lofo[lofo["DeltaNLL_BaselineMinusKernel_Primary"] > 0.0]
    morph_positive = lofo[lofo["DeltaNLL_BaselineMinusKernel_MorphologyNull"] > 0.0]

    summary = {
        "ProtocolID": PROTOCOL_ID,
        "AuditID": AUDIT_ID,
        "Status": "P_TAUCOV_EPSILON_P3_MORPHOLOGY_NULL_DOMINANCE_DIAGNOSED",
        "PrimaryOOSDeltaNLL": float(primary["DeltaNLL_BaselineMinusKernel_Primary"].sum()),
        "MorphologyNullOOSDeltaNLL": float(primary["DeltaNLL_BaselineMinusKernel_MorphologyNull"].sum()),
        "MorphologyMinusPrimaryOOSDeltaNLL": float(primary["MorphologyMinusPrimaryDeltaNLL"].sum()),
        "LOFOPrimaryDeltaNLL": float(lofo["DeltaNLL_BaselineMinusKernel_Primary"].sum()),
        "LOFOMorphologyNullDeltaNLL": float(lofo["DeltaNLL_BaselineMinusKernel_MorphologyNull"].sum()),
        "ClockPrimaryDeltaNLL": float(clock["DeltaNLL_BaselineMinusKernel_Primary"].sum()),
        "ClockMorphologyNullDeltaNLL": float(clock["DeltaNLL_BaselineMinusKernel_MorphologyNull"].sum()),
        "KernelCorrelationPrimaryVsMorphologyNull": kernel_corr(primary_kernel, morphology_kernel),
        "PrimaryMedianAlpha": float(primary["Alpha_Primary"].median()),
        "MorphologyNullMedianAlpha": float(primary["Alpha_MorphologyNull"].median()),
        "PrimaryPositiveLOFOFamilies": int(len(primary_positive)),
        "MorphologyNullPositiveLOFOFamilies": int(len(morph_positive)),
        "DominantFailureFamily": "" if strongest_family is None else str(strongest_family["TestFamilies"]),
        "DominantFailureFoldDelta": float("nan") if strongest_family is None else float(strongest_family["MorphologyMinusPrimaryDeltaNLL"]),
        "SurvivalClaimAllowed": False,
        "MeasurementValidationAllowed": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    pd.DataFrame([summary]).to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Epsilon-P3 Morphology-Null Failure Diagnostic",
                "",
                f"Status: `{summary['Status']}`.",
                "",
                "This is a post-failure diagnostic. It does not authorize a new",
                "score, a survival claim, or measurement validation.",
                "",
                "## Key Numbers",
                "",
                f"- primary OOS DeltaNLL: `{summary['PrimaryOOSDeltaNLL']}`",
                f"- morphology-null OOS DeltaNLL: `{summary['MorphologyNullOOSDeltaNLL']}`",
                f"- morphology minus primary OOS DeltaNLL: `{summary['MorphologyMinusPrimaryOOSDeltaNLL']}`",
                f"- kernel correlation primary versus morphology-null: `{summary['KernelCorrelationPrimaryVsMorphologyNull']}`",
                f"- dominant failure family: `{summary['DominantFailureFamily']}`",
                f"- dominant failure fold margin: `{summary['DominantFailureFoldDelta']}`",
                "",
                "## Interpretation",
                "",
                "The failed survival gate is not a small bookkeeping issue. The",
                "morphology-null comparator carries a stronger covariance improvement",
                "than the declared Tau-response primary. The next Tau-specific step must",
                "therefore explain or remove this morphology-null dominance before any",
                "new survival claim is considered.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(summary["Status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
