"""Either equivalence comparison grounds the complementary pair."""

from itertools import product
import typing

import pytest

from addons.typing.relation import Equivalence


class TestEquivalence:

	values = (-2, -1, 0, 1, 2)

	class Value(Equivalence):

		def __init__(self, value: int):
			self.value = value

	class ByEq(Value):

		def __eq__(self, other: typing.Self, /) -> bool:
			return abs(self.value) == abs(other.value)

	class ByNe(Value):

		def __ne__(self, other: typing.Self, /) -> bool:
			return abs(self.value) != abs(other.value)

	@pytest.mark.parametrize("cls", (ByEq, ByNe))
	def test_either_comparison_defines_equivalence(self, cls: type[Value]):
		for left, right in product(self.values, repeat = 2):
			a, b = cls(left), cls(right)

			assert (a == b) == (abs(left) == abs(right))
			assert (a != b) == (abs(left) != abs(right))

	@pytest.mark.parametrize("cls", (ByEq, ByNe))
	def test_equivalence_needs_no_canonical_representation(self, cls: type[Value]):
		a, b = cls(-1), cls(1)

		assert a == b
		assert a.value != b.value
		assert not hasattr(a, "key")

	def test_missing_comparisons_remain_recursive(self):
		with pytest.raises(RecursionError):
			assert self.Value(1) == self.Value(1)
