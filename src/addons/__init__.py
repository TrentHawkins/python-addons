from __future__ import annotations


from math import gcd
from typing import Self


class scalar:

	__slots__ = (
		"numer",
		"denom",
	)

	numer: int
	denom: int


	def __new__(cls,
		numer: int = 0,
		denom: int = 1, /
	) -> Self:
		if numer < 0: raise ValueError
		if denom < 0: raise ValueError

		if not denom:
			numer = 1

		norm = gcd(
			numer,
			denom,
		)

		self = super().__new__(cls)

		super(scalar, self).__setattr__("numer", numer // norm)
		super(scalar, self).__setattr__("denom", denom // norm)

		return self

	def __setattr__(self, name: str, value: int) -> None: raise AttributeError
	def __delattr__(self, name: str            ) -> None: raise AttributeError

	def __float__(self) -> float:
		return self.denom / (self.numer + self.denom)

	def __add__(self, value: scalar) -> Self:
		cls = type(self)

		return cls(
			self.numer * value.denom + value.numer * self.denom,
			self.denom * value.denom
		)

	def __matmul__(self, value: scalar) -> Self:
		return ~(~self + ~value)

	def __mul__(self, value: scalar) -> Self:
		cls = type(self)

		return cls(
			self.numer * value.numer,
			self.denom * value.denom,
		)

	def __and__(self, value: scalar) -> Self: return (self + value) + (self * value)
	def  __or__(self, value: scalar) -> Self: return (self @ value) @ (self * value)
	def __xor__(self, value: scalar) -> Self: return (self @ value) - (self & value)
	def __sub__(self, value: scalar) -> Self:
		return self & ~value

	def __invert__(self) -> Self:
		cls = type(self)

		return cls(
			self.denom,
			self.numer,
		)
