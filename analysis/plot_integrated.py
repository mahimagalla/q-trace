"""
Integrated Visualization Module for Q-TRACE Experiments.

Generates publication-quality figures analyzing compilation trade-offs across
optimization levels and qubit connectivity topologies:
  1. 2Q gates vs. median transpilation time (with asymmetric min-max error bars).
  2. Circuit depth vs. 2Q gates (structural comparison).
  3. Multi-objective Pareto frontier (dominated vs. non-dominated configurations).
  4. Observed connectivity-associated overhead across optimization levels.

All metrics and percentage overheads are computed dynamically from experiment CSVs.
"""

from __future__ import annotations
import os
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple

# Set writable Matplotlib config directory before importing pyplot
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="matplotlib_qtrace_"))

import matplotlib.pyplot as plt
import numpy as np

from analysis.data_loader import ConfigurationSummary, DataLoader
from analysis.pareto import pareto_frontier
from analysis.tradeoff_analysis import (
    ParetoResult,
    build_pareto_results,
    calculate_frontier,
    calculate_percentage_change,
)

# Output directory for analysis figures
OUTPUT_DIR = Path("plots/analysis")


def _setup_figure_style() -> None:
    """Set uniform style conventions across all generated plots."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 13,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.grid": True,
            "grid.alpha": 0.4,
            "grid.linestyle": "--",
        }
    )


def plot_gates_vs_transpilation_time(
    loader: DataLoader,
    output_path: Path,
) -> None:
    """
    Plot 1: Two-qubit gate count versus median transpilation time.
    Horizontal error bars represent observed asymmetric min-max ranges across trials (N=5).
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))

    summaries = loader.get_all_summaries()

    colors = {"fully_connected": "#1f77b4", "linear": "#d62728"}
    markers = {"fully_connected": "o", "linear": "s"}
    labels_map = {
        "fully_connected": "Fully Connected (Idealized)",
        "linear": "Linear Topology",
    }

    # Group by topology
    by_topo: Dict[str, List[ConfigurationSummary]] = {}
    for s in summaries:
        if s.optimization_level is not None:
            by_topo.setdefault(s.topology, []).append(s)

    for topo, s_list in by_topo.items():
        s_list.sort(key=lambda x: x.optimization_level)  # type: ignore

        x_meds = [s.median_time_ms for s in s_list]
        y_gates = [s.gate_count_2q for s in s_list]

        # Calculate asymmetric error bars: [median - min, max - median]
        x_err_low = [s.median_time_ms - s.min_time_ms for s in s_list]  # type: ignore
        x_err_high = [s.max_time_ms - s.median_time_ms for s in s_list]  # type: ignore
        xerr = np.array([x_err_low, x_err_high])

        color = colors.get(topo, "#333333")
        marker = markers.get(topo, "o")

        ax.errorbar(
            x_meds,
            y_gates,
            xerr=xerr,
            fmt=marker,
            color=color,
            ecolor=color,
            elinewidth=1.5,
            capsize=4,
            capthick=1.5,
            markersize=8,
            label=labels_map.get(topo, topo),
            zorder=3,
        )

        # Annotate optimization levels with staggered offsets to avoid collisions
        for s in s_list:
            opt = s.optimization_level
            # Alternate vertical positioning
            if topo == "linear":
                if opt in (0, 2):
                    offset_y = 0.45
                    va = "bottom"
                else:
                    offset_y = -0.55
                    va = "top"
            else:
                if opt in (0, 2):
                    offset_y = -0.55
                    va = "top"
                else:
                    offset_y = 0.45
                    va = "bottom"

            ax.annotate(
                f"Opt {opt}",
                xy=(s.median_time_ms, s.gate_count_2q),  # type: ignore
                xytext=(s.median_time_ms, s.gate_count_2q + offset_y),  # type: ignore
                fontsize=8.5,
                fontweight="semibold",
                color=color,
                ha="center",
                va=va,
            )

    ax.set_xlabel("Median Classical Transpilation Time (ms) [Horizontal bars: Min–Max range]")
    ax.set_ylabel("Two-Qubit Gate Count (CX)")
    ax.set_title("Two-Qubit Gates vs. Transpilation Time (QAOA Cycle-4, p=1)")
    ax.legend(loc="upper right", framealpha=0.9)

    ax.set_ylim(6, 16)
    ax.set_yticks([6, 8, 10, 12, 14, 16])

    # Methodological caption note
    fig.text(
        0.5,
        -0.03,
        "Note: 5 trials per configuration (Qiskit 2.5.2, Python 3.14.4, seed 2026). "
        "Transpilation times are classical compile durations, not quantum execution times.",
        ha="center",
        fontsize=8,
        color="#555555",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def plot_depth_vs_2q_gates(
    loader: DataLoader,
    output_path: Path,
) -> None:
    """
    Plot 2: Gate-only circuit depth versus two-qubit gate count.
    Illustrates structural resource requirements and connectivity penalty.
    """
    fig, ax = plt.subplots(figsize=(7.5, 5))

    summaries = loader.get_all_summaries()

    colors = {"fully_connected": "#1f77b4", "linear": "#d62728"}
    markers = {"fully_connected": "o", "linear": "s"}
    labels_map = {
        "fully_connected": "Fully Connected",
        "linear": "Linear Topology",
    }

    # Group configurations with identical structural coordinates to prevent overlapping labels
    struct_groups: Dict[Tuple[str, int, int], List[int]] = {}
    for s in summaries:
        if s.optimization_level is not None:
            key = (s.topology, s.gate_count_2q, s.circuit_depth)
            struct_groups.setdefault(key, []).append(s.optimization_level)

    plotted_labels = set()
    for (topo, gates_2q, depth), opts in struct_groups.items():
        color = colors.get(topo, "#333333")
        marker = markers.get(topo, "o")

        label = labels_map.get(topo, topo) if topo not in plotted_labels else None
        plotted_labels.add(topo)

        ax.scatter(
            gates_2q,
            depth,
            color=color,
            marker=marker,
            s=110,
            label=label,
            zorder=3,
        )

        # Create concise grouped label
        opts.sort()
        if len(opts) == 4 and opts == [0, 1, 2, 3]:
            opt_str = "Opt 0–3"
        elif len(opts) > 1:
            opt_str = f"Opt {', '.join(str(o) for o in opts)}"
        else:
            opt_str = f"Opt {opts[0]}"

        offset_y = 0.45 if topo == "linear" and gates_2q == 14 else -0.55
        va = "bottom" if offset_y > 0 else "top"
        ax.annotate(
            f"{opt_str}\n({topo})",
            xy=(gates_2q, depth),
            xytext=(gates_2q, depth + offset_y),
            fontsize=8.5,
            fontweight="semibold",
            color=color,
            ha="center",
            va=va,
        )

    ax.set_xlabel("Two-Qubit Gate Count (CX)")
    ax.set_ylabel("Gate-Only Circuit Depth")
    ax.set_title("Structural Comparison: Circuit Depth vs. Two-Qubit Gates")
    ax.legend(loc="upper left", framealpha=0.9)

    ax.set_xlim(6, 16)
    ax.set_ylim(10, 20)
    ax.set_xticks([6, 8, 10, 12, 14, 16])
    ax.set_yticks([10, 12, 14, 16, 18, 20])

    fig.text(
        0.5,
        -0.03,
        "Note: Circuit depth and gate counts strictly exclude measurement operations, barriers, and directives.",
        ha="center",
        fontsize=8,
        color="#555555",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def plot_pareto_frontier(
    loader: DataLoader,
    output_path: Path,
) -> None:
    """
    Plot 3: Multi-objective Pareto frontier visualization.
    Shows dominated vs. non-dominated configurations across 2Q gates, depth, and median compilation time.
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))

    summaries = loader.get_all_summaries()
    pareto_results = build_pareto_results(summaries)

    # Calculate 3D primary frontier
    primary_frontier = calculate_frontier(
        pareto_results,
        ["two_qubit_gates", "circuit_depth", "median_transpile_time_ms"],
    )
    frontier_set = {(r.topology, r.optimization_level) for r in primary_frontier}

    for r in pareto_results:
        is_frontier = (r.topology, r.optimization_level) in frontier_set
        time_val = r.median_transpile_time_ms

        if is_frontier:
            ax.scatter(
                time_val,
                r.two_qubit_gates,
                color="#2ca02c",
                marker="*",
                s=260,
                edgecolor="black",
                linewidth=1.2,
                label="Pareto-Optimal (Non-dominated)" if "Pareto-Optimal" not in [t.get_label() for t in ax.get_lines()] else None,
                zorder=5,
            )
            ax.annotate(
                f"{r.label}\n[Non-dominated]",
                xy=(time_val, r.two_qubit_gates),  # type: ignore
                xytext=(time_val + 0.4, r.two_qubit_gates + 0.6),  # type: ignore
                fontsize=8.5,
                fontweight="bold",
                color="#1b6d1b",
                arrowprops=dict(arrowstyle="->", color="#1b6d1b", lw=1),
            )
        else:
            color = "#1f77b4" if r.topology == "fully_connected" else "#d62728"
            ax.scatter(
                time_val,
                r.two_qubit_gates,
                color=color,
                marker="o",
                s=70,
                alpha=0.65,
                edgecolor="none",
                zorder=3,
            )
            # Alternate label placement above/below to prevent overlap
            opt = r.optimization_level
            offset_y = 0.35 if opt in (0, 2) else -0.5
            va = "bottom" if offset_y > 0 else "top"
            prefix = "FU" if r.topology == "fully_connected" else "LI"
            ax.annotate(
                f"{prefix}-Opt{opt}",
                xy=(time_val, r.two_qubit_gates),  # type: ignore
                xytext=(time_val, r.two_qubit_gates + offset_y),  # type: ignore
                fontsize=8,
                color="#555555",
                ha="center",
                va=va,
            )

    ax.set_xlabel("Median Transpilation Time (ms)")
    ax.set_ylabel("Two-Qubit Gate Count (CX)")
    ax.set_title("Pareto-Optimal Frontier (Minimizing 2Q Gates, Depth & Transpile Time)")

    # Custom legend entries
    from matplotlib.lines import Line2D
    custom_legend = [
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#2ca02c", markeredgecolor="black", markersize=14, label="Pareto-Optimal"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#1f77b4", markersize=8, label="Fully Connected (Dominated)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#d62728", markersize=8, label="Linear (Dominated)"),
    ]
    ax.legend(handles=custom_legend, loc="upper right", framealpha=0.9)

    ax.set_ylim(6, 16)
    ax.set_yticks([6, 8, 10, 12, 14, 16])

    fig.text(
        0.5,
        -0.03,
        "Note: Dominance evaluated under strict Pareto minimization across all 3 objectives.",
        ha="center",
        fontsize=8,
        color="#555555",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def plot_routing_overhead_integrated(
    loader: DataLoader,
    output_path: Path,
) -> None:
    """
    Plot 4: Observed connectivity-associated overhead across optimization levels.
    Calculates percentage increases for Linear vs. Fully Connected at each optimization level:
      - Two-qubit gate overhead (%)
      - Gate-only depth overhead (%)
      - Transpilation time overhead (%)
    All values are calculated programmatically from the CSV data.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    opt_levels = [0, 1, 2, 3]

    gate_overheads = []
    depth_overheads = []
    time_overheads = []

    for opt in opt_levels:
        s_fc = loader.get_summary("fully_connected", opt)
        s_lin = loader.get_summary("linear", opt)

        if s_fc is None or s_lin is None:
            continue

        pct_gate = calculate_percentage_change(s_fc.gate_count_2q, s_lin.gate_count_2q)
        pct_depth = calculate_percentage_change(s_fc.circuit_depth, s_lin.circuit_depth)
        pct_time = calculate_percentage_change(s_fc.median_time_ms, s_lin.median_time_ms)  # type: ignore

        gate_overheads.append(pct_gate)
        depth_overheads.append(pct_depth)
        time_overheads.append(pct_time)

    x = np.arange(len(opt_levels))
    width = 0.25

    rects1 = ax.bar(x - width, gate_overheads, width, label="Two-Qubit Gates (CX) Overhead", color="#d62728", alpha=0.85)
    rects2 = ax.bar(x, depth_overheads, width, label="Circuit Depth Overhead", color="#ff7f0e", alpha=0.85)
    rects3 = ax.bar(x + width, time_overheads, width, label="Transpilation Time Overhead", color="#1f77b4", alpha=0.85)

    ax.set_ylabel("Observed Overhead (% Increase vs. Fully Connected)")
    ax.set_title("Observed Connectivity-Associated Overhead: Linear vs. Fully Connected")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Optimization Level {opt}" for opt in opt_levels])
    ax.legend(loc="upper right", framealpha=0.9)

    # Annotate bar values
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height is not None:
                ax.annotate(
                    f"+{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=7.5,
                    fontweight="bold",
                )

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    ax.set_ylim(0, 90)

    fig.text(
        0.5,
        -0.03,
        "Note: Overheads calculated programmatically: (Linear - Fully Connected) / Fully Connected * 100%. "
        "Fully Connected serves as the idealized, unconstrained reference topology.",
        ha="center",
        fontsize=8,
        color="#555555",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def generate_all_plots(csv_path: str = "results/qtrace_results.csv") -> None:
    """Generate all four publication-ready integrated analysis figures."""
    _setup_figure_style()
    loader = DataLoader(csv_path)

    print(f"Loading data from {csv_path}...")
    print("Generating Plot 1: 2Q gates vs. transpilation time...")
    plot_gates_vs_transpilation_time(loader, OUTPUT_DIR / "2q_gates_vs_transpilation_time.png")

    print("Generating Plot 2: Circuit depth vs. 2Q gates...")
    plot_depth_vs_2q_gates(loader, OUTPUT_DIR / "depth_vs_2q_gates.png")

    print("Generating Plot 3: Pareto frontier...")
    plot_pareto_frontier(loader, OUTPUT_DIR / "pareto_frontier.png")

    print("Generating Plot 4: Routing overhead across optimization levels...")
    plot_routing_overhead_integrated(loader, OUTPUT_DIR / "routing_overhead_integrated.png")

    print(f"\nAll 4 figures successfully generated in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all_plots()
