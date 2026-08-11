# DDO-01B-R field-level firewall audit

## Result

`REFERENCE_IN_MODEL_INPUT = false`

The 15,360 particle records are physically divided into three files keyed only
by `case_id, particle_id`:

- metadata: positions and registry/configuration metadata;
- observables: low-cost sampled state and SPH operator outputs; and
- reference targets: analytical continuum values and continuum-minus-SPH
  defects.

Every low-cost field is prefixed `obs__`. Every analytical/reference/defect
field is prefixed `target_ref__` and resides only in the reference-target file.
The observable header contains no `target`, `ref`, or `analytic` field. No
reference-minus-low-cost quantity, analytical field, target-derived feature,
target-derived normalization, or case label encoding an analytical answer
appears in the observable schema.

No model, representation, regression, neural architecture, or optimizer was
constructed. The join keys are identifiers, not model inputs, and no target-
derived normalization metadata was created.
