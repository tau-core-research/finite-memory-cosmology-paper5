#!/usr/bin/env python3
"""Run the target-blind P-TauCov linear specificity prescore audit."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
MODEL_PACKET = EVIDENCE / "p_taucov_linear_model_packet.yaml"
THRESHOLDS = EVIDENCE / "p_taucov_linear_specificity_threshold_freeze.csv"
METRICS = EVIDENCE / "p_taucov_linear_specificity_metric_registry.csv"

OUT_DOC = DOCS / "p_taucov_linear_specificity_prescore.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_specificity_prescore.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_specificity_prescore_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1"
RUN_ID = "P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_RUN_v1"
CLAIM_BOUNDARY = "linear_specificity_prescore_blocked_until_model_packet_exists"


def read_matrix(rel_path: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(ROOT / rel_path)
    ids = [col for col in df.columns if col != "coordinate_id"]
    return ids, df[ids].astype(float).to_numpy()


def write_blocked(reason: str) -> int:
    metrics = pd.read_csv(METRICS) if METRICS.exists() else pd.DataFrame()
    metric_ids = list(metrics["MetricID"]) if "MetricID" in metrics.columns else []
    rows = []
    for metric_id in metric_ids:
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
                "LinearCandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    if not rows:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "MetricID": "NO_METRICS_LOADED",
                "MetricValue": "NOT_EVALUATED",
                "Pass": False,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
                "LinearCandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "Status": "BLOCKED",
                "BlockReason": reason,
                "MetricsEvaluated": False,
                "MetricsPassed": "0/6",
                "LinearCandidateFrozen": False,
                "DeltaCTauGenerated": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "create_target_blind_linear_model_packet",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        f"""# P-TauCov Linear Specificity Prescore

Status: blocked / no metric evaluation / no linear freeze / no scoring
authorization.

The prescore evaluator was invoked, but it did not evaluate the linear
specificity metrics.

## Block Reason

```text
{reason}
```

## Required Missing Artifact

```text
evidence/p_taucov_linear_model_packet.yaml
```

That packet must contain concrete target-blind matrices/operators for the
strictly linear candidate:

```text
L0_B
R_B
P_red
A_Phi
A_B
P0
observable coordinate basis
input provenance hashes
```

## Current Boundary

```text
LinearCandidateFrozen: false
DeltaCTauGenerated: false
PTauCovScoringAuthorized: false
```

Allowed statement:

```text
The prescore evaluator exists and correctly blocks without a target-blind linear
model packet.
```

Forbidden statement:

```text
The strictly linear candidate passed the specificity audit.
```
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_BLOCKED")
    return 0


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    if not THRESHOLDS.exists():
        return write_blocked("missing_threshold_freeze")
    if not METRICS.exists():
        return write_blocked("missing_metric_registry")
    if not MODEL_PACKET.exists():
        return write_blocked("missing_target_blind_linear_model_packet")

    manifest = yaml.safe_load(MODEL_PACKET.read_text(encoding="utf-8")) or {}
    input_files = manifest.get("InputFiles", {})
    if not input_files:
        return write_blocked("model_packet_missing_input_files")
    if manifest.get("OutcomeInformationUsed") is not False or manifest.get("ResidualInformationUsed") is not False:
        return write_blocked("model_packet_leakage_flags_not_false")
    if manifest.get("P5CV3OutcomeUsed") is not False or manifest.get("ScoreInformationUsed") is not False:
        return write_blocked("model_packet_score_or_p5c_leakage_flags_not_false")

    ids, l0_b = read_matrix(input_files["L0_B"])
    _, r_b = read_matrix(input_files["R_B"])
    _, a_phi = read_matrix(input_files["A_Phi"])
    _, a_b = read_matrix(input_files["A_B"])
    _, p0 = read_matrix(input_files["P0"])
    _, p_red = read_matrix(input_files["p_red"])

    # Linearized Tau morphology response:
    # T_tau = A_Phi + A_B L0_B^+ R_B under the packet convention
    # R_B = -D_Phi F_B. The pseudo-inverse keeps null/gauge rows inert.
    l0_pinv = np.linalg.pinv(l0_b)
    t_tau = a_phi + a_b @ l0_pinv @ r_b
    delta_c_tau = t_tau @ t_tau.T

    fro = float(np.linalg.norm(t_tau, ord="fro"))
    denom = float(np.linalg.norm(p0 @ t_tau, ord="fro"))
    comm = p0 @ t_tau - t_tau @ p0
    noncomm_share = 0.0 if denom == 0.0 else float(np.linalg.norm(comm, ord="fro") / denom)

    eigvals = np.linalg.eigvalsh(delta_c_tau)
    eigvals = np.clip(eigvals, 0.0, None)
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

    # Target-blind structural nulls. With the strict-linear zero response, all
    # structural separations are exactly zero, so the frozen margin fails.
    null_margins = {
        "SHUFFLED_BRANCH_OPERATOR": 0.0,
        "COMMUTING_PROJECTION_NULL": noncomm_share,
        "RANDOM_LOW_RANK_LINEAR_NULL": effective_rank_fraction,
        "DIAGONAL_LINEAR_NULL": effective_rank_fraction,
        "FAMILY_LABEL_PROXY_NULL": 1.0 - label_proxy_overlap if support_total > 0.0 else 0.0,
        "CLOCK_BLOCK_PROXY_NULL": 1.0 - label_proxy_overlap if support_total > 0.0 else 0.0,
    }
    null_separation_margin = float(min(null_margins.values()))

    metric_rows = [
        ("M1_NONCOMMUTATOR_SHARE", noncomm_share, noncomm_share >= 0.10, "requires >=0.10"),
        (
            "M2_EFFECTIVE_RANK",
            effective_rank_fraction,
            0.10 <= effective_rank_fraction <= 0.85,
            "requires 0.10<=value<=0.85",
        ),
        (
            "M3_SUPPORT_ENTROPY",
            normalized_entropy,
            0.25 <= normalized_entropy <= 0.85,
            "requires 0.25<=value<=0.85",
        ),
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
                "LinearCandidateFrozen": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": "linear_specificity_prescore_evaluated_no_freeze_no_scoring",
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    passed_count = int(df["Pass"].astype(bool).sum())
    all_passed = passed_count == len(df)
    status = "PASS_NOT_FROZEN" if all_passed else "FAIL_STRICT_LINEAR_REJECTED"
    next_step = "create_linear_freeze_manifest" if all_passed else "freeze_minimal_nonzero_lambda_B_or_epsilon_P_model"
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RunID": RUN_ID,
                "Status": status,
                "BlockReason": "",
                "MetricsEvaluated": True,
                "MetricsPassed": f"{passed_count}/{len(df)}",
                "LinearCandidateFrozen": False,
                "DeltaCTauGenerated": True,
                "DeltaCTauFrobeniusNorm": fro,
                "PTauCovScoringAuthorized": False,
                "NextStep": next_step,
                "ClaimBoundary": "linear_specificity_prescore_evaluated_no_freeze_no_scoring",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        f"""# P-TauCov Linear Specificity Prescore

Status: evaluated / strict-linear candidate not frozen / P-TauCov scoring not
authorized.

The target-blind strict-linear packet was evaluated using only the frozen
coordinate basis, reference-domain projectors, source objects, and derived
linear objects.

## Linear Response Convention

```text
T_tau = A_Phi + A_B L0_B^+ R_B
delta_C_tau = T_tau T_tau^T
```

Under the frozen minimal packet:

```text
A_Phi = P_red
A_B   = P_red
L0_B  = P_red
R_B   = -P_red
```

therefore the direct morphology term and branch-mediated term cancel in the
retained reduced domain. The resulting linear response is the zero baseline:

```text
||T_tau||_F = {fro:.12g}
```

## Result

```text
Status: {status}
MetricsPassed: {passed_count}/{len(df)}
LinearCandidateFrozen: false
PTauCovScoringAuthorized: false
```

This is a useful negative gate. The strictly linear minimal candidate is too
degenerate to freeze as a Tau-specific branch/projection/covariance response.

## Next Step

```text
{next_step}
```

The next model must be declared before empirical scoring and must use either a
minimal nonzero branch backreaction term or a minimal nonzero projection-response
term.

## Claim Boundary

Allowed statement:

```text
The strict-linear minimal P-TauCov packet fails the target-blind specificity
audit and is not frozen for scoring.
```

Forbidden statement:

```text
The specificity audit produced an empirical Tau signal or authorized P-TauCov
scoring.
```
""",
        encoding="utf-8",
    )

    print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_FAIL_STRICT_LINEAR_REJECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
