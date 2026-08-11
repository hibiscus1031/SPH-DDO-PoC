#!/usr/bin/env python3
"""Python-exclusive publication figure exports for frozen DDO-01E metrics."""

from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42

import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/identifiability/ddo01e_figure_source_data.csv"
OUT = ROOT / "figures/ddo01e"
SOURCE_SHA256 = "3619a8928aae81cffa105688fc767315f6a27baddb5dd029e2aedad2cde866c8"

COMPONENTS = ["density_rate", "pressure_gradient_acceleration", "viscosity_laplacian_acceleration"]
COMPONENT_LABELS = {"density_rate": "Density rate", "pressure_gradient_acceleration": "Pressure", "viscosity_laplacian_acceleration": "Viscosity"}
COLORS = {"density_rate": "#3775BA", "pressure_gradient_acceleration": "#B64342", "viscosity_laplacian_acceleration": "#42949E"}
CONTENT_COLORS = {"C0": "#7884B4", "C1": "#E9A6A1"}
LAYOUTS = ["regular", "jitter_0.025", "jitter_0.05", "jitter_0.1"]
LAYOUT_LABELS = ["Regular", "Jitter 0.025", "Jitter 0.05", "Jitter 0.1"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def style() -> None:
    plt.rcParams.update({
        "font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7,
        "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.2,
        "axes.linewidth": .7, "xtick.major.width": .7, "ytick.major.width": .7,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "figure.facecolor": "white", "axes.facecolor": "white",
    })


def panel(ax, label: str) -> None:
    ax.text(-.13, 1.05, label, transform=ax.transAxes, fontweight="bold", fontsize=8, va="bottom")


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = OUT / stem
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    with Image.open(base.with_suffix(".tiff")) as raster:
        raster.convert("RGB").save(base.with_suffix(".tiff"), dpi=(600, 600), compression="tiff_lzw")
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def identifiability_ladder(data: pd.DataFrame) -> None:
    subset = data[data.figure == "identifiability_ladder"]
    fig, axes = plt.subplots(2, 3, figsize=(7.205, 4.45), constrained_layout=True)
    contents, localities = ["C0", "C1", "C2", "C3"], ["L0", "L1", "L2", "L3"]
    for col, component in enumerate(COMPONENTS):
        for row, (metric, title, vmax, threshold) in enumerate((("oracle_nrmse", "Best-oracle NRMSE", 1.2, .5), ("cvar", "Conditional variance ratio", 1.2, .25))):
            ax = axes[row, col]
            matrix = np.empty((4, 4))
            for i, content in enumerate(contents):
                for j, locality in enumerate(localities):
                    matrix[i, j] = subset[(subset.component == component) & (subset.content == content) & (subset.locality == locality) & (subset.metric == metric)].value.iloc[0]
            image = ax.imshow(matrix, vmin=0, vmax=vmax, cmap="magma_r", aspect="auto")
            for i in range(4):
                for j in range(4):
                    value = matrix[i, j]
                    ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=5.7, color="white" if value > .62 * vmax else "black")
                    if value <= threshold:
                        ax.add_patch(plt.Rectangle((j - .48, i - .48), .96, .96, fill=False, edgecolor="#2E9E44", linewidth=1.2))
            ax.set_xticks(range(4), localities); ax.set_yticks(range(4), contents)
            if row == 0: ax.set_title(COMPONENT_LABELS[component], fontweight="bold")
            if col == 0: ax.set_ylabel(title)
            if row == 1: ax.set_xlabel("Spatial context")
            panel(ax, chr(ord('a') + row * 3 + col))
    cbar = fig.colorbar(image, ax=axes, fraction=.018, pad=.015)
    cbar.set_label("Metric value (green outline: point threshold met)")
    save(fig, "identifiability_ladder")


def locality_ladder(data: pd.DataFrame) -> None:
    subset = data[data.figure == "locality_ladder"]
    fig, axes = plt.subplots(1, 2, figsize=(7.205, 2.65), constrained_layout=True)
    for ax, metric, ylabel, threshold in ((axes[0], "oracle_nrmse", "Best-oracle NRMSE", .5), (axes[1], "cvar", "Conditional variance ratio", .25)):
        for component in COMPONENTS:
            values = [subset[(subset.component == component) & (subset.locality == locality) & (subset.metric == metric)].value.iloc[0] for locality in ("L0", "L1", "L2", "L3")]
            ax.plot(range(4), values, marker="o", ms=4, lw=1.5, color=COLORS[component], label=COMPONENT_LABELS[component])
        ax.axhline(threshold, color="#606060", lw=.9, ls="--", label=f"Gate {threshold:g}")
        ax.set_xticks(range(4), ["L0\nparticle", "L1\none-hop", "L2\ntwo-hop", "L3\nglobal"])
        ax.set_ylabel(ylabel); ax.set_xlabel("C3 spatial information scope"); ax.grid(axis="y", color="#E5E5E5", lw=.5)
    axes[0].legend(ncol=2, loc="upper right"); panel(axes[0], "a"); panel(axes[1], "b")
    save(fig, "locality_ladder")


def paired_bars(ax, data: pd.DataFrame, component: str, metric: str, ylabel: str, threshold: float) -> None:
    x = np.arange(4); width = .34
    for offset, content in ((-.5, "C0"), (.5, "C1")):
        values = [data[(data.component == component) & (data.content == content) & (data.stratum == layout) & (data.metric == metric)].value.iloc[0] for layout in LAYOUTS]
        ax.bar(x + offset * width, values, width, color=CONTENT_COLORS[content], edgecolor="#4D4D4D", linewidth=.5, label=f"{content}: {'G' if content == 'C0' else 'G+C'}")
    ax.axhline(threshold, color="#606060", lw=.8, ls="--")
    ax.set_xticks(x, LAYOUT_LABELS, rotation=20, ha="right"); ax.set_ylabel(ylabel); ax.grid(axis="y", color="#E5E5E5", lw=.5)


def consistency_ablation(data: pd.DataFrame) -> None:
    subset = data[data.figure == "consistency_ablation"]
    fig, axes = plt.subplots(2, 2, figsize=(7.205, 4.5), constrained_layout=True)
    for col, component in enumerate(COMPONENTS[1:]):
        paired_bars(axes[0, col], subset, component, "cvar", "Conditional variance ratio", .25)
        paired_bars(axes[1, col], subset, component, "oracle_nrmse", "Best-oracle NRMSE", .5)
        axes[0, col].set_title(COMPONENT_LABELS[component], fontweight="bold")
        for row in range(2): panel(axes[row, col], chr(ord('a') + row * 2 + col))
    axes[0, 0].legend(ncol=2, loc="upper left")
    save(fig, "consistency_ablation")


def disorder_stratified(data: pd.DataFrame) -> None:
    subset = data[data.figure == "disorder_stratified_ambiguity"]
    fig, axes = plt.subplots(2, 2, figsize=(7.205, 4.35), constrained_layout=True)
    for col, component in enumerate(COMPONENTS[1:]):
        for row, (metric, ylabel, threshold) in enumerate((("dnn_p90", "DNN 90th percentile", .6), ("cvar", "Conditional variance ratio", .25))):
            ax=axes[row,col]
            values=[subset[(subset.component==component)&(subset.stratum==layout)&(subset.metric==metric)].value.iloc[0] for layout in LAYOUTS]
            ax.plot(range(4), values, marker="o", lw=1.6, ms=4.5, color=COLORS[component])
            ax.axhline(threshold,color="#606060",lw=.8,ls="--")
            ax.set_xticks(range(4),LAYOUT_LABELS,rotation=20,ha="right"); ax.set_ylabel(ylabel); ax.grid(axis="y",color="#E5E5E5",lw=.5)
            if row==0: ax.set_title(COMPONENT_LABELS[component],fontweight="bold")
            panel(ax,chr(ord('a')+row*2+col))
    save(fig,"disorder_stratified_ambiguity")


def family_stratified(data: pd.DataFrame) -> None:
    subset=data[data.figure=="family_stratified_metrics"]
    fig,axes=plt.subplots(1,2,figsize=(7.205,2.75),constrained_layout=True)
    families=["F1","F2","F3","F4"]
    for ax,metric,ylabel,threshold in ((axes[0],"oracle_nrmse","Best-oracle NRMSE",.75),(axes[1],"dnn_p90","DNN 90th percentile",.6)):
        for component in COMPONENTS:
            values=[subset[(subset.component==component)&(subset.stratum==family)&(subset.metric==metric)].value.iloc[0] for family in families]
            ax.plot(range(4),values,marker="o",ms=4,lw=1.5,color=COLORS[component],label=COMPONENT_LABELS[component])
        ax.axhline(threshold,color="#606060",lw=.8,ls="--")
        ax.set_xticks(range(4),families); ax.set_xlabel("Analytical field family"); ax.set_ylabel(ylabel); ax.grid(axis="y",color="#E5E5E5",lw=.5)
    axes[0].legend(ncol=2,loc="upper left"); panel(axes[0],"a"); panel(axes[1],"b")
    save(fig,"family_stratified_metrics")


def main() -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("frozen figure source table hash mismatch")
    style(); data=pd.read_csv(SOURCE)
    identifiability_ladder(data); locality_ladder(data); consistency_ablation(data)
    disorder_stratified(data); family_stratified(data)
    print({path.name: sha256(path) for path in sorted(OUT.glob('*'))})


if __name__ == "__main__":
    main()
