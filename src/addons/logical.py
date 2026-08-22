from __future__ import annotations


import math
import typing


type pair[T] = tuple[T, T]


class frac:

	numer: int
	denom: int

	def __new__(cls,
		numer: int | frac = 0,
		denom: int        = 1, /
	) -> typing.Self:
		if isinstance(numer, cls ): return numer
		if isinstance(numer, frac): return cls.from_integer_ratio(*numer.integer_ratio)

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

	def __float__(self) -> float:
		return self.numer / self.denom if self.denom else math.inf

	def     __add__(self, other: frac) -> typing.Self: cls = type(self); return cls(dist(self) + dist(other))
	def     __mul__(self, other: frac) -> typing.Self: cls = type(self); return cls(dist(self) * dist(other))
	def      __or__(self, other: frac) -> typing.Self: cls = type(self); return cls(prob(self) | prob(other))
	def     __and__(self, other: frac) -> typing.Self: cls = type(self); return cls(prob(self) & prob(other))
	def     __sub__(self, other: frac) -> typing.Self: cls = type(self); return cls(prob(self) - prob(other))
	def     __xor__(self, other: frac) -> typing.Self: cls = type(self); return cls(prob(self) ^ prob(other))
	def __truediv__(self, other: frac) -> typing.Self: cls = type(self); return cls(dist(self) / dist(other))

	def __invert__(self) -> typing.Self:
		cls = type(self)

		return cls(~prob(self))

	@classmethod
	def from_integer_ratio(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		return cls(numer, denom)

	@property
	def integer_ratio(self) -> pair[int]:
		return self.numer, self.denom


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

	def __mul__(self, other: frac) -> typing.Self:
		cls, other = type(self), dist(other)

		return cls(
			self.numer * other.numer,
			self.denom * other.denom,
		)

	def __truediv__(self, other: frac) -> typing.Self:
		cls, other = type(self), dist(other)

		return cls(
			self.numer * other.denom,
			self.denom * other.numer,
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

	def __and__(self, other: frac) -> typing.Self:
		cls, other = type(self), prob(other)

		return cls(
			self.numer * other.numer,
			self.denom * other.denom,
		)

	def __or__(self, other: frac) -> typing.Self:
		return ~(~self & ~other)

	def __sub__(self, other: frac) -> typing.Self:
		return self & ~other

	def __xor__(self, other: frac) -> typing.Self:
		return (self | other) - (self & other)

	def __invert__(self) -> typing.Self:
		cls = type(self)

		return cls(
			self.denom - self.numer,
			self.denom             ,
		)

	@classmethod
	def from_integer_ratio(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		return cls(
			denom,
			denom + numer,
		)

	@property
	def integer_ratio(self) -> pair[int]:
		return (
			self.denom - self.numer,
			self.numer,
		)
