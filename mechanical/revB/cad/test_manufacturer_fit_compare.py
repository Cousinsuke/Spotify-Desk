"""Tests for dimensioned STEP reference mapping; no manufacturer STEP copy required."""
import copy
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from manufacturer_fit_compare import mapped_parts, overlap_3d, study, svg_layout

class StepReferenceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((HERE/'dimensions.json').read_text())
        cls.r=json.loads((HERE/'waveshare_step_reference.json').read_text())

    def test_manufacturer_source_and_box_extent(self):
        s=self.r['source'];self.assertEqual(s['step_bytes'],31338066)
        self.assertEqual(s['solid_count'],693)
        a=study(self.d,self.r)
        self.assertAlmostEqual(a['dimensions_mm']['complete_step_depth'],16.906,delta=.002)
        self.assertFalse(a['physical_fit_verified'])

    def test_front_orientation_of_usb_and_i2c(self):
        p=mapped_parts(self.r,self.d)
        self.assertGreater(p['usb_type_c1'].center[0],100)
        self.assertLess(p['i2c_4pin_socket'].center[0],20)
        self.assertAlmostEqual(p['usb_type_c1'].center[1],40.936,delta=.1)

    def test_standoffs_pitch(self):
        a=study(self.d,self.r)
        self.assertAlmostEqual(a['dimensions_mm']['step_standoff_pitch_x'],98)
        self.assertAlmostEqual(a['dimensions_mm']['step_standoff_pitch_v'],60)

    def test_existing_156mm_and_centered_keys_preserved(self):
        self.assertEqual(self.d['width'],156)
        self.assertAlmostEqual(sum(self.d['keys_x'])/3,self.d['screen_center_x'])

    def test_usb_socket_body_clear_encoder_by_about_17mm(self):
        a=study(self.d,self.r)
        self.assertAlmostEqual(a['gap_usb_socket_to_encoder_body_x_mm'],17.544,delta=.002)
        self.assertIsNone(a['trial_usb_encoder_overlap_xyz_mm'])

    def test_usb_20mm_extension_trial_can_overlap_encoder(self):
        a=study(self.d,self.r,usb_extension=20)
        self.assertIsNotNone(a['trial_usb_encoder_overlap_xyz_mm'])
        self.assertAlmostEqual(a['trial_usb_encoder_overlap_xyz_mm'][0],2.456,delta=.002)

    def test_i2c_6mm_extension_violates_trial_left_inner_wall(self):
        a=study(self.d,self.r,i2c_extension=6)
        self.assertAlmostEqual(a['trial_i2c_inner_left_margin_mm'],-.423,delta=.002)
        self.assertIsNone(a['trial_i2c_encoder_overlap_xyz_mm'])

    def test_depth_offset_changes_mapped_coordinates(self):
        r=copy.deepcopy(self.r)
        r['reference_alignment']['assumed_front_glass_w_mm']=1.5
        orig=mapped_parts(self.r,self.d)['usb_type_c1']
        new=mapped_parts(r,self.d)['usb_type_c1']
        self.assertAlmostEqual(new.minimum[2]-orig.minimum[2],1.5)

    def test_invalid_extension_rejected(self):
        with self.assertRaises(ValueError):study(self.d,self.r,usb_extension=-1)
        with self.assertRaises(ValueError):study(self.d,self.r,i2c_extension=-1)

    def test_svg_front_orientation_and_warning(self):
        svg=svg_layout(self.d,study(self.d,self.r))
        self.assertIn('USB right, I2C left',svg)
        self.assertIn('No mating cable',svg)

if __name__=='__main__':unittest.main()
