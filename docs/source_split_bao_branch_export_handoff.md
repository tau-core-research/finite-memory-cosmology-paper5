# Source-Split BAO Branch Export Handoff

Status: BAO branch handoff added; candidate export still absent.

This handoff maps the DESI DR2 BAO residual branch onto the frozen
reconstruction-family export schema without writing the real candidate file.

## Run

```text
python3 scripts/build_source_split_bao_branch_export_handoff.py
```

It writes:

```text
evidence/source_split_bao_branch_export_handoff.csv
evidence/source_split_bao_branch_export_handoff_summary.csv
```

## Important Scale Boundary

The BAO preflight contains log-distance residuals and diagonal uncertainty
proxies. The source-split candidate export expects the common source-split
standardized response scale.

For this handoff:

```text
ResponseValue = BAOStandardizedResidual
ResponseSigma = 1.0
```

This is a schema handoff, not a measurement result and not a K2 input.

## Next Action

Append these BAO rows to the future candidate export together with the SN branch:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

Then run the validation and authorization chain.
