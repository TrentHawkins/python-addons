# python-addons
Contains additional fundamental datatypes built solely from the foundational `bool`, `int`, `float`, `list`, `tuple`, `set` and `dict` data types as well as borrowing from `complex` and `collections` as necessary.

The initial implementation focuses on small, composable algebraic building
blocks:

- structural min/max-style protocols expressed as `meet`, `join` and
  `complement`
- generic helpers that work across ordered values and sets
- a bounded-set implementation for container algebra
- a probability type whose operations satisfy De Morgan style identities
