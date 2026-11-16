import abc


class Equivalence(abc.ABC):

	def __eq__(self, other: Equivalence, /) -> bool: return not self != other
	def __ne__(self, other: Equivalence, /) -> bool: return not self == other
