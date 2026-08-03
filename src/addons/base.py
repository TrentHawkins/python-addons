from __future__ import annotations


import math
import operator
import typing


class Numeric(typing.Protocol):

	def __hash__ (self) -> int  : ...
	def __bool__ (self) -> bool : ...
	def __int__  (self) -> int  : ...
	def __float__(self) -> float: ...

	def __add__(self, other: typing.Self, /) -> typing.Self: ...
	def __mul__(self, other: typing.Self, /) -> typing.Self: ...

	def __pos__(self) -> typing.Self: ...
	def __abs__(self) -> typing.Self: ...

	def __eq__(self, other: object     , /) -> bool: ...
	def __le__(self, other: typing.Self, /) -> bool: ...
	def __ge__(self, other: typing.Self, /) -> bool: ...
	def __lt__(self, other: typing.Self, /) -> bool: ...
	def __gt__(self, other: typing.Self, /) -> bool: ...


class Number[T: Numeric]:

	value_type: typing.Callable[[typing.Any], T]

	def __init_subclass__(cls, *args,
		value_type: type[T] | None = None,
	**kwargs):
		super().__init_subclass__(*args, **kwargs)

		if value_type is not None: cls.value_type = value_type
		elif not hasattr(cls, "value_type"): raise TypeError(f"{cls.__name__} must define a `value_type` attribute")

	def __init__(self, value: typing.Self | T):
		if (value := self.value_type(value._ if isinstance(value, Number) else value)) < self.value_type(0):
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
	def zero(cls) -> typing.Self:
		return cls(cls.value_type(0))

	@classmethod
	def unit(cls) -> typing.Self:
		return cls(cls.value_type(1))

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
	def operator(self, /, *, operator: typing.Callable[[T], T]) -> typing.Self: ...

	@typing.overload
	def operator(self, other: typing.Self, /, *, operator: typing.Callable[[T, T], T]) -> typing.Self: ...

	def operator(self, *others: typing.Self, operator: typing.Callable[..., T]) -> typing.Self:
		if not others:
			return type(self)(operator(self._))

		other, *_ = others

		if type(other) is not type(self):
			return NotImplemented

		return type(self)(operator(self._, other._))

	def relation(self, other: object, relation: typing.Callable[[T, T], bool]) -> bool:
		if type(other) is not type(self):
			return NotImplemented

		return relation(self._, other._)


class Int(Number[int]):

	value_type = int


class Float(Number[float]):

	value_type = float

	@classmethod
	def nan(cls) -> typing.Self:
		return cls(math.nan)

	@classmethod
	def inf(cls) -> typing.Self:
		return cls(math.inf)
