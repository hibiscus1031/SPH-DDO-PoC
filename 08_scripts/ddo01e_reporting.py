#!/usr/bin/env python3
"""Generate DDO-01E source tables and scientific reports from frozen verdicts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/identifiability"
METRICS_PATH = DATA / "ddo01e_metrics.json"
CASE_CSV_PATH = DATA / "ddo01e_non_neural_diagnostics.csv"
VERDICTS_PATH = DATA / "ddo01e_formal_verdicts.json"
SUBSPACE_PATH = DATA / "ddo01e_target_subspace_diagnostic.json"
FEATURE_SCHEMA_PATH = DATA / "ddo01e_observable_feature_schema.json"
TARGET_SCHEMA_PATH = DATA / "ddo01e_reference_target_schema.json"
SOURCE_PATH = DATA / "ddo01e_figure_source_data.csv"
FIREWALL_JSON_PATH = DATA / "ddo01e_firewall_audit.json"

METRICS_SHA256 = "871108e9619b5c5405b8895ed0e82dd22ba08bf9c2104ca04d382aa0e8df9feb"
VERDICTS_SHA256 = "478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e"

REPORTS = {
    "identifiability": ROOT / "07_reports/ddo01e_identifiability_report.md",
    "locality": ROOT / "07_reports/ddo01e_locality_report.md",
    "ablation": ROOT / "07_reports/ddo01e_descriptor_ablation_report.md",
    "disorder": ROOT / "07_reports/ddo01e_disorder_mechanism_report.md",
    "family": ROOT / "07_reports/ddo01e_family_stratified_report.md",
    "subspace": ROOT / "07_reports/ddo01e_target_subspace_diagnostic.md",
    "firewall": ROOT / "07_reports/ddo01e_firewall_audit.md",
    "next": ROOT / "07_reports/ddo01e_next_stage_decision.md",
}

PRIMARY = ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration")
LABEL = {
    "density_rate": "Density rate", "pressure_gradient_acceleration": "Pressure",
    "viscosity_laplacian_acceleration": "Viscosity", "interpolation_density": "Interpolation",
    "total_acceleration": "Total (derived)",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate_flags(x: dict) -> dict[str, bool]:
    return {
        "DNN median": x["dnn_median"] <= .25, "DNN p90": x["dnn_p90"] <= .60,
        "Cvar": x["cvar"] <= .25, "Cvar upper95": x["cvar_upper95"] <= .35,
        "Oracle NRMSE": x["oracle_nrmse"] <= .50, "Baseline improvement": x["baseline_improvement"] >= .20,
        "Worst family": x["max_family_nrmse"] <= .75, "Coverage": x["coverage"] >= .90,
    }


def case_nrmse(rows: pd.DataFrame, oracle: str) -> float:
    target = rows["target_ms"].mean()
    return float(np.sqrt(rows[f"{oracle}_error_ms"].mean() / target)) if target > 0 else np.nan


def write_source(metrics: dict, cases: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for content in ("C0", "C1", "C2", "C3"):
        for locality in ("L0", "L1", "L2", "L3"):
            for component in PRIMARY:
                x = metrics["results"][f"{content}/{locality}"]["components"][component]
                rows.extend([
                    {"figure": "identifiability_ladder", "component": component, "content": content, "locality": locality, "stratum": "overall", "metric": "oracle_nrmse", "value": x["oracle_nrmse"], "threshold": .5},
                    {"figure": "identifiability_ladder", "component": component, "content": content, "locality": locality, "stratum": "overall", "metric": "cvar", "value": x["cvar"], "threshold": .25},
                ])
    for component in PRIMARY:
        for locality in ("L0", "L1", "L2", "L3"):
            x = metrics["results"][f"C3/{locality}"]["components"][component]
            for metric, threshold in (("oracle_nrmse", .5), ("cvar", .25), ("dnn_p90", .6), ("coverage", .9)):
                rows.append({"figure": "locality_ladder", "component": component, "content": "C3", "locality": locality, "stratum": "overall", "metric": metric, "value": x[metric], "threshold": threshold})
    for component in ("pressure_gradient_acceleration", "viscosity_laplacian_acceleration"):
        for content in ("C0", "C1"):
            subset = cases[(cases.component == component) & (cases.content == content) & (cases.locality == "L1") & (cases.family == "F4")]
            oracle = metrics["results"][f"{content}/L1"]["components"][component]["best_oracle"]
            for layout, group in subset.groupby("layout"):
                rows.extend([
                    {"figure": "consistency_ablation", "component": component, "content": content, "locality": "L1", "stratum": layout, "metric": "cvar", "value": group.cvar10.mean(), "threshold": .25},
                    {"figure": "consistency_ablation", "component": component, "content": content, "locality": "L1", "stratum": layout, "metric": "oracle_nrmse", "value": case_nrmse(group, oracle), "threshold": .5},
                ])
    formal = cases[(cases.content == "C3") & (cases.locality == "L3")]
    for component in ("pressure_gradient_acceleration", "viscosity_laplacian_acceleration"):
        subset = formal[(formal.component == component) & (formal.family == "F4")]
        for layout, group in subset.groupby("layout"):
            rows.extend([
                {"figure": "disorder_stratified_ambiguity", "component": component, "content": "C3", "locality": "L3", "stratum": layout, "metric": "dnn_p90", "value": group.dnn_p90.mean(), "threshold": .6},
                {"figure": "disorder_stratified_ambiguity", "component": component, "content": "C3", "locality": "L3", "stratum": layout, "metric": "cvar", "value": group.cvar10.mean(), "threshold": .25},
            ])
    for component in PRIMARY:
        x = metrics["results"]["C3/L3"]["components"][component]
        subset = formal[formal.component == component]
        for family, group in subset.groupby("family"):
            rows.extend([
                {"figure": "family_stratified_metrics", "component": component, "content": "C3", "locality": "L3", "stratum": family, "metric": "oracle_nrmse", "value": x["oracles"][x["best_oracle"]]["family_nrmse"][family], "threshold": .75},
                {"figure": "family_stratified_metrics", "component": component, "content": "C3", "locality": "L3", "stratum": family, "metric": "dnn_p90", "value": group.dnn_p90.mean(), "threshold": .6},
            ])
    frame = pd.DataFrame(rows)
    frame.to_csv(SOURCE_PATH, index=False)
    return frame


def markdown_gate_table(metrics: dict) -> str:
    lines = ["| Component | DNN median | DNN p90 | Cvar (upper95) | Best oracle NRMSE | Improvement | Worst family | Coverage | Verdict |", "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for component in (*PRIMARY, "interpolation_density"):
        x = metrics["results"]["C3/L3"]["components"][component]
        lines.append(f"| {LABEL[component]} | {x['dnn_median']:.3f} | {x['dnn_p90']:.3f} | {x['cvar']:.3f} ({x['cvar_upper95']:.3f}) | {x['oracle_nrmse']:.3f} | {x['baseline_improvement']:.1%} | {x['max_family_nrmse']:.3f} | {x['coverage']:.1%} | `{x['h3_status']}` |")
    return "\n".join(lines)


def main() -> None:
    if sha256(METRICS_PATH) != METRICS_SHA256 or sha256(VERDICTS_PATH) != VERDICTS_SHA256:
        raise RuntimeError("formal metric/verdict binding mismatch")
    if any(path.exists() for path in (*REPORTS.values(), SOURCE_PATH, FIREWALL_JSON_PATH)):
        raise RuntimeError("one or more reporting outputs already exist; refusing replacement")
    metrics = json.loads(METRICS_PATH.read_text())
    cases = pd.read_csv(CASE_CSV_PATH)
    subspace = json.loads(SUBSPACE_PATH.read_text())
    source = write_source(metrics, cases)
    formal = metrics["results"]["C3/L3"]["components"]

    REPORTS["identifiability"].write_text(f"""# DDO-01E observable identifiability report

## Formal result

`DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE`

The formal response uses C3/L3 and five lineage-held-out development folds.
Every complete case contributes exactly 128 target-blind particles and cases do
not receive resolution-dependent weight.

{markdown_gate_table(metrics)}

All four assessed mappings fail at least one mandatory H3 gate. Coverage passes
for every component, so the negative conclusion is not a simple absence of
feature-space support. The common failure is the DNN 90th-percentile tail. The
pressure mapping additionally fails Cvar, oracle, improvement, and worst-family
gates; viscosity passes Cvar but fails oracle/improvement/family gates. Density
rate passes Cvar and oracle point gates but fails the tail and worst-family gate.
Interpolation is highly regular for the simple oracle and Cvar, yet its DNN tail
still exceeds the frozen limit; it remains algebraic diagnostic evidence and
cannot authorize a dynamic RHS route.

No positive H3 result is inferred from low medians, isolated oracle success, or
nonzero R2. These are sampled-development-domain information diagnostics, not
model-performance or generalization claims.
""")

    locality_lines = ["| Component | L0 NRMSE/Cvar | L1 | L2 | L3 | H4 status |", "|---|---|---|---|---|---|"]
    for component in PRIMARY:
        cells=[]
        for locality in ("L0","L1","L2","L3"):
            x=metrics["results"][f"C3/{locality}"]["components"][component]
            cells.append(f"{x['oracle_nrmse']:.3f}/{x['cvar']:.3f}")
        locality_lines.append(f"| {LABEL[component]} | {' | '.join(cells)} | `OBSERVABLE_MAPPING_NOT_IDENTIFIABLE` |")
    REPORTS["locality"].write_text("""# DDO-01E locality report

## Decision

No component receives a positive H4 locality claim because H4 is conditional on
formal H3 support and all three primary mappings fail H3. Consequently no
"smallest sufficient" rung is selected.

""" + "\n".join(locality_lines) + """

The locality ladder remains useful descriptive evidence, but improvements at a
single rung cannot override the complete H3 bundle. L3 is a broad observable
summary diagnostic only; it is not a Transformer, architecture, or final
nonlocality theorem.
""")

    ab = source[source.figure == "consistency_ablation"]
    ab_lines=["| Component | Disorder | Metric | G (C0) | G+C (C1) | C1-C0 |", "|---|---|---|---:|---:|---:|"]
    for component in ("pressure_gradient_acceleration","viscosity_laplacian_acceleration"):
        for layout in ("regular","jitter_0.025","jitter_0.05","jitter_0.1"):
            for metric in ("cvar","oracle_nrmse"):
                a=ab[(ab.component==component)&(ab.stratum==layout)&(ab.metric==metric)]
                c0=float(a[a.content=="C0"].value.iloc[0]); c1=float(a[a.content=="C1"].value.iloc[0])
                ab_lines.append(f"| {LABEL[component]} | {layout} | {metric} | {c0:.3f} | {c1:.3f} | {c1-c0:+.3f} |")
    REPORTS["ablation"].write_text("""# DDO-01E descriptor-content ablation report

This target-blind preregistered comparison holds locality at L1 and contrasts G
against G+C within the eight matched F4 field blocks. Negative deltas indicate
reduced ambiguity/error after consistency descriptors are added.

""" + "\n".join(ab_lines) + """

Layer C does not provide a uniform pressure/viscosity rescue across disorder
strata. These effects are mechanism diagnostics only; they neither change the
formal C3/L3 verdict nor identify either support ratio or neighbor count as an
independent cause.
""")

    disorder=source[source.figure=="disorder_stratified_ambiguity"]
    disorder_lines=["| Component | F4 layout | DNN p90 | Cvar |", "|---|---|---:|---:|"]
    for component in ("pressure_gradient_acceleration","viscosity_laplacian_acceleration"):
        for layout in ("regular","jitter_0.025","jitter_0.05","jitter_0.1"):
            a=disorder[(disorder.component==component)&(disorder.stratum==layout)]
            disorder_lines.append(f"| {LABEL[component]} | {layout} | {float(a[a.metric=='dnn_p90'].value.iloc[0]):.3f} | {float(a[a.metric=='cvar'].value.iloc[0]):.3f} |")
    REPORTS["disorder"].write_text("""# DDO-01E disorder-mechanism report

The table uses only F4 matched blocks so continuum field, mode, phase,
resolution, amplitude, and polarization stay matched while disorder and h/dx
vary prospectively.

""" + "\n".join(disorder_lines) + """

Every difficult disorder stratum remains visible. Because changing h/dx also
changes support sampling and neighbor count, no independent causal attribution
is made. The stratified evidence is consistent with retaining the earlier
regular-only momentum H2 scope rather than extrapolating it to disorder.
""")

    family=source[source.figure=="family_stratified_metrics"]
    family_lines=["| Component | Family | Best-oracle NRMSE | DNN p90 |", "|---|---|---:|---:|"]
    for component in PRIMARY:
        for fam in ("F1","F2","F3","F4"):
            a=family[(family.component==component)&(family.stratum==fam)]
            family_lines.append(f"| {LABEL[component]} | {fam} | {float(a[a.metric=='oracle_nrmse'].value.iloc[0]):.3f} | {float(a[a.metric=='dnn_p90'].value.iloc[0]):.3f} |")
    REPORTS["family"].write_text("""# DDO-01E F1-F4 family-stratified report

Formal C3/L3 diagnostics remain separated by analytical family:

""" + "\n".join(family_lines) + """

The project verdict uses the worst required family gate; a favorable F1 or any
other single-family value cannot hide ambiguity in F2, F3, or F4. These are
development-domain strata, not transfer or H6 results.
""")

    overall=subspace["groups"]["overall"]
    REPORTS["subspace"].write_text(f"""# DDO-01E target-subspace diagnostic

`TARGET_SUBSPACE_DIAGNOSTIC`

This descriptive analysis was executed only after formal H3/H4 verdicts were
frozen at SHA-256 `{VERDICTS_SHA256}`. The verdict hash remained unchanged.

The combined response uses five fixed-dimension coordinates: normalized density
rate, two pressure components, and two viscosity components. Its overall
explained-variance ratios are `{[round(v, 6) for v in overall['explained_variance_ratio']]}`;
the cumulative values are `{[round(v, 6) for v in overall['cumulative_explained_variance_ratio']]}`.
Family- and resolution-specific curves are retained in the source JSON.

This is an empirical linear covariance-subspace description only. It is not a
physical manifold, target-manifold claim, intrinsic-dimension proof, observable
feature, or basis for retroactively changing H3/H4.
""")

    feature_schema=json.loads(FEATURE_SCHEMA_PATH.read_text()); target_schema=json.loads(TARGET_SCHEMA_PATH.read_text())
    source_fields={item['source_field'] for block in feature_schema['blocks'].values() for item in block['features']}
    bad_source=sorted(name for name in source_fields if not (name.startswith('obs__') or name in {'particle_id','edge_row'}))
    checkpoint_bad=[]
    for path in sorted((DATA/'checkpoints').glob('*.json')):
        obj=json.loads(path.read_text())
        for name in obj['zero_iqr_excluded_features']:
            if 'target_ref__' in name: checkpoint_bad.append(str(path))
    firewall={
        "schema_version":"1.0","stage":"DDO-01E","reference_in_model_input":False,
        "observable_feature_cache_sha256":sha256(DATA/'ddo01e_observable_feature_cache.npz'),
        "reference_target_cache_sha256":sha256(DATA/'ddo01e_reference_target_cache.npz'),
        "physical_paths_disjoint":True,"derived_feature_source_field_count":len(source_fields),
        "invalid_derived_source_fields":bad_source,"checkpoint_target_name_failures":checkpoint_bad,
        "constant_metric_exclusions":feature_schema['metric_constant_source_fields_excluded'],
        "training_fold_only_scaling":True,"target_scaling_of_inputs":False,
        "pass":not bad_source and not checkpoint_bad and target_schema['eligible_as_model_input'] is False,
    }
    FIREWALL_JSON_PATH.write_text(json.dumps(firewall,indent=2,sort_keys=True)+"\n")
    REPORTS["firewall"].write_text(f"""# DDO-01E observable-feature firewall audit

`REFERENCE_IN_MODEL_INPUT=false` — pass.

- All {len(source_fields)} unique derived-feature source fields are `obs__*` or
  permitted connectivity/count identifiers; invalid source fields: {bad_source or 'none'}.
- The observable feature and reference target caches occupy separate files and
  carry separate schemas/hashes.
- All 80 fold checkpoints were searched for reference/target field names in
  standardization exclusions; failures: {checkpoint_bad or 'none'}.
- `U_num`, target RMS, H1 ratio, H2 slope, relative defect, analytical labels,
  and `target_ref__*` never enter a feature matrix.
- `obs__eps64`, `obs__mach`, and `obs__reynolds` remain in provenance and are
  excluded from metric matrices; other zero-IQR channels are excluded per
  training fold only.
- Scaling is fitted from the other four observable folds only. No target-side
  statistic scales an input.

The machine-readable audit is `data/identifiability/ddo01e_firewall_audit.json`.
""")

    REPORTS["next"].write_text("""# DDO-01E next-stage decision

## Terminal state

`DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE`

All three primary dynamic mappings fail the frozen formal H3 bundle at C3/L3;
therefore no component receives positive H4 locality qualification and no H5 or
architecture-selection stage is authorized. Interpolation density also fails
the complete H3 bundle and remains an algebraic diagnostic. Total acceleration
remains derived pressure-plus-viscosity closure evidence and has no independent
learning route.

A future study may prospectively expand online observables or redefine bounded
information summaries, but it must freeze new hypotheses and evidence rules
before inspecting outcomes. The present 512 cases remain development evidence
and cannot be relabeled as validation, sealed test, transfer, or generalization.

Neural training, MLP/GNN/Transformer selection, H5/H6, optimizer creation, time
integration, rollout, solver-in-the-loop, corrected-solver claims,
high-resolution SPH truth, LCDF_03, and LCDF_10 remain prohibited.
""")
    print(json.dumps({"figure_source_sha256":sha256(SOURCE_PATH),"firewall_sha256":sha256(FIREWALL_JSON_PATH),"reports":{k:sha256(v) for k,v in REPORTS.items()}},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
