from __future__ import annotations


import abc
import functools
import math
import typing


type pair[T] = tuple[T, T]


class Invertible(abc.ABC):

	@abc.abstractmethod
	def __invert__(self) -> typing.Self:
		...


class Operable(Invertible):

	def  __or__(self, other: Operable, /) -> typing.Self: return ~(~self & ~other)
	def __and__(self, other: Operable, /) -> typing.Self: return ~(~self | ~other)
	def __sub__(self, other: Operable, /) -> typing.Self: return    self & ~other
	def __xor__(self, other: Operable, /) -> typing.Self:
		return (self | other) - (self & other)
	#	return (self - other) | (other - self)

	def  __ror__(self, other: Operable, /) -> typing.Self: return self | other
	def __rand__(self, other: Operable, /) -> typing.Self: return self & other
	def __rxor__(self, other: Operable, /) -> typing.Self: return self ^ other

	def  __ior__(self, other: Operable, /) -> typing.Self: return self | other
	def __iand__(self, other: Operable, /) -> typing.Self: return self & other
	def __isub__(self, other: Operable, /) -> typing.Self: return self - other
	def __ixor__(self, other: Operable, /) -> typing.Self: return self ^ other

	@typing.final
	def union(self, *others: Operable) -> typing.Self:
		return functools.reduce(self.__class__.__or__, others, self)

	@typing.final
	def intersection(self, *others: Operable) -> typing.Self:
		return functools.reduce(self.__class__.__and__, others, self)

	@typing.final
	def difference(self, *others: Operable) -> typing.Self:
		return functools.reduce(self.__class__.__sub__, others, self)

	@typing.final
	def symmetric_difference(self, other: Operable, /) -> typing.Self:
		return self ^ other

	@typing.final
	@classmethod
	def any(cls, others: typing.Iterable[Operable], /) -> typing.Self:
		return cls.union(*others)  # pyright: ignore[reportArgumentType]

	@typing.final
	@classmethod
	def all(cls, others: typing.Iterable[Operable], /) -> typing.Self:
		return cls.intersection(*others)  # pyright: ignore[reportArgumentType]

class Additive(abc.ABC):

	@abc.abstractmethod
	def __add__(self, other: Additive, /) -> typing.Self:
		...

	@abc.abstractmethod
	def __mul__(self, times: int, /) -> typing.Self:
		...

	def __radd__(self, other: Additive, /) -> typing.Self: return self + other
	def __rmul__(self, other: int     , /) -> typing.Self: return self * other

	def __iadd__(self, other: Additive, /) -> typing.Self: return self + other
	def __imul__(self, other: int     , /) -> typing.Self: return self * other

	@typing.final
	@classmethod
	def sum(cls, others: typing.Iterable[Additive], /) -> typing.Self:
		return sum(others,  #  pyright: ignore[reportArgumentType, reportCallIssue]
		#	start = cls()  #  pyright: ignore[reportReturnType]
		)
	#	return functools.reduce(cls.__add__, others, cls())

class Order(abc.ABC):

	@abc.abstractmethod
	def __le__(self, other: Order, /) -> bool:
		...

	@abc.abstractmethod
	def __ge__(self, other: Order, /) -> bool:
		...

	def __ne__(self, other: Order, /) -> bool:
		return not self == other

	def __eq__(self, other: Order, /) -> bool: return self <= other and self >= other
	def __lt__(self, other: Order, /) -> bool: return self <= other and self != other
	def __gt__(self, other: Order, /) -> bool: return self >= other and self != other

	@typing.final
	def issubset  (self, other: Order, /) -> bool:
		return self <= other

	@typing.final
	def issuperset(self, other: Order, /) -> bool:
		return self >= other


class Partial(Order):

#	Without trichotomy `__le__` is primitive; its converse is only the reflection:
	def __le__(self, other: Order, /) -> bool: return other >= self
	def __ge__(self, other: Order, /) -> bool: return other <= self


class Total(Order):

#	Trichotomy derives each relation from the negation of its converse:
	def __le__(self, other: Order, /) -> bool: return not self > other
	def __ge__(self, other: Order, /) -> bool: return not self < other

	def __lt__(self, other: Order, /) -> bool: return not self >= other
	def __gt__(self, other: Order, /) -> bool: return not self <= other


class Separable(Operable, abc.ABC):

	@abc.abstractmethod
	def __bool__(self) -> bool:
		...

	@typing.final
	def isdisjoint(self, other: Operable) -> bool:
		return not (self & other)


class Boolean(Separable, Additive, abc.ABC):

	@classmethod
	@abc.abstractmethod
	def minimum(cls) -> typing.Self:
		...

	@classmethod
	@abc.abstractmethod
	def maximum(cls) -> typing.Self:
		...


class Frac(Boolean, Total, abc.ABC):

	numer: int
	denom: int

	def __new__(cls,
		numer: int | Frac = 0,
		denom: int        = 1, /
	) -> typing.Self:
		if isinstance(numer, cls):
			return numer

		if isinstance(numer, Frac):
			return cls.encode(*numer.decode())

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
		return hash(self.decode())

	def __bool__(self) -> bool:
		_, b = self.decode()

		return bool(b)

	def __float__(self) -> float:
		return self.numer / self.denom if self.denom else math.inf

	def __add__(self, other: int | Frac, /) -> typing.Self: cls = type(self); return cls(Dist(self) + Dist(other))
	def __mul__(self, times: int       , /) -> typing.Self: cls = type(self); return cls(Dist(self) *      times )
	def __and__(self, other: int | Frac, /) -> typing.Self: cls = type(self); return cls(Prob(self) & Prob(other))

	def __invert__(self) -> typing.Self: cls = type(self); a, b = self.decode(); return cls.encode(b, a)

	def __le__(self, other: Frac, /) -> bool: a, b = self.decode(); c, d = other.decode(); return a * d >= c * b
	def __ge__(self, other: Frac, /) -> bool: a, b = self.decode(); c, d = other.decode(); return a * d <= c * b


	@classmethod
	@abc.abstractmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		...

#	The distinguished values are just canonical readings, so `encode` already knows them:
	@classmethod
	def minimum(cls) -> typing.Self:
		return cls.encode(0, 1)

	@classmethod
	def midimum(cls) -> typing.Self:
		return cls.encode(1, 1)

	@classmethod
	def maximum(cls) -> typing.Self:
		return cls.encode(1, 0)

	@typing.final
	@property
	def decoded(self) -> pair[int]:
		return self.decode()

	@abc.abstractmethod
	def decode(self) -> pair[int]:
		...


class Dist(Frac):

	def __new__(cls,
		numer: int | Frac = 0,
		denom: int        = 1, /
	) -> typing.Self:
		if not (numer or denom): numer = 1

		self = super().__new__(cls, numer, denom)

		if self.numer < 0 or self.denom < 0:
			raise ValueError(f"{self.numer} < 0 or {self.denom} < 0")

		return self

	def __add__(self, other: int | Frac) -> typing.Self:
		cls, other = type(self), Dist(other)

		return cls(
			other.numer * self.denom + self.numer * other.denom,
			              self.denom              * other.denom,
		)

	def __mul__(self, times: int) -> typing.Self:
		cls = type(self)

		return cls(
			self.numer * times,
			self.denom,
		) if times else cls()

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		return cls(numer, denom)

	def decode(self) -> pair[int]:
		return self.numer, self.denom


class Prob(Frac):

	def __new__(cls,
		numer: int | Frac = 1,
		denom: int        = 1, /
	) -> typing.Self:
		if not (numer or denom): denom = 1

		self = super().__new__(cls, numer, denom)

		if not 0 <= self.numer <= self.denom:
			raise ValueError(f"not 0 <= {self.numer} <= {self.denom}")

		return self

	def __and__(self, other: int | Frac) -> typing.Self:
		cls, other = type(self), Prob(other)

		return cls(
			self.numer * other.numer,
			self.denom * other.denom,
		)

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> typing.Self:
		return cls(
			denom,
			denom + numer,
		)

	def decode(self) -> pair[int]:
		return (
			self.denom - self.numer,
			self.numer,
		)


class Bool(Boolean, Total):

	def __init__(self, _: object = False, /):
		self._ = bool(_)

	def __repr__(self) -> str: return repr(bool(self))
	def __hash__(self) -> int: return hash(bool(self))

	def __bool__(self) -> bool:
		return self._

	def __add__(self, other: object, /) -> typing.Self: cls = type(self); return cls(self    and other)
	def __mul__(self, times: int   , /) -> typing.Self: cls = type(self); return cls(self or not times)
	def __and__(self, other: object, /) -> typing.Self: cls = type(self); return cls(self    and other)

	def __invert__(self, /) -> typing.Self:
		cls = type(self)

		return cls(not self)

	@classmethod
	def minimum(cls) -> typing.Self:
		return cls(True)

	@classmethod
	def maximum(cls) -> typing.Self:
		return cls(False)

	def __ne__(self, other: object, /) -> bool: return bool(self ) is not bool(other)
	def __le__(self, other: object, /) -> bool: return bool(other) or not bool(self )
	def __ge__(self, other: object, /) -> bool: return bool(self ) or not bool(other)


class Set[K: typing.Hashable, V: Boolean = Bool](Boolean, Partial, dict[K , V]):

	truth: type[V]
	complement: bool = False

	def __init_subclass__(cls, *args,
		truth: type[V] | None = None,
	**kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)

		if truth is not None:
			cls.truth = truth

	def __init__(self, iterable: typing.Iterable[K] | typing.Mapping[K, V] = (), /, *,
		complement: bool | None = None,
	):
		if complement is None:
			complement = iterable.complement if isinstance(iterable, Set) else False

		self.complement = complement

		super().__init__(
			iterable.items() if isinstance(iterable, typing.Mapping) else ((key, self.covered)
			for key in iterable),
		)

	def __missing__(self, _: K, /) -> V:
		return self.default

	@property
	def covered(self) -> V:
		return type(self).truth.maximum() if self.complement else type(self).truth.minimum()

	@property
	def default(self) -> V:
		return type(self).truth.minimum() if self.complement else type(self).truth.maximum()


type IndexSet[I: typing.Hashable] = Set[I, Bool]
type FuzzySet[I: typing.Hashable] = Set[I, Prob]

type UnweightedGraph[I: typing.Hashable] = Set[I, Set[I, Bool]]
type           Graph[I: typing.Hashable] = Set[I, Set[I, Prob]]
