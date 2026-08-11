#!/usr/bin/env python3
"""Synthetic-only CA-02 tests. No SPH or historical target values are used."""

from __future__ import annotations

import math
import unittest

import numpy as np

from h1_signal_semantics import (
    case_label,
    component_verdict,
    deterministic_seed,
    equal_case_component_rms,
    evaluate_component,
    scalar_case_rms,
    stratified_group_bootstrap,
    vector_case_rms,
)


def strata(count: int) -> list[tuple[int, str]]:
    return [(16 if index < count // 2 else 32, "regular" if index % 2 == 0 else "jitter_0.05") for index in range(count)]


class H1SignalSemanticsTests(unittest.TestCase):
    def test_01_obvious_pass(self) -> None:
        result = evaluate_component(
            case_rms_values=np.full(8, 20.0),
            case_uncertainties=np.ones(8),
            strata=strata(8),
            canonical_component_name="synthetic_obvious_pass",
            mandatory_audits_valid=True,
        )
        self.assertEqual(result["verdict"], "H1_SIGNAL_PASS")
        self.assertEqual(result["R_c"], 20.0)
        self.assertEqual(result["L95_c"], 20.0)

    def test_02_point_threshold_fail(self) -> None:
        result = evaluate_component(
            case_rms_values=np.full(8, 9.0),
            case_uncertainties=np.ones(8),
            strata=strata(8),
            canonical_component_name="synthetic_point_fail",
            mandatory_audits_valid=True,
        )
        self.assertEqual(result["verdict"], "H1_SIGNAL_FAIL")
        self.assertLess(result["R_c"], 10.0)

    def test_03_bootstrap_lower_bound_fail(self) -> None:
        result = evaluate_component(
            case_rms_values=np.asarray([40.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            case_uncertainties=np.ones(8),
            strata=[(16, "regular")] * 8,
            canonical_component_name="synthetic_bootstrap_fail",
            mandatory_audits_valid=True,
        )
        self.assertGreaterEqual(result["R_c"], 10.0)
        self.assertLessEqual(result["L95_c"], 5.0)
        self.assertEqual(result["verdict"], "H1_SIGNAL_FAIL")

    def test_04_analytically_unexcited_exclusion(self) -> None:
        excited = np.asarray([True] * 8 + [False])
        targets = np.asarray([20.0] * 8 + [1.0e9])
        uncertainties = np.asarray([1.0] * 8 + [1.0e-12])
        result = evaluate_component(
            case_rms_values=targets[excited],
            case_uncertainties=uncertainties[excited],
            strata=[item for item, keep in zip(strata(9), excited) if keep],
            canonical_component_name="synthetic_unexcited_exclusion",
            mandatory_audits_valid=True,
        )
        self.assertEqual(result["eligible_case_count"], 8)
        self.assertEqual(result["R_c"], 20.0)
        self.assertEqual(
            case_label(analytically_excited=False, mandatory_audit_valid=True, ratio=1.0e21),
            "CASE_NOT_APPLICABLE_UNEXCITED",
        )

    def test_05_unequal_particle_count_equal_case_weighting(self) -> None:
        first = scalar_case_rms([1.0])
        second = scalar_case_rms(np.full(100, 3.0))
        self.assertAlmostEqual(equal_case_component_rms([first, second]), math.sqrt(5.0))

    def test_06_vector_rms_no_cartesian_divisor(self) -> None:
        self.assertEqual(vector_case_rms([[3.0, 4.0]]), 5.0)

    def test_07_unresolved_insufficient_eligible_cases(self) -> None:
        result = evaluate_component(
            case_rms_values=np.full(7, 20.0),
            case_uncertainties=np.ones(7),
            strata=strata(7),
            canonical_component_name="synthetic_insufficient",
            mandatory_audits_valid=True,
        )
        self.assertEqual(result["verdict"], "H1_SIGNAL_UNRESOLVED")

    def test_08_invalid_mandatory_audit_route(self) -> None:
        self.assertEqual(
            component_verdict(
                eligible_case_count=8,
                mandatory_audits_valid=False,
                point_ratio=100.0,
                bootstrap_lower_bound=100.0,
            ),
            "H1_SIGNAL_UNRESOLVED",
        )
        self.assertEqual(
            case_label(analytically_excited=True, mandatory_audit_valid=False, ratio=100.0),
            "CASE_UNRESOLVED",
        )

    def test_09_fixed_bootstrap_denominator(self) -> None:
        boot = stratified_group_bootstrap(
            case_rms_values=np.full(8, 1000.0),
            case_uncertainties=np.asarray([100.0] + [1.0] * 7),
            strata=[(16, "regular")] * 8,
            canonical_component_name="synthetic_fixed_denominator",
        )
        np.testing.assert_array_equal(boot, np.full(10_000, 10.0))

    def test_10_deterministic_repeated_execution(self) -> None:
        arguments = dict(
            case_rms_values=np.arange(8, dtype=np.float64) + 10.0,
            case_uncertainties=np.ones(8),
            strata=strata(8),
            canonical_component_name="synthetic_deterministic",
        )
        first = stratified_group_bootstrap(**arguments)
        second = stratified_group_bootstrap(**arguments)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(
            deterministic_seed("synthetic_deterministic"),
            deterministic_seed("synthetic_deterministic"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
