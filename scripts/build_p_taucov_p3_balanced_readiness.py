#!/usr/bin/env python3
"""Build readiness packet for the P3 balanced preflight object."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "evidence/p_taucov_p3_balanced_preflight_summary.csv"
PREFLIGHT_VALIDATION = ROOT / "evidence/p_taucov_p3_balanced_preflight_validation.csv"
BALANCE_PROJECTOR = ROOT / "evidence/p_taucov_clock_family_balance_projector_summary.csv"
BALANCE_PROJECTOR_VALIDATION = ROOT / "evidence/p_taucov_clock_family_balance_projector_validation.csv"
NEXT_GATE = ROOT / "evidence/p_taucov_clock_family_balanced_next_gate_validation.csv"
OUT = ROOT / "evidence/p_taucov_p3_balanced_readiness.csv"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_readiness_summary.csv"
DOC = ROOT / "docs/p_taucov_p3_balanced_readiness.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
READINESS_ID = "P_TAUCOV_P3_BALANCED_READINESS_v1"
STATUS_READY = "P_TAUCOV_P3_BALANCED_READY_FOR_MANIFEST_NO_SCORING"
STATUS_BLOCKED = "P_TAUCOV_P3_BALANCED_READINESS_BLOCKED_NO_SCORING"
CLAIM_BOUNDARY = "p3_balanced_readiness_no_scoring"


def first_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return str(pd.read_csv(path).iloc[0]["Status"])


def validation_all_pass(path: Path) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    return bool(df[df["Required"].astype(bool)]["Passed"].astype(bool).all())


def main() -> int:
    preflight = pd.read_csv(PREFLIGHT).iloc[0].to_dict() if PREFLIGHT.exists() else {}
    checks = [
        {
            "CheckID": "READY-01_BALANCE_PROJECTOR_VALID",
            "Expected": "all required balance-projector checks pass",
            "Observed": "PASS" if validation_all_pass(BALANCE_PROJECTOR_VALIDATION) else "FAIL",
            "Passed": validation_all_pass(BALANCE_PROJECTOR_VALIDATION),
        },
        {
            "CheckID": "READY-02_NEXT_GATE_VALID",
            "Expected": "all required next-gate checks pass",
            "Observed": "PASS" if validation_all_pass(NEXT_GATE) else "FAIL",
            "Passed": validation_all_pass(NEXT_GATE),
        },
        {
            "CheckID": "READY-03_PREFLIGHT_VALID",
            "Expected": "all required P3 balanced preflight checks pass",
            "Observed": "PASS" if validation_all_pass(PREFLIGHT_VALIDATION) else "FAIL",
            "Passed": validation_all_pass(PREFLIGHT_VALIDATION),
        },
        {
            "CheckID": "READY-04_RETENTION_NONZERO",
            "Expected": "BalanceRetention > 0",
            "Observed": str(preflight.get("BalanceRetention", "MISSING")),
            "Passed": bool(float(preflight.get("BalanceRetention", 0.0)) > 0.0),
        },
        {
            "CheckID": "READY-05_OFFDIAGONAL_DOMINANT",
            "Expected": "OffDiagonalShareBeforeOffdiagRemoval >= 0.5",
            "Observed": str(preflight.get("OffDiagonalShareBeforeOffdiagRemoval", "MISSING")),
            "Passed": bool(float(preflight.get("OffDiagonalShareBeforeOffdiagRemoval", 0.0)) >= 0.5),
        },
        {
            "CheckID": "READY-06_BALANCE_LEAKAGE_SMALL",
            "Expected": "balance leakage < 1e-10",
            "Observed": f"{preflight.get('BalanceProjectorLeftLeakageFrobenius', 'MISSING')};{preflight.get('BalanceProjectorSandwichLeakageFrobenius', 'MISSING')}",
            "Passed": bool(
                float(preflight.get("BalanceProjectorLeftLeakageFrobenius", 1.0)) < 1e-10
                and float(preflight.get("BalanceProjectorSandwichLeakageFrobenius", 1.0)) < 1e-10
            ),
        },
        {
            "CheckID": "READY-07_NO_SCORING_AUTHORIZED",
            "Expected": "preflight object is not a candidate and does not authorize scoring",
            "Observed": f"CandidateConstructed={preflight.get('CandidateConstructed', 'MISSING')};ScoringAuthorized={preflight.get('ScoringAuthorized', 'MISSING')}",
            "Passed": bool(
                preflight.get("CandidateConstructed", True) is False
                and preflight.get("ScoringAuthorized", True) is False
            ),
        },
        {
            "CheckID": "READY-08_NO_TARGET_OR_SCORE_USE",
            "Expected": "no target residuals or score outcome used",
            "Observed": f"UsesTargetResiduals={preflight.get('UsesTargetResiduals', 'MISSING')};UsesScoreOutcome={preflight.get('UsesScoreOutcome', 'MISSING')}",
            "Passed": bool(
                preflight.get("UsesTargetResiduals", True) is False
                and preflight.get("UsesScoreOutcome", True) is False
            ),
        },
    ]

    rows = [
        {
            "ProtocolID": PROTOCOL_ID,
            "ReadinessID": READINESS_ID,
            "ClaimBoundary": CLAIM_BOUNDARY,
            **check,
        }
        for check in checks
    ]
    table = pd.DataFrame(rows)
    table.to_csv(OUT, index=False)
    ready = bool(table["Passed"].all())
    status = STATUS_READY if ready else STATUS_BLOCKED
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "ReadinessID": READINESS_ID,
                "Status": status,
                "ChecksPassed": int(table["Passed"].sum()),
                "ChecksTotal": int(len(table)),
                "BalanceProjectorStatus": first_status(BALANCE_PROJECTOR),
                "P3BalancedPreflightStatus": first_status(PREFLIGHT),
                "BalanceRetention": preflight.get("BalanceRetention", ""),
                "BalancedRank": preflight.get("BalancedRank", ""),
                "OffDiagonalShareBeforeOffdiagRemoval": preflight.get("OffDiagonalShareBeforeOffdiagRemoval", ""),
                "CandidateConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        f"""# P-TauCov P3 Balanced Readiness

Readiness ID: `{READINESS_ID}`

Status:

`{status}`

## Result

The P3 balanced preflight object is checked against the frozen clock/family balance gate.

```text
ChecksPassed = {int(table["Passed"].sum())}/{int(len(table))}
BalanceRetention = {preflight.get("BalanceRetention", "")}
BalancedRank = {preflight.get("BalancedRank", "")}
OffDiagonalShareBeforeOffdiagRemoval = {preflight.get("OffDiagonalShareBeforeOffdiagRemoval", "")}
```

## Interpretation

This readiness packet means only that the target-blind P3 parent-side object
survives the pre-score balance filter well enough to be considered for a later
manifest.

It still does not authorize scoring.

## Claim Boundary

Allowed statement:

> The balanced P3 preflight object is ready for a later no-score final manifest.

Forbidden statement:

> The balanced P3 object has produced a Tau signal, passed empirical scoring, or
> validated Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
