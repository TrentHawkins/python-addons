from __future__ import annotations

from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class SupportsMeet(Protocol):
    def meet(self, other: object) -> object:
        ...


@runtime_checkable
class SupportsJoin(Protocol):
    def join(self, other: object) -> object:
        ...


@runtime_checkable
class SupportsComplement(Protocol):
    def complement(self) -> object:
        ...


def meet(left: T, right: T) -> T:
    if isinstance(left, SupportsMeet):
        return left.meet(right)  # type: ignore[return-value]
    if isinstance(right, SupportsMeet):
        return right.meet(left)  # type: ignore[return-value]
    if isinstance(left, AbstractSet) and isinstance(right, AbstractSet):
        return left.intersection(right)  # type: ignore[return-value]
    return min(left, right)


def join(left: T, right: T) -> T:
    if isinstance(left, SupportsJoin):
        return left.join(right)  # type: ignore[return-value]
    if isinstance(right, SupportsJoin):
        return right.join(left)  # type: ignore[return-value]
    if isinstance(left, AbstractSet) and isinstance(right, AbstractSet):
        return left.union(right)  # type: ignore[return-value]
    return max(left, right)


def complement(value: T) -> T:
    if isinstance(value, SupportsComplement):
        return value.complement()  # type: ignore[return-value]
    raise TypeError(f"{type(value).__name__} does not define a complement")


class LogicInt(int):
    def __new__(cls, value: int | bool) -> "LogicInt":
        integer = int(value)
        if integer not in (0, 1):
            raise ValueError("LogicInt only accepts 0 or 1")
        return super().__new__(cls, integer)

    def meet(self, other: object) -> "LogicInt":
        return type(self)(min(int(self), int(LogicInt(other))))  # type: ignore[arg-type]

    def join(self, other: object) -> "LogicInt":
        return type(self)(max(int(self), int(LogicInt(other))))  # type: ignore[arg-type]

    def complement(self) -> "LogicInt":
        return type(self)(1 - int(self))

    def __invert__(self) -> "LogicInt":
        return self.complement()


class Probability(float):
    def __new__(cls, value: float | int) -> "Probability":
        numeric = float(value)
        if not 0.0 <= numeric <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        return super().__new__(cls, numeric)

    @classmethod
    def _coerce(cls, value: object) -> "Probability":
        return value if isinstance(value, cls) else cls(value)  # type: ignore[arg-type]

    def meet(self, other: object) -> "Probability":
        candidate = type(self)._coerce(other)
        return type(self)(float(self) * float(candidate))

    def join(self, other: object) -> "Probability":
        candidate = type(self)._coerce(other)
        return type(self)(float(self) + float(candidate) - (float(self) * float(candidate)))

    def complement(self) -> "Probability":
        return type(self)(1.0 - float(self))

    def __invert__(self) -> "Probability":
        return self.complement()


U = TypeVar("U")


@dataclass(frozen=True)
class BoundedSet(Generic[U]):
    members: frozenset[U]
    universe: frozenset[U]

    def __init__(self, members: AbstractSet[U] | frozenset[U], universe: AbstractSet[U] | frozenset[U]):
        frozen_members = frozenset(members)
        frozen_universe = frozenset(universe)
        if not frozen_members.issubset(frozen_universe):
            raise ValueError("members must be a subset of universe")
        object.__setattr__(self, "members", frozen_members)
        object.__setattr__(self, "universe", frozen_universe)

    def meet(self, other: object) -> "BoundedSet[U]":
        candidate = self._coerce(other)
        self._validate_shared_universe(candidate)
        return type(self)(self.members.intersection(candidate.members), self.universe)

    def join(self, other: object) -> "BoundedSet[U]":
        candidate = self._coerce(other)
        self._validate_shared_universe(candidate)
        return type(self)(self.members.union(candidate.members), self.universe)

    def complement(self) -> "BoundedSet[U]":
        return type(self)(self.universe.difference(self.members), self.universe)

    def _coerce(self, other: object) -> "BoundedSet[U]":
        if not isinstance(other, BoundedSet):
            raise TypeError("expected BoundedSet")
        return other

    def _validate_shared_universe(self, other: "BoundedSet[U]") -> None:
        if self.universe != other.universe:
            raise ValueError("bounded sets must share a universe")
