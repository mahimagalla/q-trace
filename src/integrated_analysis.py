"""Validate and combine Q-TRACE connectivity and optimization datasets."""

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from src.experiment_schema import CSV_COLUMNS, write_csv_atomic
from src.transpilation import OPTIMIZATION_LEVELS
from analysis.pareto import pareto_frontier


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = {
    "connectivity": ROOT / "results" / "connectivity_experiments.csv",
    "optimization": ROOT / "results" / "optimization_experiments.csv",
}
DEFAULT_OUTPUT = ROOT / "results" / "integrated_analysis_summary.csv"
PROVENANCE = {
    "connectivity": "Qiskit 2.5.1; Python 3.14.2 (historical CSV provenance)",
    "optimization": "Qiskit 2.5.2; Python 3.14.4 (historical CSV provenance)",
}
CONFIGURATIONS = {
    (topology, level)
    for topology in ("linear", "fully_connected")
    for level in OPTIMIZATION_LEVELS
}
INTEGER_METRICS = (
    "num_qubits", "qaoa_p", "total_ops", "measurement_count", "gate_count_1q",
    "gate_count_2q", "circuit_depth", "explicit_swap_count", "input_swap_count",
)
SUMMARY_COLUMNS = [
    "dataset", "source_file", "provenance", "topology", "optimization_level",
    "trial_count", "gate_count_1q", "gate_count_2q", "circuit_depth", "total_ops",
    "measurement_count", "explicit_swap_count", "input_swap_count",
    "median_transpile_time_seconds", "pareto_structural",
]


def _read_dataset(name: str, path: str | Path) -> tuple[list[dict], dict]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Missing {name} input CSV: {source}")
    with source.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != CSV_COLUMNS:
            raise ValueError(
                f"{source}: expected exact 22-column schema; got {reader.fieldnames}"
            )
        rows = list(reader)
    if len(rows) != 41:
        raise ValueError(f"{source}: expected 41 data rows, found {len(rows)}")

    baselines = [row for row in rows if row["experiment_id"] == "EXP-BASELINE"]
    if len(baselines) != 1 or baselines[0]["topology"] != "baseline":
        raise ValueError(f"{source}: expected exactly one untranspiled EXP-BASELINE row")
    baseline = baselines[0]
    if (baseline["graph_edges"] != "0-1;1-2;2-3;3-0"
            or baseline["initial_layout"] != "0-0;1-1;2-2;3-3"
            or baseline["optimization_level"].strip()
            or baseline["trial_id"].strip()
            or baseline["transpile_time_seconds"].strip()):
        raise ValueError(f"{source}: baseline metadata is inconsistent with an untranspiled circuit")
    for field in ("circuit_name", "graph_edges", "parameter_values", "initial_layout",
                  "basis_gates", "qiskit_version"):
        if not baseline[field].strip():
            raise ValueError(f"{source}: baseline field {field} is required")
    for field in INTEGER_METRICS:
        try:
            value = int(baseline[field])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{source}: baseline {field} must be an integer") from exc
        if value < 0:
            raise ValueError(f"{source}: baseline {field} cannot be negative")
    if (int(baseline["num_qubits"]) != 4 or int(baseline["gate_count_2q"]) != 4
            or int(baseline["total_ops"]) != 16 or int(baseline["circuit_depth"]) != 6):
        raise ValueError(f"{source}: baseline metrics do not match the QAOA input circuit")
    if int(baseline["input_swap_count"]) != 0:
        raise ValueError(f"{source}: baseline input_swap_count must be zero")

    compiled = [row for row in rows if row["experiment_id"] != "EXP-BASELINE"]
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    seen_ids = set()
    for row in compiled:
        try:
            level = int(row["optimization_level"])
            trial = int(row["trial_id"])
            int(row["seed_transpiler"])
            values = {field: int(row[field]) for field in INTEGER_METRICS}
            time_value = float(row["transpile_time_seconds"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{source}: nonnumeric or missing trial metric in {row}") from exc
        if row["topology"] not in {"linear", "fully_connected"} or level not in OPTIMIZATION_LEVELS:
            raise ValueError(f"{source}: invalid topology/optimization level: {row}")
        if (row["graph_edges"] != "0-1;1-2;2-3;3-0"
                or row["initial_layout"] != "0-0;1-1;2-2;3-3"
                or values["num_qubits"] != 4):
            raise ValueError(f"{source}: trial metadata is inconsistent with the four-qubit protocol")
        if trial not in range(1, 6) or not math.isfinite(time_value) or time_value <= 0:
            raise ValueError(f"{source}: invalid trial id or transpilation time: {row}")
        if any(value < 0 for value in values.values()):
            raise ValueError(f"{source}: structural metrics cannot be negative: {row}")
        for field in ("experiment_id", "circuit_name", "graph_edges", "parameter_values",
                      "initial_layout", "routing_method", "basis_gates", "qiskit_version"):
            if not row[field].strip():
                raise ValueError(f"{source}: required trial field {field} is blank")
        identity = (row["experiment_id"], trial)
        if identity in seen_ids:
            raise ValueError(f"{source}: duplicate experiment/trial identity {identity}")
        seen_ids.add(identity)
        row["_level"] = level
        row["_trial"] = trial
        row["_time"] = time_value
        row["_metrics"] = values
        groups[(row["topology"], level)].append(row)
    if set(groups) != CONFIGURATIONS:
        raise ValueError(f"{source}: configuration coverage mismatch: {sorted(groups)}")

    summaries = {}
    for key, trials in groups.items():
        ids = [row["_trial"] for row in trials]
        if sorted(ids) != [1, 2, 3, 4, 5]:
            raise ValueError(f"{source}: {key} must have unique trials 1 through 5; got {ids}")
        metric_rows = [row["_metrics"] for row in trials]
        if any(item != metric_rows[0] for item in metric_rows[1:]):
            raise ValueError(f"{source}: structural metrics vary across trials for {key}")
        versions = {row["qiskit_version"] for row in trials}
        if len(versions) != 1 or not next(iter(versions)):
            raise ValueError(f"{source}: inconsistent or missing Qiskit version")
        summaries[key] = {
            **metric_rows[0],
            "trial_count": len(trials),
            "median_transpile_time_seconds": median(row["_time"] for row in trials),
        }
    summaries[("baseline", None)] = {
        **{field: int(baseline[field]) for field in INTEGER_METRICS},
        "trial_count": 0,
        "median_transpile_time_seconds": "",
    }
    return rows, summaries


def analyze(connectivity_path=DEFAULT_INPUTS["connectivity"],
            optimization_path=DEFAULT_INPUTS["optimization"],
            output_path=DEFAULT_OUTPUT) -> list[dict]:
    """Validate both datasets, combine comparable structure, and save summaries."""
    loaded = {
        "connectivity": _read_dataset("connectivity", connectivity_path),
        "optimization": _read_dataset("optimization", optimization_path),
    }
    for key in CONFIGURATIONS:
        left = loaded["connectivity"][1][key]
        right = loaded["optimization"][1][key]
        comparable = ("gate_count_1q", "gate_count_2q", "circuit_depth", "total_ops",
                      "measurement_count", "explicit_swap_count", "input_swap_count")
        if any(left[field] != right[field] for field in comparable):
            raise ValueError(f"Structural metrics disagree for matching configuration {key}")

    # Pareto objectives use structural resource counts only. Historical timings
    # remain separate by dataset due to known Python/Qiskit provenance differences.
    config_order = sorted(CONFIGURATIONS)
    vectors = [
        (loaded["connectivity"][1][key]["gate_count_2q"],
         loaded["connectivity"][1][key]["circuit_depth"])
        for key in config_order
    ]
    frontier = {config_order[index] for index in pareto_frontier(vectors)}

    output_rows = []
    for dataset, (rows, summaries) in loaded.items():
        source = Path(connectivity_path if dataset == "connectivity" else optimization_path)
        for (topology, level), summary in sorted(
            summaries.items(), key=lambda item: (item[0][0], -1 if item[0][1] is None else item[0][1])
        ):
            output_rows.append({
                "dataset": dataset,
                "source_file": source.name,
                "provenance": PROVENANCE[dataset],
                "topology": topology,
                "optimization_level": "" if level is None else level,
                **{field: summary[field] for field in (
                    "trial_count", "gate_count_1q", "gate_count_2q", "circuit_depth",
                    "total_ops", "measurement_count", "explicit_swap_count",
                    "input_swap_count", "median_transpile_time_seconds",
                )},
                "pareto_structural": (topology, level) in frontier,
            })
    write_csv_atomic(output_path, output_rows, fieldnames=SUMMARY_COLUMNS)

    print("Integrated Q-TRACE analysis")
    print("Comparable across sources: gate counts, gate-only depth, total operations, measurements, SWAP metrics.")
    print("Timing medians are reported per source and are not pooled (different historical Python/Qiskit versions).")
    print("Pareto objectives (minimized): two-qubit gate count and gate-only circuit depth; timing excluded.")
    for dataset, (_, summaries) in loaded.items():
        print(f"\n{dataset} - {PROVENANCE[dataset]}")
        for (topology, level), item in sorted(summaries.items()):
            if level is None:
                print(f"  baseline         : 2Q={item['gate_count_2q']:2}, depth={item['circuit_depth']:2}; untranspiled")
                continue
            median_time_ms = item["median_transpile_time_seconds"] * 1000
            print(f"  {topology:16} Opt {level}: 2Q={item['gate_count_2q']:2}, "
                  f"depth={item['circuit_depth']:2}, median transpile time={median_time_ms:.3f} ms, "
                  f"Pareto={'yes' if (topology, level) in frontier else 'no'}")
    print(f"\nCombined summary saved to: {output_path}")
    return output_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connectivity", type=Path, default=DEFAULT_INPUTS["connectivity"])
    parser.add_argument("--optimization", type=Path, default=DEFAULT_INPUTS["optimization"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    analyze(args.connectivity, args.optimization, args.output)


if __name__ == "__main__":
    main()
