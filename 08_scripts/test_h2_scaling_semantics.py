#!/usr/bin/env python3
"""Synthetic-only qualification tests for CA-03 H2 semantics."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_scripts"))

from h2_scaling_semantics import (  # noqa: E402
    FAIL,
    PASS,
    UNRESOLVED,
    deterministic_pool_permutation,
    evaluate_family,
    evaluate_track,
    local_log_slope,
    map_component_verdict,
)


def track_points(
    xs: list[float],
    values: list[float],
    *,
    replicate_factors: tuple[float, float, float] = (1.0, 1.0, 1.0),
    relative_uncertainty: float = 1.0e-8,
) -> list[dict[str, float | int | bool]]:
    result = []
    for x, value in zip(xs, values, strict=True):
        for replicate, factor in enumerate(replicate_factors):
            target = value * factor
            result.append({
                "x": x,
                "replicate_id": replicate,
                "T": target,
                "U": target * relative_uncertainty,
                "S": 1.0,
                "audit_valid": True,
            })
    return result


class TestH2ScalingSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        expected = json.loads((ROOT / "06_manifests/ca03_synthetic_expected_outputs.json").read_text())
        assert len(expected["tests"]) == 14
        assert expected["historical_or_real_sph_values_used"] is False

    def test_01_clean_p2_refinement_pass(self) -> None:
        xs = [0.125, 0.25, 0.5]
        values = [x**2 for x in xs]
        result = evaluate_family({"track_a": track_points(xs, values), "track_b": track_points(xs, [2*v for v in values])})
        self.assertEqual(result["verdict"], PASS)
        self.assertAlmostEqual(result["tracks"]["track_a"]["representative_slope_descriptive"], 2.0)

    def test_02_clean_positive_spectral_pass(self) -> None:
        xs = [0.25, 0.5, 1.0]
        result = evaluate_family({
            "track_a": track_points(xs, [1.0, 1.5, 2.5]),
            "track_b": track_points(xs, [2.0, 3.0, 5.0]),
        })
        self.assertEqual(result["verdict"], PASS)

    def test_03_exactly_75pct_pass(self) -> None:
        xs = [1.0, 2.0, 4.0]
        result = evaluate_family({
            "all_supported": track_points(xs, [1.0, 2.0, 4.0]),
            "half_supported": track_points(xs, [1.0, 2.0, 1.0]),
        })
        self.assertEqual(result["verdict"], PASS)
        self.assertEqual(result["M_family"], 0.75)

    def test_04_below_75pct_fails(self) -> None:
        xs = [1.0, 2.0, 4.0, 8.0]
        result = evaluate_family({
            "all_supported": track_points(xs, [1.0, 2.0, 4.0, 8.0]),
            "one_of_three": track_points(xs, [1.0, 2.0, 1.0, 0.5]),
        })
        self.assertEqual(result["verdict"], FAIL)
        self.assertLess(result["M_family"], 0.75)

    def test_05_uncertainty_overlap_plateau_non_supporting(self) -> None:
        a = {"x": 1.0, "replicate_id": 0, "T": 1.0, "U": 0.02, "S": 1.0, "audit_valid": True}
        b = {"x": 2.0, "replicate_id": 0, "T": 1.01, "U": 0.02, "S": 1.0, "audit_valid": True}
        slope = local_log_slope(a, b)
        self.assertEqual(slope["classification"], "PLATEAU_OR_UNCERTAINTY_OVERLAP")
        xs = [1.0, 2.0, 4.0]
        result = evaluate_family({
            "track_a": track_points(xs, [1.0, 1.01, 1.02], relative_uncertainty=0.02),
            "track_b": track_points(xs, [2.0, 2.02, 2.04], relative_uncertainty=0.02),
        })
        self.assertEqual(result["verdict"], FAIL)
        self.assertEqual(result["M_family"], 0.0)

    def test_06_opposite_sign_fails(self) -> None:
        xs = [1.0, 2.0, 4.0]
        a = track_points(xs, [4.0, 2.0, 1.0])
        result = evaluate_family({"track_a": a, "track_b": track_points(xs, [8.0, 4.0, 2.0])})
        self.assertEqual(result["verdict"], FAIL)
        self.assertTrue(all(
            slope["classification"] == "OPPOSITE_SIGN"
            for slope in result["tracks"]["track_a"]["local_slopes"]
        ))

    def test_07_dispersion_exceeding_change_fails(self) -> None:
        xs = [1.0, 2.0, 4.0]
        values = [1.0, 1.1, 1.21]
        wide = track_points(xs, values, replicate_factors=(0.5, 1.0, 2.0))
        result = evaluate_family({"track_a": wide, "track_b": wide})
        self.assertEqual(result["verdict"], FAIL)
        self.assertGreaterEqual(result["tracks"]["track_a"]["D_t"], result["tracks"]["track_a"]["C_t"])

    def test_08_two_levels_unresolved(self) -> None:
        result = evaluate_track(track_points([1.0, 2.0], [1.0, 2.0]))
        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(result["reason"], "INSUFFICIENT_LEVELS")

    def test_09_one_track_unresolved(self) -> None:
        result = evaluate_family({"only_track": track_points([1.0, 2.0, 4.0], [1.0, 2.0, 4.0])})
        self.assertEqual(result["verdict"], UNRESOLVED)

    def test_10_nonpositive_lower_response_unresolved(self) -> None:
        points = track_points([1.0, 2.0, 4.0], [1.0, 2.0, 4.0])
        points[0]["U"] = points[0]["T"]
        result = evaluate_track(points)
        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(result["reason"], "LOG_RESPONSE_UNRESOLVED")

    def test_11_equal_track_weighting(self) -> None:
        result = evaluate_family({
            "short_positive": track_points([1.0, 2.0, 4.0], [1.0, 2.0, 4.0]),
            "long_negative": track_points([1.0, 2.0, 4.0, 8.0, 16.0], [16.0, 8.0, 4.0, 2.0, 1.0]),
        })
        self.assertEqual(result["M_family"], 0.5)
        self.assertNotEqual(result["M_family"], 6.0 / 18.0)

    def test_12_regular_pass_jitter_fail_mapping(self) -> None:
        mapped = map_component_verdict(PASS, PASS, PASS, FAIL)
        self.assertEqual(mapped["component_verdict"], "H2_SCALING_PASS_REGULAR_SCOPE_ONLY")

    def test_13_support_ratio_cannot_change_verdict(self) -> None:
        first = map_component_verdict(PASS, PASS, PASS, PASS, support_ratio_diagnostic={"shape": "increasing"})
        second = map_component_verdict(PASS, PASS, PASS, PASS, support_ratio_diagnostic={"shape": "nonmonotonic"})
        self.assertEqual(first, second)

    def test_14_deterministic_registry_hash_mapping(self) -> None:
        phases = [0.0, math.pi / 4.0, math.pi / 2.0]
        first, first_records = deterministic_pool_permutation(phases, "DDO01CR|PHASE", "synthetic-track", 3)
        second, second_records = deterministic_pool_permutation(phases, "DDO01CR|PHASE", "synthetic-track", 3)
        self.assertEqual(first, second)
        self.assertEqual(first_records, second_records)
        self.assertEqual(len(set(first)), 3)
        seeds, _ = deterministic_pool_permutation([20260811, 20260817, 20260823], "DDO01CR|JITTER", "synthetic-track", 3)
        self.assertEqual(len(set(seeds)), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
