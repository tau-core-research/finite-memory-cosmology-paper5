#!/usr/bin/env python3
"""Check whether any source-split K1 candidate can be promoted to primary K1."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CANDIDATE_SUMMARY = EVIDENCE / "source_split_k1_response_candidate_summary.csv"
SENSITIVITY = EVIDENCE / "source_split_k1_candidate_sensitivity.csv"
REQUIREMENTS = EVIDENCE / "source_split_k1_response_requirements.csv"
OUT = EVIDENCE / "source_split_k1_candidate_promotion_readiness.csv"
SUMMARY = EVIDENCE / "source_split_k1_candidate_promotion_summary.csv"


def bool_value(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def promotion_reasons(row: pd.Series, best_sensitivity_model: str | None) -> list[str]:
    reasons: list[str] = []
    candidate_id = str(row["K1CandidateID"])
    candidate_class = str(row["CandidateClass"])
    nonzero_rows = int(row["NonzeroRows"])
    allowed_primary = bool_value(row["AllowedAsPrimaryK1"])
    risk = str(row["Risk"])

    if nonzero_rows <= 0:
        reasons.append("zero_response_degenerate_for_multiplicative_k2")
    if not allowed_primary:
        reasons.append("not_allowed_as_primary_k1_in_candidate_audit")
    if candidate_class == "diagnostic_control":
        reasons.append("diagnostic_control_not_primary_source_split_k1")
    if candidate_class == "candidate_k1_sensitivity":
        reasons.append("sensitivity_candidate_requires_predeclared_external_provenance")
    if "same exported family responses" in risk:
        reasons.append("same_exported_family_response_not_external_k1")
    if "single-branch control" in risk:
        reasons.append("single_branch_control_not_source_split_no_memory_target")
    if candidate_id == "K1_ZERO_CONTRAST_CURRENT":
        reasons.append("fair_null_must_remain_null_comparator")
    if best_sensitivity_model and best_sensitivity_model.startswith(candidate_id):
        reasons.append("best_score_is_not_promotion_authority")

    return reasons


def requirement_status(requirements: pd.DataFrame, requirement_id: str) -> str:
    match = requirements[requirements["RequirementID"].astype(str).eq(requirement_id)]
    if match.empty:
        return "missing_requirement_row"
    return str(match.iloc[0]["CurrentStatus"])


def main() -> None:
    candidate_summary = pd.read_csv(CANDIDATE_SUMMARY)
    sensitivity = pd.read_csv(SENSITIVITY)
    requirements = pd.read_csv(REQUIREMENTS)

    best = sensitivity.sort_values(["AIC", "Chi2"]).iloc[0]
    best_model = str(best["ModelID"])
    best_candidate = str(best["K1CandidateID"])

    rows: list[dict[str, object]] = []
    for _, row in candidate_summary.iterrows():
        candidate_id = str(row["K1CandidateID"])
        candidate_models = sensitivity[sensitivity["K1CandidateID"].astype(str).eq(candidate_id)]
        best_candidate_model = candidate_models.sort_values(["AIC", "Chi2"]).iloc[0]
        reasons = promotion_reasons(row, best_model)
        promotion_authorized = len(reasons) == 0
        rows.append(
            {
                "GateID": "SOURCE_SPLIT_K1_CANDIDATE_PROMOTION_V1",
                "K1CandidateID": candidate_id,
                "CandidateClass": row["CandidateClass"],
                "Rows": int(row["Rows"]),
                "NonzeroRows": int(row["NonzeroRows"]),
                "AllowedAsPrimaryK1InAudit": bool_value(row["AllowedAsPrimaryK1"]),
                "BestCandidateModel": best_candidate_model["ModelID"],
                "BestCandidateAIC": float(best_candidate_model["AIC"]),
                "BestCandidateStatus": best_candidate_model["Status"],
                "IsGlobalBestAICCandidate": candidate_id == best_candidate,
                "PromotionAuthorized": promotion_authorized,
                "BlockingIssue": "" if promotion_authorized else ";".join(reasons),
                "RequiredNextCheck": (
                    "freeze as primary source-split K1 before K2 scoring"
                    if promotion_authorized
                    else "derive externally predeclared nonzero K1 or likelihood-native K1 target"
                ),
                "ClaimBoundary": "k1_promotion_gate_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    promoted = output[output["PromotionAuthorized"].astype(bool)]
    summary = pd.DataFrame(
        [
            {
                "GateID": "SOURCE_SPLIT_K1_CANDIDATE_PROMOTION_V1",
                "Candidates": len(output),
                "PromotedPrimaryK1Count": len(promoted),
                "AnyPromotionAuthorized": len(promoted) > 0,
                "BestAICModel": best_model,
                "BestAICCandidateID": best_candidate,
                "BestAICCandidatePromotionAuthorized": bool(
                    output[
                        output["K1CandidateID"].astype(str).eq(best_candidate)
                    ]["PromotionAuthorized"].iloc[0]
                ),
                "NonzeroRequirementStatus": requirement_status(requirements, "K1R1_NONZERO_RESPONSE_TARGET"),
                "NoSameDataRescueStatus": requirement_status(requirements, "K1R2_NO_SAME_DATA_AMPLITUDE_RESCUE"),
                "Conclusion": (
                    "primary_k1_available"
                    if len(promoted) > 0
                    else "no_primary_k1_promoted; k2_scoring_requires_external_nonzero_or_likelihood_native_k1"
                ),
                "ClaimBoundary": "k1_promotion_gate_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
