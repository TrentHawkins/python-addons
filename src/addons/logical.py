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


from abc import ABC, abstractmethod
from math import inf, exp, log, isnan
from functools import reduce
from typing import (
	Hashable,
	Iterable,
	Iterator,
	KeysView,
	Mapping,
	Never,
	Protocol,
	Self,
	TypeAlias,
)
from typing import cast


number: TypeAlias = int | float



class SupportsComplement(Protocol):

	def __invert__(self, /) -> Self:
		...


class SupportsTruth(SupportsComplement, Protocol):

	def __and__(self, value: Self, /) -> Self:
		...

	def __or__(self, value: Self, /) -> Self:
		...

	def __sub__(self, value: Self, /) -> Self:
		...

	def __xor__(self, value: Self, /) -> Self:
		...


class Complementable(ABC):

	@abstractmethod
	def __invert__(self, /) -> Self:
		...


class Truth(Complementable):

	def __and__(self, value: Self, /) -> Self: return ~(~self | ~value)
	def  __or__(self, value: Self, /) -> Self: return ~(~self & ~value)
	def __sub__(self, value: Self, /) -> Self: return    self & ~value

	def __xor__(self, value: Self, /) -> Self:
		return (self | value) - (self & value)
	#	return (self - value) | (self - value)

class Operable[O](ABC):

	@abstractmethod
	def __and__(self, value: O, /) -> Self:
		...

	@abstractmethod
	def __or__(self, value: O, /) -> Self:
		...

	@abstractmethod
	def __sub__(self, value: O, /) -> Self:
		...

	def __xor__(self, value: O, /) -> Self:
		return (self | value) - cast(O, self & value)


class Measurable[T: SupportsComplement](ABC):

	@abstractmethod
	def __abs__(self, /) -> T:
		...


class Order[O, T: SupportsTruth](ABC):

	@abstractmethod
	def __le__(self, value: O, /) -> T:
		...

	@abstractmethod
	def __ge__(self, value: O, /) -> T:
		...

	def __eq__(self, value: O, /) -> T: return ~(self != value)
	def __ne__(self, value: O, /) -> T: return ~(self == value)

	def __lt__(self, value: O, /) -> T: return (self <= value) & (self != value)
	def __gt__(self, value: O, /) -> T: return (self >= value) & (self != value)


class Partial[O, T: SupportsTruth](Order[O, T]):

	def __le__(self, value: O, /) -> T: return (self < value) | (self == value)
	def __ge__(self, value: O, /) -> T: return (self > value) | (self == value)


class Total[O, T: SupportsTruth](Order[O, T]):

	def __le__(self, value: O, /) -> T: return ~(self > value)
	def __ge__(self, value: O, /) -> T: return ~(self < value)


class Boolean[O: Complementable, T: SupportsTruth](Truth, Operable[O], Partial[O, T]):

	def __and__(self, value: O, /) -> Self: complement: Self = ~self; return ~(complement | ~value)
	def  __or__(self, value: O, /) -> Self: complement: Self = ~self; return ~(complement & ~value)
	def __sub__(self, value: O, /) -> Self:                           return         self & ~value

	def __le__(self, value: O, /) -> T: return (self | value) == value
	def __ge__(self, value: O, /) -> T: return (self & value) == value


class Semi[O](ABC):

	@abstractmethod
	def __add__(self, value: O, /) -> Self:
		...

	@abstractmethod
	def __mul__(self, value: O, /) -> Self:
		...


class Full[O](Semi[O]):

	@abstractmethod
	def __truediv__(self, value: O, /) -> Self:
		...


class SetLike[O, T: SupportsTruth](Operable[O], Partial[O, T]):

	def        union(self, *values: O) -> Self: cls = self.__class__; return reduce(cls. __or__, values, self)
	def intersection(self, *values: O) -> Self: cls = self.__class__; return reduce(cls.__and__, values, self)
	def   difference(self, *values: O) -> Self: cls = self.__class__; return reduce(cls.__sub__, values, self)

	def symmetric_difference(self, value: O, /) -> Self:
		return self ^ value

	def issubset  (self, value: O, /) -> T: return self <= value
	def issuperset(self, value: O, /) -> T: return self >= value

	@abstractmethod
	def isdisjoint(self, value: O, /) -> T:
		...


class MeasuredSetLike[O, T: SupportsTruth](SetLike[O, T], Measurable[T]):

	def isdisjoint(self, value: O, /) -> T:
		return ~abs(self & value)


class Bounded(ABC):

	@classmethod
	@abstractmethod
	def minimum(cls, /) -> Self:
		...

	@classmethod
	@abstractmethod
	def maximum(cls, /) -> Self:
		...


class SetValue[O, T: SupportsTruth](SupportsTruth, Protocol):

	def __bool__(self, /) -> bool:
		...

	def __add__(self, value: O, /) -> Self:
		...

	def __mul__(self, value: O, /) -> Self:
		...

	def __and__(self, value: O, /) -> Self:
		...

	def __or__(self, value: O, /) -> Self:
		...

	def __sub__(self, value: O, /) -> Self:
		...

	def __xor__(self, value: O, /) -> Self:
		...

	def __abs__(self, /) -> T:
		...

	def __eq__(self, value: O, /) -> T:
		...

	def __ne__(self, value: O, /) -> T:
		...

	def __lt__(self, value: O, /) -> T:
		...

	def __le__(self, value: O, /) -> T:
		...

	def __gt__(self, value: O, /) -> T:
		...

	def __ge__(self, value: O, /) -> T:
		...

	def intersection(self, *values: O) -> Self:
		...

	@classmethod
	def minimum(cls, /) -> Self:
		...

	@classmethod
	def maximum(cls, /) -> Self:
		...


class Real(
	Bounded,
	Full[number],
	SetLike[number, "Prob"],
	Measurable["Real"],
	Truth,
	float,
):

	__slots__ = ()

	def __new__(cls, value: number, /) -> Self:
		value = getattr(value, cls.__name__.lower(), value)
		value = cls.maximum() if isnan(value) else value

		self = super().__new__(cls, value)

		lower = min(float(cls.minimum()), float(cls.maximum()))
		upper = max(float(cls.minimum()), float(cls.maximum()))

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

	def __bool__(self, /) -> bool:
		return float.__bool__(self)

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
	def minimum(cls, /) -> Self: return float.__new__(cls, +inf)
	@classmethod
	def midimum(cls, /) -> Self: return float.__new__(cls,  0.0)
	@classmethod
	def maximum(cls, /) -> Self: return float.__new__(cls, -inf)

	@property
	def real(self, /) -> Real: return self
	@property
	def dist(self, /) -> Dist: return Dist(exp(-float(self)))
	@property
	def prob(self, /) -> Prob: return self.dist.prob
	@property
	def imag(self, /) -> Real:
		cls = self.__class__

		return cls.midimum().real

	def conjugate(self, /) -> Self:
		return self

	def isdisjoint(self, value: number, /) -> Prob:
		return ~abs(self & value).prob


class Dist(Real):

	__slots__ = ()

	def __add__(self, value: number, /) -> Self: cls = self.__class__; return cls(float(self) + float(cls(value)))
	def __mul__(self, value: number, /) -> Self: cls = self.__class__; return cls(float(self) * float(cls(value)))

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(1 / float(self) if self else self.maximum())

	@classmethod
	def minimum(cls, /) -> Self: return float.__new__(cls,  0.0)
	@classmethod
	def midimum(cls, /) -> Self: return float.__new__(cls,  1.0)
	@classmethod
	def maximum(cls, /) -> Self: return float.__new__(cls, +inf)

	@property
	def real(self, /) -> Real: return Real(-log(self) if self else Real.minimum())
	@property
	def dist(self, /) -> Dist: return self
	@property
	def prob(self, /) -> Prob: return Prob(1 / (1 + float(self)))


class Prob(Real):

	__slots__ = ()

	def __add__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		lower = min(float(self), float(value))
		upper = max(float(self), float(value))

		if lower == float(self.maximum()): return cls(lower)

		ratio = lower / upper
		complement = 1 - upper

		return cls(lower / (1 + ratio * complement))
	#	return cls(float(self & value) / float(self | value))

	def __mul__(self, value: number, /) -> Self:
		cls = self.__class__

		value = cls(value)

		lower = min(float(self), float(value))
		upper = max(float(self), float(value))

		if lower == float(self.maximum()) or upper == float(self.midimum()): return cls(lower)
		if upper == float(self.minimum()) or lower == float(self.midimum()): return cls(upper)

		if lower <= 1 - upper:
			product = lower / (1 - lower) * (upper / (1 - upper))

			return cls(product / (1 + product))

		else:
			product = (1 - lower) / lower * ((1 - upper) / upper)

			return cls(1 / (1 + product))

	#	return cls(float(self & value) / float(self == value))

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(float(self.minimum()) - float(self))

	@classmethod
	def minimum(cls, /) -> Self: return float.__new__(cls, 1.0)
	@classmethod
	def midimum(cls, /) -> Self: return float.__new__(cls, 0.5)
	@classmethod
	def maximum(cls, /) -> Self: return float.__new__(cls, 0.0)

	@property
	def real(self, /) -> Real: return self.dist.real
	@property
	def dist(self, /) -> Dist: return Dist((1 - float(self)) / float(self) if self else Dist.maximum())
	@property
	def prob(self, /) -> Prob: return self


class Bool(
	Bounded,
	Semi[number],
	MeasuredSetLike[number, "Bool"],
	Truth,
	int,
):

	__slots__ = ()

	def __new__(cls, value: number = False, /) -> Self:
		if not isinstance(value, int) or int(value) not in (int(cls.minimum()), int(cls.maximum())):
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
	def minimum(cls, /) -> Self: return int.__new__(cls, True )
	@classmethod
	def maximum(cls, /) -> Self: return int.__new__(cls, False)


class Set[K: Hashable, T: SetValue, V: SetValue = T](
	Bounded,
	Semi[Iterable[K] | Mapping[K, V]],
	MeasuredSetLike[Iterable[K] | Mapping[K, V], T],
	Truth,
	dict[K, V],
):

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

		super().__init__(iterable.items() if isinstance(iterable, Mapping) else ((key, ~self.default) for key in iterable))

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

	def become(self, result: Self, /) -> Self:
		if result is self:
			return self

		self.complement = result.complement

		dict.clear(self)
		dict.update(self, result)

		return self

	def __iadd__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.become(self + other)
	def __imul__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.become(self * other)
	def __iand__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.become(self & other)
	def  __ior__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.become(self | other)
	def __isub__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.become(self - other)
	def __ixor__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.become(self ^ other)

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

	def __abs__(self, /) -> T:
		cls = self.__class__

		result = cast(T, sum((abs(value if self.complement else ~value) for value in self.values()), abs(cls.truth.minimum())))

		return result if self.complement else ~result

	def __eq__(self, other: Iterable[K] | Mapping[K, V], /) -> T:
		cls = self.__class__

		other = cls(other)

		return (self.default == other.default).intersection(*(self[key] == other[key] for key in self.keys() | other.keys()))

	def __le__(self, other: Iterable[K] | Mapping[K, V], /) -> T:
		cls = self.__class__

		other = cls(other)

		return (self.default <= other.default).intersection(*(self[key] <= other[key] for key in self.keys() | other.keys()))


	def __ge__(self, other: Iterable[K] | Mapping[K, V], /) -> T:
		cls = self.__class__

		other = cls(other)

		return (self.default >= other.default).intersection(*(self[key] >= other[key] for key in self.keys() | other.keys()))

	def __ne__(self, other: Iterable[K] | Mapping[K, V], /) -> T: return ~(self == other)
	def __lt__(self, other: Iterable[K] | Mapping[K, V], /) -> T: return  (self <= other) & (self != other)
	def __gt__(self, other: Iterable[K] | Mapping[K, V], /) -> T: return  (self >= other) & (self != other)

	@classmethod
	def fromkeys(cls, iterable: Iterable[K], value: V | None = None, /) -> Self:
		if value is not None:
			return cls(dict.fromkeys(iterable, value))

		return cls({key: cls.truth.minimum() for key in iterable})

	@classmethod
	def minimum(cls, /) -> Self: return cls(complement = True )
	@classmethod
	def maximum(cls, /) -> Self: return cls(complement = False)

	@property
	def indices(self, /) -> KeysView[K]:
		return self.keys()

	@property
	def default(self, /) -> V:
		return self.truth.minimum() if self.complement else self.truth.maximum()

	def copy(self, /) -> Self:
		cls = self.__class__

		return cls(self,
			complement = self.complement,
		)

	def add(self, key: K, /) -> None:
		self[key] = self.truth.minimum()

	def remove(self, key: K, /) -> None:
		if key not in self:
			raise KeyError(key)

		self.discard(key)

	def discard(self, key: K, /) -> None:
		self[key] = self.truth.maximum()

	def clear(self, /) -> None:
		self.complement = False
		dict.update(self, {key: self.truth.maximum() for key in self.indices})

	def              update(self, *iterables: Iterable[K]): self.become(self.       union(*iterables))
	def intersection_update(self, *iterables: Iterable[K]): self.become(self.intersection(*iterables))
	def   difference_update(self, *iterables: Iterable[K]): self.become(self.  difference(*iterables))

	def symmetric_difference_update(self, iterable : Iterable[K], /):
		self.become(self.symmetric_difference(iterable))


class IndexSet[I: Hashable](Set[I, Bool],
	truth = Bool,
):
	...


class FuzzySet[I: Hashable](Set[I, Prob],
	truth = Prob,
):
	...
