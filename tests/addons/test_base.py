"""`addons.base` — the non-negative numeric wrapper."""

from __future__ import annotations


import math

import pytest

from addons.base import Float, Int, Number


class TestConstruction:

	def test_a_subclass_must_declare_a_value_type(self):
		with pytest.raises(TypeError, match = "value_type"):
			class Untyped(Number):  # pyright: ignore[reportUnusedClass, reportMissingTypeArgument]
				...

	def test_a_subclass_may_declare_it_by_keyword(self):
		class Keyed(Number[int], value_type = int):
			...

		assert Keyed(3) == Keyed(3)

	@pytest.mark.parametrize("cls, raw", [(Int, 3), (Float, 3.5)])
	def test_it_wraps_and_unwraps(self, cls: type, raw: float):
		assert float(cls(raw)) == float(raw)
		assert int(cls(raw)) == int(raw)

	def test_it_accepts_its_own_kind(self):
		assert Int(Int(3)) == Int(3)

	@pytest.mark.parametrize("cls, raw", [(Int, -1), (Float, -0.5)])
	def test_it_refuses_a_negative(self, cls: type, raw: float):
		with pytest.raises(ValueError, match = "non-negative"):
			cls(raw)

	def test_int_truncates_toward_zero_so_a_small_negative_survives(self):
		assert int(Int(-0.5)) == 0  # pyright: ignore[reportArgumentType]


class TestAlgebra:

	def test_addition_and_multiplication(self):
		assert Int(2) + Int(3) == Int(5)
		assert Int(2) * Int(3) == Int(6)

	def test_sum_and_prod_have_the_right_identities(self):
		assert Int.zero() == Int(0) and Int.unit() == Int(1)
		assert Int.sum([]) == Int.zero() and Int.prod([]) == Int.unit()
		assert Int.sum([Int(1), Int(2), Int(3)]) == Int(6)
		assert Int.prod([Int(2), Int(3)]) == Int(6)

	def test_unary_operators(self):
		assert +Int(3) == Int(3) and abs(Int(3)) == Int(3)

	def test_mixed_kinds_do_not_operate(self):
		with pytest.raises(TypeError):
			Int(1) + Float(1.0)  # pyright: ignore[reportArgumentType, reportUnusedExpression, reportOperatorIssue]

	def test_mixed_kinds_compare_unequal_rather_than_raising(self):
		assert Int(1) != Float(1.0)

	def test_mixed_kinds_refuse_an_ordering(self):
		with pytest.raises(TypeError):
			Int(1) <= Float(1.0)  # pyright: ignore[reportArgumentType, reportUnusedExpression, reportOperatorIssue]


class TestOrdering:

	def test_it_is_total_within_a_kind(self):
		assert Int(1) < Int(2) < Int(3)
		assert Int(2) >= Int(2) and Int(2) <= Int(2)

	def test_equal_values_hash_alike(self):
		assert hash(Int(3)) == hash(Int(3)) == hash(3)
		assert len({Int(3), Int(3)}) == 1


class TestFloat:

	def test_it_carries_the_special_values(self):
		assert math.isnan(float(Float.nan()))
		assert math.isinf(float(Float.inf()))

	def test_nan_is_admitted_because_it_is_not_negative(self):
		assert math.isnan(float(Float(math.nan)))

	def test_nan_is_not_equal_to_itself(self):
		assert Float.nan() != Float.nan()

	def test_repr_and_str_defer_to_the_value(self):
		assert repr(Float(1.5)) == repr(1.5) and str(Int(2)) == str(2)

	def test_bool_defers_to_the_value(self):
		assert not Int(0) and Int(1)
