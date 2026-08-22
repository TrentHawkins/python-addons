# Logical values and indexed sets

`addons.logical` models one logical strength in four compatible coordinates and
lifts that algebra pointwise to indexed sets. The design is intended to make
crisp and fuzzy relations share one representation without pretending that all
of their operations have the same numerical meaning.

## Coordinates

The active coordinate system is

```text
d = exp(-x)
p = 1 / (1 + d)

x = -log(d) = log(p) - log(1 - p)
d = (1 - p) / p
```

where:

- `Real` stores the extended-real score or logit `x`;
- `Dist` stores nonnegative difficulty `d`, the odds against success;
- `Prob` stores probability `p` in `[0, 1]`;
- `Bool` is the crisp restriction of `Prob` to `{0, 1}`.

Typed values retain their coordinate when passed to another constructor:

```python
from addons import Dist, Prob, Real

Prob(Dist(1))       # 0.5
Dist(Prob(0.5))     # 1.0
Real(Prob(0.5))     # 0.0
```

A bare `int` or `float` is interpreted directly in the target coordinate.
Conversions use endpoint-aware formulas; finite logits outside the exponential
range saturate at the appropriate extended endpoint instead of raising.
Negative zero is canonicalized to positive zero.

## Distinguished values

`minimum()` and `maximum()` follow difficulty order, not the raw numerical
ordering of every coordinate:

| Meaning | `Real` | `Dist` | `Prob` | `Bool` |
|---|---:|---:|---:|---:|
| best / certain / zero difficulty (`minimum`) | `+inf` | `0` | `1` | `True` |
| reference (`midimum`) | `0` | `1` | `0.5` | — |
| worst / absent / infinite difficulty (`maximum`) | `-inf` | `+inf` | `0` | `False` |

For indexed sets, `minimum()` is consequently the universal set and
`maximum()` is the empty set.

NaN has no independent logical meaning. Construction maps it to `maximum()`,
the absent or worst value in the requested coordinate. This also resolves
indeterminate transported endpoint forms such as `0 * inf` conservatively to
absence.

## Operation authority

Each operation has one authoritative coordinate and is transported to the
others:

| Operation | Authority | Meaning |
|---|---|---|
| `a + b` | `Dist` addition | consecutive path difficulty |
| `a * b` | `Dist` multiplication | multiplication in odds/difficulty space |
| `a & b` | `Prob` multiplication | independent probabilistic conjunction |
| `a \| b` | De Morgan dual of `&` | probabilistic disjunction |
| `~a` | `Prob`, as `1 - p` | logical complement |

Authority specifies the algebra, not a mandatory runtime call path. `Real` and
`Dist` use equivalent direct formulas where round-tripping through another
coordinate would lose range. For example, `~Real(-1000)` remains `Real(1000)`
even though converting the original score to `Prob` underflows to zero.

These distinctions matter away from Boolean endpoints. In particular,
`Prob.__mul__` is not ordinary multiplication of probabilities. It transports
distance multiplication, so its identity is `Prob.midimum()` (`0.5`). Ordinary
probabilistic conjunction belongs to `&`:

```text
p & q = p*q
p | q = 1 - (1-p)*(1-q)
```

Distance addition transports to the Hamacher product with parameter zero:

```text
p + q = p*q / (p + q - p*q)
```

with endpoints evaluated by their limits. Thus `Prob.minimum()` (`1`) is the
identity of path extension and `Prob.maximum()` (`0`) is an absent path.

Difference, symmetric difference, and the remaining set-like methods are
derived from complement, conjunction, and disjunction. The formulas agree with
ordinary Boolean algebra on `Bool`; intermediate probabilities intentionally
remain fuzzy.

## Fuzzy relations are values, not predicates

Comparisons on `Real`, `Dist`, and `Prob` return `Prob`. Comparisons on `Bool`
return `Bool`. They are relation strengths and should not be mistaken for crisp
ordering predicates.

Python necessarily calls `bool()` on a comparison result in `if`, sorting,
`min`, heaps, and similar machinery. Any nonzero probability then counts as
true, which is not a usable total order. Algorithms requiring a crisp cost
order should compare an explicit projection such as `float(weight.dist)`.
The fuzzy scalar classes are unhashable for the same reason: fuzzy equality
does not satisfy the equality contract required by hash tables. `Bool` retains
`int` hashing because its equality is crisp.

## Indexed sets

`Set[K, T, V = T]` is a `dict[K, V]` with a logical default:

- `K` is the index type;
- `V` is the membership value stored at each covered index;
- `T` is the terminal truth type returned after recursive measurement or
  comparison;
- `truth` is the concrete `V` carrier and the normalization boundary.

A finite set defaults to `truth.maximum()` (absence). A complemented set
defaults to `truth.minimum()` (presence). Explicit entries are retained even
when equal to the default; they record the set's known coverage. Complement
flips both every explicit value and the implicit default, so it is an effective
operation rather than a universe-dependent materialization.

```python
from addons import FuzzySet, IndexSet

crisp = IndexSet({"a", "b"})
bool(crisp["a"])          # True
bool(crisp["missing"])    # False

fuzzy = FuzzySet({"a": 0.8})
float(fuzzy["a"])         # 0.8
float(fuzzy["missing"])   # 0.0
float((~fuzzy)["missing"])  # 1.0
```

Mapping values are normalized through `truth.coerce` during construction,
assignment, `setdefault`, and `fromkeys`. Raw nested mappings therefore become
typed nested sets automatically.

### Views and iteration

- `value[key]` and `value.get(key)` return valued membership, including the
  implicit default;
- `key in value` converts that membership to a crisp Python `bool`;
- `value.indices` exposes all explicitly covered keys;
- `len(value)` counts those covered keys, not fuzzy cardinality;
- iteration yields explicitly covered keys whose membership is truthy;
- complemented sets cannot be iterated because they have implicit members
  outside the finite coverage map.

Consequently `set(IndexSet(...))` behaves as expected. For a nested adjacency
relation, an explicitly stored vertex with an empty neighborhood is present in
`.indices` but is not yielded by outer iteration. A separate vertex registry or
`.indices` should be used when isolated vertices matter.

`abs(value)` is a recursively collapsed truth measure, not cardinality. Its
result is `T`, and complement satisfies `abs(~value) == ~abs(value)` in the
value algebra.

## Recursive relations and future graphs

Conceptually, an unweighted adjacency relation is a set indexed by vertices
whose values are `IndexSet` neighborhoods; the fuzzy analogue substitutes
`FuzzySet`. A future graph-facing class can hide the expanded recursive type:

```python
from typing import Hashable

from addons import Bool, FuzzySet, IndexSet, Prob, Set, SetValue


class Graph[I: Hashable, T: SetValue](Set[I, T, Set[I, T]]):
    pass


class UnweightedGraph[I: Hashable](Graph[I, Bool], truth=IndexSet):
    pass


class WeightedGraph[I: Hashable](Graph[I, Prob], truth=FuzzySet):
    pass
```

The apparent repetition of `T` is required for sound static typing. Python has
no associated types that let a checker infer the terminal result type from
`Set[I, T]`. `Graph[I, T]` is the appropriate public abstraction: it hides that
implementation detail and remains open to future truth/weight carriers.

No graph type or algorithm is part of the library yet. The nested form is an
acceptance case for the set algebra, not a commitment to a graph API.

## Graph interpretation

For a probabilistic edge weight:

| Probability | Distance | Interpretation |
|---:|---:|---|
| `0` | `+inf` | absent / impossible edge |
| `1` | `0` | zero-difficulty edge |
| interior `p` | `(1-p)/p` | finite difficulty |

`+` extends a path by adding its distance difficulties. Choosing the best of
alternative paths is a separate operation: minimize projected distance or
maximize probability. It is not probabilistic `|`, which aggregates an
independent-event disjunction. Keeping extension, choice, and probabilistic
union distinct is essential for correct future graph algorithms.
