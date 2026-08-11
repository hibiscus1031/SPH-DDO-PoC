#!/usr/bin/env python3
"""Synthetic-only qualification tests for prospective CA-05 semantics."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from h3_identifiability_semantics import (
    CONSTANT_EXCLUDED, assign_diagnostic_folds, conditional_variance_ratios,
    content_fields, field_lineage_id, fit_robust_scaler, h3_gate,
    project_status, selected_particle_ids, target_trace_variance, transform_robust,
)
from h4_locality_semantics import locality_verdict


def synthetic_case(family: str, index: int) -> dict:
    return {
        "canonical_case_id": f"case-{family}-{index}", "macro_family": family,
        "field_subtype": "synthetic", "mode_indices": [[1 + index % 2, 0]],
        "phases_radians": [0.0], "probe": "density", "polarization": "none",
        "active_amplitude": 0.01, "resolution_per_axis": 16 + 8 * index,
        "support_over_dx": 2 + index % 4, "jitter_fraction": 0.0,
    }


class TestCA05Semantics(unittest.TestCase):
    def test_01_lineage_ignores_numerical_variants(self):
        first = synthetic_case("F1", 0)
        second = copy.deepcopy(first)
        second.update(resolution_per_axis=64, support_over_dx=5, jitter_fraction=0.1)
        self.assertEqual(field_lineage_id(first), field_lineage_id(second))

    def test_02_lineage_changes_with_field(self):
        first = synthetic_case("F1", 0)
        second = copy.deepcopy(first)
        second["phases_radians"] = [1.0]
        self.assertNotEqual(field_lineage_id(first), field_lineage_id(second))

    def test_03_fold_assignment_keeps_lineage(self):
        first = synthetic_case("F1", 0)
        second = copy.deepcopy(first)
        second["canonical_case_id"] = "variant"
        second["resolution_per_axis"] = 64
        folds = assign_diagnostic_folds([first, second])
        self.assertEqual(folds[first["canonical_case_id"]], folds[second["canonical_case_id"]])

    def test_04_particle_sample_exact_and_deterministic(self):
        first = selected_particle_ids("case", 256)
        self.assertEqual(len(first), 128)
        self.assertEqual(len(set(first)), 128)
        self.assertEqual(first, selected_particle_ids("case", 256))

    def test_05_particle_sample_rejects_short_case(self):
        with self.assertRaises(ValueError):
            selected_particle_ids("case", 127)

    def test_06_content_sets_are_nested(self):
        sets = [set(content_fields(name)) for name in ("C0", "C1", "C2", "C3")]
        self.assertTrue(sets[0] < sets[1] < sets[2] < sets[3])

    def test_07_constants_retained_in_c3(self):
        self.assertTrue(set(CONSTANT_EXCLUDED).issubset(content_fields("C3")))

    def test_08_scaler_excludes_zero_iqr(self):
        train = np.array([[1.0, 1.0], [1.0, 2.0], [1.0, 3.0], [1.0, 4.0]])
        scaler = fit_robust_scaler(train, ["constant", "varying"])
        self.assertEqual(scaler["retained_names"], ("varying",))
        self.assertEqual(transform_robust(train, scaler).shape, (4, 1))

    def test_09_conditional_variance_known(self):
        neighbors = np.array([[[0.0], [2.0]], [[1.0], [3.0]]])
        np.testing.assert_allclose(conditional_variance_ratios(neighbors, 2.0), [1.0, 1.0])

    def test_10_equal_case_unconditional_variance(self):
        target = np.array([0.0, 2.0, 10.0, 10.0])
        cases = np.array(["a", "a", "b", "b"])
        self.assertAlmostEqual(target_trace_variance(target, cases), 20.75)

    def test_11_h3_obvious_pass(self):
        metrics = dict(execution_complete=True, dnn_median=.1, dnn_p90=.2, cvar=.1,
                       cvar_upper95=.2, oracle_nrmse=.3, baseline_improvement=.4,
                       max_family_nrmse=.5, coverage=.95)
        self.assertEqual(h3_gate(metrics), "H3_OBSERVABLE_MAPPING_IDENTIFIABLE")

    def test_12_h3_tail_fail(self):
        metrics = dict(execution_complete=True, dnn_median=.1, dnn_p90=.61, cvar=.1,
                       cvar_upper95=.2, oracle_nrmse=.3, baseline_improvement=.4,
                       max_family_nrmse=.5, coverage=.95)
        self.assertEqual(h3_gate(metrics), "H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE")

    def test_13_h3_incomplete_unresolved(self):
        self.assertEqual(h3_gate({"execution_complete": False}), "H3_IDENTIFIABILITY_UNRESOLVED")

    def test_14_h4_selects_smallest_equivalent(self):
        evidence = {
            "L0": {"h3_status": "H3_OBSERVABLE_MAPPING_IDENTIFIABLE", "paired_degradation": {
                "L1": {"relative_nrmse_upper95": .06, "cvar_difference_upper95": .01},
                "L2": {"relative_nrmse_upper95": .06, "cvar_difference_upper95": .01},
                "L3": {"relative_nrmse_upper95": .06, "cvar_difference_upper95": .01}}},
            "L1": {"h3_status": "H3_OBSERVABLE_MAPPING_IDENTIFIABLE", "paired_degradation": {
                "L2": {"relative_nrmse_upper95": .04, "cvar_difference_upper95": .02},
                "L3": {"relative_nrmse_upper95": .05, "cvar_difference_upper95": .03}}},
        }
        self.assertEqual(locality_verdict("H3_OBSERVABLE_MAPPING_IDENTIFIABLE", evidence)["selected_rung"], "L1")

    def test_15_h4_requires_h3(self):
        self.assertEqual(locality_verdict("H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE", {})["status"], "OBSERVABLE_MAPPING_NOT_IDENTIFIABLE")

    def test_16_h4_l3_global_language(self):
        evidence = {"L3": {"h3_status": "H3_OBSERVABLE_MAPPING_IDENTIFIABLE", "paired_degradation": {}}}
        self.assertEqual(locality_verdict("H3_OBSERVABLE_MAPPING_IDENTIFIABLE", evidence)["status"], "STRICT_LOCALITY_NOT_SUPPORTED_GLOBAL_CONTEXT_REQUIRED")

    def test_17_project_mixed(self):
        h3 = {"density_rate": "H3_OBSERVABLE_MAPPING_IDENTIFIABLE", "pressure_gradient_acceleration": "H3_OBSERVABLE_MAPPING_NOT_IDENTIFIABLE", "viscosity_laplacian_acceleration": "H3_OBSERVABLE_MAPPING_IDENTIFIABLE"}
        self.assertEqual(project_status(h3, {}), "DDO01E_COMPONENTWISE_IDENTIFIABILITY_MIXED")

    def test_18_project_all_bounded(self):
        h3 = {name: "H3_OBSERVABLE_MAPPING_IDENTIFIABLE" for name in ("density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration")}
        h4 = {name: "ONE_HOP_LOCALITY_SUPPORTED" for name in h3}
        self.assertEqual(project_status(h3, h4), "DDO01E_OBSERVABLE_MAPPING_AND_LOCALITY_QUALIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
