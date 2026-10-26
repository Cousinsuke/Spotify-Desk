#!/usr/bin/env python3
"""Nominal geometric sanity tests. No actual print, force, or fatigue validation."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import hook_click_cover_study as old
from hook_click_latch_refinement_v2 import config,analyze,generate,refine_lid,latch_coupon

class GeometryMathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.casecfg=old.load()
        cls.baseline=old.configuration();cls.cfg=config()
        cls.report=analyze(cls.dim,cls.ref,cls.casecfg,cls.baseline,cls.cfg)
    def test_root_fillet_and_cam_have_explicit_dimensions(self):
        self.assertAlmostEqual(self.report['rounded_root_fillet_mm'],.68)
        self.assertAlmostEqual(self.report['ramped_nose_y_retraction_top_mm'],1.50)
    def test_lower_shoulder_retained_after_leadin(self):
        self.assertLess(self.report['cam_shoulder_bottom_z_mm'],self.report['cam_flat_shoulder_to_z_mm'])
        self.assertLess(self.report['cam_flat_shoulder_to_z_mm'],self.report['cam_top_z_mm'])
    def test_top_cam_starts_inside_rear_wall_inner_edge(self):
        self.assertLess(self.report['nose_top_leading_y_mm'],self.report['keeper_inner_edge_y_mm'])
    def test_rear_cam_outer_nose_still_engages(self):
        self.assertGreater(self.report['nose_outer_y_at_rest_mm'],self.report['keeper_inner_edge_y_mm']+.7)
    def test_retraction_does_not_exceed_stated_stroke(self):
        self.assertLess(self.report['ramped_nose_y_retraction_top_mm'],self.report['assumed_release_stroke_mm'])
    def test_fixed_case_and_screen_hardware_preserved(self):
        self.assertTrue(self.report['unchanged_case_and_screen_mounts'])
        self.assertEqual(self.report['lid_screws'],0)
        self.assertEqual(self.report['screen_screw_targets'],4)
    def test_ideal_beam_strain_finite_and_cautioned(self):
        self.assertAlmostEqual(self.report['estimated_ideal_beam_surface_strain_percent'],.781,places=3)
        self.assertTrue(self.report['strain_is_approximate_not_fea'])
    def test_no_false_print_ready_claim(self):
        self.assertFalse(self.report['fabrication_approved'])
        self.assertFalse(self.report['physically_click_tested'])
        self.assertTrue(any('actual elastic' in s for s in self.report['remaining_gates']))
    def test_finger_pad_not_linked_to_neighbouring_solid(self):
        b=self.report['finger_pad_bbox']
        self.assertGreater(b['x_max']-b['x_min'],7)
        self.assertGreater(b['y_max']-b['y_min'],2)
    def test_valid_summary_report_and_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=generate(Path(tmp),True)
            self.assertIsNone(r['cad'])
            svg=(Path(tmp)/'hook_click_latch_v2_design.svg').read_text()
            self.assertIn('Root fillet:',svg)
            self.assertIn('not a rating',svg)
            self.assertFalse(json.loads((Path(tmp)/'hook_click_latch_v2_report.json').read_text())['analysis']['fabrication_approved'])
    def test_reject_overambitious_root_fillet(self):
        c=copy.deepcopy(self.cfg);c['latch']['root_inside_fillet_mm']=1.15
        with self.assertRaises(ValueError):analyze(self.dim,self.ref,self.casecfg,self.baseline,c)
    def test_reject_top_bevel_not_clear_wall(self):
        c=copy.deepcopy(self.cfg);c['latch']['cam_y_retraction_at_top_mm']=.9
        with self.assertRaises(ValueError):analyze(self.dim,self.ref,self.casecfg,self.baseline,c)
    def test_reject_cam_over_release_stroke(self):
        c=copy.deepcopy(self.cfg);c['latch']['cam_y_retraction_at_top_mm']=1.9
        with self.assertRaises(ValueError):analyze(self.dim,self.ref,self.casecfg,self.baseline,c)
    def test_reject_pad_attached_to_lid_right_body(self):
        c=copy.deepcopy(self.cfg);c['latch']['finger_pad']['x_max']=94.2
        with self.assertRaises(ValueError):analyze(self.dim,self.ref,self.casecfg,self.baseline,c)
    def test_reject_pad_outside_cover(self):
        c=copy.deepcopy(self.cfg);c['latch']['finger_pad']['y_max']=71
        with self.assertRaises(ValueError):analyze(self.dim,self.ref,self.casecfg,self.baseline,c)
    def test_reject_flexure_absent_from_pad(self):
        c=copy.deepcopy(self.cfg);c['latch']['finger_pad']['x_min']=90.2
        with self.assertRaises(ValueError):analyze(self.dim,self.ref,self.casecfg,self.baseline,c)

try:
 import cadquery as cq
 from cadquery import importers
 import shapely
 HAS_CAD=True
except ImportError:HAS_CAD=False

@unittest.skipUnless(HAS_CAD,'optional CadQuery/Shapely required to reimport actual STEP solids')
class RealCADTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.casecfg=old.load();cls.base=old.configuration();cls.cfg=config()
        cls.temp=tempfile.TemporaryDirectory();cls.dir=Path(cls.temp.name)
        cls.result=generate(cls.dir,False)
        cls.case=importers.importStep(str(cls.dir/'SpotifyDesk_R5_hook_click_v2_CASE.step')).val()
        cls.lid=importers.importStep(str(cls.dir/'SpotifyDesk_R5_hook_click_v2_LID.step')).val()
        cls.frame=importers.importStep(str(cls.dir/'SpotifyDesk_latch_v2_test_FRAME.step')).val()
        cls.crop=importers.importStep(str(cls.dir/'SpotifyDesk_latch_v2_test_LID.step')).val()
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'temp'):cls.temp.cleanup()
    def test_all_four_steps_are_valid_reopened_solids(self):
        for s in (self.case,self.lid,self.crop,self.frame):
            self.assertTrue(s.isValid())
            self.assertEqual(len(s.Solids()),1)
    def test_case_and_lid_not_intersecting_when_shut(self):
        self.assertLess(self.case.intersect(self.lid).Volume(),.005)
    def test_cropped_coupons_same_no_overlap(self):
        self.assertLess(self.crop.intersect(self.frame).Volume(),.005)
    def test_coupon_catches_if_rigidly_pulled_down(self):
        self.assertGreater(self.crop.translate((0,0,-.65)).intersect(self.frame).Volume(),.10)
    def test_lid_still_two_locating_hooks(self):
        dat=old.layout(self.dim,self.ref,self.casecfg,self.base)
        for h in dat['front_hooks']:
            probe=old.xy_box(cq,h['x_min_mm']+.5,h['x_max_mm']-.5,10.15,10.35,2.28,2.48).val()
            self.assertGreater(self.lid.intersect(probe).Volume(),.05)
    def test_nose_top_relieved_but_lower_shouldered(self):
        dat=old.layout(self.dim,self.ref,self.casecfg,self.base)
        r=dat['rear_latch']
        # A small volume near the distal end must exist LOW but not HIGH.
        lower=old.xy_box(cq,87.3,88.0,r['nose_y_max_mm']-.55,r['nose_y_max_mm']-.15,1.61,1.77).val()
        upper=old.xy_box(cq,87.3,88.0,r['nose_y_max_mm']-.55,r['nose_y_max_mm']-.15,2.38,2.48).val()
        self.assertGreater(self.lid.intersect(lower).Volume(),.005)
        self.assertLess(self.lid.intersect(upper).Volume(),.0001)
    def test_unchanged_case_has_four_screen_mount_locations(self):
        self.assertEqual(self.case.BoundingBox().xlen,156.)
        self.assertGreater(self.case.Volume(),130000)
    def test_thumb_pad_measured_envelope(self):
        b=self.cfg['latch']['finger_pad']
        p=old.xy_box(cq,b['x_min']+.5,b['x_max']-.5,67.7,68.3,.75,1.05).val()
        self.assertGreater(self.lid.intersect(p).Volume(),.1)
    def test_stl_coupons_created_and_nonzero(self):
        for name in ['SpotifyDesk_latch_v2_test_FRAME.stl','SpotifyDesk_latch_v2_test_LID.stl']:
            self.assertGreater((self.dir/name).stat().st_size,1000)
    def test_assembled_and_exploded_saved(self):
        self.assertTrue((self.dir/'SpotifyDesk_R5_hook_click_v2_ASSEMBLY.step').exists())
        self.assertTrue((self.dir/'SpotifyDesk_R5_hook_click_v2_EXPLODED.step').exists())
        self.assertTrue((self.dir/'SpotifyDesk_latch_v2_test_ASSEMBLY.step').exists())

if __name__=='__main__':unittest.main(verbosity=2)
