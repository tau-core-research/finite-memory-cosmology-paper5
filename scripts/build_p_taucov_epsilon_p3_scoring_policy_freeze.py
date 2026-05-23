#!/usr/bin/env python3
"""Freeze epsilon-P3 P-TauCov scoring policies without authorizing scoring."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_scoring_policy_freeze.md"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze.sha256"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_scoring_policy_freeze_summary.csv"
FOLDS = ROOT / "evidence/p_taucov_epsilon_p3_fold_policy.csv"
NULLS = ROOT / "evidence/p_taucov_epsilon_p3_null_policy.csv"
COV_DF = ROOT / "evidence/p_taucov_epsilon_p3_covariance_df_policy.csv"
GATES = ROOT / "evidence/p_taucov_epsilon_p3_survival_kill_gates.csv"
BRANCH_SUPPORT = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_freeze.yaml"
FREEZE_MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_freeze_manifest.yaml"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EPSILON_P3_SCORING_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "epsilon_p3_scoring_policies_frozen_no_scorecard_no_scoring_authorization"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    for path in [BRANCH_SUPPORT, FREEZE_MANIFEST]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")

    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)

    fold_rows = [
        ("PRIMARY_LOFO_FAMILY", "primary_leave_one_family_out", True, "reuse_p5c_family_blocks_without_gain_pattern"),
        ("PRIMARY_CLOCK_BLOCK", "primary_contiguous_clock_block", True, "reuse_p5c_clock_blocks_without_gain_pattern"),
        ("SECONDARY_FAMILY_X_CLOCK", "secondary_family_x_clock_block", False, "stability_diagnostic_only"),
    ]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FoldPolicyID": policy_id,
                "FoldClass": fold_class,
                "Primary": primary,
                "Source": source,
                "RandomRowShufflePrimaryForbidden": True,
                "TargetResidualsUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for policy_id, fold_class, primary, source in fold_rows
        ]
    ).to_csv(FOLDS, index=False)

    null_rows = [
        ("OUTSIDE_BRANCH", "localization_control", "score_complement_of_frozen_omega_branch"),
        ("SHUFFLED_SUPPORT", "support_null", "shuffle_support_preserving_selected_cell_count"),
        ("MORPHOLOGY_NULL", "morphology_null", "preserve_energy_destroy_branch_relaxation_structure"),
        ("PROJECTION_NULL", "projection_null", "preserve_support_break_parent_projection_coupling"),
        ("GENERIC_RANDOM_SMOOTH_PSD", "generic_baseline", "strongest_declared_random_smooth_psd"),
        ("GENERIC_FAMILY_PERMUTED", "generic_baseline", "family_permuted_branch_structure"),
        ("GENERIC_DIAGONAL", "generic_baseline", "diagonal_variance_inflation"),
        ("GENERIC_WRONG_CLOCK", "generic_baseline", "wrong_clock_support"),
        ("GENERIC_PHASE_SHIFT", "generic_baseline", "phase_shift_support"),
    ]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "NullID": null_id,
                "NullClass": null_class,
                "Definition": definition,
                "Required": True,
                "TargetResidualsUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for null_id, null_class, definition in null_rows
        ]
    ).to_csv(NULLS, index=False)

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "PolicyID": "ALIGNMENT_STATISTIC",
                "PolicyValue": "normalized_frobenius_alignment_on_frozen_omega_branch",
                "DegreesOfFreedomPolicy": "df_not_claimed_until_scorecard_script_frozen",
                "CovariancePolicy": "whitened_covariance_residual_under_declared_baseline",
                "SignedDiagnosticPolicy": "diagnostic_only_not_survival_claim",
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "PolicyID": "LIKELIHOOD_POLICY",
                "PolicyValue": "not_authorized_by_this_artifact",
                "DegreesOfFreedomPolicy": "no_aic_bic_until_scorecard_script_frozen",
                "CovariancePolicy": "no_covariance_likelihood_score_until_final_authorization",
                "SignedDiagnosticPolicy": "cannot_rescue_failed_primary",
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    ).to_csv(COV_DF, index=False)

    gate_rows = [
        ("G1", "DELTA_C_TAU_SOURCE_LOCKED", "branch_support_from_delta_C_Tau_only"),
        ("G2", "PRIMARY_ALIGNMENT_POSITIVE", "inside_branch_alignment_positive_on_primary_folds"),
        ("G3", "BEATS_OUTSIDE_BRANCH", "inside_branch_alignment_beats_complement"),
        ("G4", "BEATS_SHUFFLED_SUPPORT", "inside_branch_alignment_beats_shuffled_support"),
        ("G5", "BEATS_MORPHOLOGY_NULL", "tau_response_beats_morphology_null"),
        ("G6", "BEATS_PROJECTION_NULL", "tau_response_beats_projection_null"),
        ("G7", "BEATS_GENERIC_BASELINES", "beats_all_declared_generic_baselines"),
        ("G8", "NO_SINGLE_FOLD_DOMINANCE", "no_single_fold_over_60_percent_positive_gain_unless_predeclared"),
        ("G9", "SIGNED_DIAGNOSTIC_NOT_PROMOTED", "signed_diagnostic_cannot_establish_survival"),
        ("K1", "KILL_IF_SUPPORT_FROM_OUTCOME", "kill_if_branch_support_uses_p5c_gain_or_heldout_residuals"),
        ("K2", "KILL_IF_ANY_REQUIRED_NULL_BEATS", "kill_if_required_null_beats_primary_tau_support"),
        ("K3", "KILL_IF_SCORECARD_SCRIPT_CHANGED_AFTER_SCORING", "kill_if_scorecard_hash_not_prefrozen"),
    ]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "GateName": gate_name,
                "Requirement": requirement,
                "Required": True,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, gate_name, requirement in gate_rows
        ]
    ).to_csv(GATES, index=False)

    input_files = {
        "epsilon_p3_freeze": str(FREEZE_MANIFEST.relative_to(ROOT)),
        "branch_support": str(BRANCH_SUPPORT.relative_to(ROOT)),
        "fold_policy": str(FOLDS.relative_to(ROOT)),
        "null_policy": str(NULLS.relative_to(ROOT)),
        "covariance_df_policy": str(COV_DF.relative_to(ROOT)),
        "survival_kill_gates": str(GATES.relative_to(ROOT)),
    }
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": "SCORING_POLICIES_FROZEN_NO_AUTHORIZATION",
        "FoldPolicyFrozen": True,
        "NullPolicyFrozen": True,
        "CovarianceDFPolicyFrozen": True,
        "SurvivalKillGatesFrozen": True,
        "BranchSupportFrozen": True,
        "ScorecardScriptFrozen": False,
        "PTauCovScoringAuthorized": False,
        "ReasonScoringNotAuthorized": "scorecard_script_and_final_authorization_manifest_not_frozen",
        "InputFiles": input_files,
        "InputSHA256": {key: file_sha256(ROOT / rel) for key, rel in input_files.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in [FOLDS, NULLS, COV_DF, GATES, MANIFEST]) + "\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": manifest["Status"],
                "FrozenPolicyItems": 4,
                "BranchSupportFrozen": True,
                "ScorecardScriptFrozen": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "freeze_scorecard_script_and_build_final_authorization_manifest",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)

    DOC.write_text(
        """# P-TauCov Epsilon-P3 Scoring Policy Freeze

Status: scoring policies frozen / scoring not authorized.

This artifact freezes the policy layer needed before any epsilon-P3 P-TauCov
score can be run:

- primary fold policy;
- required null controls;
- covariance and degrees-of-freedom policy;
- survival and kill gates.

It does not freeze the final scorecard script and therefore does not authorize
empirical scoring.

## Scoring Boundary

```text
PTauCovScoringAuthorized: false
Reason: scorecard script and final authorization manifest are not frozen
```

Allowed statement:

```text
The epsilon-P3 scoring policies are frozen for later authorization.
```

Forbidden statement:

```text
The epsilon-P3 candidate has been scored or has produced a Tau-specific
observational signal.
```
""",
        encoding="utf-8",
    )

    for path in [FOLDS, NULLS, COV_DF, GATES, MANIFEST, SHA256, SUMMARY, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    print("P_TAUCOV_EPSILON_P3_SCORING_POLICIES_FROZEN_NO_AUTHORIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
