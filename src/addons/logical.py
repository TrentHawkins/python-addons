from __future__ import annotations


from functools import reduce
from math import inf, exp, isinf, log
from typing import Hashable, Iterable, Iterator, KeysView, Mapping, Self, TypeAlias


numeric: TypeAlias = int | float

type pair[T: numeric] = tuple[T, T]


class real(float):

	__slots__ = ()

	minimum: float = +inf
	midimum: float =  0.0
	maximum: float = -inf

	def __new__(cls, value: numeric | logical, /) -> Self:
		self = super().__new__(cls, getattr(value, cls.__name__.lower(), value))

		lower, upper = sorted(cls.range())

		if not lower <= float(self) <= upper:
			raise ValueError(f"not {lower} <= {self} <= {upper} for {cls.__name__}")

		return self

	def     __add__(self, value: float, /) -> Self: cls = self.__class__; return cls(self.dist + cls(value).dist)
	def     __mul__(self, value: float, /) -> Self: cls = self.__class__; return cls(self.prob * cls(value).prob)
	def __truediv__(self, value: float, /) -> Self: cls = self.__class__; return cls(self.prob - cls(value).prob)
	def     __and__(self, value: float, /) -> Self: cls = self.__class__; return cls(self.prob * cls(value).prob)

#	def __pow__(self, value: float, mod: None = None, /) -> Self:
#		cls = self.__class__
#
#		return cls(super().__pow__(value, mod))

	def __or__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return ~(~self & ~value)

	def __sub__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return self & ~value

	def __xor__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return (self - value) | (value - self)
	#	return (self | value) - (value & self)

	def      __radd__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) + self
	def      __rsub__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) - self
	def      __rmul__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) * self
	def  __rtruediv__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) / self
	def      __rand__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) & self
	def       __ror__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) | self
	def      __rxor__(self, value: float, /) -> Self: cls = self.__class__; return cls(value) ^ self

#	def __rpow__(self, value: float, mod: None = None, /) -> Self:
#		cls = self.__class__
#
#		return cls(value).__pow__(self, mod)

	def __neg__(self, /) -> Self: return ~self
	def __pos__(self, /) -> Self: return  self
	def	__abs__(self, /) -> Self: return  self

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(~self.prob)

	def __eq__(self, value: float, /) -> prob:
		meet = float((self & value).prob)
		join = float((self | value).prob)

		return prob(meet / join if join else prob.minimum)

	@classmethod
	def range(cls, /) -> pair[float]:
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
	def real(self, /) -> real: return self
	@property
	def dist(self, /) -> dist: return dist(exp(-float(self)))
	@property
	def prob(self, /) -> prob: return self.dist.prob
	@property
	def imag(self, /) -> real:
		cls = self.__class__

		return cls(self.midimum).real

	def conjugate(self, /) -> Self:
		return self

	def union       (self, iterable: Iterable[float], /) -> Self: cls = self.__class__; return reduce(cls. __or__, iterable, self)
	def intersection(self, iterable: Iterable[float], /) -> Self: cls = self.__class__; return reduce(cls.__and__, iterable, self)
	def difference  (self, iterable: Iterable[float], /) -> Self: cls = self.__class__; return reduce(cls.__sub__, iterable, self)

	def symmetric_difference(self, value: float, /) -> Self:
		return self ^ value


class dist(real):

	__slots__ = ()

	minimum: float =  0.0
	midimum: float =  1.0
	maximum: float = +inf

	def __add__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) + float(value))

	def __mul__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return cls(self.maximum if isinf(self) or isinf(value) else float(self) + float(value) + float(self) * float(value))

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(1 / float(self) if self else dist.maximum)

	@property
	def real(self, /) -> real:
		return real(-log(self) if self else real.minimum)

	@property
	def dist(self, /) -> dist:
		return self

	@property
	def prob(self, /) -> prob:
		return prob(1 / (1 + float(self)))


class prob(real):

	__slots__ = ()

	minimum: float =  1.0
	midimum: float =  0.5
	maximum: float =  0.0

	def __add__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)
		self, value = min(self, value), max(self, value)

		return cls(float(self) / (1 + float(self) / float(value) - float(self)) if value else prob.maximum)

	def __mul__(self, value: float, /) -> Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) * float(value))

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(self.minimum - float(self))

	@property
	def real(self, /) -> real:
		return self.dist.real

	@property
	def dist(self, /) -> dist:
		return dist((1 - float(self)) / float(self) if self else dist.maximum)

	@property
	def prob(self, /) -> prob:
		return self


logical: TypeAlias = real | dist | prob


class boolean(int):

	__slots__ = ()

	def __new__(cls, value: object = False, /) -> Self:
		return super().__new__(cls, bool(value))

	def __repr__(self, /) -> str: return repr(bool(self))
	def  __str__(self, /) -> str: return  str(bool(self))

	def __and__(self, value: object, /) -> Self: cls = self.__class__; return cls(bool(self)     and bool(value))
	def  __or__(self, value: object, /) -> Self: cls = self.__class__; return cls(bool(self)      or bool(value))
	def __sub__(self, value: object, /) -> Self: cls = self.__class__; return cls(bool(self) and not bool(value))
	def __xor__(self, value: object, /) -> Self: cls = self.__class__; return cls(bool(self)  is not bool(value))

	def __rand__(self, value: object, /) -> Self: cls = self.__class__; return cls(value) & self
	def  __ror__(self, value: object, /) -> Self: cls = self.__class__; return cls(value) | self
	def __rsub__(self, value: object, /) -> Self: cls = self.__class__; return cls(value) - self
	def __rxor__(self, value: object, /) -> Self: cls = self.__class__; return cls(value) ^ self

	def __invert__(self, /) -> Self:
		cls = self.__class__

		return cls(not self)

	@classmethod
	def min(cls, /) -> Self: return cls(1)
	@classmethod
	def max(cls, /) -> Self: return cls(0)

	def union       (self, iterable: Iterable[object], /) -> Self: cls = self.__class__; return reduce(cls. __or__, iterable, self)
	def intersection(self, iterable: Iterable[object], /) -> Self: cls = self.__class__; return reduce(cls.__and__, iterable, self)
	def difference  (self, iterable: Iterable[object], /) -> Self: cls = self.__class__; return reduce(cls.__sub__, iterable, self)

	def symmetric_difference(self, value: object, /) -> Self:
		return self ^ value


class indexset[T: Hashable](dict[T, boolean]):

	default: boolean

	def __init__(self, iterable: Iterable[T] | Mapping[T, boolean] = (), /, *, default: boolean = boolean.max()):
		super().__init__(iterable if isinstance(iterable, Mapping) else ((key, boolean.min()) for key in iterable))

		self.default = default

	def __repr__(self, /) -> str:
		return repr(set(self)) if not self.default else "~" + repr(set(~self))

	def __missing__(self, _: T, /) -> boolean:
		return self.default

	def __contains__(self, key: T, /) -> boolean:
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
	def fromkeys(cls, iterable: Iterable[T], value: boolean = boolean.min(), /) -> Self:
		return cls(dict.fromkeys(iterable, value))

	def copy(self, /) -> Self:
		cls = self.__class__

		return cls(self, default = self.default)

	def add(self, key: T, /) -> None:
		self[key] = boolean.min()

	def remove(self, key: T, /) -> None:
		if key not in self:
			raise KeyError(key)

		self.discard(key)

	def discard(self, key: T, /) -> None:
		self[key] = boolean.max()

	def clear(self, /) -> None:
		self.default = boolean.max()
		self.update(dict.fromkeys(self.indices, boolean.max()))
