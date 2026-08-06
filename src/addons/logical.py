from __future__ import annotations


import math
import typing


numeric: typing.TypeAlias = int | float

type pair[T: numeric] = tuple[T, T]


class base(float):

	minimum: float
	midimum: float
	maximum: float

	def __new__(cls, value: numeric | logical, /) -> typing.Self:
		self = super().__new__(cls, getattr(value, cls.__name__.lower(), value))

		lower, upper = sorted(cls.range())

		if not lower <= float(self) <= upper:
			raise ValueError(f"not {lower} <= {self} <= {upper} for {cls.__name__}")

		return self

	def     __add__(self, value: float, /) -> typing.Self: return self.__class__(super().    __add__(value))
#	def     __sub__(self, value: float, /) -> typing.Self: return self.__class__(super().    __sub__(value))
	def     __mul__(self, value: float, /) -> typing.Self: return self.__class__(super().    __mul__(value))
	def __truediv__(self, value: float, /) -> typing.Self: return self.__class__(super().__truediv__(value))
#	def     __mod__(self, value: float, /) -> typing.Self: return self.__class__(super().    __mod__(value))

#	def __floordiv__(self, value: float, /) -> typing.Self:
#		return self.__class__(super().__floordiv__(value))

	def __and__(self, value: float, /) -> typing.Self: return self.__class__(self.prob.meet(self.__class__(value).prob))
	def  __or__(self, value: float, /) -> typing.Self: return self.__class__(self.prob.join(self.__class__(value).prob))

	def __pow__(self, value: float, mod: None = None, /) -> typing.Self:
		return self.__class__(super().__pow__(value, mod))

	def __sub__(self, value: float, /) -> typing.Self:
		value = self.__class__(value)

		return self & ~value

	def __xor__(self, value: float, /) -> typing.Self:
		value = self.__class__(value)

		return (self - value) | (value - self)
		return (self | value) - (value & self)

	def      __radd__(self, value: float, /) -> typing.Self: return self.__class__(value) +  self
	def      __rsub__(self, value: float, /) -> typing.Self: return self.__class__(value) -  self
	def      __rmul__(self, value: float, /) -> typing.Self: return self.__class__(value) *  self
	def  __rtruediv__(self, value: float, /) -> typing.Self: return self.__class__(value) /  self
#	def      __rmod__(self, value: float, /) -> typing.Self: return self.__class__(value) %  self
#	def __rfloordiv__(self, value: float, /) -> typing.Self: return self.__class__(value) // self
	def      __rand__(self, value: float, /) -> typing.Self: return self.__class__(value) &  self
	def       __ror__(self, value: float, /) -> typing.Self: return self.__class__(value) |  self
	def      __rxor__(self, value: float, /) -> typing.Self: return self.__class__(value) ^  self

#	def __rpow__(self, value: float, mod: None = None, /) -> typing.Self:
#		return self.__class__(value).__pow__(self, mod)

	def __neg__(self, /) -> typing.Self: return self.__class__(super().__neg__())
	def __pos__(self, /) -> typing.Self: return self.__class__(super().__pos__())
	def	__abs__(self, /) -> typing.Self: return self.__class__(super().__abs__())

	def __invert__(self, /) -> typing.Self:
		return self.__class__(self.prob.complement())

	def __eq__(self, value: float, /) -> prob:
		meet = (self & value).prob
		join = (self | value).prob

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
	def real(self, /) -> real: return real(self)
	@property
	def dist(self, /) -> dist: return dist(self)
	@property
	def prob(self, /) -> prob: return prob(self)
	@property
	def imag(self, /) -> real: return self.__class__(self.midimum).real

	def conjugate(self, /) -> typing.Self:
		return self


class real(base):

	minimum: float = +math.inf
	midimum: float =     0.
	maximum: float = -math.inf

	@property
	def real(self, /) -> real:
		return self

	@property
	def dist(self, /) -> dist:
		return dist(math.exp(-self))

	@property
	def prob(self, /) -> prob:
		return self.dist.prob


class dist(base):

	minimum: float =     0.
	midimum: float =     1.
	maximum: float = +math.inf

	def __mul__(self, value: float, /) -> typing.Self:
		return self.__class__(self.prob * self.__class__(value).prob)

	@property
	def real(self, /) -> real:
		return real(-math.log(float(self)) if self else real.minimum)

	@property
	def dist(self, /) -> dist:
		return self

	@property
	def prob(self, /) -> prob:
		return prob(math.exp(-float(self)))
		return prob( 1 / (1 + float(self)))


class prob(base):

	minimum: float =    1.
	midimum: float = math.exp(-1)
#	midimum: float =     .5
	maximum: float =    0.

	def __add__(self, value: float, /) -> typing.Self:
		return self.__class__(self.dist + self.__class__(value).dist)

	@property
	def real(self, /) -> real:
		return self.dist.real

	@property
	def dist(self, /) -> dist:
		return dist(-math.log(float(self))    if self else dist.maximum)
		return dist(      1 / float(self) - 1 if self else dist.maximum)

	@property
	def prob(self, /) -> prob:
		return self

	def meet(self, value: float, /) -> typing.Self:
		return self * self.__class__(value)

	def join(self, value: float, /) -> typing.Self:
		other = self.__class__(value)

		return self.complement().meet(other.complement()).complement()

	def complement(self, /) -> typing.Self:
		return self.__class__(self.minimum - float(self))


logical: typing.TypeAlias = real | dist | prob


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
		if self.default:
			raise TypeError(f"cannot iterate an {self.__class__.__name__} with implicit members")

		return (key for key, value in self.items() if value)

	def __len__(self, /) -> int:
		if self.default:
			raise TypeError(f"an {self.__class__.__name__} with implicit members has no finite length")

		return sum(self.values())

	def __bool__(self, /) -> bool:
		return self.default or any(self.values())

	def __invert__(self, /) -> typing.Self:
		return self.__class__({key: not value for key, value in self.items()}, default = not self.default)

	@property
	def indices(self, /) -> typing.KeysView[T]:
		return self.keys()

	@classmethod
	def fromkeys(cls, iterable: typing.Iterable[T], value: bool = True, /) -> typing.Self:
		return cls(dict.fromkeys(iterable, value))

	def copy(self, /) -> typing.Self:
		return self.__class__(self, default = self.default)

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
