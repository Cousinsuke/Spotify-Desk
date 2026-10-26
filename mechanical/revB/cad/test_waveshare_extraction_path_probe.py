#!/usr/bin/env python3
"""Pure waypoint and small synthetic CAD tests, not a complete physical install test."""
from __future__ import annotations

import unittest

from waveshare_extraction_path_probe import (
    poses_for_profile, PROFILES, check_profiles, rotated_at_pose,
)

try:
    import cadquery as cq
except ImportError:
    cq = None


class WaypointTests(unittest.TestCase):
    def test_interpolation_and_origin(self):
        seq = poses_for_profile(PROFILES["forward_pitch_plus"])
        self.assertEqual(len(seq), 7)
        self.assertEqual((seq[0]["dy_mm"], seq[0]["dz_mm"], seq[0]["pitch_deg"]),
                         (0.0, 0.0, 0.0))
        self.assertEqual((seq[-1]["dy_mm"], seq[-1]["dz_mm"], seq[-1]["pitch_deg"]),
                         (-8.0, -28.0, 12.0))

    def test_face_normal_direction_uses_case_slope(self):
        import math
        from waveshare_extraction_path_probe import FACE_TILT_DEG
        end = poses_for_profile(PROFILES["normal_in_4"])[-1]
        self.assertAlmostEqual(end["dy_mm"], 4 * math.sin(math.radians(FACE_TILT_DEG)), delta=0.0001)
        self.assertAlmostEqual(end["dz_mm"], -4 * math.cos(math.radians(FACE_TILT_DEG)), delta=0.0001)
        self.assertGreater(end["dy_mm"], 0)
        self.assertLess(end["dz_mm"], 0)

    def test_two_stage_profile_withdraws_before_lowering(self):
        first = poses_for_profile(PROFILES["normal_in_4"])
        both = poses_for_profile(PROFILES["normal_in_4_then_down_12"])
        self.assertEqual(len(first), 7)
        self.assertEqual(len(both), 13)
        self.assertEqual(both[6]["dy_mm"], first[-1]["dy_mm"])
        self.assertEqual(both[6]["dz_mm"], first[-1]["dz_mm"])
        self.assertEqual(both[-1]["dy_mm"], first[-1]["dy_mm"])
        self.assertAlmostEqual(both[-1]["dz_mm"], first[-1]["dz_mm"] - 12, places=4)
        self.assertTrue(all(a["fraction"] < b["fraction"] for a, b in zip(both, both[1:])))

    def test_segment_interruption_never_approves_path(self):
        first = poses_for_profile(PROFILES["normal_in_4"])
        def probe(p):
            return {"status": ("SAMPLED_SOLID_COLLISION"
                               if p["dz_mm"] < first[-1]["dz_mm"] - 1
                               else "SAMPLED_POSE_CLEAR")}
        result = check_profiles(("normal_in_4_then_down_12",), probe)
        self.assertEqual(result["path_results"][0]["status"], "SAMPLED_SOLID_COLLISION")
        self.assertFalse(result["continuous_entry_path_certified"])

    def test_unknown_profile(self):
        with self.assertRaises(ValueError):
            check_profiles(("unknown",), lambda pose: {"status": "SAMPLED_POSE_CLEAR"})

    def test_collisions_stop_scanning_and_cache_origin(self):
        calls = []
        def probe(p):
            calls.append(p)
            return {"status": "SAMPLED_SOLID_COLLISION" if p["fraction"] >= 0.25 else "SAMPLED_POSE_CLEAR"}
        res = check_profiles(("vertical", "forward"), probe)
        self.assertEqual(res["unique_positions_tested"], 5)
        self.assertEqual(len(calls), 5)
        self.assertTrue(all(p["status"] == "SAMPLED_SOLID_COLLISION" for p in res["path_results"]))

    def test_pose_budget_does_not_imply_clearance(self):
        res = check_profiles(("vertical",),
                             lambda p: {"status": "SAMPLED_POSE_CLEAR"}, max_poses=2)
        self.assertEqual(res["path_results"][0]["status"], "POSE_BUDGET_EXHAUSTED")
        self.assertFalse(res["continuous_entry_path_certified"])

    def test_all_clear_waypoints_still_not_a_sweep(self):
        res = check_profiles(("vertical",), lambda p: {"status": "SAMPLED_POSE_CLEAR"})
        self.assertEqual(res["path_results"][0]["status"],
                         "ALL_SAMPLED_WAYPOINTS_CLEAR_NOT_SWEPT")
        self.assertFalse(res["swept_motion_tested"])


@unittest.skipUnless(cq is not None, "CadQuery optional for synthetic rotation")
class RigidTransformTests(unittest.TestCase):
    def test_rotated_multi_solid_assembly_preserves_volume(self):
        a = cq.Workplane("XY").box(2, 2, 2).translate((1, 2, 3)).val()
        b = cq.Workplane("XY").box(1, 1, 1).translate((7, 3, 8)).val()
        compound = cq.Compound.makeCompound((a, b))
        out = rotated_at_pose(compound, (3, 3, 3),
                              {"dy_mm": -4.0, "dz_mm": -8.0, "pitch_deg": 10.0})
        self.assertEqual(len(out), 2)
        self.assertAlmostEqual(sum(s.Volume() for s in out), a.Volume() + b.Volume(),
                               places=5)


if __name__ == "__main__":
    unittest.main()
