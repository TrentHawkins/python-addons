from abc import ABC
from typing import Self
class Preorder(ABC):
	"""A reflexive and transitive relation; a carrier writes either method and the other reflects it."""
	def __le__(self, other: Self, /) -> bool: return other >= self  # a <= b is b >= a
	def __ge__(self, other: Self, /) -> bool: return other <= self  # a >= b is b <= a
