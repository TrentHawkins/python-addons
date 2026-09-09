from typing import Self

from .partial import Partial


class Total(Partial):

	def __lt__(self, other: Self, /) -> bool:
		return not other <= self
