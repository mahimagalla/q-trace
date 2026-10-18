"""Plotting and visualization module for Optimization-Level Experiments.

Member 3: K Prerana (2024BCS0048)

Generates publication-quality figures comparing optimization levels 0, 1, 2, and 3:
1. Gate Counts vs. Optimization Level (1Q and 2Q gates)
2. Gate-Only Circuit Depth vs. Optimization Level
3. Transpilation Runtime vs. Optimization Level (with min-max error bars)
4. Compilation Cost vs. Resource Reduction Trade-off
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RESULTS_CSV = REPO_ROOT / "results" / "optimization_experiments.csv"
FALLBACK_CSV = REPO_ROOT / "results" / "qtrace_results.csv"
PLOTS_DIR = REPO_ROOT / "plots" / "optimization"
FINDINGS_DOC = REPO_ROOT / "experiments" / "optimization" / "OPTIMIZATION_FINDINGS.md"


def load_data() -> pd.DataFrame:
    """Load optimization results from CSV, falling back to main results CSV."""
    if RESULTS_CSV.exists():
        df = pd.read_csv(RESULTS_CSV)
    elif FALLBACK_CSV.exists():
        df = pd.read_csv(FALLBACK_CSV)
    else:
        raise FileNotFoundError(
            f"No experiment CSV found at {RESULTS_CSV} or {FALLBACK_CSV}. "
            "Please run optimization_runner.py first."
        )

    # Filter out baseline if present
    df = df[df["topology"].isin(["linear", "fully_connected"])].copy()
    df["optimization_level"] = df["optimization_level"].astype(int)
    return df


def plot_gate_counts(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot 2-qubit and 1-qubit gate counts across optimization levels."""
    grouped = (
        df.groupby(["topology", "optimization_level"], as_index=False)
        .agg(
            gate_count_2q=("gate_count_2q", "first"),
            gate_count_1q=("gate_count_1q", "first"),
            total_ops=("total_ops", "first"),
        )
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    styles = {
        "linear": {"color": "#1f77b4", "marker": "s", "label": "Linear Topology"},
        "fully_connected": {"color": "#2ca02c", "marker": "o", "label": "Fully Connected"},
    }

    # Subplot 1: Two-Qubit Gates (Primary metric for NISQ noise)
    for topo, style in styles.items():
        sub = grouped[grouped["topology"] == topo]
        ax1.plot(
            sub["optimization_level"],
            sub["gate_count_2q"],
            marker=style["marker"],
            color=style["color"],
            linewidth=2,
            markersize=8,
            label=style["label"],
        )

    ax1.set_title("Two-Qubit Gates (CX) vs Optimization Level", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Optimization Level", fontsize=10)
    ax1.set_ylabel("Two-Qubit Gate Count", fontsize=10)
    ax1.set_xticks([0, 1, 2, 3])
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(frameon=True)

    # Subplot 2: One-Qubit Gates
    for topo, style in styles.items():
        sub = grouped[grouped["topology"] == topo]
        ax2.plot(
            sub["optimization_level"],
            sub["gate_count_1q"],
            marker=style["marker"],
            color=style["color"],
            linewidth=2,
            markersize=8,
            label=style["label"],
        )

    ax2.set_title("Single-Qubit Gates vs Optimization Level", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Optimization Level", fontsize=10)
    ax2.set_ylabel("Single-Qubit Gate Count", fontsize=10)
    ax2.set_xticks([0, 1, 2, 3])
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(frameon=True)

    fig.tight_layout()
    target_path = out_dir / "opt_level_vs_gate_counts.png"
    fig.savefig(target_path, dpi=200)
    plt.close(fig)
    return target_path


def plot_circuit_depth(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot gate-only circuit depth across optimization levels."""
    grouped = (
        df.groupby(["topology", "optimization_level"], as_index=False)["circuit_depth"]
        .first()
    )

    fig, ax = plt.subplots(figsize=(6.5, 4.5))

    styles = {
        "linear": {"color": "#1f77b4", "marker": "s", "label": "Linear Topology"},
        "fully_connected": {"color": "#2ca02c", "marker": "o", "label": "Fully Connected"},
    }

    for topo, style in styles.items():
        sub = grouped[grouped["topology"] == topo]
        ax.plot(
            sub["optimization_level"],
            sub["circuit_depth"],
            marker=style["marker"],
            color=style["color"],
            linewidth=2,
            markersize=8,
            label=style["label"],
        )

    ax.set_title("Gate-Only Circuit Depth vs Optimization Level", fontsize=11, fontweight="bold")
    ax.set_xlabel("Optimization Level", fontsize=10)
    ax.set_ylabel("Gate-Only Depth", fontsize=10)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_ylim(bottom=0, top=max(grouped["circuit_depth"]) + 4)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True)

    fig.tight_layout()
    target_path = out_dir / "opt_level_vs_circuit_depth.png"
    fig.savefig(target_path, dpi=200)
    plt.close(fig)
    return target_path


def plot_transpilation_time(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot transpilation execution time with median and error bars."""
    timing = (
        df.groupby(["topology", "optimization_level"])["transpile_time_seconds"]
        .agg(["median", "min", "max"])
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(7, 4.5))

    styles = {
        "linear": {"color": "#1f77b4", "marker": "s", "label": "Linear Topology"},
        "fully_connected": {"color": "#2ca02c", "marker": "o", "label": "Fully Connected"},
    }

    for topo, style in styles.items():
        sub = timing[timing["topology"] == topo]
        median_ms = sub["median"] * 1000
        lower_err = (sub["median"] - sub["min"]) * 1000
        upper_err = (sub["max"] - sub["median"]) * 1000

        ax.errorbar(
            sub["optimization_level"],
            median_ms,
            yerr=[lower_err, upper_err],
            marker=style["marker"],
            color=style["color"],
            capsize=5,
            linewidth=2,
            markersize=8,
            label=style["label"],
        )

    ax.set_title("Transpilation Time (ms) vs Optimization Level", fontsize=11, fontweight="bold")
    ax.set_xlabel("Optimization Level", fontsize=10)
    ax.set_ylabel("Transpilation Time (ms)", fontsize=10)
    ax.set_xticks([0, 1, 2, 3])
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True)

    fig.tight_layout()
    target_path = out_dir / "opt_level_vs_transpilation_time.png"
    fig.savefig(target_path, dpi=200)
    plt.close(fig)
    return target_path


def plot_tradeoff_pareto(df: pd.DataFrame, out_dir: Path) -> Path:
    """Plot trade-off between Transpilation Runtime (ms) and 2Q Gate Count."""
    agg = (
        df.groupby(["topology", "optimization_level"], as_index=False)
        .agg(
            gate_count_2q=("gate_count_2q", "first"),
            circuit_depth=("circuit_depth", "first"),
            median_ms=("transpile_time_seconds", lambda s: s.median() * 1000),
        )
    )

    fig, ax = plt.subplots(figsize=(7.5, 5))

    colors = {"linear": "#1f77b4", "fully_connected": "#2ca02c"}

    for _, row in agg.iterrows():
        topo = row["topology"]
        opt = int(row["optimization_level"])
        ax.scatter(
            row["median_ms"],
            row["gate_count_2q"],
            color=colors[topo],
            s=120,
            zorder=4,
            edgecolors="black",
        )
        ax.annotate(
            f"Opt {opt} ({topo[:3]})",
            (row["median_ms"], row["gate_count_2q"]),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=9,
        )

    ax.set_title("Trade-off: Classical Compilation Time vs Quantum 2Q Gate Count", fontsize=11, fontweight="bold")
    ax.set_xlabel("Median Transpilation Time (ms) [Cost]", fontsize=10)
    ax.set_ylabel("Two-Qubit Gates (CX) [NISQ Noise Risk]", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    target_path = out_dir / "optimization_tradeoff_pareto.png"
    fig.savefig(target_path, dpi=200)
    plt.close(fig)
    return target_path


def generate_findings_report(df: pd.DataFrame) -> None:
    """Generate Markdown report summarizing optimization experiments."""
    agg = (
        df.groupby(["topology", "optimization_level"], as_index=False)
        .agg(
            gate_count_1q=("gate_count_1q", "first"),
            gate_count_2q=("gate_count_2q", "first"),
            circuit_depth=("circuit_depth", "first"),
            median_ms=("transpile_time_seconds", lambda s: s.median() * 1000),
            min_ms=("transpile_time_seconds", lambda s: s.min() * 1000),
            max_ms=("transpile_time_seconds", lambda s: s.max() * 1000),
        )
    )

    lines = [
        "# Optimization-Level Experiments: Summary & Findings",
        "",
        "**Author:** K Prerana (Member 3 - 2024BCS0048)  ",
        "**Module:** `experiments/optimization`  ",
        "**Project:** Q-TRACE (EIGEN5)  ",
        "",
        "## 1. Experimental Overview",
        "",
        "This study isolates the empirical impact of Qiskit transpiler optimization levels (0, 1, 2, and 3) "
        "while holding fixed: basis gates (`['u', 'cx']`), initial layout (`identity`), transpiler seed (`2026`), "
        "and 5 repeated trials per configuration to measure runtime variability.",
        "",
        "## 2. Quantitative Results Table",
        "",
        "| Topology | Opt Level | 1Q Gates | 2Q Gates (CX) | Depth | Median Time (ms) | Min-Max Range (ms) |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for _, row in agg.iterrows():
        lines.append(
            f"| {row['topology']} | {row['optimization_level']} | "
            f"{row['gate_count_1q']} | {row['gate_count_2q']} | {row['circuit_depth']} | "
            f"{row['median_ms']:.2f} ms | {row['min_ms']:.2f} - {row['max_ms']:.2f} ms |"
        )

    lines.extend([
        "",
        "## 3. Key Observations & Trade-Off Analysis",
        "",
        "1. **Gate Count Optimization:**",
        "   - **Linear Topology:** Optimization level 0 and 1 yield 14 two-qubit operations. Optimization levels 2 and 3 reduce two-qubit operations to 12 (a **14.3% reduction** in 2Q gates) alongside an increase in single-qubit operations (from 12 to 17). Rather than asserting specific internal pulse cancellation mechanisms without transpiler pass-manager execution traces, we report this as an empirical structural reduction achieved through Qiskit's higher-level synthesis and heuristic optimization passes, which restructure entangling blocks at the expense of additional single-qubit rotations.",
        "   - **Fully Connected Topology:** Optimization levels 0 through 3 consistently produce 8 two-qubit operations under the chosen basis gates (`['u', 'cx']`) and transpilation settings. This is an observed result for this configuration, not a universal theoretical lower bound.",
        "",
        "2. **Circuit Depth Invariance:**",
        "   - For this 4-vertex cycle QAOA circuit, gate-only depth is 18 on linear and 14 on fully connected connectivity across all optimization levels. While optimization levels 2 and 3 eliminate 2 CX gates on linear topology, the critical path length remains bounded by the routing dependencies.",
        "",
        "3. **Transpilation Time Overhead & Sample Size Considerations:**",
        "   - Classical transpilation duration generally increases from Level 0/1 to Level 2/3 as additional synthesis passes are invoked.",
        "   - **Timing Variability & Sample Size Note:** Each configuration uses five trials (N=5), so measured runtimes show variability in this sample and do not establish definitive latency distributions. Timing conclusions are preliminary and should be interpreted cautiously. Record the software versions and operating environment alongside the experiment results for reproducibility.",
        "   - **Candidate Choice for this Benchmark:** Comparing Level 2 and Level 3, both produce identical compiled structural metrics (12 CX gates on linear, 8 on fully connected, depth 18 on linear and 14 on fully connected). Level 2 is a candidate choice for this specific QAOA benchmark based on its observed gate reductions; the small sample and variable measured times do not establish a reliable timing advantage. Wider benchmark suites and varied topologies are needed before generalizing this finding to all NISQ QAOA circuits.",
        "",
        "## 4. Generated Plots",
        "- `plots/optimization/opt_level_vs_gate_counts.png`",
        "- `plots/optimization/opt_level_vs_circuit_depth.png`",
        "- `plots/optimization/opt_level_vs_transpilation_time.png`",
        "- `plots/optimization/optimization_tradeoff_pareto.png`",
    ])

    FINDINGS_DOC.parent.mkdir(parents=True, exist_ok=True)
    FINDINGS_DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Generated findings report at: {FINDINGS_DOC}")


def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()

    print("Generating optimization analysis plots...")
    p1 = plot_gate_counts(df, PLOTS_DIR)
    p2 = plot_circuit_depth(df, PLOTS_DIR)
    p3 = plot_transpilation_time(df, PLOTS_DIR)
    p4 = plot_tradeoff_pareto(df, PLOTS_DIR)

    print("Saved optimization plots:")
    for p in (p1, p2, p3, p4):
        print(f" - {p}")

    generate_findings_report(df)


if __name__ == "__main__":
    main()
