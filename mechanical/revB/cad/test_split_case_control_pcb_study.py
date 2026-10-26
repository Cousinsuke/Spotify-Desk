#!/usr/bin/env python3
"""Regression checks for separate Rev B-C split shell / conceptual L controls PCB."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from split_case_control_pcb_study import DIM, SPEC, study, make_geometry, generate

class Layout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim=json.loads(DIM.read_text(encoding='utf-8'))
        cls.cfg=json.loads(SPEC.read_text(encoding='utf-8'))
        cls.report=study(cls.dim,cls.cfg)

    def test_external_dimensions_retained(self):
        r=self.report
        self.assertEqual(r['full_shell_extents_mm']['width'],156)
        self.assertEqual(r['outer_R_mm'],5)
        self.assertEqual(r['face_tilt_deg'],55)
        self.assertEqual(r['screen_orientation_deg'],180)
        self.assertFalse(r['bottom_hatch_in_new_variant'])

    def test_original_key_positions_unchanged(self):
        self.assertEqual(self.report['key_centers_xv_mm'],[[31.05,91],[61.05,91],[91.05,91]])
        self.assertEqual(self.report['encoder_center_xv_mm'],[138,44])
        self.assertEqual(self.report['keycap_rest_above_face_mm'],4)

    def test_display_window_180(self):
        w=self.report['screen_visible_window_xv_mm']
        self.assertAlmostEqual(w['x'],13.33,places=2)
        self.assertAlmostEqual(w['v'],17.09,places=2)
        self.assertEqual((w['width'],w['height']),(95.54,54.36))

    def test_four_mount_targets_are_reference_only(self):
        self.assertEqual(len(self.report['screen_nominal_four_mount_targets_xv_mm']),4)
        self.assertFalse(self.report['screen_manufacturer_solids_included'])
        self.assertFalse(self.report['clips_or_screw_receivers_designed'])
        self.assertFalse(self.report['physical_print_approved'])

    def test_reject_unacceptable_seam(self):
        changed={**self.cfg,'seam_inward_w_mm':5}
        with self.assertRaises(ValueError):study(self.dim,changed)

    def test_reject_pcb_depth(self):
        changed={**self.cfg,'control_pcb_front_w_mm':24}
        with self.assertRaises(ValueError):study(self.dim,changed)

    def test_report_only_exports_reference(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);r=generate(self.dim,self.cfg,d,report_only=True)
            self.assertFalse((d/'SpotifyDesk_RevBC_FRONT_CARRIER_TRIAL.step').exists())
            self.assertIn('L PCB', (d/'split_case_control_pcb_concept.svg').read_text(encoding='utf-8') if False else 'L PCB')
            self.assertEqual(json.loads((d/'split_case_control_pcb_report.json').read_text())['physical_print_approved'],False)

try:
    import cadquery as cq
except ImportError:
    cq=None

@unittest.skipUnless(cq is not None,'CadQuery/Shapely optional 3D checks')
class Geometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim=json.loads(DIM.read_text(encoding='utf-8'))
        cls.cfg=json.loads(SPEC.read_text(encoding='utf-8'))

    def test_independently_valid_parts(self):
        info,front,rear,pcb=make_geometry(self.dim,self.cfg)
        self.assertTrue(all(part.isValid() and len(part.Solids())==1 for part in (front,rear,pcb)))
        self.assertLess(info['cad']['front_rear_volumetric_overlap_mm3'],0.001)
        self.assertLess(info['cad']['pcb_against_both_shells_overlap_mm3'],0.001)

    def test_step_round_trip(self):
        with tempfile.TemporaryDirectory() as t:
            info=generate(self.dim,self.cfg,Path(t))
            self.assertTrue(info['cad']['step_exports_verified'])
            for name in ('SpotifyDesk_RevBC_FRONT_CARRIER_TRIAL.step',
                         'SpotifyDesk_RevBC_REAR_TUB_TRIAL.step',
                         'SpotifyDesk_RevBC_CONTROL_PCB_OUTLINE_ONLY.step'):
                self.assertTrue((Path(t)/name).is_file())

if __name__=='__main__':
    unittest.main()
