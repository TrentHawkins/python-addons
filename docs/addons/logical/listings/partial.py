from typing import Self

from .preorder import Preorder


class Partial(Preorder):

	def __eq__(self, other: Self, /) -> bool:
		return self <= other and other <= self

	def __lt__(self, other: Self, /) -> bool:
		return self <= other and self != other

	def __gt__(self, other: Self, /) -> bool:
		return other < self
