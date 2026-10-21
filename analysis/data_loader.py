"""
Data loader and schema validator for Q-TRACE experiment results.

This module loads, validates, and aggregates experimental runs across
different transpiler optimization levels and qubit connectivity topologies.
It handles schema validation, baseline separation, metadata checks,
and compatibility audits across multiple experiment files.
"""

from dataclasses import dataclass, field
import csv
import math
from pathlib import Path
import statistics
from typing import Any, Dict, List, Optional, Set, Tuple


from src.experiment_schema import CSV_COLUMNS

REQUIRED_COLUMNS = CSV_COLUMNS


@dataclass(frozen=True)
class ExperimentRecord:
    """Represents a single trial observation from a Q-TRACE experiment CSV."""
    experiment_id: str
    circuit_name: str
    graph_edges: str
    num_qubits: int
    qaoa_p: int
    parameter_values: str
    optimization_level: Optional[int]
    topology: str
    initial_layout: str
    routing_method: str
    basis_gates: str
    seed_transpiler: Optional[int]
    qiskit_version: str
    total_ops: int
    measurement_count: int
    gate_count_1q: int
    gate_count_2q: int
    circuit_depth: int
    explicit_swap_count: int
    input_swap_count: int
    transpile_time_seconds: Optional[float]
    trial_id: Optional[int]

    @property
    def is_baseline(self) -> bool:
        """Return True if this row represents an untranspiled baseline circuit."""
        return self.topology.lower() == "baseline" or self.optimization_level is None


@dataclass
class ConfigurationSummary:
    """Aggregated structural and timing metrics for a specific (topology, opt_level) configuration."""
    topology: str
    optimization_level: Optional[int]
    trial_count: int
    gate_count_1q: int
    gate_count_2q: int
    circuit_depth: int
    total_ops: int
    measurement_count: int
    explicit_swap_count: int
    input_swap_count: int
    qiskit_version: str
    basis_gates: str
    seed_transpiler: Optional[int]
    times_seconds: List[float] = field(default_factory=list)

    @property
    def times_ms(self) -> List[float]:
        return [t * 1000.0 for t in self.times_seconds]

    @property
    def median_time_seconds(self) -> Optional[float]:
        return statistics.median(self.times_seconds) if self.times_seconds else None

    @property
    def median_time_ms(self) -> Optional[float]:
        med = self.median_time_seconds
        return med * 1000.0 if med is not None else None

    @property
    def mean_time_ms(self) -> Optional[float]:
        return statistics.mean(self.times_ms) if self.times_ms else None

    @property
    def min_time_ms(self) -> Optional[float]:
        return min(self.times_ms) if self.times_ms else None

    @property
    def max_time_ms(self) -> Optional[float]:
        return max(self.times_ms) if self.times_ms else None

    @property
    def time_range_ms(self) -> Optional[float]:
        if not self.times_ms:
            return None
        return max(self.times_ms) - min(self.times_ms)

    @property
    def std_time_ms(self) -> Optional[float]:
        if len(self.times_ms) < 2:
            return 0.0
        return statistics.stdev(self.times_ms)


class DataLoader:
    """Loads, validates, and manages experimental runs from Q-TRACE CSV outputs."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.records: List[ExperimentRecord] = []
        self.baseline_records: List[ExperimentRecord] = []
        self.compiled_records: List[ExperimentRecord] = []
        self.summaries: Dict[Tuple[str, Optional[int]], ConfigurationSummary] = {}
        self.validation_errors: List[str] = []
        self._load_and_validate()

    def _load_and_validate(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Experiment file not found: {self.file_path}")

        with open(self.file_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            if headers != REQUIRED_COLUMNS:
                raise ValueError(
                    f"CSV schema error in {self.file_path.name}: expected columns in exact order "
                    f"{REQUIRED_COLUMNS}; got {headers}"
                )

            for line_no, row in enumerate(reader, start=2):
                record = self._parse_row(row, line_no)
                self.records.append(record)
                if record.is_baseline:
                    self.baseline_records.append(record)
                else:
                    self.compiled_records.append(record)

        self._build_summaries()

    def _parse_row(self, row: Dict[str, str], line_no: int) -> ExperimentRecord:
        def parse_opt_level(val: str) -> Optional[int]:
            v = val.strip()
            if not v or v.upper() in ("NA", "NONE", "BLANK", "N/A"):
                return None
            return int(v)

        def parse_optional_float(val: str) -> Optional[float]:
            v = val.strip()
            if not v or v.upper() in ("NA", "NONE", "BLANK", "N/A"):
                return None
            return float(v)

        def parse_optional_int(val: str) -> Optional[int]:
            v = val.strip()
            if not v or v.upper() in ("NA", "NONE", "BLANK", "N/A"):
                return None
            return int(v)

        try:
            return ExperimentRecord(
                experiment_id=row["experiment_id"].strip(),
                circuit_name=row["circuit_name"].strip(),
                graph_edges=row["graph_edges"].strip(),
                num_qubits=int(row["num_qubits"]),
                qaoa_p=int(row["qaoa_p"]),
                parameter_values=row["parameter_values"].strip(),
                optimization_level=parse_opt_level(row["optimization_level"]),
                topology=row["topology"].strip(),
                initial_layout=row["initial_layout"].strip(),
                routing_method=row["routing_method"].strip(),
                basis_gates=row["basis_gates"].strip(),
                seed_transpiler=parse_optional_int(row.get("seed_transpiler", "")),
                qiskit_version=row["qiskit_version"].strip(),
                total_ops=int(row["total_ops"]),
                measurement_count=int(row["measurement_count"]),
                gate_count_1q=int(row["gate_count_1q"]),
                gate_count_2q=int(row["gate_count_2q"]),
                circuit_depth=int(row["circuit_depth"]),
                explicit_swap_count=int(row["explicit_swap_count"]),
                input_swap_count=int(row["input_swap_count"]),
                transpile_time_seconds=parse_optional_float(row["transpile_time_seconds"]),
                trial_id=parse_optional_int(row.get("trial_id", "")),
            )
        except Exception as e:
            raise ValueError(f"Error parsing row {line_no} in {self.file_path.name}: {e}")

    def _build_summaries(self) -> None:
        """Group trials by (topology, optimization_level) and verify metric consistency."""
        grouped: Dict[Tuple[str, Optional[int]], List[ExperimentRecord]] = {}
        for rec in self.compiled_records:
            key = (rec.topology, rec.optimization_level)
            grouped.setdefault(key, []).append(rec)

        for (topology, opt_level), recs in grouped.items():
            # Check for consistent structural metrics across trials
            first = recs[0]
            for r in recs[1:]:
                if (
                    r.gate_count_1q != first.gate_count_1q
                    or r.gate_count_2q != first.gate_count_2q
                    or r.circuit_depth != first.circuit_depth
                    or r.total_ops != first.total_ops
                ):
                    self.validation_errors.append(
                        f"Inconsistent structural metrics detected for ({topology}, opt={opt_level}) "
                        f"across trials in {self.file_path.name}."
                    )

            times = [r.transpile_time_seconds for r in recs if r.transpile_time_seconds is not None]

            summary = ConfigurationSummary(
                topology=topology,
                optimization_level=opt_level,
                trial_count=len(recs),
                gate_count_1q=first.gate_count_1q,
                gate_count_2q=first.gate_count_2q,
                circuit_depth=first.circuit_depth,
                total_ops=first.total_ops,
                measurement_count=first.measurement_count,
                explicit_swap_count=first.explicit_swap_count,
                input_swap_count=first.input_swap_count,
                qiskit_version=first.qiskit_version,
                basis_gates=first.basis_gates,
                seed_transpiler=first.seed_transpiler,
                times_seconds=times,
            )
            self.summaries[(topology, opt_level)] = summary

    def get_summary(self, topology: str, opt_level: Optional[int]) -> Optional[ConfigurationSummary]:
        return self.summaries.get((topology, opt_level))

    def get_all_summaries(self) -> List[ConfigurationSummary]:
        return sorted(
            self.summaries.values(),
            key=lambda s: (s.topology, -1 if s.optimization_level is None else s.optimization_level),
        )

    def get_baseline_summary(self) -> Optional[ExperimentRecord]:
        if self.baseline_records:
            return self.baseline_records[0]
        return None


def audit_compatibility(datasets: Dict[str, DataLoader]) -> Dict[str, Any]:
    """
    Audits compatibility across multiple datasets.
    Compares environment versions (Qiskit), basis gates, layouts,
    and checks if results can be combined or must be analyzed separately.
    """
    report: Dict[str, Any] = {
        "datasets": {},
        "compatible_groups": {},
        "notes": [],
    }

    signatures: Dict[str, List[str]] = {}
    for name, loader in datasets.items():
        qiskit_vers = {r.qiskit_version for r in loader.records}
        basis_gates = {r.basis_gates for r in loader.records}
        seeds = {r.seed_transpiler for r in loader.records}
        initial_layouts = {r.initial_layout for r in loader.records}
        routing_methods = {r.routing_method for r in loader.compiled_records}
        topologies = {r.topology for r in loader.compiled_records}
        opt_levels = {r.optimization_level for r in loader.compiled_records}

        signature_parts = {
            "qiskit": qiskit_vers,
            "basis": basis_gates,
            "seed": seeds,
            "layout": initial_layouts,
            "routing": routing_methods,
        }
        sig = "_".join(
            f"{key}={sorted(str(value) if value is not None else 'unknown' for value in values)}"
            for key, values in signature_parts.items()
        )
        signatures.setdefault(sig, []).append(name)

        report["datasets"][name] = {
            "total_records": len(loader.records),
            "baseline_records": len(loader.baseline_records),
            "compiled_records": len(loader.compiled_records),
            "topologies": sorted(list(topologies)),
            "optimization_levels": sorted([x for x in opt_levels if x is not None]),
            "qiskit_versions": sorted(list(qiskit_vers)),
            "basis_gates": sorted(list(basis_gates)),
            "validation_errors": loader.validation_errors,
        }

    report["compatible_groups"] = signatures

    # Check cross-version differences
    all_qiskit = {ver for ds in report["datasets"].values() for ver in ds["qiskit_versions"]}
    if len(all_qiskit) > 1:
        report["notes"].append(
            f"Different Qiskit versions detected across datasets: {all_qiskit}. "
            "Timing comparisons between different versions must not be combined directly; "
            "separate analyses should be maintained."
        )

    return report
