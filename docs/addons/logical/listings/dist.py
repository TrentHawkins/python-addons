import math


class Dist:

	numer: int
	denom: int


	def __init__(self,
		numer: int,
		denom: int,
	):
		if numer < 0: raise ValueError
		if denom < 0: raise ValueError

		norm = math.gcd(
			numer,
			denom,
		)

		self.numer = numer // norm
		self.denom = denom // norm


	def __repr__(self) -> str:
		return f"{self.numer}/{self.denom}"

	def __hash__(self) -> int:
		return hash(
			(
				self.numer,
				self.denom,
			)
		)


	def __eq__(self, other: Dist) -> bool: return self.numer * other.denom == self.denom * other.numer
	def __le__(self, other: Dist) -> bool: return self.numer * other.denom <= self.denom * other.numer
	def __ge__(self, other: Dist) -> bool: return self.numer * other.denom >= self.denom * other.numer

	def __ne__(self, other: Dist) -> bool: return not self == other
	def __lt__(self, other: Dist) -> bool: return not self >= other
	def __gt__(self, other: Dist) -> bool: return not self <= other
