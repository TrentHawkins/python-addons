"""§6 — `Path`, the addressing boundary, and `Edge`, the path that knows its orbit."""

from __future__ import annotations


import copy
import pickle

from itertools import permutations

import pytest

from addons.logical import Edge, Path


class TestConstruction:

	def test_coordinates_are_variadic(self):
		assert tuple(Path(1, 2, 3)) == (1, 2, 3)
		assert tuple(Path()) == ()

	@pytest.mark.parametrize("bad", [slice(1, None), slice(None, 5), slice(1, 5, 2), slice(None, None, 2)])
	def test_a_bounded_slice_is_refused_at_construction(self, bad: slice):
		with pytest.raises(KeyError, match = "unbounded"):
			Path(1, bad)

	def test_an_unbounded_slice_is_admitted(self):
		assert len(Path(1, slice(None))) == 2

	def test_validation_happens_once_so_accessors_need_not_recheck(self):
		path = Path(1, slice(None))

		assert not path.contracts(1) and path.contracts(slice(None))


class TestNormalisation:

	@pytest.mark.parametrize("key, expected", [
		(1, (1,)),
		((1, 2), (1, 2)),
		("uv", ("uv",)),
		(slice(None), (slice(None),)),
		(None, (None,)),
	])
	def test_read_turns_any_subscript_into_one_type(self, key: object, expected: tuple):
		path = Path.read(key)  # pyright: ignore[reportArgumentType]

		assert isinstance(path, Path) and tuple(path) == expected

	def test_read_leaves_a_path_alone(self):
		path = Path(1, 2)

		assert Path.read(path) is path

	def test_read_preserves_an_edge(self):
		edge = Edge(1, 2)

		assert Path.read(edge) is edge and isinstance(Path.read(edge), Edge)

	def test_a_string_is_one_coordinate_not_its_characters(self):
		assert tuple(Path.read("abc")) == ("abc",)


class TestContraction:

	@pytest.mark.parametrize("coordinate, expected", [(None, True), (slice(None), True), (1, False), ("x", False), (0, False)])
	def test_contracts_recognises_a_sentinel(self, coordinate: object, expected: bool):
		assert Path.contracts(coordinate) is expected

	@pytest.mark.parametrize("coordinates, expected", [
		((1, 2), False),
		((1, None), True),
		((slice(None), 2), True),
		((None, None), True),
		((), False),
	])
	def test_contracting_asks_of_the_whole_path(self, coordinates: tuple, expected: bool):
		assert Path(*coordinates).contracting is expected

	def test_truthiness_is_left_as_plain_tuple_semantics(self):
		"""A non-empty tuple that is falsy would break `filter`, `any` and every `if seq:`."""
		assert bool(Path(1, None)) and not bool(Path())

		paths = [Path(1, 2), Path(1, None), Path(3, 4)]

		assert len(list(filter(None, paths))) == 3


class TestEdge:

	def test_an_edge_is_a_path(self):
		assert issubclass(Edge, Path) and isinstance(Edge(1, 2), Path)

	def test_it_inherits_construction_and_validation(self):
		assert "__new__" not in Edge.__dict__

		with pytest.raises(KeyError, match = "unbounded"):
			Edge(1, slice(1, 5))

	def test_permutations_are_the_orbit(self):
		assert {tuple(edge) for edge in Edge(1, 2, 3).permutations} == set(permutations((1, 2, 3)))

	def test_permutations_stay_edges(self):
		assert all(isinstance(edge, Edge) for edge in Edge(1, 2).permutations)

	def test_permutations_are_deduplicated(self):
		assert len(Edge(1, 1, 2).permutations) == 3

	def test_a_singleton_orbit_is_itself(self):
		assert Edge(1).permutations == {Edge(1)}


class TestSerialisation:

	@pytest.mark.parametrize("cls", [Path, Edge])
	def test_it_survives_pickling(self, cls: type):
		"""A varargs `__new__` needs `__getnewargs__`: `tuple`'s hands back a nested one-tuple."""
		value = cls(1, 2, 3)

		assert pickle.loads(pickle.dumps(value)) == value
		assert len(pickle.loads(pickle.dumps(value))) == 3

	@pytest.mark.parametrize("cls", [Path, Edge])
	def test_it_survives_copying(self, cls: type):
		value = cls(1, 2, 3)

		assert copy.copy(value) == value and copy.deepcopy(value) == value

	@pytest.mark.parametrize("cls", [Path, Edge])
	def test_the_type_survives_too(self, cls: type):
		assert type(pickle.loads(pickle.dumps(cls(1, 2)))) is cls


class TestTupleNature:

	def test_it_hashes_and_compares_as_a_tuple(self):
		assert hash(Path(1, 2)) == hash((1, 2)) and Path(1, 2) == (1, 2)

	def test_it_unpacks_and_slices(self):
		head, *rest = Path(1, 2, 3)

		assert head == 1 and rest == [2, 3]
		assert Path(1, 2, 3)[1:] == (2, 3)

	def test_an_unbounded_slice_is_hashable_which_is_why_reserving_it_costs_something(self):
		assert hash(slice(None)) is not None and slice(None) == slice(None)
