#!/usr/bin/env python3
"""Freeze held-out fold design for Backreaction-36."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SOURCE = DATA / "physical_nulls/backreaction_reproduction/registered_protocol_guided_reproduction_backreaction_vector.csv"
OUT = EVIDENCE / "backreaction_36_fold_design.csv"
SUMMARY = EVIDENCE / "backreaction_36_fold_design_summary.csv"
DOC = DOCS / "backreaction_36_fold_design.md"

PROTOCOL_ID = "P5B_BACKREACTION_36_FROZEN_MORPHOLOGY_PROTOCOL_v1"
CLAIM_BOUNDARY = "backreaction_36_fold_design_no_random_primary_oos"


def clock_block(index: int) -> str:
    if index < 4:
        return "clock_block_0"
    if index < 8:
        return "clock_block_1"
    return "clock_block_2"


def main() -> int:
    rows = pd.read_csv(SOURCE).sort_values(["FamilyID", "z"]).reset_index(drop=True)
    rows["ClockIndex"] = rows.groupby("FamilyID").cumcount()
    rows["ClockBlock"] = rows["ClockIndex"].map(clock_block)
    folds = []

    for family in sorted(rows["FamilyID"].unique()):
        test = rows["FamilyID"].eq(family)
        folds.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FoldID": f"lofo_{family}",
                "FoldClass": "primary_leave_one_family_out",
                "TrainRows": int((~test).sum()),
                "TestRows": int(test.sum()),
                "TestFamilies": family,
                "TestClockBlocks": "all",
                "PrimaryOOS": True,
                "RandomRowShuffle": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    for block in ["clock_block_0", "clock_block_1", "clock_block_2"]:
        test = rows["ClockBlock"].eq(block)
        folds.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FoldID": f"holdout_{block}",
                "FoldClass": "primary_contiguous_clock_block",
                "TrainRows": int((~test).sum()),
                "TestRows": int(test.sum()),
                "TestFamilies": "all",
                "TestClockBlocks": block,
                "PrimaryOOS": True,
                "RandomRowShuffle": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    for parity, label in [(0, "even"), (1, "odd")]:
        test = rows["ClockIndex"].mod(2).eq(parity)
        folds.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FoldID": f"holdout_clock_{label}",
                "FoldClass": "secondary_interleaved_clock_holdout",
                "TrainRows": int((~test).sum()),
                "TestRows": int(test.sum()),
                "TestFamilies": "all",
                "TestClockBlocks": f"clock_index_{label}",
                "PrimaryOOS": False,
                "RandomRowShuffle": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    for family in sorted(rows["FamilyID"].unique()):
        for block in ["clock_block_0", "clock_block_1", "clock_block_2"]:
            test = rows["FamilyID"].eq(family) & rows["ClockBlock"].eq(block)
            folds.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FoldID": f"holdout_{family}_{block}",
                    "FoldClass": "secondary_family_x_clock_block",
                    "TrainRows": int((~test).sum()),
                    "TestRows": int(test.sum()),
                    "TestFamilies": family,
                    "TestClockBlocks": block,
                    "PrimaryOOS": False,
                    "RandomRowShuffle": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )

    fold_df = pd.DataFrame(folds)
    fold_df.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "Rows": len(rows),
                "Families": int(rows["FamilyID"].nunique()),
                "ClockPositions": int(rows["z"].nunique()),
                "Folds": len(fold_df),
                "PrimaryFolds": int(fold_df["PrimaryOOS"].sum()),
                "RandomRowShufflePrimaryForbidden": True,
                "CurrentStatus": "HELD_OUT_FOLD_DESIGN_FROZEN",
                "ScoringAuthorizedByThisArtifact": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# Backreaction-36 Held-Out Fold Design",
                "",
                "Status: frozen fold design; random row-level shuffle is forbidden as primary OOS.",
                "",
                "Primary OOS folds:",
                "",
                "- leave-one-family-out: 3 folds;",
                "- contiguous clock-block holdout: 3 folds.",
                "",
                "Secondary folds:",
                "",
                "- interleaved clock holdout: 2 folds;",
                "- family x clock blocked holdout: 9 folds.",
                "",
                "Scoring remains locked until the full freeze checklist is complete.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for path in [OUT, SUMMARY, DOC]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("HELD_OUT_FOLD_DESIGN_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
