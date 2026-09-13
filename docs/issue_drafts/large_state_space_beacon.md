# Draft: abstract interpretation for large concrete state spaces

## Summary

Economoist's current canon proves small, fixed-dimensional instances with SMT.
Scaling verification to materially larger concrete state spaces requires the
Beacon bound-propagation and abstract-interpretation roadmap; the shell does not
reconstruct those guarantees from sampled execution.

## Re-probe trigger

Revisit when a published Beacon surface can consume these models and report
auditable bounds. Add executable characterization and negative controls before
claiming that larger state spaces are verified.

## 0.18.7 re-probe

`chelis prove properties/growth.ch --tier beacon-only --json` returned structured
unsupported records for the existing imported Gordon properties. The reason was
`Beacon bounds require distinct named rank-zero tensor[f64] parameters`.
The released NN route therefore does not establish this larger-state-space
capability. The pure economic models and their SMT scope remain unchanged.
Receipt: [Sonar's released surface probe](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-beacon-surface-reprobe).
