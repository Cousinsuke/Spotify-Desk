"""Run: python -m unittest discover -s mechanical/revB/cad -p test_rotated_case_prototype.py -v"""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from rotated_case_prototype import load,geometry_parameters,make_summary_svg,make_shell

HERE=Path(__file__).resolve().parent

class RotatedCaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.dim,cls.ref,cls.cfg=load()
  cls.par=geometry_parameters(cls.dim,cls.ref,cls.cfg)

 def test_existing_rev_b_outer_size_and_layout_retained(self):
  self.assertEqual(self.par['outer_width_mm'],156)
  self.assertEqual(self.dim['keys_x'],[31.05,61.05,91.05])
  self.assertEqual(self.par['orientation_deg'],180)

 def test_visible_window_moves_lower_and_barely_right(self):
  w=self.par['display_aperture'];o=self.par['original_aperture']
  self.assertAlmostEqual(w['v']-o['v'],4.74)
  self.assertAlmostEqual(w['x']-o['x'],.1)
  self.assertAlmostEqual(self.par['visible_to_keycap_top_gap_mm'],10.55)

 def test_socket_orientations_from_real_manufacturer_boxes(self):
  self.assertLess(self.par['usb_c1_measured_bare_housing']['max'][0],18)
  self.assertGreater(self.par['right_i2c_measured_bare_housing']['min'][0],100)

 def test_left_usb_service_slot_intersects_side_wall_but_not_front_skin(self):
  p=self.par['left_usb_c1_service_slot_trial'];w=self.cfg['case_wall_mm']
  self.assertLess(p['x_min'],0)
  self.assertGreater(p['x_max'],w)
  self.assertGreater(p['w_min'],w)
  self.assertAlmostEqual(p['w_min'],8.889,places=3)
  self.assertAlmostEqual(p['w_max'],17.051,places=3)

 def test_trial_mount_datum_separates_screen_from_nominal_front_skin(self):
  self.assertGreater(self.cfg['front_glass_inward_w_mm'],self.cfg['case_wall_mm'])
  self.assertAlmostEqual(self.par['assembled_step_rear_w_max_at_datum_mm'],20.153,places=2)
  self.assertFalse('physical_fit_verified' in self.par)

 def test_rejects_frontal_cutout_through_skin(self):
  bad=copy.deepcopy(self.cfg)
  bad['front_glass_inward_w_mm']=0
  with self.assertRaises(ValueError):geometry_parameters(self.dim,self.ref,bad)

 def test_warns_no_real_plug_or_fit_claim(self):
  self.assertIn('NOT FIT-VERIFIED',self.par['design_status'])
  self.assertTrue(any('no actual USB-C male plug' in s for s in self.par['unmodelled']))
  self.assertTrue(any('no LCD bearing ledge' in s for s in self.par['unmodelled']))

 def test_svg_marks_power_port_as_side_wall_trial(self):
  svg=make_summary_svg(self.dim,self.par)
  self.assertIn('USB-C1 trial wall opening',svg)
  self.assertIn('No real plugs',svg)

 @unittest.skipUnless(importlib.util.find_spec("cadquery") and importlib.util.find_spec("shapely"), "optional CadQuery + Shapely required for B-Rep tests")
 def test_sharp_and_rounded_are_valid_brep_solids(self):
  for version in ('sharp','rounded'):
   with self.subTest(version=version):
    shell=make_shell(self.dim,self.par,version,self.cfg)
    self.assertTrue(shell.isValid())
    self.assertEqual(len(shell.Solids()),1)
    self.assertAlmostEqual(shell.BoundingBox().xlen,156,delta=.001)
    self.assertAlmostEqual(shell.BoundingBox().zlen,106.1067,delta=.02)

 @unittest.skipUnless(importlib.util.find_spec("cadquery") and importlib.util.find_spec("shapely"), "optional CadQuery + Shapely required for B-Rep tests")
 def test_left_usb_cut_removes_wall_material_both_variants(self):
  p=self.par['left_usb_c1_service_slot_trial']
  no_port=copy.deepcopy(self.par)
  no_port['left_usb_c1_service_slot_trial']={**p,'x_min':4.5}
  for version in ('sharp','rounded'):
   with self.subTest(version=version):
    actual=make_shell(self.dim,self.par,version,self.cfg)
    blank=make_shell(self.dim,no_port,version,self.cfg)
    self.assertLess(actual.Volume(),blank.Volume()-10)
    self.assertLess(blank.Volume()-actual.Volume(),1500)

if __name__=='__main__':unittest.main()
