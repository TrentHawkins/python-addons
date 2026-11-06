from __future__ import annotations


import collections
import json
import operator
import typing

from . import Bool


type binary[T] = typing.Callable[[T, T], T]


class Set[I: typing.Hashable](collections.defaultdict[I, Bool]):

	default: Bool


	def __init__(self, items: typing.Iterable[I] | typing.Mapping[I, Bool] = (),
		complement: Bool | None = None,
	):
		self.default = complement if complement is not None else items.default if isinstance(items, Set) else Bool.max()

		if not isinstance(items, typing.Mapping):
			items = dict.fromkeys(items, ~self.default)

		super().__init__(lambda: self.default, items)

	def __iter__(self):
		for key, value in self.items():
			if value != self.default:
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

	def __invert__(self) -> typing.Self:
		cls = type(self)

		return cls({key: ~value for key, value in self.items()},
			complement = ~self.default,
		)

	def  __or__ (self, value: typing.Self | Bool) -> typing.Self: return self.operate(value, operator.or_ )
	def  __and__(self, value: typing.Self | Bool) -> typing.Self: return self.operate(value, operator.and_)
	def  __sub__(self, value: typing.Self | Bool) -> typing.Self: return self.operate(value, operator.sub )
	def  __xor__(self, value: typing.Self | Bool) -> typing.Self: return self.operate(value, operator.xor )

	def __ror__ (self, value: typing.Self | Bool) -> typing.Self: return self | value
	def __rand__(self, value: typing.Self | Bool) -> typing.Self: return self & value
	def __rxor__(self, value: typing.Self | Bool) -> typing.Self: return self ^ value
	def __rsub__(self, value: typing.Self | Bool) -> typing.Self:
		return self.operate(value, lambda left, right: right - left)


	def get(self, key: I) -> Bool:
		return super().get(key, self.default)

	def setdefault(self, key: I) -> Bool:
		return super().setdefault(key, self.default)

	def add(self, item: I) -> None:
		self[item] = Bool.min()

	def remove(self, item: I) -> None:
		if item not in self:
			raise KeyError(item)

		self.discard(item)

	def discard(self, item: I) -> None:
		self[item] = Bool.max()

	def operate(self, value: typing.Self | Bool,
		operation: binary[Bool],
	) -> typing.Self:
		cls = type(self)

		if isinstance(value, Bool):
			items = {key: operation(member, value) for key, member in self.items()}
			default = operation(self.default, value)

		else:
			items = {key: operation(self[key], value[key]) for key in self.keys() | value.keys()}
			default = operation(self.default, value.default)

		return cls(items,
			complement = default,
		)
