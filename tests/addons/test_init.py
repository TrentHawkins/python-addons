"""The standalone scalar: exact probability ordering and difficulty arithmetic."""

from __future__ import annotations


from fractions import Fraction
from itertools import product
from operator import add, and_, ge, gt, le, lt, matmul, or_
from typing import Any

import pytest

from addons import scalar


class TestScalar:

	components = ((1, 0), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (0, 1))
	pairs = tuple(product(components, repeat = 2))
	foreign = (0, 1, 0.5, None, object())
	associative = (add, matmul, and_, or_)
	ordering = (lt, le, gt, ge)

	class Specialized(scalar):
		__slots__ = ()

	@staticmethod
	def probability(value: scalar) -> Fraction:
		return Fraction(value.denom, value.numer + value.denom)

	@pytest.mark.parametrize("left, right", pairs)
	def test_comparisons_follow_exact_probability(self, left: tuple[int, int], right: tuple[int, int]):
		a, b = scalar(*left), scalar(*right)
		p, q = self.probability(a), self.probability(b)

		assert (a == b) == (p == q)
		assert (a != b) == (p != q)
		assert (a < b) == (p < q)
		assert (a <= b) == (p <= q)
		assert (a > b) == (p > q)
		assert (a >= b) == (p >= q)

	def test_order_is_transitive_and_complement_reverses_it(self):
		values = [scalar(*pair) for pair in self.components]

		assert sorted(reversed(values)) == values
		assert scalar.max() < scalar.mid() < scalar.min()

		for a, b, c in product(values, repeat = 3):
			if a <= b <= c:
				assert a <= c

			assert (a <= b) == (~a >= ~b)

	def test_comparison_does_not_round_through_float(self):
		scale = 10 ** 100
		a, b = scalar(scale, 1), scalar(scale + 1, 1)

		assert float(a) == float(b)
		assert b < a
		assert a != b

	def test_normalized_values_and_subclasses_hash_equally(self):
		a, b, c = scalar(1, 2), scalar(2, 4), self.Specialized(3, 6)

		assert a == b == c == a
		assert hash(a) == hash(b) == hash(c)
		assert len({a, b, c}) == 1
		assert scalar(0, 9) == scalar.min()
		assert scalar(0, 0) == scalar(9, 0) == scalar.max()
		assert c < self.Specialized.min()

	@pytest.mark.parametrize("value", foreign)
	def test_foreign_operands_are_not_coerced(self, value: Any):
		a = scalar.mid()

		assert a.__eq__(value) is NotImplemented
		assert a.__lt__(value) is NotImplemented
		assert not (a == value)
		assert not (value == a)
		assert a != value
		assert value != a

		for operation in self.ordering:
			with pytest.raises(TypeError):
				operation(a, value)

			with pytest.raises(TypeError):
				operation(value, a)

	@pytest.mark.parametrize("left, right", pairs)
	def test_operations_keep_their_probability_meaning(self, left: tuple[int, int], right: tuple[int, int]):
		a, b = scalar(*left), scalar(*right)
		p, q = self.probability(a), self.probability(b)
		denominator = p * q + (1 - p) * (1 - q)
		expected_product = p * q / denominator if denominator else Fraction(1, 2)
		expected_sum = p * q / (p + q - p * q) if p or q else Fraction(0)
		expected_dual = (p + q - 2 * p * q) / (1 - p * q) if p * q != 1 else Fraction(1)

		assert self.probability(a + b) == expected_sum
		assert self.probability(a @ b) == expected_dual
		assert self.probability(a * b) == expected_product
		assert self.probability(a & b) == p * q
		assert self.probability(a | b) == p + q - p * q
		assert self.probability(a - b) == p * (1 - q)
		assert self.probability(a ^ b) == p + q - 2 * p * q
		assert self.probability(~a) == 1 - p
		assert ~~a == a
		assert ~(a * b) == ~a * ~b
		assert ~(a & b) == (~a | ~b)
		assert ~(a + b) == (~a @ ~b)

	def test_associative_operations_remain_associative(self):
		values = [scalar(*pair) for pair in self.components]

		for operation in self.associative:
			for a, b, c in product(values, repeat = 3):
				assert operation(operation(a, b), c) == operation(a, operation(b, c))

	def test_self_dual_product_is_deliberately_not_associative_at_conflict(self):
		false, true, three_quarters = scalar.max(), scalar.min(), scalar(1, 3)

		assert false * true == true * false == scalar.mid()
		assert (false * true) * three_quarters == three_quarters
		assert false * (true * three_quarters) == scalar.mid()

	def test_state_is_read_only(self):
		value = scalar(1, 2)

		assert not hasattr(value, "__dict__")

		with pytest.raises(AttributeError):
			value.numer = 3

		with pytest.raises(AttributeError):
			del value.denom

		value.__init__()

		assert value == scalar(1, 2)

	@pytest.mark.parametrize("numer, denom", [(-1, 1), (1, -1), (-1, -1)])
	def test_negative_components_are_rejected(self, numer: int, denom: int):
		with pytest.raises(ValueError):
			scalar(numer, denom)

	def test_operations_and_constants_preserve_subclasses(self):
		a, b = self.Specialized(1, 2), self.Specialized(2, 1)

		for value in (a + b, a @ b, a * b, a & b, a | b, a - b, a ^ b, ~a):
			assert type(value) is self.Specialized

		for value in (self.Specialized.min(), self.Specialized.mid(), self.Specialized.max()):
			assert type(value) is self.Specialized

		assert type(self.Specialized.min() * self.Specialized.max()) is self.Specialized
