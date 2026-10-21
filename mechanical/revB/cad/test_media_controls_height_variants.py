"""Run from repo root: python -m unittest discover -s mechanical/revB/cad -p test_media_controls_height_variants.py -v"""
from __future__ import annotations
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from rotated_case_prototype import load
from media_controls_fit_study import assumptions
from media_controls_height_variants import (load_spec, variant, all_variant_reports, comparison_svg,
    side_comparison_svg, generate, _validate_heights)
try:
    import cadquery as cq
    HAS_CAD = True
except ImportError:
    HAS_CAD = False

class HeightVariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim,cls.ref,cls.cfg=load()
        cls.base=assumptions();cls.spec=load_spec()
        cls.variants=all_variant_reports(cls.dim,cls.ref,cls.cfg,cls.base,cls.spec)

    def test_exact_heights(self):
        self.assertEqual(list(self.variants.keys()),[2.0,4.0,6.0])
    def test_recessed_2mm_same_as_existing_reference(self):
        self.assertEqual(self.variants[2.0]['cap'],self.base)
    def test_retainer_plate_moves_with_cap(self):
        self.assertEqual([self.variants[h]['cap']['switch_plate_top_inward_mm'] for h in (2,4,6)],[11.5,9.5,7.5])
    def test_cap_top_w_matches_requested_rest_heights(self):
        self.assertEqual([self.variants[h]['report']['keycap_rest_and_pressed'][0]['cap_top_w_mm'] for h in (2,4,6)],[-2,-4,-6])
    def test_full_press_caps_match_nominal_travel(self):
        self.assertEqual([self.variants[h]['report']['keycap_rest_and_pressed'][1]['cap_top_w_mm'] for h in (2,4,6)],[2,0,-2])
    def test_stem_tip_engagement_held_constant(self):
        self.assertEqual([self.variants[h]['report']['keycap_stem_tip_overlap_assumed_mm'] for h in (2,4,6)],[3.3,3.3,3.3])
    def test_plate_clearance_held_constant(self):
        self.assertEqual([self.variants[h]['report']['cap_skirt_to_plate_gap_at_full_press_mm'] for h in (2,4,6)],[1.5,1.5,1.5])
    def test_face_and_key_layout_same_for_all(self):
        a=[self.variants[h]['report'] for h in (2,4,6)]
        self.assertTrue(all(x['outer_case_size_mm'][0]==156 for x in a))
        self.assertTrue(all(x['key_centres_x_mm']==[31.05,61.05,91.05] for x in a))
        self.assertTrue(all(x['rotated_window']['v']==17.09 for x in a))
    def test_all_share_usb_left_rotated_geometry(self):
        self.assertEqual({v['report']['case_variant'] for v in self.variants.values()},{'rounded R5 derived rotated-180 experimental only'})
    def test_profile_and_lateral_clearance_consistent(self):
        self.assertTrue(all(v['report']['lateral_clearance_each_side_mm']==.6 for v in self.variants.values()))
    def test_full_lcd_projection_gap_consistent(self):
        self.assertEqual({v['report']['min_support_to_full_lcd_v_gap_mm'] for v in self.variants.values()},{3.6})
    def test_invalid_height_rejected(self):
        for n in (0,3,5,8,-1,12):
            with self.subTest(height=n),self.assertRaises(ValueError):variant(self.base,self.spec,n)
    def test_plate_too_close_guard(self):
        sp=copy.deepcopy(self.spec)
        sp['minimum_plate_front_inward_mm']=8
        with self.assertRaises(ValueError):variant(self.base,sp,6)
    def test_bad_stroke_plate_guard_rejected(self):
        sp=copy.deepcopy(self.spec)
        sp['plate_shift_per_mm_height']=0
        with self.assertRaises(ValueError):all_variant_reports(self.dim,self.ref,self.cfg,self.base,sp)
    def test_bad_curated_heights_rejected(self):
        sp=copy.deepcopy(self.spec);sp['heights_above_front_mm']=[2.0,3.0,6.0]
        with self.assertRaises(ValueError):_validate_heights(sp)
    def test_svg_comparison_contains_three_heights(self):
        svg=comparison_svg(self.dim,self.cfg,self.variants)
        for x in ['2 mm raised','4 mm raised','6 mm raised','NOT']: # note all three frames
            if x=='NOT':continue
            self.assertIn(x,svg)
        self.assertIn('Nominal MX stems only',svg)
    def test_section_shows_three_plate_depths(self):
        svg=side_comparison_svg(self.base,self.variants)
        for label in ['11.5 mm','9.5 mm','7.5 mm']:
            self.assertIn(label,svg)
    def test_report_only_generates_all_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'g'; data=generate(out,report_only=True)
            self.assertFalse(data['physical_fit_verified'])
            self.assertTrue((out/'4mm'/'media_controls_front_4mm.svg').exists())
            self.assertTrue((out/'6mm'/'mx_section_6mm.svg').exists())
            self.assertFalse(list(out.rglob('*.step')))
    @unittest.skipUnless(HAS_CAD,'optional CadQuery/Shapely needed to build/re-import STEP')
    def test_three_roundtripped_cad_shells_are_distinct_valid_breps(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            generate(folder,report_only=False)
            volumes=[]
            for h in (2,4,6):
                p=folder/f'{h}mm'/'spotify_desk_rounded180_recessed_3keys_EXPERIMENTAL.step'
                imported=cq.importers.importStep(str(p)).val()
                self.assertTrue(imported.isValid());self.assertEqual(len(imported.Solids()),1)
                self.assertAlmostEqual(imported.BoundingBox().xlen,156,places=1)
                volumes.append(imported.Volume())
            self.assertGreater(volumes[0],volumes[1]);self.assertGreater(volumes[1],volumes[2])
    @unittest.skipUnless(HAS_CAD,'optional CadQuery/Shapely needed to build STEP assemblies')
    def test_assemblies_contain_all_three_controls_and_knob(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            generate(out,report_only=False)
            for h in (2,4,6):
                p=out/f'{h}mm'/'spotify_desk_rounded180_with_cap_knob_ENVELOPES.step'
                self.assertTrue(p.exists());self.assertGreater(p.stat().st_size,300000)
                text=p.read_text(errors='ignore')
                for label in ('previous_cap_ASSUMED','play_pause_cap_ASSUMED','next_cap_ASSUMED','black_knurled_knob_OUTER_ENVELOPE'):
                    self.assertIn(label,text)

if __name__=='__main__':unittest.main()
