#!/usr/bin/env python3
"""Run unchanged CA-05 non-neural H3/H4 semantics on fresh CA-06 features."""

from __future__ import annotations

import csv,hashlib,json,math,sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"08_scripts"))
import ddo01e_non_neural_analysis as analysis  # noqa: E402

DATA=ROOT/"data/ddo02b_identifiability"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def terminal(primary_h3,primary_h4):
    passed=[name for name,status in primary_h3.items() if status=="H3_OBSERVABLE_MAPPING_IDENTIFIABLE"]
    if not passed: return "ONLINE_SPATIAL_DDO_OBSERVABILITY_ROUTE_NOT_SUPPORTED"
    if passed==["density_rate"]: return "DDO02B_DENSITY_RATE_ONLY_OBSERVABILITY_QUALIFIED"
    return "DDO02B_COMPONENTWISE_OBSERVABILITY_MIXED_OR_QUALIFIED"

def exact_nearest_different_lineage(tree, train, lineages, dimension):
    """Exact progressive global-tree query, avoiding one complement tree per lineage."""
    result=np.full(train.shape[0],np.inf); remaining=np.arange(train.shape[0])
    _,counts=np.unique(lineages,return_counts=True); maximum=int(counts.max())+1
    schedule=sorted(set(min(maximum,k) for k in (32,128,512,2048,maximum)))
    for k in schedule:
        if remaining.size==0: break
        distances,indices=tree.query(train[remaining],k=k,eps=0,p=2,workers=-1)
        if k==1: distances,indices=distances[:,None],indices[:,None]
        unresolved=[]
        for local,global_row in enumerate(remaining):
            valid=lineages[indices[local]]!=lineages[global_row]
            where=np.flatnonzero(valid)
            if where.size: result[global_row]=distances[local,where[0]]/math.sqrt(dimension)
            else: unresolved.append(global_row)
        remaining=np.asarray(unresolved,dtype=np.int64)
    if remaining.size or not np.isfinite(result).all(): raise RuntimeError("different-lineage exact query failure")
    return result

def rewrite():
    metrics=json.loads(analysis.METRICS_PATH.read_text()); metrics["stage"]="DDO-02B"; metrics["generated_date"]="2026-08-11"
    metrics["fresh_formal_evidence_case_count"]=384; metrics["old_ddo01d_formal_evidence_reused"]=False
    metrics["formal_h3_combination"]="C3/L3_CA06_EXPANDED_DEPLOYABLE"; metrics["formal_h4_content"]="C3_CA06_EXPANDED_DEPLOYABLE"
    analysis.METRICS_PATH.write_text(json.dumps(metrics,indent=2,sort_keys=True)+"\n")
    diagnostics=json.loads(analysis.DIAGNOSTICS_JSON_PATH.read_text()); diagnostics["stage"]="DDO-02B"; diagnostics["metric_file_sha256"]=sha(analysis.METRICS_PATH)
    analysis.DIAGNOSTICS_JSON_PATH.write_text(json.dumps(diagnostics,indent=2,sort_keys=True)+"\n")
    verdict=json.loads(analysis.VERDICTS_PATH.read_text()); verdict["stage"]="DDO-02B"; verdict["metrics_sha256"]=sha(analysis.METRICS_PATH)
    verdict["fresh_evidence_only"]=True; verdict["permanent_ddo01e_status_preserved"]="DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE"
    analysis.VERDICTS_PATH.write_text(json.dumps(verdict,indent=2,sort_keys=True)+"\n")

def execute_selected():
    """Evaluate all formal gates plus the minimal prospective content ablation."""
    final_paths=(analysis.METRICS_PATH,analysis.DIAGNOSTICS_JSON_PATH,analysis.DIAGNOSTICS_CSV_PATH,analysis.VERDICTS_PATH,analysis.LEDGER_PATH)
    if any(p.exists() for p in final_paths): raise RuntimeError("final DDO-02B outputs already exist")
    analysis.build_target_cache(); analysis.CHECKPOINT_DIR.mkdir(parents=True,exist_ok=True)
    fs=json.loads(analysis.FEATURE_SCHEMA_PATH.read_text()); part=json.loads(analysis.PARTITION_PATH.read_text())
    meta_json=json.loads(analysis.META_PATH.read_text()); part_cases={c["case_index"]:c for c in part["cases"]}; metadata={c["case_index"]:c for c in meta_json["cases"]}
    combos=[("C0","L3"),("C1","L3"),("C2","L3")]+[("C3",loc) for loc in analysis.LOCALITIES]
    with np.load(analysis.FEATURE_PATH,allow_pickle=False) as feature,np.load(analysis.TARGET_PATH,allow_pickle=False) as target:
        fm={key:np.asarray(feature[key]) for key in ("sample_case_index","sample_particle_id","sample_fold","sample_family","sample_lineage","sample_key")}
        ta={key:np.asarray(target[key]) for key in target.files}; all_results={}; all_rows=[]; rows_by_combo={}
        for content,locality in combos:
            x,specs=analysis.feature_matrix(feature,fs,content,locality); fold_results=[]
            for fold in range(5):
                result=analysis.run_fold(content,locality,fold,x,specs,fm,ta,part_cases,metadata); fold_results.append(result)
                print(f"formal_diagnostic_complete {content} {locality} fold={fold}",flush=True)
            rows=[r for result in fold_results for r in result["case_rows"]]; rows_by_combo[f"{content}/{locality}"]=rows
            all_rows.extend([{**r,"content":content,"locality":locality} for r in rows])
            all_results[f"{content}/{locality}"]={"feature_qc":[{k:v for k,v in r.items() if k!="case_rows"} for r in fold_results],
                "components":{c:analysis.summarize_combination(rows,c,content,locality) for c in analysis.ALL_REPORTED_COMPONENTS}}
        formal_h3={c:all_results["C3/L3"]["components"][c]["h3_status"] for c in analysis.COMPONENTS}; h4={}; h4e={}
        for component in analysis.COMPONENTS:
            summaries={loc:all_results[f"C3/{loc}"]["components"][component] for loc in analysis.LOCALITIES}; evidence={}
            for i,loc in enumerate(analysis.LOCALITIES):
                evidence[loc]={"h3_status":summaries[loc]["h3_status"],"paired_degradation":{}}
                for broad in analysis.LOCALITIES[i+1:]:
                    evidence[loc]["paired_degradation"][broad]=analysis.paired_degradation(
                        {name:rows_by_combo[f"C3/{name}"] for name in analysis.LOCALITIES},summaries,component,loc,broad)
            h4e[component]=evidence; h4[component]=analysis.locality_verdict(formal_h3[component],evidence)
        primary={c:formal_h3[c] for c in analysis.COMPONENTS[:3]}; primary_h4={c:h4[c]["status"] for c in analysis.COMPONENTS[:3]}; status=terminal(primary,primary_h4)
        metrics={"schema_version":"1.0","project":"SPH-DDO-PoC","stage":"DDO-02B","generated_date":"2026-08-11","formal_sample_count":49152,
            "fresh_formal_evidence_case_count":384,"combination_count":len(combos),"evaluated_combinations":[f"{a}/{b}" for a,b in combos],"results":all_results,
            "formal_h3_combination":"C3/L3_CA06_EXPANDED_DEPLOYABLE","formal_h3":formal_h3,"formal_h4_content":"C3_CA06_EXPANDED_DEPLOYABLE",
            "formal_h4":h4,"h4_paired_evidence":h4e,"terminal_status":status,"controls":{"neural_training":False,"old_ddo01d_formal_evidence_reused":False}}
        analysis.atomic_json(analysis.METRICS_PATH,metrics)
        analysis.atomic_json(analysis.DIAGNOSTICS_JSON_PATH,{"schema_version":"1.0","stage":"DDO-02B","metric_file_sha256":sha(analysis.METRICS_PATH),
            "oracle_classes":list(analysis.ORACLES),"case_row_count":len(all_rows),"case_diagnostics_csv":str(analysis.DIAGNOSTICS_CSV_PATH.relative_to(ROOT)),
            "controls":{"production_model_claim":False,"architecture_selection":False,"neural_training":False}})
        fields=sorted({k for r in all_rows for k in r})
        with analysis.DIAGNOSTICS_CSV_PATH.open("w",newline="") as h:
            w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(all_rows)
        analysis.atomic_json(analysis.VERDICTS_PATH,{"schema_version":"1.0","stage":"DDO-02B","generated_date":"2026-08-11","metrics_sha256":sha(analysis.METRICS_PATH),
            "formal_h3":formal_h3,"formal_h4":h4,"terminal_status":status,"fresh_evidence_only":True,
            "permanent_ddo01e_status_preserved":"DDO01E_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE"})
        with analysis.LEDGER_PATH.open("w",newline="") as h:
            w=csv.DictWriter(h,fieldnames=("component","role","formal_combination","h3_status","h4_selected_rung","h4_status"));w.writeheader()
            for component in analysis.ALL_REPORTED_COMPONENTS:
                role=metadata[0]["components"][component]["role"]
                if component=="total_acceleration":
                    w.writerow({"component":component,"role":role,"formal_combination":"derived only","h3_status":"DERIVED_CLOSURE_DIAGNOSTIC_NO_INDEPENDENT_H3","h4_selected_rung":"","h4_status":"NOT_APPLICABLE_INDEPENDENT_ROUTE"})
                else:
                    hv=h4[component];w.writerow({"component":component,"role":role,"formal_combination":"C3/L3","h3_status":formal_h3[component],"h4_selected_rung":hv["selected_rung"] or "","h4_status":hv["status"]})

def main():
    analysis.DATA_DIR=DATA
    analysis.FEATURE_PATH=DATA/"ddo02b_observable_feature_cache.npz"; analysis.FEATURE_SCHEMA_PATH=DATA/"ddo02b_observable_feature_schema.json"
    analysis.TARGET_PATH=DATA/"ddo02b_reference_target_cache.npz"; analysis.TARGET_SCHEMA_PATH=DATA/"ddo02b_reference_target_schema.json"
    analysis.PARTITION_PATH=ROOT/"06_manifests/ddo02b_diagnostic_partition.json"; analysis.SAMPLE_PATH=ROOT/"06_manifests/ddo02b_particle_sample_registry.json"
    analysis.REF_INDEX_PATH=ROOT/"data/ddo02b_atlas/ddo02b_reference_target_atlas.json"; analysis.META_PATH=ROOT/"data/ddo02b_atlas/ddo02b_case_metadata.json"
    analysis.CHECKPOINT_DIR=DATA/"checkpoints"; analysis.METRICS_PATH=DATA/"ddo02b_metrics.json"
    analysis.DIAGNOSTICS_JSON_PATH=DATA/"ddo02b_non_neural_diagnostics.json"; analysis.DIAGNOSTICS_CSV_PATH=DATA/"ddo02b_non_neural_diagnostics.csv"
    analysis.VERDICTS_PATH=DATA/"ddo02b_formal_verdicts.json"; analysis.LEDGER_PATH=ROOT/"07_reports/ddo02b_component_h3_h4_ledger.csv"
    analysis.FEATURE_SHA256=sha(analysis.FEATURE_PATH); analysis.FEATURE_SCHEMA_SHA256=sha(analysis.FEATURE_SCHEMA_PATH)
    analysis.PARTITION_SHA256=sha(analysis.PARTITION_PATH); analysis.SAMPLE_SHA256=sha(analysis.SAMPLE_PATH)
    analysis.REF_INDEX_SHA256=sha(analysis.REF_INDEX_PATH); analysis.META_SHA256=sha(analysis.META_PATH)
    analysis.LAYERS={"C0":("G",),"C1":("G","C"),"C2":("G","C","P"),"C3":("G","C","P","N")}
    analysis.project_status=terminal
    analysis.nearest_different_lineage=exact_nearest_different_lineage
    execute_selected()
    verdict=json.loads(analysis.VERDICTS_PATH.read_text())
    print(json.dumps({"terminal_status":verdict["terminal_status"],"verdict_sha256":sha(analysis.VERDICTS_PATH),
                      "formal_h3":verdict["formal_h3"],"formal_h4":verdict["formal_h4"]},indent=2,sort_keys=True))

if __name__=="__main__": main()
