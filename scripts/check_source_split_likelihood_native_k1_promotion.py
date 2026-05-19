#!/usr/bin/env python3
"""Check whether the likelihood-native source-split K1 route can be promoted."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA_K1 = ROOT / "data" / "k1"

BASELINE = DATA_K1 / "source_split_likelihood_native_baseline_prediction.csv"
COORDINATE = DATA_K1 / "source_split_likelihood_native_coordinate_map.csv"
COV_SUMMARY = EVIDENCE / "source_split_joint_covariance_policy_summary.csv"
NULL_SCORE = EVIDENCE / "source_split_likelihood_native_null_scorecard.csv"
EXTERNAL_K1 = DATA_K1 / "source_split_external_k1_response.csv"
NUISANCE_POLICY = ROOT / "docs" / "source_split_likelihood_native_nuisance_policy.md"
COORDINATE_PROMOTION = ROOT / "docs" / "source_split_likelihood_native_coordinate_promotion.md"
COVARIANCE_PROMOTION = ROOT / "docs" / "source_split_likelihood_native_covariance_promotion.md"

OUT = EVIDENCE / "source_split_likelihood_native_k1_promotion_gate.csv"
SUMMARY = EVIDENCE / "source_split_likelihood_native_k1_promotion_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def add_row(rows: list[dict[str, object]], **kwargs: object) -> None:
    rows.append(
        {
            "GateID": kwargs.get("GateID", "SOURCE_SPLIT_LIKELIHOOD_NATIVE_K1_PROMOTION_V1"),
            "CheckID": kwargs["CheckID"],
            "Required": kwargs.get("Required", True),
            "Available": kwargs.get("Available", False),
            "Promotable": kwargs.get("Promotable", False),
            "ArtifactPath": kwargs.get("ArtifactPath", ""),
            "BlockingIssue": kwargs.get("BlockingIssue", ""),
            "NextAction": kwargs.get("NextAction", ""),
            "ClaimBoundary": "promotion_gate_only_no_measurement_validation",
        }
    )


def external_k1_validated() -> bool:
    if not EXTERNAL_K1.exists():
        return False
    external = pd.read_csv(EXTERNAL_K1)
    if external.empty:
        return False
    return bool(
        external.get("LikelihoodNative", pd.Series([False])).map(truthy).all()
        and external.get("AllowedAsPrimaryK1Candidate", pd.Series([False])).map(truthy).all()
        and set(external.get("ProvenanceType", pd.Series(dtype=str)).astype(str)) == {"likelihood_native_baseline"}
    )


def main() -> None:
    rows: list[dict[str, object]] = []
    external_valid = external_k1_validated()

    if BASELINE.exists():
        baseline = pd.read_csv(BASELINE)
        response = pd.to_numeric(baseline.get("RawSourceSplitResponse", pd.Series(dtype=float)), errors="coerce")
        sigma = pd.to_numeric(baseline.get("JointSigmaDiagProxy", pd.Series(dtype=float)), errors="coerce")
        nonzero = not np.isclose(response.fillna(0.0).to_numpy(float), 0.0).all()
        finite = np.isfinite(response.to_numpy(float)).all() and np.isfinite(sigma.to_numpy(float)).all()
        positive_sigma = bool((sigma > 0).all())
        marked_primary = baseline.get("AllowedAsPrimaryK1Candidate", pd.Series([False])).map(truthy).all() or external_valid
        nuisance_policy = NUISANCE_POLICY.exists()
        promotable = bool(nonzero and finite and positive_sigma and marked_primary and nuisance_policy)
        blockers = []
        if not nonzero:
            blockers.append("baseline_response_identically_zero")
        if not finite:
            blockers.append("baseline_or_sigma_not_finite")
        if not positive_sigma:
            blockers.append("baseline_sigma_not_positive")
        if not marked_primary:
            blockers.append("baseline_vector_not_marked_primary")
        if not nuisance_policy:
            blockers.append("nuisance_policy_missing")
        add_row(
            rows,
            CheckID="PROMO_BASELINE_VECTOR",
            Available=True,
            Promotable=promotable,
            ArtifactPath=str(BASELINE.relative_to(ROOT)),
            BlockingIssue=";".join(blockers),
            NextAction=(
                "Primary response policy exists; keep primary-K1 flag closed until covariance/null policy is frozen."
                if nuisance_policy
                else "Promote nuisance policy and primary-K1 flag only after covariance/null policy is frozen."
            ),
        )
    else:
        add_row(
            rows,
            CheckID="PROMO_BASELINE_VECTOR",
            ArtifactPath=str(BASELINE.relative_to(ROOT)),
            BlockingIssue="baseline_prediction_vector_missing",
            NextAction="Build source_split_likelihood_native_baseline_prediction.csv.",
        )

    if COORDINATE.exists():
        coordinate = pd.read_csv(COORDINATE)
        monotone = bool(np.all(np.diff(coordinate["x_likelihood_native"].to_numpy(float)) > 0))
        frozen = coordinate.get("FrozenBeforeK2Scoring", pd.Series([False])).map(truthy).all()
        likelihood_native = coordinate.get("LikelihoodNative", pd.Series([False])).map(truthy).all() or external_valid
        coordinate_promotion = COORDINATE_PROMOTION.exists()
        allowed = coordinate.get("AllowedForK1Export", pd.Series([False])).map(truthy).all() or external_valid
        promotable = bool(monotone and frozen and likelihood_native and allowed and coordinate_promotion)
        blockers = []
        if not monotone:
            blockers.append("coordinate_not_strictly_monotone")
        if not frozen:
            blockers.append("coordinate_not_frozen")
        if not likelihood_native:
            blockers.append("coordinate_not_likelihood_native")
        if not allowed:
            blockers.append("coordinate_not_allowed_for_k1_export")
        if not coordinate_promotion:
            blockers.append("coordinate_promotion_policy_missing")
        add_row(
            rows,
            CheckID="PROMO_COORDINATE_MAP",
            Available=True,
            Promotable=promotable,
            ArtifactPath=str(COORDINATE.relative_to(ROOT)),
            BlockingIssue=";".join(blockers),
            NextAction=(
                "Coordinate policy exists; keep export flag closed until covariance/null policy is frozen."
                if coordinate_promotion
                else "Promote coordinate map together with the joint vector and covariance policy."
            ),
        )
    else:
        add_row(
            rows,
            CheckID="PROMO_COORDINATE_MAP",
            ArtifactPath=str(COORDINATE.relative_to(ROOT)),
            BlockingIssue="coordinate_map_missing",
            NextAction="Build source_split_likelihood_native_coordinate_map.csv.",
        )

    if COV_SUMMARY.exists():
        cov = pd.read_csv(COV_SUMMARY)
        positive = cov.get("PositiveDefinite", pd.Series([False])).map(truthy).all()
        k1_compatible = cov.get("K1Compatible", pd.Series([False])).map(truthy).all()
        allowed = cov.get("AllowedForK2Scoring", pd.Series([False])).map(truthy).all() or external_valid
        covariance_promotion = COVARIANCE_PROMOTION.exists()
        promotable = bool(positive and k1_compatible and allowed and covariance_promotion)
        blockers = []
        if not positive:
            blockers.append("covariance_not_positive_definite")
        if not k1_compatible:
            blockers.append("covariance_not_k1_compatible")
        if not allowed:
            blockers.append("covariance_not_promoted_for_scoring")
        if not covariance_promotion:
            blockers.append("covariance_promotion_policy_missing")
        add_row(
            rows,
            CheckID="PROMO_COVARIANCE_POLICY",
            Available=True,
            Promotable=promotable,
            ArtifactPath=str(COV_SUMMARY.relative_to(ROOT)),
            BlockingIssue=";".join(blockers),
            NextAction=(
                "Covariance policy exists; keep scoring flag closed until external K1 and null scorecard are ready."
                if covariance_promotion
                else "Promote a declared joint covariance policy or ingest public full covariance."
            ),
        )
    else:
        add_row(
            rows,
            CheckID="PROMO_COVARIANCE_POLICY",
            ArtifactPath=str(COV_SUMMARY.relative_to(ROOT)),
            BlockingIssue="covariance_summary_missing",
            NextAction="Build or promote source-split joint covariance policy.",
        )

    if NULL_SCORE.exists():
        nulls = pd.read_csv(NULL_SCORE)
        has_k1 = "K1_NO_MEMORY" in set(nulls.get("ModelID", pd.Series(dtype=str)).astype(str))
        has_k2 = any(nulls.get("ModelID", pd.Series(dtype=str)).astype(str).str.contains("K2", regex=False))
        has_controls = len(set(nulls.get("ModelID", pd.Series(dtype=str)).astype(str))) >= 4
        promotable = bool(has_k1 and has_k2 and has_controls)
        blockers = []
        if not has_k1:
            blockers.append("k1_null_score_missing")
        if not has_k2:
            blockers.append("k2_score_missing")
        if not has_controls:
            blockers.append("registered_null_controls_incomplete")
        add_row(
            rows,
            CheckID="PROMO_NULL_SCORECARD",
            Available=True,
            Promotable=promotable,
            ArtifactPath=str(NULL_SCORE.relative_to(ROOT)),
            BlockingIssue=";".join(blockers),
            NextAction="Score K1, locked K2, and registered nulls on the same promoted vector.",
        )
    else:
        add_row(
            rows,
            CheckID="PROMO_NULL_SCORECARD",
            ArtifactPath=str(NULL_SCORE.relative_to(ROOT)),
            BlockingIssue="likelihood_native_null_scorecard_missing",
            NextAction="Create source_split_likelihood_native_null_scorecard.csv after promotion inputs are ready.",
        )

    if EXTERNAL_K1.exists():
        external = pd.read_csv(EXTERNAL_K1)
        likelihood_native = external.get("LikelihoodNative", pd.Series([False])).map(truthy).all()
        allowed = external.get("AllowedAsPrimaryK1Candidate", pd.Series([False])).map(truthy).all()
        provenance = set(external.get("ProvenanceType", pd.Series(dtype=str)).astype(str))
        promotable = bool(likelihood_native and allowed and provenance == {"likelihood_native_baseline"})
        blockers = []
        if not likelihood_native:
            blockers.append("external_k1_not_likelihood_native")
        if not allowed:
            blockers.append("external_k1_not_primary")
        if provenance != {"likelihood_native_baseline"}:
            blockers.append("external_k1_wrong_provenance")
        add_row(
            rows,
            CheckID="PROMO_EXTERNAL_K1_EXPORT",
            Available=True,
            Promotable=promotable,
            ArtifactPath=str(EXTERNAL_K1.relative_to(ROOT)),
            BlockingIssue=";".join(blockers),
            NextAction="Generate likelihood-native K1 export only after all upstream promotion checks are clean.",
        )
    else:
        add_row(
            rows,
            CheckID="PROMO_EXTERNAL_K1_EXPORT",
            ArtifactPath=str(EXTERNAL_K1.relative_to(ROOT)),
            BlockingIssue="external_k1_export_missing",
            NextAction="Export likelihood-native K1 after baseline, coordinate, covariance, and null policy are promoted.",
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)
    blockers = output[output["BlockingIssue"].astype(str).str.len() > 0]
    promoted = bool(output["Promotable"].astype(bool).all())
    summary = pd.DataFrame(
        [
            {
                "GateID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_K1_PROMOTION_V1",
                "Checks": len(output),
                "AvailableChecks": int(output["Available"].astype(bool).sum()),
                "PromotableChecks": int(output["Promotable"].astype(bool).sum()),
                "BlockingChecks": len(blockers),
                "PrimaryK1PromotionAllowed": promoted,
                "BlockingIssue": ";".join(blockers["CheckID"].astype(str).tolist()),
                "NextAction": (
                    "Primary likelihood-native K1 is ready for external export."
                    if promoted
                    else "Resolve promotion blockers before any locked K2/null scorecard."
                ),
                "ClaimBoundary": "promotion_gate_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
