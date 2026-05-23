#!/usr/bin/env python3
"""Build the P-TauCov target-blind reference-domain selection rule."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_reference_domain_selection_rule.md"
OUT_CSV = EVIDENCE / "p_taucov_reference_domain_selection_rule.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_reference_domain_selection_rule_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
RULE_ID = "P_TAUCOV_REFERENCE_DOMAIN_SELECTION_RULE_v1"
CLAIM_BOUNDARY = "target_blind_selection_rule_declared_no_values_no_packet"

ROWS = [
    {
        "Object": "Phi_0",
        "SelectionRule": "choose the frozen coordinate-basis origin if physically declared; otherwise choose the frozen coordinate-basis center; neither option may use residual, score, or family-gain information",
        "RequiredInput": "frozen_coordinate_basis",
        "ConcreteValueSet": False,
        "BlocksLinearPacket": True,
    },
    {
        "Object": "B_star_at_Phi_0",
        "SelectionRule": "solve F_B(Phi_0,B)=0 only after F_B and Phi_0 are frozen",
        "RequiredInput": "F_B_and_Phi_0",
        "ConcreteValueSet": False,
        "BlocksLinearPacket": True,
    },
    {
        "Object": "P_null",
        "SelectionRule": "span of exact zero modes of the candidate L_B on the frozen branch basis, declared before inversion",
        "RequiredInput": "candidate_L_B_and_branch_basis",
        "ConcreteValueSet": False,
        "BlocksLinearPacket": True,
    },
    {
        "Object": "P_gauge",
        "SelectionRule": "span of coordinate-duplicate or symmetry-redundant source modes defined by basis symmetries; empty set requires an explicit no-redundancy certificate",
        "RequiredInput": "basis_symmetry_certificate",
        "ConcreteValueSet": False,
        "BlocksLinearPacket": True,
    },
    {
        "Object": "P_forbidden",
        "SelectionRule": "span of outcome-derived columns or target-leaking fields; empty set requires an input-provenance leakage certificate",
        "RequiredInput": "input_provenance_leakage_certificate",
        "ConcreteValueSet": False,
        "BlocksLinearPacket": True,
    },
    {
        "Object": "P_red",
        "SelectionRule": "build P_red = I - P_null - P_gauge - P_forbidden after all three exclusion subspaces are frozen",
        "RequiredInput": "P_null_P_gauge_P_forbidden",
        "ConcreteValueSet": False,
        "BlocksLinearPacket": True,
    },
]

FORBIDDEN_INPUTS = [
    "held_out_residuals",
    "P5C_v3_gains",
    "OOS_DeltaNLL",
    "family_localization_after_scoring",
    "linear_specificity_metric_result",
    "post_hoc_support_localization",
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "RuleID": RULE_ID,
                **row,
                "OutcomeInformationAllowed": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "RuleID": RULE_ID,
                "ObjectsCovered": len(df),
                "SelectionRuleDeclared": True,
                "ConcretePhi0Set": False,
                "ConcreteBasisSet": False,
                "ReducedDomainFrozen": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ForbiddenInputs": ";".join(FORBIDDEN_INPUTS),
                "NextStep": "freeze_coordinate_basis_then_apply_selection_rule",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Reference-Domain Selection Rule

Status: target-blind selection rule / no concrete `Phi_0` / no concrete basis /
no reduced-domain matrix / no linear packet / no metric evaluation / no scoring
authorization.

This note sharpens the reference-domain freeze policy into a selection rule. It
does not choose a numerical reference state. It only declares how the reference
state and excluded subspaces may be chosen once the coordinate basis and Tau-side
operators exist.

## Selection Rule

| Object | Target-blind rule |
| --- | --- |
| `Phi_0` | Choose the frozen coordinate-basis origin if physically declared; otherwise choose the frozen coordinate-basis center. The choice must be made from the coordinate/source convention only. |
| `B_*(Phi_0)` | Solve `F_B(Phi_0,B)=0` only after `F_B` and `Phi_0` are frozen. |
| `P_null` | Use the span of exact zero modes of the candidate `L_B` on the frozen branch basis, declared before inversion. |
| `P_gauge` | Use the span of coordinate-duplicate or symmetry-redundant source modes defined by basis symmetries. If no such modes exist, an explicit no-redundancy certificate is required. |
| `P_forbidden` | Use the span of outcome-derived columns or target-leaking fields. If empty, an input-provenance leakage certificate is required. |
| `P_red` | Build `P_red = I - P_null - P_gauge - P_forbidden` only after all three exclusion subspaces are frozen. |

## Forbidden Inputs

The selection rule must not use:

```text
held-out residuals
P5C v3 gains
OOS DeltaNLL
family localization after scoring
linear specificity metric result
post-hoc support localization
```

## What Is Still Missing

This artifact does not supply:

```text
concrete Phi_0
concrete coordinate basis
concrete null/gauge/forbidden bases
concrete P_red
linear model packet
linear specificity metric evaluation
P-TauCov scoring authorization
```

## Claim Boundary

Allowed statement:

```text
A target-blind reference-domain selection rule is declared.
```

Forbidden statement:

```text
The P-TauCov reference state or reduced domain has been frozen.
```

## Next Gate

The next gate is to freeze a coordinate/source basis, then apply this rule to
produce concrete `Phi_0`, `P_null`, `P_gauge`, `P_forbidden`, and `P_red`
artifacts with provenance hashes.
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
