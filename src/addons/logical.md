# `logical.py` — exact logical value algebras and their containers

Working notes for `src/addons/logical.py`. Records what the module is, what is built, what holds, and the decided direction for sub-dimensional linkage.

---

## 1. What this is

Two things, stacked:

1. **A scalar algebra** of logical values carried as exact rational coordinates on the projective line $\mathbb{P}^1(\mathbb{Q})$ — no floats, no rounding.
2. **A container algebra** whose members carry those values, and whose containers are themselves values in the same algebra, so nesting closes.

The second is the point. `Set` is a `Boolean`, so a `Set` can be the value type of another `Set`, and that recursion is what makes graphs, hypergraphs and complexes expressible in one vocabulary.

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

---

## 4. The container

`Set[K, T: Coded = Bool, V: Boolean = T]` over `defaultdict[K, V]`.

- `truth: type[V]` — the carrier. What an unrecorded key is, and what any value becomes.
- **A `Set` is a background plus recorded deviations.** `default` is the background; `complement` is a *reading* of it (`bool(self.default)`), not separate state.
- A background can be **graded**, not just a bound: `FuzzySet(Prob(1,2))` is the half-present set, and `abs` brings it back exactly.

### The seam, both directions

| direction | mechanism | contract |
| --- | --- | --- |
| `Set` → scalar | `abs` — the measure | `Boolean.__abs__` |
| scalar → `Set` | the background it *is* | `Set.__init__` |

The round trip is exact for every scalar $x$:

$$\bigl\lvert\, \mathrm{Set}(x) \,\bigr\rvert = x$$

Comparisons are authority-free — a set meets a scalar at the measure — so `set OP scalar` and `scalar OP.reflected set` always agree.

### The tower

`DeepSet[V, E: Coded = Bool](Set[V, E, "DeepSet[V, E] | E"])` — a set whose values are sets.

- `registry: pair[list[type[DeepSet]]]` — one dense list per polarity, indexed by depth.
- A rung declares its slot: `class Graph[V](DeepSet[V, Prob], weighted = True, depth = 1)`, and `__init_subclass__` derives `truth` from the rung below and claims the slot. Declaring and looking up name **one** class, never two.
- `arity()` $= \text{depth} + 1$ — how many coordinates the rung takes, derived from the `truth` chain.

| | depth 0 | depth 1 |
| --- | --- | --- |
| crisp | `IndexSet` | `UnweightedGraph` |
| graded | `FuzzySet` | `Graph` |

`type(Graph()["u"]) is FuzzySet` — a graph's neighbourhoods *are* the named sets.

---

## 5. Paths

`Edge[K](tuple[K, ...])` is a path, told apart from a key by being an `Edge`. A plain tuple stays a key — `IndexSet()[(0,0)] = True` still stores a tuple vertex.

`route(key) -> (holder, coordinate)` is the single resolution point; every accessor funnels through it and then acts at the storage layer. `Set.route` handles the base case (a `Set` is flat by declaration); `DeepSet.route` owns the descent, because that is where the value union `DeepSet[V, E] | E` is declared and can be narrowed exactly.

`Edge.permutations` yields the orderings, deduped, as `Edge`s — the input `Undirected` needs.

---

## 6. What already works, and is not obvious

On a depth-2 rung `g` with `g[Edge(1,2,3)] = Prob(3,4)`:

```txt
g[Edge(1,2,3)]      ->  0.75            the triangle's weight
g[Edge(1,2)]        ->  {3: 0.75}       the LINK of the edge (1,2)
g[1]                ->  {2: {3: 0.75}}  the link of the vertex 1
g[1][Edge(2,3)]     ==  g[Edge(1,2,3)]  True
```

**A short path already gives the link (star) of a face.** That is a real and useful semantic that falls out of routing, and three of the four examples in the design discussion already hold.

Two premises worth correcting:

- **A 1-tuple subscript is expressible.** `g[1,]` is `g[(1,)]`. So `Edge` is not constrained to length $\geq 2$ by syntax — `Edge(1)` is legal and already means "the link of vertex 1".
- **Modulo cyclic rotation there are 2 orientations** of a triangle, $|S_3| / |C_3| = 2$ — correct. But see §8 on why orientation is deliberately out of scope.

---

## 7. Sub-dimensional linkage

**The gap, precisely:** the current model is *one* adjacency tensor of rank $d + 1$, that is a single map

$$A_d \colon K^{\,d+1} \longrightarrow E$$

It stores only top-dimensional cells. A face has a **derived** weight ($\lvert\,\cdot\,\rvert$ of its link) but nowhere to keep an **independent** one. A depth-2 object cannot say "this triangle weighs $\tfrac{3}{4}$ *and* its side $(1,2)$ weighs $\tfrac{3}{10}$ for unrelated reasons".

```txt
g[Edge(1,2)] is a FuzzySet   -- a container, not a scalar slot
abs(g[Edge(1,2)]) == 0.75    -- derived from the triangle, not independent
```

### Decided: a graded family, kept directed

A `Complex` of dimension $d$ owns **one existing rung per dimension** — the graded family

$$\bigl(A_k \colon K^{\,k+1} \to E\bigr)_{k=0}^{d}$$

where $A_k$ is a `DeepSet` of depth $k$. `DeepSet` is untouched; the algebra lifts componentwise, so for any lattice operation $\ast$ we have $(g \ast h)_k = g_k \ast h_k$.

**Cells are ordered.** Each permutation of a tuple is its own cell with its own weight, at every dimension — the fully directed case. `Undirected` collapses them by mirroring, per dimension. No sign is involved anywhere (see §8).

### The one notational rule

**A single key descends. An `Edge` addresses a cell.**

| written | means | reaches |
| --- | --- | --- |
| `g[1]` | the **link** of $1$ — a `Complex` of dimension $d - 1$ | $\mathrm{Complex}(A_1[1], \dots, A_d[1])$ |
| `g[Edge(1)]` | the **weight** of the vertex $1$ | $A_0$ |
| `g[Edge(1,2)]` | the **weight** of the edge $(1,2)$ | $A_1$ |
| `g[Edge(1,2,3)]` | the **weight** of the triangle | $A_2$ |
| `g.link(edge)` | readability helper for the descent | same as chained single keys |

That is the whole of it — no second accessor, no length heuristic. `Edge`-vs-plain-key is exactly the notation needed, and it is the same disambiguation `Edge` was introduced for.

### Why the link is cheap

Because every $A_k$ is already *nested*, the link of $1$ in dimension $j$ is the **stored** sub-object $A_{j+1}[1]$. So `g[1]` gathers $d$ existing references — no restriction is computed:

$$g[1] = \bigl(A_{j+1}[1]\bigr)_{j=0}^{d-1} \qquad g[1][2] = \bigl(A_{j+2}[1][2]\bigr)_{j=0}^{d-2}$$

At dimension $-1$ the link degenerates to the weight, which is what makes the chain bottom out.

### The examples, resolved

```txt
g[1][2][3]        ==  g[Edge(1,2,3)]     the triangle's weight -- these AGREE
g[1][Edge(2,3)]   ==  g[Edge(1,2,3)]     also the triangle: Edge(2,3) inside the link of 1
g[Edge(2,3)]      !=  g[1][Edge(2,3)]    the edge's OWN weight, from A_1
g[Edge(1,2)]      ->  a scalar           the edge's weight
g[1][2]           ->  the link of (1,2)  the vertices triangulating with it
```

So is `g[1][2,3]` the same as `g[2,3]`? **No** — and that is the point of the design. The first is the triangle $(1,2,3)$ seen from inside the link of $1$; the second is the edge $(2,3)$'s independent weight. Different dimensions, different storage.

Note `g[1,2][3]` from the original sketch becomes `g[1][2][3]`: an `Edge` now lands on a *scalar*, which has no further subscript. The link is reached by single keys.

### What this costs

- **`Edge` is reinterpreted** from "path" to "cell address". Today a short `Edge` on a depth-2 rung gives the link; under `Complex` it gives that dimension's weight. Full-length edges are unaffected, so `g[Edge(1,2,3)] == g[1][2][3]` still holds.
- **Downward closure** (a cell implies its faces) becomes an invariant that is *not* enforced — same class of problem as `Undirected`'s symmetry in §8.

### Rejected alternatives

**Keep the pure tensor.** Depth $d$ models $d$-simplices only, faces stay derived slices. Zero rework, but no independent sub-dimensional weights and no mixed-dimension complexes.

**A weight at every node.** Each slot holds *(weight, children)* rather than weight *or* children, so `V` becomes a product instead of the union `DeepSet[V, E] | E`. Most faithful to "partial keying yields sub-dimensional topology", and one walk reaches everything — but the largest rework: `abs` must combine own-weight with children, and the union typed exactly over several passes becomes a pair. The graded family reaches the same expressiveness by composition.

---

## 8. Known open ends

**Orientation is out of scope, deliberately.** An *oriented* complex assigns $\pm 1$ by permutation parity, and boundary maps need that sign. `Prob` and `Bool` are a bounded lattice and a projective line — **neither has negation** — so orientation, boundary maps and anything homological are not expressible without a second, signed carrier.

That is not a gap here, because the model takes the **directed** reading instead: each ordering is an independent cell with its own weight, at every dimension. Directed is strictly more information than oriented (which records only a sign), and `Undirected` recovers the symmetric case by mirroring. What is given up is the *alternating* case in between, and with it homology. Worth knowing before anyone reaches for $\partial$.

**`Undirected`'s invariant cannot be enforced.** Verified — three of five ordinary mutations leave it asymmetric:

```txt
u[Edge('a','b')] = 0.75      symmetric
u['a']['b'] = 0.75           NOT   -- u['a'] is a plain FuzzySet; the mixin never sees it
u['a'] = {'b': 0.5}          NOT
del u['a']  (after an edge)  NOT
```

The middle case is the natural way to write an edge, and it bypasses the mixin for the same reason `Edge` had to exist: no per-level hook ever sees a whole path.

**`Undirected.__delitem__` is not atomic.** Deleting orderings in a loop can raise partway, having already mutated. Proposed contract: *raise `KeyError` iff no ordering is present; otherwise remove every ordering that is* — strict where `del` must be, self-healing where the invariant was already broken, and it forces nothing on `Set.__delitem__`.

**Repository debt.** `tests/` is empty; the whole verification suite (256-pair sweep against builtin `set`, `abs` self-duality, the symmetric set-vs-scalar comparison pairs, copy/deepcopy/pickle) lives in throwaway scripts. `src/addons/__init__.py` is empty.
