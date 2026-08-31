"""§5 — the tower: one class per rung, the registry that keeps it dense, and derived arity."""

from __future__ import annotations


import pickle

from typing import Any

import pytest

from addons.logical import Bool, Boolean, FuzzySet, Graph, IndexSet, Node, Prob, Set, UnweightedGraph

from .conftest import ARITY, CRISP_RUNGS, CrispHyper, GRADED_RUNGS, Hyper, RUNGS, carrier, registry, sample


class TestRegistry:

	def test_there_is_one_dense_list_per_polarity(self):
		crisp, graded = registry()

		assert crisp[:3] == [IndexSet, UnweightedGraph, CrispHyper]
		assert graded[:3] == [FuzzySet, Graph, Hyper]

	def test_depth_indexes_the_list(self):
		for depth, cls in enumerate(CRISP_RUNGS):
			assert registry()[False][depth] is cls

		for depth, cls in enumerate(GRADED_RUNGS):
			assert registry()[True][depth] is cls

	def test_declaring_and_looking_up_name_one_class(self):
		assert registry()[True][1] is Graph
		assert type(Graph()["u"]) is FuzzySet


class TestSlotGuards:

	def test_an_occupied_slot_is_refused(self):
		with pytest.raises(TypeError, match = "already holds it"):
			class Duplicate(Set, weighted = True, depth = 1):  # pyright: ignore[reportUnusedClass]
				...

	def test_a_gap_is_refused(self):
		with pytest.raises(TypeError, match = "rungs stand under it"):
			class Detached(Set, weighted = True, depth = 9):  # pyright: ignore[reportUnusedClass]
				...

	def test_a_negative_depth_is_refused_without_wrapping_around(self):
		with pytest.raises(TypeError, match = "rungs stand under it"):
			class Backwards(Set, weighted = True, depth = -1):  # pyright: ignore[reportUnusedClass]
				...

	def test_a_refused_declaration_leaves_the_registry_untouched(self):
		before = [len(rungs) for rungs in registry()]

		with pytest.raises(TypeError):
			class Duplicate(Set, weighted = False, depth = 0):  # pyright: ignore[reportUnusedClass]
				...

		assert [len(rungs) for rungs in registry()] == before

	def test_an_ordinary_subclass_claims_nothing(self):
		before = [len(rungs) for rungs in registry()]

		class Plain(Graph):
			...

		assert [len(rungs) for rungs in registry()] == before
		assert Plain not in registry()[True]


class TestTruthChain:

	@pytest.mark.parametrize("cls, truth", [
		(IndexSet, Bool),
		(FuzzySet, Prob),
		(UnweightedGraph, IndexSet),
		(Graph, FuzzySet),
		(CrispHyper, UnweightedGraph),
		(Hyper, Graph),
	])
	def test_a_rung_derives_its_carrier_from_the_one_below(self, cls: Any, truth: type):
		assert carrier(cls) is truth

	@pytest.mark.parametrize("cls", RUNGS)
	def test_arity_is_depth_plus_one(self, cls: Any):
		assert cls.arity() == ARITY[cls]

	@pytest.mark.parametrize("cls", RUNGS)
	def test_arity_is_derived_from_the_chain_not_stored(self, cls: Any):
		expected = 1
		below = carrier(cls)

		while issubclass(below, Set):
			expected += 1
			below = carrier(below)

		assert cls.arity() == expected

	def test_an_explicit_carrier_overrides_derivation(self):
		class Custom(Graph, truth = FuzzySet):
			...

		assert carrier(Custom) is FuzzySet

	@pytest.mark.parametrize("cls", RUNGS)
	def test_every_rung_shares_the_ground_carrier_of_its_tower(self, cls: Any):
		ground = carrier(cls)

		while issubclass(ground, Set):
			ground = carrier(ground)

		assert ground is (Bool if cls in CRISP_RUNGS else Prob)


class TestHierarchy:

	def test_a_rung_is_a_set_is_a_node_is_a_boolean(self):
		assert issubclass(Graph, Set) and issubclass(Set, Node) and issubclass(Node, Boolean)

	def test_a_node_is_not_a_set(self):
		assert not issubclass(Node, Set)

	def test_a_node_is_a_defaultdict(self):
		assert isinstance(Graph(), dict)

	def test_the_mro_puts_the_tower_between_the_rung_and_the_container(self):
		names = [cls.__name__ for cls in Graph.__mro__]

		assert names[:3] == ["Graph", "Set", "Node"]


class TestSerialisation:

	@pytest.mark.parametrize("cls", RUNGS)
	def test_every_rung_is_a_module_level_name_so_it_pickles(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 41)

		assert pickle.loads(pickle.dumps(node)) == node

	@pytest.mark.parametrize("cls", RUNGS)
	def test_the_class_survives_too(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 43)

		assert type(pickle.loads(pickle.dumps(node))) is cls

	@pytest.mark.parametrize("cls", RUNGS)
	def test_a_reconstructed_node_is_independent(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 47)
		clone = pickle.loads(pickle.dumps(node))

		clone.clear()

		assert node != clone or not node
