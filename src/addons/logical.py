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
import operator
from math import inf, exp, log, isnan
from functools import reduce
from typing import (
	Hashable,
	Callable,
	Iterable,
	Iterator,
	KeysView,
	Mapping,
	Protocol,
	Self,
	SupportsAbs,
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


class SupportsOperable[O](Protocol):

	def __and__(self, value: O, /) -> Self:
		...

	def __or__(self, value: O, /) -> Self:
		...

	def __sub__(self, value: O, /) -> Self:
		...

	def __xor__(self, value: O, /) -> Self:
		...


class SupportsOrder[O, T: SupportsTruth](Protocol):

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


class SupportsSemi[O](Protocol):

	def __add__(self, value: O, /) -> Self:
		...

	def __mul__(self, value: O, /) -> Self:
		...


class SupportsBounded(Protocol):

	@classmethod
	def minimum(cls, /) -> Self:
		...

	@classmethod
	def maximum(cls, /) -> Self:
		...


class SupportsIntersection[O](Protocol):

	def intersection(self, *values: O) -> Self:
		...


class SupportsBool(Protocol):

	def __bool__(self, /) -> bool:
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

	def __pos__(self, /) -> Self: return  self
	def __neg__(self, /) -> Self: return ~self

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


class SelfMeasured:

	def __abs__(self, /) -> Self:
		return self


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


class ConjunctiveSemi[O](Semi[O], Operable[O]):

	def __add__(self, value: O, /) -> Self: return self.__and__(value)
	def __mul__(self, value: O, /) -> Self: return self.__and__(value)


class Full[O](Semi[O]):

	@abstractmethod
	def __truediv__(self, value: O, /) -> Self:
		...


class Coercible[O](ABC):

	@classmethod
	def coerce(cls, value: O, /) -> Self:
		constructor = cast(Callable[[O], Self], cls)

		return constructor(value)


class Reflected[O](Semi[O], Operable[O], Coercible[O]):

	def __radd__(self, value: O, /) -> Self: return self.coerce(value) + cast(O, self)
	def __rmul__(self, value: O, /) -> Self: return self.coerce(value) * cast(O, self)
	def __rand__(self, value: O, /) -> Self: return self.coerce(value) & cast(O, self)
	def  __ror__(self, value: O, /) -> Self: return self.coerce(value) | cast(O, self)
	def __rsub__(self, value: O, /) -> Self: return self.coerce(value) - cast(O, self)
	def __rxor__(self, value: O, /) -> Self: return self.coerce(value) ^ cast(O, self)


class DivisiblyReflected[O](Full[O], Reflected[O]):

	def __rtruediv__(self, value: O, /) -> Self: return self.coerce(value) / cast(O, self)


class SetLike[O, T: SupportsTruth](Operable[O], Order[O, T]):

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


class CoerciveSetLike[O, T: SupportsTruth](SetLike[O, T], Coercible[O], Truth):

	def __or__(self, value: O, /) -> Self:
		coerced = self.coerce(value)

		return ~(~self & cast(O, ~coerced))

	def __sub__(self, value: O, /) -> Self:
		coerced = self.coerce(value)

		return self & cast(O, ~coerced)

	def __xor__(self, value: O, /) -> Self:
		coerced = self.coerce(value)

		left = self - cast(O, coerced)
		right = coerced - cast(O, self)

		return left | cast(O, right)

class MeasuredSetLike[O, T: SupportsTruth](SetLike[O, T], Measurable[T]):

	def isdisjoint(self, value: O, /) -> T:
		return ~abs(self & value)


class Mutable[O](Semi[O], Operable[O]):

	@abstractmethod
	def become(self, result: Self, /) -> Self:
		...

	def __iadd__(self, value: O, /) -> Self: return self.become(self + value)
	def __imul__(self, value: O, /) -> Self: return self.become(self * value)
	def __iand__(self, value: O, /) -> Self: return self.become(self & value)
	def  __ior__(self, value: O, /) -> Self: return self.become(self | value)
	def __isub__(self, value: O, /) -> Self: return self.become(self - value)
	def __ixor__(self, value: O, /) -> Self: return self.become(self ^ value)


class MutableSetLike[O, T: SupportsTruth](Mutable[O], SetLike[O, T]):

	def              update(self, *values: O) -> None: self.become(self.       union(*values))
	def intersection_update(self, *values: O) -> None: self.become(self.intersection(*values))
	def   difference_update(self, *values: O) -> None: self.become(self.  difference(*values))

	def symmetric_difference_update(self, value: O, /) -> None:
		self.become(self.symmetric_difference(value))


class Bounded(ABC):

	@classmethod
	@abstractmethod
	def minimum(cls, /) -> Self:
		...

	@classmethod
	@abstractmethod
	def maximum(cls, /) -> Self:
		...


class SetValue[O, T: SupportsTruth](
	SupportsOperable[O],
	SupportsOrder[O, T],
	SupportsSemi[O],
	SupportsAbs[T],
	SupportsBounded,
	SupportsIntersection[O],
	SupportsBool,
	SupportsTruth,
	Protocol,
):

	...


class Real(
	Bounded,
	DivisiblyReflected[number],
	CoerciveSetLike[number, "Prob"],
	Total[number, "Prob"],
	SelfMeasured,
	Measurable["Real"],
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

#	def __rpow__(self, value: numeric, mod: None = None, /) -> Self:
#		cls = self.__class__
#
#		return cls(value).__pow__(self, mod)

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(~self.prob)

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
	ConjunctiveSemi[number],
	Reflected[number],
	SelfMeasured,
	MeasuredSetLike[number, "Bool"],
	Total[number, "Bool"],
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

	def apply(self, value: number, operation: Callable[[bool, bool], bool], /) -> Self:
		cls = self.__class__

		if isinstance(value, float):
			return cast(Self, NotImplemented)

		return cls(operation(bool(self), bool(value)))

	def __and__(self, value: number, /) -> Self: return self.apply(value, lambda left, right: left and     right)
	def  __or__(self, value: number, /) -> Self: return self.apply(value, lambda left, right: left or      right)
	def __sub__(self, value: number, /) -> Self: return self.apply(value, lambda left, right: left and not right)
	def __xor__(self, value: number, /) -> Self: return self.apply(value, lambda left, right: left is  not right)

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(not self)

	def __eq__(self, value: number, /) -> Self: return self.apply(value, operator.eq)
	def __ne__(self, value: number, /) -> Self: return self.apply(value, operator.ne)
	def __lt__(self, value: number, /) -> Self: return self.apply(value, operator.lt)
	def __le__(self, value: number, /) -> Self: return self.apply(value, operator.le)
	def __gt__(self, value: number, /) -> Self: return self.apply(value, operator.gt)
	def __ge__(self, value: number, /) -> Self: return self.apply(value, operator.ge)

	@classmethod
	def minimum(cls, /) -> Self: return int.__new__(cls, True )
	@classmethod
	def maximum(cls, /) -> Self: return int.__new__(cls, False)


class Set[K: Hashable, T: SetValue, V: SetValue = T](
	Bounded,
	MutableSetLike[Iterable[K] | Mapping[K, V], T],
	MeasuredSetLike[Iterable[K] | Mapping[K, V], T],
	Partial[Iterable[K] | Mapping[K, V], T],
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

	def __add__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.combine(other, operator.add )
	def __mul__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.combine(other, operator.mul )
	def __and__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.combine(other, operator.and_)
	def  __or__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.combine(other, operator.or_ )
	def __sub__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.combine(other, operator.sub )
	def __xor__(self, other: Iterable[K] | Mapping[K, V], /) -> Self: return self.combine(other, operator.xor )

	def combine(self, other: Iterable[K] | Mapping[K, V], operation: Callable[[V, V], V], /) -> Self:
		cls = self.__class__

		other = cls(other)

		return cls({key: operation(self[key], other[key]) for key in self.keys() | other.keys()},
			complement = bool(operation(self.default, other.default)),
		)

	def become(self, result: Self, /) -> Self:
		if result is self:
			return self

		self.complement = result.complement

		dict.clear(self)
		dict.update(self, result)

		return self

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls({key: ~value for key, value in self.items()},
			complement = not self.complement,
		)

	def __pos__(self, /) -> Self:
		return self.copy()

	def __abs__(self, /) -> T:
		cls = self.__class__

		result = cast(T, sum((abs(value if self.complement else ~value) for value in self.values()), abs(cls.truth.minimum())))

		return result if self.complement else ~result

	def __eq__(self, other: Iterable[K] | Mapping[K, V], /) -> T: return self.compare(other, operator.eq)
	def __le__(self, other: Iterable[K] | Mapping[K, V], /) -> T: return self.compare(other, operator.le)
	def __ge__(self, other: Iterable[K] | Mapping[K, V], /) -> T: return self.compare(other, operator.ge)

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

	def compare(self, other: Iterable[K] | Mapping[K, V], comparison: Callable[[V, V], T], /) -> T:
		cls = self.__class__

		other = cls(other)

		return comparison(self.default, other.default).intersection(
			*(comparison(self[key], other[key]) for key in self.keys() | other.keys()),
		)

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


class IndexSet[I: Hashable](Set[I, Bool],
	truth = Bool,
):
	...


class FuzzySet[I: Hashable](Set[I, Prob],
	truth = Prob,
):
	...
