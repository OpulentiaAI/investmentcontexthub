# decisions/

One JSON record per JEV decision, in `schemas/jev-decision.schema.json` shape.

- `2026-09-18-live-runs.json` — the seven live calls used to verify the layer before writing it into
the packages, including the two abstentions, the rejected negative control, and the one call whose
output was lost.

Naming: `<date>-<slug>.json`. A decision is not "made" until it is a record here, because
calibration needs the probability that was stated *before* the outcome.
