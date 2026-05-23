#!/usr/bin/env python3
"""Build the next P-TauCov gate after diagonal-orthogonal failure."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "evidence/p_taucov_clock_family_balanced_next_gate.csv"
OUT_MD = ROOT / "docs/p_taucov_clock_family_balanced_next_gate.md"

AUDIT_ID = "P_TAUCOV_CLOCK_FAMILY_BALANCED_NEXT_GATE_v1"
STATUS = "P_TAUCOV_NEXT_GATE_DEFINED_NO_CANDIDATE_NO_SCORING"


ROWS = [
    {
        "GateID": "G1",
        "Requirement": "parent_derived_support",
        "Required": True,
        "Criterion": "support_or_weights_must_be_derived_from_delta_c_tau_or_parent_response_before_score_access",
        "Rationale": "prevents post-score construction from the failed diagonal-orthogonal result",
    },
    {
        "GateID": "G2",
        "Requirement": "clock_consistency",
        "Required": True,
        "Criterion": "candidate_must_declare_clock_block_response_expectation_before_scoring",
        "Rationale": "the last candidate failed because clock aggregate was negative",
    },
    {
        "GateID": "G3",
        "Requirement": "family_balance",
        "Required": True,
        "Criterion": "candidate_must_not_concentrate_positive_support_in_a_single_registered_family",
        "Rationale": "the last candidate was dominated by one family contribution",
    },
    {
        "GateID": "G4",
        "Requirement": "diagonal_orthogonality",
        "Required": True,
        "Criterion": "diagonal_energy_must_be_zero_or_explicitly_forbidden_from_the_alignment_statistic",
        "Rationale": "prevents trivial variance inflation or diagonal leakage",
    },
    {
        "GateID": "G5",
        "Requirement": "null_reuse_discipline",
        "Required": True,
        "Criterion": "same_null_classes_must_be_kept_or_predeclared_stronger_nulls_must_be_added_before_scoring",
        "Rationale": "prevents changing the comparator set after seeing a candidate",
    },
    {
        "GateID": "G6",
        "Requirement": "forbidden_failure_tuning",
        "Required": True,
        "Criterion": "the_previous_best_family_clock_cell_must_not_be_used_as_a_direct_template",
        "Rationale": "prevents converting the failure diagnostic into a target-derived kernel",
    },
    {
        "GateID": "G7",
        "Requirement": "claim_boundary",
        "Required": True,
        "Criterion": "no_survival_no_tau_validation_no_measurement_validation_until_frozen_scorecard_passes",
        "Rationale": "keeps the protocol as a validation gate rather than a narrative rescue",
    },
]


def main() -> int:
    df = pd.DataFrame(
        [
            {
                "AuditID": AUDIT_ID,
                "Status": STATUS,
                **row,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    md_rows = "\n".join(
        f"| `{row['GateID']}` | {row['Requirement']} | {row['Criterion']} |"
        for row in ROWS
    )
    md = f"""# P-TauCov Clock/Family-Balanced Next Gate

Audit ID: `{AUDIT_ID}`

Status:

`{STATUS}`

## Purpose

The diagonal-orthogonal scorecard produced a positive raw alignment, but failed through clock inconsistency and family dominance. This document defines the next admissibility gate before any new candidate is built or scored.

The goal is not to rescue the failed candidate. The goal is to prevent the next route from inheriting the same hidden failure mode.

## Required Gates

| Gate | Requirement | Criterion |
|---|---|---|
{md_rows}

## Forbidden Move

The strongest observed family-by-clock cell from the failed scorecard cannot be used as a direct template for a new kernel.

That would turn the failure diagnostic into target-derived tuning.

## Allowed Next Work

The next legitimate work is one of the following:

- derive a clock-consistent support rule from the parent response object;
- derive a family-balanced support rule from the parent response object;
- define a stronger pre-score structural audit that must pass before any scorecard is authorized;
- explicitly close this path as a localized anomaly if no parent-derived balanced support rule exists.

## Claim Boundary

This artifact does not authorize scoring.

It authorizes only a pre-score design requirement:

> the next P-TauCov candidate must be clock-consistent and family-balanced before it can be scored.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
