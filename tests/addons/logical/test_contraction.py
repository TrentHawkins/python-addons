"""§4 — `abs` as the fold of the dual sum, and `contracted` as its single pass."""

from __future__ import annotations


import random

from fractions import Fraction
from functools import reduce
from typing import Any

import pytest

from addons.logical import Bool, Dist, FuzzySet, Graph, IndexSet, Node, Prob

from .conftest import CRISP_RUNGS, GRADED_RUNGS, Hyper, RUNGS, carrier, oplus, rank, sample


CRISP_BACKGROUNDS = (None, Prob.minimum(), Prob.maximum())
GRADED_BACKGROUNDS = (Prob(1, 3), Prob(2, 5), Prob(3, 4))


def iterate(node: Any) -> Any:
	while isinstance(node, Node):
		node = node.contracted

	return node


class TestTheFold:

	def test_abs_is_the_oplus_fold(self, rng: random.Random):
		for _ in range(400):
			values = [Prob(rng.randint(0, 8), 8) for _ in range(rng.randint(1, 5))]
			node = FuzzySet(dict(enumerate(values)))

			assert abs(node) == reduce(oplus, values)

	def test_oplus_is_or_on_the_crisp_carrier(self):
		for a in (True, False):
			for b in (True, False):
				assert bool(oplus(Bool(a), Bool(b))) == (a or b)

	def test_abs_is_any_on_a_crisp_node(self):
		assert abs(IndexSet(["a"])) == Bool(True)
		assert abs(IndexSet([])) == Bool(False)

	def test_it_is_parallel_conductance_in_dist_coordinates(self):
		"""`1/D = sum(1/d_i)` — the reason the `Dist` reading is the natural one."""
		values = [Prob(1, 3), Prob(1, 2), Prob(3, 4)]
		node = FuzzySet(dict(enumerate(values)))

		difficulties = [Fraction(*Dist(value).decoded) for value in values]
		parallel = 1 / sum(1 / difficulty for difficulty in difficulties)

		assert Fraction(*Dist(abs(node)).decoded) == parallel

	@pytest.mark.parametrize("count, numerator", [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
	def test_n_halves_give_n_over_n_plus_one_not_noisy_or(self, count: int, numerator: int):
		node = FuzzySet({index: Prob(1, 2) for index in range(count)})

		assert abs(node) == Prob(numerator, numerator + 1)

	def test_it_is_deliberately_not_the_or_fold(self):
		node = FuzzySet({0: Prob(1, 2), 1: Prob(1, 2)})

		assert abs(node) == Prob(2, 3)
		assert reduce(lambda a, b: a | b, node.values()) == Prob(3, 4)


class TestTheLaws:

	def test_it_is_monotone_so_closure_is_a_theorem(self, rng: random.Random):
		for _ in range(400):
			keys = rng.sample("abcdefg", rng.randint(1, 5))
			node = FuzzySet({key: Prob(rng.randint(0, 8), 8) for key in keys})

			assert all(abs(node) >= value for value in node.values())

	def test_it_is_order_independent_across_a_tensor(self):
		graph = sample(Graph, 2, seed = 3, keys = 4)
		keys = list(dict.keys(graph))

		rows = FuzzySet({key: abs(graph[key]) for key in keys})
		columns = FuzzySet({key: abs(FuzzySet({other: graph[other, key] for other in keys})) for key in keys})

		assert abs(graph) == abs(rows) == abs(columns)

	@pytest.mark.parametrize("cls", RUNGS)
	def test_an_empty_node_contracts_to_its_background(self, cls: Any):
		assert abs(cls()) == carrier(cls).maximum()
		assert abs(cls(carrier(cls).minimum())) == carrier(cls).minimum()


class TestTheSinglePass:

	def test_it_walks_the_tower_down_one_rung(self):
		node = sample(Hyper, 3, seed = 5)

		assert type(node.contracted) is Graph
		assert type(node.contracted.contracted) is FuzzySet
		assert type(node.contracted.contracted.contracted) is Prob

	@pytest.mark.parametrize("cls", RUNGS)
	def test_each_pass_drops_exactly_one_axis(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 17)

		assert rank(node.contracted) == rank(node) - 1

	def test_it_is_the_programmatic_spelling_of_the_bare_sentinel(self):
		graph = sample(Graph, 2, seed = 19)

		assert graph[:] == graph.contracted
		assert graph[None] == graph.contracted

	@pytest.mark.parametrize("cls", RUNGS)
	def test_iterating_it_reaches_abs(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 23)

		assert iterate(node) == abs(node)

	@pytest.mark.parametrize("background", CRISP_BACKGROUNDS)
	def test_it_respects_a_complemented_background(self, background: Prob | None):
		"""A naive fold of the recorded values ignores `default` and fails on every complement."""
		for seed in range(40):
			node = sample(Graph, 2, seed = seed, background = background)

			assert iterate(node) == abs(node)


class TestTheDivergence:

	@pytest.mark.parametrize("cls", CRISP_RUNGS + GRADED_RUNGS)
	@pytest.mark.parametrize("background", ["false", "true"])
	def test_crisp_backgrounds_always_agree(self, cls: Any, background: str):
		grounding = carrier(cls).minimum() if background == "true" else None

		for seed in range(30):
			node = sample(cls, cls.arity(), seed = seed, background = grounding)

			assert iterate(node) == abs(node)

	def test_rank_one_agrees_even_when_graded(self):
		for background in GRADED_BACKGROUNDS:
			for seed in range(50):
				node = sample(FuzzySet, 1, seed = seed, background = background)

				assert iterate(node) == abs(node)

	def test_a_graded_background_at_rank_two_diverges(self):
		"""Folding containers compounds their backgrounds; `abs` scalarises each child first."""
		divergent = [
			seed
			for background in GRADED_BACKGROUNDS
			for seed in range(60)
			if iterate(sample(Graph, 2, seed = seed, background = background)) != abs(sample(Graph, 2, seed = seed, background = background))
		]

		assert divergent, "the divergence is documented in §4 and must not vanish silently"

	def test_which_is_why_abs_is_not_defined_through_the_single_pass(self):
		assert Node.__abs__ is not None
		assert "contracted" not in Node.__abs__.__code__.co_names
