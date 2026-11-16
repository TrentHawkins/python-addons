import abc

from . import Equivalence


class Partial(Equivalence, abc.ABC):

	def __le__(self, other: Partial, /) -> bool: return other >= self
	def __ge__(self, other: Partial, /) -> bool: return other <= self

	def __eq__(self, other: Partial, /) -> bool: return self <= other and self >= other
	def __lt__(self, other: Partial, /) -> bool: return self <= other and self != other
	def __gt__(self, other: Partial, /) -> bool: return self >= other and self != other


class Total(Partial, abc.ABC):

	def __lt__(self, other: Total, /) -> bool: return not self >= other
	def __gt__(self, other: Total, /) -> bool: return not self <= other
