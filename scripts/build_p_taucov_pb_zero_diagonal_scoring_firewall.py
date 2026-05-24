#!/usr/bin/env python3
"""Build scoring firewall for the frozen PB zero-diagonal object."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_v1"
CLAIM = "pb_zero_diagonal_scoring_firewall_no_scoring"

OBJECT_MANIFEST = EVIDENCE / "p_taucov_pb_zero_diagonal_object_manifest.csv"
OBJECT_VALIDATION = EVIDENCE / "p_taucov_pb_zero_diagonal_object_validation.csv"
OBJECT_MATRIX = EVIDENCE / "p_taucov_pb_zero_diagonal_object_matrix.csv"

POLICY_FILES = {
    "scorecard_script_freeze": EVIDENCE / "p_taucov_pb_zero_diagonal_scorecard_script_freeze_summary.csv",
    "fold_policy": EVIDENCE / "p_taucov_pb_zero_diagonal_fold_policy_summary.csv",
    "null_comparators": EVIDENCE / "p_taucov_pb_zero_diagonal_null_comparators_summary.csv",
    "df_covariance_policy": EVIDENCE / "p_taucov_pb_zero_diagonal_df_covariance_policy_summary.csv",
    "survival_kill_gates": EVIDENCE / "p_taucov_pb_zero_diagonal_survival_kill_gates_summary.csv",
}

OUT_TABLE = EVIDENCE / "p_taucov_pb_zero_diagonal_scoring_firewall.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_pb_zero_diagonal_scoring_firewall_summary.csv"
OUT_DOC = DOCS / "p_taucov_pb_zero_diagonal_scoring_firewall.md"

EXPECTED_OBJECT_STATUS = "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING"


def validation_passes(path: Path) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    return bool(df.loc[df["Required"], "Passed"].all())


def main() -> int:
    object_exists = OBJECT_MANIFEST.exists() and OBJECT_MATRIX.exists()
    object_status_ok = False
    object_validation_ok = validation_passes(OBJECT_VALIDATION)
    object_hash = ""
    if object_exists:
        manifest = pd.read_csv(OBJECT_MANIFEST).iloc[0]
        object_status_ok = str(manifest["Status"]) == EXPECTED_OBJECT_STATUS
        object_hash = str(manifest["MatrixSHA256"])

    records = [
        ("PB-FW1_OBJECT_FROZEN", object_exists and object_status_ok, "Frozen PB zero-diagonal object exists with expected status."),
        ("PB-FW2_OBJECT_VALIDATION_PASS", object_validation_ok, "Object freeze validation passes."),
        ("PB-FW3_OBJECT_HASH_READY", bool(object_hash), "Object matrix hash is fixed."),
    ]
    for key, path in POLICY_FILES.items():
        records.append((f"PB-FW_POLICY_{key.upper()}", path.exists(), f"Required policy file exists: {path.name}"))

    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FirewallItemID": item_id,
                "Satisfied": bool(satisfied),
                "Meaning": meaning,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
            for item_id, satisfied, meaning in records
        ]
    )
    table.to_csv(OUT_TABLE, index=False)
    missing = table.loc[~table["Satisfied"], "FirewallItemID"].astype(str).tolist()
    ready = len(missing) == 0
    status = (
        "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_AUTHORIZATION_READY"
        if ready
        else "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_BLOCKED"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "SatisfiedItems": int(table["Satisfied"].sum()),
                "TotalItems": len(table),
                "MissingItems": ";".join(missing),
                "ObjectMatrixSHA256": object_hash,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    missing_text = "\n".join(f"- `{item}`" for item in missing) if missing else "- none"
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov PB Zero-Diagonal Scoring Firewall",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                f"Status: `{status}`",
                "",
                "## Purpose",
                "",
                "This firewall checks whether the frozen `PB_ZERO_DIAGONAL_OUTER_PRODUCT`",
                "object is ready for a future empirical scorecard. It deliberately does",
                "not authorize scoring by itself.",
                "",
                "## Missing Items",
                "",
                missing_text,
                "",
                "## Interpretation",
                "",
                "A frozen object is now available, but a separate scorecard-script freeze,",
                "fold policy, null-comparator policy, df/covariance policy, and survival/",
                "kill-gate policy must be declared for this object before scoring.",
                "",
                "## Links",
                "",
                "- [`p_taucov_pb_zero_diagonal_object_freeze.md`](p_taucov_pb_zero_diagonal_object_freeze.md)",
                "- [`p_taucov_pb_interaction_object_preflight.md`](p_taucov_pb_interaction_object_preflight.md)",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> The PB zero-diagonal object has a scoring firewall that records which pre-scoring policies remain missing.",
                "",
                "Forbidden statement:",
                "",
                "> This firewall authorizes scoring, reports survival, or validates Tau Core.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
