from math import inf
from typing import Hashable

import pytest

from addons.logical import Bool, Dist, FuzzySet, IndexSet, Prob, Real, Set, SetValue


class Graph[I: Hashable, T: SetValue](Set[I, T, Set[I, T]]):
	"""The generic nested-set shape; concrete graphs choose a row carrier."""


class UnweightedGraph[I: Hashable](Graph[I, Bool], truth=IndexSet):
	pass


class WeightedGraph[I: Hashable](Graph[I, Prob], truth=FuzzySet):
	pass


def test_boolean_algebra_is_closed() -> None:
	false = Bool(False)
	true = Bool(True)

	assert type(~false) is Bool
	assert type(false | true) is Bool
	assert hash(true) == hash(True)
	assert bool(~false)
	assert bool(false | true)
	assert not bool(false & true)
	assert not bool(true - true)
	assert bool(false ^ true)


def test_coordinate_endpoints_and_round_trips() -> None:
	assert float(Prob.maximum().dist) == inf
	assert float(Prob.minimum().dist) == 0.0
	assert float(Dist.maximum().prob) == 0.0
	assert float(Dist.minimum().prob) == 1.0

	for probability in (0.0, 0.1, 0.5, 0.9, 1.0):
		value = Prob(probability)
		assert float(value.dist.prob) == pytest.approx(probability)
		assert float(value.real.prob) == pytest.approx(probability)

	assert float(Real(-1_000).dist) == inf
	assert float(Real(-1_000).prob) == 0.0
	assert float(~Real(-1_000)) == 1_000.0
	assert float(Real(-1_000) + Real(-1_000)) == pytest.approx(-1_000.6931471805599)
	assert float(Real(-1_000) & Real(-1_000)) == -2_000.0
	assert float(Prob(1e-320).real) > -inf


def test_probability_operations_have_distinct_authorities() -> None:
	left = Prob(0.2)
	right = Prob(0.4)

	assert float((left + right).dist) == pytest.approx(float(left.dist + right.dist))
	assert float((left * right).dist) == pytest.approx(float(left.dist * right.dist))
	assert float(left & right) == pytest.approx(0.08)
	assert float(left | right) == pytest.approx(0.52)

	assert float(Prob.maximum() | right) == pytest.approx(float(right))
	assert float(Prob.maximum() & right) == 0.0


def test_index_set_membership_and_complement() -> None:
	value = IndexSet({1, 2})
	complement = ~value
	copy = value.union()

	assert set(value) == {1, 2}
	assert bool(value[1])
	assert not bool(value[3])
	assert not bool(complement[1])
	assert bool(complement[3])
	assert copy is not value
	copy.add(3)
	assert not bool(value[3])
	assert type(complement.get(3)) is Bool
	assert bool(complement.get(3))

	with pytest.raises(TypeError, match="implicit members"):
		set(complement)


def test_fuzzy_set_normalizes_values_and_preserves_weights() -> None:
	value = FuzzySet({1: 0.25})
	value[2] = 0.75
	value.setdefault(3, 0.5)

	assert type(value[1]) is Prob
	assert type(value[2]) is Prob
	assert type(value[3]) is Prob
	assert float(value[1]) == 0.25
	assert float(value[2]) == 0.75
	assert float(value[3]) == 0.5
	assert repr(value) == "{1: 0.25, 2: 0.75, 3: 0.5}"
	assert repr(~FuzzySet({1: 0.25})) == "~{1: 0.25}"


def test_fuzzy_set_operations_are_pointwise_over_implicit_absence() -> None:
	left = FuzzySet({1: 0.2})
	right = FuzzySet({1: 0.4, 2: 0.7})

	union = left | right
	intersection = left & right

	assert float(union[1]) == pytest.approx(0.52)
	assert float(union[2]) == pytest.approx(0.7)
	assert float(intersection[1]) == pytest.approx(0.08)
	assert float(intersection[2]) == 0.0
	assert float(abs(~left)) == pytest.approx(float(~abs(left)))


def test_mutation_preserves_type_and_coverage() -> None:
	value = FuzzySet({1: 0.2})
	identity = value

	value |= {2: 0.7}
	assert value is identity
	assert type(value[2]) is Prob
	assert float(value[2]) == pytest.approx(0.7)

	value.clear()
	assert value.indices == {1, 2}
	assert not value.complement
	assert not bool(value)
	assert float(value[1]) == 0.0
	assert float(value[2]) == 0.0


def test_nested_sets_accept_raw_adjacency_mappings() -> None:
	crisp = UnweightedGraph({0: {1}, 1: set()})
	weighted = WeightedGraph({0: {1: 0.75}, 1: {0: 1.0}})

	assert type(crisp[0]) is IndexSet
	assert type(crisp[0][1]) is Bool
	assert type(abs(crisp)) is Bool
	assert type(crisp.__eq__(crisp)) is Bool
	assert not bool(crisp[2][1])
	assert repr(crisp) == "{0: {1}, 1: set()}"

	assert type(weighted[0]) is FuzzySet
	assert type(weighted[0][1]) is Prob
	assert type(abs(weighted)) is Prob
	assert type(weighted.__eq__(weighted)) is Prob
	assert float(weighted[0][1]) == 0.75
	assert float(weighted[2][1]) == 0.0
	assert float(weighted[2][1].dist) == inf
	assert repr(weighted) == "{0: {1: 0.75}, 1: {0: 1.0}}"


def test_generic_set_requires_a_concrete_truth_carrier() -> None:
	with pytest.raises(TypeError, match="truth carrier"):
		Graph[int, Bool]()
