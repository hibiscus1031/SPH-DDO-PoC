#!/usr/bin/env python3
"""Generate DDO-01C-R reports and Python-only publication figures."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data/scaling_f1/ddo01cr_scaling_evidence.json"
REGISTRY_PATH = ROOT / "06_manifests/ddo01cr_case_registry.json"
REPORT_DIR = ROOT / "07_reports"
FIGURE_DIR = ROOT / "figures/ddo01cr"

COMPONENTS = [
    "interpolation_density",
    "density_rate",
    "pressure_gradient_acceleration",
    "viscosity_laplacian_acceleration",
    "total_acceleration",
]
LABELS = {
    "interpolation_density": "Interpolation/density",
    "density_rate": "Density rate",
    "pressure_gradient_acceleration": "Pressure gradient",
    "viscosity_laplacian_acceleration": "Viscosity/Laplacian",
    "total_acceleration": "Total acceleration",
}
TRACK_COLORS = {"D005": "#3B6FB6", "D010": "#65A9D7", "V050": "#D8873A", "V100": "#A64B3C"}
LAYOUT_STYLES = {"regular": "-", "jitter_0.05": "--"}

FIGURE_CONTRACT = {
    "core_conclusion": "H2 scaling is componentwise: density rate is disorder-robust, three acceleration channels are regular-scope only, and interpolation/density lacks systematic scaling.",
    "archetype": "quantitative grid",
    "target_output": "technical report; editable SVG/PDF plus 600-dpi TIFF and PNG preview",
    "backend": "Python/matplotlib only",
    "final_size_mm": [183, 122],
    "evidence_hierarchy": ["formal refinement and spectral families", "support-ratio scope", "paired disorder robustness", "relative effect size"],
    "statistics": "three matched replicates; CA-01 conservative bounds; medians are descriptive; formal gates use every local interval",
    "source_data": "data/scaling_f1/ddo01cr_scaling_evidence.csv and .json",
    "image_integrity": "vector-native quantitative plots; no raster image manipulation",
    "reviewer_risk": "log axes and small CA-01 intervals can visually hide uncertainty; verdict text and gate tables remain primary",
}


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return format(value, ".12g")
    return str(value)


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    base = FIGURE_DIR / stem
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def setup_style() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.titlesize": 7.2,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "legend.fontsize": 6.1,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.7,
        "legend.frameon": False,
    })


def panel_grid() -> tuple[plt.Figure, list[plt.Axes]]:
    fig, axes = plt.subplots(2, 3, figsize=(183 / 25.4, 122 / 25.4))
    flat = list(axes.flat)
    flat[-1].axis("off")
    return fig, flat[:5]


def grouped_response(cases: list[dict[str, Any]], component: str, family: str, track: str, layout: str, x_key: str) -> list[tuple[float, float, float, float]]:
    groups: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        if family in case["family_labels"] and case["track_template"] == track and case["layout_class"] == layout:
            groups[float(case[x_key])].append(case)
    result = []
    for x in sorted(groups):
        values = [case["components"][component] for case in groups[x]]
        result.append((
            x,
            float(median(item["normalized_target_Y"] for item in values)),
            min(item["Y_minus"] for item in values),
            max(item["Y_plus"] for item in values),
        ))
    return result


def plot_formal_family(evidence: dict[str, Any], registry: dict[str, Any], family: str, stem: str) -> None:
    x_key = "support_h" if family == "REFINEMENT_H" else "kh"
    xlabel = "Support radius, h" if family == "REFINEMENT_H" else "Spectral coordinate, kh"
    fig, axes = panel_grid()
    for index, (component, ax) in enumerate(zip(COMPONENTS, axes)):
        for track in registry["mandatory_component_tracks"][component]:
            for layout in ("regular", "jitter_0.05"):
                series = grouped_response(evidence["cases"], component, family, track, layout, x_key)
                if not series:
                    continue
                x = np.array([row[0] for row in series])
                y = np.array([row[1] for row in series])
                lo = np.array([row[2] for row in series])
                hi = np.array([row[3] for row in series])
                label = f"{track}, {'regular' if layout == 'regular' else 'jitter'}"
                ax.plot(x, y, marker="o", ms=2.8, lw=1.0, linestyle=LAYOUT_STYLES[layout], color=TRACK_COLORS[track], label=label)
                ax.fill_between(x, lo, hi, color=TRACK_COLORS[track], alpha=0.10, linewidth=0)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Normalized defect, Y")
        verdict = evidence["formal_h2"][component]["formal_families"][f"{family}|regular"]["verdict"]
        jitter = evidence["formal_h2"][component]["formal_families"][f"{family}|jitter_0.05"]["verdict"]
        ax.set_title(f"{LABELS[component]}\nregular {verdict}; jitter {jitter}")
        ax.text(-0.18, 1.06, chr(ord("a") + index), transform=ax.transAxes, fontweight="bold", fontsize=8)
        ax.grid(True, which="major", color="#D9D9D9", lw=0.4)
    handles, labels = axes[-1].get_legend_handles_labels()
    legend_ax = fig.axes[-1]
    legend_ax.axis("off")
    legend_ax.legend(handles, labels, loc="center", ncol=1, title="Track and layout")
    fig.suptitle(f"{'Refinement' if family == 'REFINEMENT_H' else 'Spectral'} scaling at canonical h/dx = 4", fontsize=8.2, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    save_figure(fig, stem)


def plot_support(evidence: dict[str, Any]) -> None:
    relevant = {
        "interpolation_density": ["D010"], "density_rate": ["V100"],
        "pressure_gradient_acceleration": ["D010"], "viscosity_laplacian_acceleration": ["V100"],
        "total_acceleration": ["D010", "V100"],
    }
    fig, axes = panel_grid()
    for index, (component, ax) in enumerate(zip(COMPONENTS, axes)):
        for track in relevant[component]:
            for layout in ("regular", "jitter_0.05"):
                series = grouped_response(evidence["cases"], component, "SUPPORT_RATIO_HDX", track, layout, "support_over_dx")
                x = np.array([row[0] for row in series])
                y = np.array([row[1] for row in series])
                lo = np.array([row[2] for row in series])
                hi = np.array([row[3] for row in series])
                ax.plot(x, y, marker="o", ms=2.8, lw=1.0, linestyle=LAYOUT_STYLES[layout], color=TRACK_COLORS[track], label=f"{track}, {layout}")
                ax.fill_between(x, lo, hi, color=TRACK_COLORS[track], alpha=0.10, linewidth=0)
        ax.set_yscale("log")
        ax.set_xticks([2, 3, 4, 5])
        ax.set_xlabel("Support ratio, h/dx")
        ax.set_ylabel("Normalized defect, Y")
        ax.set_title(LABELS[component])
        ax.text(-0.18, 1.06, chr(ord("a") + index), transform=ax.transAxes, fontweight="bold", fontsize=8)
        ax.grid(True, axis="y", color="#D9D9D9", lw=0.4)
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.axes[-1].axis("off")
    fig.axes[-1].legend(handles, labels, loc="center", title="DESCRIPTIVE_SCOPE_DIAGNOSTIC")
    fig.suptitle("Support-ratio scope diagnostic (no expected sign; not an H2 gate)", fontsize=8.2, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    save_figure(fig, "support_ratio_diagnostics")


def plot_disorder(evidence: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(183 / 25.4, 92 / 25.4))
    data = []
    for component in COMPONENTS:
        ratios = [item["jitter_to_regular_ratio"] for item in evidence["regular_vs_disorder"]["components"][component]["pair_records"] if item.get("jitter_to_regular_ratio") is not None]
        data.append(ratios)
    positions = np.arange(1, len(COMPONENTS) + 1)
    boxes = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True, showfliers=False, medianprops={"color": "#202020", "linewidth": 1.1})
    colors = ["#B9CBE5", "#9CC7B8", "#E5C29E", "#D9AEAA", "#C7B6D9"]
    for patch, color in zip(boxes["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor("#555555")
    for pos, ratios in zip(positions, data):
        x = np.linspace(pos - 0.18, pos + 0.18, len(ratios))
        ax.scatter(x, ratios, s=5, color="#555555", alpha=0.28, linewidths=0)
    ax.axhline(1.0, color="#333333", lw=0.8, linestyle="--")
    ax.set_yscale("log")
    ax.set_xticks(positions, [LABELS[c] for c in COMPONENTS], rotation=18, ha="right")
    ax.set_ylabel("Jitter / regular normalized defect")
    ax.set_title("Matched regular–disorder robustness (102 case pairs)")
    ax.grid(True, axis="y", which="major", color="#D9D9D9", lw=0.4)
    fig.tight_layout()
    save_figure(fig, "disorder_robustness")


def plot_relative_effect(evidence: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(183 / 25.4, 92 / 25.4))
    positions, data, colors, labels = [], [], [], []
    position = 1.0
    for component in COMPONENTS:
        for layout, color in (("regular", "#6C8EBF"), ("jitter_0.05", "#D79A63")):
            values = [case["components"][component]["relative_effect_E_rel"] for case in evidence["cases"] if case["layout_class"] == layout]
            positions.append(position)
            data.append(values)
            colors.append(color)
            labels.append(f"{LABELS[component]}\n{'regular' if layout == 'regular' else 'jitter'}")
            position += 0.72
        position += 0.45
    boxes = ax.boxplot(data, positions=positions, widths=0.48, patch_artist=True, showfliers=False, medianprops={"color": "#202020", "linewidth": 1.0})
    for patch, color in zip(boxes["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.72)
        patch.set_edgecolor("#555555")
    ax.set_yscale("log")
    ax.set_xticks(positions, labels, rotation=25, ha="right")
    ax.set_ylabel("Relative defect effect, E_rel")
    ax.set_title("Relative defect effect size (DESCRIPTIVE_NOT_H2_GATE)")
    ax.grid(True, axis="y", which="major", color="#D9D9D9", lw=0.4)
    fig.tight_layout()
    save_figure(fig, "relative_effect")


def family_rows(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for component in COMPONENTS:
        for key, result in evidence["formal_h2"][component]["formal_families"].items():
            family, layout = key.split("|")
            track_margins = [track["C_t"] - track["D_t"] for track in result["tracks"].values() if track["C_t"] is not None]
            slopes = {name: track["representative_slope_descriptive"] for name, track in result["tracks"].items()}
            rows.append({
                "component": component, "family": family, "layout": layout,
                "M_family": result["M_family"],
                "monotonicity_margin": None if result["M_family"] is None else result["M_family"] - 0.75,
                "minimum_dispersion_margin_C_minus_D": min(track_margins) if track_margins else None,
                "representative_track_slopes_descriptive": json.dumps(slopes, sort_keys=True),
                "verdict": result["verdict"], "reason": result["reason"],
            })
    return rows


def write_ledger(evidence: dict[str, Any]) -> None:
    path = REPORT_DIR / "ddo01cr_component_h2_ledger.csv"
    columns = [
        "component", "raw_target_rms_min", "raw_target_rms_max", "normalized_Y_min", "normalized_Y_max",
        "U_num_max", "refinement_regular", "refinement_jitter", "spectral_regular", "spectral_jitter",
        "refinement_regular_M", "refinement_jitter_M", "spectral_regular_M", "spectral_jitter_M",
        "minimum_formal_monotonicity_margin", "minimum_formal_dispersion_margin_C_minus_D",
        "regular_scope", "jitter_scope", "component_h2_verdict", "formal_support_over_dx",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for component in COMPONENTS:
            values = [case["components"][component] for case in evidence["cases"]]
            formal = evidence["formal_h2"][component]
            ff = formal["formal_families"]
            results = list(ff.values())
            monotonicity_margins = [result["M_family"] - 0.75 for result in results if result["M_family"] is not None]
            dispersion_margins = [track["C_t"] - track["D_t"] for result in results for track in result["tracks"].values() if track["C_t"] is not None]
            writer.writerow({
                "component": component,
                "raw_target_rms_min": min(v["target_rms"] for v in values), "raw_target_rms_max": max(v["target_rms"] for v in values),
                "normalized_Y_min": min(v["normalized_target_Y"] for v in values), "normalized_Y_max": max(v["normalized_target_Y"] for v in values),
                "U_num_max": max(v["U_num"] for v in values),
                "refinement_regular": ff["REFINEMENT_H|regular"]["verdict"], "refinement_jitter": ff["REFINEMENT_H|jitter_0.05"]["verdict"],
                "spectral_regular": ff["SPECTRAL_KH|regular"]["verdict"], "spectral_jitter": ff["SPECTRAL_KH|jitter_0.05"]["verdict"],
                "refinement_regular_M": ff["REFINEMENT_H|regular"]["M_family"], "refinement_jitter_M": ff["REFINEMENT_H|jitter_0.05"]["M_family"],
                "spectral_regular_M": ff["SPECTRAL_KH|regular"]["M_family"], "spectral_jitter_M": ff["SPECTRAL_KH|jitter_0.05"]["M_family"],
                "minimum_formal_monotonicity_margin": min(monotonicity_margins),
                "minimum_formal_dispersion_margin_C_minus_D": min(dispersion_margins),
                "regular_scope": formal["regular_scope"], "jitter_scope": formal["jitter_scope"],
                "component_h2_verdict": formal["component_verdict"], "formal_support_over_dx": 4.0,
            })


def write_reports(evidence: dict[str, Any]) -> None:
    rows = family_rows(evidence)
    table = ["| Component | Family | Layout | M_family | M-0.75 | min(C-D) | Descriptive track median slopes | Verdict |", "|---|---|---|---:|---:|---:|---|---|"]
    for row in rows:
        table.append(f"| {LABELS[row['component']]} | {row['family']} | {row['layout']} | {fmt(row['M_family'])} | {fmt(row['monotonicity_margin'])} | {fmt(row['minimum_dispersion_margin_C_minus_D'])} | `{row['representative_track_slopes_descriptive']}` | `{row['verdict']}` |")
    component_table = ["| Component | Regular scope | Jitter scope | Component result |", "|---|---|---|---|"]
    for component in COMPONENTS:
        result = evidence["formal_h2"][component]
        component_table.append(f"| {LABELS[component]} | `{result['regular_scope']}` | `{result['jitter_scope']}` | `{result['component_verdict']}` |")
    scaling = f"""# DDO-01C-R controlled spatial-defect scaling report

## Project result

`{evidence['terminal_status']}`

All 204 fresh registered cases passed every mandatory CA-01 numerical/reference audit, and every formal log response was admissible. The project result is componentwise rather than global.

{chr(10).join(component_table)}

Every PASS is restricted to the sampled F1 domain and canonical formal support ratio `h/dx=4`. It supports systematic scaling only; it does not establish H3-H6, learnability, architecture suitability, or corrected-solver convergence.

## Formal gate evidence

{chr(10).join(table)}

`M_family` uses equal scientific-track weighting. The formal monotonicity margin is `M_family-0.75`; the dispersion margin is `C_t-D_t`, reported conservatively as the minimum over mandatory tracks. A positive value supports the respective gate. Descriptive median local slopes are not fitted convergence orders and do not replace either gate.

## Numerical validity

- mandatory cases passed: `{evidence['aggregate_numerical']['mandatory_cases_passed']}/204`;
- maximum derivative discrepancy: `{fmt(evidence['aggregate_numerical']['derivative_discrepancy_max'])}`;
- maximum derivative gate fraction: `{fmt(evidence['aggregate_numerical']['derivative_gate_fraction_max'])}`;
- `U_num` range: `{fmt(evidence['aggregate_numerical']['U_num_min'])}` to `{fmt(evidence['aggregate_numerical']['U_num_max'])}`;
- maximum component-closure residual: `{fmt(evidence['aggregate_numerical']['component_closure_residual_max'])}`.

The independently rebuilt float32 graph was unavailable for 14 diagnostic cases because support-boundary rounding broke reciprocity. Those cases used the valid primary edge set cast to float32 solely for the explicitly non-gating precision-degradation diagnostic. Primary float64 topology, CA-01 `U_num`, formal targets, and H2 decisions were unchanged.

## Claim boundary

H2 FAIL for interpolation/density rejects systematic scaling under these formal families and sampled scope; it does not imply H3 FAIL. Regular-only acceleration-channel results retain the disorder limitation. No case, interval, or disorder failure was removed.
"""
    (REPORT_DIR / "ddo01cr_scaling_report.md").write_text(scaling)

    relative_lines = ["# DDO-01C-R relative defect effect-size report", "", "All values use `E_rel=T_jc/max(C_jc,U_round(j,c))` and are `DESCRIPTIVE_NOT_H2_GATE`. No threshold is introduced.", "", "| Component | Layout | Minimum | Median | Maximum |", "|---|---|---:|---:|---:|"]
    for component in COMPONENTS:
        for layout in ("regular", "jitter_0.05"):
            values = [case["components"][component]["relative_effect_E_rel"] for case in evidence["cases"] if case["layout_class"] == layout]
            relative_lines.append(f"| {LABELS[component]} | {layout} | {fmt(min(values))} | {fmt(median(values))} | {fmt(max(values))} |")
    relative_lines.extend(["", "Large values mean the defect is large relative to the matching continuum quantity or CA-01 roundoff floor. They do not change any H2 verdict."])
    (REPORT_DIR / "ddo01cr_relative_effect_report.md").write_text("\n".join(relative_lines) + "\n")

    support_lines = ["# DDO-01C-R support-ratio report", "", "Every result is `DESCRIPTIVE_SCOPE_DIAGNOSTIC`. No expected sign or H2 threshold applies.", "", "| Component | Track/layout | Median local slope | Minimum local slope | Maximum local slope |", "|---|---|---:|---:|---:|"]
    for component, groups in evidence["support_ratio_diagnostic"]["components"].items():
        for name, group in groups.items():
            slopes = [item["p"] for item in group["local_descriptive_slopes"] if item.get("p") is not None]
            support_lines.append(f"| {LABELS[component]} | {name} | {fmt(median(slopes))} | {fmt(min(slopes))} | {fmt(max(slopes))} |")
    support_lines.extend(["", "Support-ratio changes also change neighbor count; this diagnostic is not interpreted as an independent neighbor-count effect and cannot alter the canonical `h/dx=4` verdict."])
    (REPORT_DIR / "ddo01cr_support_ratio_report.md").write_text("\n".join(support_lines) + "\n")

    classes = {
        "H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT": "REGULAR_AND_DISORDER_SCALING_SUPPORTED",
        "H2_SCALING_PASS_REGULAR_SCOPE_ONLY": "REGULAR_ONLY_SCALING_SUPPORTED",
        "H2_SCALING_PASS_REGULAR_SCOPE_DISORDER_UNRESOLVED": "REGULAR_SCALING_SUPPORTED_DISORDER_UNRESOLVED",
        "H2_SCALING_FAIL_REGULAR_SCOPE": "NO_SYSTEMATIC_SCALING_SUPPORTED",
        "H2_SCALING_UNRESOLVED": "SCALING_UNRESOLVED",
    }
    disorder_lines = ["# DDO-01C-R disorder robustness report", "", "Regular and 5% jitter cases are compared through 102 prospectively paired identities. No disorder failure was deleted.", "", "| Component | Interaction class | Median jitter/regular Y | Minimum | Maximum |", "|---|---|---:|---:|---:|"]
    for component in COMPONENTS:
        d = evidence["regular_vs_disorder"]["components"][component]
        verdict = evidence["formal_h2"][component]["component_verdict"]
        disorder_lines.append(f"| {LABELS[component]} | `{classes[verdict]}` | {fmt(d['median_jitter_to_regular_ratio'])} | {fmt(d['minimum_jitter_to_regular_ratio'])} | {fmt(d['maximum_jitter_to_regular_ratio'])} |")
    disorder_lines.extend(["", "The paired response ratios are descriptive effect sizes. Formal robustness is determined only by the separately frozen refinement and spectral gates for the jitter layout."])
    (REPORT_DIR / "ddo01cr_disorder_robustness_report.md").write_text("\n".join(disorder_lines) + "\n")

    decision = f"""# DDO-01C-R next-stage decision

## Decision

Assign:

`{evidence['terminal_status']}`

Density rate receives `H2_SIGNAL_SCALING_PASS_CANONICAL_SUPPORT`. Pressure-gradient, viscosity/Laplacian, and total-acceleration defects receive `H2_SCALING_PASS_REGULAR_SCOPE_ONLY`. Interpolation/density receives `H2_SCALING_FAIL_REGULAR_SCOPE`.

This is a componentwise partial qualification over the sampled F1 domain at formal `h/dx=4`. H2 FAIL does not imply H3 FAIL.

## Authorization boundary

DDO-01C-R is complete, but DDO-01D is not automatically authorized and was not executed. A separate authorization must decide whether and how a balanced atlas should proceed while preserving the componentwise scope and disorder failures.

H3-H6, F2-F4 balanced-atlas construction, PCA/SVD, nearest-neighbor or regression prediction, MLP, GNN, Transformer, optimizer, time integration, rollout, solver-in-the-loop, high-resolution SPH truth, LCDF_03, and LCDF_10 were not executed.
"""
    (REPORT_DIR / "ddo01cr_next_stage_decision.md").write_text(decision)


def main() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text())
    registry = json.loads(REGISTRY_PATH.read_text())
    if evidence["case_count"] != 204 or evidence["terminal_status"] != "DDO01CR_COMPONENTWISE_SCALING_PARTIALLY_QUALIFIED":
        raise RuntimeError("unexpected frozen DDO-01C-R evidence")
    setup_style()
    write_ledger(evidence)
    write_reports(evidence)
    plot_formal_family(evidence, registry, "REFINEMENT_H", "refinement_scaling")
    plot_formal_family(evidence, registry, "SPECTRAL_KH", "spectral_scaling")
    plot_support(evidence)
    plot_disorder(evidence)
    plot_relative_effect(evidence)
    print(json.dumps({
        "figure_contract": FIGURE_CONTRACT,
        "reports_created": 6,
        "figure_families_created": 5,
        "formats_per_figure": ["svg", "pdf", "tiff", "png"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
