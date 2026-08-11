#!/usr/bin/env python3
"""Generate the fresh DDO-02B observable/reference atlas after CA-06 freeze."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))
import ddo01d_atlas_builder as base  # noqa: E402

REGISTRY = ROOT / "06_manifests/ddo02b_case_registry.json"
CA06 = ROOT / "06_manifests/ca06_manifest.json"
DATA = ROOT / "data/ddo02b_atlas"
OBS_DIR = DATA / "observable_cases"
REF_DIR = DATA / "reference_cases"
CHECKPOINT = DATA / "ddo02b_case_checkpoint.jsonl"
OBS_INDEX = DATA / "ddo02b_observable_atlas.json"
REF_INDEX = DATA / "ddo02b_reference_target_atlas.json"
META_JSON = DATA / "ddo02b_case_metadata.json"
META_CSV = DATA / "ddo02b_case_metadata.csv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checkpoint(registry: dict) -> list[dict]:
    if not CHECKPOINT.exists(): return []
    rows = [json.loads(line) for line in CHECKPOINT.read_text().splitlines() if line]
    for i,row in enumerate(rows):
        if row["canonical_case_id"] != registry["cases"][i]["canonical_case_id"]:
            raise RuntimeError("checkpoint prefix mismatch")
        if sha(ROOT/row["observable_archive_path"]) != row["observable_archive_sha256"]: raise RuntimeError("observable checkpoint hash")
        if sha(ROOT/row["reference_archive_path"]) != row["reference_archive_sha256"]: raise RuntimeError("reference checkpoint hash")
    return rows


def write_outputs(cases: list[dict], obs_schema: dict, ref_schema: dict, registry_sha: str, ca06_sha: str) -> None:
    OBS_INDEX.write_text(json.dumps({
        "schema_version":"1.0","stage":"DDO-02B","side":"OBSERVABLE_SIDE","reference_in_model_input":False,
        "case_count":len(cases),"particle_count":sum(c["particle_count"] for c in cases),"schema":obs_schema,
        "cases":[{"case_index":c["case_index"],"canonical_case_id":c["canonical_case_id"],"path":c["observable_archive_path"],"sha256":c["observable_archive_sha256"]} for c in cases],
    }, indent=2, sort_keys=True)+"\n")
    REF_INDEX.write_text(json.dumps({
        "schema_version":"1.0","stage":"DDO-02B","side":"REFERENCE_TARGET_SIDE","eligible_as_model_input":False,
        "case_count":len(cases),"particle_count":sum(c["particle_count"] for c in cases),"schema":ref_schema,
        "cases":[{"case_index":c["case_index"],"canonical_case_id":c["canonical_case_id"],"path":c["reference_archive_path"],"sha256":c["reference_archive_sha256"]} for c in cases],
    }, indent=2, sort_keys=True)+"\n")
    META_JSON.write_text(json.dumps({
        "schema_version":"1.0","stage":"DDO-02B","registry_sha256":registry_sha,"ca06_manifest_sha256":ca06_sha,
        "case_count":len(cases),"cases":cases,
        "environment":{"python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,"torch":torch.__version__,"platform":platform.platform(),"device":"cpu"},
        "controls":{"fresh_formal_evidence":True,"old_ddo01d_formal_evidence_reused":False,"neural_training":False},
    }, indent=2, sort_keys=True)+"\n")
    columns = ("case_index","canonical_case_id","macro_family","data_role","resolution_per_axis","particle_count","edge_count",
               "support_over_dx","probe","layout_class","jitter_fraction","mandatory_case_pass","observable_archive_path",
               "observable_archive_sha256","reference_archive_path","reference_archive_sha256")
    with META_CSV.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns); writer.writeheader()
        for c in cases:
            writer.writerow({**{key:c.get(key) for key in columns},"mandatory_case_pass":c["mandatory_audit"]["mandatory_case_pass"]})


def main() -> None:
    if any(p.exists() for p in (OBS_INDEX,REF_INDEX,META_JSON,META_CSV)):
        raise RuntimeError("final DDO-02B atlas already exists")
    ca06=json.loads(CA06.read_text()); registry=json.loads(REGISTRY.read_text())
    if ca06.get("terminal_status")!="DDO_CA06_EXPANDED_OBSERVABLE_CONTRACT_FROZEN" or registry.get("registry_status")!="FROZEN_BEFORE_FRESH_TARGET_EVALUATION":
        raise RuntimeError("freeze prerequisite failure")
    DATA.mkdir(parents=True,exist_ok=True); OBS_DIR.mkdir(exist_ok=True); REF_DIR.mkdir(exist_ok=True)
    cases=load_checkpoint(registry); cache=base.GeometryCache(); obs_schema=ref_schema=None
    with CHECKPOINT.open("a" if cases else "w") as handle:
        for entry in registry["cases"][len(cases):]:
            meta,obs,ref=base.run_case(entry,cache.get(entry))
            meta["data_role"]="FRESH_FORMAL_H3_H4_QUALIFICATION_EVIDENCE"
            op=OBS_DIR/f"case_{entry['case_index']:04d}.npz"; rp=REF_DIR/f"case_{entry['case_index']:04d}.npz"
            meta["observable_archive_path"]=str(op.relative_to(ROOT)); meta["observable_archive_sha256"]=base.deterministic_npz(op,obs)
            meta["reference_archive_path"]=str(rp.relative_to(ROOT)); meta["reference_archive_sha256"]=base.deterministic_npz(rp,ref)
            if obs_schema is None: obs_schema=base.archive_schema(obs); ref_schema=base.archive_schema(ref)
            handle.write(json.dumps(meta,sort_keys=True)+"\n"); handle.flush(); cases.append(meta)
            print(f"ddo02b_case_complete {len(cases)}/384 {entry['macro_family']}",flush=True)
    if obs_schema is None:
        with np.load(ROOT/cases[0]["observable_archive_path"]) as z: obs_schema=base.archive_schema({k:z[k] for k in z.files})
        with np.load(ROOT/cases[0]["reference_archive_path"]) as z: ref_schema=base.archive_schema({k:z[k] for k in z.files})
    if not all(c["mandatory_audit"]["mandatory_case_pass"] for c in cases): raise RuntimeError("numerically invalid fresh case")
    write_outputs(cases,obs_schema,ref_schema,sha(REGISTRY),sha(CA06))
    print(json.dumps({"case_count":len(cases),"valid":sum(c["mandatory_audit"]["mandatory_case_pass"] for c in cases),
                      "observable_index_sha256":sha(OBS_INDEX),"reference_index_sha256":sha(REF_INDEX)},indent=2))


if __name__=="__main__": main()
