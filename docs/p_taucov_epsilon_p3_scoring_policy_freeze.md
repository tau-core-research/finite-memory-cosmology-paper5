# P-TauCov Epsilon-P3 Scoring Policy Freeze

Status: scoring policies frozen / scoring not authorized.

This artifact freezes the policy layer needed before any epsilon-P3 P-TauCov
score can be run:

- primary fold policy;
- required null controls;
- covariance and degrees-of-freedom policy;
- survival and kill gates.

It does not freeze the final scorecard script and therefore does not authorize
empirical scoring.

## Scoring Boundary

```text
PTauCovScoringAuthorized: false
Reason: scorecard script and final authorization manifest are not frozen
```

Allowed statement:

```text
The epsilon-P3 scoring policies are frozen for later authorization.
```

Forbidden statement:

```text
The epsilon-P3 candidate has been scored or has produced a Tau-specific
observational signal.
```
