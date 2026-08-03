import unittest

from python_addons import BoundedSet, LogicInt, Probability, complement, join, meet


class MinMaxTests(unittest.TestCase):
    def test_ordered_values_use_min_and_max(self) -> None:
        self.assertEqual(meet(3, 5), 3)
        self.assertEqual(join(3, 5), 5)

    def test_plain_sets_use_intersection_and_union(self) -> None:
        self.assertEqual(meet({1, 2}, {2, 3}), {2})
        self.assertEqual(join({1, 2}, {2, 3}), {1, 2, 3})


class LogicIntTests(unittest.TestCase):
    def test_logic_int_reuses_int_for_boolean_algebra(self) -> None:
        left = LogicInt(0)
        right = LogicInt(1)

        self.assertEqual(join(left, right), LogicInt(1))
        self.assertEqual(meet(left, right), LogicInt(0))
        self.assertEqual(complement(left), LogicInt(1))
        self.assertEqual(complement(right), LogicInt(0))


class ProbabilityTests(unittest.TestCase):
    def test_probability_is_bounded(self) -> None:
        with self.assertRaises(ValueError):
            Probability(2)

    def test_probability_accepts_plain_values_on_either_side(self) -> None:
        self.assertEqual(meet(Probability(0.25), 0.6), Probability(0.15))
        self.assertEqual(meet(0.6, Probability(0.25)), Probability(0.15))
        self.assertAlmostEqual(join(0.6, Probability(0.25)), Probability(0.7))

    def test_probability_satisfies_de_morgan_laws(self) -> None:
        left = Probability(0.25)
        right = Probability(0.6)

        self.assertEqual(complement(join(left, right)), meet(complement(left), complement(right)))
        self.assertAlmostEqual(
            complement(meet(left, right)),
            join(complement(left), complement(right)),
        )


class BoundedSetTests(unittest.TestCase):
    def test_bounded_set_satisfies_de_morgan_laws(self) -> None:
        universe = {1, 2, 3, 4}
        left = BoundedSet({1, 2}, universe)
        right = BoundedSet({2, 3}, universe)

        self.assertEqual(complement(join(left, right)), meet(complement(left), complement(right)))
        self.assertEqual(complement(meet(left, right)), join(complement(left), complement(right)))


if __name__ == "__main__":
    unittest.main()
