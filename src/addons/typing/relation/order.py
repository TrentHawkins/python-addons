import abc

from . import Equivalence


class Pre(Equivalence, abc.ABC):

	@abc.abstractmethod
	def __hash__(self) -> int:
		...

	def __eq__(self, other: Pre, /) -> bool: return self <= other and self >= other
	def __lt__(self, other: Pre, /) -> bool: return self <= other and self != other
	def __gt__(self, other: Pre, /) -> bool: return self >= other and self != other

	def __le__(self, other: Pre, /) -> bool: return self < other or self == other
	def __ge__(self, other: Pre, /) -> bool: return self > other or self == other


class Partial(Pre, abc.ABC):

	@abc.abstractmethod
	def __hash__(self) -> int:
		...

	def __eq__(self, other: Partial, /) -> bool: return hash(self) == hash(other)


class Total(Partial, abc.ABC):

	def __lt__(self, other: Total, /) -> bool: return not self >= other
	def __gt__(self, other: Total, /) -> bool: return not self <= other
