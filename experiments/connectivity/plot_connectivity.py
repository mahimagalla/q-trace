"""Plotting and visualization module for Connectivity and Routing Experiments.

Member 4: Mounika Kolluru
Primary Responsibility: Connectivity and routing experiments (Linear vs. Fully Connected).

Generates publication-quality figures comparing Linear vs. Fully Connected topologies:
1. Two-qubit gate counts across optimization levels
2. Circuit depth across optimization levels
3. Transpilation execution time (with min-max range error bars)
4. Routing overhead percentage comparison
"""

import sys
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RESULTS_CSV = REPO_ROOT / "results" / "connectivity_experiments.csv"
FALLBACK_CSV = REPO_ROOT / "results" / "qtrace_results.csv"
PLOTS_DIR = REPO_ROOT / "plots" / "connectivity"


def load_data() -> pd.DataFrame:
    """Load connectivity experiment results from CSV."""
    if RESULTS_CSV.exists():
        df = pd.read_csv(RESULTS_CSV)
    elif FALLBACK_CSV.exists():
        df = pd.read_csv(FALLBACK_CSV)
    else:
        raise FileNotFoundError(
            f"No experiment CSV found at {RESULTS_CSV} or {FALLBACK_CSV}. "
            "Please run connectivity_runner.py first."
        )

    # Exclude baseline row
    df = df[df["topology"].isin(["linear", "fully_connected"])].copy()
    df["optimization_level"] = df["optimization_level"].astype(int)
    return df


def plot_two_qubit_gates(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot 2Q gate comparison between Linear and Fully Connected."""
    grouped = (
        df.groupby(["topology", "optimization_level"], as_index=False)["gate_count_2q"]
        .first()
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(4)
    width = 0.35

    lin = grouped[grouped["topology"] == "linear"].sort_values("optimization_level")["gate_count_2q"].values
    fc = grouped[grouped["topology"] == "fully_connected"].sort_values("optimization_level")["gate_count_2q"].values

    rects1 = ax.bar(x - width / 2, lin, width, label="Linear Topology", color="#1f77b4")
    rects2 = ax.bar(x + width / 2, fc, width, label="Fully Connected (Ideal)", color="#2ca02c")

    ax.set_xlabel("Transpiler Optimization Level", fontsize=11, fontweight="bold")
    ax.set_ylabel("Two-Qubit (CX) Gate Count", fontsize=11, fontweight="bold")
    ax.set_title("Two-Qubit Gates: Linear vs. Fully Connected Topology", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["Level 0", "Level 1", "Level 2", "Level 3"])
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Add count labels on bars
    ax.bar_label(rects1, padding=3, fontweight="bold")
    ax.bar_label(rects2, padding=3, fontweight="bold")

    fig.tight_layout()
    output_path = out_dir / "connectivity_2q_gates.png"
    fig.savefig(output_path, dpi=250)
    plt.close(fig)
    return output_path


def plot_circuit_depth(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot gate-only circuit depth comparison."""
    grouped = (
        df.groupby(["topology", "optimization_level"], as_index=False)["circuit_depth"]
        .first()
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    for topology, color, marker, label in [
        ("linear", "#1f77b4", "s", "Linear (Depth = 18)"),
        ("fully_connected", "#2ca02c", "o", "Fully Connected (Depth = 14)"),
    ]:
        subset = grouped[grouped["topology"] == topology].sort_values("optimization_level")
        ax.plot(
            subset["optimization_level"],
            subset["circuit_depth"],
            marker=marker,
            markersize=8,
            linewidth=2,
            color=color,
            label=label,
        )

    ax.set_xlabel("Transpiler Optimization Level", fontsize=11, fontweight="bold")
    ax.set_ylabel("Gate-Only Circuit Depth", fontsize=11, fontweight="bold")
    ax.set_title("Critical-Path Circuit Depth by Topology", fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3])
    ax.set_ylim(10, 22)
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    output_path = out_dir / "connectivity_circuit_depth.png"
    fig.savefig(output_path, dpi=250)
    plt.close(fig)
    return output_path


def plot_transpilation_time(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot median compilation time with min-max variability ranges."""
    timing = (
        df.groupby(["topology", "optimization_level"])["transpile_time_seconds"]
        .agg(["median", "min", "max"])
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(7, 5))
    for topology, color, marker, label in [
        ("linear", "#1f77b4", "s", "Linear Topology"),
        ("fully_connected", "#2ca02c", "o", "Fully Connected"),
    ]:
        subset = timing[timing["topology"] == topology].sort_values("optimization_level")
        med_ms = subset["median"] * 1000
        low_err = (subset["median"] - subset["min"]) * 1000
        up_err = (subset["max"] - subset["median"]) * 1000

        ax.errorbar(
            subset["optimization_level"],
            med_ms,
            yerr=[low_err, up_err],
            marker=marker,
            markersize=7,
            capsize=4,
            linewidth=2,
            color=color,
            label=label,
        )

    ax.set_xlabel("Transpiler Optimization Level", fontsize=11, fontweight="bold")
    ax.set_yscale("log")
    ax.set_ylabel("Median Transpilation Time (ms, log scale)", fontsize=11, fontweight="bold")
    ax.set_title("Transpilation Time (Median; Min–Max, N=5)", fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1, 2, 3])
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    output_path = out_dir / "connectivity_transpilation_time.png"
    fig.savefig(output_path, dpi=250)
    plt.close(fig)
    return output_path


def plot_routing_overhead_pct(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot routing overhead percentages of Linear relative to Fully Connected."""
    grouped = (
        df.groupby(["optimization_level", "topology"])
        .agg(
            gate_count_2q=("gate_count_2q", "first"),
            circuit_depth=("circuit_depth", "first"),
        )
        .reset_index()
    )

    levels = [0, 1, 2, 3]
    q2_overheads = []
    depth_overheads = []

    for opt in levels:
        lin_2q = grouped[(grouped["optimization_level"] == opt) & (grouped["topology"] == "linear")]["gate_count_2q"].iloc[0]
        fc_2q = grouped[(grouped["optimization_level"] == opt) & (grouped["topology"] == "fully_connected")]["gate_count_2q"].iloc[0]
        lin_d = grouped[(grouped["optimization_level"] == opt) & (grouped["topology"] == "linear")]["circuit_depth"].iloc[0]
        fc_d = grouped[(grouped["optimization_level"] == opt) & (grouped["topology"] == "fully_connected")]["circuit_depth"].iloc[0]

        q2_overheads.append(((lin_2q - fc_2q) / fc_2q) * 100)
        depth_overheads.append(((lin_d - fc_d) / fc_d) * 100)

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(4)
    width = 0.35

    rects1 = ax.bar(x - width / 2, q2_overheads, width, label="2Q Gate Overhead (%)", color="#d62728")
    rects2 = ax.bar(x + width / 2, depth_overheads, width, label="Depth Overhead (%)", color="#ff7f0e")

    ax.set_xlabel("Transpiler Optimization Level", fontsize=11, fontweight="bold")
    ax.set_ylabel("Routing Overhead (%)", fontsize=11, fontweight="bold")
    ax.set_title("Relative Routing Penalty of Linear vs. Fully Connected", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["Level 0", "Level 1", "Level 2", "Level 3"])
    ax.set_ylim(0, 90)
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    ax.bar_label(rects1, fmt="%.1f%%", padding=3, fontweight="bold")
    ax.bar_label(rects2, fmt="%.1f%%", padding=3, fontweight="bold")

    fig.tight_layout()
    output_path = out_dir / "connectivity_routing_overhead_pct.png"
    fig.savefig(output_path, dpi=250)
    plt.close(fig)
    return output_path


def main():
    out_dir = PLOTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_data()

    p1 = plot_two_qubit_gates(df, out_dir)
    p2 = plot_circuit_depth(df, out_dir)
    p3 = plot_transpilation_time(df, out_dir)
    p4 = plot_routing_overhead_pct(df, out_dir)

    print("Successfully generated all connectivity comparison plots:")
    for p in (p1, p2, p3, p4):
        print(f"  [SAVED] {p}")


if __name__ == "__main__":
    main()
