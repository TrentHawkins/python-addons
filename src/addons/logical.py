from __future__ import annotations


import functools
import math
import typing


numeric: typing.TypeAlias = int | float

type pair[T: numeric] = tuple[T, T]


class real(float):

	__slots__ = ()

	minimum: float = +math.inf
	midimum: float =     0.0
	maximum: float = -math.inf

	def __new__(cls, value: numeric | logical, /) -> typing.Self:
		self = super().__new__(cls, getattr(value, cls.__name__.lower(), value))

		lower, upper = sorted(cls.range())

		if not lower <= float(self) <= upper:
			raise ValueError(f"not {lower} <= {self} <= {upper} for {cls.__name__}")

		return self

	def     __add__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(self.dist + cls(value).dist)
	def     __mul__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(self.prob * cls(value).prob)
	def __truediv__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(self.prob - cls(value).prob)
	def     __and__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(self.prob * cls(value).prob)

#	def __pow__(self, value: float, mod: None = None, /) -> typing.Self:
#		cls = self.__class__
#
#		return cls(super().__pow__(value, mod))

	def __or__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)

		return ~(~self & ~value)

	def __sub__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)

		return self & ~value

	def __xor__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)

		return (self - value) | (value - self)
	#	return (self | value) - (value & self)

	def      __radd__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) + self
	def      __rsub__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) - self
	def      __rmul__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) * self
	def  __rtruediv__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) / self
	def      __rand__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) & self
	def       __ror__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) | self
	def      __rxor__(self, value: float, /) -> typing.Self: cls = self.__class__; return cls(value) ^ self

#	def __rpow__(self, value: float, mod: None = None, /) -> typing.Self:
#		cls = self.__class__
#
#		return cls(value).__pow__(self, mod)

	def __neg__(self, /) -> typing.Self: return ~self
	def __pos__(self, /) -> typing.Self: return  self
	def	__abs__(self, /) -> typing.Self: return  self

	def __invert__(self, /) -> typing.Self:
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
	def dist(self, /) -> dist: return dist(math.exp(-float(self)))
	@property
	def prob(self, /) -> prob: return self.dist.prob
	@property
	def imag(self, /) -> real:
		cls = self.__class__

		return cls(self.midimum).real

	def conjugate(self, /) -> typing.Self:
		return self


class dist(real):

	__slots__ = ()

	minimum: float =     0.0
	midimum: float =     1.0
	maximum: float = +math.inf

	def __add__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) + float(value))

	def __mul__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)
		isinf = math.isinf(self) or math.isinf(value)

		return cls(self.maximum if isinf else float(self) + float(value) + float(self) * float(value))

	def __invert__(self, /) -> typing.Self:
		cls = self.__class__

		return cls(1 / float(self) if self else dist.maximum)

	@property
	def real(self, /) -> real:
		return real(-math.log(self) if self else real.minimum)

	@property
	def dist(self, /) -> dist:
		return self

	@property
	def prob(self, /) -> prob:
		return prob(1 / (1 + float(self)))


class prob(real):

	__slots__ = ()

	minimum: float =     1.0
	midimum: float =     0.5
	maximum: float =     0.0

	def __add__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)
		self, value = min(self, value), max(self, value)

		return cls(float(self) / (1 + float(self) / float(value) - float(self)) if value else prob.maximum)

	def __mul__(self, value: float, /) -> typing.Self:
		cls = self.__class__

		value = cls(value)

		return cls(float(self) * float(value))

	def __invert__(self, /) -> typing.Self:
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


logical: typing.TypeAlias = real | dist | prob


class boolean(int):

	__slots__ = ()

	def __new__(cls, value: object = False, /) -> typing.Self:
		return super().__new__(cls, bool(value))

	def __repr__(self, /) -> str: return repr(bool(self))
	def  __str__(self, /) -> str: return  str(bool(self))

	def __and__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(bool(self)     and bool(value))
	def  __or__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(bool(self)      or bool(value))
	def __sub__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(bool(self) and not bool(value))
	def __xor__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(bool(self)  is not bool(value))

	def __rand__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(value) & self
	def  __ror__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(value) | self
	def __rsub__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(value) - self
	def __rxor__(self, value: object, /) -> typing.Self: cls = self.__class__; return cls(value) ^ self

	def __invert__(self, /) -> typing.Self:
		cls = self.__class__

		return cls(not self)


class indexset[T: typing.Hashable](dict[T, bool]):

	default: bool

	def __init__(self, iterable: typing.Iterable[T] | typing.Mapping[T, bool] = (), /, *, default: bool = False):
		super().__init__(iterable if isinstance(iterable, typing.Mapping) else ((key, True) for key in iterable))

		self.default = default

	def __repr__(self, /) -> str:
		return repr(set(self)) if not self.default else "~" + repr(set(~self))

	def __missing__(self, _: T, /) -> bool:
		return self.default

	def __contains__(self, key: T, /) -> bool:
		return self.get(key, self.default)

	def __iter__(self, /) -> typing.Iterator[T]:
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
		return self.default or any(self.values())

	def __invert__(self, /) -> typing.Self:
		cls = self.__class__

		return cls({key: not value for key, value in self.items()}, default = not self.default)

	@property
	def indices(self, /) -> typing.KeysView[T]:
		return self.keys()

	@property
	def size(self, /) -> int:
		exceptions = sum(membership != self.default for membership in self.values())

		return ~exceptions if self.default else exceptions

	@classmethod
	def fromkeys(cls, iterable: typing.Iterable[T], value: bool = True, /) -> typing.Self:
		return cls(dict.fromkeys(iterable, value))

	def copy(self, /) -> typing.Self:
		cls = self.__class__

		return cls(self, default = self.default)

	def add(self, key: T, /) -> None:
		self[key] = True

	def remove(self, key: T, /) -> None:
		if key not in self:
			raise KeyError(key)

		self.discard(key)

	def discard(self, key: T, /) -> None:
		self[key] = False

	def clear(self, /) -> None:
		self.default = False
		self.update(dict.fromkeys(self.indices, False))
