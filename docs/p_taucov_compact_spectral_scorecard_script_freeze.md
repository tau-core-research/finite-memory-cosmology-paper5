# P-TauCov Compact Spectral Scorecard Script Freeze

Status: `P_TAUCOV_COMPACT_SPECTRAL_SCORECARD_SCRIPT_FROZEN_NO_SCORING`.

- script: `scripts/run_p_taucov_compact_spectral_scorecard.py`
- SHA256: `9b00acef0b144c00191a8a512d3bbee6ccd17211e27bddde90d60700e665bc98`
- mode: `blocked_until_compact_spectral_final_manifest`

This freezes the compact spectral scorecard entrypoint before scoring
authorization. The script remains blocked unless a final authorization manifest
exists and explicitly authorizes the compact spectral primary covariance
scorecard scope.
