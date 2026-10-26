#!/usr/bin/env python3
"""Python stdlib geometry tests + optional CadQuery B-rep closure checks."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from rotated_case_prototype import load
from hook_click_cover_study import configuration,layout,generate,build_cad,rounded_lid,xy_box

class HookClickTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.casecfg=load()
        cls.cfg=configuration()
        cls.report=layout(cls.dim,cls.ref,cls.casecfg,cls.cfg)

    def test_both_front_hooks_and_one_rear_catch(self):
        self.assertEqual(len(self.report['front_hooks']),2)
        self.assertIn('nose_y_max_mm',self.report['rear_latch'])
        self.assertEqual(len([k for k in self.report['rear_latch'] if 'nose_y_max' in k]),1)
    def test_lid_has_zero_screws(self):
        self.assertEqual(self.report['cover_screw_count'],0)
    def test_screen_retains_four_screws(self):
        self.assertEqual(self.report['screen_mount_screw_count'],4)
        self.assertEqual(self.report['screen_mount_pitch_mm'],[98.,60.])
    def test_dimensions_preserved(self):
        self.assertEqual(self.dim['width'],156.)
        self.assertEqual(self.cfg['cap_rest_height_mm'],4.)
        self.assertEqual(self.cfg['rotation_deg'],180)
    def test_lid_plate_is_two_mm(self):
        b=self.report['cover_body'];self.assertAlmostEqual(b['z_max']-b['z_min'],2.)
        self.assertAlmostEqual(b['x_max']-b['x_min'],133.2)
        self.assertAlmostEqual(b['y_max']-b['y_min'],58.29340799861508)
    def test_has_nominal_perimeter_clearance(self):
        self.assertAlmostEqual(self.report['cover_body']['x_min']-11.,.4)
        self.assertAlmostEqual(self.report['cover_body']['y_min']-12.,.4)
    def test_front_hook_centres_and_separation(self):
        self.assertEqual([h['center_x_mm'] for h in self.report['front_hooks']],[46.5,109.5])
        self.assertTrue(all(h['y_min_mm']<12 for h in self.report['front_hooks']))
    def test_front_hook_z_has_clearance_in_pocket(self):
        c=self.cfg['front_hooks'];self.assertGreater(c['tongue_z_bottom_mm'],c['pocket_z_bottom_mm'])
        self.assertLess(c['tongue_z_top_mm'],c['pocket_z_top_mm'])
    def test_rear_nose_retracts_past_wall(self):
        maxy=self.report['rear_latch']['nose_y_max_mm']
        rel=self.report['release_stroke_trial_mm']
        self.assertLess(maxy-rel,self.dim['depth']-12.-.2)
    def test_latch_keeper_floor_below_nose(self):
        l=self.cfg['rear_latch']
        self.assertLess(l['rear_pocket_z_bottom_mm'],1.55)
        self.assertGreater(l['rear_pocket_z_top_mm'],2.50)
    def test_kit_gives_fdm_cautions(self):
        self.assertFalse(self.report['physical_fit_verified'])
        self.assertTrue(self.report['original_cad_preserved'])
        self.assertIn('insertion',self.report['frame_insertion_issue'].lower())
    def test_no_rear_wall_through_slot(self):
        self.assertLess(self.cfg['rear_latch']['notch_right_x_mm']-self.cfg['rear_latch']['notch_left_x_mm'],10.)
        self.assertLess(self.cfg['front_hooks']['pocket_depth_y_mm'],4.)
    def test_reject_invalid_release_stroke(self):
        broken=copy.deepcopy(self.cfg);broken['rear_latch']['nominal_rear_release_stroke_mm']=.5
        with self.assertRaises(ValueError):layout(self.dim,self.ref,self.casecfg,broken)
    def test_reject_invalid_roof_lip(self):
        broken=copy.deepcopy(self.cfg);broken['cover']['support_lip_z_min_mm']=2.6
        with self.assertRaises(ValueError):layout(self.dim,self.ref,self.casecfg,broken)
    def test_reject_bad_front_hook_clearance(self):
        broken=copy.deepcopy(self.cfg);broken['front_hooks']['pocket_z_top_mm']=2.5
        with self.assertRaises(ValueError):layout(self.dim,self.ref,self.casecfg,broken)
    def test_no_cad_report_generates_svgs_and_json(self):
        with tempfile.TemporaryDirectory() as t:
            a=generate(Path(t),True)
            self.assertIsNone(a['cad'])
            for n in ['hook_click_design_report.json','hook_click_underside_plan.svg','hook_click_operation.svg']:
                self.assertTrue((Path(t)/n).exists())
            self.assertIn('not',json.loads((Path(t)/'hook_click_design_report.json').read_text())['layout']['status'].lower())
    def test_svg_marks_front_and_rear(self):
        from hook_click_cover_study import underside_svg,latch_section_svg
        self.assertIn('COVER HAS NONE',latch_section_svg(self.dim,self.report,self.cfg).upper())
        svg=underside_svg(self.dim,self.report,self.cfg)
        self.assertIn('locating tongues',svg)
        self.assertIn('REAR',svg)
    def test_no_screws_mislabelled_in_lid_art(self):
        from hook_click_cover_study import underside_svg
        self.assertIn('zero cover screws',underside_svg(self.dim,self.report,self.cfg))
    def test_print_approvals_explicitly_missing(self):
        self.assertTrue(any('No physical proof' in x for x in self.cfg['warnings']))
        self.assertTrue(any('insertion' in x for x in self.cfg['warnings']))
    def test_case_feature_sizes_stay_trial(self):
        self.assertLess(self.cfg['rear_latch']['nominal_rear_release_stroke_mm'],2)
        self.assertAlmostEqual(self.cfg['cover']['thickness_mm'],2.)

try:
    import cadquery as cq
    import shapely
    FULL=True
except ImportError:
    FULL=False

@unittest.skipUnless(FULL,'CadQuery and Shapely required for B-Rep STEP tests')
class BRepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.casecfg=load()
        cls.cfg=configuration()
        cls.report=layout(cls.dim,cls.ref,cls.casecfg,cls.cfg)
        cls.temp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.temp.name)
        cls.stats=build_cad(cls.dim,cls.ref,cls.casecfg,cls.cfg,cls.out)
        from cadquery import importers
        cls.case=importers.importStep(str(cls.out/'spotify_R5_4mm_hook_click_CASE_trial.step')).val()
        cls.lid=importers.importStep(str(cls.out/'spotify_R5_4mm_hook_click_LID_trial.step')).val()
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'temp'):cls.temp.cleanup()
    def test_both_cad_solids_valid_and_separate(self):
        self.assertTrue(self.case.isValid() and self.lid.isValid())
        self.assertEqual(len(self.case.Solids()),1)
        self.assertEqual(len(self.lid.Solids()),1)
    def test_no_case_lid_overlap_in_closed_position(self):
        self.assertLess(self.case.intersect(self.lid).Volume(),0.005)
    def test_2_front_locating_tongues_present_brep(self):
        for h in self.report['front_hooks']:
            probe=xy_box(cq,h['x_min_mm']+.5,h['x_max_mm']-.5,10.15,10.35,2.28,2.48).val()
            self.assertGreater(self.lid.intersect(probe).Volume(),.05)
            self.assertLess(self.case.intersect(probe).Volume(),.005)
    def test_lid_without_cover_screw_bores(self):
        # Four old screw locations were throughholes in prior panel, solid now.
        for x in [18.5,137.5]:
            for y in [19.5,self.dim['depth']-19.5]:
                probe=cq.Workplane('XY').workplane(offset=.9).center(x,y).circle(1.1).extrude(1).val()
                self.assertGreater(self.lid.intersect(probe).Volume(),2.)
    def test_contact_under_downward_pull_at_hooks(self):
        # If someone pulls the closed cover straight down, the roof/keeper
        # should geometrically intercept it (this is NOT a force test).
        lowered=self.lid.translate((0,0,-.65))
        self.assertGreater(self.case.intersect(lowered).Volume(),.3)
    def test_case_still_nominal_width(self):
        self.assertAlmostEqual(self.case.BoundingBox().xlen,156.,places=3)
    def test_two_step_files_reopen(self):
        self.assertTrue(self.stats['step_roundtrip'])
        self.assertEqual(self.stats['separate_valid_solids'],2)
    def test_front_pockets_have_seated_slack(self):
        self.assertLess(self.case.intersect(self.lid).Volume(),.005)
    def test_four_screen_support_positions(self):
        self.assertEqual(self.report['screen_mount_screw_count'],4)
        self.assertEqual(self.report['screen_mount_pitch_mm'],[98.,60.])
        self.assertGreater(self.case.Volume(),130000)

if __name__=='__main__':unittest.main(verbosity=2)
