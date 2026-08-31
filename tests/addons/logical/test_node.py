"""§5 — the container: background, seam, the `set` algebra, and the storage protocols."""

from __future__ import annotations


import copy
import pickle

from itertools import chain, combinations
from typing import Any

import pytest

from addons.logical import Bool, FuzzySet, Graph, IndexSet, Node, Prob

from .conftest import RUNGS, carrier, present, sample


UNIVERSE = ("a", "b", "c", "d")
SUBSETS = [frozenset(items) for size in range(len(UNIVERSE) + 1) for items in combinations(UNIVERSE, size)]


class TestConstruction:

	def test_empty_is_empty(self):
		assert not IndexSet() and len(IndexSet()) == 0

	def test_from_an_iterable(self):
		assert set(IndexSet(["a", "b"])) == {"a", "b"}

	def test_from_a_mapping(self):
		node = FuzzySet({"a": Prob(1, 2)})

		assert node["a"] == Prob(1, 2)

	def test_from_another_node(self):
		node = FuzzySet({"a": Prob(1, 2)})

		assert FuzzySet(node) == node

	def test_from_a_scalar_is_the_polarity_it_carries(self):
		"""A background is crisp: a scalar names which of the two, nothing finer."""
		assert FuzzySet(Prob.maximum()).default == Prob.maximum()
		assert FuzzySet(Prob.minimum()).default == Prob.minimum()
		assert FuzzySet(Prob(1, 2)).default == Prob.minimum(), "a true-ish scalar is the universal set"

	def test_an_empty_iterable_and_no_argument_agree(self):
		assert IndexSet([]) == IndexSet()

	def test_the_polarity_is_a_flag_not_a_value(self):
		"""`complement` is the API; `default` is that one bit wearing the carrier's clothes."""
		assert FuzzySet(complement = False).default == Prob.maximum()
		assert FuzzySet(complement = True).default == Prob.minimum()

		assert not FuzzySet(complement = False).complement
		assert FuzzySet(complement = True).complement

	def test_the_flag_overrides_the_iterable(self):
		assert FuzzySet(["a"], complement = True).complement
		assert not FuzzySet(Prob.minimum(), complement = False).complement

	def test_fromkeys(self):
		assert set(IndexSet.fromkeys(["a", "b"])) == {"a", "b"}
		assert FuzzySet.fromkeys(["a"], Prob(1, 4))["a"] == Prob(1, 4)


class TestBackground:

	def test_complement_is_a_reading_of_the_default(self):
		assert not IndexSet().complement and IndexSet(Bool(True)).complement

	def test_the_bounds_are_the_full_and_empty_sets(self):
		assert IndexSet.minimum().complement and not IndexSet.maximum().complement
		assert IndexSet.maximum() == IndexSet()

	def test_a_background_is_never_graded(self):
		"""Eliminated deliberately: a uniform grade over an infinite key space has no measure."""
		for scalar in (Prob(1, 3), Prob(1, 2), Prob(3, 4)):
			assert FuzzySet(scalar).default in (Prob.minimum(), Prob.maximum())

		assert FuzzySet(Prob(1, 2))["anything"] == Prob.minimum()

	@pytest.mark.parametrize("cls", RUNGS)
	def test_the_seam_round_trips_for_every_rung(self, cls: Any):
		for value in (carrier(cls).minimum(), carrier(cls).maximum()):
			assert abs(cls(value)) == value

	def test_iteration_refuses_implicit_members(self):
		with pytest.raises(TypeError, match = "implicit"):
			list(IndexSet(Bool(True)))

	def test_a_complemented_node_is_true_even_when_it_records_nothing(self):
		assert IndexSet(Bool(True))


class TestRepresentation:

	def test_empty_prints_as_empty_braces(self):
		assert repr(IndexSet()) == "{}"

	def test_a_crisp_node_prints_as_a_roster(self):
		assert repr(IndexSet(["a"])) == "{'a'}"

	def test_a_graded_node_prints_as_a_mapping(self):
		assert repr(FuzzySet({"a": Prob(1, 2)})) == "{'a': 0.5}"

	def test_a_complement_is_marked(self):
		assert repr(~IndexSet(["a"])).startswith("~")

	def test_the_representation_carries_only_the_polarity(self):
		assert repr(FuzzySet(Prob(1, 2))) == "~{}"
		assert repr(FuzzySet()) == "{}"


class TestSetAlgebra:

	@pytest.mark.parametrize("left", SUBSETS)
	def test_the_lattice_agrees_with_builtin_set(self, left: frozenset):
		for right in SUBSETS:
			a, b = IndexSet(left), IndexSet(right)

			assert a | b == IndexSet(left | right)
			assert a & b == IndexSet(left & right)
			assert a - b == IndexSet(left - right)
			assert a ^ b == IndexSet(left ^ right)

	@pytest.mark.parametrize("left", SUBSETS)
	def test_the_ordering_agrees_with_builtin_set(self, left: frozenset):
		for right in SUBSETS:
			a, b = IndexSet(left), IndexSet(right)

			assert (a <= b) == (left <= right)
			assert (a >= b) == (left >= right)
			assert (a == b) == (left == right)
			assert a.isdisjoint(b) == left.isdisjoint(right)

	def test_the_named_operations_agree_with_the_operators(self):
		a, b = IndexSet(["a", "b"]), IndexSet(["b", "c"])

		assert a.union(b) == a | b
		assert a.intersection(b) == a & b
		assert a.difference(b) == a - b
		assert a.symmetric_difference(b) == a ^ b

	def test_in_place_operators_mutate_in_place(self):
		node = IndexSet(["a", "b"])
		before = id(node)

		node |= IndexSet(["c"])

		assert id(node) == before and set(node) == {"a", "b", "c"}

	@pytest.mark.parametrize("operation, expected", [
		("__ior__", {"a", "b", "c"}),
		("__iand__", {"b"}),
		("__isub__", {"a"}),
		("__ixor__", {"a", "c"}),
	])
	def test_every_in_place_operator(self, operation: str, expected: set):
		node = IndexSet(["a", "b"])

		getattr(node, operation)(IndexSet(["b", "c"]))

		assert set(node) == expected

	def test_multiplication_repeats_addition(self):
		node = FuzzySet({"a": Prob(1, 2)})

		assert node * 2 == node + node


class TestScalarComparison:

	@pytest.mark.parametrize("grade", [Prob(0, 1), Prob(1, 4), Prob(1, 2), Prob(3, 4), Prob(1, 1)])
	def test_a_node_meets_a_scalar_at_its_measure(self, grade: Prob):
		"""The seam lives in the recorded values now that backgrounds are crisp."""
		node = FuzzySet({"a": grade})

		assert node == grade and grade == node
		assert (node <= grade) and (node >= grade)

	def test_comparison_is_authority_free(self):
		node, scalar = FuzzySet({"a": Prob(1, 2)}), Prob(1, 4)

		assert (node <= scalar) == (scalar >= node)
		assert (node >= scalar) == (scalar <= node)


class TestStorageProtocols:

	def test_add_records_presence_and_discard_records_absence(self):
		node = IndexSet()

		node.add("a")
		assert node["a"] == Bool(True)

		node.discard("a")
		assert node["a"] == Bool(False)

	def test_discard_and_delete_differ_under_a_complement(self):
		discarded, deleted = ~IndexSet(["a", "b"]), ~IndexSet(["a", "b"])

		discarded.discard("a")
		del deleted["a"]

		assert not discarded["a"], "discard records absence"
		assert deleted["a"], "delete forgets the record, so the background shows through"

	def test_remove_raises_on_a_missing_key(self):
		with pytest.raises(KeyError):
			IndexSet().remove("a")

	def test_pop_returns_or_raises(self):
		node = IndexSet(["a"])

		assert node.pop("a") == Bool(True)

		with pytest.raises(KeyError):
			node.pop("a")

		assert node.pop("a", Bool(False)) == Bool(False)

	def test_get_falls_back_to_the_background(self):
		assert IndexSet().get("a") == Bool(False)
		assert FuzzySet(Prob(1, 3)).get("a") == Prob.minimum()

	def test_setdefault_records_only_when_absent(self):
		node = FuzzySet({"a": Prob(1, 2)})

		assert node.setdefault("a", Prob(1, 4)) == Prob(1, 2)
		assert node.setdefault("b", Prob(1, 4)) == Prob(1, 4)

	def test_clear_empties_to_the_false_background(self):
		node = ~IndexSet(["a"])
		node.clear()

		assert node == IndexSet.maximum() and not node.complement

	def test_become_adopts_both_records_and_background(self):
		node, other = IndexSet(["a"]), ~IndexSet(["b"])
		node.become(other)

		assert node == other and node.complement

	def test_update_family(self):
		node = IndexSet(["a"])
		node.update(IndexSet(["b"]))

		assert set(node) == {"a", "b"}

		node.intersection_update(IndexSet(["b"]))
		assert set(node) == {"b"}

	def test_reads_autovivify_so_presence_cannot_be_probed_by_reading(self):
		"""A `defaultdict` consequence every presence-shaped contract has to respect."""
		node: Graph[str] = Graph()

		assert len(node) == 0

		_ = node["u", "v"]
		assert len(node) == 1

		other: Graph[str] = Graph()
		assert ("u", "v") not in other and len(other) == 1

		assert not present(Graph(), "u", "v")


class TestIdentity:

	def test_a_node_is_unhashable_like_every_mutable_container(self):
		with pytest.raises(TypeError):
			hash(IndexSet())  # pyright: ignore[reportArgumentType]

	@pytest.mark.parametrize("cls", RUNGS)
	def test_copy_deepcopy_and_pickle_all_round_trip(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 13)

		assert copy.copy(node) == node
		assert copy.deepcopy(node) == node
		assert pickle.loads(pickle.dumps(node)) == node

	@pytest.mark.parametrize("cls", RUNGS)
	def test_the_background_survives_a_round_trip(self, cls: Any):
		node = cls(carrier(cls).minimum())

		assert pickle.loads(pickle.dumps(node)).complement == node.complement

	def test_a_copy_is_independent(self):
		node = IndexSet(["a"])
		clone = node.copy()

		clone.add("b")

		assert "b" not in set(node) and set(clone) == {"a", "b"}

	def test_assignment_copies_rather_than_aliases(self):
		"""Which is why a stored child has exactly one parent."""
		source: Graph[str] = Graph()
		source["u", "v"] = Prob(3, 4)

		target: Graph[str] = Graph()
		target["x"] = source["u"]

		assert target["x"] is not source["u"]
		assert target["x"] == source["u"]

	def test_a_read_aliases_rather_than_copies(self):
		node: Graph[str] = Graph()
		node["u", "v"] = Prob(3, 4)

		neighbourhood = node["u"]
		neighbourhood["w"] = Prob(1, 2)  # pyright: ignore[reportIndexIssue]

		assert node["u", "w"] == Prob(1, 2)


class TestCoverageSemantics:

	def test_a_recorded_entry_equal_to_the_background_is_still_recorded(self):
		"""Coverage is what the set knows, not which values differ — this is why `del` != `discard`."""
		node: IndexSet[str] = IndexSet()
		node.discard("a")

		assert len(node) == 1 and dict(node) == {"a": Bool(False)}

	def test_del_and_discard_coincide_only_on_a_false_background(self):
		plain, complemented = IndexSet(["a", "b"]), ~IndexSet(["a", "b"])

		for node in (plain, complemented):
			forgotten, absent = node.copy(), node.copy()

			del forgotten["a"]
			absent.discard("a")

			assert (bool(forgotten["a"]) == bool(absent["a"])) is (not node.complement)

	def test_complement_is_effective_not_materialised(self):
		node = FuzzySet({"a": Prob(1, 4)})
		flipped = ~node

		assert len(flipped) == len(node), "no universe was enumerated"
		assert flipped.default == ~node.default
		assert flipped["a"] == ~node["a"]
		assert flipped["unrecorded"] == ~node["unrecorded"]

	def test_len_counts_coverage_not_measure(self):
		node = FuzzySet({"a": Prob(1, 4), "b": Prob(3, 4)})

		assert len(node) == 2
		assert abs(node) != Prob(2, 2)

	@pytest.mark.parametrize("cls", RUNGS)
	def test_the_bounds_are_the_universal_and_empty_sets(self, cls: Any):
		assert cls.minimum().complement and not cls.maximum().complement
		assert cls.maximum() == cls()
		assert abs(cls.minimum()) == carrier(cls).minimum()
