import abc


class Extensible(abc.ABC):

	@abc.abstractmethod
	def __hash__(self) -> int:
		...
