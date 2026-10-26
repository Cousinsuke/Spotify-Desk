#!/usr/bin/env python3
"""Mechanical comparison regression tests. Passing != installed hardware works."""
from __future__ import annotations
import json, os, tempfile, unittest
from pathlib import Path
from screen_install_bracket_options import cfg,describe,generate
from rotated_case_prototype import load

ROOT=Path(__file__).resolve().parent
CASE=Path(os.environ.get('SPOTIFY_HOOK_CLICK_V2_CASE_STEP',str(ROOT/'BASELINE_CASE_V2.step')))
try:
 import cadquery as cq
 CAD=CASE.is_file()
except ImportError:CAD=False

class Calculations(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.dim,cls.ref,cls.casecfg=load();cls.options=cfg()
  cls.options['legacy_screen_install_settings']=json.loads((ROOT/'screen_install_study_parameters.json').read_text())
  cls.data=describe(cls.dim,cls.ref,cls.casecfg,cls.options)
 def test_chosen_external_layout_preserved(self):
  self.assertEqual(self.dim['width'],156);self.assertEqual(self.data['physical_rotation_deg'],180)
  self.assertEqual(self.options['rest_keycap_mm'],4)
 def test_mounting_pitch(self):
  x=self.data['screen_mount_centres_x_mm'];v=self.data['screen_mount_centres_v_mm']
  self.assertAlmostEqual(x[1]-x[0],98);self.assertAlmostEqual(v[1]-v[0],60)
 def test_two_carriers_only(self):self.assertEqual(len(self.data['trial_preassembled_sidebars']),2)
 def test_original_screen_target_count(self):self.assertEqual(self.data['screen_screws_retained'],4)
 def test_no_bottom_cover_screws(self):self.assertEqual(self.data['lid_screws'],0)
 def test_stage_window_is_two_dimensional(self):
  self.assertEqual(self.data['projected_y_stage_translation_range_mm'],[-10.129,-4.041])
  self.assertTrue(self.data['staged_y_range_is_2d_only'])
 def test_external_bar_not_claimed_as_mated(self):
  self.assertTrue(self.data['bracket_bars_without_case_mating_structure'])
  self.assertTrue(self.data['case_needs_new_underside_accessible_screw_bosses_for_carrier'])
 def test_no_case_geometry_change(self):
  self.assertFalse(self.data['case_modified']);self.assertFalse(self.data['hook_click_v2_cover_modified'])
 def test_4_mx_key_unchanged(self):self.assertEqual(self.options['rest_keycap_mm'],4.0)
 def test_72_grid_poses_including_zero(self):
  s=self.options['entry_samples'];self.assertEqual(len(s['temporary_y_shifts_mm'])*len(s['temporary_tilt_deg'])*len(s['approach_z_offsets_mm']),72)
  self.assertIn(0,s['temporary_tilt_deg']);self.assertIn(0,s['temporary_y_shifts_mm']);self.assertIn(0,s['approach_z_offsets_mm'])
 def test_reject_missing_final_pose(self):
  s=json.loads(json.dumps(self.options));s['entry_samples']['approach_z_offsets_mm']=[-120]
  with self.assertRaises(ValueError):describe(self.dim,self.ref,self.casecfg,s)
 def test_reject_unsupported_rotation(self):
  s=json.loads(json.dumps(self.options));s['rotation_deg']=0
  with self.assertRaises(ValueError):describe(self.dim,self.ref,self.casecfg,s)
 def test_reject_bad_rail_width(self):
  s=json.loads(json.dumps(self.options));s['preassembled_carrier']['bar_width_x_mm']=25
  with self.assertRaises(ValueError):describe(self.dim,self.ref,self.casecfg,s)
 def test_reject_unreasonable_tool_size(self):
  s=json.loads(json.dumps(self.options));s['access_screw_trial']['shaft_diameter_mm']=15
  with self.assertRaises(ValueError):describe(self.dim,self.ref,self.casecfg,s)
 def test_report_and_svgs(self):
  with tempfile.TemporaryDirectory() as d:
   r=generate(Path(d),report_only=True)
   self.assertFalse(r['cad_sweep_performed'])
   self.assertIn('NO VERIFIED PHYSICAL INSTALLATION',r['status'])
   for f in ['carrier_bar_mounting_plan.svg','staged_entry_2d_projection.svg']:
    self.assertIn('<svg', (Path(d)/f).read_text())
   rep=json.loads((Path(d)/'screen_entry_and_preassembly_report.json').read_text())
   self.assertTrue(rep['case_needs_new_underside_accessible_screw_bosses_for_carrier'])

@unittest.skipUnless(CAD,'CadQuery and baseline V2 case STEP optional for real B-Rep')
class CADChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.dst=Path(cls.tmp.name)
  cls.res=generate(cls.dst,case_step=CASE)
  cls.c=cls.res['cad_samples']
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_reference_exports_exist(self):
  for f in ['Waveshare_trial_preassembled_LEFT_RAIL.step','Waveshare_trial_preassembled_RIGHT_RAIL.step', 'Waveshare_carrier_bars_IN_CASE_CLASHES_UNRESOLVED.step','Waveshare_preassembly_STAGED_POSITION_UNVERIFIED.step']:
   self.assertGreater((self.dst/f).stat().st_size,10000)
 def test_rails_solid_reimport(self):
  for side in ['LEFT','RIGHT']:
   part=cq.importers.importStep(str(self.dst/f'Waveshare_trial_preassembled_{side}_RAIL.step')).val()
   self.assertTrue(part.isValid());self.assertEqual(len(part.Solids()),1)
 def test_rails_not_mistaken_as_drop_in(self):
  self.assertGreater(self.c['rail_case_intersection_mm3'][0],100)
  self.assertGreater(self.c['rail_case_intersection_mm3'][1],100)
 def test_vertical_tool_centres_are_just_trial_clear(self):
  self.assertEqual(len(self.c['vertical_ear_tool_access_trial']),2)
  for a in self.c['vertical_ear_tool_access_trial']:
   self.assertLessEqual(a['trial_case_material_intersection_mm3'],0.01)
 def test_continuous_path_NOT_certified(self):
  self.assertEqual(self.c['sampled_poses'],72)
  self.assertTrue(self.c['continuous_collision_free_path_NOT_verified'])
  self.assertTrue(self.c['full_assembled_693_solid_NOT_used'])
  self.assertTrue(any(a['proxy_case_intersection_mm3']>0.05 for a in self.c['poses'] if a['vertical_z_offset_mm']>=-75))
  self.assertTrue(any(a['conservative_proxy_free'] for a in self.c['poses'] if a['vertical_z_offset_mm']<=-110))

if __name__=='__main__':unittest.main()
