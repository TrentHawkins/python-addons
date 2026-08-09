"""
------------------------------------------------------------------------------------------------------------------------------------
L − ~
0 1 1
1 0 0
------------------------------------------------------------------------------------------------------------------------------------
L R + × ∧ ∨ − Δ ≠ > < = ≤ ≥
0 0 0 0 0 0 0 0 0 0 0 1 1 1
0 1 0 0 0 1 1 1 1 0 1 0 1 0
1 0 0 0 0 1 0 1 1 1 0 0 0 1
1 1 1 1 1 1 0 0 0 0 0 1 1 1
------------------------------------------------------------------------------------------------------------------------------------
"""



from __future__ import annotations


from math import inf, exp, log, isfinite
from functools import reduce
from typing import Hashable, Iterable, Iterator, KeysView, Mapping, Self, TypeAlias


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

	def __new__(cls, value: number , /) -> Self:
		self = super().__new__(cls, getattr(value, cls.__name__.lower(), value))

		lower, upper = sorted(cls.range())

		if not lower <= float(self) <= upper:
			raise ValueError(f"not {lower} <= {self} <= {upper} for {cls.__name__}")

		return self

	def     __add__(self, value: number, /) -> Self: cls = self.__class__; return cls(self.dist + cls(value).dist)
	def     __mul__(self, value: number, /) -> Self: cls = self.__class__; return cls(self.prob * cls(value).prob)
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

	def union       (self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__or__, values, self)
	def intersection(self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__and__, values, self)
	def difference  (self, *values: number) -> Self: cls = self.__class__; return reduce(cls.__sub__, values, self)

	def symmetric_difference(self, value: number, /) -> Self:
		return self ^ value

	def issubset  (self, value: number, /) -> Prob: return self <= value
	def issuperset(self, value: number, /) -> Prob: return self >= value
	def isdisjoint(self, value: number, /) -> Prob: return self != value


class Dist(Real):

	__slots__ = ()

	minimum: number =  0.0
	midimum: number =  1.0
	maximum: number = +inf

	def __add__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) + float(value))

	def __mul__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) + float(value) + float(self) * float(value) if isfinite(self) and isfinite(value) else self.maximum)

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

		return cls(lower / (1 + lower / upper - lower) if upper else self.maximum)

	def __mul__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) * float(value))

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

	def __new__(cls, value: object = False, /) -> Self:
		return super().__new__(cls, bool(value))

	def __repr__(self, /) -> str: return repr(bool(self))
	def  __str__(self, /) -> str: return  str(bool(self))

	def __add__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self) and     bool(value))
	def __mul__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self) and     bool(value))
	def __and__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self) and     bool(value))
	def  __or__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self)  or     bool(value))
	def __sub__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self) and not bool(value))
	def __xor__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self)  is not bool(value))

	def __radd__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) + self
	def __rmul__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) * self
	def __rand__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) & self
	def  __ror__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) | self
	def __rsub__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) - self
	def __rxor__(self, value: int, /) -> Self: cls = self.__class__; return cls(value) ^ self

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(not self)

	def __eq__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self)  is     bool(value))
	def __ne__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self)  is not bool(value))
	def __lt__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(value) and not bool(self))
	def __le__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(value)  or not bool(self))
	def __gt__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self) and not bool(value))
	def __ge__(self, value: int, /) -> Self: cls = self.__class__; return cls(bool(self)  or not bool(value))

	@classmethod
	def min(cls, /) -> Self: return cls(1)
	@classmethod
	def max(cls, /) -> Self: return cls(0)

	def union       (self, *values: int) -> Self: cls = self.__class__; return reduce(cls. __or__, values, self)
	def intersection(self, *values: int) -> Self: cls = self.__class__; return reduce(cls.__and__, values, self)
	def difference  (self, *values: int) -> Self: cls = self.__class__; return reduce(cls.__sub__, values, self)

	def symmetric_difference(self, value: int, /) -> Self:
		return self ^ value

	def issubset  (self, value: int, /) -> Self: return self <= value
	def issuperset(self, value: int, /) -> Self: return self >= value
	def isdisjoint(self, value: int, /) -> Self: return self != value


class IndexSet[T: Hashable](dict[T, Bool]):

	default: Bool

	def __init__(self, iterable: Iterable[T] | Mapping[T, Bool] | None = None, /, *, default: Bool = Bool.max()):
		if iterable is None:
			iterable = ()

		super().__init__(iterable if isinstance(iterable, Mapping) else ((key, Bool.min()) for key in iterable))

		self.default = default

	def __repr__(self, /) -> str:
		return repr(set(self)) if not self.default else "~" + repr(set(~self))

	def __missing__(self, _: T, /) -> Bool:
		return self.default

	def __contains__(self, key: T, /) -> Bool:
		return self.get(key, self.default)

	def __iter__(self, /) -> Iterator[T]:
		cls = self.__class__

		if self.default:
			raise TypeError(f"cannot iterate an {cls.__name__} with implicit members")

		return (key for key, value in self.items() if value)

	def __len__(self, /) -> int:
		cls = self.__class__

		if self.default:
			raise TypeError(f"an {cls.__name__} with implicit members has no finite length")

		return self.size

	def __bool__(self, /) -> bool:
		return bool(self.default) or any(self.values())

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls({key: ~value for key, value in self.items()}, default = ~self.default)

	@property
	def indices(self, /) -> KeysView[T]:
		return self.keys()

	@property
	def size(self, /) -> int:
		exceptions = sum(membership != self.default for membership in self.values())

		return ~exceptions if self.default else exceptions

	@classmethod
	def fromkeys(cls, iterable: Iterable[T], value: Bool = Bool.min(), /) -> Self:
		return cls(dict.fromkeys(iterable, value))

	def copy(self, /) -> Self:
		cls = self.__class__

		return cls(self, default = self.default)

	def add(self, key: T, /) -> None:
		self[key] = Bool.min()

	def remove(self, key: T, /) -> None:
		if key not in self:
			raise KeyError(key)

		self.discard(key)

	def discard(self, key: T, /) -> None:
		self[key] = Bool.max()

	def clear(self, /) -> None:
		self.default = Bool.max()
		self.update(dict.fromkeys(self.indices, Bool.max()))
