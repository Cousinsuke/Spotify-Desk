#!/usr/bin/env python3
"""Design-only regression checks for the new independent 4mm rear cover study."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from rotated_case_prototype import load
from rear_cover_screen_mount_study import load_specification,report,generate

try:
    import cadquery as cq
    import shapely
    CAD=True
except ImportError:
    CAD=False

class MountStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.cfg=load()
        cls.settings=load_specification()
        cls.report=report(cls.dim,cls.ref,cls.cfg,cls.settings)
        cls.directory=Path(tempfile.mkdtemp(prefix='spotify_cover_tests_'))
        cls.cad=None
        if CAD:
            cls.result=generate(cls.directory,False)
        else:
            cls.result=generate(cls.directory,True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.directory,ignore_errors=True)

    def test_desired_architecture_unmodified(self):
        self.assertTrue(self.report['original_cad_preserved'])
        self.assertFalse(self.report['physical_fit_verified'])
        self.assertIn('4mm',self.report['chosen_case'])
        self.assertEqual(self.dim['width'],156.0)
        self.assertEqual(self.cfg['physical_rotation_deg'],180)

    def test_cover_inside_original_underbody_cutout(self):
        c=self.report['bottom_cover_mm'];o=self.report['bottom_opening_mm']
        for axis in ('x','y'):
            self.assertAlmostEqual(c[f'{axis}_min']-o[f'{axis}_min'],0.4)
            self.assertAlmostEqual(o[f'{axis}_max']-c[f'{axis}_max'],0.4)
        self.assertAlmostEqual(c['z_max'],2.35)

    def test_case_lip_has_overlap(self):
        self.assertGreaterEqual(self.report['lip_support_inner_reach_mm'],1.4)

    def test_four_underside_screws_accessible_and_symmetric(self):
        points=self.report['cover_screw_centers_xyz_mm']
        self.assertEqual(len(points),4)
        xs=sorted(set(p[0] for p in points));ys=sorted(set(p[1] for p in points))
        self.assertEqual(len(xs),2);self.assertEqual(len(ys),2)
        self.assertAlmostEqual(sum(xs),self.dim['width'])
        self.assertAlmostEqual(sum(ys),self.dim['depth'])
        for x,y,_ in points:
            c=self.report['bottom_cover_mm']
            self.assertTrue(c['x_min']+4<x<c['x_max']-4)
            self.assertTrue(c['y_min']+4<y<c['y_max']-4)

    def test_manufacturer_standoff_pitch_and_positions(self):
        mounts=self.report['screen_standoff_centers_and_seats']
        self.assertEqual(len(mounts),4)
        self.assertEqual(self.report['screen_standoff_pitch_mm'],[98.0,60.0])
        self.assertEqual(sorted(set(m['x'] for m in mounts)),[12.05,110.05])
        self.assertEqual(sorted(set(m['v'] for m in mounts)),[11.8,71.8])

    def test_screen_anchor_points_outside_glass(self):
        mounts=self.report['screen_standoff_centers_and_seats'];s=self.settings['screen_brackets']
        front_edge=self.dim['screen_origin'][1]; back_edge=front_edge+self.dim['screen_outer'][1]
        for m in mounts:
            end=m['anchor_v_mm']+s['anchor_v_length_mm']/2
            begin=m['anchor_v_mm']-s['anchor_v_length_mm']/2
            self.assertTrue(end<front_edge or begin>back_edge)
            self.assertGreater(m['seat_front_w_mm'],self.cfg['case_wall_mm'])

    def test_mounting_uses_2023_board_not_guaranteed_latest_revision(self):
        self.assertGreater(self.report['screen_board_max_inward_w_at_trial_datum_mm'],19.0)
        self.assertTrue(any('revision' in x for x in self.report['hardware_unverified']))

    def test_wrong_orientation_rejected(self):
        new={**self.settings,'physical_rotation_deg':0}
        with self.assertRaises(ValueError):report(self.dim,self.ref,self.cfg,new)

    def test_wrong_cap_height_rejected(self):
        new={**self.settings,'cap_rest_height_mm':2.0}
        with self.assertRaises(ValueError):report(self.dim,self.ref,self.cfg,new)

    def test_excess_cover_clearance_rejected(self):
        new=json.loads(json.dumps(self.settings));new['cover']['perimeter_clearance_mm']=2
        with self.assertRaises(ValueError):report(self.dim,self.ref,self.cfg,new)

    def test_invalid_pilot_hole_rejected(self):
        new=json.loads(json.dumps(self.settings));new['cover_fasteners']['pilot_diameter_mm']=3.5
        with self.assertRaises(ValueError):report(self.dim,self.ref,self.cfg,new)

    def test_report_svg_contains_both_separate_views(self):
        names=['rear_cover_bottom_plan.svg','screen_mount_front_plan.svg','rear_screen_mount_report.json']
        for name in names:self.assertTrue((self.directory/name).exists(),name)
        r=json.loads((self.directory/names[2]).read_text())
        self.assertFalse(r['geometry']['physical_fit_verified'])
        self.assertIn('M2.5',(self.directory/names[1]).read_text())
        self.assertIn('4 removable screws',(self.directory/names[0]).read_text())

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely needed for B-rep generation')
    def test_actual_case_reimports_as_one_valid_solid(self):
        n='spotify_revB_R5_USBleft_4mm_case_with_mounts_EXPERIMENTAL.step'
        part=cq.importers.importStep(str(self.directory/n)).val()
        self.assertTrue(part.isValid())
        self.assertEqual(len(part.Solids()),1)
        self.assertGreater(part.Volume(),137087.0)
        bb=part.BoundingBox()
        self.assertAlmostEqual(bb.xlen,156,places=2)

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely needed for B-rep generation')
    def test_actual_rear_cover_reimports_with_four_holes(self):
        n='spotify_revB_removable_rear_cover_EXPERIMENTAL.step'
        part=cq.importers.importStep(str(self.directory/n)).val()
        self.assertTrue(part.isValid());self.assertEqual(len(part.Solids()),1)
        self.assertGreater(part.Volume(),10000)
        # The four screw centre XY locations must be void throughout cover thickness.
        for x,y,_ in self.report['cover_screw_centers_xyz_mm']:
            hole=cq.Workplane('XY').workplane(offset=.4).center(x,y).circle(.5).extrude(1.7).val()
            self.assertLess(part.intersect(hole).Volume(),1e-3)

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely needed for B-rep generation')
    def test_actual_lid_does_not_interpenetrate_shell(self):
        cad=self.result['cad_build'];self.assertTrue(cad['case_valid']);self.assertTrue(cad['cover_valid'])
        self.assertEqual(cad['cover_case_overlap_mm3'],0)
        self.assertGreater(cad['shell_with_supports_volume_mm3'],cad['original_4mm_case_volume_mm3'])

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely needed for B-rep generation')
    def test_step_assemblies_created(self):
        for n in ['spotify_revB_case_cover_and_screen_target_ASSEMBLY.step','spotify_revB_rear_cover_exploded_ASSEMBLY.step']:
            self.assertTrue((self.directory/n).is_file())
            self.assertGreater((self.directory/n).stat().st_size,100000)

if __name__=='__main__':unittest.main(verbosity=2)
