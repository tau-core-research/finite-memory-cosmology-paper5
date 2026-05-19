# Source-Split Likelihood-Native Scorecard Dominance

Status: dominance and amplitude-gap diagnosis complete.

The likelihood-native preflight null-scorecard is now diagnosable row by row:

```text
evidence/source_split_likelihood_native_scorecard_dominance_audit.csv
evidence/source_split_likelihood_native_scorecard_dominance_summary.csv
evidence/source_split_likelihood_native_amplitude_gap_audit.csv
evidence/source_split_likelihood_native_amplitude_gap_summary.csv
```

## Main Result

The locked K2 response improves over K1/no-memory on the promoted preflight
vector, but it does not beat flexible polynomial controls.

```text
K1_NO_MEMORY Chi2: 139789.55908762495
K2_LOCKED_RHO4 Chi2: 136480.74383394732
POLY_DEG2 Chi2: 2661.832384218718
```

## Mechanism

The main driver is an amplitude gap, especially at low depth.

```text
RowsTargetGt5xK2: 4
MeanAbsTarget: 2.2234938839612974
MeanAbsK1: 0.17046820413894592
MeanAbsK2Rho4: 0.4831648049861127
LowDepthRows: 2
LowDepthMeanAbsTarget: 4.572063629864912
LowDepthMeanAbsK2Rho4: 0.27297731740775516
```

At the first two source-split rows, the target response is much larger than the
locked K2 prediction. K2 moves in the right broad direction relative to K1, but
the fixed multiplicative response is too small on the current response scale.

## Interpretation

This is a weakening preflight result, not a final rejection. It says that the
current likelihood-native target scale and covariance proxy do not yet make the
locked K2 response competitive against flexible controls.

The next technical question is whether the amplitude gap is caused by:

- an inappropriate source-split target scale;
- a too-small externally derived K1 amplitude;
- the diagonal/shrinkage covariance proxy;
- or a genuine limitation of the locked cubic finite-memory operator.

The K1 amplitude must not be rescaled post hoc to fix this. Any amplitude
normalization must be independently declared before a new scorecard.

A bounded-rho follow-up shows that the amplitude gap is not recoverable inside
the locked passive bound. The best scan point is `rho=4`, but all eight rows
would require `rho>4` for exact amplitude matching. This strengthens the
conclusion that the next issue is target scale, covariance, or independent
normalization, not a rho rescue.
