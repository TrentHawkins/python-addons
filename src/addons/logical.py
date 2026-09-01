from __future__ import annotations


from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from functools import partial, reduce
from itertools import permutations
from math import gcd, inf
from operator import eq, ge, le
from typing import Self, cast, final


type pair[T] = tuple[T, T]
type frozenlist[T] = tuple[T, ...]


class Bounded(ABC):

	@classmethod
	@abstractmethod
	def minimum(cls) -> Self:
		...

	@classmethod
	@abstractmethod
	def maximum(cls) -> Self:
		...


class Invertible(ABC):

	@abstractmethod
	def __invert__(self) -> Self:
		...


class Operable(Invertible, Bounded):

	def  __or__(self, other: Operable, /) -> Self: return ~(~self & ~other)
	def __and__(self, other: Operable, /) -> Self: return ~(~self | ~other)
	def __sub__(self, other: Operable, /) -> Self: return    self & ~other
	def __xor__(self, other: Operable, /) -> Self:
		return (self | other) - (self & other)
	#	return (self - other) | (other - self)

	def  __ror__(self, other: Operable, /) -> Self: return self | other
	def __rand__(self, other: Operable, /) -> Self: return self & other
	def __rxor__(self, other: Operable, /) -> Self: return self ^ other

	@final
	def union(self, *others: Operable) -> Self:
		cls = type(self)

		return reduce(cls.__or__, others, self)

	@final
	def intersection(self, *others: Operable) -> Self:
		cls = type(self)

		return reduce(cls.__and__, others, self)

	@final
	def difference(self, *others: Operable) -> Self:
		cls = type(self)

		return reduce(cls.__sub__, others, self)

	@final
	def symmetric_difference(self, other: Operable, /) -> Self:
		return self ^ other

	@final
	@classmethod
	def any(cls, others: Iterable[Operable], /) -> Self:
		return cls.maximum().union(*others)
	#	return reduce(cls.__or__, others, cls.maximum())

	@final
	@classmethod
	def all(cls, others: Iterable[Operable], /) -> Self:
		return cls.minimum().intersection(*others)
	#	return reduce(cls.__and__, others, cls.minimum())


class Additive(Bounded):

	@abstractmethod
	def __add__(self, other: Additive, /) -> Self:
		...

	@abstractmethod
	def __mul__(self, times: int, /) -> Self:
		...

	def __radd__(self, other: Additive, /) -> Self: return self + other
	def __rmul__(self, other: int     , /) -> Self: return self * other

	@final
	@classmethod
	def sum(cls, others: Iterable[Additive], /) -> Self:
		return sum(others, cls.minimum())  # pyright: ignore[reportReturnType]
	#	return reduce(cls.__add__, others, cls.minimum())


class Order(ABC):

	@abstractmethod
	def __le__(self, other: Order, /) -> bool:
		...

	@abstractmethod
	def __ge__(self, other: Order, /) -> bool:
		...

	def __ne__(self, other: Order, /) -> bool:
		return not self == other

	def __eq__(self, other: Order, /) -> bool: return self <= other and self >= other
	def __lt__(self, other: Order, /) -> bool: return self <= other and self != other
	def __gt__(self, other: Order, /) -> bool: return self >= other and self != other

	@final
	def issubset  (self, other: Order, /) -> bool:
		return self <= other

	@final
	def issuperset(self, other: Order, /) -> bool:
		return self >= other


class Partial(Order):

	def __le__(self, other: Order, /) -> bool: return other >= self
	def __ge__(self, other: Order, /) -> bool: return other <= self


class Total(Order):

	def __le__(self, other: Order, /) -> bool: return not self > other
	def __gt__(self, other: Order, /) -> bool: return     other < self

	def __lt__(self, other: Order, /) -> bool: return not self >= other
	def __ge__(self, other: Order, /) -> bool: return     other <= self


class Separable(Operable, ABC):

	@abstractmethod
	def __bool__(self) -> bool:
		...

	@final
	def isdisjoint(self, other: Operable) -> bool:
		return not (self & other)


class Boolean[T: Coded = Coded](Separable, Additive, Order, ABC):  # pylint: disable=used-before-assignment

	@abstractmethod
	def __abs__(self) -> T:
		...


class Coded(Boolean, ABC):

	@classmethod
	@abstractmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
		...

	@abstractmethod
	def decode(self) -> pair[int]:
		...

	@final
	@property
	def decoded(self) -> pair[int]:
		return self.decode()


type Coordinate[K: Hashable] = K | None | slice
type Address[K: Hashable] = Coordinate[K] | tuple[Coordinate[K], ...]


class Path[K: Hashable](tuple[Coordinate[K], ...]):

	def __new__(cls, *coordinates: Coordinate[K]) -> Self:
		for coordinate in coordinates:
			if isinstance(coordinate, slice) and coordinate != slice(None):
				raise KeyError(f"only an unbounded slice contracts an axis, not {coordinate!r}")

		return super().__new__(cls, coordinates)

	def __getnewargs__(self) -> tuple[Coordinate[K], ...]:
		return tuple(self)

	@classmethod
	def read(cls, key: Address[K], /) -> Path[K]:
		return key if isinstance(key, Path) else cls(*key) if isinstance(key, tuple) else cls(key)

	@classmethod
	def contracts(cls, coordinate: Coordinate[K], /) -> bool:
		return coordinate is None or isinstance(coordinate, slice)

	@property
	def contracting(self) -> bool:
		return any(map(self.contracts, self))


class Edge[K: Hashable](Path[K]):

	@property
	def permutations(self) -> set[Self]:
		cls = type(self)

		return {cls(*keys) for keys in permutations(self)}


type NodeLike[K: Hashable, V: Boolean] = Iterable[Address[K]] | Mapping[Address[K], V] | V
type Operator[V: Boolean] = Callable[[V, V], V]
type Relation = Callable[[Boolean, Boolean], bool]


class Frac(Coded, Total, ABC):

	numer: int
	denom: int

	def __new__(cls,
		numer: int | Boolean = 0,
		denom: int           = 1, /
	) -> Self:
		if isinstance(numer, cls):
			return numer

		if isinstance(numer, bool):
			return cls.encode(*((0, 1) if numer else (1, 0)))

		if isinstance(numer, Boolean):
			return cls.encode(*abs(numer).decode())

		self = super().__new__(cls)

		greatest_common_divisor = gcd(
			numer,
			denom,
		)

		self.numer = numer // greatest_common_divisor
		self.denom = denom // greatest_common_divisor

		return self

	def __repr__(self) -> str:
		return repr(float(self))

	def __hash__(self) -> int:
		return hash(self.decode())

	def __bool__(self) -> bool:
		_, b = self.decode()

		return bool(b)

	def __float__(self) -> float:
		return self.numer / self.denom if self.denom else inf

	def __add__(self, other: int | Boolean, /) -> Self: cls = type(self); return cls(Dist(self) + Dist(other))
	def __mul__(self, times: int          , /) -> Self: cls = type(self); return cls(Dist(self) *      times )
	def __and__(self, other: int | Boolean, /) -> Self: cls = type(self); return cls(Prob(self) & Prob(other))

	def __invert__(self) -> Self: cls = type(self); a, b = self.decode(); return cls.encode(b, a)

	def __abs__(self) -> Self: cls = type(self); return cls(self)

	def __le__(self, other: object, /) -> bool: a, b = self.decode(); c, d = self.contract(other).decoded; return a * d >= c * b
	def __ge__(self, other: object, /) -> bool: a, b = self.decode(); c, d = self.contract(other).decoded; return a * d <= c * b

	@final
	@classmethod
	def contract(cls, other: object, /) -> Coded:
		return abs(other) if isinstance(other, Boolean) else cls(cast(int, other))

	@classmethod
	def minimum(cls) -> Self:
		return cls.encode(0, 1)

	@classmethod
	def midimum(cls) -> Self:
		return cls.encode(1, 1)

	@classmethod
	def maximum(cls) -> Self:
		return cls.encode(1, 0)


class Dist(Frac):

	def __new__(cls,
		numer: int | Boolean = 0,
		denom: int           = 1, /
	) -> Self:
		if not (numer or denom): numer = 1

		self = super().__new__(cls, numer, denom)

		if self.numer < 0 or self.denom < 0:
			raise ValueError(f"{self.numer} < 0 or {self.denom} < 0")

		return self

	def __add__(self, other: int | Boolean) -> Self:
		cls, other = type(self), Dist(other)

		return cls(
			other.numer * self.denom + self.numer * other.denom,
			              self.denom              * other.denom,
		)

	def __mul__(self, times: int) -> Self:
		cls = type(self)

		return cls(
			self.numer * times,
			self.denom,
		) if times else cls()

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
		return cls(numer, denom)

	def decode(self) -> pair[int]:
		return self.numer, self.denom


class Prob(Frac):

	def __new__(cls,
		numer: int | Boolean = 1,
		denom: int           = 1, /
	) -> Self:
		if not (numer or denom): denom = 1

		self = super().__new__(cls, numer, denom)

		if not 0 <= self.numer <= self.denom:
			raise ValueError(f"not 0 <= {self.numer} <= {self.denom}")

		return self

	def __and__(self, other: int | Boolean) -> Self:
		cls, other = type(self), Prob(other)

		return cls(
			self.numer * other.numer,
			self.denom * other.denom,
		)

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
		return cls(
			denom,
			denom + numer,
		)

	def decode(self) -> pair[int]:
		return (
			self.denom - self.numer,
			self.numer,
		)


class Bool(Frac):

	def __new__(cls, _: object = False, /) -> Self:
		decoded = (0, 1) if _ else (1, 0)

		return super().__new__(cls, *decoded)

	def __repr__(self) -> str:
		return repr(bool(self))

	@classmethod
	def encode(cls,
		numer: int,
		denom: int, /
	) -> Self:
		return cls(denom)

	def decode(self) -> pair[int]:
		return (
			self.numer,
			self.denom,
		)


class Node[K: Hashable, T: Coded = Bool, V: Boolean = T](Boolean[T], Partial, defaultdict[K , V]):

	truth: type[V]

	def __init_subclass__(cls, *args,
		truth: type[Boolean] | None = None,
	**kwargs):
		super().__init_subclass__(*args, **kwargs)

		if truth is not None:
			cls.truth = cast(type[V], truth)

	def __init__(self, iterable: NodeLike[K, V] = (), /, *,
		complement: bool | None = None,
	):
		background = not isinstance(iterable, Iterable)
		foreground =     isinstance(iterable, Node    )

		if complement is None:
			complement = iterable.complement if foreground else bool(iterable) if background else False

		if background:
			iterable = ()

		super().__init__(partial(self.truth, self.truth.minimum() if complement else self.truth.maximum()))

		items = iterable.items() if isinstance(iterable, Mapping) else ((key, ~self.default) for key in iterable)

		for key, value in items:
			self[key] = value

	def __repr__(self) -> str:
		shown = ~self if self.complement else self
		items = {key: value for key, value in shown.items() if value}

		body = repr(set(items)) if items and all(value == self.truth.minimum() for value in items.values()) else repr(items)

		return f"~{body}" if self.complement else body

	def __reduce__(self) -> tuple[Callable[[NodeLike[K, V]], Self], tuple[dict[K, V]]]:
		cls = type(self)

		factory = partial(cls,
			complement = self.complement,
		)

		return factory, (dict(self),)

	def __contains__(self, key: Address[K], /) -> bool:
		return bool(self[key])

	def __iter__(self, /) -> Iterator[K]:
		cls = type(self)

		if self.complement:
			raise TypeError(f"cannot iterate {cls.__qualname__} with implicit members")

		return (key for key, value in self.items() if value)

	def __bool__(self, /) -> bool:
		return self.complement or any(map(bool, self.values()))

	def __getitem__(self, key: Address[K], /) -> V:
		path = self.address(key)

		if not path:
			return cast(V, self)

		head, *rest = path
		value = self.contracted if Path.contracts(head) else cast(V, dict.__getitem__(self, cast(K, head)))

		return cast(Node[K, T, V], value)[Path(*rest)] if rest else value

	def __setitem__(self, key: Address[K], value: NodeLike[K, V] | int, /):
		holder, last = self.locate(key)

		dict.__setitem__(holder, last, holder.truth(value))  # pyright: ignore[reportCallIssue]

	def __delitem__(self, key: Address[K], /):
		holder, last = self.locate(key)

		dict.__delitem__(holder, last)

	def __abs__(self) -> T:
		return cast(T, ~sum((~abs(value) for value in self.values()), ~abs(self.default)))

	def __invert__(self) -> Self:
		cls = type(self)

		return cls({key: ~value for key, value in self.items()},
			complement = not self.complement,
		)

	def __mul__(self, times: int, /) -> Self:
		cls = type(self)

		return cls({key: self[key] * times for key in self.keys()},
			complement = bool(self.default * times),
		)

	def __add__(self, other: NodeLike[K, V], /) -> Self: cls = type(self); return self.operate(other, cls.truth.__add__)
	def __and__(self, other: NodeLike[K, V], /) -> Self: cls = type(self); return self.operate(other, cls.truth.__and__)
	def  __or__(self, other: NodeLike[K, V], /) -> Self: cls = type(self); return self.operate(other, cls.truth. __or__)
	def __sub__(self, other: NodeLike[K, V], /) -> Self: cls = type(self); return self.operate(other, cls.truth.__sub__)
	def __xor__(self, other: NodeLike[K, V], /) -> Self: cls = type(self); return self.operate(other, cls.truth.__xor__)

	def __ior__ (self, other: NodeLike[K, V], /) -> Self: self.update                     (other); return self
	def __iand__(self, other: NodeLike[K, V], /) -> Self: self.intersection_update        (other); return self
	def __isub__(self, other: NodeLike[K, V], /) -> Self: self.difference_update          (other); return self
	def __ixor__(self, other: NodeLike[K, V], /) -> Self: self.symmetric_difference_update(other); return self

	def __le__(self, other: NodeLike[K, V], /) -> bool: return self.relate(other, le)
	def __ge__(self, other: NodeLike[K, V], /) -> bool: return self.relate(other, ge)
	def __eq__(self, other: NodeLike[K, V], /) -> bool: return self.relate(other, eq)

	@classmethod
	def fromkeys(cls, iterable: Iterable[K], value: V | None = None, /) -> Self:
		return cls(iterable if value is None else dict.fromkeys(iterable, value))

	@classmethod
	def minimum(cls) -> Self:
		return cls(cls.truth.minimum())

	@classmethod
	def maximum(cls) -> Self:
		return cls(cls.truth.maximum())

	@classmethod
	def arity(cls) -> int:
		return 1

	@property
	def contracted(self) -> V:
		return cast(V, ~sum((~value for value in self.values()), ~self.default))

	@property
	def default(self) -> V:
		if (default := self.default_factory) is None:
			raise TypeError(f"{type(self).__qualname__}.default_factory() returned None, expected a value of type {V.__name__}")

		return default()

	@property
	def complement(self) -> bool:
		return bool(self.default)

	def address(self, key: Address[K], /) -> Path[K]:
		path = Path.read(key)

		if len(path) > self.arity():
			raise KeyError(f"{type(self).__qualname__} takes up to {self.arity()} coordinates, not {len(path)}")

		return path

	def locate(self, key: Address[K], /) -> tuple[Node[K, T, V], K]:
		path = self.address(key)

		if not path            : raise KeyError(f"{type(self).__qualname__} has no slot at an empty path")
		if     path.contracting: raise KeyError(f"{type(self).__qualname__} has no slot at a contracted axis: {key!r}")

		*head, last = path

		return cast(Node[K, T, V], self[Path(*head)]) if head else self, cast(K, last)

	def add    (self, key: Address[K], /): self[key] = self.truth.minimum()
	def discard(self, key: Address[K], /): self[key] = self.truth.maximum()
	def remove (self, key: Address[K], /):
		if key not in self:
			raise KeyError(key)

		self.discard(key)

	def pop(self, key: Address[K], default: V | None = None, /) -> V:
		holder, last = self.locate(key)

		if last in holder.keys():
			return cast(V, dict.pop(holder, last))

		if default is None:
			raise KeyError(key)

		return default

	def clear(self):
		self.become(self.maximum())

	def copy(self) -> Self:
		cls = type(self)

		return cls(self)

	__copy__ = copy

	def get(self, key: Address[K], default: V | None = None, /) -> V:
		holder, last = self.locate(key)

		return cast(V, dict.get(holder, last, holder.default if default is None else default))

	def setdefault(self, key: Address[K], default: V | None = None, /) -> V:
		holder, last = self.locate(key)

		if default is not None and last not in holder.keys(): self[key] = default

		return self[key]

	def update(self, *others: NodeLike[K, V]):
		cls = type(self)

		self.become(self.union(*map(cls, others)))

	def intersection_update(self, *others: NodeLike[K, V]):
		cls = type(self)

		self.become(self.intersection(*map(cls, others)))

	def difference_update(self, *others: NodeLike[K, V]):
		cls = type(self)

		self.become(self.difference(*map(cls, others)))

	def symmetric_difference_update(self, other: NodeLike[K, V], /):
		cls = type(self)

		self.become(self.symmetric_difference(cls(other)))

	def become(self, other: Self, /):
		items = dict(other)

		self.default_factory = other.default_factory

		dict.clear(self)
		dict.update(self, items)

	def operate(self, other: NodeLike[K, V], /, operator: Operator[V]) -> Self:
		cls = type(self)
		other = cls(other)

		return cls({key: operator(self[key], other[key]) for key in self.keys() | other.keys()},
			complement = bool(operator(self.default, other.default)),
		)

	def relate(self, other: NodeLike[K, V], /, relation: Relation) -> bool:
		cls = type(self)

		if isinstance(other, Boolean) and not isinstance(other, Node):
			return relation(abs(self), other)

		other = cls(other)

		return relation(self.default, other.default) and all(relation(self[key], other[key]) for key in self.keys() | other.keys())


class Set[V: Hashable, E: Coded = Bool](Node[V, E, "Set[V, E] | E"]):

	registry: pair[list[type[Set[V, E]]]] = (
		[],
		[],
	)

	def __init_subclass__(cls, *args,
		truth: type[Boolean] | None = None,
		weighted: bool | None = None,
		depth: int | None = None,
	**kwargs):
		rung = weighted is not None or depth is not None
		weighted, depth = bool(weighted), depth or 0
		registry = cls.registry[weighted]

		if rung and len(registry) != depth:
			held = 0 <= depth < len(registry)
			message = f"{registry[depth].__qualname__} already holds it" if held else f"only {len(registry)} rungs stand under it"

			raise TypeError(f"{cls.__name__} cannot take depth {depth}: {message}")

		if rung and truth is None:
			truth = registry[depth - 1] if depth else Prob if weighted else Bool

		super().__init_subclass__(*args,
			truth = truth,
		**kwargs)

		if rung:
			registry.append(cls)

	@classmethod
	def arity(cls) -> int:
		return 1 + cls.truth.arity() if issubclass(cls.truth, Set) else 1


class Undirected[K: Hashable, T: Coded = Bool, V: Boolean = T](Node[K, T, V]):

	def __setitem__(self, key: Address[K], value: NodeLike[K, V] | int, /):
		if isinstance(key, tuple):
			for edge in Edge(*key).permutations:
				super().__setitem__(edge, value)

		else:
			super().__setitem__(key, value)

	def __delitem__(self, key: Address[K], /):
		if isinstance(key, tuple):
			for edge in Edge(*key).permutations:
				super().__delitem__(edge)

		else:
			super().__delitem__(key)


class IndexSet[I: Hashable](Set[I, Bool],
	weighted = False,
	depth = 0,
):

	...


class FuzzySet[I: Hashable](Set[I, Prob],
	weighted = True,
	depth = 0,
):

	...


class UnweightedGraph[V: Hashable](Set[V, Bool],
	weighted = False,
	depth = 1,
):

	...


class Graph[V: Hashable](Set[V, Prob],
	weighted = True,
	depth = 1,
):

	...
