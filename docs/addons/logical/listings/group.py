from abc import ABC, abstractmethod
from typing import Literal, Self
class Magma(ABC):
	"""A carrier closed under one binary operation, written here as addition."""
	@abstractmethod
	def __add__(self, other: Self, /) -> Self:
		"""a + b, supplied by the concrete carrier; every fallback chain ends here, declining."""
		return NotImplemented
	def __pos__(self) -> Self:
		return self  # +a = a
class Semigroup(Magma):
	"""A magma whose operation is associative: a law, hence no new method."""
class Monoid(Semigroup):
	"""A semigroup with an identity, spelled by the literal 0; a carrier handles a + b and defers a + 0 here."""
	@abstractmethod
	def __add__(self, other: Self | Literal[0], /) -> Self:
		if other == 0:
			return self  # a + 0 = a
		return super().__add__(other)  # a + b is the carrier's to define
	def __radd__(self, other: Literal[0], /) -> Self:
		if other == 0:
			return self  # 0 + a = a, which is what the builtin sum relies on
		return NotImplemented
class Group(Monoid):
	"""A monoid in which every element has an inverse, written as the unary minus."""
	def __sub__(self, other: Self, /) -> Self:
		return self + -other  # a - b = a + (-b)
	@abstractmethod
	def __neg__(self) -> Self:
		"""-a, supplied by the concrete carrier."""
