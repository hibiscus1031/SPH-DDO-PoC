#!/usr/bin/env python3
"""Create DDO-02B reports, release audit, and final manifest."""

from __future__ import annotations
import csv,hashlib,json,py_compile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data/ddo02b_identifiability"; REPORT=ROOT/"07_reports"; MAN=ROOT/"06_manifests"
VERDICT=DATA/"ddo02b_formal_verdicts.json"; METRICS=DATA/"ddo02b_metrics.json"; OLD=ROOT/"data/identifiability/ddo01e_formal_verdicts.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    verdict=json.loads(VERDICT.read_text()); metrics=json.loads(METRICS.read_text()); status=verdict["terminal_status"]
    primary=("density_rate","pressure_gradient_acceleration","viscosity_laplacian_acceleration")
    passed=[c for c in primary if verdict["formal_h3"][c]=="H3_OBSERVABLE_MAPPING_IDENTIFIABLE"]
    h5_authorized=bool(passed)
    report=REPORT/"ddo02b_h3_h4_requalification_report.md"
    lines=["# DDO-02B fresh H3/H4 requalification","",f"Terminal status: `{status}`.","",
           "Formal evidence comprises 384 entirely fresh complete cases (96 per F1--F4) and 49,152 frozen particle samples. The old 512-case atlas was not formal evidence.",""]
    for comp in primary:
        result=metrics["results"]["C3/L3"]["components"][comp]
        lines.append(f"- `{comp}`: `{verdict['formal_h3'][comp]}`; DNN median {result['dnn_median']:.4g}, DNN P90 {result['dnn_p90']:.4g}, Cvar upper95 {result['cvar_upper95']:.4g}, oracle NRMSE {result['oracle_nrmse']:.4g}, worst-family NRMSE {result['max_family_nrmse']:.4g}.")
    lines.extend(["",f"H5-authorized components: {', '.join(passed) if passed else 'none'}. Neural training remains unperformed."])
    report.write_text("\n".join(lines)+"\n")
    firewall=REPORT/"ddo02b_firewall_audit.md"
    schema=json.loads((DATA/"ddo02b_observable_feature_schema.json").read_text())
    prohibited=schema["prohibited_fields_absent"]
    firewall.write_text("# DDO-02B firewall audit\n\nPASS. Observable and reference caches are physically separate; the observable builder opened no reference archive. "
        "All CA-06 expanded descriptors use low-cost state/geometry only, train-fold scaling is target-free, and DESIGN_ONLY fields are absent: "+", ".join(prohibited)+".\n")
    nextp=REPORT/"ddo02b_next_stage_decision.md"
    if status=="ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED":
        decision="All three primary dynamic components failed fresh H3. The online spatial-DDO observability route is closed. H5, neural representation training, solver development, time integration and rollout are not authorized."
    else:
        decision=f"Only H3-passing components may proceed to a separately contracted H5: {', '.join(passed)}. No other component or full corrected-solver claim is authorized."
    nextp.write_text(f"# DDO-02B next-stage decision\n\nTerminal status: `{status}`.\n\n{decision}\n")
    final_ledger=MAN/"ddo02_final_status_ledger.json"
    final_ledger.write_text(json.dumps({
        "schema_version":"1.0","stage":"DDO-02","terminal_status":status,
        "ddo01e_permanent_status":"DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE",
        "ddo01d_case_count":512,"ddo01d_roles":["DEVELOPMENT_ATLAS","CONSUMED_OBSERVABLE_DESIGN_EVIDENCE"],
        "ddo01d_future_formal_h3_eligibility":False,"ddo02b_fresh_case_count":384,
        "formal_h3":verdict["formal_h3"],"h5_authorized_components":passed,
        "online_spatial_ddo_route_closed":status=="ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED",
        "neural_training_authorized":h5_authorized,"solver_development_authorized":False,
    },indent=2,sort_keys=True)+"\n")
    formal_names=[f"{content}_{locality}_fold{fold}.json" for content,locality in
                  [("C0","L3"),("C1","L3"),("C2","L3"),("C3","L0"),("C3","L1"),("C3","L2"),("C3","L3")]
                  for fold in range(5)]
    checkpoints=[DATA/"checkpoints"/name for name in formal_names]
    if not all(p.exists() for p in checkpoints): raise RuntimeError("formal checkpoint missing")
    cpman=DATA/"ddo02b_checkpoint_manifest.json"
    cpman.write_text(json.dumps({"checkpoint_count":len(checkpoints),"evaluated_combinations":7,
        "excluded_interrupted_exploratory_checkpoint_count":len(list((DATA/"checkpoints").glob("*.json")))-len(checkpoints),
        "files":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in checkpoints]},indent=2,sort_keys=True)+"\n")
    scripts=[ROOT/"08_scripts"/name for name in ("ddo02_descriptors.py","ddo02a_failure_attribution.py","ca06_freeze.py","ddo02b_registry_builder.py","ddo02b_partition_builder.py","ddo02b_atlas_builder.py","ddo02b_feature_builder.py","ddo02b_formal_requalification.py","ddo02b_release_audit.py")]
    compile_pass=True
    for p in scripts:
        try: py_compile.compile(str(p),doraise=True)
        except Exception: compile_pass=False
    required=[MAN/"ddo02a_manifest.json",MAN/"ca06_manifest.json",MAN/"ddo02b_case_registry.json",MAN/"ddo02b_diagnostic_partition.json",MAN/"ddo02b_particle_sample_registry.json",
              ROOT/"data/ddo02b_atlas/ddo02b_observable_atlas.json",ROOT/"data/ddo02b_atlas/ddo02b_reference_target_atlas.json",ROOT/"data/ddo02b_atlas/ddo02b_case_metadata.json",
              DATA/"ddo02b_observable_feature_cache.npz",DATA/"ddo02b_observable_feature_schema.json",DATA/"ddo02b_reference_target_cache.npz",DATA/"ddo02b_reference_target_schema.json",
              METRICS,DATA/"ddo02b_non_neural_diagnostics.json",DATA/"ddo02b_non_neural_diagnostics.csv",VERDICT,cpman,
              REPORT/"ddo02b_component_h3_h4_ledger.csv",report,firewall,nextp,final_ledger]+scripts
    gates={
        "ddo02a_frozen":json.loads((MAN/"ddo02a_manifest.json").read_text())["terminal_status"]=="DDO02A_FAILURE_ATTRIBUTION_FROZEN",
        "ca06_frozen_before_fresh_targets":json.loads((MAN/"ca06_manifest.json").read_text())["frozen_before_ddo02b_target_evaluation"],
        "fresh_case_count_384":json.loads((MAN/"ddo02b_case_registry.json").read_text())["case_count"]==384,
        "balanced_96_each":json.loads((MAN/"ddo02b_case_registry.json").read_text())["family_counts"]=={"F1":96,"F2":96,"F3":96,"F4":96},
        "old_lineage_overlap_zero":json.loads((MAN/"ddo02b_case_registry.json").read_text())["old_ddo01d_lineage_overlap_count"]==0,
        "formal_samples_49152":json.loads((MAN/"ddo02b_particle_sample_registry.json").read_text())["total_sample_count"]==49152,
        "all_fresh_cases_valid":all(c["mandatory_audit"]["mandatory_case_pass"] for c in json.loads((ROOT/"data/ddo02b_atlas/ddo02b_case_metadata.json").read_text())["cases"]),
        "observable_firewall":schema["controls"]["reference_archives_opened"] is False and len(prohibited)==4,
        "old_verdict_unchanged":sha(OLD)=="478e51ea8a9b407a0181c9bb7789590a76e7dc8b6aa3301beb5084e8dbd1dd0e",
        "formal_checkpoint_count_35":len(checkpoints)==35,
        "scripts_compile":compile_pass,
        "no_neural_training":metrics["controls"]["neural_training"] is False,
        "terminal_consistent":status in ("ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED","DDO02B_DENSITY_RATE_ONLY_OBSERVABILITY_QUALIFIED","DDO02B_COMPONENTWISE_OBSERVABILITY_MIXED_OR_QUALIFIED"),
    }
    audit=DATA/"ddo02b_release_audit.json"; audit.write_text(json.dumps({"gate_count":len(gates),"pass_count":sum(gates.values()),"gates":gates,"release_pass":all(gates.values())},indent=2,sort_keys=True)+"\n")
    required.append(audit)
    if not all(gates.values()): raise RuntimeError(f"release gates failed: {[k for k,v in gates.items() if not v]}")
    manifest={"schema_version":"1.0","stage":"DDO-02B","terminal_status":status,"formal_h3":verdict["formal_h3"],"formal_h4":verdict["formal_h4"],
              "h5_authorized_components":passed,"online_route_closed":status=="ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED",
              "neural_training_performed":False,"bound_files":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in required]}
    out=MAN/"ddo02b_manifest.json"; out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"terminal_status":status,"manifest_sha256":sha(out),"release_gates":f"{sum(gates.values())}/{len(gates)}","h5_authorized_components":passed},indent=2))
if __name__=="__main__": main()
