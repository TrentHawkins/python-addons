from __future__ import annotations


import math
import operator
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

	def __add__(self, other: typing.Self, /) -> typing.Self: return self.operator(other, operator = operator.add)
	def __mul__(self, other: typing.Self, /) -> typing.Self: return self.operator(other, operator = operator.mul)

	def __pos__(self) -> typing.Self: return self.operator(operator = operator.pos)
	def __abs__(self) -> typing.Self: return self.operator(operator = operator.abs)

	def __eq__(self, other: object     , /) -> bool: return self.relation(other, relation = operator.eq)
	def __le__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.le)
	def __ge__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.ge)
	def __lt__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.lt)
	def __gt__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.gt)

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
	def operator(self, /, *, operator: typing.Callable[[int], int]) -> typing.Self: ...

	@typing.overload
	def operator(self, other: typing.Self, /, *, operator: typing.Callable[[int, int], int]) -> typing.Self: ...

	def operator(self, *others: typing.Self, operator: typing.Callable[..., int]) -> typing.Self:
		if not others:
			return self.cast(operator(self._))

		other, *_ = others

		if type(other) is not type(self):
			return NotImplemented

		return self.cast(operator(self._, other._))

	def relation(self, other: object, relation: typing.Callable[[int, int], bool]) -> bool:
		if type(other) is not type(self):
			return NotImplemented

		return relation(self._, other._)


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

	def __add__(self, other: typing.Self, /) -> typing.Self: return self.operator(other, operator = operator.add)
	def __mul__(self, other: typing.Self, /) -> typing.Self: return self.operator(other, operator = operator.mul)

	def __pos__(self) -> typing.Self: return self.operator(operator = operator.pos)
	def __abs__(self) -> typing.Self: return self.operator(operator = operator.abs)

	def __eq__(self, other: object     , /) -> bool: return self.relation(other, relation = operator.eq)
	def __le__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.le)
	def __ge__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.ge)
	def __lt__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.lt)
	def __gt__(self, other: typing.Self, /) -> bool: return self.relation(other, relation = operator.gt)

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
	def operator(self, /, *, operator: typing.Callable[[float], float]) -> typing.Self: ...

	@typing.overload
	def operator(self, other: typing.Self, /, *, operator: typing.Callable[[float, float], float]) -> typing.Self: ...

	def operator(self, *others: typing.Self, operator: typing.Callable[..., float]) -> typing.Self:
		if not others:
			return self.cast(operator(self._))

		other, *_ = others

		if type(other) is not type(self):
			return NotImplemented

		return self.cast(operator(self._, other._))

	def relation(self, other: object, relation: typing.Callable[[float, float], bool]) -> bool:
		if type(other) is not type(self):
			return NotImplemented

		return relation(self._, other._)
