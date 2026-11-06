"""Finite membership indices, complements, and Boolean broadcasting."""

from __future__ import annotations


from itertools import product
from operator import and_, iand, ior, isub, ixor, or_, sub, xor
from typing import Callable, Iterable, Mapping, Self, assert_type

import pytest

from addons import Bool
from addons.crisp import Set


class TestSet:

	keys = ("a", "b")
	bounds = (Bool.max(), Bool.min())
	operations = (or_, and_, sub, xor)
	reductions = (("union", or_), ("intersection", and_), ("difference", sub))
	updates = (
		("update", "union", ior),
		("intersection_update", "intersection", iand),
		("difference_update", "difference", isub),
		("symmetric_difference_update", "symmetric_difference", ixor),
	)
	associative = (or_, and_, xor)
	states = tuple((first, second) for first, second in product((None, False, True), repeat = 2))
	cases = tuple(product((False, True), states))

	class Specialized(Set[str]):
		...

	class InvertedScalars(Set[str]):

		def __init__(self, items: Iterable[str] | Mapping[str, Bool] | Bool = (),
			default: Bool | None = None,
		):
			if isinstance(items, Bool):
				items = ~items

			super().__init__(items, default = default)

	class EmptyResults(Set[str]):

		def union(self, *others: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(Bool.max())

		def intersection(self, *others: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(Bool.max())

		def difference(self, *others: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(Bool.max())

		def symmetric_difference(self, other: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(Bool.max())

	class IdentityResults(Set[str]):

		def union(self, *others: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return self

		def intersection(self, *others: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return self

		def difference(self, *others: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return self

		def symmetric_difference(self, other: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return self

	class Reflected(Set[str]):

		def __ror__(self, other: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(["union"])

		def __rand__(self, other: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(["intersection"])

		def __rsub__(self, other: Iterable[str] | Mapping[str, Bool] | Bool) -> Self:
			return type(self)(["difference"])

	@staticmethod
	def truth(value: bool) -> Bool:
		return Bool.min() if value else Bool.max()

	@classmethod
	def make(cls, complement: bool, states: tuple[bool | None, bool | None]) -> Set[str]:
		return Set({key: cls.truth(value) for key, value in zip(cls.keys, states) if value is not None},
			default = cls.truth(complement),
		)

	@classmethod
	def signature(cls, value: Set[str]) -> tuple[Bool, ...]:
		return (value.default, *(value.get(key) for key in cls.keys))

	@pytest.mark.parametrize("scalar", bounds)
	def test_scalar_construction_defines_constant_membership(self, scalar: Bool):
		value = Set[str](scalar)

		assert_type(value, Set[str])
		assert value.default is scalar
		assert not value.keys()
		assert len(value) == 0
		assert bool(value) is bool(scalar)
		assert value["missing"] is scalar
		assert not set(value)

	@pytest.mark.parametrize("scalar", bounds)
	@pytest.mark.parametrize("default", bounds)
	def test_explicit_default_overrides_scalar_construction(self, scalar: Bool, default: Bool):
		value = Set[str](scalar, default = default)

		assert value.default is default
		assert not value.keys()
		assert value["missing"] is default

	@pytest.mark.parametrize("complement", (False, True))
	def test_iterable_defines_exceptions_to_the_default(self, complement: bool):
		value = Set(iter(self.keys), default = self.truth(complement))

		assert type(value.default) is Bool
		assert bool(value.default) is complement
		assert all(type(member) is Bool for member in value.values())
		assert all(bool(value[key]) is not complement for key in self.keys)
		assert set(value) == set(self.keys)
		assert len(value) == 2
		assert not hasattr(value, "complement")

	@pytest.mark.parametrize("complement", bounds)
	def test_explicit_default_is_preserved_even_when_false(self, complement: Bool):
		value = Set[str](default = complement)
		copy = Set(~value, default = complement)

		assert value.default is complement
		assert copy.default is complement
		assert value["missing"] is complement
		assert copy["missing"] is complement

	@pytest.mark.parametrize("complement, states", cases)
	def test_mapping_and_copy_preserve_actual_memberships(self, complement: bool, states: tuple[bool | None, bool | None]):
		value = self.make(complement, states)
		copy = Set(value)
		changed = Set(value, default = ~value.default)

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
		value = Set[str](default = self.truth(complement))

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
		empty = Set[str](default = self.truth(complement))
		single = Set(["a"], default = self.truth(complement))
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
	def test_binary_operations_cover_both_indices_and_defaults(self, operation: Callable[[Bool, Bool], Bool]):
		for (left_default, left_states), (right_default, right_states) in product(self.cases, repeat = 2):
			left = self.make(left_default, left_states)
			right = self.make(right_default, right_states)
			right_items = dict(right.items())
			keys = left.keys() | right.keys()
			expected = tuple(operation(a, b) for a, b in zip(self.signature(left), self.signature(right)))
			result = left.operate(right, operation)

			assert self.signature(result) == expected
			assert result.keys() == keys
			assert all(type(value) is Bool for value in result.values())
			assert left.keys() == keys
			assert dict(right.items()) == right_items
			assert result["new"] == operation(left.default, right.default)

	@pytest.mark.parametrize("operation", operations)
	@pytest.mark.parametrize("scalar", bounds)
	def test_scalar_promotion_preserves_pointwise_operations(self, operation: Callable[[Bool, Bool], Bool], scalar: Bool):
		for complement, states in self.cases:
			value = self.make(complement, states)
			expected = tuple(operation(member, scalar) for member in self.signature(value))
			result = value.operate(scalar, operation)

			assert self.signature(result) == expected
			assert result.keys() == value.keys()

	@pytest.mark.parametrize("scalar", bounds)
	def test_constructor_interpretation_is_shared_by_operations(self, scalar: Bool):
		direct = self.InvertedScalars(scalar)
		value = self.InvertedScalars()
		result = value | scalar

		assert direct.default == result.default == ~scalar
		assert not direct.keys()
		assert not result.keys()
		assert type(result) is self.InvertedScalars

	@pytest.mark.parametrize("scalar", bounds)
	@pytest.mark.parametrize("default", bounds)
	def test_constructor_override_preserves_explicit_defaults(self, scalar: Bool, default: Bool):
		value = self.InvertedScalars(scalar, default = default)

		assert value.default is default

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
	def test_pointwise_operations_remain_associative(self, operation: Callable[[Bool, Bool], Bool]):
		for first, second, third in product(self.cases, repeat = 3):
			a, b, c = self.make(*first), self.make(*second), self.make(*third)
			left = a.operate(b, operation).operate(c, operation)
			right = a.operate(b.operate(c, operation), operation)

			assert self.signature(left) == self.signature(right)

	@pytest.mark.parametrize("complement", (False, True))
	def test_membership_mutators_store_bool_values(self, complement: bool):
		value = Set[str](default = self.truth(complement))
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

	@pytest.mark.parametrize("name, operation", reductions)
	@pytest.mark.parametrize("complement, states", cases)
	def test_reductions_fold_mixed_operands(self, name: str, operation: Callable[[Set[str], Set[str]], Set[str]],
		complement: bool, states: tuple[bool | None, bool | None],
	):
		value = self.make(complement, states)
		original = dict(value.items())
		others = (["a"], {"b": Bool.min()}, Set(["b"], default = Bool.min()), Bool.max(), Bool.min())
		expected = Set(value)

		for other in others:
			normalized = Set[str](default = other) if isinstance(other, Bool) else Set(other)
			expected = operation(expected, normalized)

		result = getattr(value, name)(*others)

		assert self.signature(result) == self.signature(expected)
		assert result.keys() == expected.keys()
		assert dict(value.items()) == original
		assert bool(value.default) is complement

	@pytest.mark.parametrize("name, operation", reductions)
	def test_reductions_accept_one_shot_iterables(self, name: str, operation: Callable[[Set[str], Set[str]], Set[str]]):
		value = Set(self.keys)
		result = getattr(value, name)(iter(["a"]))
		expected = operation(Set(value), Set(["a"]))

		assert self.signature(result) == self.signature(expected)

	@pytest.mark.parametrize("name, operation", reductions)
	@pytest.mark.parametrize("default", bounds)
	def test_empty_reductions_return_fresh_copies(self, name: str,
		operation: Callable[[TestSet.Specialized, Iterable[str] | Mapping[str, Bool] | Bool], TestSet.Specialized],
		default: Bool,
	):
		value = self.Specialized({"a": Bool.min(), "b": Bool.max()}, default = default)

		for result in (getattr(value, name)(), value.reduce(operation)):
			assert result is not value
			assert type(result) is self.Specialized
			assert result.default == value.default
			assert dict(result.items()) == dict(value.items())

	@pytest.mark.parametrize("name, operation", reductions)
	def test_reductions_use_reflected_operator_dispatch(self, name: str,
		operation: Callable[[Set[str], Iterable[str] | Mapping[str, Bool] | Bool], Set[str]],
	):
		value = Set(["a"])
		other = self.Reflected(["b"])

		for result in (getattr(value, name)(other), value.reduce(operation, other)):
			assert type(result) is self.Reflected
			assert set(result) == {name}

	def test_difference_reduction_groups_from_the_left(self):
		value = Set(self.keys)

		assert set(value.difference(["a"], ["a"])) == {"b"}

	def test_reductions_preserve_subclasses_and_static_types(self):
		value = self.Specialized(self.keys)

		assert_type(value.union(["c"], Bool.max()), TestSet.Specialized)
		assert_type(value.intersection({"a": Bool.min()}, Bool.min()), TestSet.Specialized)
		assert_type(value.difference(iter(["a"]), Bool.max()), TestSet.Specialized)
		assert_type(value.reduce(or_, ["c"], Bool.max()), TestSet.Specialized)

		for result in (value.union(Bool.min()), value.intersection(Bool.max()), value.difference(["a"])):
			assert type(result) is self.Specialized

	@pytest.mark.parametrize("name, pure, operation", updates)
	@pytest.mark.parametrize("complement, states", cases)
	def test_updates_and_inplace_operators_match_the_algebra(self, name: str, pure: str,
		operation: Callable[[Set[str], Iterable[str] | Mapping[str, Bool] | Bool], Set[str]],
		complement: bool, states: tuple[bool | None, bool | None],
	):
		others = [self.make(default, entries) for default, entries in self.cases]

		for other in (*others, *self.bounds):
			value = self.make(complement, states)
			inplace = Set(value)
			expected = getattr(Set(value), pure)(other)
			factory = value.default_factory

			assert getattr(value, name)(other) is None
			assert operation(inplace, other) is inplace

			for result in (value, inplace):
				assert self.signature(result) == self.signature(expected)
				assert dict(result.items()) == dict(expected.items())
				assert result["missing"] is result.default

			assert value.default_factory is factory

	@pytest.mark.parametrize("name, operation", reductions)
	@pytest.mark.parametrize("default", bounds)
	def test_empty_updates_preserve_the_receiver(self, name: str,
		operation: Callable[[TestSet.Specialized, Iterable[str] | Mapping[str, Bool] | Bool], TestSet.Specialized],
		default: Bool,
	):
		value = self.Specialized({"a": Bool.min(), "b": Bool.max()}, default = default)
		items = dict(value.items())
		factory = value.default_factory
		update_name = "update" if name == "union" else name + "_update"

		assert getattr(value, update_name)() is None
		assert type(value) is self.Specialized
		assert dict(value.items()) == items
		assert value.default is default
		assert value.default_factory is factory
		assert self.signature(value) == self.signature(value.reduce(operation))

	@pytest.mark.parametrize("name, pure, operation", updates)
	@pytest.mark.parametrize("default", bounds)
	def test_updates_accept_the_receiver_as_an_operand(self, name: str, pure: str,
		operation: Callable[[Set[str], Iterable[str] | Mapping[str, Bool] | Bool], Set[str]], default: Bool,
	):
		value = Set({"a": Bool.min(), "b": Bool.max()}, default = default)
		inplace = Set(value)
		expected = getattr(Set(value), pure)(value)

		assert getattr(value, name)(value) is None
		assert operation(inplace, inplace) is inplace
		assert self.signature(value) == self.signature(inplace) == self.signature(expected)

	def test_updates_support_multiple_mixed_operands(self):
		value = Set(["a"])
		value.update(iter(["b"]), {"c": Bool.min()}, Bool.max())

		assert set(value) == {"a", "b", "c"}

		value.intersection_update(iter(["a", "b"]), {"b": Bool.min()}, Bool.min())

		assert set(value) == {"b"}

		value.difference_update(iter(["a"]), {"b": Bool.min()}, Bool.max())

		assert not value

		value.symmetric_difference_update(iter(["c"]))

		assert set(value) == {"c"}

	def test_update_unions_memberships_instead_of_overwriting_them(self):
		value = Set(["a"])
		value.update({"a": Bool.max()})

		assert "a" in value

	@pytest.mark.parametrize("name, pure, operation", updates)
	def test_updates_honor_named_overrides_and_replace_stale_entries(self, name: str, pure: str,
		operation: Callable[[Set[str], Iterable[str] | Mapping[str, Bool] | Bool], Set[str]],
	):
		value = self.EmptyResults(["a"], default = Bool.min())
		alias = value

		assert not getattr(value, pure)(Bool.min())
		assert getattr(value, name)(Bool.min()) is None
		assert value is alias
		assert not value.keys()
		assert value.default == Bool.max()

		value.add("b")

		assert operation(value, Bool.min()) is value
		assert not value.keys()

	@pytest.mark.parametrize("name, pure, operation", updates)
	def test_update_overrides_can_return_the_receiver(self, name: str, pure: str,
		operation: Callable[[Set[str], Iterable[str] | Mapping[str, Bool] | Bool], Set[str]],
	):
		value = self.IdentityResults({"a": Bool.min(), "b": Bool.max()}, default = Bool.min())
		items = dict(value.items())
		default = value.default

		assert getattr(value, pure)(Bool.max()) is value
		assert getattr(value, name)(Bool.max()) is None
		assert operation(value, Bool.max()) is value
		assert dict(value.items()) == items
		assert value.default is default

	def test_inplace_syntax_preserves_aliases_subclasses_and_factory_binding(self):
		value = self.Specialized(["a"])
		alias = value
		factory = value.default_factory
		value |= ["b"]

		assert_type(value, TestSet.Specialized)
		assert set(value) == {"a", "b"}

		value &= {"a": Bool.min()}

		assert_type(value, TestSet.Specialized)
		assert set(value) == {"a"}

		value ^= Bool.min()

		assert_type(value, TestSet.Specialized)
		assert value.default == Bool.min()
		assert "a" not in value

		value -= Bool.min()

		assert_type(value, TestSet.Specialized)
		assert not value
		assert value is alias
		assert value.default_factory is factory

		value.default = Bool.min()

		assert value["missing"] is value.default
