"""Every supported choice of comparison primitive completes its order."""

from itertools import product
import sys
import typing

import pytest

from addons.typing.relation.order import Partial, Total


class TestPartial:

	values = (
		(frozenset[int](), "a"),
		(frozenset({1}), "a"),
		(frozenset({1}), "b"),
		(frozenset({2}), "a"),
		(frozenset({1, 2}), "a"),
	)

	class Value(Partial):

		def __init__(self, value: frozenset[int], label: str = ""):
			self.value, self.label = value, label

	class ByLe(Value):

		def __le__(self, other: typing.Self, /) -> bool:
			return self.value <= other.value

	class ByGe(Value):

		def __ge__(self, other: typing.Self, /) -> bool:
			return self.value >= other.value

	@pytest.mark.parametrize("cls", (ByLe, ByGe))
	def test_either_weak_comparison_completes_the_order_on_classes(self, cls: type[Value]):
		for left, right in product(self.values, repeat = 2):
			a, b = cls(*left), cls(*right)
			x, y = left[0], right[0]

			assert (a == b) == (x == y)
			assert (a != b) == (x != y)
			assert (a < b) == (x < y)
			assert (a > b) == (x > y)
			assert (a <= b) == (x <= y)
			assert (a >= b) == (x >= y)
			assert (a == b) == (a <= b and b <= a)

	@pytest.mark.parametrize("cls", (ByLe, ByGe))
	def test_equivalent_representatives_denote_one_ordered_value(self, cls: type[Value]):
		a, b = cls(frozenset({1}), "a"), cls(frozenset({1}), "b")

		assert a <= b and b <= a
		assert a == b
		assert a is not b
		assert a.label != b.label
		assert not hasattr(a, "key")

		for value, label in self.values:
			c = cls(value, label)

			assert (a <= c) == (b <= c)
			assert (c <= a) == (c <= b)
			assert (a < c) == (b < c)
			assert (c < a) == (c < b)

	@pytest.mark.parametrize("cls", (ByLe, ByGe))
	def test_incomparable_classes_are_neither_less_nor_greater(self, cls: type[Value]):
		a, b = cls(frozenset({1})), cls(frozenset({2}))

		assert a != b
		assert not (a <= b or a >= b or a < b or a > b)

	def test_missing_weak_comparisons_remain_recursive(self):
		with pytest.raises(RecursionError):
			assert self.Value(frozenset(), "a") <= self.Value(frozenset(), "a")

		with pytest.raises(RecursionError):
			assert self.Value(frozenset(), "a") == self.Value(frozenset(), "b")

	class Number(Partial):

		def __init__(self, value: int):
			self.value = value

		def __le__(self, other: typing.Self, /) -> bool:
			return self.value <= other.value

	def test_equal_hashes_do_not_identify_distinct_values(self):
		a, b = self.Number(0), self.Number(sys.hash_info.modulus)

		assert hash(a.value) == hash(b.value)
		assert a != b
		assert a < b


class TestTotal:

	values = (0, 1, 2)

	class Value(Total):

		def __init__(self, value: int, label: str = ""):
			self.value, self.label = value, label

	class ByLt(Value):

		def __lt__(self, other: typing.Self, /) -> bool:
			return self.value < other.value

	class ByGt(Value):

		def __gt__(self, other: typing.Self, /) -> bool:
			return self.value > other.value

	class ByLe(Value):

		def __le__(self, other: typing.Self, /) -> bool:
			return self.value <= other.value

	class ByGe(Value):

		def __ge__(self, other: typing.Self, /) -> bool:
			return self.value >= other.value

	@pytest.mark.parametrize("cls", (ByLe, ByGe))
	def test_either_weak_comparison_completes_the_total_order(self, cls: type[Value]):
		for left, right in product(self.values, repeat = 2):
			a, b = cls(left), cls(right)

			assert (a == b) == (left == right)
			assert (a != b) == (left != right)
			assert (a < b) == (left < right)
			assert (a > b) == (left > right)
			assert (a <= b) == (left <= right)
			assert (a >= b) == (left >= right)
			assert a <= b or b <= a

	@pytest.mark.parametrize("cls", (ByLe, ByGe))
	def test_equivalent_representatives_are_not_strictly_ordered(self, cls: type[Value]):
		a, b = cls(1, "a"), cls(1, "b")

		assert a is not b
		assert a == b
		assert a <= b and b <= a
		assert not (a < b or a > b)
		assert not hasattr(a, "key")

	@pytest.mark.parametrize("cls", (ByLt, ByGt))
	def test_strict_comparison_alone_does_not_ground_the_weak_cycle(self, cls: type[Value]):
		with pytest.raises(RecursionError):
			assert cls(1) <= cls(2)

	def test_missing_ordering_comparisons_remain_recursive(self):
		with pytest.raises(RecursionError):
			assert self.Value(1) < self.Value(2)
