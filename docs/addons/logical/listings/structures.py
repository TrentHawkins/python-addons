from abc import ABC, abstractmethod
from typing import Self


class Magma(ABC):

	@abstractmethod
	def combine(self, other: Self, /) -> Self:
		...


class Semigroup(Magma):

	...


class Monoid(Semigroup):

	@classmethod
	@abstractmethod
	def identity(cls) -> Self:
		...


class Group(Monoid):

	@property
	@abstractmethod
	def inverse(self) -> Self:
		...
