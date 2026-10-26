#!/usr/bin/env python3
"""CAD-only tests for an actual slide-through underside entry, without lid screws."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from rotated_case_prototype import load
from slide_in_rear_cover_study import specification,layout,generate

try:
    import cadquery as cq
    import shapely
    CAD=True
except ImportError:
    CAD=False

class ScrewlessSlideCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.cfg=load()
        cls.settings=specification()
        cls.plan=layout(cls.dim,cls.ref,cls.cfg,cls.settings)
        cls.directory=Path(tempfile.mkdtemp(prefix='spotify_slide_cover_check_'))
        cls.result=generate(cls.directory,report_only=not CAD)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.directory,ignore_errors=True)

    def changed(self,callback):
        s=copy.deepcopy(self.settings);callback(s)
        return layout(self.dim,self.ref,self.cfg,s)

    def test_round_case_usb_left_and_4mm_caps_preserved(self):
        self.assertEqual(self.dim['width'],156.)
        self.assertEqual(self.settings['physical_rotation_deg'],180)
        self.assertIn('4mm',self.plan['case'])
        self.assertTrue(self.plan['original_models_unchanged'])

    def test_cover_has_zero_screws_while_screen_has_four(self):
        self.assertEqual(self.plan['cover_screw_count'],0)
        self.assertNotIn('cover_fasteners',self.settings)
        self.assertEqual(self.plan['screen_screw_count'],4)

    def test_screen_mounts_still_on_manufacturer_98_by_60_pitch(self):
        self.assertEqual(self.plan['screen_pitch_mm'],[98,60])
        self.assertEqual(sorted(set(x['x'] for x in self.plan['screen_mounts'])),[12.05,110.05])
        self.assertEqual(sorted(set(x['v'] for x in self.plan['screen_mounts'])),[11.8,71.8])

    def test_cover_has_conservative_plan_gap(self):
        p=self.plan['cover_body'];o=self.plan['opening']
        for key in ('x','y'):
            self.assertAlmostEqual(p[f'{key}_min']-o[f'{key}_min'],.4)
            self.assertAlmostEqual(o[f'{key}_max']-p[f'{key}_max'],.4)
        self.assertAlmostEqual(p['z_max']-p['z_min'],2)

    def test_upper_lower_capture_lips_do_not_collide_with_plate(self):
        p=self.plan['cover_body']
        self.assertGreater(p['z_min']-self.plan['rail_lower_top_z_mm'],.15)
        self.assertGreater(self.plan['rail_upper_bottom_z_mm']-p['z_max'],.20)
        self.assertAlmostEqual(self.plan['side_rail_overlap_on_cover_mm'],2.6)

    def test_throat_is_taller_than_panel_and_below_upper_support(self):
        self.assertGreater(self.plan['rear_entry_mouth_top_z_mm'],self.plan['cover_body']['z_max'])
        self.assertLess(self.plan['rear_entry_mouth_top_z_mm'],self.plan['rail_upper_bottom_z_mm'])

    def test_pull_tab_reaches_the_exterior_rear_face(self):
        tab=self.plan['tab']
        self.assertGreater(tab['y_max'],self.dim['depth'])
        self.assertGreater(tab['y_min'],self.plan['cover_body']['y_max']-2)
        self.assertAlmostEqual(tab['x_min']+tab['x_max'],self.dim['width'])

    def test_slide_direction_explicit(self):
        self.assertIn('Y+',self.plan['slide_direction'])
        self.assertIn('rear',self.plan['slide_direction'].lower())

    def test_no_false_claim_of_snap_lock_and_physical_fit(self):
        self.assertFalse(self.plan['physical_fit_verified'])
        self.assertFalse(self.plan['positive_retention_verified'])
        self.assertIn('no proven positive latch',self.plan['retention_warning'].lower())
        self.assertTrue(any('slide out' in x for x in self.plan['open_questions']))

    def test_invalid_orientation_rejected(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s.update(physical_rotation_deg=0))

    def test_invalid_keycap_height_rejected(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s.update(cap_rest_height_mm=6))

    def test_rear_opening_must_be_consistent(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s['rear_opening'].update(y_edge_mm=11))

    def test_too_narrow_rail_rejected(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s['sliding_rails'].update(overhang_into_opening_mm=.4))

    def test_upper_rail_touching_cover_rejected(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s['sliding_rails'].update(upper_rail_z_min_mm=2.60))

    def test_rear_throat_too_low_rejected(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s['sliding_rails'].update(mouth_cut_upper_z_mm=2.65))

    def test_unwanted_cover_fasteners_rejected(self):
        with self.assertRaises(ValueError):self.changed(lambda s:s.update(cover_fasteners={'screws':4}))

    def test_report_only_outputs_are_readable(self):
        for name in ('slide_cover_design_report.json','slide_cover_rail_section.svg','slide_cover_underside_plan.svg'):
            self.assertTrue((self.directory/name).exists())
        report=json.loads((self.directory/'slide_cover_design_report.json').read_text())
        self.assertEqual(report['plan']['cover_screw_count'],0)
        self.assertIn('slide', (self.directory/'slide_cover_underside_plan.svg').read_text().lower())

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely required for STEP checks')
    def test_two_distinct_valid_step_solids_export(self):
        paths=['spotify_R5_USBleft_4mm_SLIDER_case_experimental.step','spotify_R5_SLIDE_IN_bottom_lid_experimental.step']
        for fn in paths:
            solid=cq.importers.importStep(str(self.directory/fn)).val()
            self.assertTrue(solid.isValid());self.assertEqual(len(solid.Solids()),1)
        body=cq.importers.importStep(str(self.directory/paths[0])).val()
        self.assertAlmostEqual(body.BoundingBox().xlen,156,places=2)

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely required for STEP checks')
    def test_cover_not_drilled_at_old_four_screw_locations(self):
        cover=cq.importers.importStep(str(self.directory/'spotify_R5_SLIDE_IN_bottom_lid_experimental.step')).val()
        depth=self.dim['depth'];p=self.plan['cover_body']
        for x in (18.5,137.5):
            for y in (19.5,depth-19.5):
                probe=(cq.Workplane('XY').workplane(offset=p['z_min']+.4).center(x,y)
                       .circle(.5).extrude(.9).val())
                self.assertGreater(cover.intersect(probe).Volume(),.5,'Accidental old screw hole detected')

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely required for STEP checks')
    def test_real_swept_translation_is_nonintersecting(self):
        self.assertTrue(self.result['cad_build'])
        sweep=self.result['cad_build']['sweep']
        self.assertGreaterEqual(len(sweep),9)
        self.assertTrue(all(x['overlap_mm3']<.06 for x in sweep))
        self.assertAlmostEqual(self.result['cad_build']['closed_overlap_mm3'],0,places=3)

    @unittest.skipUnless(CAD,'optional CadQuery/Shapely required for STEP checks')
    def test_four_historical_screen_mounts_and_assemblies(self):
        for n in ('spotify_R5_4mm_slider_installed_REFERENCE_ASSEMBLY.step',
                  'spotify_R5_4mm_slider_open_38mm_REFERENCE_ASSEMBLY.step'):
            self.assertGreater((self.directory/n).stat().st_size,100000)
        self.assertEqual(self.result['cad_build']['rail_count'],4)
        self.assertEqual(self.plan['screen_screw_count'],4)

if __name__=='__main__':unittest.main(verbosity=2)
