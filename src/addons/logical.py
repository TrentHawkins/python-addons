from __future__ import annotations


import abc
import builtins
import functools
import math
import typing


type pair[T] = tuple[T, T]


class Invertible(abc.ABC):

	@abc.abstractmethod
	def __invert__(self) -> typing.Self:
		...


class Boolean(Invertible):

	def  __or__(self, other: typing.Self, /) -> typing.Self: return ~(~self & ~other)
	def __and__(self, other: typing.Self, /) -> typing.Self: return ~(~self | ~other)
	def __sub__(self, other: typing.Self, /) -> typing.Self: return    self & ~other
	def __xor__(self, other: typing.Self, /) -> typing.Self:
		return (self | other) - (self & other)
	#	return (self - other) | (other - self)

	def union       (self, *others: typing.Self) -> typing.Self: return functools.reduce(self.__class__. __or__, others, self)
	def intersection(self, *others: typing.Self) -> typing.Self: return functools.reduce(self.__class__.__and__, others, self)
	def difference  (self, *others: typing.Self) -> typing.Self: return functools.reduce(self.__class__.__sub__, others, self)

	def symmetric_difference(self, other: typing.Self) -> typing.Self:
		return self ^ other


class Distance(abc.ABC):

	@abc.abstractmethod
	def __add__(self, other: typing.Self, /) -> typing.Self:
		...

	@abc.abstractmethod
	def __mul__(self, times: int, /) -> typing.Self:
		...


class Order(abc.ABC):

	@abc.abstractmethod
	def __le__(self, other: typing.Self, /) -> bool:
		...

	@abc.abstractmethod
	def __ge__(self, other: typing.Self, /) -> bool:
		...

	def __eq__(self, other: typing.Self, /) -> bool: return not self != other
	def __ne__(self, other: typing.Self, /) -> bool: return not self == other

	def __lt__(self, other: typing.Self, /) -> bool: return self <= other and self != other
	def __gt__(self, other: typing.Self, /) -> bool: return self >= other and self != other

	def issubset  (self, other: typing.Self, /) -> bool: return self <= other
	def issuperset(self, other: typing.Self, /) -> bool: return self >= other

	@abc.abstractmethod
	def isdisjoint(self, other: typing.Self, /) -> bool:
		...


class Partial(Order):

	def __le__(self, other: typing.Self, /) -> bool: return self < other or self == other
	def __ge__(self, other: typing.Self, /) -> bool: return self > other or self == other


class Total(Order):

	def __le__(self, other: typing.Self, /) -> bool: return not self > other
	def __ge__(self, other: typing.Self, /) -> bool: return not self < other
	def __eq__(self, other: typing.Self, /) -> bool:
		return self <= other and self >= other


class frac(Distance, Boolean, Total, abc.ABC):

	numer: int
	denom: int

	def __new__(cls,
		numer: int | frac = 0,
		denom: int        = 1, /
	) -> typing.Self:
		if isinstance(numer, cls ): return numer
		if isinstance(numer, frac): return cls.from_integers(*numer.integers)

		self = super().__new__(cls)

		greatest_common_divisor = math.gcd(
			numer,
			denom,
		)

		self.numer = numer // greatest_common_divisor
		self.denom = denom // greatest_common_divisor

		return self

	def __repr__(self) -> str:
		return repr(float(self))

	def __hash__(self) -> int:
		return hash(self.integers)

	def __bool__(self) -> bool:
		_, b = self.integers

		return bool(b)

	def __float__(self) -> float:
		return self.numer / self.denom if self.denom else math.inf

	def __le__(self, other: frac, /) -> bool: a, b = self.integers; c, d = other.integers; return a * d >= c * b
	def __ge__(self, other: frac, /) -> bool: a, b = self.integers; c, d = other.integers; return a * d <= c * b


	@classmethod
	def from_integers(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		return cls(numer, denom)

	@property
	def integers(self) -> pair[int]:
		return self.numer, self.denom

	def isdisjoint(self, other: frac) -> bool:
		return not (self & other)


class dist(frac):

	def __new__(cls,
		numer: int | frac = 0,
		denom: int        = 1, /
	) -> typing.Self:
		if not (numer or denom): numer = 1

		self = super().__new__(cls, numer, denom)

		if self.numer < 0 or self.denom < 0:
			raise ValueError(f"{self.numer} < 0 or {self.denom} < 0")

		return self

	def __add__(self, other: frac) -> typing.Self:
		cls, other = type(self), dist(other)

		return cls(
			other.numer * self.denom + self.numer * other.denom,
			              self.denom              * other.denom,
		)

	def __mul__(self, times: int) -> typing.Self:
		cls = type(self)

		return cls(
			self.numer * times,
			self.denom,
		)

	def __and__(self, other: frac) -> typing.Self:
		cls = type(self)

		return cls(prob(self) & prob(other))

	def __invert__(self) -> typing.Self:
		cls = type(self)

		return cls(
			self.denom,
			self.numer,
		)


class prob(frac):

	def __new__(cls,
		numer: int | frac = 0,
		denom: int        = 1, /
	) -> typing.Self:
		if not (numer or denom): denom = 1

		self = super().__new__(cls, numer, denom)

		if not 0 <= self.numer <= self.denom:
			raise ValueError(f"not 0 <= {self.numer} <= {self.denom}")

		return self

	def __add__(self, other: frac) -> typing.Self: cls = type(self); return cls(dist(self) + dist(other))
	def __mul__(self, times: int ) -> typing.Self: cls = type(self); return cls(dist(self) *      times )

	def __and__(self, other: frac) -> typing.Self:
		cls, other = type(self), prob(other)

		return cls(
			self.numer * other.numer,
			self.denom * other.denom,
		)

	def __invert__(self) -> typing.Self:
		cls = type(self)

		return cls(
			self.denom - self.numer,
			self.denom             ,
		)

	@classmethod
	def from_integers(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		return cls(
			denom,
			denom + numer,
		)

	@property
	def integers(self) -> pair[int]:
		return (
			self.denom - self.numer,
			self.numer,
		)
