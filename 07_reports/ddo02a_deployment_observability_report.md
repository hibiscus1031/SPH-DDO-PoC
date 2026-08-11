# Deployment observability audit

Every existing `obs__` field was classified exactly once. DESIGN_ONLY fields are: obs__jitter_fraction, obs__kh_max, obs__kh_rms, obs__mode_count. Reference-free does not imply deployment-observable; these fields are prohibited from future formal inputs.
