from __future__ import annotations


from collections import defaultdict
from typing import Hashable, Iterable, Mapping, Self


class index[I: Hashable](defaultdict[I, bool]):

	def __init__(self, items: Iterable[I] | Mapping[I, bool] = (), complement: bool | None = None):
		self.complement = complement if complement is not None else items.complement if isinstance(items, index) else False

		if not isinstance(items, Mapping):
			items = dict.fromkeys(items, not self.complement)

		super().__init__(lambda: self.complement, items)

	def __iter__(self):
		for key, value in self.items():
			if value is not self.complement:
				yield key

	def __repr__(self) -> str:
		return ("~" if self.complement else "") + repr(set(self))

	def __bool__(self) -> bool:
		return self.complement or any(self.values())

	def __len__(self) -> int:
		return sum(value is not self.complement for value in self.values())

	def __contains__(self, item: I) -> bool:
		return self[item]

	def __invert__(self) -> Self:
		cls = type(self)

		return cls({key: not value for key, value in self.items()},
			complement = not self.complement,
		)

	def __or__(self, value: Self) -> Self:
		cls = type(self)

		return cls({key: self[key] or value[key] for key in self.keys() | value.keys()},
			complement = self.complement or value.complement,
		)

	def __and__(self, value: Self) -> Self:
		cls = type(self)

		return cls({key: self[key] and value[key] for key in self.keys() | value.keys()},
			complement = self.complement and value.complement,
		)

	def __sub__(self, value: Self) -> Self:
		cls = type(self)

		return cls({key: self[key] and not value[key] for key in self.keys() | value.keys()},
			complement = self.complement and not value.complement,
		)

	def __xor__(self, value: Self) -> Self:
		cls = type(self)

		return cls({key: self[key] is not value[key] for key in self.keys() | value.keys()},
			complement = self.complement is not value.complement,
		)

	def get(self, key: I) -> bool:
		return super().get(key, self.complement)

	def setdefault(self, key: I) -> bool:
		return super().setdefault(key, self.complement)

	def add(self, item: I) -> None:
		self[item] = True

	def remove(self, item: I) -> None:
		if item not in self:
			raise KeyError(item)

		self.discard(item)

	def discard(self, item: I) -> None:
		self[item] = False
