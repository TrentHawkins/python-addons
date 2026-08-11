"""
------------------------------------------------------------------------------------------------------------------------------------
L − ~
0 1 1
1 0 0
------------------------------------------------------------------------------------------------------------------------------------
L R + × ∧ ∨ − Δ ≠ > < = ≤ ≥
0 0 0 0 0 0 0 0 0 0 0 1 1 1
0 1 0 0 0 1 0 1 1 0 1 0 1 0
1 0 0 0 0 1 1 1 1 1 0 0 0 1
1 1 1 1 1 1 0 0 0 0 0 1 1 1
------------------------------------------------------------------------------------------------------------------------------------
"""



from __future__ import annotations


from math import inf, exp, log, isnan
from functools import reduce
from typing import (
	Hashable,
	Iterable,
	Iterator,
	KeysView,
	Mapping,
	Protocol,
	Self,
	SupportsAbs,
	TypeAlias,
)


number: TypeAlias = int | float

type pair[T_co: number] = tuple[
	T_co,
	T_co,
]


class Real(float):

	__slots__ = ()

	minimum: number = +inf
	midimum: number =  0.0
	maximum: number = -inf

	def __new__(cls, value: number, /) -> Self:
		value = getattr(value, cls.__name__.lower(), value)
		value = cls.maximum if isnan(value) else value

		self = super().__new__(cls, value)

		lower = min(cls.minimum, cls.maximum)
		upper = max(cls.minimum, cls.maximum)

		if not lower <= float(self) <= upper:
			raise ValueError(f"not {lower} <= {self} <= {upper} for {cls.__name__}")

		return self

	def     __add__(self, value: number, /) -> Self: cls = self.__class__; return cls(self.dist + cls(value).dist)
	def     __mul__(self, value: number, /) -> Self: cls = self.__class__; return cls(self.dist * cls(value).dist)
	def __truediv__(self, value: number, /) -> Self: cls = self.__class__; return cls(self.prob - cls(value).prob)
	def     __and__(self, value: number, /) -> Self: cls = self.__class__; return cls(self.prob * cls(value).prob)

#	def __pow__(self, value: numeric, mod: None = None, /) -> Self:
#		cls = self.__class__
#
#		return cls(super().__pow__(value, mod))

	def __or__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return ~(~self & ~value)

	def __sub__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return self & ~value

	def __xor__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return (self - value) | (value - self)
	#	return (self | value) - (value & self)

	def     __radd__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) + self
	def     __rsub__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) - self
	def     __rmul__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) * self
	def __rtruediv__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) / self
	def     __rand__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) & self
	def      __ror__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) | self
	def     __rxor__(self, value: number, /) -> Self: cls = self.__class__; return cls(value) ^ self

#	def __rpow__(self, value: numeric, mod: None = None, /) -> Self:
#		cls = self.__class__
#
#		return cls(value).__pow__(self, mod)

	def __neg__(self, /) -> Self: return ~self
	def __pos__(self, /) -> Self: return  self
	def	__abs__(self, /) -> Self: return  self

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(~self.prob)

	def __eq__(self, value: number, /) -> Prob: return ~(self != value)
	def __le__(self, value: number, /) -> Prob: return ~(self >  value)
	def __ge__(self, value: number, /) -> Prob: return ~(self <  value)

	def __ne__(self, value: number, /) -> Prob: cls = self.__class__; return self.prob ^ cls(value).prob
	def __lt__(self, value: number, /) -> Prob: cls = self.__class__; return cls(value).prob - self.prob
	def __gt__(self, value: number, /) -> Prob: cls = self.__class__; return self.prob - cls(value).prob

	@classmethod
	def range(cls, /) -> pair[number]:
		return (
			min(
				cls.minimum,
				cls.maximum,
			),
			max(
				cls.minimum,
				cls.maximum,
			),
		)

	@property
	def real(self, /) -> Real: return self
	@property
	def dist(self, /) -> Dist: return Dist(exp(-float(self)))
	@property
	def prob(self, /) -> Prob: return self.dist.prob
	@property
	def imag(self, /) -> Real:
		cls = self.__class__

		return cls(self.midimum).real

	def conjugate(self, /) -> Self:
		return self

	def union       (self, *values: number) -> Self: cls = self.__class__; return reduce(cls. __or__, values, self)
	def intersection(self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__and__, values, self)
	def difference  (self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__sub__, values, self)

	def symmetric_difference(self, value: number, /) -> Self:
		return self ^ value

	def issubset  (self, value: number, /) -> Prob: return self <= value
	def issuperset(self, value: number, /) -> Prob: return self >= value

	def isdisjoint(self, value: number, /) -> Self: cls = self.__class__; return ~abs(self & cls(value))


class Dist(Real):

	__slots__ = ()

	minimum: number =  0.0
	midimum: number =  1.0
	maximum: number = +inf

	def __add__(self, value: number, /) -> Self: cls = self.__class__; return cls(float(self) + float(cls(value)))
	def __mul__(self, value: number, /) -> Self: cls = self.__class__; return cls(float(self) * float(cls(value)))

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(1 / float(self) if self else self.maximum)

	@property
	def real(self, /) -> Real:
		return Real(-log(self) if self else Real.minimum)

	@property
	def dist(self, /) -> Dist:
		return self

	@property
	def prob(self, /) -> Prob:
		return Prob(1 / (1 + float(self)))


class Prob(Real):

	__slots__ = ()

	minimum: number =  1.0
	midimum: number =  0.5
	maximum: number =  0.0

	def __add__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		lower = min(float(self), float(value))
		upper = max(float(self), float(value))

		if lower == self.maximum: return cls(lower)

		ratio = lower / upper
		complement = 1 - upper

		return cls(lower / (1 + ratio * complement))
	#	return cls(float(self & value) / float(self | value))

	def __mul__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		lower = min(float(self), float(value))
		upper = max(float(self), float(value))

		if lower == self.maximum or upper == self.midimum: return cls(lower)
		if upper == self.minimum or lower == self.midimum: return cls(upper)

		if lower <= 1 - upper:
			product = lower / (1 - lower) * (upper / (1 - upper))

			return cls(product / (1 + product))

		else:
			product = (1 - lower) / lower * ((1 - upper) / upper)

			return cls(1 / (1 + product))

	#	return cls(float(self & value) / float(self == value))

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(self.minimum - float(self))

	@property
	def real(self, /) -> Real:
		return self.dist.real

	@property
	def dist(self, /) -> Dist:
		return Dist((1 - float(self)) / float(self) if self else Dist.maximum)

	@property
	def prob(self, /) -> Prob:
		return self


class Bool(int):

	__slots__ = ()

	minimum: int = 1
	maximum: int = 0

	def __new__(cls, value: number = False, /) -> Self:
		if not isinstance(value, int) or value not in (cls.minimum, cls.maximum):
			raise TypeError(f"expected a boolean value, got {value!r}")

		return super().__new__(cls, bool(value))

	def __repr__(self, /) -> str: return repr(bool(self))
	def  __str__(self, /) -> str: return  str(bool(self))

	def __add__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) and bool(value))

	def __mul__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) and bool(value))

	def __and__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) and bool(value))

	def  __or__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) or bool(value))

	def __sub__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) and not bool(value))

	def __xor__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) is not bool(value))

	def __radd__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) + self
	def __rmul__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) * self
	def __rand__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) & self
	def  __ror__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) | self
	def __rsub__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) - self
	def __rxor__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) ^ self

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(not self)

	def __pos__(self, /) -> Self: return  self
	def __neg__(self, /) -> Self: return ~self
	def __abs__(self, /) -> Self: return  self

	def __eq__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) is bool(value))

	def __ne__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) is not bool(value))

	def __lt__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(value) and not bool(self))

	def __le__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(value) or not bool(self))

	def __gt__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) and not bool(value))

	def __ge__(self, value: number, /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return NotImplemented

		return cls(bool(self) or not bool(value))

	@classmethod
	def min(cls, /) -> Self: return cls(cls.minimum)
	@classmethod
	def max(cls, /) -> Self: return cls(cls.maximum)

	def union       (self, *values: number) -> Self: cls = self.__class__; return reduce(cls. __or__, values, self)
	def intersection(self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__and__, values, self)
	def difference  (self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__sub__, values, self)

	def symmetric_difference(self, value: int, /) -> Self:
		return self ^ value

	def issubset  (self, value: number, /) -> Self: return self <= value
	def issuperset(self, value: number, /) -> Self: return self >= value

	def isdisjoint(self, value: number, /) -> Self: cls = self.__class__; return ~abs(self & cls(value))


class Set[K: Hashable, V: (Bool, Prob)](dict[K, V]):

	truth: type[V]
	complement: bool

	def __init_subclass__(cls, /, *args,
		truth: type[V] | None = None,
	**kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)

		if truth is not None:
			cls.truth = truth

		if not hasattr(cls, "truth"):
			raise TypeError("missing required keyword-only argument: 'truth'")

	def __init__(self, iterable: Iterable[K] | Mapping[K, V] | None = None, /, *,
		complement: bool | None = None,
	):
		if iterable is None:
			iterable = ()

		if complement is None:
			complement = iterable.complement if isinstance(iterable, Set) else False

		self.complement = complement

		super().__init__(
			iterable.items() if isinstance(iterable, Mapping) else ((key, self.truth(not self.complement)) for key in iterable),
		)

	def __repr__(self, /) -> str:
		return repr(set(self)) if not self.complement else "~" + repr(set(~self))

	def __missing__(self, _: K, /) -> V:
		return self.default

	def __contains__(self, key: K, /) -> V:
		return self[key]

	def __iter__(self, /) -> Iterator[K]:
		cls = self.__class__

		if self.complement:
			raise TypeError(f"cannot iterate an {cls.__name__} with implicit members")

		return (key for key, value in self.items() if value)

	def __len__(self, /) -> int:
		cls = self.__class__

		if self.complement:
			raise TypeError(f"an {cls.__name__} with implicit members has no finite length")

		return self.size

	def __bool__(self, /) -> bool:
		return self.complement or any(self.values())

	def __add__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: self[key] + other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default + other.default),
		)

	def __mul__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: self[key] * other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default * other.default),
		)

	def __and__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: self[key] & other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default & other.default),
		)

	def __or__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: self[key] | other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default | other.default),
		)

	def __sub__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: self[key] - other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default - other.default),
		)

	def __xor__(self, other: Iterable[K] | Mapping[K, V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: self[key] ^ other[key] for key in self.keys() | other.keys()},
			complement = bool(self.default ^ other.default),
		)

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls({key: ~value for key, value in self.items()},
			complement = not self.complement,
		)

	def __pos__(self, /) -> Self:
		cls = self.__class__

		return cls(self,
			complement = self.complement,
		)

	def __neg__(self, /) -> Self:
		return ~self

	def __abs__(self, /) -> V:
		cls = self.__class__

		result = sum((value if self.complement else ~value for value in self.values()), cls.truth(cls.truth.minimum))

		return result if self.complement else ~result

	def __eq__(self, other: Iterable[K] | Mapping[K, V], /) -> V:
		cls = self.__class__

		other = cls(other)

		return cls.truth(self.default == other.default).intersection(
			*(self[key] == other[key] for key in self.keys() | other.keys())
		)

	def __le__(self, other: Iterable[K] | Mapping[K, V], /) -> V:
		cls = self.__class__

		other = cls(other)

		return cls.truth(self.default <= other.default).intersection(
			*(self[key] <= other[key] for key in self.keys() | other.keys())
		)


	def __ge__(self, other: Iterable[K] | Mapping[K, V], /) -> V:
		cls = self.__class__

		other = cls(other)

		return cls.truth(self.default >= other.default).intersection(
			*(self[key] >= other[key] for key in self.keys() | other.keys())
		)

	def __ne__(self, other: Iterable[K] | Mapping[K, V], /) -> V: return ~(self == other)
	def __lt__(self, other: Iterable[K] | Mapping[K, V], /) -> V: return  (self <= other) & (self != other)
	def __gt__(self, other: Iterable[K] | Mapping[K, V], /) -> V: return  (self >= other) & (self != other)

	@property
	def indices(self, /) -> KeysView[K]:
		return self.keys()

	@property
	def size(self, /) -> int:
		exceptions = sum(float(membership) != float(self.default) for membership in self.values())

		return ~exceptions if self.default else exceptions

	@property
	def default(self, /) -> V:
		return self.truth(self.complement)

	@classmethod
	def fromkeys(cls, iterable: Iterable[K], value: V | None = None, /) -> Self:
		return cls(dict.fromkeys(iterable, cls.truth(1) if value is None else value))

	def copy(self, /) -> Self:
		cls = self.__class__

		return cls(self, complement = self.complement)

	def add(self, key: K, /) -> None:
		self[key] = self.truth(1)

	def remove(self, key: K, /) -> None:
		if key not in self:
			raise KeyError(key)

		self.discard(key)

	def discard(self, key: K, /) -> None:
		self[key] = self.truth(0)

	def clear(self, /) -> None:
		excluded = self.truth(0)

		self.complement = False
		self.update(dict.fromkeys(self.indices, excluded))

	def union	    (self, *iterables: Iterable[K]) -> Self: cls = self.__class__; return reduce(cls. __or__, iterables, self)
	def intersection(self, *iterables: Iterable[K]) -> Self: cls = self.__class__; return reduce(cls.__and__, iterables, self)
	def difference  (self, *iterables: Iterable[K]) -> Self: cls = self.__class__; return reduce(cls.__sub__, iterables, self)

	def symmetric_difference(self, iterable: Iterable[K], /) -> Self:
		cls = self.__class__

		return cls(iterable) ^ self

	def issubset  (self, iterable: Iterable[K] | Mapping[K, V], /) -> V: return self <= iterable
	def issuperset(self, iterable: Iterable[K] | Mapping[K, V], /) -> V: return self >= iterable

	def isdisjoint(self, iterable: Iterable[K] | Mapping[K, V], /) -> V: return ~abs(self & iterable)


class IndexSet[K: Hashable](Set[K, Bool],
	truth = Bool,
):
	...


class FuzzySet[K: Hashable](Set[K, Prob],
	truth = Prob,
):
	...


class Boolean[T: number](SupportsAbs[T], Protocol):

	def __bool__(self, /) -> bool: ...

	def __add__(self, value: Self, /) -> Self: ...
	def __mul__(self, value: Self, /) -> Self: ...
	def __and__(self, value: Self, /) -> Self: ...
	def  __or__(self, value: Self, /) -> Self: ...
	def __sub__(self, value: Self, /) -> Self: ...
	def __xor__(self, value: Self, /) -> Self: ...

	def __neg__(self, /) -> Self: ...
	def __pos__(self, /) -> Self: ...

	def __invert__(self, /) -> Self: ...

	def __eq__(self, value: Self, /) -> T: ...
	def __ne__(self, value: Self, /) -> T: ...
	def __lt__(self, value: Self, /) -> T: ...
	def __le__(self, value: Self, /) -> T: ...
	def __gt__(self, value: Self, /) -> T: ...
	def __ge__(self, value: Self, /) -> T: ...

	def union       (self, *values: Self) -> Self: ...
	def intersection(self, *values: Self) -> Self: ...
	def difference  (self, *values: Self) -> Self: ...

	def symmetric_difference(self, value: Self, /) -> Self: ...

	def issubset  (self, value: Self, /) -> T: ...
	def issuperset(self, value: Self, /) -> T: ...
	def isdisjoint(self, value: Self, /) -> T: ...
