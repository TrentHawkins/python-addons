"""Listings for the paper in `main.lyx`, one file per stage of the buildup.

`main.lyx` includes these files verbatim, so the manuscript always displays the code as it
currently stands. They are checked by pyright and pylint alongside the library, and they build
on one another by relative import in the order the text introduces them.
"""


from .group import Magma, Semigroup, Monoid, Group
from .abelian import Abelian, AbelianGroup
from .preorder import Preorder
from .partial import Partial
from .total import Total
