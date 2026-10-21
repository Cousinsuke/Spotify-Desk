"""Run: python -m unittest discover -s mechanical/revB/cad -p 'test_*packaging.py' -v"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from internal_packaging import boxes, enclosure_margin, overlap, study, write_scad_params, world_yz

class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim=json.loads((HERE/'dimensions.json').read_text(encoding='utf-8'))
        cls.cfg=json.loads((HERE/'internal_packaging_assumptions.json').read_text(encoding='utf-8'))

    def test_centered_unchanged(self):
        self.assertEqual(study(self.dim,self.cfg)['screen_centered_key_row_mm'],0)
        self.assertEqual(self.dim['width'],156)

    def test_14mm_cable_no_encoder_body_overlap(self):
        parts={p.name:p for p in boxes(self.dim,self.cfg)}
        self.assertIsNone(overlap(parts['right_i2c_cable'],parts['encoder_body']))
        self.assertAlmostEqual(parts['encoder_body'].minimum[0]-parts['right_i2c_cable'].maximum[0],3.3)

    def test_20mm_cable_overlap_in_three_dimensions(self):
        import copy
        new=copy.deepcopy(self.cfg)
        new['assumptions']['i2c_extension']=20
        parts={p.name:p for p in boxes(self.dim,new)}
        intersection=overlap(parts['right_i2c_cable'],parts['encoder_body'])
        self.assertIsNotNone(intersection)
        self.assertAlmostEqual(intersection[0],2.7)
        self.assertGreater(intersection[1],0)
        self.assertGreater(intersection[2],0)

    def test_different_v_routing_removes_overlap(self):
        import copy
        new=copy.deepcopy(self.cfg)
        new['assumptions'].update(i2c_extension=20,i2c_v_start=60)
        parts={p.name:p for p in boxes(self.dim,new)}
        self.assertIsNone(overlap(parts['right_i2c_cable'],parts['encoder_body']))

    def test_nominal_usb_plug_enters_sharp_side_wall(self):
        parts={p.name:p for p in boxes(self.dim,self.cfg)}
        self.assertAlmostEqual(enclosure_margin(parts['left_usb_cable'],self.dim),-1,places=2)
        self.assertLess(enclosure_margin(parts['left_usb_cable'],self.dim),0)

    def test_side_face_transform(self):
        y,z=world_yz(0,0,self.dim)
        self.assertAlmostEqual(y,self.dim['front_face_length']*__import__('math').cos(__import__('math').radians(55)))
        self.assertAlmostEqual(z,self.dim['height'])
        y,z=world_yz(110,0,self.dim)
        self.assertAlmostEqual(y,0)
        self.assertAlmostEqual(z,self.dim['front_chin'])

    def test_provisional_report_no_false_fit_claim(self):
        out=study(self.dim,self.cfg)
        self.assertFalse(out['physical_fit_verified'])
        self.assertGreaterEqual(len(out['not_modelled']),6)

    def test_generated_scad_params_match_checked_in(self):
        expected=write_scad_params(self.dim,self.cfg)
        self.assertEqual((HERE/'internal_packaging_params.scad').read_text(encoding='utf-8'),expected)
        self.assertIn('KEY_X = [31.05,61.05,91.05];',expected)

if __name__=='__main__':unittest.main()
