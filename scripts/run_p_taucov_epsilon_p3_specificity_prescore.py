#!/usr/bin/env python3
"""Run the target-blind epsilon_P3 P-TauCov specificity prescore audit."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_specificity_prescore.md"
CSV = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore_summary.csv"
MODEL_PACKET = ROOT / "evidence/p_taucov_epsilon_p3_model_packet.yaml"
THRESHOLDS = ROOT / "evidence/p_taucov_linear_specificity_threshold_freeze.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_EPSILON_P3_SPECIFICITY_AUDIT_v1"
RUN_ID = "P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_RUN_v1"


def read_matrix(rel_path: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(ROOT / rel_path)
    ids = [col for col in df.columns if col != "coordinate_id"]
    return ids, df[ids].astype(float).to_numpy()


def write_blocked(reason: str) -> int:
    rows = []
    for metric_id in [
        "M1_NONCOMMUTATOR_SHARE",
        "M2_EFFECTIVE_RANK",
        "M3_SUPPORT_ENTROPY",
        "M4_LABEL_PROXY_OVERLAP",
        "M5_NULL_SEPARATION_MARGIN",
        "M6_OUTCOME_LEAKAGE_CERTIFICATE",
    ]:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "MetricID": metric_id,
                "MetricValue": "NOT_EVALUATED",
                "Pass": False,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
                "EpsilonP3CandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": "epsilon_p3_specificity_prescore_blocked_no_scoring",
            }
        )
    pd.DataFrame(rows).to_csv(CSV, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "MetricsEvaluated": False,
                "MetricsPassed": "0/6",
                "EpsilonP3CandidateFrozen": False,
                "DeltaCTauGenerated": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "repair_missing_epsilon_p_packet_inputs",
                "ClaimBoundary": "epsilon_p3_specificity_prescore_blocked_no_scoring",
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Specificity Prescore

Status: blocked / no metric evaluation / no scoring authorization.

Block reason:

```text
{reason}
```
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_BLOCKED")
    return 0


def main() -> int:
    DOC.parent.mkdir(exist_ok=True)
    CSV.parent.mkdir(exist_ok=True)
    if not MODEL_PACKET.exists():
        return write_blocked("missing_epsilon_p3_model_packet")
    if not THRESHOLDS.exists():
        return write_blocked("missing_threshold_freeze")

    manifest = yaml.safe_load(MODEL_PACKET.read_text(encoding="utf-8")) or {}
    if manifest.get("OutcomeInformationUsed") is not False or manifest.get("ResidualInformationUsed") is not False:
        return write_blocked("model_packet_leakage_flags_not_false")
    if manifest.get("P5CV3OutcomeUsed") is not False or manifest.get("ScoreInformationUsed") is not False:
        return write_blocked("model_packet_score_or_p5c_leakage_flags_not_false")

    input_files = manifest.get("InputFiles", {})
    ids, l0_b = read_matrix(input_files["L0_B"])
    _, r_b = read_matrix(input_files["R_B"])
    _, a_phi = read_matrix(input_files["A_Phi"])
    _, a_b = read_matrix(input_files["A_B"])
    _, p0 = read_matrix(input_files["P0"])
    _, p1 = read_matrix(input_files["P3"])
    _, p_red = read_matrix(input_files["p_red"])

    epsilon_p = float(manifest.get("epsilon_P", 1))
    base = a_phi + a_b @ np.linalg.pinv(l0_b) @ r_b
    t_tau = base + epsilon_p * p1
    delta_c_tau = t_tau @ t_tau.T

    fro = float(np.linalg.norm(t_tau, ord="fro"))
    denom = float(np.linalg.norm(p_red @ t_tau, ord="fro"))
    comm = p_red @ t_tau - t_tau @ p_red
    noncomm_share = 0.0 if denom == 0.0 else float(np.linalg.norm(comm, ord="fro") / denom)

    eigvals = np.clip(np.linalg.eigvalsh(delta_c_tau), 0.0, None)
    total = float(eigvals.sum())
    if total == 0.0:
        effective_rank_fraction = 0.0
        normalized_entropy = 0.0
    else:
        probs = eigvals[eigvals > 0.0] / total
        entropy = float(-(probs * np.log(probs)).sum())
        effective_rank_fraction = float(np.exp(entropy) / len(eigvals))
        normalized_entropy = float(entropy / np.log(len(eigvals))) if len(eigvals) > 1 else 0.0

    basis = pd.read_csv(ROOT / input_files["coordinate_basis"])
    label_rows = basis["coordinate_family"].isin(["ExternalMetadata", "CoordinateConvention"]).to_numpy()
    support = np.sum(np.abs(delta_c_tau), axis=1)
    support_total = float(support.sum())
    label_proxy_overlap = 0.0 if support_total == 0.0 else float(support[label_rows].sum() / support_total)

    diagonal_share = 0.0 if np.linalg.norm(delta_c_tau, ord="fro") == 0.0 else float(
        np.linalg.norm(np.diag(np.diag(delta_c_tau))) / np.linalg.norm(delta_c_tau, ord="fro")
    )
    null_margins = {
        "COMMUTING_PROJECTION_NULL": noncomm_share,
        "RANK_COLLAPSE_NULL": effective_rank_fraction,
        "ENTROPY_COLLAPSE_NULL": normalized_entropy,
        "LABEL_PROXY_NULL": 1.0 - label_proxy_overlap,
        "DIAGONAL_LINEAR_NULL": 1.0 - diagonal_share,
    }
    null_separation_margin = float(min(null_margins.values()))

    metric_rows = [
        ("M1_NONCOMMUTATOR_SHARE", noncomm_share, noncomm_share >= 0.10, "requires >=0.10"),
        ("M2_EFFECTIVE_RANK", effective_rank_fraction, 0.10 <= effective_rank_fraction <= 0.85, "requires 0.10<=value<=0.85"),
        ("M3_SUPPORT_ENTROPY", normalized_entropy, 0.25 <= normalized_entropy <= 0.85, "requires 0.25<=value<=0.85"),
        ("M4_LABEL_PROXY_OVERLAP", label_proxy_overlap, label_proxy_overlap <= 0.35, "requires <=0.35"),
        ("M5_NULL_SEPARATION_MARGIN", null_separation_margin, null_separation_margin >= 0.05, "requires >=0.05"),
        ("M6_OUTCOME_LEAKAGE_CERTIFICATE", 1.0, True, "manifest leakage flags false"),
    ]
    rows = []
    for metric_id, value, passed, threshold in metric_rows:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "MetricID": metric_id,
                "MetricValue": value,
                "Pass": bool(passed),
                "Status": "PASS" if passed else "FAIL",
                "BlockReason": "",
                "Threshold": threshold,
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
                "EpsilonP3CandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": "epsilon_p3_specificity_prescore_evaluated_no_freeze_no_scoring",
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(CSV, index=False)

    passed_count = int(df["Pass"].astype(bool).sum())
    status = "PASS_NOT_FROZEN" if passed_count == len(df) else "FAIL_EPSILON_P3_NOT_SPECIFIC"
    next_step = "create_epsilon_p3_freeze_manifest" if status == "PASS_NOT_FROZEN" else "revise_target_blind_projection_support_operator"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "Status": status,
                "BlockReason": "",
                "MetricsEvaluated": True,
                "MetricsPassed": f"{passed_count}/{len(df)}",
                "EpsilonP3CandidateFrozen": False,
                "DeltaCTauGenerated": True,
                "DeltaCTauFrobeniusNorm": fro,
                "PTauCovScoringAuthorized": False,
                "NextStep": next_step,
                "ClaimBoundary": "epsilon_p3_specificity_prescore_evaluated_no_freeze_no_scoring",
            }
        ]
    ).to_csv(SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Specificity Prescore

Status: evaluated / epsilon-P3 candidate not yet frozen / P-TauCov scoring not
authorized.

This prescore evaluates the target-blind epsilon-P3 model packet:

```text
T_tau_epsilon = A_Phi + A_B L0_B^+ R_B + epsilon_P P3
delta_C_tau = T_tau_epsilon T_tau_epsilon^T
```

The strict-linear base term cancels, so the active nonzero structure comes from
the frozen `P3` projection-response operator.

## Result

```text
Status: {status}
MetricsPassed: {passed_count}/{len(df)}
||T_tau_epsilon||_F = {fro:.12g}
PTauCovScoringAuthorized: false
```

## Metric Values

```text
M1_NONCOMMUTATOR_SHARE = {noncomm_share:.12g}
M2_EFFECTIVE_RANK = {effective_rank_fraction:.12g}
M3_SUPPORT_ENTROPY = {normalized_entropy:.12g}
M4_LABEL_PROXY_OVERLAP = {label_proxy_overlap:.12g}
M5_NULL_SEPARATION_MARGIN = {null_separation_margin:.12g}
M6_OUTCOME_LEAKAGE_CERTIFICATE = true
```

Passing this prescore would only allow a later freeze manifest. It does not
authorize empirical P-TauCov scoring.

## Claim Boundary

Allowed statement:

```text
The epsilon-P3 candidate has been evaluated by target-blind specificity metrics.
```

Forbidden statement:

```text
The epsilon-P3 candidate has produced a P-TauCov score, survival result, or
empirical Tau signal.
```
""",
        encoding="utf-8",
    )
    print(f"P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
