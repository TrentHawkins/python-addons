# `python-addons`

`python-addons` provides foundational Python value types whose supported
operations form an explicit part of their contract.

The project is currently experimental and requires Python 3.14 or newer.

## Distribution and import names

The installable distribution is named `python-addons`, so downstream projects
declare it by that name:

```toml
[project]
dependencies = ["python-addons>=0.1"]
```

The Python import package is named `addons`:

```python
from addons import Float, Int
```

Keeping these names distinct lets the distribution retain the descriptive
project name while the import remains short.

## Nonnegative numeric carriers

The first two value types use composition over Python's builtin `int` and
`float`. They deliberately expose a small, monoid-like algebra rather than the
complete builtin numeric interface.

```python
from addons import Float, Int


two = Int(2)
three = Int(3)

two + three                 # 5, as Int
two * three                 # 6, as Int
Int.sum([two, three])       # 5, as Int
Int.prod([two, three])      # 6, as Int

Float.sum([])               # 0.0, as Float
Float.prod([])              # 1.0, as Float
```

Both carriers currently support:

- nonnegative construction;
- addition and multiplication;
- unary `+` and `abs`;
- equality and ordered comparisons;
- truth testing and explicit `int`/`float` conversion;
- additive and multiplicative identities through `zero()` and `unit()`;
- ordered class-level reductions through `sum()` and `prod()`.

Subtraction, negation, division, powers, reflected arithmetic, and implicit
cross-carrier promotion are intentionally absent.

### Strict carrier operations

Arithmetic is defined only between values with the same exact dynamic class.
Unsupported operands return `NotImplemented` to Python's operator protocol and
normally end in `TypeError`:

```python
Int(1) + 1               # TypeError
Int(1) + Float(1)        # TypeError
```

Class identities and results preserve subclasses:

```python
class Count(Int):
    pass


type(Count(2) + Count(3)) is Count
type(Count.sum([])) is Count
```

`cast()` is exact-class idempotent. It returns an existing value only when its
dynamic class is precisely the requested class; otherwise it reconstructs the
requested carrier.

The class reducers seed their folds with carrier-valued identities, so they do
not need permissive reflected operations solely to interoperate with builtin
`sum` or `math.prod`.

### Float semantics

`Float` delegates arithmetic to builtin IEEE-style floating-point operations
and provides `Float.nan()` and `Float.inf()`. NaN is not reflexively equal and
floating-point arithmetic is not mathematically associative, so `Float` is an
operational monoid-like carrier rather than a law-perfect mathematical monoid.

### Mutability status

Instances are intended to be treated as immutable value objects, but that
contract is currently conventional rather than enforced. In particular,
internal state must not be changed after an instance has been used as a
dictionary key or set member.

## Logical values and indexed sets

`Bool`, `Prob`, `Dist`, and `Real` are compatible representations of logical
strength. `Prob` uses `[0, 1]`, while `Dist` uses odds against success:

```text
p = 1 / (1 + d)
d = (1 - p) / p
```

This gives the endpoints a useful graph interpretation: probability `0` is an
absent edge at infinite difficulty, and probability `1` is a zero-difficulty
edge. Distance addition is transported to `Prob.__add__`, so `+` extends a path
without leaving probability representation.

`IndexSet` and `FuzzySet` lift the same pointwise algebra to indexed
membership:

```python
from addons import FuzzySet, IndexSet


neighbors = IndexSet({"b", "c"})
bool(neighbors["b"])            # True
bool(neighbors["missing"])      # False

weights = FuzzySet({"b": 0.8})
float(weights["b"])             # 0.8
float(weights["missing"].dist)  # inf
```

The mapping backend retains explicit coverage, while every missing key obtains
the algebraic default. Complement flips that default, making `~set_value` an
effective representation of a complement without materializing a universe.
Raw values are normalized through the declared truth carrier, including in
nested set structures.

The generic `Set[K, T, V = T]` supports recursive relations: `K` is the index,
`V` the stored membership type, and `T` the terminal truth returned by recursive
comparison or measurement. This is sufficient for a later `Graph[I, T]` layer
to hide crisp or fuzzy neighborhood carriers without fixing the universe of
possible weights today.

See [Logical values and indexed sets](docs/logical-foundations.md) for the
coordinate formulas, operator authorities, complement semantics, typing model,
and the graph-shaped acceptance example.

## Project layout

```text
src/
└── addons/
    ├── __init__.py
    ├── base.py
    ├── logical.py
    └── py.typed
tests/
└── test_logical.py
```

The package ships inline type information and is checked with Pyright.

Useful development commands:

```console
uv sync --all-groups
uv run pyright
uv run pytest
uv build
```
