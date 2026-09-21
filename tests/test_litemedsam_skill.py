"""Input contract tests without optional imaging libraries or model inference."""

import unittest

from tb3_medical.skills.litemedsam.scripts.segment import validate_boxes


class LiteMedSAMContractTests(unittest.TestCase):
    def test_nonsquare_image_uses_xy_and_exclusive_upper_bounds(self):
        boxes = [[0, 0, 200, 80], [130.5, 4, 190, 79]]
        self.assertEqual(validate_boxes(boxes, 200, 80), boxes)
        with self.assertRaises(ValueError):
            validate_boxes([[0, 0, 80, 200]], 200, 80)

    def test_invalid_prompts_fail_instead_of_clipping_or_swapping(self):
        for boxes in (
            [],
            [[0, 0, 0, 5]],
            [[9, 0, 4, 5]],
            [[-1, 0, 4, 5]],
            [[0, 0, 11, 5]],
            [[0, 0, float("nan"), 5]],
            [[0, 0, float("inf"), 5]],
            [[False, 0, 4, 5]],
            [[0, 0, "4", 5]],
            [[0, 0, 4]],
            {"box": [0, 0, 4, 5]},
        ):
            with self.subTest(boxes=boxes), self.assertRaises(ValueError):
                validate_boxes(boxes, 10, 10)
