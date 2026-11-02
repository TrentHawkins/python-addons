from typing import Self
from . import Preorder
class Partial(Preorder):
	"""A preorder that is antisymmetric, so equality is derived from the order rather than declared."""
	def __eq__(self, other: Self, /) -> bool: return self <= other and self >= other  # a = b iff a <= b and a >= b
	def __lt__(self, other: Self, /) -> bool: return self <= other and self != other  # a < b iff a <= b and a != b
	def __gt__(self, other: Self, /) -> bool: return self >= other and self != other  # a > b iff a >= b and a != b
