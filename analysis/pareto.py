"""Pareto-frontier analysis for Q-TRACE experiments."""
from __future__ import annotations
import math
from collections.abc import Callable, Sequence
from typing import Any


def dominates(
    candidate_a: Sequence[float],
    candidate_b: Sequence[float],
) -> bool:
    """
    Return True if candidate_a Pareto-dominates candidate_b.
    All objectives are minimized.
    A dominates B when:
      1. A is no worse than B on every objective.
      2. A is strictly better than B on at least one objective.
    Both candidates must contain the same number of objectives.
    """
    if len(candidate_a) != len(candidate_b):
        raise ValueError(
            "Candidates must have the same number of objectives."
        )
    if not candidate_a:
        raise ValueError("Candidates must contain at least one objective.")
    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        for value in (*candidate_a, *candidate_b)
    ):
        raise TypeError("All objective values must be numeric.")
    if any(
        not math.isfinite(value)
        for value in (*candidate_a, *candidate_b)
    ):
        raise ValueError("Objective values must be finite.")
    return (
        all(a <= b for a, b in zip(candidate_a, candidate_b))
        and any(a < b for a, b in zip(candidate_a, candidate_b))
    )


def pareto_frontier(
    candidates: Sequence[Sequence[float]],
) -> list[int]:
    """
    Return indices of candidates on the Pareto frontier.
    Duplicate objective vectors are retained because neither strictly
    dominates the other.
    """
    if not candidates:
        return []
    objective_count = len(candidates[0])
    if objective_count == 0:
        raise ValueError("Candidates must contain at least one objective.")
    for candidate in candidates:
        if len(candidate) != objective_count:
            raise ValueError(
                "All candidates must have the same number of objectives."
            )
    frontier = []
    for i, candidate in enumerate(candidates):
        dominated = any(
            i != j and dominates(other, candidate)
            for j, other in enumerate(candidates)
        )
        if not dominated:
            frontier.append(i)
    return frontier
