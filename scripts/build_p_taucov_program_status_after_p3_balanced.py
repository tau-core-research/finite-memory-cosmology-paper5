#!/usr/bin/env python3
"""Build program-level status after P3 balanced scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evidence/p_taucov_program_status_after_signed_scorecard.csv"
DIAG = ROOT / "evidence/p_taucov_diagonal_orthogonal_scorecard_interpretation.csv"
P3 = ROOT / "evidence/p_taucov_p3_balanced_scorecard_interpretation.csv"
OUT_CSV = ROOT / "evidence/p_taucov_program_status_after_p3_balanced.csv"
OUT_MD = ROOT / "docs/p_taucov_program_status_after_p3_balanced.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
STATUS = "P_TAUCOV_PROTOCOL_INFRASTRUCTURE_VALID_BUT_P3_BALANCED_NEGATIVE_NO_TAU_SIGNAL"


def main() -> int:
    base = pd.read_csv(BASE).iloc[0]
    diag = pd.read_csv(DIAG).iloc[0]
    p3 = pd.read_csv(P3).iloc[0]
    row = {
        "ProtocolID": PROTOCOL_ID,
        "Status": STATUS,
        "ParentActionPSDDeltaNLL": float(base["ParentActionPSDDeltaNLL"]),
        "InitialSignedPrimaryS": float(base["SignedPrimaryS"]),
        "InitialSignedRequiredNullMaxS": float(base["SignedRequiredNullMaxS"]),
        "DiagonalOrthogonalPrimaryS": float(diag["PrimarySignedS"]),
        "DiagonalOrthogonalBeatsNullMax": bool(diag["PrimaryBeatsNullMax"]),
        "DiagonalOrthogonalClockGatePassed": bool(diag["ClockGatePassed"]),
        "DiagonalOrthogonalFamilyGatePassed": bool(diag["FamilyBalanceGatePassed"]),
        "P3BalancedPrimaryS": float(p3["PrimarySignedS"]),
        "P3BalancedFamilyS": float(p3["FamilySignedS"]),
        "P3BalancedClockS": float(p3["ClockSignedS"]),
        "P3BalancedStrongestNullID": p3["StrongestNullID"],
        "BestClaim": "protocol_success_negative_empirical_result",
        "SurvivalClaimAuthorized": False,
        "TauCoreValidationClaimAuthorized": False,
        "MeasurementValidationAuthorized": False,
    }
    pd.DataFrame([row]).to_csv(OUT_CSV, index=False)
    OUT_MD.write_text(
        f"""# P-TauCov Program Status After P3 Balanced Scorecard

Status:

`{STATUS}`

## Executed Route Ladder

The P-TauCov program has now executed a stricter route ladder:

| Route | Primary result | Status |
|---|---:|---|
| Parent-action PSD covariance | `{float(base["ParentActionPSDDeltaNLL"])}` | fail |
| Initial signed response | `{float(base["SignedPrimaryS"])}` | fail versus required null / family dominated |
| Diagonal-orthogonal signed response | `{float(diag["PrimarySignedS"])}` | beats null max, but fails clock/family gates |
| P3 balanced signed response | `{float(p3["PrimarySignedS"])}` | negative primary alignment |

## Scientific Interpretation

This is a strong negative-control result.

The earlier local positive anomaly did not survive the stricter path:

1. diagonal leakage was removed;
2. family/clock balance was imposed;
3. structural nulls were audited;
4. a frozen P3 balanced scorecard was authorized and run.

The result was negative:

```text
P3BalancedPrimaryS = {float(p3["PrimarySignedS"])}
P3BalancedFamilyS = {float(p3["FamilySignedS"])}
P3BalancedClockS = {float(p3["ClockSignedS"])}
StrongestNullID = {p3["StrongestNullID"]}
```

## Claim Boundary

Allowed statement:

> The current P-TauCov implementation is reproducible and methodologically disciplined, but the tested parent-action, signed, diagonal-orthogonal, and P3 balanced candidates do not provide a surviving Tau-specific empirical signal.

Forbidden statement:

> P-TauCov validates Tau Core, establishes a physical covariance response, or provides a survival claim.

## Next Admissible Direction

The next route should not be a v4 support tweak.

Any future Tau-specific attempt needs a genuinely new parent-derived response structure, for example:

- a different parent Hessian channel;
- an independently motivated external observable family;
- a new source of phase/orientation structure not derived from the failed scorecards;
- or a decision to close P-TauCov as negative for this dataset and move to a different empirical domain.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
