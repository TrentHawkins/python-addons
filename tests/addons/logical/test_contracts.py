"""The abstract contracts of §2 — each law, on every concrete carrier that claims it."""

from __future__ import annotations


from typing import Any

import pytest

from addons.logical import Bool, Boolean, Coded, Dist, Frac, IndexSet, Node, Prob

from .conftest import GRADED_RUNGS, RUNGS, carrier, sample


SCALARS = (Dist, Prob, Bool)


def values(cls: type[Frac]) -> list[Frac]:
	return [cls.minimum(), cls.midimum(), cls.maximum()] if cls is not Bool else [Bool(True), Bool(False)]


class TestBounded:

	@pytest.mark.parametrize("cls", SCALARS)
	def test_the_bounds_are_the_extremes(self, cls: type[Frac]):
		for value in values(cls):
			assert cls.maximum() <= value <= cls.minimum()

	@pytest.mark.parametrize("cls", SCALARS)
	def test_the_names_read_against_the_ordering(self, cls: type[Frac]):
		"""`minimum` names the least *difficulty*, so it is the greatest truth: `<=` is `issubset`."""
		assert bool(cls.minimum()) and not bool(cls.maximum())
		assert cls.maximum() <= cls.minimum() and not cls.minimum() <= cls.maximum()

	@pytest.mark.parametrize("cls", RUNGS)
	def test_a_node_bound_is_the_bound_as_a_background(self, cls: Any):
		assert abs(cls.minimum()) == carrier(cls).minimum()
		assert abs(cls.maximum()) == carrier(cls).maximum()


class TestInvertible:

	@pytest.mark.parametrize("cls", SCALARS)
	def test_inversion_is_an_involution(self, cls: type[Frac]):
		for value in values(cls):
			assert ~~value == value

	@pytest.mark.parametrize("cls", SCALARS)
	def test_it_swaps_the_bounds(self, cls: type[Frac]):
		assert ~cls.minimum() == cls.maximum()
		assert ~cls.maximum() == cls.minimum()

	@pytest.mark.parametrize("cls", RUNGS)
	def test_a_node_inverts_pointwise_and_involutes(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 7)

		assert ~~node == node


class TestOperable:

	@pytest.mark.parametrize("cls", SCALARS)
	def test_de_morgan(self, cls: type[Frac]):
		for a in values(cls):
			for b in values(cls):
				assert ~(a | b) == ~a & ~b
				assert ~(a & b) == ~a | ~b

	@pytest.mark.parametrize("cls", SCALARS)
	def test_difference_and_symmetric_difference(self, cls: type[Frac]):
		for a in values(cls):
			for b in values(cls):
				assert a - b == a & ~b
				assert a ^ b == (a | b) - (a & b)

	@pytest.mark.parametrize("cls", SCALARS)
	def test_the_folds_carry_the_right_identity(self, cls: type[Frac]):
		assert cls.any([]) == cls.maximum()
		assert cls.all([]) == cls.minimum()

		for value in values(cls):
			assert cls.any([value]) == value
			assert cls.all([value]) == value

	@pytest.mark.parametrize("cls", SCALARS)
	def test_the_folds_agree_with_the_operators(self, cls: type[Frac]):
		items = values(cls)

		assert cls.any(items) == items[0] | items[-1] | items[len(items) // 2]
		assert cls.all(items) == items[0] & items[-1] & items[len(items) // 2]

	@pytest.mark.parametrize("cls", SCALARS)
	def test_reflected_operators_agree(self, cls: type[Frac]):
		a, b = values(cls)[0], values(cls)[-1]

		assert a.__ror__(b) == b | a and a.__rand__(b) == b & a and a.__rxor__(b) == b ^ a


class TestOrder:

	@pytest.mark.parametrize("cls", SCALARS)
	def test_equality_is_two_sided_comparison(self, cls: type[Frac]):
		for a in values(cls):
			for b in values(cls):
				assert (a == b) == (a <= b and a >= b)
				assert (a != b) == (not a == b)

	@pytest.mark.parametrize("cls", SCALARS)
	def test_strict_orders_derive(self, cls: type[Frac]):
		for a in values(cls):
			for b in values(cls):
				assert (a < b) == (a <= b and a != b)
				assert (a > b) == (a >= b and a != b)

	@pytest.mark.parametrize("cls", SCALARS)
	def test_totality(self, cls: type[Frac]):
		for a in values(cls):
			for b in values(cls):
				assert a <= b or a >= b

	@pytest.mark.parametrize("cls", RUNGS)
	def test_subset_and_superset_are_the_orderings(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 11)

		assert node.issubset(node) and node.issuperset(node)
		assert cls.minimum().issuperset(node) and cls.maximum().issubset(node)


class TestSeparable:

	def test_disjointness_is_an_empty_intersection(self):
		a, b, c = IndexSet(["x"]), IndexSet(["y"]), IndexSet(["x", "z"])

		assert a.isdisjoint(b) and not a.isdisjoint(c)

	@pytest.mark.parametrize("cls", RUNGS)
	def test_an_empty_node_is_false_and_a_complemented_one_is_true(self, cls: Any):
		assert not cls()
		assert cls(carrier(cls).minimum())


class TestCoded:

	@pytest.mark.parametrize("cls", SCALARS)
	def test_the_round_trip_is_faithful(self, cls: type[Frac]):
		for value in values(cls):
			assert cls.encode(*value.decode()) == value
			assert value.decoded == value.decode()

	@pytest.mark.parametrize("cls", SCALARS)
	def test_a_scalar_is_its_own_contraction(self, cls: type[Frac]):
		for value in values(cls):
			assert abs(value) == value

	def test_coded_is_contained_in_boolean(self):
		assert issubclass(Coded, Boolean)
		assert all(issubclass(cls, Coded) for cls in SCALARS)
		assert issubclass(Node, Boolean) and not issubclass(Node, Coded)

	@pytest.mark.parametrize("cls", GRADED_RUNGS)
	def test_a_node_is_not_faithful_which_is_why_it_is_not_coded(self, cls: Any):
		assert not hasattr(cls, "decode")


class TestAbstractness:

	@pytest.mark.parametrize("cls", [Frac, Coded, Boolean])
	def test_the_contracts_refuse_instantiation(self, cls: type):
		with pytest.raises(TypeError):
			cls()  # pyright: ignore[reportAbstractUsage]
