#!/usr/bin/env python3
"""Build the required schema for public source-split reconstruction families."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.reconstruction_family import (
    reconstruction_family_export_schema,
    reconstruction_family_export_template,
)

EVIDENCE = ROOT / "evidence"
SCHEMA_OUT = EVIDENCE / "source_split_reconstruction_family_export_schema.csv"
TEMPLATE_OUT = EVIDENCE / "source_split_reconstruction_family_export_template.csv"


def main() -> None:
    reconstruction_family_export_schema().to_csv(SCHEMA_OUT, index=False)
    reconstruction_family_export_template().to_csv(TEMPLATE_OUT, index=False)
    print(f"Wrote {SCHEMA_OUT}")
    print(f"Wrote {TEMPLATE_OUT}")


if __name__ == "__main__":
    main()
