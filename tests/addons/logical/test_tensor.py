"""§7 — the bordered tensor: derived borders, position-dependent views, closure."""

from __future__ import annotations


from itertools import combinations
from typing import Any

import pytest

from addons.logical import Bool, FuzzySet, Graph, IndexSet, Prob, UnweightedGraph

from .conftest import Hyper, carrier, sample


MATRIX = [
	[0, 0, 0, 1],
	[0, 0, 0, 0],
	[1, 0, 0, 0],
	[0, 0, 1, 0],
]


def views(rank: int, face: tuple[Any, ...]) -> list[tuple[Any, ...]]:
	"""Every placement of a face's coordinates into the tensor's positions, in order."""
	placements: list[tuple[Any, ...]] = []

	for positions in combinations(range(rank), len(face)):
		path: list[Any] = [slice(None)] * rank

		for position, coordinate in zip(positions, face):
			path[position] = coordinate

		placements.append(tuple(path))

	return placements


@pytest.fixture
def bordered() -> UnweightedGraph[int]:
	node: UnweightedGraph[int] = UnweightedGraph()

	for row, values in enumerate(MATRIX, 1):
		for column, value in enumerate(values, 1):
			if value:
				node[row, column] = True

	return node


class TestBorderedMatrix:

	def test_the_left_border_is_out_existence(self, bordered: Any):
		assert [int(bool(bordered[row, :])) for row in range(1, 5)] == [1, 0, 1, 1]

	def test_the_top_border_is_in_existence(self, bordered: Any):
		assert [int(bool(bordered[:, column])) for column in range(1, 5)] == [1, 0, 1, 1]

	def test_the_corner_is_the_whole_contraction(self, bordered: Any):
		assert bordered[:, :] == abs(bordered) == Bool(True)

	def test_a_vertex_with_no_incident_edge_is_invisible(self, bordered: Any):
		assert not bordered[2, :] and not bordered[:, 2]

	def test_an_unrecorded_vertex_is_invisible_too(self, bordered: Any):
		assert not bordered[99, :]

	def test_the_borders_are_derived_not_stored(self, bordered: Any):
		assert set(dict.keys(bordered)) == {1, 3, 4}, "no border ever became a key"


class TestViews:

	def test_a_vertex_of_a_graph_has_two(self):
		node: UnweightedGraph[str] = UnweightedGraph()
		node["a", "b"] = True

		assert bool(node["a", :]) and not bool(node[:, "a"])
		assert not bool(node["b", :]) and bool(node[:, "b"])

	@pytest.mark.parametrize("face, count", [((1,), 3), ((1, 2), 3), ((1, 2, 3), 1)])
	def test_the_count_is_n_choose_k_plus_one(self, face: tuple, count: int):
		assert len(views(3, face)) == count

	def test_they_genuinely_differ_when_directed(self, triangle: Any):
		edge = [triangle[view] for view in views(3, (1, 2))]
		vertex = [triangle[view] for view in views(3, (1,))]

		assert edge == [Prob(3, 4), Prob.maximum(), Prob.maximum()]
		assert vertex == [Prob(3, 4), Prob.maximum(), Prob.maximum()]

	def test_the_facet_matrices_share_the_corner(self):
		node = sample(Hyper, 3, seed = 31)

		assert node[:, :, :] == abs(node)


class TestClosure:

	def test_a_face_is_at_least_as_true_as_its_coface(self, triangle: Any):
		assert triangle[1, 2, :] >= triangle[1, 2, 3]
		assert triangle[1, :, :] >= triangle[1, 2, :]

	def test_it_holds_across_a_sampled_tensor(self):
		node = sample(Hyper, 3, seed = 37, keys = 4)

		for i in range(4):
			for j in range(4):
				for k in range(4):
					assert node[i, j, :] >= node[i, j, k]
					assert node[i, :, :] >= node[i, j, :]

	def test_it_is_structural_rather_than_maintained(self):
		"""Nothing enforces closure; monotonicity of the fold makes it unavoidable."""
		node: Hyper[int] = Hyper()
		node[1, 2, 3] = Prob(3, 4)

		assert node[1, 2, :] >= Prob(3, 4)


class TestDegenerateCells:

	def test_a_repeated_coordinate_records_a_lower_face(self, triangle: Any):
		assert triangle[4, 5, :] == Prob(1, 2)

	def test_it_borders_upward_correctly(self, triangle: Any):
		assert triangle[4, :, :] == Prob(1, 2)

	def test_the_genuine_and_degenerate_cells_coexist(self, triangle: Any):
		assert triangle[1, 2, :] == Prob(3, 4) and triangle[4, 5, :] == Prob(1, 2)

	def test_an_unrecorded_vertex_stays_invisible(self, triangle: Any):
		assert triangle[9, :, :] == Prob.maximum()


class TestRepresentationalCorrespondence:

	def test_roster_and_indicator_are_one_object(self):
		node = IndexSet(["a", "b"])

		assert set(node) == {"a", "b"}
		assert node["a"] == Bool(True) and node["c"] == Bool(False)

	def test_adjacency_list_and_matrix_are_one_object(self, bordered: Any):
		assert set(bordered[1]) == {4}
		assert bordered[1, 4] == Bool(True) and bordered[1, 3] == Bool(False)

	def test_unweighted_is_weighted_with_a_crisp_carrier(self):
		assert carrier(UnweightedGraph) is IndexSet and carrier(Graph) is FuzzySet
		assert carrier(IndexSet) is Bool and carrier(FuzzySet) is Prob
