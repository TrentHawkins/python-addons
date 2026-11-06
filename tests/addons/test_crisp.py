"""Finite membership indices, complements, and Boolean broadcasting."""

from __future__ import annotations


from itertools import product
from operator import and_, or_, sub, xor
from typing import assert_type

import pytest

from addons import Bool
from addons.crisp import Set, binary


class TestSet:

	keys = ("a", "b")
	bounds = (Bool.max(), Bool.min())
	operations = (or_, and_, sub, xor)
	associative = (or_, and_, xor)
	states = tuple((first, second) for first, second in product((None, False, True), repeat = 2))
	cases = tuple(product((False, True), states))

	class Specialized(Set[str]):
		...

	@staticmethod
	def truth(value: bool) -> Bool:
		return Bool.min() if value else Bool.max()

	@classmethod
	def make(cls, complement: bool, states: tuple[bool | None, bool | None]) -> Set[str]:
		return Set({key: cls.truth(value) for key, value in zip(cls.keys, states) if value is not None},
			complement = cls.truth(complement),
		)

	@classmethod
	def signature(cls, value: Set[str]) -> tuple[Bool, ...]:
		return (value.default, *(value.get(key) for key in cls.keys))

	@pytest.mark.parametrize("complement", (False, True))
	def test_iterable_defines_exceptions_to_the_default(self, complement: bool):
		value = Set(iter(self.keys), complement = self.truth(complement))

		assert type(value.default) is Bool
		assert bool(value.default) is complement
		assert all(type(member) is Bool for member in value.values())
		assert all(bool(value[key]) is not complement for key in self.keys)
		assert set(value) == set(self.keys)
		assert len(value) == 2
		assert not hasattr(value, "complement")

	@pytest.mark.parametrize("complement", bounds)
	def test_explicit_default_is_preserved_even_when_false(self, complement: Bool):
		value = Set[str](complement = complement)
		copy = Set(~value, complement = complement)

		assert value.default is complement
		assert copy.default is complement
		assert value["missing"] is complement
		assert copy["missing"] is complement

	@pytest.mark.parametrize("complement, states", cases)
	def test_mapping_and_copy_preserve_actual_memberships(self, complement: bool, states: tuple[bool | None, bool | None]):
		value = self.make(complement, states)
		copy = Set(value)
		changed = Set(value, complement = ~value.default)

		assert dict(copy.items()) == dict(changed.items()) == dict(value.items())
		assert copy.default == value.default
		assert changed.default == ~value.default
		assert copy is not value

		value.default = ~value.default

		assert bool(copy["new"]) is complement
		assert bool(value["new"]) is not complement

	def test_factory_reads_the_current_default(self):
		value = Set[str]()

		assert not value["old"]

		value.default = Bool.min()

		assert value["new"] is value.default
		assert not value["old"]
		assert value
		assert set(value) == {"old"}
		assert len(value) == 1
		assert repr(value) == "~{'old'}"

	@pytest.mark.parametrize("complement", (False, True))
	def test_missing_membership_and_setdefault_insert_but_get_does_not(self, complement: bool):
		value = Set[str](complement = self.truth(complement))

		assert value.get("read") is value.default
		assert "read" not in value.keys()
		assert value.setdefault("stored") is value.default
		assert "stored" in value.keys()
		assert value["indexed"] is value.default
		assert "indexed" in value.keys()
		assert ("queried" in value) is complement
		assert "queried" in value.keys()
		assert len(value) == 0
		assert not set(value)

	@pytest.mark.parametrize("complement, states", cases)
	def test_truth_and_iteration_follow_values_not_identity(self, complement: bool, states: tuple[bool | None, bool | None]):
		value = self.make(complement, states)
		exceptions = {key for key, state in zip(self.keys, states) if state is not None and state != complement}

		assert set(value) == exceptions
		assert len(value) == len(exceptions)
		assert bool(value) is (complement or any(states))
		assert type(value.__bool__()) is bool
		assert type(value.__contains__("new")) is bool

	@pytest.mark.parametrize("complement", (False, True))
	def test_representations_show_the_finite_index(self, complement: bool):
		empty = Set[str](complement = self.truth(complement))
		single = Set(["a"], complement = self.truth(complement))
		prefix = "~" if complement else ""

		assert repr(empty) == prefix + "set()"
		assert repr(single) == prefix + "{'a'}"

	@pytest.mark.parametrize("complement, states", cases)
	def test_inversion_flips_entries_and_default(self, complement: bool, states: tuple[bool | None, bool | None]):
		value = self.make(complement, states)
		inverse = ~value

		assert inverse.default == ~value.default
		assert inverse.keys() == value.keys()
		assert all(inverse[key] == ~member for key, member in value.items())
		assert self.signature(~~value) == self.signature(value)
		assert set(inverse) == set(value)
		assert len(inverse) == len(value)

	@pytest.mark.parametrize("operation", operations)
	def test_binary_operations_cover_both_indices_and_defaults(self, operation: binary[Bool]):
		for (left_default, left_states), (right_default, right_states) in product(self.cases, repeat = 2):
			left = self.make(left_default, left_states)
			right = self.make(right_default, right_states)
			keys = left.keys() | right.keys()
			expected = tuple(operation(a, b) for a, b in zip(self.signature(left), self.signature(right)))
			result = left.operate(right, operation)

			assert self.signature(result) == expected
			assert result.keys() == keys
			assert all(type(value) is Bool for value in result.values())
			assert left.keys() == right.keys() == keys
			assert result["new"] == operation(left.default, right.default)

	@pytest.mark.parametrize("default", bounds)
	def test_operator_preserves_the_computed_default(self, default: Bool):
		value = Set(["a"])

		for operand in (Set(["b"]), Bool.min()):
			result = value.operate(operand, lambda left, right: default)

			assert result.default is default
			assert result["missing"] is default

	@pytest.mark.parametrize("complement, states", cases)
	def test_operator_syntax_and_scalar_broadcasting(self, complement: bool, states: tuple[bool | None, bool | None]):
		left = self.make(complement, states)
		right = Set(["b"])

		for result, operation in zip((left | right, left & right, left - right, left ^ right), self.operations):
			assert self.signature(result) == self.signature(left.operate(right, operation))

		for scalar in (Bool.min(), Bool.max()):
			forward = (left | scalar, left & scalar, left - scalar, left ^ scalar)
			reverse = (scalar | left, scalar & left, scalar - left, scalar ^ left)

			for result, reflected, operation in zip(forward, reverse, self.operations):
				assert self.signature(result) == tuple(operation(member, scalar) for member in self.signature(left))
				assert self.signature(reflected) == tuple(operation(scalar, member) for member in self.signature(left))
				assert result.keys() == reflected.keys() == left.keys()

	def test_reflected_difference_reverses_the_operands(self):
		value = Set(["a"])
		true, false = Bool.min(), Bool.max()

		assert self.signature(true - value) == self.signature(~value)
		assert not (false - value)
		assert self.signature(value - false) == self.signature(value)
		assert not (value - true)

	@pytest.mark.parametrize("operation", associative)
	def test_pointwise_operations_remain_associative(self, operation: binary[Bool]):
		for first, second, third in product(self.cases, repeat = 3):
			a, b, c = self.make(*first), self.make(*second), self.make(*third)
			left = a.operate(b, operation).operate(c, operation)
			right = a.operate(b.operate(c, operation), operation)

			assert self.signature(left) == self.signature(right)

	@pytest.mark.parametrize("complement", (False, True))
	def test_membership_mutators_store_bool_values(self, complement: bool):
		value = Set[str](complement = self.truth(complement))
		value.add("a")

		assert value["a"] == Bool.min()

		value.remove("a")

		assert value["a"] == Bool.max()
		assert "a" in value.keys()

		with pytest.raises(KeyError):
			value.remove("a")

		value.discard("b")

		assert value["b"] == Bool.max()

	def test_operators_preserve_subclasses_and_static_types(self):
		left, right = self.Specialized(["a"]), self.Specialized(["b"])
		true = Bool.min()

		assert_type(left | right, TestSet.Specialized)
		assert_type(left & true, TestSet.Specialized)
		assert_type(true | left, TestSet.Specialized)
		assert_type(true & left, TestSet.Specialized)
		assert_type(true - left, TestSet.Specialized)
		assert_type(true ^ left, TestSet.Specialized)

		for result in (~left, left | right, left & true, left - true, left ^ true,
			true | left, true & left, true - left, true ^ left,
		):
			assert type(result) is self.Specialized
