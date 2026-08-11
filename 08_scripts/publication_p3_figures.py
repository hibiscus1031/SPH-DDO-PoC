#!/usr/bin/env python3
"""Publication P3 main-figure assembly from frozen SPH-DDO artifacts.

Python is the exclusive visual backend. The script reads frozen ledgers and
metric files, applies only display transformations, and writes SVG, PDF,
600-dpi TIFF, and PNG previews. It does not recompute scientific metrics.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams.update(
    {
        "font.size": 7,
        "axes.titlesize": 7.5,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "axes.linewidth": 0.7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "legend.frameon": False,
        "legend.fontsize": 6.2,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "main"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#356E9C"
BLUE_LIGHT = "#DCEAF3"
TEAL = "#2A8C82"
TEAL_LIGHT = "#D9EEE9"
ORANGE = "#D9782D"
ORANGE_LIGHT = "#F5E2D3"
PURPLE = "#745C97"
PURPLE_LIGHT = "#E9E2F0"
GREY = "#6F7478"
GREY_LIGHT = "#E7E8E9"
DARK = "#252A2D"
RED = "#B54A45"
PASS_COLOR = BLUE
FAIL_COLOR = ORANGE
PASS_HATCH = ""
FAIL_HATCH = "////"

COMPONENTS = [
    "density_rate",
    "pressure_gradient_acceleration",
    "viscosity_laplacian_acceleration",
]
COMP_SHORT = {
    "density_rate": "Density rate",
    "pressure_gradient_acceleration": "Pressure gradient",
    "viscosity_laplacian_acceleration": "Viscosity Laplacian",
    "interpolation_density": "Interpolation density",
    "total_acceleration": "Total acceleration",
}
COMP_TINY = {
    "density_rate": "Density\nrate",
    "pressure_gradient_acceleration": "Pressure\ngradient",
    "viscosity_laplacian_acceleration": "Viscosity\nLaplacian",
}


def read_csv(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


H1 = read_csv("07_reports/ddo01br_component_h1_ledger.csv")
H2 = read_csv("07_reports/ddo01cr_component_h2_ledger.csv")
H2_EVIDENCE = read_csv("data/scaling_f1/ddo01cr_scaling_evidence.csv")
INITIAL = read_json("data/identifiability/ddo01e_metrics.json")
FRESH = read_json("data/ddo02b_identifiability/ddo02b_metrics.json")
INITIAL_FIG = read_csv("data/identifiability/ddo01e_figure_source_data.csv")


def mm_to_in(mm: float) -> float:
    return mm / 25.4


def panel_label(ax, label: str, x: float = -0.08, y: float = 1.03) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="left",
        va="bottom",
        color=DARK,
    )


def clean_axis(ax) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def rounded_box(
    ax,
    xy,
    width,
    height,
    text,
    facecolor=GREY_LIGHT,
    edgecolor=GREY,
    fontsize=7,
    weight="normal",
    textcolor=DARK,
    linewidth=0.8,
    radius=0.02,
):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=textcolor,
        linespacing=1.25,
    )
    return box


def arrow(ax, start, end, color=GREY, linewidth=1.1, style="-|>") -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            transform=ax.transAxes,
            arrowstyle=style,
            mutation_scale=9,
            linewidth=linewidth,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def save_figure(fig, number: int) -> None:
    base = OUT / f"figure{number:02d}"
    fig.savefig(base.with_suffix(".svg"))
    fig.savefig(base.with_suffix(".pdf"))
    fig.savefig(
        base.with_suffix(".tiff"),
        dpi=600,
        pil_kwargs={"compression": "tiff_lzw"},
    )
    fig.savefig(base.with_suffix(".png"), dpi=300)
    plt.close(fig)


def metric_bundle(metrics: dict, component: str) -> dict[str, tuple[float, float, str]]:
    row = metrics["results"]["C3/L3"]["components"][component]
    return {
        "NN median": (float(row["dnn_median"]), 0.25, "upper"),
        "NN P90": (float(row["dnn_p90"]), 0.60, "upper"),
        "Cvar upper 95%": (float(row["cvar_upper95"]), 0.35, "upper"),
        "Oracle NRMSE": (float(row["oracle_nrmse"]), 0.50, "upper"),
        "Oracle improvement": (float(row["baseline_improvement"]), 0.20, "lower"),
        "Worst-family NRMSE": (float(row["max_family_nrmse"]), 0.75, "upper"),
        "Coverage": (float(row["coverage"]), 0.90, "lower"),
    }


def metric_pass(value: float, limit: float, direction: str) -> bool:
    return value <= limit if direction == "upper" else value >= limit


def fmt_metric(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) < 0.001:
        return f"{value:.2e}"
    if abs(value) < 0.01:
        return f"{value:.4f}"
    if abs(value) < 10:
        return f"{value:.3f}"
    return f"{value:.2f}"


def draw_pass_matrix(ax, values: np.ndarray, xlabels, ylabels, annotations=None) -> None:
    cmap = mcolors.ListedColormap([FAIL_COLOR, PASS_COLOR])
    ax.imshow(values.astype(int), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(xlabels)), labels=xlabels)
    ax.set_yticks(range(len(ylabels)), labels=ylabels)
    ax.tick_params(length=0)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            txt = annotations[i][j] if annotations is not None else ("P" if values[i, j] else "N")
            ax.text(j, i, txt, ha="center", va="center", color="white", fontsize=6.1, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(xlabels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(ylabels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)


def figure01() -> None:
    fig = plt.figure(figsize=(mm_to_in(183), mm_to_in(125)), layout="constrained")
    gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1], height_ratios=[0.9, 1.1])

    ax = fig.add_subplot(gs[0, 0]); clean_axis(ax); panel_label(ax, "a")
    ax.set_title("Fixed-time spatial defect", loc="left", fontweight="bold")
    ax.text(
        0.5, 0.60,
        r"$d_h^*=\mathcal{R}_h\mathcal{L}(q^*)-\mathcal{L}_h(\mathcal{R}_h q^*)$",
        transform=ax.transAxes, ha="center", va="center", fontsize=12, color=BLUE,
    )
    ax.text(
        0.5, 0.30,
        "sampled analytical continuum operator\nminus low-cost SPH spatial operator",
        transform=ax.transAxes, ha="center", va="center", fontsize=7, color=DARK,
    )
    ax.text(
        0.5, 0.08, "Excludes time integration, next-state prediction, and rollout error",
        transform=ax.transAxes, ha="center", va="center", fontsize=6.3, color=GREY,
    )

    ax = fig.add_subplot(gs[0, 1]); clean_axis(ax); panel_label(ax, "b")
    ax.set_title("Observable/reference firewall", loc="left", fontweight="bold")
    rounded_box(ax, (0.02, 0.53), 0.31, 0.28, "Analytical reference\nclosed-form + audit", BLUE_LIGHT, BLUE)
    rounded_box(ax, (0.67, 0.53), 0.31, 0.28, "Deployment\nobservables\nreference-free only", TEAL_LIGHT, TEAL, fontsize=6.2)
    rounded_box(ax, (0.35, 0.08), 0.30, 0.27, "Defect target\nreference − SPH", PURPLE_LIGHT, PURPLE)
    arrow(ax, (0.22, 0.52), (0.43, 0.35), BLUE)
    arrow(ax, (0.78, 0.52), (0.57, 0.35), TEAL)
    ax.plot([0.50, 0.50], [0.42, 0.91], color=RED, lw=1.2, ls="--", transform=ax.transAxes)
    ax.text(0.50, 0.94, "no target leakage", transform=ax.transAxes, ha="center", color=RED, fontsize=6.3)

    ax = fig.add_subplot(gs[1, 0]); clean_axis(ax); panel_label(ax, "c")
    ax.set_title("Pre-learning qualification hierarchy", loc="left", fontweight="bold")
    labels = [
        ("H1", "signal resolvability", "qualified", BLUE_LIGHT, BLUE),
        ("H2", "controlled scaling", "component/scope dependent", BLUE_LIGHT, BLUE),
        ("H3", "operational identifiability", "fresh criteria not satisfied", ORANGE_LIGHT, ORANGE),
        ("H4", "locality", "not interpreted / not qualified", GREY_LIGHT, GREY),
        ("H5", "representation learning", "not initiated / not authorized", GREY_LIGHT, GREY),
        ("H6", "generalization", "not initiated / not authorized", GREY_LIGHT, GREY),
    ]
    y = np.linspace(0.82, 0.08, len(labels))
    for i, ((h, name, status, fc, ec), yi) in enumerate(zip(labels, y)):
        rounded_box(ax, (0.03, yi), 0.93, 0.105, f"{h}   {name}     {status}", fc, ec, fontsize=6.5)
        if i < len(labels) - 1:
            arrow(ax, (0.50, yi), (0.50, y[i + 1] + 0.105), GREY, linewidth=0.8)

    ax = fig.add_subplot(gs[1, 1]); clean_axis(ax); panel_label(ax, "d")
    ax.set_title("Tested stopping logic", loc="left", fontweight="bold")
    rounded_box(ax, (0.04, 0.66), 0.42, 0.20, "Three primary mappings\nfresh H3 requalification", BLUE_LIGHT, BLUE, weight="bold")
    rounded_box(ax, (0.54, 0.66), 0.42, 0.20, "None satisfied all\npreregistered criteria", ORANGE_LIGHT, ORANGE, weight="bold")
    arrow(ax, (0.46, 0.76), (0.54, 0.76), ORANGE)
    rounded_box(ax, (0.04, 0.30), 0.42, 0.18, "Locality\nnot interpreted", GREY_LIGHT, GREY)
    rounded_box(ax, (0.54, 0.30), 0.42, 0.18, "No neural stage\ninitiated", GREY_LIGHT, GREY)
    arrow(ax, (0.75, 0.65), (0.25, 0.49), GREY)
    arrow(ax, (0.75, 0.65), (0.75, 0.49), GREY)
    ax.text(
        0.50, 0.08, "Conclusion is specific to the tested instantaneous observable route",
        transform=ax.transAxes, ha="center", color=DARK, fontsize=6.5, fontweight="bold",
    )
    save_figure(fig, 1)


def figure02() -> None:
    fig = plt.figure(figsize=(mm_to_in(183), mm_to_in(145)), layout="constrained")
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.08], width_ratios=[0.94, 1.06])

    ax = fig.add_subplot(gs[0, 0]); panel_label(ax, "a")
    labels = [COMP_SHORT[r["component"]] for r in H1][::-1]
    rvals = np.array([float(r["R_c"]) for r in H1][::-1])
    lvals = np.array([float(r["L95_c"]) for r in H1][::-1])
    y = np.arange(len(labels))
    ax.set_xscale("log")
    ax.scatter(rvals, y + 0.10, color=BLUE, marker="o", s=25, label=r"$R_c$")
    ax.scatter(lvals, y - 0.10, color=TEAL, marker="s", s=22, label=r"$L_{95,c}$")
    ax.axvline(10, color=BLUE, lw=1, ls="--")
    ax.axvline(5, color=TEAL, lw=1, ls=":")
    ax.set_yticks(y, labels)
    ax.set_xlabel("Defect / qualified numerical-reference uncertainty")
    ax.set_title("Signal resolvability", loc="left", fontweight="bold")
    ax.legend(loc="lower right", ncol=2)
    ax.text(0.02, 0.02, "Not a physical signal-to-noise ratio", transform=ax.transAxes, fontsize=6.2, color=GREY)

    ax = fig.add_subplot(gs[0, 1]); panel_label(ax, "b")
    comps = [r["component"] for r in H2]
    cols = ["refinement_regular", "refinement_jitter", "spectral_regular", "spectral_jitter"]
    values = np.array([[r[c] == "PASS" for c in cols] for r in H2], dtype=bool)
    draw_pass_matrix(
        ax, values,
        ["Refine\nregular", "Refine\ndisorder", "Spectral\nregular", "Spectral\ndisorder"],
        [COMP_SHORT[c] for c in comps],
    )
    ax.set_title(r"Controlled scaling at $h/\Delta x=4$", loc="left", fontweight="bold")
    ax.text(0.00, -0.18, "P: passed     N: did not satisfy criteria", transform=ax.transAxes, fontsize=6.2, color=GREY)

    ax = fig.add_subplot(gs[1, 0]); panel_label(ax, "c")
    rows = [
        r for r in H2_EVIDENCE
        if r["component"] == "density_rate" and r["track"] == "V100"
        and "REFINEMENT_H" in r["families"] and r["log_response_admissible"] == "True"
    ]
    for layout, color, marker, ls in [("regular", BLUE, "o", "-"), ("jitter_0.05", TEAL, "s", "--")]:
        for rep in ["0", "1", "2"]:
            rr = sorted([r for r in rows if r["layout"] == layout and r["replicate"] == rep], key=lambda x: float(x["h"]))
            ax.plot(
                [float(r["h"]) for r in rr], [float(r["normalized_Y"]) for r in rr],
                color=color, marker=marker, ls=ls, lw=1.0, ms=3.0, alpha=0.75,
                label=("regular" if layout == "regular" else "5% disorder") if rep == "0" else None,
            )
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"Smoothing length $h$")
    ax.set_ylabel(r"Normalized density-rate defect $Y_{jc}$")
    ax.set_title("Density-rate refinement tracks", loc="left", fontweight="bold")
    ax.legend(loc="lower right")
    ax.text(0.02, 0.96, "V100; three matched replicates", transform=ax.transAxes, va="top", fontsize=6.1, color=GREY)

    ax = fig.add_subplot(gs[1, 1]); panel_label(ax, "d")
    momentum = [
        "pressure_gradient_acceleration",
        "viscosity_laplacian_acceleration",
        "total_acceleration",
    ]
    lookup = {r["component"]: r for r in H2}
    x = np.arange(len(momentum)); width = 0.34
    regular = [float(lookup[c]["refinement_regular_M"]) for c in momentum]
    disorder = [float(lookup[c]["refinement_jitter_M"]) for c in momentum]
    ax.bar(x - width / 2, regular, width, color=BLUE, edgecolor=DARK, lw=0.5, label="regular")
    ax.bar(x + width / 2, disorder, width, color=ORANGE_LIGHT, edgecolor=ORANGE, hatch="////", lw=0.7, label="5% disorder")
    ax.axhline(0.75, color=DARK, lw=1, ls="--", label="criterion 0.75")
    ax.set_xticks(x, ["Pressure", "Viscosity", "Total\n(derived)"])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Refinement monotonicity fraction")
    ax.set_title("Momentum-component disorder breakdown", loc="left", fontweight="bold")
    ax.legend(loc="upper right", ncol=3)
    for j, value in enumerate(disorder):
        ax.text(j + width / 2, max(value, 0.018), f"{value:.1f}", ha="center", va="bottom", fontsize=5.8, color=ORANGE)
    ax.text(0.02, 0.04, "Local slopes remain descriptive, not convergence orders", transform=ax.transAxes, fontsize=6.1, color=GREY)
    save_figure(fig, 2)


def figure03() -> None:
    fig = plt.figure(figsize=(mm_to_in(183), mm_to_in(135)), layout="constrained")
    gs = fig.add_gridspec(2, 2, width_ratios=[0.9, 1.1], height_ratios=[0.92, 1.08])

    ax = fig.add_subplot(gs[0, 0]); clean_axis(ax); panel_label(ax, "a")
    ax.set_title("Mechanism-stratified development atlas", loc="left", fontweight="bold")
    families = [
        ("single-mode", BLUE_LIGHT, BLUE),
        ("multimode", TEAL_LIGHT, TEAL),
        ("directional / mechanism", PURPLE_LIGHT, PURPLE),
        ("controlled disorder", ORANGE_LIGHT, ORANGE),
    ]
    for i, (name, fc, ec) in enumerate(families):
        y = 0.73 - i * 0.19
        rounded_box(ax, (0.08, y), 0.68, 0.12, name, fc, ec, fontsize=6.8, weight="bold")
        ax.text(0.83, y + 0.06, "128", transform=ax.transAxes, ha="center", va="center", fontsize=8, color=ec, fontweight="bold")
    ax.text(0.83, 0.90, "cases", transform=ax.transAxes, ha="center", fontsize=6.2, color=GREY)
    ax.text(0.50, 0.04, "512 complete cases; balanced before target evaluation", transform=ax.transAxes, ha="center", fontsize=6.4, color=DARK)

    ax = fig.add_subplot(gs[0, 1]); clean_axis(ax); panel_label(ax, "b")
    ax.set_title("Field-lineage-held-out diagnostic folds", loc="left", fontweight="bold")
    rounded_box(ax, (0.03, 0.65), 0.20, 0.20, "target-free\nlineage key", BLUE_LIGHT, BLUE, weight="bold")
    for i in range(5):
        x0 = 0.32 + i * 0.13
        rounded_box(ax, (x0, 0.68), 0.09, 0.14, f"fold\n{i}", GREY_LIGHT if i else ORANGE_LIGHT, GREY if i else ORANGE, fontsize=6.0)
    arrow(ax, (0.23, 0.75), (0.32, 0.75), GREY)
    rounded_box(ax, (0.16, 0.18), 0.68, 0.22, "one fold held out\nother four supply neighbours and oracle fit", TEAL_LIGHT, TEAL, fontsize=7)
    for i in range(5):
        arrow(ax, (0.365 + i * 0.13, 0.67), (0.50, 0.40), GREY, linewidth=0.65)
    ax.text(0.50, 0.05, "No particle-level split; cases and folds receive equal weight", transform=ax.transAxes, ha="center", fontsize=6.3, color=GREY)

    ax = fig.add_subplot(gs[1, 0]); clean_axis(ax); panel_label(ax, "c")
    ax.set_title("Observable-to-ambiguity diagnostic", loc="left", fontweight="bold")
    rounded_box(ax, (0.01, 0.64), 0.28, 0.20, "deployment-compatible\nobservables", TEAL_LIGHT, TEAL, fontsize=5.7, weight="bold")
    rounded_box(ax, (0.36, 0.64), 0.28, 0.20, "nearest points in\nfeature space", BLUE_LIGHT, BLUE, fontsize=5.7, weight="bold")
    rounded_box(ax, (0.71, 0.64), 0.28, 0.20, "compare fixed-time\ndefects", PURPLE_LIGHT, PURPLE, fontsize=5.7, weight="bold")
    arrow(ax, (0.29, 0.74), (0.36, 0.74), GREY)
    arrow(ax, (0.64, 0.74), (0.71, 0.74), GREY)
    for x0, label in zip([0.02, 0.365, 0.71], ["NN\ndisagreement", "conditional\nvariance", "non-neural\noracle"]):
        rounded_box(ax, (x0, 0.25), 0.27, 0.16, label, GREY_LIGHT, GREY, fontsize=5.7)
        arrow(ax, (0.50, 0.63), (x0 + 0.12, 0.42), GREY, linewidth=0.7)
    ax.text(0.50, 0.06, "Coverage is assessed independently from conditional ambiguity", transform=ax.transAxes, ha="center", fontsize=6.3, color=DARK)

    ax = fig.add_subplot(gs[1, 1]); panel_label(ax, "d")
    metric_names = list(metric_bundle(INITIAL, COMPONENTS[0]).keys())
    matrix = np.array(
        [
            [metric_pass(*metric_bundle(INITIAL, c)[m]) for m in metric_names]
            for c in COMPONENTS
        ],
        dtype=bool,
    )
    draw_pass_matrix(ax, matrix, [m.replace(" ", "\n", 1) for m in metric_names], [COMP_SHORT[c] for c in COMPONENTS])
    ax.set_title("Initial operational-identifiability summary", loc="left", fontweight="bold")
    ax.text(0.00, -0.21, "P/N labels preserve the decision encoding in grayscale", transform=ax.transAxes, fontsize=6.0, color=GREY)
    save_figure(fig, 3)


def figure04() -> None:
    fig = plt.figure(figsize=(mm_to_in(183), mm_to_in(150)), layout="constrained")
    gs = fig.add_gridspec(2, 2, width_ratios=[0.94, 1.06], height_ratios=[0.92, 1.08])
    x = np.arange(len(COMPONENTS))

    ax = fig.add_subplot(gs[0, 0]); panel_label(ax, "a")
    med = [INITIAL["results"]["C3/L3"]["components"][c]["dnn_median"] for c in COMPONENTS]
    p90 = [INITIAL["results"]["C3/L3"]["components"][c]["dnn_p90"] for c in COMPONENTS]
    ax.set_yscale("log")
    ax.scatter(x - 0.08, med, color=BLUE, marker="o", s=28, label="NN median")
    ax.scatter(x + 0.08, p90, color=ORANGE, marker="s", s=26, label="NN P90")
    ax.axhline(0.25, color=BLUE, lw=0.9, ls="--")
    ax.axhline(0.60, color=ORANGE, lw=0.9, ls=":")
    ax.set_xticks(x, [COMP_TINY[c] for c in COMPONENTS])
    ax.set_ylabel("Nearest-neighbour disagreement ratio")
    ax.set_title("Initial disagreement retains favorable medians", loc="left", fontweight="bold")
    ax.legend(loc="upper left")

    ax = fig.add_subplot(gs[0, 1]); panel_label(ax, "b")
    cvar = [INITIAL["results"]["C3/L3"]["components"][c]["cvar_upper95"] for c in COMPONENTS]
    oracle = [INITIAL["results"]["C3/L3"]["components"][c]["oracle_nrmse"] for c in COMPONENTS]
    width = 0.34
    ax.bar(x - width / 2, np.array(cvar) / 0.35, width, color=PURPLE_LIGHT, edgecolor=PURPLE, label="Cvar upper 95% / 0.35")
    ax.bar(x + width / 2, np.array(oracle) / 0.50, width, color=TEAL_LIGHT, edgecolor=TEAL, hatch="..", label="Oracle NRMSE / 0.50")
    ax.axhline(1, color=DARK, lw=1, ls="--")
    ax.set_xticks(x, [COMP_TINY[c] for c in COMPONENTS])
    ax.set_ylabel("Value / frozen upper limit")
    ax.set_title("Conditional variance and oracle error", loc="left", fontweight="bold")
    ax.legend(loc="upper left")
    ax.set_ylim(0, 4.6)
    for j, (cv, oe) in enumerate(zip(cvar, oracle)):
        ax.text(j - width / 2, cv / 0.35 + 0.05, fmt_metric(cv), ha="center", fontsize=5.6, rotation=90)
        ax.text(j + width / 2, oe / 0.50 + 0.05, fmt_metric(oe), ha="center", fontsize=5.6, rotation=90)

    ax = fig.add_subplot(gs[1, 0]); panel_label(ax, "c")
    fams = ["F1", "F2", "F3", "F4"]
    mat = []
    for c in COMPONENTS:
        row = INITIAL["results"]["C3/L3"]["components"][c]
        oracle_name = row["best_oracle"]
        mat.append([row["oracles"][oracle_name]["family_nrmse"][f] for f in fams])
    mat = np.array(mat)
    im = ax.imshow(mat, cmap="YlOrBr", vmin=0.25, vmax=max(1.5, float(mat.max())), aspect="auto")
    ax.set_xticks(range(4), ["single-mode", "multimode", "directional", "disorder"], rotation=18, ha="right")
    ax.set_yticks(range(3), [COMP_SHORT[c] for c in COMPONENTS])
    ax.set_title("Best-oracle family robustness", loc="left", fontweight="bold")
    for i in range(3):
        for j in range(4):
            ax.text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center", fontsize=6, color="white" if mat[i,j] > 0.9 else DARK)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("Family NRMSE; limit 0.75")

    ax = fig.add_subplot(gs[1, 1]); panel_label(ax, "d")
    strata = ["regular", "jitter_0.025", "jitter_0.05", "jitter_0.1"]
    for component, color, marker in [
        ("pressure_gradient_acceleration", BLUE, "o"),
        ("viscosity_laplacian_acceleration", ORANGE, "s"),
    ]:
        for content, ls in [("C0", "--"), ("C1", "-")]:
            vals = []
            for s in strata:
                rr = [r for r in INITIAL_FIG if r["figure"] == "consistency_ablation" and r["component"] == component and r["content"] == content and r["stratum"] == s and r["metric"] == "cvar"]
                vals.append(float(rr[0]["value"]))
            ax.plot(
                range(4), np.array(vals) / 0.25, color=color, marker=marker, ls=ls, lw=1.1, ms=3.2,
                label=f"{COMP_SHORT[component].replace(' gradient','').replace(' Laplacian','')} {content}",
            )
    ax.axhline(1, color=DARK, lw=1, ls=":")
    ax.set_xticks(range(4), ["regular", "2.5%", "5%", "10%"])
    ax.set_yscale("log")
    ax.set_ylabel("Conditional variance / 0.25")
    ax.set_title("Geometry versus geometry + consistency", loc="left", fontweight="bold")
    ax.legend(ncol=2, loc="upper left")
    ax.text(0.02, 0.03, "Matched development-evidence ablation; no uniform rescue", transform=ax.transAxes, fontsize=6.0, color=GREY)
    save_figure(fig, 4)


def figure05() -> None:
    fig = plt.figure(figsize=(mm_to_in(183), mm_to_in(135)), layout="constrained")
    gs = fig.add_gridspec(2, 2, height_ratios=[0.95, 1.05])

    ax = fig.add_subplot(gs[0, :]); clean_axis(ax); panel_label(ax, "a", x=-0.035)
    ax.set_title("Prospective redesign with separated evidence roles", loc="left", fontweight="bold")
    boxes = [
        (0.02, "512 development cases\nconsumed after diagnosis", ORANGE_LIGHT, ORANGE),
        (0.27, "supported hypotheses\nmoments • direction\nreconstruction", PURPLE_LIGHT, PURPLE),
        (0.53, "prospective descriptor freeze\n30 deployable\ndescriptors", BLUE_LIGHT, BLUE),
        (0.78, "384 fresh cases\nzero lineage overlap", TEAL_LIGHT, TEAL),
    ]
    for x0, text, fc, ec in boxes:
        rounded_box(ax, (x0, 0.36), 0.20, 0.34, text, fc, ec, fontsize=6.1, weight="bold")
    for i in range(3):
        arrow(ax, (boxes[i][0] + 0.20, 0.53), (boxes[i + 1][0], 0.53), GREY)
    ax.text(0.63, 0.20, "Four design-only fields excluded", transform=ax.transAxes, ha="center", fontsize=6.2, color=RED)
    ax.text(0.88, 0.20, "96 cases per scientific family", transform=ax.transAxes, ha="center", fontsize=6.2, color=TEAL)

    ax = fig.add_subplot(gs[1, 0]); clean_axis(ax); panel_label(ax, "b")
    ax.set_title("Fresh formal H3 population", loc="left", fontweight="bold")
    rounded_box(ax, (0.08, 0.60), 0.36, 0.24, "384 fresh cases", TEAL_LIGHT, TEAL, fontsize=8, weight="bold")
    rounded_box(ax, (0.56, 0.60), 0.36, 0.24, "128 particles\nper case", BLUE_LIGHT, BLUE, fontsize=8, weight="bold")
    arrow(ax, (0.44, 0.72), (0.56, 0.72), GREY)
    rounded_box(ax, (0.27, 0.18), 0.46, 0.23, "49,152 formal samples", PURPLE_LIGHT, PURPLE, fontsize=9, weight="bold")
    arrow(ax, (0.50, 0.59), (0.50, 0.42), PURPLE)
    ax.text(0.50, 0.05, "Neighbour, variance, oracle, family, and coverage diagnostics", transform=ax.transAxes, ha="center", fontsize=6.2, color=GREY)

    ax = fig.add_subplot(gs[1, 1]); clean_axis(ax); panel_label(ax, "c")
    ax.set_title("Full-particle directional-frame audit", loc="left", fontweight="bold")
    total = 627264; fallback = 515904; stable = total - fallback
    ax.barh([0], [fallback], color=ORANGE, height=0.34, edgecolor=DARK, linewidth=0.5)
    ax.barh([0], [stable], left=[fallback], color=BLUE_LIGHT, height=0.34, edgecolor=BLUE, linewidth=0.5)
    ax.text(fallback / 2, 0, "fallback\n515,904", ha="center", va="center", color="white", fontsize=7, fontweight="bold")
    ax.text(fallback + stable / 2, 0, "non-fallback\n111,360", ha="center", va="center", color=DARK, fontsize=6.3)
    ax.set_xlim(0, total); ax.set_ylim(-0.7, 0.7); ax.set_yticks([])
    ax.set_xticks([0, total], ["0", "627,264 full particle environments"])
    ax.set_title("Full-particle directional-frame audit", loc="left", fontweight="bold")
    ax.text(0.50, 0.18, "515,904 / 627,264 = 82.246710%", transform=ax.transAxes, ha="center", fontsize=8, color=ORANGE, fontweight="bold")
    ax.text(0.50, 0.06, "Frequent degeneracy of the tested frame; not equivariant-GNN failure", transform=ax.transAxes, ha="center", fontsize=6.2, color=GREY)
    save_figure(fig, 5)


def figure06() -> None:
    fig = plt.figure(figsize=(mm_to_in(183), mm_to_in(135)), layout="constrained")
    gs = fig.add_gridspec(3, 1, height_ratios=[0.23, 1.0, 0.26])

    ax = fig.add_subplot(gs[0]); clean_axis(ax); panel_label(ax, "a", x=-0.035)
    ax.set_title("Fresh requalification scope", loc="left", fontweight="bold")
    items = [
        ("384", "fresh cases"),
        ("49,152", "formal samples"),
        ("0", "field-lineage overlap"),
        ("5", "held-out folds"),
    ]
    for i, (value, label) in enumerate(items):
        x0 = 0.02 + i * 0.245
        rounded_box(ax, (x0, 0.10), 0.22, 0.62, f"{value}\n{label}", BLUE_LIGHT if i < 2 else TEAL_LIGHT, BLUE if i < 2 else TEAL, fontsize=7.5, weight="bold")

    ax = fig.add_subplot(gs[1]); panel_label(ax, "b", x=-0.035)
    metrics = list(metric_bundle(FRESH, COMPONENTS[0]).keys())
    values = np.zeros((len(metrics), len(COMPONENTS)), dtype=bool)
    annotations: list[list[str]] = []
    for i, metric in enumerate(metrics):
        ann_row = []
        for j, component in enumerate(COMPONENTS):
            value, limit, direction = metric_bundle(FRESH, component)[metric]
            values[i, j] = metric_pass(value, limit, direction)
            sign = "≤" if direction == "upper" else "≥"
            decision = "P" if values[i, j] else "N"
            ann_row.append(f"{decision}  {fmt_metric(value)}\n{sign} {fmt_metric(limit)}")
        annotations.append(ann_row)
    draw_pass_matrix(ax, values, [COMP_SHORT[c] for c in COMPONENTS], metrics, annotations)
    ax.set_title("All preregistered operational-identifiability criteria", loc="left", fontweight="bold")
    ax.tick_params(axis="x", labelsize=7)
    ax.text(1.02, 0.50, "cell text:\nvalue\nfrozen limit", transform=ax.transAxes, va="center", fontsize=6.1, color=GREY)
    ax.text(0.00, -0.10, "Blue = criterion satisfied; orange = criterion not satisfied. Every row must pass for a component to qualify.", transform=ax.transAxes, fontsize=6.2, color=GREY)

    ax = fig.add_subplot(gs[2]); clean_axis(ax); panel_label(ax, "c", x=-0.035)
    ax.set_title("Route conclusion", loc="left", fontweight="bold")
    rounded_box(
        ax, (0.02, 0.18), 0.62, 0.58,
        "None of the three primary mappings satisfied\nall preregistered identifiability criteria",
        ORANGE_LIGHT, ORANGE, fontsize=8, weight="bold",
    )
    rounded_box(ax, (0.70, 0.18), 0.28, 0.58, "No neural stage\nwas initiated", GREY_LIGHT, GREY, fontsize=8, weight="bold")
    arrow(ax, (0.64, 0.47), (0.70, 0.47), GREY)
    save_figure(fig, 6)


def main() -> None:
    figure01()
    figure02()
    figure03()
    figure04()
    figure05()
    figure06()
    print(f"Wrote 24 publication exports to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
