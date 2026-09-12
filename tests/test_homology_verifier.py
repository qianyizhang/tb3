"""Certificate acceptance and rejection independently of any solver algorithm."""
import copy
from pathlib import Path
import types
import unittest


PATH = Path(__file__).resolve().parents[1] / "probes/homology-basis/tests/verifier.py"
# Read the frozen probe without creating cache files inside its task snapshot.
verifier = types.ModuleType("homology_verifier")
exec(compile(PATH.read_text(), str(PATH), "exec"), verifier.__dict__)


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.request = {"A": [[2, -1]], "B": [[3], [6]]}
        self.output = {"basis": [[1, 0], [2, 1]], "boundary_basis": [[1]],
                       "kernel_rank": 1, "factors": [3]}

    def test_primitive_cycle_and_opposite_sign_are_accepted(self):
        verifier.check(self.request, self.output)
        self.output["basis"] = [[-1, 0], [-2, 1]]
        self.output["boundary_basis"] = [[-1]]
        verifier.check(self.request, self.output)

    def test_rational_kernel_with_missing_integral_cycles_is_rejected(self):
        self.output["basis"] = [[3, 0], [6, 1]]
        self.output["factors"] = [1]
        with self.assertRaisesRegex(ValueError, "unimodular"):
            verifier.check(self.request, self.output)

    def test_changed_image_lattice_is_rejected(self):
        self.output["boundary_basis"] = [[2]]
        self.output["factors"] = [6]
        with self.assertRaisesRegex(ValueError, "unimodular"):
            verifier.check(self.request, self.output)

    def test_incomplete_kernel_and_wrong_torsion_are_rejected(self):
        for mutate, message in [
            ({"kernel_rank": 0, "factors": []}, "incomplete"),
            ({"factors": [2]}, "identity"),
            ({"factors": []}, "identity"),
            ({"factors": [True]}, "integer"),
        ]:
            output = copy.deepcopy(self.output)
            output.update(mutate)
            with self.subTest(mutate=mutate), self.assertRaisesRegex(ValueError, message):
                verifier.check(self.request, output)

    def test_nondividing_diagonal_is_rejected(self):
        request = {"A": [[0, 0]], "B": [[6, 0], [0, 10]]}
        output = {"basis": [[1, 0], [0, 1]], "boundary_basis": [[1, 0], [0, 1]],
                  "kernel_rank": 2, "factors": [6, 10]}
        with self.assertRaisesRegex(ValueError, "divisibility"):
            verifier.check(request, output)

    def test_injective_and_zero_boundaries(self):
        for a, b, z, factors in [([[-7]], [[0]], 0, []),
                                ([[0]], [[0]], 1, []),
                                ([[0]], [[1]], 1, [1])]:
            verifier.check({"A": a, "B": b}, {"basis": [[1]], "boundary_basis": [[1]],
                                              "kernel_rank": z, "factors": factors})


if __name__ == "__main__":
    unittest.main()
