from typing import Self
from . import Magma, Group
class Abelian(Magma):
	"""A magma whose operation is commutative, which licenses the reflected form."""
	def __radd__(self, other: Self, /) -> Self:
		return self + other  # b + a = a + b
class AbelianGroup(Abelian, Group):
	"""A group that is also abelian; the mixin comes first so that its reflected form is found first."""
