"""Quick regression tests: python -m unittest mechanical.revB.cad.test_fit_audit"""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from fit_audit import audit, make_svg


class RevBFitAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim=json.loads((HERE/"dimensions.json").read_text(encoding="utf-8"))

    def test_centred_row(self):
        a=audit(self.dim,14)
        self.assertAlmostEqual(a["key_row_center_error_mm"],0)
        self.assertAlmostEqual(a["lcd_to_keycap_gap_mm"],6.2)

    def test_14mm_original_hypothesis(self):
        a=audit(self.dim,14)
        self.assertAlmostEqual(a["lateral_gap_mm"],3.3)
        self.assertTrue(a["meets_trial_2d_guard"])

    def test_20mm_cable_requires_more_space(self):
        a=audit(self.dim,20)
        self.assertFalse(a["meets_trial_2d_guard"])
        self.assertAlmostEqual(a["extra_knob_shift_mm"],4.7)
        self.assertAlmostEqual(a["width_if_shift_knob_and_right_edge_mm"],160.7)

    def test_negative_inputs_rejected(self):
        with self.assertRaises(ValueError): audit(self.dim,-2)
        with self.assertRaises(ValueError): audit(self.dim,14,-1)

    def test_svg_does_not_claim_physical_verification(self):
        self.assertFalse(audit(self.dim,14)["physical_fit_verified"])
        svg=make_svg(self.dim,14)
        self.assertIn("NOT physical connector geometry",svg)
        self.assertIn("156 x 110 mm",svg)


if __name__=="__main__":
    unittest.main()
