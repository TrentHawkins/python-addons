# `logical.py` — exact logical value algebras and their containers

Working notes for `src/addons/logical.py`. Records what the module is, what is built, what holds, and the decided direction: **one bordered tensor per object, with every sub-dimensional weight derived by contraction.**

---

## 1. What this is

Two things, stacked:

1. **A scalar algebra** of logical values carried as exact rational coordinates on the projective line $\mathbb{P}^1(\mathbb{Q})$ — no floats, no rounding.
2. **A container algebra** whose members carry those values, and whose containers are themselves values in the same algebra, so nesting closes.

The second is the point. `Node` is a `Boolean`, so a `Node` can be the value type of another `Node`, and that recursion is what makes graphs, hypergraphs and complexes expressible in one vocabulary.

### The representational correspondence

The design is one idea seen twice, and naming it explains most of what follows:

| set theory | graph theory | here |
| --- | --- | --- |
| roster notation $\{a, b, c\}$ | adjacency list | `repr` of a crisp `Node` |
| indicator function $\chi \colon K \to \{0,1\}$ | adjacency matrix | the `defaultdict` itself |

A `Node` **is** the indicator function; the roster is a rendering of it. One nesting level up, a `Graph` **is** the adjacency matrix and its neighbourhoods are the adjacency list. Generalising the codomain from $\{0,1\}$ to a graded carrier is exactly the step from unweighted to weighted — an unweighted graph *is* a `Bool`-weighted one, which is why `UnweightedGraph` and `Graph` differ only in `truth`.

---

## 2. The contracts

Each names one responsibility, and the concrete types get their behaviour by derivation.

| contract | responsibility | gives |
| --- | --- | --- |
| `Bounded` | there is a top and a bottom | `minimum`, `maximum` |
| `Invertible` | negation exists | `__invert__` |
| `Operable` | the lattice | `\|`, `&`, `-`, `^` by De Morgan, `union`/`intersection`/… |
| `Additive` | the sum | `__add__`, `__mul__`, `sum` |
| `Order` / `Partial` / `Total` | how two compare | `__eq__`, `__ne__`, `__lt__`, `__gt__` derived from `__le__`/`__ge__` |
| `Separable` | am I true | `__bool__`, `isdisjoint` |
| `Coded` | **I am a point on $\mathbb{P}^1(\mathbb{Q})$, faithfully** | `encode`, `decode`, `decoded` |
| `Boolean[T: Coded]` | I am in the algebra, and I contract to a point | `__abs__ -> T` |

Two laws separate `Coded` from `Boolean`, and the distinction is load-bearing:

- `Coded` is **faithful**: `encode(*x.decode()) == x`. Only scalars satisfy it.
- `__abs__` is a **projection**: lossy, and the only member of the contract that leaves its own type. It is therefore *the* seam between containers and scalars.

`Coded` extends `Boolean` — every point is a value, not every value is a point. That containment is what lets `relate` compare a set to a scalar at all.

---

## 3. The scalars

`Frac(Coded, Total, ABC)` holds `numer`/`denom` and derives everything from `encode`/`decode`. Writing a point as $(a : b)$:

| type | coordinates | reading |
| --- | --- | --- |
| `Dist` | $(a : b)$ as stored | difficulty, $0$ truest, $\infty$ falsest |
| `Prob` | $\operatorname{encode}(a, b) = (b : b + a)$ | probability, $1$ truest, $0$ falsest |
| `Bool` | only $(0 : 1)$ and $(1 : 0)$ | the two-point quotient of the line |

`Bool` is a `Frac` in four members. Everything else — `__and__`, `__add__`, `__mul__`, `__invert__`, `__abs__`, `__hash__`, ordering, bounds — is inherited.

**Mixing is closed.** `Prob(0.5) & Bool(True) -> 0.5`, `Dist(0.75) | Bool(False) -> 0.75`, with the left operand's type as authority. Cross-type equality and hashing agree: `Bool(True) == Prob(1,1) == Dist(0,1)` and all three hash alike.

**Raw values**: a `bool` is crisp (`Dist(True)` is the minimum), an `int` is a numerator (`Dist(1) == 1.0`). Comparison and construction read them identically.

**Bound naming.** `minimum()` is the *truest* end and `maximum()` the falsest — the `Dist` orientation, where zero difficulty is certainty. Worth stating because it reads backwards against `float`: `Prob.minimum() == 1.0` and `Prob.maximum() == 0.0`, while `Prob(3,4) >= Prob(1,2)` is `True`.

---

## 4. The contraction

`abs` is the whole engine of the design, so it deserves an exact statement rather than a mention. Define the De Morgan dual of the sum:

$$a \oplus b \;:=\; \neg\bigl(\neg a + \neg b\bigr)$$

Then, for a set $s$ with a false background:

$$\bigl\lvert\, s \,\bigr\rvert \;=\; \bigoplus_{v \,\in\, s} v$$

Verified over 400 random graded sets: `abs(s)` and `reduce(oplus, s.values())` agree exactly.

### What it is, in each reading

| carrier | $\oplus$ is | check |
| --- | --- | --- |
| `Bool` | plain **OR** | `(F,F)->F  (F,T)->T  (T,F)->T  (T,T)->T` |
| `Dist` | **parallel conductance**, $1/D = \sum 1/d_i$ | exact to rationals |
| `Prob` | neither max nor noisy-or | $n$ elements at $\tfrac12$ give $\tfrac{n}{n+1}$ |

```txt
n=1 of 0.5  ->  abs 0.500000    noisy-or 0.500000
n=2 of 0.5  ->  abs 0.666667    noisy-or 0.750000
n=3 of 0.5  ->  abs 0.750000    noisy-or 0.875000
n=4 of 0.5  ->  abs 0.800000    noisy-or 0.937500
```

**`abs` is deliberately not the or-fold.** `|` on `Prob` is noisy-or, $1 - \prod(1 - p_i)$ — the probability that at least one of several *independent* events occurs. `abs` is the parallel combination of difficulties. The two agree on `Bool` and diverge on `Prob`, and `abs` is the chosen one: it is already the declared seam, it is what makes the borders compose (below), and its `Dist` reading — many easy routes make the whole easy — is the natural aggregation for a carrier whose stored coordinates *are* difficulties. `abs` does **not** distribute over `|`, and nothing in the design asks it to.

### The two properties everything below rests on

**Monotone.** $\lvert s \rvert$ is at least as true as every member — verified over 400 random sets. This is what turns downward closure from an unenforceable invariant into a theorem.

**Order-independent.** Contracting a tensor axis by axis reaches the same scalar whatever the order:

```txt
abs(g)                          0.8108108108108109
abs(row borders of g)           0.8108108108108109
abs(column borders of g)        0.8108108108108109
```

Because $\oplus$ is associative and commutative, the full contraction is $\bigoplus$ over every cell, however you get there.

### One axis at a time

`abs` contracts every axis. The **single pass** contracts one:

$$\operatorname{contract}(g) \;=\; \bigoplus_{i} g[i], \qquad \bigl\lvert g \bigr\rvert \;=\; \operatorname{contract}^{\,r}(g)$$

Verified exactly at rank $2$ and rank $3$: iterating the single pass to a scalar reproduces `abs` to the last rational.

It **walks the tower down one rung per pass**, which is the structural confirmation that this is the right single step — a rung's `truth` *is* the rung below, so the fold of its values is an object of that rung:

```txt
Hyper  ->  Graph  ->  FuzzySet  ->  Prob
```

Two notes before it becomes code.

**It is already spelled `g[:]`** (§6), and only in that direction. A subscript consumes axes left to right, so the axes it *keeps* are always the trailing ones — which means folding axis $0$ is expressible and folding the innermost axis is not:

```txt
g[:]           {0: 0.5, 1: 0.7692307692307693}          the top border — spelled
left border    {0: 0.5714285714285714, 1: 0.75}         not spellable
```

The left border is `abs` mapped over the values, and it needs a name of its own or a second notation. The missing direction is the one worth a helper, not the one already written.

**It is `Node.contracted`, a property** — the once-contracted node, following the file's `Coded.decoded` convention where a past participle names *the result*, not a question. It is also the programmatic spelling of `g[:]`, which matters because `:` cannot be written outside a subscript:

```txt
g[:] == g.contracted                       True
g.contracted.contracted == abs(g)          True
```

Note the neighbouring name: `Path.contracting` is a **state** (does an axis contract), while `Node.contracted` is a **value**. Present participle for the question, past participle for the result — one word could not carry both. `Frac.contract` is a third thing again, an existing `@final @classmethod` doing scalar coercion, which is why neither of these is called `contract`.

**It must respect the background.** A naive $\oplus$-fold of the recorded values ignores `default` and disagrees with `abs` on every complemented set — $0/43$ in a sweep. `contracted` mirrors `__abs__`'s own shape instead, inverting around the complement:

```python
values = [value if self.complement else ~value for value in self.values()]

result = sum(values, self.truth.minimum())

return result if self.complement else ~result
```

**Where it agrees with `abs`, exactly:**

| | crisp background | graded background |
| --- | --- | --- |
| rank $1$ | $300/300$ | $300/300$ |
| rank $2$ | $300/300$ | $186/300$ |

The one divergence is a **graded background at rank $\geq 2$**. There, the values being folded are themselves containers carrying their own graded backgrounds, and a pointwise sum compounds them once per recorded key, while `abs` scalarises each child first so each background contributes once. Neither is wrong — they are two readings of an infinite implicit family — but they are not the same, so `__abs__` stays the declared seam and `contracted` is not used to define it.

### Ragged rungs

A rung is **ragged** if its values are of mixed rank. The single pass is total there, but it does not agree with `abs`, and it does not even agree with itself:

```txt
naive fold, scalar first     Prob      0.8125
naive fold, set first        FuzzySet  0.5~{...}
lifted fold, either order    FuzzySet  0.5~{...}   -> abs 0.5
recursive abs, either order  Prob      0.8125
```

$\oplus$ takes its **left operand as authority**, so a naive fold over mixed ranks depends on iteration order. Lifting each scalar to its background set (the §5 seam, applied one level down) restores order-independence but changes the answer, because a lifted scalar is a constant over the *whole* key space rather than one value among many. `abs` avoids both by mapping every value to a scalar *before* summing.

**So the single pass is well defined exactly when the rung is uniform** — and that is not a restriction, because the coercion sandwich makes every rung uniform by construction:

```txt
g['x'] = Prob(1,2)          stored as FuzzySet 0.5~{}    lifted by truth
f['y'] = FuzzySet({...})    stored as Prob 0.75          contracted by truth
```

Raggedness requires `dict.__setitem__` — bypassing `truth` — so no public write can produce it. This is also the exact sense in which `Set[V, E] | E` is over-wide: **the type permits what `truth` forbids.**

---

## 5. The container

Two classes, and the names carry the distinction:

| class | is | role |
| --- | --- | --- |
| `Node` | one keyed record of weights — a row | the general container, flat by declaration |
| `Set` | the self-referential tower, values of itself-or-scalar | where every named type comes from |

**Why these names.** A `Node` is exactly what §7 says a graph node *is* — its weight is not stored but is `abs` of its record. And because every named type is a rung of the tower, `class Graph[V](Set[V, Prob], …)` states the library's thesis in its own declaration: **a graph is a set**. Rungs are uniform by construction (§4), so the tower is the only place a container is ever built.

To keep the word unambiguous, the prose below says **vertex** for a key and reserves `Node` for the class — a vertex is the label, a `Node` is the record it indexes.

`Node[K, T: Coded = Bool, V: Boolean = T]` over `defaultdict[K, V]`.

- `truth: type[V]` — the carrier. What an unrecorded key is, and what any value becomes.
- **A `Node` is a background plus recorded deviations.** `default` is the background; `complement` is a *reading* of it (`bool(self.default)`), not separate state.
- A background can be **graded**, not just a bound: `FuzzySet(Prob(1,2))` is the half-present set, and `abs` brings it back exactly.

### The seam, both directions

| direction | mechanism | contract |
| --- | --- | --- |
| `Node` → scalar | `abs` — the contraction of §4 | `Boolean.__abs__` |
| scalar → `Node` | the background it *is* | `Node.__init__` |

The round trip is exact for every scalar $x$:

$$\bigl\lvert\, \mathrm{Node}(x) \,\bigr\rvert = x$$

Comparisons are authority-free — a set meets a scalar at the measure — so `set OP scalar` and `scalar OP.reflected set` always agree.

### The tower

`Set[V, E: Coded = Bool](Node[V, E, "Set[V, E] | E"])` — a set whose values are sets. A rung of depth $d$ **is** a tensor of rank $n = d + 1$:

$$A \colon K^{\,n} \longrightarrow E, \qquad n = \operatorname{arity}() = \text{depth} + 1$$

- `registry: pair[list[type[Set]]]` — one dense list per polarity, indexed by depth.
- A rung declares its slot: `class Graph[V](Set[V, Prob], weighted = True, depth = 1)`, and `__init_subclass__` derives `truth` from the rung below and claims the slot. Declaring and looking up name **one** class, never two.

| | depth 0 — rank 1 | depth 1 — rank 2 |
| --- | --- | --- |
| crisp | `IndexSet` | `UnweightedGraph` |
| graded | `FuzzySet` | `Graph` |

`type(Graph()["u"]) is FuzzySet` — a graph's neighbourhoods *are* the named sets. The nesting is **row-major**: `g[i]` is a stored object, a column is not.

---

## 6. Addressing

### Tuple keying and rung keying are the same thing

$$g[x_0, x_1, \dots, x_{k-1}] \;\equiv\; g[x_0][x_1]\cdots[x_{k-1}]$$

A subscript tuple **is** a chain of descents — verified: `h[0,1,2] == h[0][1][2]`, `h[0,1] == h[0][1]`, and `h[0] == h[0,]`.

Python delivers `g[1,2]` and `g[(1,2)]` to `__getitem__` as the same object, so there is no way to honour this rule and also keep tuple keys. **A tuple is therefore no longer a key**; see the cost below.

### The rank law

$$\operatorname{rank}\bigl(g[x_0, \dots, x_{k-1}]\bigr) \;=\; r - k$$

Every coordinate consumes exactly one axis, and the result is a scalar precisely when $k = r$. **Sentinels do not change this arithmetic** — they change which operation is applied at that axis, not whether the axis is consumed. Verified across nine forms on a rank-3 tensor:

```txt
h[0]        len 1   rank 2        h[:]        len 1   rank 2
h[0,]       len 1   rank 2        h[:,1]      len 2   rank 1
h[0,1]      len 2   rank 1        h[0,:]      len 2   rank 1
h[0,1,2]    len 3   rank 0        h[0,:,2]    len 3   rank 0
                                  h[:,:,:]    len 3   rank 0
```

There is **no padding**: a short subscript yields a container, not a contracted scalar. A trailing contraction is spelled by writing the sentinel, or simply by `abs` of the container — `g[0,:] == abs(g[0])`, verified.

| at this position | operation | axis |
| --- | --- | --- |
| a key | index down one level | consumed |
| a sentinel | fold this level's values with $\oplus$ | consumed |

### `Path` — the boundary

A subscript is normalised to a `Path`, a `tuple` subclass that owns everything the notation means:

```python
class Path[K: Hashable](tuple[K | None | slice, ...]):
    """validated on construction; true when it locates a slot."""

class Edge[K: Hashable](Path[K]):
    """a path that also knows its orbit."""
```

| member | job |
| --- | --- |
| `__new__` | rejects a bounded slice **at construction**, so no accessor has to re-check |
| `__getnewargs__` | keeps a varargs `__new__` picklable — see §9 |
| `read` | normalises any subscript — bare key, tuple, `Path`, `Edge` — into one type |
| `contracts` | static, one coordinate: is it a sentinel |
| `contracting` | property, whole path: does any axis contract |
| `Edge.permutations` | the orbit, the one thing `Undirected` needs |

`Edge` subclasses `Path` because an edge *is* a path that locates; it inherits construction and validation and adds only `permutations`.

**Rejected: putting this on `__bool__`.** It was tried, and a non-empty tuple that is falsy breaks an invariant the whole language relies on:

```txt
len(Path(1, None)) == 2   but   bool(Path(1, None)) is False

filter(None, paths)        silently drops the contracting ones
any(paths) / all(paths)    answer a question nobody asked
[p for p in paths if p]    2 of 3
```

Named members cost one word at three call sites and take the trap away. The name `contractible` was also considered and rejected: in a library that talks about simplicial complexes it already means *homotopy-equivalent to a point*. The path's predicate is `contracting` rather than `contracted`, because `contracted` is taken by `Node` for the *contracted node* — the `Coded.decoded` convention, where a past participle names a result.

### The sentinel

Two spellings, one meaning — *contract this axis*:

| spelling | where it works | note |
| --- | --- | --- |
| `None` | anywhere | the programmatic form |
| `:` — an **unbounded** slice | literally in a subscript only | the sugar |

Both are needed. `:` cannot be written outside a subscript — `Edge(1, :)` is a `SyntaxError` — so any path built in code needs `None` (or `slice(None)`).

**Only the unbounded slice is accepted.** A bounded one is rejected, because $K$ is `Hashable` and carries no order, so `g[0, 1:5]` names nothing:

```txt
g[0,1:5]  ->  KeyError: only an unbounded slice is a sentinel, not slice(1, 5, None)
```

`slice` is hashable on 3.14 and would otherwise be a legal key; reserving it is a deliberate exchange.

**A bare `:` is not a tuple.** `g[:]` delivers a bare `slice`, so by the rank law it yields a rank-$(r-1)$ **container** — the border *vector*, not a scalar. On a graph:

```txt
g[:]      {1: 0.6666666666666666, 2: 0.5333333333333333}    the top border, as a set
g[:,1]    == g[:][1]                                        that border at 1
g[0,:]    == abs(g[0])                                      the left border at 0
g[:,:]    == abs(g)                                         the corner
```

### What this costs

$K$ narrows from `Hashable` to **`Hashable` minus `tuple`, `None` and `slice`**. That is a real narrowing, of the same kind as the ordering requirement rejected in §8 — milder, but it should be taken knowingly. Today `IndexSet()[(0,0)] = True` stores a tuple vertex and `g['u','v'] = x` stores a tuple vertex under `('u','v')`; both change meaning.

Everything else survives: `str`, `int`, `frozenset`, `complex`, bare `object()`, and any other non-tuple hashable. Where a tuple genuinely must be a key, a six-line wrapper restores it without touching the container:

```python
class Key[K: Hashable]:
    __slots__ = ('value',)

    def __init__(self, value: K): self.value = value
    def __hash__(self) -> int: return hash(self.value)
    def __eq__(self, other: object) -> bool: return isinstance(other, Key) and self.value == other.value
```

### Reads fold; writes descend

A sentinel builds a **derived** object — the fold of a level's values — which is not a storage location. `g[:, 'v'] = x` has nowhere to land, and no unique solution even in principle. So **`__setitem__` and `__delitem__` reject a sentinel anywhere in the key.** Nothing is lost by it: assigning a whole neighbourhood is already spelled `g['u'] = …`.

That leaves *one* walk rather than two. `route` disappears as a shared abstraction — it folds into `__getitem__`, and the write path reuses that:

```python
*head, last = key

holder = self[tuple(head)] if head else self

dict.__setitem__(holder, last, holder.truth(value))
```

so there is no second resolution to keep in step with the first. In the code this is `Node.locate`, which is write-only: it rejects a sentinel, refuses an empty path, and hands back the stored `(holder, coordinate)` pair that `__setitem__`, `__delitem__`, `get`, `setdefault` and `pop` all share.

**A bare sentinel is not a tuple**, so `g[:]` and `g[None]` would autovivify a vertex under `slice(None)` if they reached the key path. `Path.read` normalises them to a one-coordinate path first, which is what removes the special case rather than guarding it.

### `Edge` and the sentinel do not mix

An `Edge` **is** a `tuple`, so `g[Edge('u','v')]` remains a perfectly good subscript. But `:` is subscript *syntax* — `Edge(1, :)` is a `SyntaxError` — so a path carrying a sentinel must be written as a bare tuple, `g[1, :, 3]`, or built with `None`, `Edge(1, None, 3)`.

Dispatch is `isinstance(key, tuple)`, which covers both. `Edge`'s remaining job is `permutations`, so `__setitem__` coerces a tuple key to an `Edge` purely to give `Undirected` an orbit to mirror over.

---

## 7. The bordered tensor

**One tensor per object, of rank $n$, plus derived borders.** This supersedes the graded-family design recorded in earlier drafts; see *Superseded* below.

Take the classical bordered adjacency matrix of a $4$-vertex directed graph:

```txt
     1 0 1 1

1    0 0 0 1
0    0 0 0 0
1    1 0 0 0
1    0 0 1 0
```

The interior is $A$. The left border is the row-wise contraction, the top border the column-wise one. Reproduced exactly by the code:

```txt
left border  (out-existence)   [1, 0, 1, 1]
top  border  (in-existence)    [1, 0, 1, 1]
corner       abs(g)            True
```

**A vertex's weight is not stored; it is justified by its edges.** Vertex $2$ has no incident edge in either direction, so both its borders are false and it is invisible — in practice a $3$-vertex graph, which is the right reading. At rank $1$ — an `IndexSet` or a `FuzzySet` — the property is trivial: elements carry weights outright, because there is no interior to contract.

### Every face has several views, and directedness is exactly why

A vertex has *two* weights, not one: incoming and outgoing existence. They genuinely differ:

```txt
h['a','b'] = True               a -> b, nothing else

out-existence of a  True        in-existence of a  False
out-existence of b  False       in-existence of b  True
```

In general a $k$-face of a rank-$n$ tensor has

$$\binom{n}{\,k+1\,} \quad\text{views}$$

— one per choice of which positions its coordinates occupy. Rank $2$: two views of a vertex. Rank $3$: three views of an edge and three of a vertex, verified distinct:

```txt
t[1,2,3] = 3/4

edge (1,2)   t[1,2,:] = 0.75    t[1,:,2] = 0.0    t[:,1,2] = 0.0
vertex 1     t[1,:,:] = 0.75    t[:,1,:] = 0.0    t[:,:,1] = 0.0
```

These are the three facet matrices of the cube, each carrying its own border vectors, all meeting at the single corner scalar $\lvert A \rvert$ — and §4's order-independence is what makes that corner well defined.

### Closure is a theorem, not an invariant

Because $\oplus$ is monotone, a face is always at least as true as any coface:

$$\tau \subseteq \sigma \;\implies\; A(\tau) \;\geq\; A(\sigma)$$

```txt
t[1,2,:] >= t[1,2,3]     True
t[1,:,:] >= t[1,2,:]     True
```

This is the simplicial-complex closure condition, in graded form, holding **structurally**. Earlier drafts left closure as an undecided, unenforceable invariant; deriving borders rather than storing them removes the question entirely.

### Lower dimensions, via degenerate cells

A face with no coface — a whisker edge on a triangulation — is not lost. Repeating a coordinate gives a **degenerate cell**, the standard simplicial device for embedding a lower dimension, and it propagates to the borders correctly:

```txt
t[1,2,3] = 3/4              a genuine triangle
t[4,5,5] = 1/2              a degenerate cell: the edge (4,5), on no triangle

edge (1,2) border   0.75    from its triangle
edge (4,5) border   0.50    from the degenerate cell
vertex 4   border   0.50
vertex 9   border   0.00    unrecorded, therefore invisible
```

Whether degenerate cells are the *idiomatic* way to record a low-dimensional face, or merely a mechanism that happens to work, is not yet settled — see §9.

### What this gives up

Faces cannot carry weights **independent** of their cofaces. Setting the triangle $(1,2,3)$ to $\tfrac34$ forces $A(1,2,\cdot) \geq \tfrac34$; it cannot also be $\tfrac{3}{10}$ for unrelated reasons. That is not a defect under this reading — a face's existence *is* justified by what sits on it — but it is a real restriction, and anyone who genuinely needs independent per-dimension weights must hold several tensors side by side rather than expect one to carry them.

### Superseded: the graded family

Earlier drafts specified a `ComplexSet` of dimension $d$ owning one `Set` rung per dimension, $\bigl(A_k\bigr)_{k=0}^{d}$, with the algebra lifting componentwise. It was motivated by exactly the restriction above: the belief that faces need independent weights.

Withdrawn, because the restriction is the correct semantics rather than a gap, and because the pure tensor is strictly simpler and answers more:

| question | graded family | bordered tensor |
| --- | --- | --- |
| face weights | stored, independent | derived by contraction |
| downward closure | unenforceable invariant | theorem, from monotonicity |
| lower dimensions | a rung each | degenerate cells |
| a face's several views | absent — one weight per face | $\binom{n}{k+1}$, and directedness explains them |
| new machinery | a graded container, a `link` helper, `del` splitting | a sentinel, and tuples stop being keys |

The other alternative once considered, **a weight at every vertex** — each slot holding *(weight, children)* rather than weight *or* children — is withdrawn for the same reason: it stores what contraction derives, and would turn the value union into a product for no gain.

---

## 8. Symmetry — the undirected case

Permutations only, no sign (§9). Undirected has an exact statement: **$A$ is constant on $S_n$-orbits.**

$$A(x_{\sigma(0)}, \dots, x_{\sigma(n-1)}) = A(x_0, \dots, x_{n-1}) \qquad \text{for all } \sigma \in S_n$$

### What symmetry buys, in the bordered picture

**The views collapse.** All $\binom{n}{k+1}$ weights of a $k$-face become one — verified:

```txt
directed     A(1,2,.) = 0.75    A(.,1,2) = 0.0
undirected   A(1,2,.) = 0.75    A(.,1,2) = 0.75
```

So `Undirected` is not a convenience over the directed case; it is the condition under which *a face has a weight at all*, rather than a tuple of position-dependent ones. In-existence and out-existence become one vertex weight, which is why the undirected reading feels primary even though the directed one is more general.

**Links inherit symmetry for free.** A slice of a symmetric tensor is symmetric in the remaining coordinates, so the link of an undirected object is undirected with no mixin on the sub-rungs:

```txt
f[1] is a plain Graph (no mixin on it)
f[1][2,3] == f[1][3,2]   ->   True
```

### Decided: mirroring, not canonicalisation

Two implementations satisfy the orbit law. Write every ordering, or store one representative per orbit.

| | mirroring | canonicalisation, ordered | canonicalisation, multiset |
| --- | --- | --- | --- |
| the key | every ordering, stored | `tuple(sorted(edge))` | `frozenset(Counter(edge).items())` |
| slots per cell | $n!$ | $1$ | $1$ |
| nesting | preserved — a rung stays a tensor | flattened | flattened |
| borders | free — contraction of stored sub-objects | gathered by scan | gathered by scan |
| invariant | maintained, therefore breakable | structural, cannot disagree | structural, cannot disagree |
| requires of $K$ | `Hashable` | `Hashable` **and a total order** | `Hashable` |

**The last row eliminates the ordered column, and only that one.** This library generalises `set`, so it must speak `set`'s language, and `collections.abc.Hashable` promises exactly `__hash__` and `__eq__`. Ordering is absent from that contract on purpose: membership is equality-based and needs no order.

That is not a hypothetical narrowing:

```txt
complex        sorted -> TypeError: '<' not supported between instances of 'complex'
None + int     sorted -> TypeError
mixed types    sorted -> TypeError
object()       sorted -> TypeError
```

And the sharpest case is worse than raising. `frozenset` is hashable *and* supports `<`, but that `<` is **subset** — a partial order:

```txt
frozenset({1,2}) < frozenset({2,3})   ->   False
frozenset({2,3}) < frozenset({1,2})   ->   False
sorted([a, b]) and sorted([b, a]) disagree
```

So `sorted` would silently return an *insertion-order-dependent* representative, and a canonical form that depends on insertion order is not canonical.

**But the domain argument does not reach canonicalisation as such.** A *multiset* key is a canonical orbit representative needing nothing beyond `Hashable` — verified:

```txt
key = frozenset(Counter(edge).items())

hashable                        True
{1j, None, object()}            fine — no comparison is performed
ms(1,1,2) == ms(1,2)            False    repeats survive, unlike frozenset(edge)
ms(1,2,3) == ms(3,1,2)          True     constant on the orbit
```

**What actually decides it is the `nesting` row.** Any canonical scheme keys a cell by one flat object, so there are no sub-dictionaries: no `truth` chain, no descent, and — decisively under §7 — **no borders**, since every contraction would become a scan over a flat store rather than an `abs` of something already held. Mirroring is the only one of the three that keeps a rung a tensor, and the tensor is the thing being generalised. That is a structural reason rather than a domain one, and it cannot be overturned by a cleverer key.

### What this leaves

$n!$ slots per cell — $2, 6, 24, 120$ through rank $5$ — and an invariant that is maintained rather than structural, so it can be broken by any write that does not pass the whole `Edge` through the top-level `__setitem__`. Both are acceptable: the storage only bites past rank $3$, and the breakage points are enumerable (§9) rather than unbounded.

### Propagating the mixin down the tower

The tower does not carry `Undirected` downward: a `UGraph` yields plain `FuzzySet` links. Two questions hide in that, with different answers.

**Expressible? Yes, with no new machinery.** `Node.__init_subclass__` already accepts an explicit `truth`, and `Set.__init_subclass__` derives one only when the class claims a rung — so a parallel tower is a declaration, not a metaclass:

```python
class UFuzzySet[I](Undirected, FuzzySet): ...
class UGraph[V](Undirected, Graph, truth = UFuzzySet): ...
class UHyper[V](Undirected, Hyper, truth = UGraph): ...
```

Verified: `UGraph.truth is UFuzzySet`, `g['u']` returns a `UFuzzySet`, `arity()` is unchanged, and `Set.registry` is untouched because no `weighted`/`depth` kwarg means no slot claim. Named classes, so pickle is unaffected.

**Sufficient? No — and the shortfall is exactly measurable.** Writing through a link on a rank-3 undirected tensor:

```txt
h[1][2,3] = 3/4

propagated   repairs 2/6   [(1,2,3), (1,3,2)]
plain        repairs 1/6   [(1,2,3)]
```

Propagation buys precisely the **point stabilizer**. The head coordinate was consumed before the mixin was reached, so whatever the sub-object does happens inside

$$\mathrm{Stab}(0) \;\cong\; S_{n-1} \;\le\; S_n, \qquad [S_n : S_{n-1}] = n$$

so a fraction $1/n$ of the orbit is repaired, degrading with rank: $1/2$ for edges, $1/3$ for triangles, $1/4$ for tetrahedra.

**This is not a Python limitation.** The sub-object does not fail to mirror coordinate $0$ for want of a hook — it lacks the *information*. `h[1]` is reached by consuming `1`, and nothing in the resulting object records what was consumed. No metaclass, descriptor or `__init_subclass__` can synthesise a value that was never stored.

So propagate for **type honesty** — the link of an undirected object genuinely is undirected, and typing it `Graph` is a lie — never for the invariant. Doing it *automatically* is also expressible, but it resurrects the anonymous-class and pickle-qualname machinery deleted with `of`, to buy $1/n$.

**What would actually repair it** is supplying the missing prefix. Three mechanisms, none free:

| mechanism | how the prefix arrives | cost |
| --- | --- | --- |
| back-pointer on the child | stamped at insertion; walk to the root | derived sets (`~s`, `s \| t`, `abs`) are unbound, so one class has two modes |
| proxy returned by `__getitem__` | carried by the view | breaks `is` identity and the storage model |
| order-free canonical key | no prefix needed — one slot per orbit | flattens the store, per the table above |

The back-pointer is more feasible than it looks, because **a stored child has exactly one parent** — verified:

```txt
g2['x'] = g1['u']            g2['x'] is g1['u']  ->  False    __setitem__ coerces through truth, so it copies
g2.update({'x': g1['u']})    copies too
s = g1['u']; s['w'] = x      writes through                   reads return the reference
```

Assignment copies, reads alias. So ownership is unique and a parent link would be well defined. The objection is not cycles but semantics: `s = g['u']; s[...] = x` would silently mutate distant parts of `g`.

### The mixin is base-agnostic

The mirroring **algorithm** needs nothing from `Node` — verified against a plain `dict`:

```python
class Mirror:
    def __setitem__(self, key, value):
        if isinstance(key, Edge):
            for edge in key.permutations: super().__setitem__(edge, value)
        else: super().__setitem__(key, value)

class Bag(Mirror, dict): ...
```

```txt
b[Edge(1,2,3)] = "x"   ->   6 keys, every ordering
```

Only the **declaration** is tied to `Node`, which `Undirected` names so it can `super()`:

```txt
class UBag(Undirected, Bag): ...
UBag()   ->   AttributeError: 'UBag' object has no attribute 'truth'
```

With the graded family withdrawn there is a single container to mix into, so this costs nothing today. It stays recorded because it says what a future second container would cost: a base class, never a second algorithm.

---

## 9. Known open ends

**Implementation status.** §4's `contracted` and all of §6 are built and verified: tuple-as-path, the rank law across nine forms, both sentinel spellings, bounded-slice rejection, sentinel rejection on writes and deletes, `Undirected` mirroring plain tuples, and every worked example in §7 and §8 running in the notation as written. `route` is gone. Pyright reports $0$ errors and pylint $10.00/10$.

**Orientation is out of scope, deliberately.** An *oriented* complex assigns $\pm 1$ by permutation parity, and boundary maps need that sign. `Prob` and `Bool` are a bounded lattice and a projective line — **neither has negation** — so orientation, boundary maps and anything homological are not expressible without a second, signed carrier.

That is not a gap here, because the model takes the **directed** reading instead: each ordering is an independent cell with its own weight. Directed is strictly more information than oriented, and `Undirected` recovers the symmetric case by mirroring. What is given up is the *alternating* case in between, and with it homology. Worth knowing before anyone reaches for $\partial$.

**Whether degenerate cells are idiomatic.** `t[4,5,5]` records a whisker edge and borders correctly (§7), but nothing says a repeated coordinate *must* mean degeneracy rather than a genuine self-incidence. Settle before the sentinel lands, since both touch the same reading of an `Edge`.

**Tuple keys are withdrawn, and that is the one real narrowing.** §6 buys uniform notation by spending `tuple`, `None` and `slice` out of $K$. `IndexSet()[(0,0)] = True` and `g['u','v'] = x` both change meaning. The `Key` wrapper restores the case, but it is a wrapper, not the native behaviour, and it is the cost worth revisiting if it bites.

**The rank does not enter the type, so the return union stays.** An earlier draft claimed the addressing rule would retire `Set[V, E] | E`; that was wrong, and the reason is worth recording so it is not re-attempted. Under the rank law $r - k$, the result type depends on the *length* of a runtime subscript, and:

- **depth is a runtime `int`** — `IndexSet` and `UnweightedGraph` are both `Set[K, Bool]`, and the registry indexes by a plain integer, so $r$ is not in the type;
- **Python has no type-level arithmetic** — even with $r$ pinned as a `Literal`, no annotation can express "rank $r - k$";
- **overloads reach only fixed-length tuples** — `tuple[K]`, `tuple[K, K]` and so on cover a few cases, never the general one.

So `Set[V, E] | E` is the honest return type, and the only exact narrowing available is a per-rung override on the depth-0 rungs, where the union has just the one arm. That is a local patch, not a resolution.

**`Undirected`'s set and delete contracts are the one accessor-side open end.** Everything else in §6 is settled: reads fold, writes descend, `route` folds into `__getitem__`, and sentinels are rejected on writes. What remains is maintaining the orbit invariant across `__setitem__` and `__delitem__` — deliberately left open.

**`Undirected`'s invariant cannot be enforced.** Verified — three of five ordinary mutations leave it asymmetric:

```txt
u['a','b'] = 0.75            symmetric   -- one call, the mixin sees the pair
u['a']['b'] = 0.75           NOT         -- two calls, it never does
u['a'] = {'b': 0.5}          NOT
del u['a']  (after an edge)  NOT
```

**This is exactly where §6's identity fails.** `g[x_0, x_1]` and `g[x_0][x_1]` agree for every read, but the first is one call and the second is two, so anything that intercepts `__setitem__` sees only the first:

```txt
u['u','v'] = 3/4      ->   ('u','v') 0.75    ('v','u') 0.75
u['u']['v'] = 3/4     ->   ('u','v') 0.75    ('v','u') 0.0
```

So tuple keying and rung keying are the same operation but not the same *interception point*, and the invariant lives on the difference. Propagating the mixin down the tower repairs a $1/n$ fraction and no more — see §8.

**Reads autovivify, so presence cannot be probed by reading.** A consequence of `defaultdict` that every contract phrased in terms of presence has to respect:

```txt
g = Graph()                 len 0
_ = g['u','v']              len 1,  g == {'u': {}}
('u','v') in g              False,  and len 1
```

`Node.__contains__` is `bool(self[key])`, so **`in` mutates the set**. Any presence test must walk `dict.__contains__` along the path instead. A non-mutating `__contains__` is available for the asking, at the cost of no longer routing through `__getitem__`.

**`Undirected.__delitem__` is not atomic, and fails non-deterministically.** `Edge.permutations` returns a **`set`**, so the loop's order is hash-dependent. On a rank-3 tensor with one ordering already missing:

```txt
before   5/6 present
del h[1,2,3]         ->   KeyError: 2        the sub-coordinate, not the edge
after    1/6 present                          survivor (2,3,1), arbitrary
```

Four orderings deleted, one left standing, and which one is not reproducible. Contract to adopt:

```txt
del s[edge]   removes every present ordering of the orbit
              raises KeyError(edge) iff none was present
              never partially applies
```

Two-phase — collect the present orderings with `dict.__contains__`, then delete — which buys atomicity and order-independence together, and lets the error name the edge the caller passed.

**Repository debt.** `tests/` is empty; the whole verification suite (256-pair sweep against builtin `set`, `abs` self-duality, the symmetric set-vs-scalar comparison pairs, copy/deepcopy/pickle, and now the contraction laws of §4) lives in throwaway scripts. `src/addons/__init__.py` is empty.
