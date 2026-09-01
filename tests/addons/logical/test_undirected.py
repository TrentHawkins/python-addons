"""§8 — mirroring, what symmetry buys, and every way the invariant is known to break."""

from __future__ import annotations


from itertools import permutations
from typing import Any

import pytest

from addons.logical import Bool, Edge, FuzzySet, Graph, Prob, Undirected, UnweightedGraph

from .conftest import (
	CrispHyper, Hyper, IndexSet, PropagatedGraph, PropagatedHyper,
	UndirectedFuzzySet, UndirectedGraph, UndirectedHyper, carrier, present, registry,
)


class TestOrbitConstancy:

	def test_a_write_lands_on_every_ordering(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a", "b"] = Prob(1, 2)

		assert node["a", "b"] == node["b", "a"] == Prob(1, 2)

	def test_it_holds_at_rank_three(self):
		node: UndirectedHyper[int] = UndirectedHyper()
		node[1, 2, 3] = Prob(3, 4)

		assert all(node[order] == Prob(3, 4) for order in permutations((1, 2, 3)))

	def test_an_edge_and_a_plain_tuple_both_mirror(self):
		by_edge: UndirectedGraph[str] = UndirectedGraph()
		by_tuple: UndirectedGraph[str] = UndirectedGraph()

		by_edge[Edge("a", "b")] = Prob(1, 2)
		by_tuple["a", "b"] = Prob(1, 2)

		assert by_edge == by_tuple

	def test_a_bare_key_is_left_alone(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a"] = FuzzySet({"b": Prob(1, 2)})

		assert node["a", "b"] == Prob(1, 2)

	def test_deletion_removes_the_whole_orbit(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a", "b"] = Prob(1, 2)

		del node["a", "b"]

		assert not present(node, "a", "b") and not present(node, "b", "a")

	def test_a_degenerate_orbit_is_a_single_cell(self):
		node: UndirectedHyper[int] = UndirectedHyper()
		node[1, 1, 2] = Prob(1, 2)

		assert len(Edge(1, 1, 2).permutations) == 3
		assert node[1, 1, 2] == node[1, 2, 1] == node[2, 1, 1] == Prob(1, 2)


class TestWhatSymmetryBuys:

	def test_the_views_collapse(self):
		node: UndirectedHyper[int] = UndirectedHyper()
		node[1, 2, 3] = Prob(3, 4)

		assert node[1, 2, :] == node[1, :, 2] == node[:, 1, 2] == Prob(3, 4)

	def test_in_and_out_existence_become_one_vertex_weight(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a", "b"] = Prob(1, 2)

		assert node["a", :] == node[:, "a"]

	def test_a_link_inherits_symmetry_with_no_mixin_on_it(self):
		node: UndirectedHyper[int] = UndirectedHyper()
		node[1, 2, 3] = Prob(3, 4)

		link = node[1]

		assert type(link) is carrier(Hyper), "the link carries no mixin"
		assert link[2, 3] == link[3, 2]  # pyright: ignore[reportIndexIssue]


class TestKnownBreakages:
	"""Characterisation: these record the documented failures of §9, not desired behaviour."""

	def test_a_chained_write_bypasses_the_mixin(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a"]["b"] = Prob(1, 2)  # pyright: ignore[reportIndexIssue]

		assert node["a", "b"] == Prob(1, 2)
		assert node["b", "a"] != Prob(1, 2), "the mixin never saw the pair"

	def test_which_is_exactly_where_the_tuple_rung_identity_fails(self):
		paired: UndirectedGraph[str] = UndirectedGraph()
		chained: UndirectedGraph[str] = UndirectedGraph()

		paired["a", "b"] = Prob(1, 2)
		chained["a"]["b"] = Prob(1, 2)  # pyright: ignore[reportIndexIssue]

		assert paired["a", "b"] == chained["a", "b"], "reads agree"
		assert paired != chained, "writes do not"

	def test_assigning_a_whole_neighbourhood_does_not_mirror(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a"] = FuzzySet({"b": Prob(1, 2)})

		assert node["b", "a"] != Prob(1, 2)

	def test_deleting_a_vertex_leaves_the_reverse_orderings(self):
		node: UndirectedGraph[str] = UndirectedGraph()
		node["a", "b"] = Prob(1, 2)

		del node["a"]

		assert present(node, "b", "a"), "the reverse ordering survives"

	def test_deletion_is_not_atomic_when_the_orbit_is_already_broken(self):
		node: UndirectedHyper[int] = UndirectedHyper()
		node[1, 2, 3] = Prob(3, 4)

		dict.__delitem__(dict.__getitem__(dict.__getitem__(node, 3), 1), 2)

		before = sum(present(node, *order) for order in permutations((1, 2, 3)))

		with pytest.raises(KeyError):
			del node[1, 2, 3]

		after = sum(present(node, *order) for order in permutations((1, 2, 3)))

		assert before == 5 and 0 < after < before, "it mutated, then raised"


class TestPropagation:

	def test_a_parallel_tower_is_declarable_with_no_new_machinery(self):
		assert carrier(PropagatedGraph) is UndirectedFuzzySet
		assert carrier(PropagatedHyper) is PropagatedGraph
		assert PropagatedGraph.arity() == 2 and PropagatedHyper.arity() == 3

	def test_it_does_not_claim_a_registry_slot(self):
		from addons.logical import Set  # noqa: PLC0415

		assert PropagatedGraph not in registry()[True]
		assert PropagatedHyper not in registry()[True]

	def test_a_propagated_link_carries_the_mixin(self):
		node: PropagatedHyper[int] = PropagatedHyper()
		node[1, 2, 3] = Prob(3, 4)

		assert isinstance(node[1], Undirected)

	def test_propagation_repairs_only_the_point_stabilizer(self):
		"""`|Stab(0)| / |S_n|` = `1/n` of the orbit — two of six at rank three."""
		propagated: PropagatedHyper[int] = PropagatedHyper()
		plain: UndirectedHyper[int] = UndirectedHyper()

		propagated[1][2, 3] = Prob(3, 4)  # pyright: ignore[reportIndexIssue]
		plain[1][2, 3] = Prob(3, 4)  # pyright: ignore[reportIndexIssue]

		repaired = sum(propagated[order] == Prob(3, 4) for order in permutations((1, 2, 3)))
		bare = sum(plain[order] == Prob(3, 4) for order in permutations((1, 2, 3)))

		assert repaired == 2 and bare == 1


class TestOrthogonality:

	@pytest.mark.parametrize("mixed, arity, truth", [
		("IndexSet", 1, Bool),
		("FuzzySet", 1, Prob),
		("UnweightedGraph", 2, Bool),
		("Graph", 2, Prob),
		("CrispHyper", 3, Bool),
		("Hyper", 3, Prob),
	])
	def test_one_mixin_serves_every_rung(self, mixed: str, arity: int, truth: type):
		base = {
			"IndexSet": IndexSet, "FuzzySet": FuzzySet, "UnweightedGraph": UnweightedGraph,
			"Graph": Graph, "CrispHyper": CrispHyper, "Hyper": Hyper,
		}[mixed]

		mirrored = type(f"Undirected{mixed}", (Undirected, base), {})
		node: Any = mirrored()
		coordinates = tuple(range(arity))

		node[coordinates] = truth.minimum()

		assert all(node[order] == truth.minimum() for order in permutations(coordinates))

	def test_the_orbit_group_follows_the_length(self):
		assert len(Edge(1, 2).permutations) == 2
		assert len(Edge(1, 2, 3).permutations) == 6
		assert len(Edge(1, 2, 3, 4).permutations) == 24
