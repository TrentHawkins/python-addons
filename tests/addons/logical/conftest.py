"""Shared fixtures and generators.

Rung classes are declared **here and only here**: every rung claims a slot in
`Set.registry`, so a second declaration of the same `(weighted, depth)` pair raises.
"""

from __future__ import annotations


import random

from typing import Any, cast

import pytest

from addons.logical import Bool, Dist, Edge, FuzzySet, Graph, IndexSet, Node, Prob, Set, Undirected, UnweightedGraph


class Hyper[V](Set[V, Prob], weighted = True, depth = 2):
	"""A graded rank-3 rung — triangles with probabilistic weight."""


class CrispHyper[V](Set[V, Bool], weighted = False, depth = 2):
	"""A crisp rank-3 rung."""


class UndirectedFuzzySet[I](Undirected[I, Prob, "Set[I, Prob] | Prob"], FuzzySet[I]):
	"""The rank-1 rung of a propagated undirected tower."""


class UndirectedGraph[V](Undirected[V, Prob, "Set[V, Prob] | Prob"], Graph[V]):
	"""Mirroring over a rank-2 tensor.

	The mixin has to be parameterised explicitly: bare `Undirected` defaults to
	`Node[K, Bool, Bool]`, which is not the rung's `Node[V, Prob, Set | Prob]`.
	"""


class UndirectedHyper[V](Undirected[V, Prob, "Set[V, Prob] | Prob"], Hyper[V]):
	"""Mirroring over a rank-3 tensor."""


class PropagatedGraph[V](Undirected[V, Prob, "Set[V, Prob] | Prob"], Graph[V], truth = UndirectedFuzzySet):
	"""An undirected graph whose links are themselves undirected."""


class PropagatedHyper[V](Undirected[V, Prob, "Set[V, Prob] | Prob"], Hyper[V], truth = PropagatedGraph):
	"""A rank-3 undirected tensor whose links are undirected all the way down."""


RUNGS = (IndexSet, FuzzySet, UnweightedGraph, Graph, CrispHyper, Hyper)
GRADED_RUNGS = (FuzzySet, Graph, Hyper)
CRISP_RUNGS = (IndexSet, UnweightedGraph, CrispHyper)

ARITY = {IndexSet: 1, FuzzySet: 1, UnweightedGraph: 2, Graph: 2, CrispHyper: 3, Hyper: 3}


def oplus[T](a: Any, b: Any) -> Any:
	"""The De Morgan dual of the sum — the fold `abs` performs."""
	return ~(~a + ~b)


def carrier(cls: Any) -> Any:
	"""`cls.truth` through an `Any`.

	`truth: type[V]` is a generic instance variable, so pyright calls access through the
	class ambiguous. It is a plain class attribute at runtime; this localises the wart.
	"""
	return cls.truth


def registry() -> tuple[list[Any], list[Any]]:
	"""`Set.registry`, for the same reason."""
	return cast(Any, Set).registry


def rank(value: object) -> int:
	"""How many axes remain."""
	if not isinstance(value, Node):
		return 0

	values = list(dict.values(value))

	return 1 + rank(values[0]) if values else 1


def present(node: Node[Any, Any, Any], *coordinates: Any) -> bool:
	"""Presence, probed without autovivifying — `in` and `[]` both insert."""
	*head, last = coordinates

	for coordinate in head:
		if not dict.__contains__(node, coordinate):
			return False

		node = dict.__getitem__(node, coordinate)

	return dict.__contains__(node, last)


def probs(rng: random.Random, count: int, *, denominator: int = 8) -> list[Prob]:
	return [Prob(rng.randint(0, denominator), denominator) for _ in range(count)]


def sample(cls: Any, arity: int, *, seed: int, keys: int = 3, density: float = 0.6, background: Any = None) -> Any:
	"""A pseudo-random tensor of the given rung, filled to `density`."""
	rng = random.Random(seed)
	node = cls(default = background)
	crisp = cls in CRISP_RUNGS

	for coordinates in _coordinates(arity, keys):
		if rng.random() < density:
			node[coordinates] = Bool(rng.random() < 0.5) if crisp else Prob(rng.randint(0, 8), 8)

	return node


def _coordinates(arity: int, keys: int) -> list[tuple[int, ...]]:
	spans: list[tuple[int, ...]] = [()]

	for _ in range(arity):
		spans = [span + (key,) for span in spans for key in range(keys)]

	return spans


@pytest.fixture
def rng() -> random.Random:
	return random.Random(20260831)


@pytest.fixture
def graph() -> Graph[int]:
	"""A small, fully explicit rank-2 tensor."""
	node: Graph[int] = Graph()

	node[0, 0] = Prob(1, 2)
	node[0, 1] = Prob(1, 4)
	node[1, 1] = Prob(3, 4)

	return node


@pytest.fixture
def triangle() -> Hyper[int]:
	"""One genuine triangle and one degenerate cell."""
	node: Hyper[int] = Hyper()

	node[1, 2, 3] = Prob(3, 4)
	node[4, 5, 5] = Prob(1, 2)

	return node


__all__ = [
	"ARITY", "CRISP_RUNGS", "GRADED_RUNGS", "RUNGS",
	"Bool", "CrispHyper", "Dist", "Edge", "FuzzySet", "Graph", "Hyper", "IndexSet", "Node", "Prob",
	"PropagatedGraph", "PropagatedHyper", "Set", "Undirected", "UndirectedFuzzySet", "UndirectedGraph", "UndirectedHyper", "UnweightedGraph",
	"carrier", "oplus", "present", "probs", "rank", "registry", "sample",
]
