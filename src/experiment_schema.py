"""Shared CSV schema and safe serialization helpers for Q-TRACE."""

import csv
import os
import tempfile
from pathlib import Path

import qiskit

from src.metrics import collect_metrics
from src.transpilation import BASIS_GATES, NUM_QUBITS, SEED_TRANSPILER


CSV_COLUMNS = [
    "experiment_id", "circuit_name", "graph_edges", "num_qubits", "qaoa_p",
    "parameter_values", "optimization_level", "topology", "initial_layout",
    "routing_method", "basis_gates", "seed_transpiler", "qiskit_version",
    "total_ops", "measurement_count", "gate_count_1q", "gate_count_2q",
    "circuit_depth", "explicit_swap_count", "input_swap_count",
    "transpile_time_seconds", "trial_id",
]
GRAPH_EDGES_SERIALIZED = "0-1;1-2;2-3;3-0"
INITIAL_LAYOUT_SERIALIZED = "0-0;1-1;2-2;3-3"


def baseline_record(circuit, *, qiskit_version: str | None = None) -> dict:
    """Measure and describe the original untranspiled benchmark circuit."""
    from src.experiment_runner import BETA, GAMMA

    return {
        "experiment_id": "EXP-BASELINE",
        "circuit_name": "QAOA_MaxCut_Cycle4_p1",
        "graph_edges": GRAPH_EDGES_SERIALIZED,
        "num_qubits": NUM_QUBITS,
        "qaoa_p": 1,
        "parameter_values": f"gamma={GAMMA},beta={BETA}",
        "optimization_level": "",
        "topology": "baseline",
        "initial_layout": INITIAL_LAYOUT_SERIALIZED,
        "routing_method": "",
        "basis_gates": str(BASIS_GATES),
        "seed_transpiler": SEED_TRANSPILER,
        "qiskit_version": qiskit_version or qiskit.__version__,
        **collect_metrics(circuit),
        "input_swap_count": 0,
        "transpile_time_seconds": "",
        "trial_id": "",
    }


def write_csv_atomic(
    path: str | Path, rows: list[dict], *, fieldnames: list[str] = CSV_COLUMNS
) -> None:
    """Write a CSV to a sibling temporary file and atomically replace path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise")
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
