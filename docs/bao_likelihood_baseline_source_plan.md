# BAO Likelihood-Native Baseline Source Plan

Status: Phase II source-readiness plan.

The DESI DR2 BAO mean/covariance files from Cobaya are public data inputs. They
are not, by themselves, a likelihood-native baseline prediction. A fair T1
baseline export requires a public or reproducible source for the predicted BAO
observables on the same rows as the data vector.

## Registry

Machine-readable registry:

```text
evidence/bao_likelihood_baseline_source_registry.csv
```

Readiness output:

```text
evidence/bao_likelihood_baseline_source_readiness.csv
```

## Current Source Classes

- `COBAYA_DESI_DR2_DATA_ONLY`: available data/covariance only.
- `COBAYA_MODEL_EVALUATION_EXPORT`: planned reproducible model-evaluation path.
- `DESI_PUBLIC_BESTFIT_CHAIN_EXPORT`: available public best-fit path from the
  official DESI DR2 `iminuit/base/desi-bao-all` posterior maximization result.
- `PAPER_REPORTED_BESTFIT_TABLE`: possible fallback if table extraction and
  computation are frozen.
- `SAME_DATA_RD_OFFSET_ABSORBED`: sensitivity check only; never an eligible
  measurement baseline.

## Eligibility Rule

A source is eligible for BAO baseline export only if it has:

- public data vector;
- public covariance;
- baseline prediction;
- frozen cosmology or public chain selection rule;
- reproducible evaluator;
- no same-data scale absorption.

The current result is that a public best-fit baseline export is available for
preflight, but no source is eligible for K2 measurement-gate scoring. This is a
useful negative gate: it prevents a data-only product, same-data `rd` offset, or
same-data posterior maximum from being treated as an independent locked
prediction test.

The DESI best-fit baseline export is:

```text
scripts/build_desi_bestfit_bao_baseline.py
evidence/desi_bestfit_bao_baseline_export.csv
evidence/desi_bestfit_bao_baseline_summary.csv
```

The recomputed BAO chi2 from the exported flat-LCDM baseline is close to the
reported DESI `chi2__BAO`, which validates the evaluator plumbing. It does not
open the measurement gate because the best fit is optimized on the same BAO
product.

A CMB-only best-fit baseline export has also been built from the official DESI
VAC `base` CMB-only posterior maximization result. This source is more
independent of the DESI BAO data vector, but its predicted BAO chi2 is higher
than the same-data DESI BAO best fit. The comparison is summarized in:

```text
evidence/bao_baseline_scorecard.csv
```

This scorecard is a baseline-selection aid, not a K2 result.

## Next Step

Choose one of two routes:

1. Ingest a public DESI best-fit or chain product and define a frozen selection
   rule for the baseline prediction.
2. Configure a reproducible Cobaya/CAMB/CLASS model evaluation with frozen
   cosmological parameters and export the predicted BAO observables.

Only after one of these routes is complete should T1 be reconsidered for
measurement-gate scoring.
