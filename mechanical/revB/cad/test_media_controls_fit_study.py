"""Rev B design-only recessed MX media button test suite.

Run: python -m unittest discover -s mechanical/revB/cad -p test_media_controls_fit_study.py -v
"""
from __future__ import annotations
import copy, json, math, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from media_controls_fit_study import assumptions, cad_build, icon_svg, layout_svg, section_svg, study
from rotated_case_prototype import load, geometry_parameters, make_shell
try:
 import cadquery as cq
 HAS_CAD=True
except ImportError: HAS_CAD=False

class MediaControlsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.dim,cls.ref,cls.cfg=load();cls.cap=assumptions()
  cls.st=study(cls.dim,cls.ref,cls.cfg,cls.cap)
 def test_layout_unchanged(self):
  self.assertEqual(self.st['outer_case_size_mm'][0],156)
  self.assertEqual(self.st['key_centres_x_mm'],[31.05,61.05,91.05])
  self.assertEqual(self.st['rotated_window']['v'],17.09)
 def test_keycap_rest_and_pressed(self):
  self.assertEqual(self.st['keycap_rest_and_pressed'][0]['cap_top_w_mm'],-2)
  self.assertEqual(self.st['keycap_rest_and_pressed'][1]['cap_top_w_mm'],2)
  self.assertEqual(self.st['keycap_rest_and_pressed'][1]['cap_skirt_bottom_w_mm'],10)
 def test_usable_lateral_clearance(self):
  self.assertEqual(self.st['lateral_clearance_each_side_mm'],.6)
  self.assertLess(self.st['well_width_mm'],self.dim['key_pitch'])
 def test_switch_plate_nominal_retention_thickness(self):
  self.assertEqual(self.st['plate_thickness_mm'],1.5)
  self.assertEqual(self.st['plate_square_cutout_mm'],14)
 def test_full_stroke_nominal_collar_guard(self):
  self.assertEqual(self.st['cap_skirt_to_plate_gap_at_full_press_mm'],1.5)
 def test_full_module_to_recess_collars_gap(self):
  self.assertEqual(self.st['min_support_to_full_lcd_v_gap_mm'],3.6)
 def test_hood_does_not_pass_chip_width(self):
  self.assertEqual(self.st['knob']['diameter_mm'],15.1)
  self.assertEqual(self.st['knob']['x'],138)
 def test_invalid_cap_larger_than_well_rejected(self):
  c=copy.deepcopy(self.cap);c['cap_width_mm']=20
  with self.assertRaises(ValueError):study(self.dim,self.ref,self.cfg,c)
 def test_cap_too_deep_for_stroke_rejected(self):
  c=copy.deepcopy(self.cap);c['cap_depth_assumed_mm']=10
  with self.assertRaises(ValueError):study(self.dim,self.ref,self.cfg,c)
 def test_shallow_plate_rejected(self):
  c=copy.deepcopy(self.cap);c['switch_plate_top_inward_mm']=3
  with self.assertRaises(ValueError):study(self.dim,self.ref,self.cfg,c)
 def test_collared_well_near_chin_rejected(self):
  d=copy.deepcopy(self.dim);d['keys_v']=100
  with self.assertRaises(ValueError):study(d,self.ref,self.cfg,self.cap)
 def test_keys_symbols_are_independent_vector_art(self):
  for name in ('previous','play_pause','next'):
   icon=icon_svg(name)
   self.assertTrue(icon.startswith('<svg'))
   self.assertIn('<path',icon)
   self.assertNotIn('<image',icon)
 def test_svg_not_manufacturing_approved(self):
  front=layout_svg(self.dim,self.cfg,self.cap,self.st)
  section=section_svg(self.cap,self.st)
  self.assertIn('Not for fabrication',front)
  self.assertIn('ASSUMED',section)
  self.assertFalse(self.st['physical_fit_verified'])
 @unittest.skipUnless(HAS_CAD,'optional CadQuery and Shapely required')
 def test_rounded_shell_with_recessed_wells_valid(self):
  with tempfile.TemporaryDirectory() as tmp:
   shape=cad_build(self.dim,self.ref,self.cfg,self.cap,Path(tmp))
   self.assertTrue(shape.isValid())
   self.assertEqual(len(shape.Solids()),1)
   self.assertTrue((Path(tmp)/'spotify_desk_rounded180_recessed_3keys_EXPERIMENTAL.step').exists())
   self.assertTrue((Path(tmp)/'spotify_desk_rounded180_with_cap_knob_ENVELOPES.step').exists())
 @unittest.skipUnless(HAS_CAD,'optional CadQuery and Shapely required')
 def test_new_envelope_assembly_exports_with_real_brep(self):
  with tempfile.TemporaryDirectory() as tmp:
   shape=cad_build(self.dim,self.ref,self.cfg,self.cap,Path(tmp))
   sh=cq.importers.importStep(str(Path(tmp)/'spotify_desk_rounded180_recessed_3keys_EXPERIMENTAL.step')).val()
   self.assertTrue(sh.isValid())
   self.assertAlmostEqual(sh.BoundingBox().xlen,156,places=2)
   asm=(Path(tmp)/'spotify_desk_rounded180_with_cap_knob_ENVELOPES.step')
   self.assertGreater(asm.stat().st_size,100000)

if __name__=='__main__':unittest.main()
