from __future__ import annotations


import math
import typing


class Int:

	def __init__(self, value: typing.Self | int):
		if (value := int(value)) < 0:
			raise ValueError(f"{self.__class__.__name__}.value must be non-negative")

		self._ = value

	def __hash__ (self) -> int  : return hash (self._)
	def __repr__ (self) -> str  : return repr (self._)
	def __str__  (self) -> str  : return str  (self._)
	def __bool__ (self) -> bool : return bool (self._)
	def __int__  (self) -> int  : return int  (self._)
	def __float__(self) -> float: return float(self._)

	def __add__(self, other: typing.Self) -> typing.Self: return self.operation(other, operation = int.__add__)
	def __mul__(self, other: typing.Self) -> typing.Self: return self.operation(other, operation = int.__mul__)

	def __pos__(self) -> typing.Self: return self.operation(operation = int.__pos__)
	def __abs__(self) -> typing.Self: return self.operation(operation = int.__abs__)

	def __eq__(self, other: object) -> bool: return self.comparison(other, int.__eq__)
	def __le__(self, other: typing.Self) -> bool: return self.comparison(other, int.__le__)
	def __ge__(self, other: typing.Self) -> bool: return self.comparison(other, int.__ge__)
	def __lt__(self, other: typing.Self) -> bool: return self.comparison(other, int.__lt__)
	def __gt__(self, other: typing.Self) -> bool: return self.comparison(other, int.__gt__)

	@classmethod
	def cast(cls, value: typing.Self | int) -> typing.Self:
		return value if type(value) is cls else cls(value)

	@classmethod
	def zero(cls) -> typing.Self:
		return cls(0)

	@classmethod
	def unit(cls) -> typing.Self:
		return cls(1)

	@classmethod
	def sum(cls, values: typing.Iterable[typing.Self]) -> typing.Self:
		return sum(values,
			start = cls.zero(),
		)

	@classmethod
	def prod(cls, values: typing.Iterable[typing.Self]) -> typing.Self:
		return math.prod(values,
			start = cls.unit(),
		)

	@typing.overload
	def operation(self, /, *, operation: typing.Callable[[int], int]) -> typing.Self: ...

	@typing.overload
	def operation(self, other: typing.Self, /, *, operation: typing.Callable[[int, int], int]) -> typing.Self: ...

	def operation(self, other: typing.Self | None = None, /, *, operation: typing.Callable[..., int]) -> typing.Self:
		if other is None:
			return self.cast(operation(self._))

		if type(other) is not type(self):
			return NotImplemented

		return self.cast(operation(self._, other._))

	def comparison(self, other: object, comparison: typing.Callable[[int, int], bool]) -> bool:
		if type(other) is not type(self):
			return NotImplemented

		other = typing.cast(typing.Self, other)
		return comparison(self._, other._)


class Float:

	def __init__(self, value: typing.Self | float):
		if (value := float(value)) < 0:
			raise ValueError(f"{self.__class__.__name__}.value must be non-negative")

		self._ = value

	def __hash__ (self) -> int  : return hash (self._)
	def __repr__ (self) -> str  : return repr (self._)
	def __str__  (self) -> str  : return str  (self._)
	def __bool__ (self) -> bool : return bool (self._)
	def __int__  (self) -> int  : return int  (self._)
	def __float__(self) -> float: return float(self._)

	def __add__(self, other: typing.Self) -> typing.Self: return self.operation(other, operation = float.__add__)
	def __mul__(self, other: typing.Self) -> typing.Self: return self.operation(other, operation = float.__mul__)

	def __pos__(self) -> typing.Self: return self.operation(operation = float.__pos__)
	def __abs__(self) -> typing.Self: return self.operation(operation = float.__abs__)

	def __eq__(self, other: object) -> bool: return self.comparison(other, float.__eq__)
	def __le__(self, other: typing.Self) -> bool: return self.comparison(other, float.__le__)
	def __ge__(self, other: typing.Self) -> bool: return self.comparison(other, float.__ge__)
	def __lt__(self, other: typing.Self) -> bool: return self.comparison(other, float.__lt__)
	def __gt__(self, other: typing.Self) -> bool: return self.comparison(other, float.__gt__)

	@classmethod
	def cast(cls, value: typing.Self | float) -> typing.Self:
		return value if type(value) is cls else cls(value)

	@classmethod
	def zero(cls) -> typing.Self:
		return cls(0)

	@classmethod
	def unit(cls) -> typing.Self:
		return cls(1)

	@classmethod
	def nan(cls) -> typing.Self:
		return cls(math.nan)

	@classmethod
	def inf(cls) -> typing.Self:
		return cls(math.inf)

	@classmethod
	def sum(cls, values: typing.Iterable[typing.Self]) -> typing.Self:
		return sum(values,
			start = cls.zero(),
		)

	@classmethod
	def prod(cls, values: typing.Iterable[typing.Self]) -> typing.Self:
		return math.prod(values,
			start = cls.unit(),
		)

	@typing.overload
	def operation(self, /, *, operation: typing.Callable[[float], float]) -> typing.Self: ...

	@typing.overload
	def operation(self, other: typing.Self, /, *, operation: typing.Callable[[float, float], float]) -> typing.Self: ...

	def operation(self, other: typing.Self | None = None, /, *, operation: typing.Callable[..., float]) -> typing.Self:
		if other is None:
			return self.cast(operation(self._))

		if type(other) is not type(self):
			return NotImplemented

		return self.cast(operation(self._, other._))

	def comparison(self, other: object, comparison: typing.Callable[[float, float], bool]) -> bool:
		if type(other) is not type(self):
			return NotImplemented

		other = typing.cast(typing.Self, other)
		return comparison(self._, other._)
