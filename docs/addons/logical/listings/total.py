from typing import Self
from . import Partial
class Total(Partial):
	"""A partial order in which any two elements compare, so each strict form is a negation."""
	def __lt__(self, other: Self, /) -> bool: return not self >= other  # a < b iff not a >= b
	def __gt__(self, other: Self, /) -> bool: return not self <= other  # a > b iff not a <= b
