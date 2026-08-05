# Logical weights: probability-distance duality

Status: exploratory design reference, 2026-08-05.

This note records the intended foundations of `src/addons/logical.py`. It is a
stable reference for later discussion and should be updated whenever a mapping,
operation, identity, or interpretation changes.

## Objective

Model the same edge strength in interchangeable coordinates:

- Boolean presence: `True` is a perfect/present edge and `False` is absence;
- probability or reliability `p` in `[0, 1]`: `1` is a zero-effort edge and
  `0` is absence;
- distance or cost `d` in `[0, +inf]`: `0` is a zero-effort edge and `+inf` is
  absence;
- `base` is the unlabelled implementation carrier for the extended-real
  reference coordinate; `real` is its public nominal type, while probability
  and distance remain the primary operational coordinates.

The principal use case is a weighted directed graph whose weights may be
written as probabilities but consumed by shortest-path-style algorithms. An
operation missing or unnatural in one coordinate may be transported through a
bijection to the coordinate in which it is canonical, then mapped back.

For a bijection `f: A -> B` and an operation defined canonically in `B`, the
transported operation in `A` is:

```text
a op_A b = f_inverse(f(a) op_B f(b))
```

Transporting operations this way preserves their algebraic laws. Defining the
same operation independently in several coordinates does not guarantee that
the coordinates remain consistent.

## Conversion matrix and transport of structure

The properties `real`, `dist`, and `prob` form a 3-by-3 coordinate-conversion
matrix. Write the conversion from coordinate `A` to `B` as `F[A,B]`. For this
matrix to represent one underlying value space, it should satisfy:

```text
F[A,A](a) = a
F[B,A](F[A,B](a)) = a
F[B,C](F[A,B](a)) = F[A,C](a)
```

The last law makes every conversion triangle commute. Only the bijections and
inverses along a spanning tree are mathematically independent; the remaining
matrix entries can be defined by composition. This avoids direct formulas that
silently disagree with an indirect path.

The implementation separates two views of this matrix:

- public `real`, `dist`, and `prob` properties return typed coordinate values;
- private `_real`, `_dist`, and `_prob` cells return raw floats.

`base.__new__` selects a private raw cell using the target class's coordinate
name, then constructs the requested type exactly once. Public properties may
therefore use the simple forms `real(self)`, `dist(self)`, and `prob(self)`
without recursively re-entering the same property.

Only the `real <-> dist` and `dist <-> prob` raw pairs contain primitive
formulas. The derived `base._prob` and `prob._real` cells compose through
`dist`, so changing one bijection pair propagates through the remaining matrix.

Every algebraic operation then has one authoritative coordinate `S`. In another
coordinate `A`, an n-ary operation is defined by converting all operands to
`S`, applying the authoritative operation, and converting its result back to
`A`. Associativity, commutativity, identities, involution, and other equational
laws are thereby inherited rather than reimplemented.

Distinguished constants are the nullary case of exactly the same rule. In the
current design, their methods and canonical values live on `base`. A `base`
instance is a tagged value in the real/reference coordinate, so construction
transports it to the requested `cls`:

```text
constant_A = cls(constant_base)
           = F[real,A](constant_real)
```

Passing the result through `A.__new__` performs this transport only when the
argument retains its source-coordinate type. A raw float is untagged and is
interpreted as already being in the target coordinate; it cannot communicate
that `0.5` was meant as a probability rather than a distance or real value.

## Current architectural direction

`prob` and `dist` deliberately have asymmetric responsibilities:

| Operation family | Authority | Transported implementation |
|---|---|---|
| path accumulation | `dist.__add__` | `prob.__add__` goes through `dist` |
| independent conjunction | `prob.__mul__` / `prob.__and__` | `dist.__mul__` and `dist.__and__` go through `prob` |
| independent disjunction | `prob.__or__`, by De Morgan duality | `dist.__or__` should go through `prob` |
| complement | `prob.__neg__`, interpreted as `1-p` | `dist.__neg__` should go through `prob` |

This is a good use of deliberate deferral. Changing the `prob.dist` and
`dist.prob` properties can change the transported formulas without duplicating
them in every dunder. For that to work completely, no transported operation may
retain a formula belonging to one particular link.

Reciprocal distance is the transport of `1-p` under the odds/rational link
only. Under the active exponential link distance complement is:

```text
d_not = -log(1 - exp(-d))
```

The current implementation correctly makes distance complement defer to
probability complement. Consequently distance `|`, inherited difference, and
inherited xor can follow the selected conversion properties automatically once
both conversion directions are operational.

Runtime checks confirm that round trips and conversion triangles commute across
all three coordinates for representative interior values and endpoints.
Complement, addition, conjunction, disjunction, difference, and xor also
commute between `prob` and `dist`.

## Distinguished constants

The draft now exposes `min`, `mid`, and `max`, sourced in the natural order of
the real/reference carrier:

- `base.min() = real.min() = -inf`;
- `base.mid() = real.mid() = 0`;
- `base.max() = real.max() = +inf`.

The active exponential conversion chain transports these constants to:

| Constant | `real` | `dist` | `prob` |
|---|---:|---:|---:|
| `min` | `-inf` | `+inf` | `0` |
| `mid` | `0` | `1` | `exp(-1)` |
| `max` | `+inf` | `0` | `1` |

The labels identify the same underlying reference points in every coordinate;
they do not promise increasing raw payloads in every representation. Probability
preserves the real ordering, while distance reverses it. This reversal records
the optimization direction: maximizing real/probability corresponds to
minimizing distance. Complement exchanges `min` with `max`.

The midpoint is link-dependent. Because `real(0)` is authoritative,
`dist.mid()` remains `1` under `d = exp(-x)`, while the selected distance-to-
probability property determines its probability representation:

```text
exponential link: prob.mid = exp(-1)
rational link:    prob.mid = 1/2
```

Thus changing the authoritative conversion properties changes the derived
constant variant without duplicating constants in each class.

`real.mid()` is the identity of ordinary real addition. It is not the identity
of the current path-addition operation: ordinary distance addition has identity
`dist(0)`, and transported probability addition has identity `prob(1)`. In the
reference-ordered naming these are the `max` constants. Each operation must
transport its own identity from the coordinate in which that operation is
authoritative.

## Domains and endpoints

The closed graph-weight domains require extended endpoints:

| Meaning | Boolean | Probability `p` | Distance `d` | Real score `x` |
|---|---:|---:|---:|---:|
| absent / impossible | `False` | `0` | `+inf` | `-inf` |
| zero effort / certain | `True` | `1` | `0` | `+inf` |

The exact score interpretation depends on the selected probability-distance
link. Implementations need explicit endpoint handling because `log(0)` and
division by zero raise before producing these mathematical limits.

## Two probability-distance links

Both candidate links are decreasing bijections between `[0, +inf]` and
`[0, 1]`, but they transport addition into different probability operations.
They therefore represent different meanings of distance and must not be mixed
inside one untagged `dist` type.

### Odds/rational link

```text
p = 1 / (1 + d)
d = 1 / p - 1 = (1 - p) / p
```

Here `d` is odds against success. With the score-distance map

```text
d = exp(-x)
x = -log(d)
```

the complete triangle is:

```text
p = sigmoid(x)
x = logit(p)
d = exp(-x) = (1 - p) / p
```

Ordinary probability complement transports particularly cleanly:

```text
p       -> 1 - p
d       -> 1 / d
x       -> -x
```

If distance addition is canonical, its transported probability composition is
the Hamacher product with parameter zero:

```text
d_path = d1 + d2
p_path = p1*p2 / (p1 + p2 - p1*p2)
```

Its De Morgan dual is:

```text
p_or = (p1 + p2 - 2*p1*p2) / (1 - p1*p2)
d_or = d1*d2 / (d1 + d2)
```

with endpoints interpreted by limits. The distance disjunction is the familiar
parallel-sum formula.

### Exponential/surprisal link

```text
p = exp(-d)
d = -log(p)
```

Here `d` is self-information, surprisal, or negative log reliability. It is the
canonical link for independent path probabilities because:

```text
d_path = d1 + d2
p_path = p1 * p2
```

This explains the intended transported implementation `prob.__add__(p, q) =
p*q` when `+` denotes distance-style path accumulation.

Ordinary probability complement is less simple in distance coordinates:

```text
p_not = 1 - p
d_not = -log(1 - exp(-d))
```

If `d = exp(-x)` remains the score-distance map, composition gives:

```text
p = exp(-exp(-x))
x = -log(-log(p))
```

This is a Gumbel/log-log coordinate, not the sigmoid/logit map. The exponential
link is nevertheless exactly the entropy-inspired construction intended by the
draft.

## Best-path algebra

For shortest or most-reliable path, two separate operations are needed:

1. extend a path through consecutive edges;
2. select the better of alternative paths.

Under the exponential link they correspond as follows:

| Coordinate | Extend path | Choose alternative | Empty path | No path |
|---|---|---|---:|---:|
| distance | `d1 + d2` | `min(d1, d2)` | `0` | `+inf` |
| probability | `p1 * p2` | `max(p1, p2)` | `1` | `0` |
| Boolean | `b1 & b2` | `b1 | b2` | `True` | `False` |
| real score | `-log(exp(-x1) + exp(-x2))` | `max(x1, x2)` | `+inf` | `-inf` |

The exponential probability-distance map is an isomorphism between the
min-plus distance semiring and the max-product probability semiring.

The rational link retains the same `min`/`max` alternative selection but uses
the Hamacher product rather than ordinary multiplication to extend a path.

An unchanged shortest-path implementation that selects the smallest value also
requires probability comparison to use cost order, which reverses ordinary
numeric probability order. Alternatively, the algorithm must accept its choice
operation explicitly and use `max` for probabilities.

## Probabilistic logic is a different choice

Product conjunction and its De Morgan dual give:

```text
p_and = p1 * p2
p_or  = 1 - (1 - p1)*(1 - p2)
```

This models independent-event conjunction and noisy disjunction. It is not the
same as the max-product best-path algebra, whose alternative operation is
`max`. The two choices agree at Boolean endpoints but differ for intermediate
probabilities.

This distinction must remain explicit:

- use `max` when choosing the single most reliable path;
- use probabilistic union when computing the chance that at least one
  independent event occurs;
- shared-edge graph paths are generally not independent, so noisy disjunction
  cannot be applied to arbitrary paths without accounting for dependence.

The operator names `&` and `|` may represent fuzzy conjunction/disjunction,
while a graph semiring may need separately named path-extension and
alternative-choice operations. Reusing the same symbols is safe only after
choosing one interpretation.

## Role of the real coordinate

The real coordinate is useful when it has a declared interpretation:

- under the rational link it is log-odds or evidence;
- under the exponential link composed with `d = exp(-x)`, it is a Gumbel/log-log
  score;
- transporting distance addition gives
  `-log(exp(-x1) + exp(-x2))`, not ordinary real addition.

The `dist` and `prob` coordinates are sufficient for graph operations. `base`
implements the reference-coordinate row of the matrix and owns the
distinguished constants; `real` is the clean public nominal form of that same
coordinate. The conversion matrix uses the spanning path
`real <-> dist <-> prob`; direct `real <-> prob` conversion defers through
`dist`, forcing the triangle to commute.

## Operation authority

Each public operation should have exactly one authoritative coordinate and be
transported everywhere else. The present direction is:

| Meaning | Authoritative coordinate |
|---|---|
| path extension | `dist`: addition |
| best alternative | `dist`: minimum |
| independent conjunction | `prob`: multiplication |
| independent disjunction | `prob`: De Morgan dual |
| complement | `prob`: `1-p` |

Graph choice and probabilistic disjunction must not silently share one
operator.

## Current draft observations

The current `logical.py` implements the intended authority/deferral pattern:

1. `base.__new__` is the sole constructor dispatcher. Tagged logical inputs
   select the target class's private raw matrix cell; untagged numeric inputs
   remain raw payloads.
2. The `_coordinate` class variable is inherited by semantic subclasses, so
   conversion does not depend on class names.
3. Private diagonal cells expose the existing raw payload, preventing recursive
   same-coordinate reconstruction. Public matrix properties remain uniformly
   defined on `base`.
4. `base` and `real` share the `real` coordinate rather than representing two
   mathematical coordinates. `real` is only its clean public nominal type.
5. The base-owned constants use `cls(base(value))`; the inner value supplies
   reference-coordinate context and the outer construction selects the target
   matrix column dynamically.
6. Interior values and the `0`, `1`, and infinite endpoints round-trip, every
   conversion triangle commutes, and complement, addition, conjunction,
   disjunction, difference, and xor agree across probability and distance.
7. The live link is currently exponential/surprisal; the unreachable second
   property returns are rational-link reference formulas. They should
   eventually become a named link strategy or comments/reference functions,
   since dead returns are not a runtime selection mechanism.
8. Validate domains: `prob` belongs to `[0, 1]`; `dist` belongs to
   `[0, +inf]`; score endpoints may be infinite; NaN needs an explicit policy.
9. Decide whether equality and hashing are coordinate-strict or semantic.
   Inheriting `float` currently makes equal raw payloads compare equal across
   different coordinates even when they represent different edge strengths.
10. Keep operation identities separate from the interior reference constant.
   With transported distance addition, the identity is `dist.max() = dist(0)`
   or equivalently `prob.max() = prob(1)`, not `mid()`.
11. Decide ordering semantics. Natural probability order and distance/cost order
   are reversed.
12. Restrict or transport raw float operations that can leave the domain.
13. Keep fuzzy conjunction/disjunction separate from best-path extension/choice
   unless one interpretation is deliberately selected.

## Open decisions

- Primary link: odds/rational, exponential/surprisal, or two distinct types?
- Primary graph task: best path, reachability, aggregate reliability, or several
  explicit algebras?
- Operator vocabulary: Python arithmetic/logical dunders or named operations?
- Probability ordering: natural confidence order or reversed cost order?
- Equality: same coordinate only or equality after canonical conversion?
- Endpoint representation and NaN policy?
- Should the nominal `real` type acquire additional authoritative operations,
  or remain a clean public view of the reference semantics implemented by
  `base`?
- Are edge/path dependencies in scope for probabilistic disjunction?
