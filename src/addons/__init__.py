from __future__ import annotations


from math import gcd
from typing import Self


class Dist:

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

		super(Dist, self).__setattr__("numer", numer // norm)
		super(Dist, self).__setattr__("denom", denom // norm)

		return self

	def __setattr__(self, name: str, value: int) -> None: raise AttributeError
	def __delattr__(self, name: str            ) -> None: raise AttributeError

	def __float__(self) -> float:
		return self.denom / (self.numer + self.denom)

	def __hash__(self) -> int:
		return hash((self.numer, self.denom))

	def __add__(self, value: Dist) -> Self:
		cls = type(self)

		return cls(
			self.numer * value.denom + value.numer * self.denom,
			self.denom * value.denom,
		)

	def __matmul__(self, value: Dist) -> Self:
		return ~(~self + ~value)

	def __and__(self, value: Dist) -> Self:
		if not isinstance(value, Dist):
			return NotImplemented

		cls = type(self)

		return cls(
			self.numer * value.numer + self.numer * value.denom + self.denom * value.numer,
			self.denom * value.denom,
		)

	def  __or__ (self, value: Dist) -> Self: return ~(~self & ~value)
	def  __sub__(self, value: Dist) -> Self: return    self & ~value

	def  __xor__(self, value: Dist) -> Self: return (self @ value) - (self & value)
#	def  __xor__(self, value: scalar) -> Self: return (self | value) - (self & value)
#	def  __xor__(self, value: scalar) -> Self: return (self - value) | (value - self)

	def __ror__ (self, value: Dist) -> Self: return NotImplemented
	def __rand__(self, value: Dist) -> Self: return NotImplemented
	def __rxor__(self, value: Dist) -> Self: return NotImplemented

	def __invert__(self) -> Self:
		cls = type(self)

		return cls(
			self.denom,
			self.numer,
		)

	def __le__(self, value: Dist) -> bool: return self.numer * value.denom <= value.numer * self.denom
	def __ge__(self, value: Dist) -> bool: return self.numer * value.denom >= value.numer * self.denom
	def __eq__(self, value: Dist) -> bool:
		return self <= value and self >= value

	def __ne__(self, value: Dist) -> bool: return                   not self == value
	def __lt__(self, value: Dist) -> bool: return self <= value and not self == value
	def __gt__(self, value: Dist) -> bool: return self >= value and not self == value


	@classmethod
	def min(cls) -> Self:
		return cls(
			0,
			1,
		)

	@classmethod
	def max(cls) -> Self:
		return cls(
			1,
			0,
		)


class Bool(Dist):

	__slots__ = ()

	def __new__(cls,
		numer: int = 0,
		denom: int = 1, /
	) -> Self:
		if numer and denom:
			raise ValueError

		return super().__new__(cls,
			numer,
			denom,
		)

	def __bool__(self) -> bool:
		return bool(self.denom)


class Prob(Dist):

	__slots__ = ()


	def __mul__(self, value: Dist) -> Self:
		cls = type(self)

		numer = self.numer * value.numer
		denom = self.denom * value.denom

		return cls.mid() if numer == denom == 0 else cls(
			numer,
			denom,
		)


	@classmethod
	def mid(cls) -> Self:
		return cls(
			1,
			1,
		)
