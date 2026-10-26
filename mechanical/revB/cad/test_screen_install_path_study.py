"""Waveshare screen insertion and screw-reach checks; not physical proof.

stdlib checks run on Windows with repo files alone. Optional real-case STEP checks
require CadQuery+Shapely AND env SPOTIFY_HOOK_CLICK_V2_CASE_STEP pointing to the
previous user's pre-generated V2 case STEP (NEVER a fabricated/modified case).
"""
import hashlib,json,math,os,tempfile,unittest
from pathlib import Path
from rotated_case_prototype import load
from orientation_180_study import rotated_parts
from screen_install_path_study import (settings,local_to_world,expanded_box_corners_world,
    proxy_footprint,screw_axes,report,drawings,side_section_svg,generate,clearance_sweep)

D,R,C=load();SET=settings()

class ScreenMathChecks(unittest.TestCase):
    def test_expected_180_orientation(self):
        self.assertEqual(SET['rotation_deg'],180)
        p=rotated_parts(D,R,180)
        self.assertLess(p['usb_type_c1'].maximum[0],25)
        self.assertGreater(p['i2c_4pin_socket'].minimum[0],100)
    def test_rigid_face_mapping(self):
        x,y,z=local_to_world(D,78,0,0)
        self.assertAlmostEqual(x,78)
        self.assertAlmostEqual(y,D['front_face_length']*math.cos(math.radians(55)),places=3)
        self.assertAlmostEqual(z,D['height'])
    def test_nonzero_board_depth(self):
        f=proxy_footprint(D,R,SET)
        a,b=f['local_bbox_x_v_w_mm']['min'],f['local_bbox_x_v_w_mm']['max']
        self.assertAlmostEqual(b[2]-a[2],16.906,places=2)
    def test_bottom_hatch_desk_dimensions(self):
        f=proxy_footprint(D,R,SET)
        self.assertAlmostEqual(f['hatch_desk_y_depth_mm'],59.093,places=2)
        self.assertEqual(f['hatch_x_width_mm'],134)
    def test_board_projection_smaller_than_hatch(self):
        f=proxy_footprint(D,R,SET)
        self.assertAlmostEqual(f['projected_desk_y_depth_mm'],53.01,places=2)
        self.assertGreater(f['projection_desk_y_slack_mm'],6)
    def test_projected_board_overhangs_hatch_at_final(self):
        f=proxy_footprint(D,R,SET)
        self.assertFalse(f['straight_z_projection_at_final_alignment_entirely_in_hatch'])
        self.assertTrue(f['projected_bounding_footprint_fits_after_y_shift'])
        self.assertAlmostEqual(f['registered_nominal_y_rear_overhang_mm'],4.041,places=2)
    def test_staging_shift_has_limited_window(self):
        lo,hi=proxy_footprint(D,R,SET)['staging_y_translation_range_for_bbox_mm']
        self.assertLess(lo,hi)
        self.assertLess(hi,-4.0)
    def test_report_does_not_claim_assembly(self):
        r=report(D,R,C,SET)
        self.assertFalse(r['physically_tested'])
        self.assertTrue(r['case_includes_latch_v2_unchanged'])
        self.assertEqual(r['cover_screws'],0)
        self.assertEqual(r['screen_mount_screw_targets'],4)
        self.assertIn('3D sweeps needed',r['projection_screening'])
    def test_screen_98x60_four_screws(self):
        axes=screw_axes(D,R,C,SET)
        self.assertEqual(len(axes),4)
        x=sorted(set(p['x_mm'] for p in axes));v=sorted(set(p['v_mm'] for p in axes))
        self.assertAlmostEqual(x[1]-x[0],98.0)
        self.assertAlmostEqual(v[1]-v[0],60.0)
    def test_absurd_tool_radius_rejected(self):
        altered=dict(SET,tool_shank_radius_mm=10)
        with self.assertRaises(ValueError):screw_axes(D,R,C,altered)
    def test_wrong_orientation_rejected(self):
        altered=dict(SET,rotation_deg=0)
        with self.assertRaises(ValueError):proxy_footprint(D,R,altered)
    def test_glass_recess_unverified_and_configurable(self):
        a=proxy_footprint(D,R,SET)
        b=proxy_footprint(D,R,dict(SET,trial_glass_recess_inward_w_mm=4.25))
        self.assertNotEqual(a['projected_desk_y_minmax_mm'],b['projected_desk_y_minmax_mm'])
    def test_svg_two_plans_and_warning(self):
        r=report(D,R,C,SET)
        for s in (drawings(D,r),side_section_svg(D,r)):
            self.assertIn('<svg',s)
            self.assertIn('NOT',s.upper())
    def test_report_only_writes_complete_geometry_without_CAD(self):
        with tempfile.TemporaryDirectory() as t:
            r=generate(Path(t),report_only=True)
            self.assertTrue((Path(t)/'waveshare_installation_side_section.svg').exists())
            self.assertTrue((Path(t)/'waveshare_underside_projection.svg').exists())
            on_disk=json.loads((Path(t)/'screen_installation_2023_reference_report.json').read_text())
            self.assertFalse(on_disk['sampled_3d_screening_performed'])
    def test_step_source_is_measured_but_no_vendor_model_shipped(self):
        self.assertIn('full_assembly',R['parts'])
        self.assertEqual(len([key for key in R['parts'] if key.startswith('standoff_')]),4)
        self.assertTrue(SET['cover_removed_during_installation'])

try:import cadquery
except ImportError:cadquery=None
STEP=Path(os.environ.get('SPOTIFY_HOOK_CLICK_V2_CASE_STEP','not-an-actual-file.step'))

@unittest.skipUnless(cadquery and STEP.is_file(),'optional CadQuery+prior generated hook-click V2 case STEP required')
class RealCaseStudyChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_sha=hashlib.sha256(STEP.read_bytes()).hexdigest()
        cls.temp=tempfile.TemporaryDirectory()
        cls.dir=Path(cls.temp.name)
        cls.cad=clearance_sweep(D,R,C,SET,STEP,cls.dir)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_seated_full_prism_raises_collision_warning(self):
        self.assertGreater(self.cad['nominal_unrotated_bbox_case_intersection_mm3'],600)
    def test_seated_touch_glass_proxy_has_no_case_overlap(self):
        self.assertAlmostEqual(self.cad['nominal_unrotated_touch_glass_bbox_case_intersection_mm3'],0.0,places=2)
    def test_vertical_unrotated_z_sweep_has_collisions(self):
        t=[x for x in self.cad['sweep'] if x['tilt_degrees']==0 and x['z_staging_mm']==-90][0]
        self.assertGreater(t['touch_glass_bbox_case_overlap_mm3'],0.1)
        self.assertFalse(self.cad['no_collision_free_continuous_route_certified'] is False)
    def test_at_least_two_tool_axes_reach_case(self):
        rows=[p for p in self.cad['driver_shaft_samples'] if p['length_mm']==40]
        self.assertEqual(len(rows),4)
        self.assertGreaterEqual(sum(x['case_intersection_mm3']>5 for x in rows),2)
    def test_step_outputs_exist_and_old_case_unchanged(self):
        import cadquery as cq
        for x in ('Waveshare_Screen_Installation_BBox_Reference_ASSEMBLY.step','Waveshare_Screen_BBox_Staged_Below_ASSEMBLY.step'):
            self.assertGreater((self.dir/x).stat().st_size,1000)
        self.assertEqual(hashlib.sha256(STEP.read_bytes()).hexdigest(),self.original_sha)

if __name__=='__main__':unittest.main()
