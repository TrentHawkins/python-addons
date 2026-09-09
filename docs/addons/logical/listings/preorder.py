from abc import ABC, abstractmethod
from typing import Self


class Preorder(ABC):

	@abstractmethod
	def __le__(self, other: Self, /) -> bool:
		...

	def __ge__(self, other: Self, /) -> bool:
		return other <= self
