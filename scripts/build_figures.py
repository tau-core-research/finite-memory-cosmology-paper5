#!/usr/bin/env python3
"""Build manuscript figures for the finite-memory cosmology method note."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
FIGURES = ROOT / "figures"


BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
GREEN = "#2f855a"
RED = "#c53030"
GRAY = "#4a5568"
LIGHT_GRAY = "#e2e8f0"


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 160,
            "savefig.dpi": 300,
        }
    )


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def fig_operator_shape() -> None:
    x = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    ax.fill_between(x, 1 + 3 * x**3, 1 + 4 * x**3, color=BLUE, alpha=0.12, label=r"locked $\rho\in[3,4]$")
    ax.plot(x, 1 + 3 * x**3, color=BLUE, lw=1.6, label=r"$\rho=3$")
    ax.plot(x, 1 + 4 * x**3, color=ORANGE, lw=1.8, label=r"$\rho=4$")
    ax.axvspan(0, 0.25, color=GREEN, alpha=0.08, label="low-depth guard")
    ax.axvline(0.25, color=GREEN, lw=1.0, ls="--")
    ax.set_xlabel(r"normalized depth $x$")
    ax.set_ylabel(r"finite-memory factor $W(x)$")
    ax.set_title(r"Locked bounded operator: $W(x)=1+\rho x^3,\ \rho\leq4$")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.95, 5.2)
    ax.grid(True, color=LIGHT_GRAY, lw=0.7)
    ax.legend(frameon=False, loc="upper left")
    save(fig, "fig1_locked_operator")


def fig_snbao_gate() -> None:
    df = pd.read_csv(EVIDENCE / "diagnostic_point_audit.csv")
    stable = df["sign_stable"].astype(bool).to_numpy()
    z = df["z"].to_numpy(float)
    median = df["target_median"].to_numpy(float)
    lo = df["target_p16"].to_numpy(float)
    hi = df["target_p84"].to_numpy(float)
    k2 = df["k2_prediction"].to_numpy(float)
    yerr = np.vstack([median - lo, hi - median])

    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    ax.fill_between(z, lo, hi, color=LIGHT_GRAY, alpha=0.75, label="SN+BAO envelope")
    ax.errorbar(z[stable], median[stable], yerr=yerr[:, stable], fmt="o", ms=4.2, color=BLUE, ecolor="#a0aec0", capsize=2, label="sign-stable median")
    ax.errorbar(z[~stable], median[~stable], yerr=yerr[:, ~stable], fmt="o", ms=4.2, mfc="white", mec=ORANGE, color=ORANGE, ecolor="#cbd5e0", capsize=2, label="sign-unstable median")
    ax.plot(z, k2, color=RED, lw=1.8, marker="s", ms=3.5, label="locked K2")
    ax.axhline(0, color="#718096", lw=0.8)
    ax.annotate("localized sign warning", xy=(1.1925, 0.3938), xytext=(1.05, 1.25), arrowprops={"arrowstyle": "->", "lw": 0.8, "color": GRAY}, color=GRAY, fontsize=8)
    ax.set_xlabel("redshift z")
    ax.set_ylabel("diagnostic response")
    ax.set_title("Point-level SN+BAO diagnostic gate")
    ax.grid(True, color=LIGHT_GRAY, lw=0.7)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    save(fig, "fig2_snbao_gate")


def fig_coordinate_robustness() -> None:
    df = pd.read_csv(EVIDENCE / "coordinate_robustness_results.csv")
    df = df[df["Model"].eq("K2_LOCKED_CURRENT")].copy()
    order = [
        "z_normalized_current_packet",
        "z_normalized_recomputed",
        "chi_normalized_flat_lcdm_audit",
        "optical_depth_like_uniform",
        "likelihood_native_index",
    ]
    df["Mapping"] = pd.Categorical(df["Mapping"], categories=order, ordered=True)
    df = df.sort_values("Mapping")
    labels = [
        "z packet",
        "z recomputed",
        r"$\chi$ norm.",
        "optical proxy",
        "native index",
    ]
    colors = [RED if "TENSION" in status else BLUE for status in df["Status"].astype(str)]

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.3), sharex=True)
    x = np.arange(len(df))
    axes[0].bar(x, df["EnvelopeFraction"].to_numpy(float), color=colors, alpha=0.85)
    axes[0].axhline(1, color=GRAY, lw=0.8, ls="--")
    axes[0].set_ylim(0, 1.08)
    axes[0].set_ylabel("envelope fraction")
    axes[0].set_title("Gate overlap")
    axes[1].bar(x, df["Chi2DiagProxy"].to_numpy(float), color=colors, alpha=0.85)
    axes[1].set_ylabel(r"diagonal $\chi^2$ proxy")
    axes[1].set_title("Score sensitivity")
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.grid(True, axis="y", color=LIGHT_GRAY, lw=0.7)
    fig.suptitle("Coordinate robustness audit: warning is localized to the chi-normalized remap", y=1.02, fontsize=10)
    save(fig, "fig3_coordinate_robustness")


def fig_null_scorecard() -> None:
    df = pd.read_csv(EVIDENCE / "model_scorecard.csv")
    keep = [
        "K2_LOCKED_RHO4",
        "K2_LOCKED_GRID_WITHIN_3_4",
        "K1_NO_MEMORY",
        "POLY_DEG2",
        "POLY_DEG3",
    ]
    df = df[df["Model"].isin(keep)].copy()
    df["Model"] = pd.Categorical(df["Model"], categories=keep, ordered=True)
    df = df.sort_values("Model")
    labels = ["K2 rho=4", "K2 grid 3-4", "K1 no memory", "poly deg2", "poly deg3"]
    colors = [BLUE, GREEN, GRAY, ORANGE, ORANGE]

    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    x = np.arange(len(df))
    ax.bar(x, df["AICMean"].to_numpy(float), color=colors, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("mean AIC proxy across mappings")
    ax.set_title("Null-comparator benchmark: runnable preflight, not measurement validation")
    ax.grid(True, axis="y", color=LIGHT_GRAY, lw=0.7)
    ax.text(0.02, 0.96, "lower is better; diagonal/envelope proxy only", transform=ax.transAxes, ha="left", va="top", fontsize=8, color=GRAY)
    save(fig, "fig4_null_scorecard")


def fig_support_ladder() -> None:
    df = pd.read_csv(EVIDENCE / "source_split_likelihood_native_support_ladder.csv")
    labels = [
        "K2 vs K1",
        "K2 vs poly",
        "public cov.",
        "branch scatter",
        "measurement",
    ]
    status_score = {
        "SUPPORTIVE_PREFLIGHT": 3.0,
        "MIXED_CONDITIONAL_SUPPORT": 2.0,
        "WEAKENING_PUBLIC_PROXY": 1.25,
        "DECLARED_PREFLIGHT_SUPPORT": 2.6,
        "BLOCKED": 0.25,
    }
    status_color = {
        "SUPPORTIVE_PREFLIGHT": GREEN,
        "MIXED_CONDITIONAL_SUPPORT": ORANGE,
        "WEAKENING_PUBLIC_PROXY": "#b7791f",
        "DECLARED_PREFLIGHT_SUPPORT": BLUE,
        "BLOCKED": RED,
    }
    scores = [status_score[s] for s in df["Status"]]
    colors = [status_color[s] for s in df["Status"]]

    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    y = np.arange(len(df))[::-1]
    ax.barh(y, scores, color=colors, alpha=0.86)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 3.25)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["blocked", "weak", "mixed", "supportive"])
    ax.set_xlabel("preflight support level")
    ax.set_title("K2 support ladder: improvement routes and remaining blockers")
    ax.grid(True, axis="x", color=LIGHT_GRAY, lw=0.7)
    for yi, (_, row), score in zip(y, df.iterrows(), scores):
        evidence = row["Evidence"]
        if row["LevelID"] == "L1_K2_VS_K1":
            note = "9/9 routes; 8/8 rows; 6/6 CV"
        elif row["LevelID"] == "L2_K2_VS_POLYNOMIAL_CONTROLS":
            note = "6/9 routes; 5/6 CV; public proxy mixed"
        elif row["LevelID"] == "L3_PUBLIC_COVARIANCE_ROUTE":
            note = "public proxy not decisive"
        elif row["LevelID"] == "L4_BRANCH_SCATTER_ROUTE":
            note = "strongest current preflight route"
        else:
            note = "closed until covariance-native benchmark"
        ax.text(min(score + 0.05, 3.05), yi, note, va="center", fontsize=8, color=GRAY)
    ax.text(
        0.01,
        -0.18,
        "Diagnostic support only: this figure summarizes reproducible scorecards, not physical validation.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color=GRAY,
    )
    save(fig, "fig5_support_ladder")


def fig_threshold_sensitivity() -> None:
    p = np.arange(1, 7)
    low_visibility = (p + 1) * 0.25**p
    endpoint_budget = 1 - 0.75 ** (p + 1)
    admissible = (low_visibility <= 0.10) & (endpoint_budget <= 0.75)

    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    ax.plot(p, low_visibility, marker="o", color=BLUE, label=r"low-depth visibility at $x=0.25$")
    ax.plot(p, endpoint_budget, marker="s", color=ORANGE, label="last-quarter budget")
    ax.axhline(0.10, color=BLUE, ls="--", lw=0.9)
    ax.axhline(0.75, color=ORANGE, ls="--", lw=0.9)
    ax.scatter(p[admissible], low_visibility[admissible], s=80, facecolors="none", edgecolors=GREEN, lw=1.8, label="baseline admissible")
    ax.set_xlabel("power-kernel exponent p")
    ax.set_ylabel("audit metric")
    ax.set_title("Shape-selection audit for simple power kernels")
    ax.set_xticks(p)
    ax.set_ylim(0, 1.05)
    ax.grid(True, color=LIGHT_GRAY, lw=0.7)
    ax.legend(frameon=False, loc="upper right")
    save(fig, "figA_threshold_sensitivity")


def fig_measurement_gate_flow() -> None:
    fig, ax = plt.subplots(figsize=(7.0, 2.7))
    ax.axis("off")
    labels = [
        "locked K2\noperator",
        "diagnostic\npacket",
        "coordinate\nrobustness",
        "null\ncomparators",
        "covariance-aware\nbenchmark",
        "falsification\ncriteria",
    ]
    x = np.linspace(0.08, 0.92, len(labels))
    y = 0.56
    for i, (xi, label) in enumerate(zip(x, labels)):
        fc = "#ebf8ff" if i < 4 else "#fffaf0"
        ec = BLUE if i < 4 else ORANGE
        ax.text(xi, y, label, ha="center", va="center", fontsize=8.5, bbox={"boxstyle": "round,pad=0.35", "fc": fc, "ec": ec, "lw": 1.0})
        if i < len(labels) - 1:
            ax.annotate("", xy=(x[i + 1] - 0.06, y), xytext=(xi + 0.06, y), arrowprops={"arrowstyle": "->", "lw": 1.0, "color": GRAY})
    ax.text(0.5, 0.17, "Current status: operational preflight; measurement gate remains closed", ha="center", va="center", fontsize=9, color=GRAY)
    save(fig, "figB_measurement_gate_flow")


def main() -> None:
    set_style()
    fig_operator_shape()
    fig_snbao_gate()
    fig_coordinate_robustness()
    fig_null_scorecard()
    fig_support_ladder()
    fig_threshold_sensitivity()
    fig_measurement_gate_flow()
    print(f"Wrote figures to {FIGURES}")


if __name__ == "__main__":
    main()
