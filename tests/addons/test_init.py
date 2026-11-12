"""Exact difficulty ordering, Boolean endpoints, and probabilistic arithmetic."""

from __future__ import annotations


from fractions import Fraction
from itertools import product
from operator import add, and_, matmul, or_, sub, xor

import pytest

from addons import Bool, Prob, Dist


class TestScalar:

	components = ((0, 1), (1, 3), (1, 2), (1, 1), (2, 1), (3, 1), (1, 0))
	pairs = tuple(product(components, repeat = 2))
	associative = (add, matmul, and_, or_)
	carriers = (Dist, Bool, Prob)

	class Specialized(Dist):
		__slots__ = ()

	@staticmethod
	def probability(value: Dist) -> Fraction:
		return Fraction(value.denom, value.numer + value.denom)

	@pytest.mark.parametrize("left, right", pairs)
	def test_comparisons_follow_exact_difficulty(self, left: tuple[int, int], right: tuple[int, int]):
		a, b = Dist(*left), Dist(*right)
		p, q = self.probability(a), self.probability(b)

		assert (a == b) == (p == q)
		assert (a != b) == (p != q)
		assert (a < b) == (p > q)
		assert (a <= b) == (p >= q)
		assert (a > b) == (p < q)
		assert (a >= b) == (p <= q)

	def test_order_is_transitive_and_complement_reverses_it(self):
		values = [Dist(*pair) for pair in self.components]

		assert sorted(reversed(values)) == values
		assert Dist.min() < Dist(1, 1) < Dist.max()

		for a, b, c in product(values, repeat = 3):
			if a <= b <= c:
				assert a <= c

			assert (a <= b) == (~a >= ~b)

	def test_comparison_does_not_round_through_float(self):
		scale = 10 ** 100
		a, b = Dist(scale, 1), Dist(scale + 1, 1)

		assert float(a) == float(b)
		assert a < b
		assert a != b

	def test_normalized_values_and_subclasses_hash_equally(self):
		a, b, c = Dist(1, 2), Dist(2, 4), self.Specialized(3, 6)

		assert a == b == c == a
		assert hash(a) == hash(b) == hash(c)
		assert len({a, b, c}) == 1
		assert Dist(0, 9) == Dist.min()
		assert Dist(0, 0) == Dist(9, 0) == Dist.max()
		assert self.Specialized.min() < c

	def test_endpoint_equality_and_hashing_agree_across_carriers(self):
		for bound in ("min", "max"):
			values = [getattr(cls, bound)() for cls in self.carriers]

			assert values[0] == values[1] == values[2]
			assert len({hash(value) for value in values}) == 1
			assert len(set(values)) == 1

	@pytest.mark.parametrize("left, right", pairs)
	def test_operations_keep_their_probability_meaning(self, left: tuple[int, int], right: tuple[int, int]):
		a, b = Dist(*left), Dist(*right)
		p, q = self.probability(a), self.probability(b)
		expected_sum = p * q / (p + q - p * q) if p or q else Fraction(0)
		expected_dual = (p + q - 2 * p * q) / (1 - p * q) if p * q != 1 else Fraction(1)

		assert self.probability(a + b) == expected_sum
		assert self.probability(a @ b) == expected_dual
		assert self.probability(a & b) == p * q
		assert self.probability(a | b) == p + q - p * q
		assert self.probability(a - b) == p * (1 - q)
		assert self.probability(a ^ b) == p + q - 2 * p * q
		assert self.probability(~a) == 1 - p
		assert ~~a == a
		assert ~(a & b) == (~a | ~b)
		assert ~(a + b) == (~a @ ~b)

	def test_associative_operations_remain_associative(self):
		values = [Dist(*pair) for pair in self.components]

		for operation in self.associative:
			for a, b, c in product(values, repeat = 3):
				assert operation(operation(a, b), c) == operation(a, operation(b, c))

	@pytest.mark.parametrize("cls", carriers)
	def test_state_is_read_only(self, cls: type[Dist]):
		value = cls.min()

		assert not hasattr(value, "__dict__")

		with pytest.raises(AttributeError):
			value.numer = 3

		with pytest.raises(AttributeError):
			del value.denom

		value.__init__()

		assert value == cls.min()

	@pytest.mark.parametrize("cls", carriers)
	@pytest.mark.parametrize("numer, denom", [(-1, 1), (1, -1), (-1, -1)])
	def test_negative_components_are_rejected(self, cls: type[Dist], numer: int, denom: int):
		with pytest.raises(ValueError):
			cls(numer, denom)

	def test_operations_and_constants_preserve_subclasses(self):
		a, b = self.Specialized(1, 2), self.Specialized(2, 1)

		for value in (a + b, a @ b, a & b, a | b, a - b, a ^ b, ~a):
			assert type(value) is self.Specialized

		for value in (self.Specialized.min(), self.Specialized.max()):
			assert type(value) is self.Specialized

	def test_shared_carrier_has_no_product_or_midpoint(self):
		assert not hasattr(Dist, "__mul__")
		assert not hasattr(Dist, "mid")


class TestBool:

	components = ((0, 1, True), (0, 9, True), (1, 0, False), (9, 0, False), (0, 0, False))
	pairs = tuple(product((False, True), repeat = 2))

	class Specialized(Bool):
		__slots__ = ()

	@pytest.mark.parametrize("numer, denom, expected", components)
	def test_constructor_accepts_only_normalized_endpoints(self, numer: int, denom: int, expected: bool):
		value = Bool(numer, denom)

		assert bool(value) is expected
		assert float(value) == float(expected)
		assert (value.numer, value.denom) == ((0, 1) if expected else (1, 0))

	@pytest.mark.parametrize("numer, denom", [(1, 1), (1, 3), (3, 1), (2, 4)])
	def test_constructor_rejects_intermediate_values(self, numer: int, denom: int):
		with pytest.raises(ValueError):
			Bool(numer, denom)

	@pytest.mark.parametrize("left, right", pairs)
	def test_every_logical_operation_is_closed_and_matches_bool(self, left: bool, right: bool):
		a = Bool.min() if left else Bool.max()
		b = Bool.min() if right else Bool.max()
		operations = (
			(add, left and right),
			(matmul, left or right),
			(and_, left and right),
			(or_, left or right),
			(sub, left and not right),
			(xor, left != right),
		)

		for operation, expected in operations:
			value = operation(a, b)

			assert type(value) is Bool
			assert bool(value) is expected
			assert (value.numer, value.denom) in ((0, 1), (1, 0))

		assert bool(~a) is not left

	def test_no_midpoint_or_product_is_exposed(self):
		assert not hasattr(Bool, "mid")
		assert not hasattr(Bool, "__mul__")

	def test_default_and_bounds_keep_the_component_contract(self):
		assert Bool() == Bool.min()
		assert bool(Bool.min())
		assert not Bool.max()
		assert Bool.min() < Bool.max()
		assert all((Bool.min(), Bool.min()))
		assert not any((Bool.max(), Bool.max()))

	def test_subclasses_keep_their_type_without_an_instance_dictionary(self):
		a, b = self.Specialized.min(), self.Specialized.max()

		for value in (a, b, a + b, a @ b, a & b, a | b, a - b, a ^ b, ~a):
			assert type(value) is self.Specialized
			assert not hasattr(value, "__dict__")


class TestProb:

	components = TestScalar.components
	pairs = tuple(product(components, repeat = 2))

	class Specialized(Prob):
		__slots__ = ()

	@pytest.mark.parametrize("left, right", pairs)
	def test_product_is_self_dual_and_keeps_its_probability_meaning(self, left: tuple[int, int], right: tuple[int, int]):
		a, b = Prob(*left), Prob(*right)
		p, q = TestScalar.probability(a), TestScalar.probability(b)
		denominator = p * q + (1 - p) * (1 - q)
		expected = p * q / denominator if denominator else Fraction(1, 2)

		assert TestScalar.probability(a * b) == expected
		assert ~(a * b) == ~a * ~b
		assert a & b == (a + b) + (a * b)
		assert a | b == (a @ b) @ (a * b)
		assert type(a * b) is Prob

	def test_self_dual_product_is_deliberately_not_associative_at_conflict(self):
		false, true, three_quarters = Prob.max(), Prob.min(), Prob(1, 3)

		assert false * true == true * false == Prob.mid()
		assert (false * true) * three_quarters == three_quarters
		assert false * (true * three_quarters) == Prob.mid()

	def test_midpoint_is_the_multiplicative_identity(self):
		assert Prob.min() < Prob.mid() < Prob.max()
		assert float(Prob.mid()) == 0.5

		for pair in self.components:
			value = Prob(*pair)

			assert Prob.mid() * value == value * Prob.mid() == value

	def test_product_accepts_boolean_endpoints_without_coercing_its_result(self):
		assert Prob.min() * Bool.max() == Prob.mid()
		assert type(Prob.min() * Bool.max()) is Prob

	def test_subclasses_keep_their_type(self):
		a, b = self.Specialized(1, 2), self.Specialized(2, 1)

		for value in (a + b, a @ b, a * b, a & b, a | b, a - b, a ^ b, ~a):
			assert type(value) is self.Specialized
			assert not hasattr(value, "__dict__")

		assert type(self.Specialized.mid()) is self.Specialized
		assert type(self.Specialized.min() * self.Specialized.max()) is self.Specialized
