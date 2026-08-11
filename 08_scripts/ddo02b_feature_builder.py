#!/usr/bin/env python3
"""Build physically isolated deployable C0--C3 features for fresh DDO-02B."""

from __future__ import annotations

import hashlib,json,os,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"08_scripts"))
import ddo01e_feature_builder as legacy  # noqa: E402
from ddo02_descriptors import DESCRIPTOR_NAMES,compute_case_descriptors,context_blocks  # noqa: E402

OBS=ROOT/"data/ddo02b_atlas/ddo02b_observable_atlas.json"
PART=ROOT/"06_manifests/ddo02b_diagnostic_partition.json"
SAMPLE=ROOT/"06_manifests/ddo02b_particle_sample_registry.json"
OUT=ROOT/"data/ddo02b_identifiability"; CACHE=OUT/"ddo02b_observable_feature_cache.npz"; SCHEMA=OUT/"ddo02b_observable_feature_schema.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if CACHE.exists() or SCHEMA.exists(): raise RuntimeError("fresh feature cache exists")
    oi=json.loads(OBS.read_text()); part=json.loads(PART.read_text()); samples=json.loads(SAMPLE.read_text())
    pmap={c["canonical_case_id"]:c for c in part["cases"]}; blocks=defaultdict(list); schema={}; qc=Counter()
    meta={key:[] for key in ("sample_case_index","sample_particle_id","sample_fold","sample_family","sample_lineage","sample_key")}
    for number,(entry,sample) in enumerate(zip(oi["cases"],samples["cases"],strict=True)):
        if sha(ROOT/entry["path"])!=entry["sha256"]: raise RuntimeError("observable hash")
        ids=sample["particle_ids"]
        with np.load(ROOT/entry["path"],allow_pickle=False) as obs:
            if any(k.startswith("target_ref__") for k in obs.files): raise RuntimeError("target on observable side")
            old,old_schema=legacy.build_case(obs,ids)
            values,_,case_qc=compute_case_descriptors(obs); qc.update(case_qc)
            expanded=context_blocks(values,np.asarray(obs["edge_row"],dtype=np.int64),np.asarray(obs["edge_col"],dtype=np.int64),ids)
        for (layer,inc),array in old.items():
            if layer not in ("G","C","P"): continue
            blocks[(layer,inc)].append(array); schema[(layer,inc)]=old_schema[(layer,inc)]
        for inc,array in expanded.items():
            blocks[("N",inc)].append(array)
            names=[]
            if inc=="I0":
                for name in DESCRIPTOR_NAMES: names.append({"name":f"ddo02__{name}","source_field":f"ddo02__{name}","transform":"particle"})
            else:
                prefix={"I1":"onehop","I2":"twohop","I3":"global"}[inc]
                for agg in ("mean","std","min","max"):
                    for name in DESCRIPTOR_NAMES: names.append({"name":f"ddo02__{name}::{prefix}_{agg}","source_field":f"ddo02__{name}","transform":f"{prefix}_{agg}"})
            schema[("N",inc)]=names
        pm=pmap[entry["canonical_case_id"]]
        for pid in ids:
            meta["sample_case_index"].append(entry["case_index"]); meta["sample_particle_id"].append(pid)
            meta["sample_fold"].append(int(pm["diagnostic_fold"].split("_")[-1])); meta["sample_family"].append(pm["macro_family"])
            meta["sample_lineage"].append(pm["field_lineage_id"]); meta["sample_key"].append(f"{entry['canonical_case_id']}|{pid}")
        if (number+1)%16==0: print(f"ddo02b_feature_case {number+1}/384",flush=True)
    output={"sample_case_index":np.asarray(meta["sample_case_index"],dtype=np.int16),"sample_particle_id":np.asarray(meta["sample_particle_id"],dtype=np.int32),
            "sample_fold":np.asarray(meta["sample_fold"],dtype=np.int8),"sample_family":np.asarray(meta["sample_family"],dtype="U2"),
            "sample_lineage":np.asarray(meta["sample_lineage"],dtype="U88"),"sample_key":np.asarray(meta["sample_key"],dtype="U160")}
    for key,values in blocks.items(): output[f"feature__{key[0]}__{key[1]}"]=np.concatenate(values)
    OUT.mkdir(parents=True,exist_ok=True); temp=CACHE.with_suffix(".npz.tmp")
    with temp.open("wb") as h: np.savez_compressed(h,**output)
    os.replace(temp,CACHE)
    SCHEMA.write_text(json.dumps({"schema_version":"1.0","stage":"DDO-02B","side":"OBSERVABLE_SIDE_DERIVED_FEATURE_CACHE",
        "reference_in_model_input":False,"source_observable_index_sha256":sha(OBS),"partition_sha256":sha(PART),"sample_registry_sha256":sha(SAMPLE),
        "sample_count":49152,"case_count":384,"content_ladder":{"C0":["G"],"C1":["G","C"],"C2":["G","C","P"],"C3":["G","C","P","N"]},
        "N_layer_semantics":"CA06_EXPANDED_DEPLOYABLE_DESCRIPTORS_NOT_LEGACY_DESIGN_METADATA",
        "prohibited_fields_absent":["obs__kh_max","obs__kh_rms","obs__mode_count","obs__jitter_fraction"],
        "blocks":{f"feature__{l}__{i}":{"layer":l,"locality_increment":i,"feature_count":len(v),"features":v} for (l,i),v in sorted(schema.items())},
        "descriptor_qc":dict(qc),"controls":{"reference_archives_opened":False,"target_fields_used":False,"neural_training":False}},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"cache_sha256":sha(CACHE),"schema_sha256":sha(SCHEMA),"sample_count":49152,"descriptor_qc":dict(qc)},indent=2))

if __name__=="__main__": main()
