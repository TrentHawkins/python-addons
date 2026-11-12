import abc

from .. import Extensible


class Equivalence(Extensible, abc.ABC):

	@abc.abstractmethod
	def __hash__(self) -> int:
		...

	def __eq__(self, other: Equivalence, /) -> bool: return not self != other
	def __ne__(self, other: Equivalence, /) -> bool: return not self == other
