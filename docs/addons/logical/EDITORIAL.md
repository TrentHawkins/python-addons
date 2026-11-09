# Paper decisions and review notes

Working record, 2026-11-09. The manuscript is `main.lyx`; the bibliography is
`main.bib`. This record distinguishes the author's decisions from proposals.
The manuscript and bibliography were not changed during this review.

## Agreed direction

- Address a mathematically knowledgeable reader with concise, concentrated prose.
- Prefer notation where it expresses a notion more precisely and economically;
  introduce the notation needed by later arguments.
- Develop the mathematics independently of the current library implementation.
  Programming problems may motivate definitions without determining their form.
- If Python illustrations are retained, use `typing.Protocol` contracts rather
  than concrete implementations. Keep standard typing names qualified by `typing`.
- The repository will accompany the paper and be referenced from it.
- Seek one principal textbook as a consistent reference for foundational
  terminology, definitions, and presentation.
- Select that reference for the classical foundational material itself, not
  for the library's eventual direction. Prefer a concrete classical development
  over a specialist universal-algebra framework for this purpose.

## Open decisions

- Whether to include code, and whether it belongs inline, at section ends, or in
  an appendix. No existing listings have been removed or relocated.
- Which principal reference to adopt. The shortlist below is not yet an
  author-approved bibliographic choice; `main.bib` remains empty.
- Membership versus typing notation: an earlier preference was `x : X`, whereas
  this revised draft uses `x ∈ X`. Do not silently impose either throughout.

## Current reference brief: classical foundations first

The author's refined scope supersedes the earlier universal-algebra-oriented
ranking below. The draft showcases the desired level and connections; it is
not a reason to anticipate later library-specific mathematics.

Desired progression: sets; relations; maps as suitably constrained relations;
subsets represented by characteristic maps and the corresponding representation
of relations; equivalence relations, partitions, and quotients; orders; then
classical algebraic structures through fields and vector spaces. Lattices and
related topics may follow, but should not organize the initial development.

### Hungerford — current leading Springer candidate

Thomas W. Hungerford, *Algebra*, Graduate Texts in Mathematics 73,
[Springer](https://link.springer.com/book/10.1007/978-1-4612-6101-8).

The introduction covers sets/classes, functions, relations/partitions,
products, and order. The main text develops groups, rings, modules, fields,
and linear algebra. This makes it a strong classical reference candidate,
without requiring universal algebra as the organizing subject.

**Caveats:** it is a graduate-level reference, not a brief elementary textbook;
the introductory material is compressed. The exact treatment of every desired
bridge, especially characteristic maps, remains to be checked in the text.
The [publisher's front matter and contents](https://link.springer.com/content/pdf/bfm:978-1-4612-6101-8/1)
establish the overall coverage, not that every connection is developed in the
author's preferred form or sequence.

### Mac Lane and Birkhoff — broader classical alternative

Saunders Mac Lane and Garrett Birkhoff, *Algebra*, third edition (1988;
AMS Chelsea Publishing). This is distinct from their *A Survey of Modern Algebra*.

The opening includes sets, functions, relations, binary operations, equivalence
relations, quotient sets, semigroups, and monoids. Subsequent chapters treat
groups, rings, modules, vector spaces, and fields. See the
[authors' preface and contents reproduced by MacTutor](https://mathshistory.st-andrews.ac.uk/Extras/Birkhoff_books/).

**Caveat:** Chapter IV introduces universal constructions, categories, posets,
and lattices before vector spaces, despite a later dedicated lattice chapter.
It is therefore a coverage candidate, not an exact match to the requested order
or avoidance of additional abstraction. The precise characteristic-map treatment
also remains unverified.

These are recommendations for inspection, not adopted bibliography entries.
The next comparison should test the classical preliminaries and basic
structures, including the requested relation/function/indicator connections,
rather than prioritize closure, lattice theory, or the eventual library design.

## Earlier annotated shortlist (background references)

These are candidates, not adopted references. Coverage was checked against
publisher contents and available introductory material; the fit assessments
below are editorial recommendations, not a full stylistic comparison of the
books. They reflect the earlier, broader brief and no longer set the priority
for the principal reference. Distinguish a mathematical authority from a model
for presentation.

### Burris and Sankappanavar — the original recommendation

Stanley N. Burris and H. P. Sankappanavar, *A Course in Universal Algebra*,
Springer, Graduate Texts in Mathematics 78 (1981).

- [Publisher record](https://link.springer.com/book/9781461381327).
- [Author-hosted corrected 2012 edition](https://math.uwaterloo.ca/~snburris/htdocs/ualg.html),
  freely available for non-commercial educational use. The authors report that
  it preserves the original edition's pagination.
- Useful locations: Preliminaries, pp. 1–2 (sets, relations, functions);
  I §1 (orders and lattices); I §4 (equivalence relations and partitions);
  I §5 (closure operators); II §§1–3 (operations, algebras, subalgebras, generation).

**Fit:** a strong single-reference candidate for the progression through orders,
lattices, closure, and general operations. Its concise preliminaries suit a
knowledgeable audience.

**Limitation:** elementary set theory is assumed rather than developed
axiomatically. It gives less space to the opening sets/functions foundations
than Cohn does.

### Cohn — the strongest challenger for foundational continuity

P. M. Cohn, *Universal Algebra* (1981; D. Reidel, now available through
[Springer](https://link.springer.com/book/10.1007/978-94-009-8399-1)).

**Coverage:** “Sets and Mappings,” pp. 1–40, followed by “Algebraic Structures,”
pp. 41–107; later chapters include relational structures and models. Cohn
describes the intended audience as users of universal algebra, rather than
only specialists.

**Fit:** a particularly promising single reference for continuity from the
paper's elementary foundations into general algebraic structures.

**Limitation:** the opening includes set/class distinctions and axioms, more
foundational machinery than the paper probably needs to reproduce.

### Grätzer — the classical reference-work option

George Grätzer, *Universal Algebra*, second edition (1979), with updates in
the [2008 Springer edition](https://link.springer.com/book/10.1007/978-0-387-77487-9).

**Coverage:** basic concepts, subalgebras, homomorphisms, partial algebras,
constructions, free algebras, and model theory, with extensive appendices.

**Fit:** a strong candidate when classical reference-work depth is the priority.
The explicit treatment of partial algebras could be useful if operations that
are not everywhere defined become part of the mathematical development.

**Limitation:** much of the specialist material exceeds the paper's current
needs. Use selectively rather than adopting the overall organization.

### Clifford Bergman — a modern operations-first comparator

Clifford Bergman, *Universal Algebra: Fundamentals and Selected Topics*
(2012; [Chapman & Hall/CRC](https://www.routledge.com/Universal-Algebra-Fundamentals-and-Selected-Topics/Bergman/p/book/9780429108082)).

**Coverage:** operations and algebras, generated subalgebras, congruences, then
orders, lattices, closure operators, and Galois connections.

**Fit:** a useful modern alternative for organizing the exposition around
operations and their structural consequences.

**Limitation:** its destination is research in universal algebra, rather than
a comprehensive treatment of elementary sets and functions.

### Halmos — the focused set-theoretic foundation

Paul R. Halmos, *Naive Set Theory*
([Springer, Undergraduate Texts in Mathematics](https://link.springer.com/book/10.1007/978-1-4757-1645-0)).

**Coverage:** sets, relations, functions, images, inverses, composition,
families, and order. The stated aim limits philosophical and logical overhead.

**Fit:** a particularly direct reference for the opening sets–relations–functions
material, and a candidate to inspect for concise foundational exposition.

**Limitation:** not sufficient as the sole reference once general algebraic
operations and structures become central.

### Davey and Priestley — the ordered-structure foundation

B. A. Davey and H. A. Priestley, *Introduction to Lattices and Order*,
second edition (2002; [Cambridge University Press](https://www.cambridge.org/core/books/introduction-to-lattices-and-order/946458CB6638AF86D85BA00F5787F4F4)).

**Coverage:** ordered sets, lattices as both orders and algebras, Boolean
lattices, Galois connections, and fixed points.

**Fit:** especially relevant to the ordered and set-like side of the project;
a potential specialist reference if those notions dominate the development.

**Limitation:** does not replace a general sets/functions/algebra reference.

### Earlier comparison plan (superseded)

Retained as context for the earlier shortlist; use the classical-foundations
brief above for the current search.

For one principal reference, compare these three first:

1. **Cohn:** continuity from sets and mappings into algebraic structures.
2. **Burris–Sankappanavar:** the progression through lattices, closure, and
   general operations.
3. **Grätzer:** classical reference-work depth.

Keep Bergman as the modern operations-first alternative. Halmos and
Davey–Priestley are stronger candidates for narrower roles than for the full
single-book requirement. None of these choices removes the need for specialist
sources for later claims outside its coverage.

Before choosing, compare the same four notions in the finalists:

- Functions, images, and inverse images.
- Equivalence relations and quotients.
- Partial orders.
- Closure under operations and generated structures.

Assess whether each definition can be adopted with little additional
scaffolding, whether the conventions remain compatible across the four topics,
and whether the exposition is concise without hiding necessary assumptions.
The proposed next inspection is Cohn's first two chapters alongside the
corresponding opening sections of Burris–Sankappanavar; it is not yet a completed
comparison or an author-approved selection.

## Proposed presentation

Keep the mathematical argument self-contained and put an optional, compact
protocol correspondence in an appendix. Section-end protocol summaries are the
fallback if reading the mathematics alongside Python becomes a primary aim.
Interleave code only where it contributes something not already said by a
signature and its laws. This is a recommendation, not a settled constraint.

Separate three layers: mathematical carrier and laws, representation, and
implementation requirements. In particular, hashability belongs to the last
layer, not to the definition of a mathematical set or equality.

The characteristic-function viewpoint already in the draft is useful on its
own: a relation `R ⊆ X × X` corresponds to `χ_R : X × X → {0, 1}`, with
`χ_R(x, y) = 1 ⇔ (x, y) ∈ R`. This supplies a mathematical bridge toward
graded relations without needing code. Changing the codomain alone does not
specify which logical operations and laws a graded relation will use.

## Current review findings (not yet applied)

- **Hashing and equality:** the opening identification is incorrect. Equal
  hashable values must have equal hashes; equal hashes need not imply equal
  values. `__eq__` does not generally delegate to `__hash__`. A mathematical
  carrier need not have hashable representations. See the
  [Python data model](https://docs.python.org/3/reference/datamodel.html#object.__hash__).
- **Function image:** in the definition of `f(A)`, the existential variable must
  range over `A`, not `X`: `f(A) = {f(a) : a ∈ A}`. As written, it always yields
  `f(X)`.
- **Function signature:** `f : X → Y` specifies a domain/codomain constraint,
  not the function itself. Python annotations alone establish neither totality
  nor purity.
- **Preorders:** the induced equivalence and quotient-order construction are
  sound. Define `[a]` and `X / ∼` before use. The strict part of a preorder is
  also sound; clarify that *when that preorder is antisymmetric*, the induced
  equivalence reduces to equality, rather than referring to an unspecified
  partial order as giving the same strict relation.
- **Strict total order:** use `<`, not `≤`, as its symbol. For distinct `a, b`,
  comparability requires `a < b or b < a`; the current `a < b or b > a`
  repeats the same condition.
- **Closure:** keep the ambient set consistently `X` rather than switching to
  undefined `S`. The operations initially take inputs from `X`; `A ⊆ X` is the
  subset being tested for closure. Specify the family of operations on which
  the closure depends, e.g. `cl_Ω(A)`. For binary operations,
  `cl_Ω(A) = ⋂{B ⊆ X : A ⊆ B and ∀ω ∈ Ω, ω(B × B) ⊆ B}`.
  The subtraction/division examples work with the stated carriers; define
  `Q*` and `Z*` as the nonzero elements and write `cl_{/}(Z*) = Q*`.
- **Protocol illustrations:** `Relation` and `Equivalence` currently inherit
  only `typing.Hashable`, not `typing.Protocol`; their `X` also needs a Python
  binding. If retained, make their protocol status and operand types explicit.
  See the [typing specification](https://typing.python.org/en/latest/spec/protocol.html#merging-and-extending-protocols).
- **Structure and economy:** merge the duplicate “Relations” subsections.
  Remove prose that immediately restates a displayed law unless it adds an
  interpretation. Use “operation” for maps on a carrier and “closure operator”
  for the map on its power set, making their different domains explicit.

## Listing conventions to preserve

- Preserve the custom minted/mdframed/tcolorbox styling and deliberate whitespace.
- Display listings use LyX **Smallest** (`\scriptsize`), not Tiny (`\tiny`),
  and the requested trailing blank line.
- Inline listings should inherit context-relative font scaling and raising,
  without a fixed size override. The current inline insets again contain
  `fontsize={\scriptsize}`; this is a discrepancy to revisit if code is kept,
  not permission to change formatting in an unrelated pass.

Update agreed decisions only when the author settles them. Keep recommendations
and outstanding review findings distinguishable from authorial choices.
