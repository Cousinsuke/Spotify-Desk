#!/usr/bin/env python3
"""Regression tests for local-only manufacturer STEP rigid-pose screening."""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from types import SimpleNamespace

from waveshare_true_solids_pose_study import (
    boxes_overlap, map_point, placement, screen_pose
)
from rotated_case_prototype import load
from orientation_180_study import rotated_parts
from screen_install_path_study import expanded_box_corners_world

HERE = Path(__file__).resolve().parent


class PlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dim, cls.ref, _ = load()
        cls.rows = placement(cls.dim, cls.ref)

    def test_rotation_preserves_lengths(self):
        r = self.rows
        vecs = [tuple(r[i][j] for i in range(3)) for j in range(3)]
        for v in vecs:
            self.assertAlmostEqual(sum(a*a for a in v), 1.0, places=9)
        for i in range(3):
            for j in range(i+1, 3):
                self.assertAlmostEqual(sum(a*b for a,b in zip(vecs[i],vecs[j])), 0, places=9)

    def test_source_bbox_matches_previous_full_assembly_reference(self):
        box = self.ref["parts"]["full_assembly"]["box"]
        lo, hi = box[:3], box[3:]
        pts = [map_point(self.rows, (x,y,z)) for x in (lo[0],hi[0])
               for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
        old_part = rotated_parts(self.dim, self.ref, 180)["full_assembly"]
        expected = expanded_box_corners_world(self.dim, old_part, 3.25)
        for axis in range(3):
            self.assertAlmostEqual(min(p[axis] for p in pts),
                                   min(p[axis] for p in expected), delta=0.006)
            self.assertAlmostEqual(max(p[axis] for p in pts),
                                   max(p[axis] for p in expected), delta=0.006)

    def test_source_usb_moves_to_left(self):
        usb = self.ref["parts"]["usb_type_c1"]["box"]
        xmin, ymin, zmin, xmax, ymax, zmax = usb
        p = map_point(self.rows, ((xmin+xmax)/2, (ymin+ymax)/2, (zmin+zmax)/2))
        self.assertLess(p[0], self.dim["width"]/2)

    def test_invalid_glass_recess(self):
        with self.assertRaises(ValueError):
            placement(self.dim, self.ref, -1.0)

    def test_bbox_broadphase(self):
        a = SimpleNamespace(xmin=0,xmax=2,ymin=0,ymax=2,zmin=0,zmax=2)
        b = SimpleNamespace(xmin=3,xmax=4,ymin=0,ymax=2,zmin=0,zmax=2)
        self.assertFalse(boxes_overlap(a, b))
        b.xmin = 1
        self.assertTrue(boxes_overlap(a, b))


try:
    import cadquery as cq
except ImportError:
    cq = None


@unittest.skipUnless(cq is not None, "CadQuery optional for synthetic B-Rep tests")
class CADTests(unittest.TestCase):
    def setUp(self):
        self.case = cq.Workplane("XY").box(10,10,10).val()
        self.parts = [cq.Workplane("XY").box(2,2,2).translate((4,0,0)).val()]

    def test_true_intersection(self):
        r = screen_pose(self.case, self.parts, 0, 0, 3)
        self.assertEqual(r["status"], "SAMPLED_SOLID_COLLISION")
        self.assertGreater(r["first_intersection_mm3"], 0)
        self.assertEqual(len(r["first_intersection_bbox_xyz_mm"]), 6)
        self.assertEqual(len(r["first_colliding_solid_bbox_xyz_mm"]), 6)
        x0,y0,z0,x1,y1,z1 = r["first_intersection_bbox_xyz_mm"]
        self.assertGreater(x1, x0)
        self.assertGreater(y1, y0)
        self.assertGreater(z1, z0)

    def test_pose_translation_clear(self):
        r = screen_pose(self.case, self.parts, 50, 0, 3)
        self.assertEqual(r["status"], "SAMPLED_POSE_CLEAR")
        self.assertEqual(r["exact_booleans_run"], 0)

    def test_budget_exhaustion_is_not_clear(self):
        parts = [cq.Workplane("XY").box(1,1,1).translate((0,0,0)).val(),
                 cq.Workplane("XY").box(1,1,1).translate((2,0,0)).val()]
        r = screen_pose(self.case, parts, 0, 0, 1)
        # First part collides, so limited budget can still conclude a collision.
        self.assertEqual(r["status"], "SAMPLED_SOLID_COLLISION")
        far_shell = (cq.Workplane("XY").box(10,10,10)
                     .cut(cq.Workplane("XY").box(8,8,8)).val())
        r2 = screen_pose(far_shell, parts, 0, 0, 1)
        self.assertEqual(r2["status"], "INDETERMINATE_LIMIT")
        self.assertTrue(r2["uncertified"])
        self.assertNotIn("first_intersection_bbox_xyz_mm", r2)


if __name__ == "__main__":
    unittest.main()
