from __future__ import annotations


import math
import typing


numeric: typing.TypeAlias = int | float

type pair[T: numeric] = tuple[T, T]


class base(float):

	minimum: float
	midimum: float
	maximum: float
	optimum: float

	def __new__(cls, value: numeric | logical, /) -> typing.Self:
		self = super().__new__(cls, getattr(value, cls.__name__.lower(), value))

		if not cls.minimum <= float(self) <= cls.maximum:
			raise ValueError(f"not {cls.minimum} <= {self} <= {cls.maximum} for {cls.__name__}")

		return self

	def     __add__(self, value: float, /) -> typing.Self: return self.__class__(super().    __add__(value))
#	def     __sub__(self, value: float, /) -> typing.Self: return self.__class__(super().    __sub__(value))
	def     __mul__(self, value: float, /) -> typing.Self: return self.__class__(super().    __mul__(value))
	def __truediv__(self, value: float, /) -> typing.Self: return self.__class__(super().__truediv__(value))
	def     __mod__(self, value: float, /) -> typing.Self: return self.__class__(super().    __mod__(value))

	def     __and__(self, value: float, /) -> typing.Self: return self.__class__(min(self, value))
	def      __or__(self, value: float, /) -> typing.Self: return self.__class__(max(self, value))

	def __floordiv__(self, value: float, /) -> typing.Self:
		return self.__class__(super().__floordiv__(value))

	def __pow__(self, value: float, mod: None = None, /) -> typing.Self:
		return self.__class__(super().__pow__(value, mod))

	def __divmod__(self, value: float, /) -> pair[typing.Self]:
		quotient, remainder = super().__divmod__(value)

		return (
			self.__class__(quotient ),
			self.__class__(remainder),
		)

	def __sub__(self, value: float, /) -> typing.Self:
		return self & ~self.__class__(value)

	def __xor__(self, value: float, /) -> typing.Self:
		return (self - value) | (self.__class__(value) - self)
		return (self | value) - (self.__class__(value) & self)

	def     __radd__(self, value: float, /) -> typing.Self: return self.__class__(value) + self
	def     __rsub__(self, value: float, /) -> typing.Self: return self.__class__(value) - self
	def     __rmul__(self, value: float, /) -> typing.Self: return self.__class__(value) * self
	def __rtruediv__(self, value: float, /) -> typing.Self: return self.__class__(value) / self
	def     __rmod__(self, value: float, /) -> typing.Self: return self.__class__(value) % self
	def     __rand__(self, value: float, /) -> typing.Self: return self.__class__(value) & self
	def      __ror__(self, value: float, /) -> typing.Self: return self.__class__(value) | self
	def     __rxor__(self, value: float, /) -> typing.Self: return self.__class__(value) ^ self

#	def __rpow__(self, value: float, mod: None = None, /) -> typing.Self:
#		return self.__class__(super().__rpow__(value, mod))

#	def __rdivmod__(self, value: float, /) -> pair[typing.Self]:
#		quotient, remainder = super().__rdivmod__(value)
#
#		return (
#			self.__class__(quotient ),
#			self.__class__(remainder),
#		)

	def __neg__(self, /) -> typing.Self: return self.__class__(super().__neg__())
	def __pos__(self, /) -> typing.Self: return self.__class__(super().__pos__())
	def	__abs__(self, /) -> typing.Self: return self.__class__(super().__abs__())

	def __invert__(self, /) -> typing.Self:
		return -self

#	@classmethod
#	def range(cls, /) -> pair[float]:
#		return (
#			min(
#				cls.minimum,
#				cls.maximum,
#			),
#			max(
#				cls.minimum,
#				cls.maximum,
#			),
#		)

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

	minimum: float = -math.inf
	midimum: float =     0.
	maximum: float = +math.inf
	optimum: float = maximum

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
	optimum: float = minimum

	def __mul__(self, value: float, /) -> typing.Self:
		return self.__class__(self.prob * self.__class__(value).prob)

	def __and__(self, value: float, /) -> typing.Self:
		return self.__class__(self.prob & self.__class__(value).prob)

	def  __or__(self, value: float, /) -> typing.Self:
		return ~(~self & ~self.__class__(value))

	def __neg__(self, /) -> typing.Self:
		return self.__class__(~self.prob)

	@property
	def real(self, /) -> real:
		return real(-math.log(float(self)) if self else real.maximum)

	@property
	def dist(self, /) -> dist:
		return self

	@property
	def prob(self, /) -> prob:
		return prob(math.exp(-float(self)))
		return prob( 1 / (1 + float(self)))


class prob(base):

	minimum: float =    0.
	midimum: float = math.exp(-1)
#	midimum: float =     .5
	maximum: float =    1.
	optimum: float = maximum

	def __add__(self, value: float, /) -> typing.Self:
		return self.__class__(self.dist + self.__class__(value).dist)

	def __and__(self, value: float, /) -> typing.Self:
		return self * value

	def  __or__(self, value: float, /) -> typing.Self:
		return ~(~self & ~self.__class__(value))

	def __neg__(self, /) -> typing.Self:
		return self.__class__(1 - self)


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


logical: typing.TypeAlias = real | dist | prob
