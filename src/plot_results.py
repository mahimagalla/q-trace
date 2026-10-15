
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULTS_PATH = Path("results") / "qtrace_results.csv"
PLOTS_DIR = Path("plots")


def main():
    df = pd.read_csv(RESULTS_PATH)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    structural = (
        df.groupby(["topology", "optimization_level"], as_index=False)
        .agg(
            gate_count_2q=("gate_count_2q", "median"),
            circuit_depth=("circuit_depth", "median"),
        )
    )

    for metric, ylabel, filename in [
        ("gate_count_2q", "Two-qubit gate count", "two_qubit_gates.png"),
        ("circuit_depth", "Circuit depth", "circuit_depth.png"),
    ]:
        fig, ax = plt.subplots()

        for topology in ("linear", "fully_connected"):
            subset = structural[structural["topology"] == topology]
            ax.plot(
                subset["optimization_level"],
                subset[metric],
                marker="o",
                label=topology.replace("_", " ").title(),
            )

        ax.set_xlabel("Optimization level")
        ax.set_ylabel(ylabel)
        ax.set_xticks([0, 1, 2, 3])
        ax.legend()
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / filename, dpi=200)
        plt.close(fig)

    timing = (
        df.groupby(["topology", "optimization_level"])["transpile_time_seconds"]
        .agg(["median", "min", "max"])
        .reset_index()
    )

    fig, ax = plt.subplots()

    for topology in ("linear", "fully_connected"):
        subset = timing[timing["topology"] == topology]
        median_ms = subset["median"] * 1000
        lower_error = (subset["median"] - subset["min"]) * 1000
        upper_error = (subset["max"] - subset["median"]) * 1000

        ax.errorbar(
            subset["optimization_level"],
            median_ms,
            yerr=[lower_error, upper_error],
            marker="o",
            capsize=4,
            label=topology.replace("_", " ").title(),
        )

    ax.set_xlabel("Optimization level")
    ax.set_ylabel("Transpilation time (ms)")
    ax.set_xticks([0, 1, 2, 3])
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "transpilation_time.png", dpi=200)
    plt.close(fig)

    print("Saved plots:")
    for name in (
        "two_qubit_gates.png",
        "circuit_depth.png",
        "transpilation_time.png",
    ):
        print(PLOTS_DIR / name)


if __name__ == "__main__":
    main()
