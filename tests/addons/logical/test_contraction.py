"""§4 — `abs` as the fold of the dual sum, and `contracted` as its single pass."""

from __future__ import annotations


import random

from fractions import Fraction
from functools import reduce
from typing import Any

import pytest

from addons.logical import Bool, Dist, FuzzySet, Graph, IndexSet, Node, Prob

from .conftest import CRISP_RUNGS, GRADED_RUNGS, Hyper, RUNGS, carrier, oplus, rank, sample


BACKGROUNDS = (None, Prob.minimum(), Prob.maximum())
CRISP_BACKGROUNDS = BACKGROUNDS
GRADED_BACKGROUNDS = (Prob(1, 3), Prob(2, 5), Prob(3, 4))   # crisped on construction


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


class TestTheSinglePassAgreesEverywhere:
	"""With graded backgrounds eliminated, the single pass reaches `abs` at every background."""

	@pytest.mark.parametrize("cls", CRISP_RUNGS + GRADED_RUNGS)
	@pytest.mark.parametrize("background", ["false", "true"])
	def test_every_rung_and_polarity_agrees(self, cls: Any, background: str):
		grounding = carrier(cls).minimum() if background == "true" else None

		for seed in range(30):
			node = sample(cls, cls.arity(), seed = seed, background = grounding)

			assert iterate(node) == abs(node)

	def test_a_would_be_graded_background_agrees_because_it_is_crisped(self):
		for background in GRADED_BACKGROUNDS:
			for seed in range(60):
				for cls, arity in ((FuzzySet, 1), (Graph, 2)):
					node = sample(cls, arity, seed = seed, background = background)

					assert iterate(node) == abs(node)

	def test_abs_is_still_defined_directly_rather_than_through_the_single_pass(self):
		assert "contracted" not in Node.__abs__.__code__.co_names


class TestSeriesAndParallel:

	def test_addition_composes_difficulties_in_series(self):
		assert Dist(1, 2) + Dist(1, 3) == Dist(5, 6)

	def test_oplus_composes_conductances_in_parallel(self):
		"""`1/d = 1/d1 + 1/d2` — the De Morgan dual of series, which is what parallel is."""
		assert oplus(Dist(1, 2), Dist(1, 3)) == Dist(1, 5)

	def test_the_two_are_dual(self):
		for a, b in ((Dist(1, 2), Dist(1, 3)), (Dist(2, 1), Dist(3, 1)), (Dist(1, 1), Dist(4, 5))):
			assert oplus(a, b) == ~(~a + ~b)

	def test_the_four_aggregations_are_genuinely_distinct(self):
		a, b = Prob(1, 2), Prob(1, 2)

		extension = a + b
		parallel = oplus(a, b)
		disjunction = a | b
		choice = max(a, b)

		assert len({extension, parallel, disjunction, choice}) == 4

	def test_abs_is_the_parallel_bundle_not_the_best_route(self):
		node = FuzzySet({0: Prob(1, 2), 1: Prob(1, 4)})

		assert abs(node) == oplus(Prob(1, 2), Prob(1, 4))
		assert abs(node) != max(node.values())


class TestSelfDuality:
	"""`abs(~s) == ~abs(s)`, now unconditional — the branch is the De Morgan switch."""

	@pytest.mark.parametrize("background", BACKGROUNDS + GRADED_BACKGROUNDS)
	def test_it_holds_at_every_background(self, background: Prob | None):
		for seed in range(60):
			node = sample(Graph, 2, seed = seed, background = background)

			assert abs(~node) == ~abs(node)

	@pytest.mark.parametrize("cls", RUNGS)
	def test_it_holds_for_every_rung(self, cls: Any):
		node = sample(cls, cls.arity(), seed = 53)

		assert abs(~node) == ~abs(node)

	@pytest.mark.parametrize("scalar", [Prob.minimum(), Prob.maximum(), Prob(1, 3), Prob(3, 4)])
	def test_complement_always_flips_because_the_background_is_crisp(self, scalar: Prob):
		node = FuzzySet(scalar)

		assert node.complement is not (~node).complement


class TestTheBranchOnComplement:
	"""Why `__abs__` branches: each fold has the background as its identity."""

	def test_a_recorded_non_deviation_is_invisible_to_the_measure(self):
		plain: FuzzySet[str] = FuzzySet()
		before = abs(plain)
		plain["x"] = Prob.maximum()

		assert abs(plain) == before

		complemented = ~IndexSet()
		before = abs(complemented)
		complemented["x"] = Bool.minimum()

		assert abs(complemented) == before

	def test_it_holds_under_reads_for_a_crisp_background(self):
		"""Which is what makes `abs` stable, since reads autovivify."""
		for background in (Prob.maximum(), Prob.minimum()):
			node = FuzzySet(background)
			before = abs(node)

			for key in "abcd":
				_ = node[key]

			assert len(node) == 4 and abs(node) == before

	def test_abs_respects_equality(self):
		"""`abs` is a function on the algebra, so equal values must have equal measures."""
		bare, padded = FuzzySet(Prob.minimum()), FuzzySet(Prob.minimum())

		for key in "abc":
			_ = padded[key]

		assert abs(bare) == abs(padded)
		assert len(bare) != len(padded), "they differ only in redundant coverage"

	def test_comparison_may_vivify_but_cannot_change_a_value(self):
		"""Vivification records the background, which is the fold's identity — structurally inert."""
		left, right = FuzzySet(Prob.minimum()), FuzzySet({"a": Prob(1, 4)})
		before = (abs(left), abs(right))

		_ = left == right
		_ = left | right
		_ = left & right

		assert (abs(left), abs(right)) == before

	def test_the_identities_are_the_two_crisp_backgrounds(self):
		assert Prob.maximum() == Prob.maximum() | Prob.maximum()
		assert Prob.minimum() + Prob.minimum() == Prob.minimum()

	def test_abs_and_bool_disagree_on_a_complemented_set_with_holes(self):
		"""Characterisation of the §9 defect: `bool` asks *any*, `abs` under a complement asks *all*."""
		assert bool(~IndexSet(["a"])) and not bool(abs(~IndexSet(["a"])))

		for node in (IndexSet(["a"]), IndexSet(), ~IndexSet()):
			assert bool(node) == bool(abs(node)), "they agree everywhere else"
