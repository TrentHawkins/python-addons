from __future__ import annotations


from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterable, Iterator, Mapping
from functools import reduce
from math import gcd, inf
from typing import Self, final, cast


type pair[T] = tuple[T, T]


class Bounded(ABC):

	@classmethod
	@abstractmethod
	def minimum(cls) -> Self:
		...

	@classmethod
	@abstractmethod
	def maximum(cls) -> Self:
		...


class Invertible(ABC):

	@abstractmethod
	def __invert__(self) -> Self:
		...


class Operable(Invertible, Bounded):

	def  __or__(self, other: Operable, /) -> Self: return ~(~self & ~other)
	def __and__(self, other: Operable, /) -> Self: return ~(~self | ~other)
	def __sub__(self, other: Operable, /) -> Self: return    self & ~other
	def __xor__(self, other: Operable, /) -> Self:
		return (self | other) - (self & other)
	#	return (self - other) | (other - self)

	def  __ror__(self, other: Operable, /) -> Self: return self | other
	def __rand__(self, other: Operable, /) -> Self: return self & other
	def __rxor__(self, other: Operable, /) -> Self: return self ^ other

	@final
	def union(self, *others: Operable) -> Self:
		return reduce(self.__class__.__or__, others, self)

	@final
	def intersection(self, *others: Operable) -> Self:
		return reduce(self.__class__.__and__, others, self)

	@final
	def difference(self, *others: Operable) -> Self:
		return reduce(self.__class__.__sub__, others, self)

	@final
	def symmetric_difference(self, other: Operable, /) -> Self:
		return self ^ other

	@final
	@classmethod
	def any(cls, others: Iterable[Operable], /) -> Self:
		return cls.maximum().union(*others)
	#	return reduce(cls.__or__, others, cls.maximum())

	@final
	@classmethod
	def all(cls, others: Iterable[Operable], /) -> Self:
		return cls.minimum().intersection(*others)
	#	return reduce(cls.__and__, others, cls.minimum())


class Additive(Bounded):

	@abstractmethod
	def __add__(self, other: Additive, /) -> Self:
		...

	@abstractmethod
	def __mul__(self, times: int, /) -> Self:
		...

	def __radd__(self, other: Additive, /) -> Self: return self + other
	def __rmul__(self, other: int     , /) -> Self: return self * other

	@final
	@classmethod
	def sum(cls, others: Iterable[Additive], /) -> Self:
		return sum(others, cls.minimum())  # pyright: ignore[reportReturnType]
	#	return reduce(cls.__add__, others, cls.minimum())


class Order(ABC):

	@abstractmethod
	def __le__(self, other: Order, /) -> bool:
		...

	@abstractmethod
	def __ge__(self, other: Order, /) -> bool:
		...

	def __ne__(self, other: Order, /) -> bool:
		return not self == other

	def __eq__(self, other: Order, /) -> bool: return self <= other and self >= other
	def __lt__(self, other: Order, /) -> bool: return self <= other and self != other
	def __gt__(self, other: Order, /) -> bool: return self >= other and self != other

	@final
	def issubset  (self, other: Order, /) -> bool:
		return self <= other

	@final
	def issuperset(self, other: Order, /) -> bool:
		return self >= other


class Partial(Order):

	def __le__(self, other: Order, /) -> bool: return other >= self
	def __ge__(self, other: Order, /) -> bool: return other <= self


class Total(Order):

	def __le__(self, other: Order, /) -> bool: return not self > other
	def __ge__(self, other: Order, /) -> bool: return not self < other

	def __lt__(self, other: Order, /) -> bool: return not self >= other
	def __gt__(self, other: Order, /) -> bool: return not self <= other


class Separable(Operable, ABC):

	@abstractmethod
	def __bool__(self) -> bool:
		...

	@final
	def isdisjoint(self, other: Operable) -> bool:
		return not (self & other)


class Boolean[T: Separable](Separable, Additive, Order, ABC):

	@abstractmethod
	def __abs__(self) -> T:
		...


class Frac(Boolean, Total, ABC):

	numer: int
	denom: int

	def __new__(cls,
		numer: int | Frac = 0,
		denom: int        = 1, /
	) -> Self:
		if isinstance(numer, cls):
			return numer

		if isinstance(numer, Frac):
			return cls.encode(*numer.decode())

		self = super().__new__(cls)

		greatest_common_divisor = gcd(
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
		return self.numer / self.denom if self.denom else inf

	def __add__(self, other: int | Frac, /) -> Self: cls = type(self); return cls(Dist(self) + Dist(other))
	def __mul__(self, times: int       , /) -> Self: cls = type(self); return cls(Dist(self) *      times )
	def __and__(self, other: int | Frac, /) -> Self: cls = type(self); return cls(Prob(self) & Prob(other))

	def __invert__(self) -> Self: cls = type(self); a, b = self.decode(); return cls.encode(b, a)

	def __abs__(self) -> Self: cls = type(self); return cls(self)

	def __le__(self, other: Frac, /) -> bool: a, b = self.decode(); c, d = other.decode(); return a * d >= c * b
	def __ge__(self, other: Frac, /) -> bool: a, b = self.decode(); c, d = other.decode(); return a * d <= c * b


	@classmethod
	@abstractmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
		...

	@classmethod
	def minimum(cls) -> Self:
		return cls.encode(0, 1)

	@classmethod
	def midimum(cls) -> Self:
		return cls.encode(1, 1)

	@classmethod
	def maximum(cls) -> Self:
		return cls.encode(1, 0)

	@final
	@property
	def decoded(self) -> pair[int]:
		return self.decode()

	@abstractmethod
	def decode(self) -> pair[int]:
		...


class Dist(Frac):

	def __new__(cls,
		numer: int | Frac = 0,
		denom: int        = 1, /
	) -> Self:
		if not (numer or denom): numer = 1

		self = super().__new__(cls, numer, denom)

		if self.numer < 0 or self.denom < 0:
			raise ValueError(f"{self.numer} < 0 or {self.denom} < 0")

		return self

	def __add__(self, other: int | Frac) -> Self:
		cls, other = type(self), Dist(other)

		return cls(
			other.numer * self.denom + self.numer * other.denom,
			              self.denom              * other.denom,
		)

	def __mul__(self, times: int) -> Self:
		cls = type(self)

		return cls(
			self.numer * times,
			self.denom,
		) if times else cls()

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
		return cls(numer, denom)

	def decode(self) -> pair[int]:
		return self.numer, self.denom


class Prob(Frac):

	def __new__(cls,
		numer: int | Frac = 1,
		denom: int        = 1, /
	) -> Self:
		if not (numer or denom): denom = 1

		self = super().__new__(cls, numer, denom)

		if not 0 <= self.numer <= self.denom:
			raise ValueError(f"not 0 <= {self.numer} <= {self.denom}")

		return self

	def __and__(self, other: int | Frac) -> Self:
		cls, other = type(self), Prob(other)

		return cls(
			self.numer * other.numer,
			self.denom * other.denom,
		)

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
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

	def __add__(self, other: object, /) -> Self: cls = type(self); return cls(self    and other)
	def __mul__(self, times: int   , /) -> Self: cls = type(self); return cls(self or not times)
	def __and__(self, other: object, /) -> Self: cls = type(self); return cls(self    and other)

	def __invert__(self, /) -> Self:
		cls = type(self)

		return cls(not self)

	def __abs__(self) -> Self:
		cls = type(self)

		return cls.minimum() if self else cls.maximum()

	@classmethod
	def minimum(cls) -> Self:
		return cls(True)

	@classmethod
	def maximum(cls) -> Self:
		return cls(False)

	def __ne__(self, other: object, /) -> bool: return bool(self ) is not bool(other)
	def __le__(self, other: object, /) -> bool: return bool(other) or not bool(self )
	def __ge__(self, other: object, /) -> bool: return bool(self ) or not bool(other)


class Set[K: Hashable, T: Boolean = Bool, V: Boolean = T](Boolean, Partial, dict[K , V]):

	truth: type[V]
	default: V

	def __init_subclass__(cls, *args,
		truth: type[V] | None = None,
	**kwargs):
		super().__init_subclass__(*args, **kwargs)

		if truth is not None:
			cls.truth = truth

	def __init__(self, iterable: Iterable[K] | Mapping[K, V] = (), /, *,
		complement: bool | None = None,
	):
		if complement is None:
			complement = iterable.complement if isinstance(iterable, Set) else False

		self.default = type(self).truth.minimum() if complement else type(self).truth.maximum()

		super().__init__()

		if not isinstance(iterable, Mapping):
			iterable = dict.fromkeys(iterable, ~self.default)

		for key, value in iterable.items():
			self[key] = value

	def __missing__(self, _: K, /) -> V:
		return self.default

	def __contains__(self, key: K, /) -> bool:
		return bool(self[key])

	def __iter__(self, /) -> Iterator[K]:
		cls = type(self)

		if self.complement:
			raise TypeError(f"cannot iterate an {cls.__name__} with implicit members")

		return (key for key, value in self.items() if value)

	def __bool__(self, /) -> bool:
		return self.complement or any(map(bool, self.values()))

	def __setitem__(self, key: K, value: object, /):
		cls = type(self)

		super().__setitem__(key, cls.truth(value))  # pyright: ignore[reportCallIssue]

	def __invert__(self) -> Self:
		cls = type(self)

		return cls({key: ~value for key, value in self.items()},
			complement = not self.complement,
		)

	def __abs__(self) -> T:
		measures = [abs(value if self.complement else ~value) for value in self.values()]

		if not measures:
			return abs(self.default)

		result = cast(T, sum(measures, abs(self.truth.minimum())))

		return result if self.complement else ~result

	def __add__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: self[key] + other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default + other.default),
		)

	def __mul__(self, times: int, /) -> Self:
		cls = type(self)

		return cls({key: self[key] * times for key in self.keys()},
			complement = bool(self.default * times),
		)

	def __and__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: self[key] & other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default & other.default),
		)

	def __or__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: self[key] | other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default | other.default),
		)

	def __sub__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: self[key] & ~other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default & ~other.default),
		)

	def __xor__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: self[key] ^ other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default ^ other.default),
		)

	def __ior__ (self, other: Iterable[K] | Mapping[K, V], /) -> Self: self.update                     (other); return self
	def __iand__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: self.intersection_update        (other); return self
	def __isub__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: self.difference_update          (other); return self
	def __ixor__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: self.symmetric_difference_update(other); return self

	def __le__(self, other: Iterable[K] | Mapping[K, V], /) -> bool:
		cls = type(self)
		other = cls(other)

		return all(self[key] <= other[key] for key in self.keys() | other.keys())

	def __ge__(self, other: Iterable[K] | Mapping[K, V], /) -> bool:
		cls = type(self)
		other = cls(other)

		return all(self[key] >= other[key] for key in self.keys() | other.keys())

	def __eq__(self, other: Iterable[K] | Mapping[K, V], /) -> bool:
		cls = type(self)
		other = cls(other)

		return all(self[key] == other[key] for key in self.keys() | other.keys())

	@classmethod
	def fromkeys(cls, iterable: Iterable[K], value: V | None = None, /) -> Self:
		return cls(iterable if value is None else dict.fromkeys(iterable, value))

	@classmethod
	def minimum(cls) -> Self:
		return cls(complement = True)

	@classmethod
	def maximum(cls) -> Self:
		return cls()

	@property
	def complement(self) -> bool:
		return bool(self.default)

	def get(self, key: K, default: V | None = None, /) -> V:
		return self[key] if default is None or key in self else default

	def setdefault(self, key: K, default: V | None = None, /) -> V:
		if key not in self: self[key] = ~self.default if default is None else default

		return self[key]
	def become(self, other: Self, /):
		items = dict(other)

		self.default = other.default

		dict.clear(self)
		dict.update(self, items)

	def update(self, *others: Iterable[K] | Mapping[K, V]):
		cls = type(self)

		self.become(self.union(*map(cls, others)))

	def intersection_update(self, *others: Iterable[K] | Mapping[K, V]):
		cls = type(self)

		self.become(self.intersection(*map(cls, others)))

	def difference_update(self, *others: Iterable[K] | Mapping[K, V]):
		cls = type(self)

		self.become(self.difference(*map(cls, others)))

	def symmetric_difference_update(self, other: Iterable[K] | Mapping[K, V], /):
		cls = type(self)

		self.become(self.symmetric_difference(cls(other)))


class IndexSet[I: Hashable](Set[I, Bool], truth = Bool): ...
class FuzzySet[I: Hashable](Set[I, Prob], truth = Prob): ...

class UnweightedGraph[I: Hashable](Set[I, IndexSet[I]], truth = IndexSet[I]): ...
class           Graph[I: Hashable](Set[I, FuzzySet[I]], truth = FuzzySet[I]): ...
