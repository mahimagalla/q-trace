"""Integrated trade-off and Pareto analysis for Q-TRACE."""
from __future__ import annotations
import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence
from analysis.data_loader import (
    ConfigurationSummary,
    DataLoader,
    audit_compatibility,
)
from analysis.pareto import pareto_frontier


@dataclass(frozen=True)
class ParetoResult:
    """A configuration and its measured objective values."""
    topology: str
    optimization_level: int | None
    two_qubit_gates: int
    circuit_depth: int
    median_transpile_time_ms: float | None

    @property
    def label(self) -> str:
        return f"{self.topology} / Opt {self.optimization_level}"


def _require_finite(value: Any, name: str) -> float:
    """Validate a numeric analysis value."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite.")
    return result


def _validate_summaries(
    summaries: Sequence[ConfigurationSummary],
) -> None:
    """Reject empty or invalid configuration collections."""
    if not summaries:
        raise ValueError("No configuration summaries were provided.")
    seen: set[tuple[str, int | None]] = set()
    for summary in summaries:
        key = (summary.topology, summary.optimization_level)
        if key in seen:
            raise ValueError(f"Duplicate configuration: {key}")
        seen.add(key)
        if summary.optimization_level is None:
            raise ValueError(
                "Baseline records must not be included in Pareto analysis."
            )
        if summary.gate_count_2q < 0:
            raise ValueError("Two-qubit gate counts cannot be negative.")
        if summary.circuit_depth < 0:
            raise ValueError("Circuit depth cannot be negative.")


def build_pareto_results(
    summaries: Sequence[ConfigurationSummary],
) -> list[ParetoResult]:
    """Convert validated configuration summaries into analysis records."""
    _validate_summaries(summaries)
    results = []
    for summary in summaries:
        time_ms = summary.median_time_ms
        if time_ms is not None:
            time_ms = _require_finite(
                time_ms,
                f"Median transpilation time for {summary.topology}",
            )
            if time_ms < 0:
                raise ValueError("Transpilation time cannot be negative.")
        results.append(
            ParetoResult(
                topology=summary.topology,
                optimization_level=summary.optimization_level,
                two_qubit_gates=summary.gate_count_2q,
                circuit_depth=summary.circuit_depth,
                median_transpile_time_ms=time_ms,
            )
        )
    return results


def calculate_frontier(
    results: Sequence[ParetoResult],
    objectives: Sequence[str],
) -> list[ParetoResult]:
    """
    Calculate a Pareto frontier.
    Supported objectives:
      - two_qubit_gates
      - circuit_depth
      - median_transpile_time_ms
    All objectives are minimized. Configurations missing any selected
    objective are excluded from that particular frontier.
    """
    supported = {
        "two_qubit_gates",
        "circuit_depth",
        "median_transpile_time_ms",
    }
    if not objectives:
        raise ValueError("At least one objective is required.")
    if len(set(objectives)) != len(objectives):
        raise ValueError("Objectives must not contain duplicates.")
    unsupported = set(objectives) - supported
    if unsupported:
        raise ValueError(f"Unsupported objectives: {sorted(unsupported)}")
    eligible = []
    for result in results:
        values = [getattr(result, objective) for objective in objectives]
        if any(value is None for value in values):
            continue
        numeric_values = [
            _require_finite(value, objective)
            for objective, value in zip(objectives, values)
        ]
        eligible.append((result, numeric_values))
    if not eligible:
        return []
    vectors = [values for _, values in eligible]
    indices = pareto_frontier(vectors)
    return [eligible[index][0] for index in indices]


def _format_number(value: float | int | None, digits: int = 2) -> str:
    """Format numbers consistently in Markdown reports."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _markdown_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
) -> str:
    """Render a basic Markdown table."""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append(
            "| " + " | ".join(str(value) for value in row) + " |"
        )
    return "\n".join(lines)


def render_configuration_table(
    results: Sequence[ParetoResult],
) -> str:
    """Render the resource metrics for all configurations."""
    rows = [
        [
            result.topology,
            result.optimization_level,
            result.two_qubit_gates,
            result.circuit_depth,
            _format_number(result.median_transpile_time_ms),
        ]
        for result in results
    ]
    return _markdown_table(
        [
            "Topology",
            "Optimization level",
            "2Q gates",
            "Depth",
            "Median transpilation time (ms)",
        ],
        rows,
    )


def render_frontier_table(
    results: Sequence[ParetoResult],
) -> str:
    """Render configurations belonging to a Pareto frontier."""
    rows = [
        [
            result.topology,
            result.optimization_level,
            result.two_qubit_gates,
            result.circuit_depth,
            _format_number(result.median_transpile_time_ms),
        ]
        for result in results
    ]
    return _markdown_table(
        [
            "Topology",
            "Optimization level",
            "2Q gates",
            "Depth",
            "Median transpilation time (ms)",
        ],
        rows,
    )


def calculate_percentage_change(
    reference: float,
    comparison: float,
) -> float | None:
    """
    Calculate percentage change relative to a reference value.
    Returns None when the reference value is zero.
    """
    reference = _require_finite(reference, "Reference value")
    comparison = _require_finite(comparison, "Comparison value")
    if reference == 0:
        return None
    return ((comparison - reference) / reference) * 100.0


def analyze_dataset(
    loader: DataLoader,
) -> dict[str, Any]:
    """Calculate configuration metrics and Pareto frontiers."""
    if loader.validation_errors:
        raise ValueError(
            "Dataset validation failed:\n"
            + "\n".join(loader.validation_errors)
        )
    results = build_pareto_results(loader.get_all_summaries())
    primary = calculate_frontier(
        results,
        [
            "two_qubit_gates",
            "circuit_depth",
            "median_transpile_time_ms",
        ],
    )
    structural = calculate_frontier(
        results,
        ["two_qubit_gates", "circuit_depth"],
    )
    compilation = calculate_frontier(
        results,
        ["two_qubit_gates", "median_transpile_time_ms"],
    )
    return {
        "configurations": results,
        "primary_frontier": primary,
        "structural_frontier": structural,
        "compilation_frontier": compilation,
    }


def render_report(
    dataset_name: str,
    analysis: dict[str, Any],
) -> str:
    """Build a Markdown report from computed analysis results."""
    lines = [
        f"# Q-TRACE Trade-off Analysis: {dataset_name}",
        "",
        "All Pareto objectives are minimized. "
        "Transpilation times are descriptive measurements, "
        "not quantum execution times.",
        "",
        "## Configuration Metrics",
        "",
        render_configuration_table(analysis["configurations"]),
        "",
        "## Primary Pareto Frontier",
        "",
        "Objectives: two-qubit gates, circuit depth, "
        "and median transpilation time.",
        "",
        render_frontier_table(analysis["primary_frontier"]),
        "",
        "## Structural Pareto Frontier",
        "",
        "Objectives: two-qubit gates and circuit depth.",
        "",
        render_frontier_table(analysis["structural_frontier"]),
        "",
        "## Compilation Trade-off Frontier",
        "",
        "Objectives: two-qubit gates and median transpilation time.",
        "",
        render_frontier_table(analysis["compilation_frontier"]),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Q-TRACE compilation trade-offs."
    )
    parser.add_argument(
        "--csv",
        default="results/qtrace_results.csv",
        help="Path to the experiment CSV.",
    )
    parser.add_argument(
        "--name",
        default="Primary Dataset",
        help="Dataset name displayed in the report.",
    )
    parser.add_argument(
        "--output",
        default="results/tradeoff_analysis.md",
        help="Output Markdown report path.",
    )
    args = parser.parse_args()
    loader = DataLoader(args.csv)
    analysis = analyze_dataset(loader)
    report = render_report(args.name, analysis)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
