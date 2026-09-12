from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "probes/clipper-polytree/tests/verifier.py"
SPEC = importlib.util.spec_from_file_location("clipper_geometry_verifier", MODULE_PATH)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
# Importing a probe must not add bytecode to the task's frozen input tree.
previous_dont_write_bytecode = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    SPEC.loader.exec_module(verifier)
finally:
    sys.dont_write_bytecode = previous_dont_write_bytecode

SQUARE = [(0, 0), (8, 0), (8, 8), (0, 8)]


def rectangle(x: int, y: int, width: int = 2) -> list[tuple[int, int]]:
    return [(x, y), (x + width, y), (x + width, y + width), (x, y + width)]


def line(depth: int, ring: list[tuple[int, int]]) -> str:
    return f"{depth}|{'true' if depth % 2 else 'false'}|" + ";".join(
        f"{x},{y}" for x, y in ring
    )


class ClipperGeometryTests(unittest.TestCase):
    def test_closed_and_adjacent_duplicate_corners_are_preserved(self) -> None:
        duplicated = [point for point in SQUARE for _ in range(2)] + [SQUARE[0]] * 2
        expected = verifier.canonical_ring(SQUARE)
        self.assertEqual(len(expected), 4)
        self.assertEqual(verifier.canonical_ring(SQUARE + SQUARE[:1]), expected)
        self.assertEqual(verifier.canonical_ring(duplicated), expected)

    def test_ring_rotation_and_reversal_are_equivalent(self) -> None:
        expected = verifier.canonical_ring(SQUARE)
        for direction in (SQUARE, list(reversed(SQUARE))):
            for start in range(len(direction)):
                with self.subTest(direction=direction, start=start):
                    self.assertEqual(
                        verifier.canonical_ring(direction[start:] + direction[:start]), expected
                    )

    def test_collinear_samples_are_removed_after_closure_deduplication(self) -> None:
        sampled = [(0, 0), (4, 0), (8, 0), (8, 4), (8, 8), (0, 8), (0, 4), (0, 0)]
        self.assertEqual(verifier.canonical_ring(sampled), verifier.canonical_ring(SQUARE))
        diagonal = [(0, 0), (2, 2), (4, 4), (0, 4)]
        self.assertEqual(
            verifier.canonical_ring(diagonal),
            verifier.canonical_ring([(0, 0), (4, 4), (0, 4)]),
        )

    def test_collinear_reversal_and_backtracking_are_preserved(self) -> None:
        reversal = [(0, 0), (10, 0), (8, 0), (8, 8), (0, 8)]
        backtracking = [(0, 0), (8, 0), (4, 0), (8, 0), (8, 8), (0, 8)]
        for ring in (reversal, backtracking):
            expected = verifier.canonical_ring(ring)
            with self.subTest(ring=ring):
                self.assertEqual(len(expected), len(ring))
                self.assertNotEqual(expected, verifier.canonical_ring(SQUARE))
                for start in range(len(ring)):
                    rotated = ring[start:] + ring[:start]
                    self.assertEqual(verifier.canonical_ring(rotated), expected)
                    self.assertEqual(verifier.canonical_ring(list(reversed(rotated))), expected)

    def test_empty_and_degenerate_contours_fail_cleanly(self) -> None:
        for ring in ([], [(0, 0)], [(0, 0)] * 4, [(0, 0), (1, 0)],
                     [(0, 0), (1, 0), (2, 0)], [(0, 0), (2, 2), (0, 2), (2, 0)]):
            with self.subTest(ring=ring), self.assertRaisesRegex(verifier.Fail, 'degenerate contour'):
                verifier.canonical_ring(ring)

    def test_complete_sibling_subtrees_and_roots_are_unordered(self) -> None:
        outer, other = line(0, SQUARE), line(0, rectangle(20, 20))
        hole_a, hole_b = line(1, rectangle(1, 1)), line(1, rectangle(5, 5))
        island = line(2, rectangle(1, 1, 1))
        first = "\n".join([outer, hole_a, island, hole_b, other])
        reordered = "\n".join([other, outer, hole_b, hole_a, island])
        self.assertEqual(verifier.canonical(first), verifier.canonical(reordered))

    def test_reparenting_changes_topology_even_with_identical_contours(self) -> None:
        outer = line(0, SQUARE)
        hole_a, hole_b = line(1, rectangle(1, 1)), line(1, rectangle(5, 5))
        island = line(2, rectangle(1, 1, 1))
        nested_under_a = "\n".join([outer, hole_a, island, hole_b])
        nested_under_b = "\n".join([outer, hole_a, hole_b, island])
        self.assertNotEqual(verifier.canonical(nested_under_a), verifier.canonical(nested_under_b))

    def test_flattening_or_changing_geometry_does_not_match(self) -> None:
        outer = line(0, SQUARE)
        nested = outer + "\n" + line(1, rectangle(1, 1))
        flat = outer + "\n" + line(0, rectangle(1, 1))
        shifted = line(0, rectangle(1, 0, 8))
        self.assertNotEqual(verifier.canonical(nested), verifier.canonical(flat))
        self.assertNotEqual(verifier.canonical(outer), verifier.canonical(shifted))

    def test_malformed_tree_output_and_inconsistent_parity_fail_cleanly(self) -> None:
        for text in ("", "0|false|", "0|false|0,0;1,1;2,2", "0|false|0,0,0;1,0;0,1",
                     "0|false|0,0;;1,0;0,1", "invalid", line(1, SQUARE), line(-1, SQUARE),
                     line(0, SQUARE) + "\n" + line(2, rectangle(1, 1)),
                     line(0, SQUARE).replace("false", "true"),
                     line(0, SQUARE).replace("false", "maybe")):
            with self.subTest(text=text), self.assertRaises(verifier.Fail):
                verifier.canonical(text)

    def test_historical_suite_failure_and_timeout_are_diagnostic(self) -> None:
        for error in ("command failed: historical child index assertion", "cargo test timed out"):
            output = io.StringIO()
            with self.subTest(error=error), contextlib.redirect_stderr(output):
                with patch.object(verifier, "run", side_effect=verifier.Fail(error)) as run:
                    verifier.historical_diagnostic(Path('/candidate'), 1, 1, 150, Path('/target'))
                self.assertIn("--include-ignored", run.call_args.args[0])
                self.assertIn("non-gating", output.getvalue())
                self.assertIn(error, output.getvalue())


if __name__ == "__main__":
    unittest.main()
