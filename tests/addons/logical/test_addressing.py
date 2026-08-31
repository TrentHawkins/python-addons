"""§6 — tuple keying is rung keying, the rank law, and the border sentinel."""

from __future__ import annotations


from typing import Any

import pytest

from addons.logical import Bool, Edge, FuzzySet, Graph, IndexSet, Path, Prob

from .conftest import ARITY, RUNGS, Hyper, rank, sample


SENTINELS = [None, slice(None)]


class TestTupleIsRung:

	def test_a_full_path_equals_the_chain(self, triangle: Any):
		assert triangle[1, 2, 3] == triangle[1][2][3] == Prob(3, 4)

	def test_a_partial_path_equals_the_partial_chain(self, triangle: Any):
		assert triangle[1, 2] == triangle[1][2]

	def test_a_bare_key_and_a_one_tuple_agree(self, triangle: Any):
		assert triangle[1] == triangle[1,]

	def test_the_empty_path_is_the_whole_tensor(self, triangle: Any):
		assert triangle[()] == triangle

	def test_the_parenthesised_and_bare_forms_are_one_expression(self, graph: Any):
		assert graph[0, 1] == graph[(0, 1)]

	def test_a_tuple_is_no_longer_a_key(self):
		"""The narrowing §6 pays for the notation: `K` loses `tuple`, `None` and `slice`."""
		node: IndexSet[Any] = IndexSet()

		with pytest.raises(KeyError, match = "coordinates"):
			node[0, 0] = True

	@pytest.mark.parametrize("cls", RUNGS)
	def test_an_over_long_write_path_is_refused_like_a_read(self, cls: Any):
		node = cls()

		with pytest.raises(KeyError, match = "coordinates"):
			node[(0,) * (ARITY[cls] + 1)] = cls.truth.minimum()


class TestRankLaw:

	@pytest.mark.parametrize("coordinates, length", [
		((1,), 1),
		((1, 2), 2),
		((1, 2, 3), 3),
		((slice(None),), 1),
		((slice(None), 2), 2),
		((1, None), 2),
		((1, slice(None), 3), 3),
		((None, None, None), 3),
	])
	def test_rank_falls_by_the_length_sentinels_included(self, triangle: Any, coordinates: tuple, length: int):
		assert rank(triangle[coordinates]) == 3 - length

	def test_a_bare_key_drops_one_axis(self, triangle: Any):
		assert rank(triangle[1]) == 2 and rank(triangle[slice(None)]) == 2

	@pytest.mark.parametrize("cls", RUNGS)
	def test_a_full_path_is_a_scalar_for_every_rung(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 29)

		assert rank(node[(0,) * ARITY[cls]]) == 0

	@pytest.mark.parametrize("cls", RUNGS)
	def test_an_over_long_path_is_refused(self, cls: Any):
		node = cls()

		with pytest.raises(KeyError, match = "coordinates"):
			node[(0,) * (ARITY[cls] + 1)]


class TestSentinel:

	@pytest.mark.parametrize("sentinel", SENTINELS)
	def test_both_spellings_agree(self, graph: Any, sentinel: Any):
		assert graph[0, sentinel] == graph[0, :] == abs(graph[0])

	def test_a_trailing_sentinel_is_abs_of_the_row(self, graph: Any):
		assert graph[0, :] == abs(graph[0])

	def test_a_bare_sentinel_gives_the_border_vector(self, graph: Any):
		border = graph[:]

		assert rank(border) == 1
		assert border[1] == graph[:, 1]

	def test_the_full_contraction_is_abs(self, graph: Any):
		assert graph[:, :] == abs(graph)

	def test_an_interior_sentinel_gathers(self, triangle: Any):
		gathered = FuzzySet({key: triangle[1, key, 3] for key in dict.keys(triangle[1])})

		assert triangle[1, :, 3] == abs(gathered)

	@pytest.mark.parametrize("bad", [slice(1, None), slice(None, 5), slice(1, 5, 2)])
	def test_a_bounded_slice_is_refused(self, graph: Any, bad: slice):
		with pytest.raises(KeyError, match = "unbounded"):
			graph[0, bad]

	def test_a_sentinel_never_autovivifies(self):
		node: Graph[str] = Graph()

		_ = node[:]

		assert len(node) == 0


class TestWrites:

	@pytest.mark.parametrize("key", [(0, slice(None)), (slice(None), 1), slice(None), None, (None, None)])
	def test_a_contracted_axis_is_not_a_location(self, graph: Any, key: Any):
		with pytest.raises(KeyError, match = "contracted"):
			graph[key] = Prob(1, 2)

	@pytest.mark.parametrize("key", [(0, slice(None)), (slice(None), 1), slice(None)])
	def test_deletion_refuses_it_too(self, graph: Any, key: Any):
		with pytest.raises(KeyError, match = "contracted"):
			del graph[key]

	def test_an_empty_path_is_not_a_location(self, graph: Any):
		with pytest.raises(KeyError, match = "empty"):
			graph[()] = Prob(1, 2)

	def test_a_write_lands_where_the_chain_would(self):
		node: Graph[str] = Graph()
		node["u", "v"] = Prob(3, 4)

		assert node["u"]["v"] == Prob(3, 4)  # pyright: ignore[reportIndexIssue] -- the over-wide `Set | E` union of §9

	def test_a_partial_write_assigns_a_whole_neighbourhood(self):
		node: Graph[str] = Graph()
		node["u"] = FuzzySet({"v": Prob(1, 2)})

		assert node["u", "v"] == Prob(1, 2)

	def test_a_scalar_written_to_a_deep_rung_becomes_a_background(self):
		node: Graph[str] = Graph()
		node["u"] = Prob(1, 2)

		neighbourhood = node["u"]

		assert isinstance(neighbourhood, FuzzySet) and neighbourhood.default == Prob(1, 2)

	def test_deletion_forgets_the_record(self):
		node: Graph[str] = Graph()
		node["u", "v"] = Prob(3, 4)

		del node["u", "v"]

		assert node["u", "v"] == Prob.maximum()

	def test_the_coercion_sandwich_keeps_a_rung_uniform(self):
		"""Which is why the single pass of §4 is total in practice."""
		graded: Graph[str] = Graph()
		graded["x"] = Prob(1, 2)

		flat: FuzzySet[str] = FuzzySet()
		flat["y"] = FuzzySet({"a": Prob(3, 4)})

		assert isinstance(dict.__getitem__(graded, "x"), FuzzySet)
		assert isinstance(dict.__getitem__(flat, "y"), Prob)


class TestLocate:

	def test_it_returns_the_holder_and_the_final_coordinate(self):
		node: Graph[str] = Graph()
		node["u", "v"] = Prob(3, 4)

		holder, last = node.locate(("u", "v"))

		assert holder is node["u"] and last == "v"

	def test_a_bare_key_locates_in_place(self):
		node: Graph[str] = Graph()
		holder, last = node.locate("u")

		assert holder is node and last == "u"


class TestConstructionFromPaths:

	def test_an_iterable_of_paths(self):
		node: Graph[str] = Graph([Edge("u", "v"), Edge("v", "w")])

		assert node["u", "v"] == Bool.minimum() and node["v", "w"] == Bool.minimum()

	def test_a_mapping_of_paths(self):
		node: Graph[str] = Graph({Edge("u", "v"): Prob(1, 2)})

		assert node["u", "v"] == Prob(1, 2)

	def test_plain_tuples_work_the_same(self):
		node: Graph[str] = Graph({("u", "v"): Prob(1, 2)})

		assert node["u", "v"] == Prob(1, 2)

	def test_membership_routes(self):
		node: Graph[str] = Graph()
		node["u", "v"] = Prob(3, 4)

		assert ("u", "v") in node and Edge("u", "v") in node


class TestEdgeAndSentinelDoNotMix:

	def test_an_edge_is_a_perfectly_good_subscript(self, graph: Any):
		assert graph[Edge(0, 1)] == graph[0, 1]

	def test_a_sentinel_path_is_written_as_a_bare_tuple_or_with_none(self, graph: Any):
		assert graph[0, :] == graph[Edge(0, None)] == graph[Path(0, None)]
