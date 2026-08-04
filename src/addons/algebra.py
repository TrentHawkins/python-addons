from __future__ import annotations


import typing


class Equivalence(typing.Protocol):

	def __eq__(self, other: object     , /) -> bool: ...
	def __ne__(self, other: object     , /) -> bool: ...


class PartialOrdering(typing.Protocol):

	def __le__(self, other: typing.Self, /) -> bool: ...
	def __ge__(self, other: typing.Self, /) -> bool: ...


class StrictPartialOrdering(typing.Protocol):

	def __lt__(self, other: typing.Self, /) -> bool: ...
	def __gt__(self, other: typing.Self, /) -> bool: ...


class TotalOrdering(PartialOrdering, StrictPartialOrdering, Equivalence, typing.Protocol):

	...

class MeetSemilattice(PartialOrdering, typing.Protocol):

	def __and__(self, other: typing.Self, /) -> typing.Self: ...


class JoinSemilattice(PartialOrdering, typing.Protocol):

	def __or__ (self, other: typing.Self, /) -> typing.Self: ...


class Lattice(
	JoinSemilattice,
	MeetSemilattice, PartialOrdering, typing.Protocol
):

	...


class Boolean(Lattice, typing.Protocol):

	def __invert__(self, /) -> typing.Self:
		...


class AddSemigroup(typing.Protocol):

	def __add__(self, other: typing.Self, /) -> typing.Self:
		...

	def __pos__(self) -> typing.Self:
		...


class AddGroup(AddSemigroup, typing.Protocol):

	def __sub__(self, other: typing.Self, /) -> typing.Self:
		...

	def __neg__(self) -> typing.Self:
		...


class MulSemigroup(typing.Protocol):

	def __mul__(self, other: typing.Self, /) -> typing.Self:
		...


class MulGroup(MulSemigroup, typing.Protocol):

	def __truediv__(self, other: typing.Self, /) -> typing.Self:
		...


class Semiring(
	AddSemigroup,
	MulSemigroup, typing.Protocol
):

	...


class Ring(Semiring, AddGroup, typing.Protocol):

	...


class Pairing[Scalar: Semiring](typing.Protocol):

	def __matmul__(self, other: typing.Self, /) -> Scalar:
		...


class Field(
	AddGroup,
	MulGroup, typing.Protocol
):

	...


class Semimodule[Scalar: Semiring](AddSemigroup, typing.Protocol):

	def __mul__(self, scalar: Scalar, /) -> typing.Self:
		...

#	def __rmul__(self, scalar: Scalar, /) -> typing.Self:
#		...


class Module[Scalar: Ring](Semimodule[Scalar], AddGroup, typing.Protocol):

	...


class Vector[Scalar: Field](Module[Scalar], typing.Protocol):

	...


class Magnitude(Semiring, TotalOrdering, typing.Protocol):

	def __abs__(self) -> typing.Self:
		...


class Involutive(typing.Protocol):

#	@property
#	def real(self) -> typing.Self:
#		...

#	@property
#	def imag(self) -> typing.Self:
#		...

	def conjugate(self) -> typing.Self:
		...


class Matrix[Scalar: Field](Vector[Scalar], Involutive, typing.Protocol):

	@typing.overload
	def __matmul__(self, other: typing.Self, /) -> typing.Self:
		...

	@typing.overload
	def __matmul__(self, other: Vector[Scalar], /) -> Vector[Scalar]:
		...

	def __matmul__(self, other: typing.Self | Vector[Scalar], /) -> typing.Self | Vector[Scalar]:
		...

#	@typing.overload
#	def __rmatmul__(self, other: typing.Self, /) -> typing.Self:
#		...

#	@typing.overload
#	def __rmatmul__(self, other: Vector[Scalar], /) -> Vector[Scalar]:
#		...

#	def __rmatmul__(self, other: typing.Self | Vector[Scalar], /) -> typing.Self | Vector[Scalar]:
#		...


class Numeric(
	typing.SupportsInt,
	typing.SupportsFloat,
#	typing.SupportsComplex,
	typing.SupportsAbs,
#	typing.SupportsRound,
	typing.Hashable,
	typing.Protocol,
):

	...
