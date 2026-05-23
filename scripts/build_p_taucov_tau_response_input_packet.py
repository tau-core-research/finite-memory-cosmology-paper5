#!/usr/bin/env python3
"""Build the P-TauCov Tau-response input packet.

The packet decomposes the blocked delta_C_Tau source schema into actionable
source classes: already declared formulas, policy-freezable choices, and genuine
Tau-theory blockers. It does not authorize scoring.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_tau_response_input_packet.md"
OUT_CSV = EVIDENCE / "p_taucov_tau_response_input_packet.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tau_response_input_packet_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_TAU_RESPONSE_INPUT_PACKET_v1"
CLAIM_BOUNDARY = "tau_response_input_packet_no_delta_c_tau_no_scoring_authorization"


ROWS = [
    {
        "SourceObject": "PhiPerturbationFamily",
        "SourceClass": "POLICY_FREEZABLE",
        "ProposedRoute": "Declare a finite parent perturbation basis before target scoring.",
        "CurrentStatus": "ROUTE_DEFINED_NOT_FROZEN",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "BranchEquationFB",
        "SourceClass": "TAU_THEORY_BLOCKER",
        "ProposedRoute": "Derive or declare the reduced branch equation F_B(Phi,B)=0 from the Tau parent branch model.",
        "CurrentStatus": "MISSING_CONCRETE_OPERATOR",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "ReducedBranchOperatorLBred",
        "SourceClass": "TAU_THEORY_BLOCKER",
        "ProposedRoute": "Compute the reduced linearization L_B^red from F_B on the frozen branch domain.",
        "CurrentStatus": "MISSING_CONCRETE_OPERATOR",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "BranchDomainPolicy",
        "SourceClass": "POLICY_AND_THEORY",
        "ProposedRoute": "Freeze invertible branch subspace, null-mode exclusions, and regularization convention.",
        "CurrentStatus": "ROUTE_DEFINED_NOT_FROZEN",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "BranchResponseRule",
        "SourceClass": "FORMULA_READY",
        "ProposedRoute": "Use deltaB_star = -(L_B^red)^-1 D_Phi F_B[deltaPhi] after L_B^red exists.",
        "CurrentStatus": "FORMULA_DECLARED_OPERATOR_MISSING",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "ParentMorphologyMap",
        "SourceClass": "TAU_THEORY_BLOCKER",
        "ProposedRoute": "Define M_parent(Phi,B) as the Tau-side morphology variable feeding covariance.",
        "CurrentStatus": "MISSING_CONCRETE_MAP",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "ProjectionMorphologyMap",
        "SourceClass": "TAU_THEORY_BLOCKER",
        "ProposedRoute": "Define P_morph(Phi,B) independent of P5C v3 outcome and target residuals.",
        "CurrentStatus": "MISSING_CONCRETE_PROJECTION",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "ProjectedMorphologyDerivativePhi",
        "SourceClass": "DERIVED_AFTER_MAPS",
        "ProposedRoute": "Differentiate M_proj with respect to Phi after M_parent and P_morph are frozen.",
        "CurrentStatus": "BLOCKED_BY_MAPS",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "ProjectedMorphologyDerivativeB",
        "SourceClass": "DERIVED_AFTER_MAPS",
        "ProposedRoute": "Differentiate M_proj with respect to B after M_parent and P_morph are frozen.",
        "CurrentStatus": "BLOCKED_BY_MAPS",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "CovarianceFunctionalDerivative",
        "SourceClass": "POLICY_FREEZABLE",
        "ProposedRoute": "Freeze D_M C as a linear map from morphology response to covariance response.",
        "CurrentStatus": "ROUTE_DEFINED_NOT_FROZEN",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "ObservableCoordinateIndex",
        "SourceClass": "POLICY_FREEZABLE",
        "ProposedRoute": "Reuse frozen observable coordinate basis only if it is declared before delta_C_Tau generation.",
        "CurrentStatus": "ROUTE_DEFINED_NOT_FROZEN",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "NormalizationPolicy",
        "SourceClass": "POLICY_FREEZABLE",
        "ProposedRoute": "Freeze sign, Frobenius/trace normalization, and zero-denominator policy before support extraction.",
        "CurrentStatus": "ROUTE_DEFINED_NOT_FROZEN",
        "BlocksDeltaCTau": True,
    },
    {
        "SourceObject": "LeakageExclusionAudit",
        "SourceClass": "AUDIT_REQUIRED",
        "ProposedRoute": "Hash inputs and prove absence of held-out residuals, v3 gain pattern, and post-score family selection.",
        "CurrentStatus": "NOT_RUN",
        "BlocksDeltaCTau": True,
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "SourceObject": row["SourceObject"],
                "SourceClass": row["SourceClass"],
                "ProposedRoute": row["ProposedRoute"],
                "CurrentStatus": row["CurrentStatus"],
                "BlocksDeltaCTau": row["BlocksDeltaCTau"],
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    class_counts = df.groupby("SourceClass").size().to_dict()
    theory_blockers = int((df["SourceClass"] == "TAU_THEORY_BLOCKER").sum())
    policy_freezable = int((df["SourceClass"] == "POLICY_FREEZABLE").sum())
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "TotalSourceObjects": len(df),
                "TauTheoryBlockers": theory_blockers,
                "PolicyFreezableObjects": policy_freezable,
                "FormulaReadyObjects": int((df["SourceClass"] == "FORMULA_READY").sum()),
                "DerivedAfterMapsObjects": int((df["SourceClass"] == "DERIVED_AFTER_MAPS").sum()),
                "AuditRequiredObjects": int((df["SourceClass"] == "AUDIT_REQUIRED").sum()),
                "DeltaCTauGenerationStatus": "BLOCKED_BY_TAU_THEORY_INPUTS",
                "PrimaryNextStep": "define_F_B_LBred_M_parent_P_morph",
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
                "ClassCounts": ";".join(f"{key}:{value}" for key, value in sorted(class_counts.items())),
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Tau-Response Input Packet

Status: input packet / blocker decomposition / no scoring authorization.

This packet turns the blocked `delta_C_Tau` source schema into an actionable
work plan. It does not generate `delta_C_Tau`. It identifies which missing
objects are simple freeze policies and which are genuine Tau-theory blockers.

## Blocker Classes

| Class | Meaning |
| --- | --- |
| `TAU_THEORY_BLOCKER` | Requires a concrete Tau-side operator or map. |
| `POLICY_FREEZABLE` | Can be frozen by protocol choice before scoring. |
| `POLICY_AND_THEORY` | Needs both a convention and a theory-side domain. |
| `FORMULA_READY` | Formula exists, but depends on missing operators. |
| `DERIVED_AFTER_MAPS` | Becomes computable after the maps are frozen. |
| `AUDIT_REQUIRED` | Requires a leakage and provenance audit. |

## Current Scientific Bottleneck

The primary bottleneck is not statistics. It is the Tau-side response model:

```text
F_B, L_B^red, M_parent, P_morph
```

Until those four objects exist in a target-blind form, any `delta_C_Tau` matrix
would be an artificial placeholder and must not be scored.

## Object Routes

| Source object | Class | Current status |
| --- | --- | --- |
| `PhiPerturbationFamily` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `BranchEquationFB` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_OPERATOR` |
| `ReducedBranchOperatorLBred` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_OPERATOR` |
| `BranchDomainPolicy` | `POLICY_AND_THEORY` | `ROUTE_DEFINED_NOT_FROZEN` |
| `BranchResponseRule` | `FORMULA_READY` | `FORMULA_DECLARED_OPERATOR_MISSING` |
| `ParentMorphologyMap` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_MAP` |
| `ProjectionMorphologyMap` | `TAU_THEORY_BLOCKER` | `MISSING_CONCRETE_PROJECTION` |
| `ProjectedMorphologyDerivativePhi` | `DERIVED_AFTER_MAPS` | `BLOCKED_BY_MAPS` |
| `ProjectedMorphologyDerivativeB` | `DERIVED_AFTER_MAPS` | `BLOCKED_BY_MAPS` |
| `CovarianceFunctionalDerivative` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `ObservableCoordinateIndex` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `NormalizationPolicy` | `POLICY_FREEZABLE` | `ROUTE_DEFINED_NOT_FROZEN` |
| `LeakageExclusionAudit` | `AUDIT_REQUIRED` | `NOT_RUN` |

## Reviewer-Safe Interpretation

Allowed statement:

```text
The P-TauCov program has isolated the Tau-side objects required before a
branch-localized covariance response can be tested.
```

Forbidden statement:

```text
The P-TauCov program has already produced a Tau-specific covariance response.
```

## Next Valid Step

Define a minimal target-blind Tau-side response model for:

```text
F_B
L_B^red
M_parent
P_morph
```

Once those are supplied, the derivatives and `delta_C_Tau` generator can be
constructed without borrowing the P5C v3 outcome.
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
