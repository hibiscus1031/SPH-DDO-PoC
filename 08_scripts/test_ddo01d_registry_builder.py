#!/usr/bin/env python3
"""Synthetic/design-only qualification tests for the CA-04 registry builder."""

from __future__ import annotations

import json
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))

from ddo01d_registry_builder import (  # noqa: E402
    DENSITY_AMPLITUDES,
    JITTER_FRACTIONS,
    JITTER_SEEDS,
    MULTI_MODE_SETS,
    PHASES,
    RESOLUTIONS,
    SINGLE_MODES,
    SUPPORT_RATIOS,
    VELOCITY_AMPLITUDES,
    build_registry,
)


class TestDDO01DRegistryBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_registry()
        cls.second = build_registry()

    def test_01_exact_size_and_family_balance(self) -> None:
        self.assertEqual(self.first["case_count"], 512)
        self.assertEqual(self.first["family_counts"], {"F1": 128, "F2": 128, "F3": 128, "F4": 128})

    def test_02_deterministic_replay(self) -> None:
        self.assertEqual(json.dumps(self.first, sort_keys=True), json.dumps(self.second, sort_keys=True))

    def test_03_unique_canonical_ids(self) -> None:
        ids = [case["canonical_case_id"] for case in self.first["cases"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_04_authorized_finite_pools_only(self) -> None:
        authorized_modes = set(SINGLE_MODES)
        authorized_sets = {tuple(value) for value in MULTI_MODE_SETS}
        for case in self.first["cases"]:
            self.assertIn(case["resolution_per_axis"], RESOLUTIONS)
            self.assertIn(case["support_over_dx"], SUPPORT_RATIOS)
            modes = tuple(tuple(value) for value in case["mode_indices"])
            self.assertTrue((len(modes) == 1 and modes[0] in authorized_modes) or modes in authorized_sets)
            self.assertTrue(all(phase in PHASES for phase in case["phases_radians"]))
            self.assertIn(case["density_amplitude"], DENSITY_AMPLITUDES)
            self.assertIn(case["velocity_amplitude"], VELOCITY_AMPLITUDES)
            self.assertIn(case["jitter_fraction"], JITTER_FRACTIONS)
            if case["jitter_seed"] is not None:
                self.assertIn(case["jitter_seed"], JITTER_SEEDS)

    def test_05_target_free_schema(self) -> None:
        forbidden = ("target", "defect", "h1_ratio", "h2_slope", "pca", "svd", "reference")
        for case in self.first["cases"]:
            keys = "|".join(case).lower()
            self.assertFalse(any(token in keys for token in forbidden))
        self.assertTrue(self.first["selection_is_target_free"])

    def test_06_design_validity_filters(self) -> None:
        for case in self.first["cases"]:
            self.assertGreaterEqual(case["points_per_wavelength_min"], 8.0)
            self.assertLess(case["support_h"], 0.5)
            self.assertGreater(1.0 - case["density_amplitude"], 0.0)

    def test_07_f4_exact_matched_blocks(self) -> None:
        blocks = defaultdict(list)
        for case in self.first["cases"]:
            if case["macro_family"] == "F4":
                blocks[case["f4_matched_block_id"]].append(case)
        self.assertEqual(len(blocks), 8)
        for cases in blocks.values():
            self.assertEqual(len(cases), 16)
            self.assertEqual(Counter(case["support_over_dx"] for case in cases), Counter({2.0: 4, 3.0: 4, 4.0: 4, 5.0: 4}))
            self.assertEqual(Counter(case["jitter_fraction"] for case in cases), Counter({0.0: 4, 0.025: 4, 0.05: 4, 0.1: 4}))
            for jitter in (0.025, 0.05, 0.1):
                self.assertEqual(len({case["jitter_seed"] for case in cases if case["jitter_fraction"] == jitter}), 1)

    def test_08_all_cases_are_development_only(self) -> None:
        self.assertEqual({case["data_role"] for case in self.first["cases"]}, {"DEVELOPMENT_ATLAS"})

    def test_09_historical_h2_not_counted(self) -> None:
        self.assertFalse(self.first["historical_h2_cases_count_toward_fresh_quota"])
        self.assertEqual(self.first["case_count"], 512)

    def test_10_component_roles(self) -> None:
        roles = self.first["component_roles"]
        self.assertEqual(roles["total_acceleration"], "DERIVED_CLOSURE_DIAGNOSTIC")
        self.assertEqual(roles["interpolation_density"], "ALGEBRAIC_DENSITY_DIAGNOSTIC")
        self.assertEqual(roles["density_rate"], "PRIMARY_DYNAMIC_TARGET")


if __name__ == "__main__":
    unittest.main(verbosity=2)
