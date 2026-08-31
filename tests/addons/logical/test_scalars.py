"""§3 — the scalars on the projective line, and the closure of mixing them."""

from __future__ import annotations


from math import inf

import pytest

from addons.logical import Bool, Dist, Frac, Prob

from .conftest import oplus


SCALARS = (Dist, Prob, Bool)

READINGS = [
	(Dist, 0, 1, 0.0),
	(Dist, 1, 1, 1.0),
	(Dist, 1, 0, inf),
	(Prob, 1, 2, 0.5),
	(Prob, 3, 4, 0.75),
	(Bool, True, None, 0.0),
	(Bool, False, None, inf),
]


class TestReadings:

	@pytest.mark.parametrize("cls, a, b, expected", READINGS)
	def test_the_coordinates_read_as_documented(self, cls: type[Frac], a: int, b: int | None, expected: float):
		assert float(cls(a) if b is None else cls(a, b)) == expected

	def test_dist_is_difficulty_and_prob_is_probability(self):
		assert float(Dist.minimum()) == 0.0 and float(Dist.maximum()) == inf
		assert float(Prob.minimum()) == 1.0 and float(Prob.maximum()) == 0.0

	def test_midimum_is_the_balance_point(self):
		assert float(Dist.midimum()) == 1.0 and float(Prob.midimum()) == 0.5

	def test_bool_is_the_two_point_quotient(self):
		"""`Bool` stores the `Dist` coordinates, so `float` is a difficulty, not a probability."""
		assert {float(Bool(True)), float(Bool(False))} == {0.0, inf}
		assert Bool(True) == Bool.minimum() == Dist.minimum() and Bool(False) == Bool.maximum() == Dist.maximum()
		assert bool(Bool(True)) and not bool(Bool(False))

	def test_repr_of_bool_is_a_bool(self):
		assert repr(Bool(True)) == "True" and repr(Bool(False)) == "False"


class TestFaithfulness:

	@pytest.mark.parametrize("cls, a, b, _", READINGS)
	def test_encode_decode_round_trips(self, cls: type[Frac], a: int, b: int | None, _: float):
		value = cls(a) if b is None else cls(a, b)

		assert cls.encode(*value.decode()) == value

	@pytest.mark.parametrize("cls", SCALARS)
	def test_the_round_trip_holds_across_the_whole_grid(self, cls: type[Frac]):
		grid = [Bool(True), Bool(False)] if cls is Bool else [cls(a, 8) for a in range(9)]

		for value in grid:
			assert cls.encode(*value.decode()) == value


class TestMixing:

	def test_the_three_carriers_agree_on_the_same_point(self):
		assert Bool(True) == Prob(1, 1) == Dist(0, 1)
		assert Bool(False) == Prob(0, 1) == Dist(1, 0)

	def test_equal_points_hash_alike_across_carriers(self):
		assert hash(Bool(True)) == hash(Prob(1, 1)) == hash(Dist(0, 1))
		assert len({Bool(True), Prob(1, 1), Dist(0, 1)}) == 1

	def test_the_left_operand_is_the_authority(self):
		assert type(Prob(1, 2) & Bool(True)) is Prob
		assert type(Dist(3, 4) | Bool(False)) is Dist
		assert type(Bool(True) & Prob(1, 2)) is Bool

	def test_mixing_preserves_the_value(self):
		assert Prob(1, 2) & Bool(True) == Prob(1, 2)
		assert Prob(1, 2) | Bool(False) == Prob(1, 2)

	def test_a_bool_is_crisp_and_an_int_is_a_numerator(self):
		assert Dist(True) == Dist.minimum() and Dist(False) == Dist.maximum()
		assert Dist(1) == Dist(1, 1) and float(Dist(1)) == 1.0

	def test_contract_scalarises_whatever_it_is_given(self):
		assert Prob.contract(Bool(True)) == Bool(True)
		assert Prob.contract(1) == Prob(1)


class TestAlgebra:

	def test_and_is_the_product_of_probabilities(self):
		assert Prob(1, 2) & Prob(1, 2) == Prob(1, 4)

	def test_or_is_noisy_or(self):
		assert Prob(1, 2) | Prob(1, 2) == Prob(3, 4)

	def test_addition_is_difficulty_addition(self):
		assert Dist(1, 2) + Dist(1, 2) == Dist(1)
		assert Prob(1, 2) + Prob(1, 2) == Prob(1, 3)

	def test_multiplication_repeats_addition(self):
		assert Dist(1, 3) * 3 == Dist(1) and Prob(1, 2) * 2 == Prob(1, 2) + Prob(1, 2)

	def test_oplus_is_the_dual_of_the_sum_and_differs_from_or(self):
		assert oplus(Prob(1, 2), Prob(1, 2)) == Prob(2, 3)
		assert oplus(Prob(1, 2), Prob(1, 2)) != Prob(1, 2) | Prob(1, 2)

	def test_oplus_is_or_on_the_crisp_carrier(self):
		for a in (True, False):
			for b in (True, False):
				assert bool(oplus(Bool(a), Bool(b))) == (a or b)

	def test_the_infinite_point_is_reachable(self):
		assert Dist(1, 0) == Dist.maximum() and float(Dist(1, 0)) == inf

	def test_zero_over_zero_is_normalised_rather_than_undefined(self):
		assert Dist(0, 0) == Dist.maximum()


class TestGuards:

	def test_a_dist_refuses_negative_coordinates(self):
		with pytest.raises(ValueError):
			Dist(-1, 1)

	@pytest.mark.parametrize("numer, denom", [(2, 1), (-1, 2)])
	def test_a_prob_stays_inside_the_unit_interval(self, numer: int, denom: int):
		with pytest.raises(ValueError):
			Prob(numer, denom)

	def test_coordinates_are_reduced(self):
		assert Dist(2, 4).decoded == Dist(1, 2).decoded
