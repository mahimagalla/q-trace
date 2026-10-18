import pytest
from analysis.pareto import dominates, pareto_frontier


def test_strict_dominance():
    assert dominates([8, 14, 2], [12, 18, 3])


def test_no_dominance_when_tradeoff_exists():
    assert not dominates([8, 14, 5], [12, 18, 2])
    assert not dominates([12, 18, 2], [8, 14, 5])


def test_equal_candidates_do_not_strictly_dominate():
    assert not dominates([8, 14, 2], [8, 14, 2])


def test_frontier_identifies_non_dominated_candidates():
    candidates = [
        [8, 14, 4],  # Can 0: best depth (14)
        [12, 18, 5], # Can 1: dominated by 0 and 3
        [7, 16, 5],  # Can 2: best 2Q gates (7)
        [12, 18, 2], # Can 3: best time (2)
    ]
    assert pareto_frontier(candidates) == [0, 2, 3]


def test_duplicate_candidates_remain_on_frontier():
    assert pareto_frontier([[8, 14], [8, 14]]) == [0, 1]


def test_empty_frontier():
    assert pareto_frontier([]) == []


def test_mismatched_objective_dimensions():
    with pytest.raises(ValueError):
        dominates([1, 2], [1])


def test_non_finite_objectives_are_rejected():
    with pytest.raises(ValueError):
        dominates([1, float("nan")], [2, 3])
