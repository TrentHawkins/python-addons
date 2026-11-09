from __future__ import annotations


import functools
import json

from collections import defaultdict
from operator import (
	or_  as join,
	and_ as meet,
	sub  as diff,
	xor  as symd,
)
from typing import (
	Hashable,
	Callable,
	Iterable,
	Mapping,
	Self,
)

from . import Bool


type binary[T, S = T] = Callable[[T, S], T]
type operand[T] = Iterable[T] | Mapping[T, Bool] | Bool

class Set[I: Hashable](defaultdict[I, Bool]):

	default: Bool


	def __init__(self, items: operand[I] = (),
		default: Bool | None = None,
	):
		if isinstance(items, Bool):
			default = items if default is None else default
			items = ()

		default = default if default is not None else items.default if isinstance(items, Set) else Bool.max()

		if not isinstance(items, Mapping):
			items = dict.fromkeys(items, ~default)

		self.default = default

		super().__init__(lambda: self.default, items)

	def __iter__(self):
		for key, other in self.items():
			if other != self.default:
				yield key

	def __repr__(self) -> str:
		return json.dumps(self,
			default = float,
			indent = 4,
		)

	def __bool__(self) -> bool:
		return bool(self.default) or any(self.values())

	def __len__(self) -> int:
		return sum(True for _ in self)

	def __contains__(self, item: I) -> bool:
		return bool(self[item])

	def __invert__(self) -> Self:
		cls = type(self)

		return cls({key: ~other for key, other in self.items()},
			default = ~self.default,
		)

	def  __or__ (self, other: operand[I]) -> Self: return self.operate(other, join)
	def  __and__(self, other: operand[I]) -> Self: return self.operate(other, meet)
	def  __sub__(self, other: operand[I]) -> Self: return self.operate(other, diff)
	def  __xor__(self, other: operand[I]) -> Self: return self.operate(other, symd)

	def __ror__ (self, other: operand[I]) -> Self: return self | other
	def __rand__(self, other: operand[I]) -> Self: return self & other
	def __rxor__(self, other: operand[I]) -> Self: return self ^ other
	def __rsub__(self, other: operand[I]) -> Self:
		return self.operate(other, lambda left, right: right - left)

	def __ior__ (self, other: operand[I]) -> Self: self.update                     (other); return self
	def __iand__(self, other: operand[I]) -> Self: self.intersection_update        (other); return self
	def __isub__(self, other: operand[I]) -> Self: self.difference_update          (other); return self
	def __ixor__(self, other: operand[I]) -> Self: self.symmetric_difference_update(other); return self


	def get(self, key: I) -> Bool:
		return super().get(key, self.default)

	def setdefault(self, key: I) -> Bool:
		return super().setdefault(key, self.default)

	def union       (self, *others: operand[I]) -> Self: return self.reduce(join, *others)
	def intersection(self, *others: operand[I]) -> Self: return self.reduce(meet, *others)
	def difference  (self, *others: operand[I]) -> Self: return self.reduce(diff, *others)

	def symmetric_difference(self, other: operand[I]) -> Self:
		return self ^ other

	def                      update(self, *others: operand[I]): self.become(self.               union(*others))
	def         intersection_update(self, *others: operand[I]): self.become(self.        intersection(*others))
	def           difference_update(self, *others: operand[I]): self.become(self.          difference(*others))
	def symmetric_difference_update(self,  other : operand[I]): self.become(self.symmetric_difference( other ))

	def add(self, item: I):
		self[item] = Bool.min()

	def remove(self, item: I):
		if item not in self:
			raise KeyError(item)

		self.discard(item)

	def discard(self, item: I):
		self[item] = Bool.max()

	def copy(self) -> Self:
		cls = type(self)
		return cls(self)

	def clear(self) -> None:
		super().clear()

		self.default = Bool.max()

	def become(self, other: Self):
		if other is self:
			return

		self.default = other.default

		super().clear()
		super().update(other)

	def operate(self, other: operand[I],
		operation: binary[Bool],
	) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: operation(self[key], other[key]) for key in self.keys() | other.keys()},
			default = operation(self.default, other.default),
		)

	def reduce(self, operation: binary[Self, operand[I]],
		*others: operand[I]
	) -> Self:
		cls = type(self)

		return functools.reduce(operation, others, cls(self))
