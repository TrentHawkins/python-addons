from __future__ import annotations


from math import gcd
from typing import Self


class scalar:

	__slots__ = (
		"numer",
		"denom",
	)

	numer: int
	denom: int


	def __new__(cls,
		numer: int = 0,
		denom: int = 1, /
	) -> Self:
		if numer < 0 \
		or denom < 0:
			raise ValueError

		if not denom:
			numer = 1

		norm = gcd(
			numer,
			denom,
		)

		self = super().__new__(cls)

		super(scalar, self).__setattr__("numer", numer // norm)
		super(scalar, self).__setattr__("denom", denom // norm)

		return self

	def __setattr__(self, name: str, value: int) -> None: raise AttributeError
	def __delattr__(self, name: str            ) -> None: raise AttributeError
