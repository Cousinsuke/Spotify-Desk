"""Run: python -m unittest discover -s mechanical/revB/cad -p test_orientation_180_study.py -v"""
import copy
import json
import unittest
from pathlib import Path
from orientation_180_study import compare,display_aperture,make_svg,rotated_parts,touch_rotate_180
HERE=Path(__file__).resolve().parent

class OrientationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim=json.loads((HERE/'dimensions.json').read_text(encoding='utf-8'))
        cls.ref=json.loads((HERE/'waveshare_step_reference.json').read_text(encoding='utf-8'))
    def test_original_unchanged_connector_sides(self):
        r=compare(self.dim,self.ref,0)
        self.assertEqual((r['usb_front_side'],r['i2c_front_side']),('right','left'))
        self.assertAlmostEqual(r['nominal_left_housing_to_inner_wall_x_mm'],5.577,places=3)
    def test_rotated_swaps_connector_sides(self):
        r=compare(self.dim,self.ref,180)
        self.assertEqual((r['usb_front_side'],r['i2c_front_side']),('left','right'))
        self.assertLess(r['usb_type_c1']['max'][0],25)
        self.assertGreater(r['i2c_4pin']['min'][0],100)
    def test_180_rotates_about_module_center(self):
        a=rotated_parts(self.dim,self.ref,0)['usb_type_c1']
        b=rotated_parts(self.dim,self.ref,180)['usb_type_c1']
        self.assertAlmostEqual(a.minimum[0]+b.maximum[0],2*self.dim['screen_origin'][0]+self.dim['screen_outer'][0],places=3)
        self.assertAlmostEqual(a.minimum[1]+b.maximum[1],2*self.dim['screen_origin'][1]+self.dim['screen_outer'][1],places=3)
        self.assertEqual(a.minimum[2],b.minimum[2])
    def test_mounting_pitch_preserved(self):
        for degrees in (0,180):
            self.assertEqual(compare(self.dim,self.ref,degrees)['mounting_pitch_x_v_mm'],[98.,60.])
    def test_visible_screen_window_moves_down(self):
        a=display_aperture(self.dim,0);b=display_aperture(self.dim,180)
        self.assertAlmostEqual(b['v']-a['v'],4.74,places=3)
        self.assertAlmostEqual(b['x']-a['x'],.1,places=3)
        self.assertAlmostEqual(compare(self.dim,self.ref,180)['visible_screen_to_keycap_top_gap_mm'],10.55,places=2)
    def test_encoder_and_case_unmodified(self):
        for deg in (0,180):
            r=compare(self.dim,self.ref,deg)
            self.assertEqual(r['case_width_mm'],156)
            self.assertFalse(r['physical_fit_verified'])
        self.assertAlmostEqual(sum(self.dim['keys_x'])/3,61.05)
    def test_left_usb_plug_assumption_enters_wall(self):
        r=compare(self.dim,self.ref,180,usb_reach_mm=6)
        self.assertLess(r['trial_left_cable_to_inner_wall_x_mm'],0)
        self.assertAlmostEqual(r['trial_left_cable_to_inner_wall_x_mm'],-.756,places=3)
    def test_rotated_right_i2c_20mm_intersects_encoder_nominal(self):
        r=compare(self.dim,self.ref,180,i2c_reach_mm=20)
        self.assertIsNotNone(r['i2c_probe_to_encoder_overlap_xyz_mm'])
        self.assertGreater(r['trial_right_cable_to_inner_wall_x_mm'],10)
    def test_default_rotated_plug_no_encoder_overlap(self):
        r=compare(self.dim,self.ref,180)
        self.assertIsNone(r['usb_probe_to_encoder_overlap_xyz_mm'])
        self.assertIsNone(r['i2c_probe_to_encoder_overlap_xyz_mm'])
    def test_invalid_degree_and_negative_reach(self):
        with self.assertRaises(ValueError):compare(self.dim,self.ref,90)
        with self.assertRaises(ValueError):compare(self.dim,self.ref,180,usb_reach_mm=-3)
        with self.assertRaises(ValueError):compare(self.dim,self.ref,180,i2c_reach_mm=-3)
    def test_touch_180_mapping(self):
        self.assertEqual(touch_rotate_180(0,0),(799,479))
        self.assertEqual(touch_rotate_180(799,479),(0,0))
        with self.assertRaises(ValueError):touch_rotate_180(800,0)
    def test_svg_shows_two_orientations_and_caveats(self):
        s=make_svg(self.dim,[compare(self.dim,self.ref,0),compare(self.dim,self.ref,180)])
        self.assertIn('Physical 180°',s)
        self.assertIn('USB left / I2C right',s)
        self.assertIn('No physical plugs',s)

if __name__=='__main__':unittest.main()
