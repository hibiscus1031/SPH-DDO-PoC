#!/usr/bin/env python3
"""Freeze target-free DDO-02B lineage folds and particle samples."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"06_manifests/ddo02b_case_registry.json"
PART=ROOT/"06_manifests/ddo02b_diagnostic_partition.json"
SAMPLE=ROOT/"06_manifests/ddo02b_particle_sample_registry.json"

def canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def payload(c):
    keys=("macro_family","field_subtype","mode_indices","phases_radians","probe","polarization","active_amplitude")
    return {k:c[k] for k in keys}
def lineage(c): return "DDO02B|FIELD_LINEAGE|"+digest(canonical(payload(c)))

def main():
    reg=json.loads(REG.read_text()); families=defaultdict(set)
    for c in reg["cases"]: families[c["macro_family"]].add(lineage(c))
    fold_by={}
    for fam,values in sorted(families.items()):
        ordered=sorted(values,key=lambda x:digest(f"DDO02B|FOLD|{fam}|{x}"))
        fold_by.update({value:i%5 for i,value in enumerate(ordered)})
    part_cases=[]; sample_cases=[]
    for c in reg["cases"]:
        lin=lineage(c); n=int(c["resolution_per_axis"])**2
        ids=sorted(range(n),key=lambda p:(digest(f"DDO02B|PARTICLE|{c['canonical_case_id']}|{p}"),p))[:128]
        part_cases.append({"case_index":c["case_index"],"canonical_case_id":c["canonical_case_id"],"macro_family":c["macro_family"],
                           "field_lineage_id":lin,"diagnostic_fold":f"FOLD_{fold_by[lin]}","formal_evidence":True})
        sample_cases.append({"case_index":c["case_index"],"canonical_case_id":c["canonical_case_id"],"particle_count":n,
                             "sample_count":128,"particle_ids":ids})
    f4=defaultdict(set)
    for c,p in zip(reg["cases"],part_cases):
        if c["macro_family"]=="F4": f4[c["f4_matched_block_id"]].add((p["field_lineage_id"],p["diagnostic_fold"]))
    if any(len(v)!=1 for v in f4.values()): raise RuntimeError("F4 matched block leakage")
    PART.write_text(json.dumps({"schema_version":"1.0","stage":"DDO-02B","selection_is_target_free":True,
        "case_count":384,"lineage_count":sum(len(v) for v in families.values()),"fold_count":5,"cases":part_cases},indent=2,sort_keys=True)+"\n")
    SAMPLE.write_text(json.dumps({"schema_version":"1.0","stage":"DDO-02B","selection_is_target_free":True,
        "case_count":384,"sample_count_per_case":128,"total_sample_count":49152,"cases":sample_cases},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"partition_sha256":hashlib.sha256(PART.read_bytes()).hexdigest(),"sample_sha256":hashlib.sha256(SAMPLE.read_bytes()).hexdigest(),
                      "lineage_count":sum(len(v) for v in families.values()),"sample_count":49152},indent=2))

if __name__=="__main__": main()
