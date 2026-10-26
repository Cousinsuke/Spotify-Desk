#!/usr/bin/env python3
"""Screen-only rigid extraction candidates against original R5 CAD and local Waveshare STEP.

Reports collisions at sampled poses, NOT certified continuous paths. Does not alter CAD.
Use with the local-only manufacturer's STEP; do not check binary files into Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from waveshare_true_solids_pose_study import (
    HERE, DIM, REF, verified_source, import_manufacturer,
    check_original_bounds, installed_solids, placement, screen_pose,
)

FRACTIONS = (0.0, 0.125, 0.25, 0.375, 0.5, 0.75, 1.0)
# Rigid-body motion from seated position towards underside, not through a cable-connected assembly.
PROFILES = {
    "vertical": {"end_dy_mm": 0.0, "end_dz_mm": -28.0, "end_pitch_deg": 0.0},
    "forward": {"end_dy_mm": -8.0, "end_dz_mm": -28.0, "end_pitch_deg": 0.0},
    "forward_pitch_plus": {"end_dy_mm": -8.0, "end_dz_mm": -28.0, "end_pitch_deg": 12.0},
    "forward_pitch_minus": {"end_dy_mm": -8.0, "end_dz_mm": -28.0, "end_pitch_deg": -12.0},
    "rearward": {"end_dy_mm": 6.0, "end_dz_mm": -28.0, "end_pitch_deg": 0.0},
}
# For a 55-degree front face, +local W points inward/backward and down.
# Trying vertical-down first can drive the board into the sloped face lip.
# Use the CURRENT dimensioned face angle instead of a hardcoded world direction.
FACE_TILT_DEG = float(json.loads(DIM.read_text(encoding="utf-8"))["face_tilt_deg"])
NORMAL_Y = math.sin(math.radians(FACE_TILT_DEG))
NORMAL_Z = -math.cos(math.radians(FACE_TILT_DEG))
PROFILES.update({
    "normal_in_4": {
        "end_dy_mm": 4.0 * NORMAL_Y, "end_dz_mm": 4.0 * NORMAL_Z, "end_pitch_deg": 0.0
    },
    "normal_in_8": {
        "end_dy_mm": 8.0 * NORMAL_Y, "end_dz_mm": 8.0 * NORMAL_Z, "end_pitch_deg": 0.0
    },
    # Only after withdrawing 4mm along the face normal, try 12mm further down.
    # This is a two-stage waypoint hypothesis, NOT a verified extraction route.
    "normal_in_4_then_down_12": {
        "stages": [
            {"end_dy_mm": 4.0 * NORMAL_Y, "end_dz_mm": 4.0 * NORMAL_Z, "end_pitch_deg": 0.0},
            {"end_dy_mm": 4.0 * NORMAL_Y, "end_dz_mm": 4.0 * NORMAL_Z - 12.0, "end_pitch_deg": 0.0}
        ]
    }
})
DEFAULT_PROFILES = ("normal_in_4", "normal_in_8", "normal_in_4_then_down_12")


def poses_for_profile(profile, fractions=FRACTIONS):
    """Absolute desk-Y/Z and global-X pitch offsets from existing seated alignment."""
    if not fractions or fractions[0] != 0 or fractions[-1] != 1:
        raise ValueError("Fraction sequence must start 0 and finish 1")
    if any(not 0 <= t <= 1 for t in fractions) or any(a >= b for a, b in zip(fractions, fractions[1:])):
        raise ValueError("Fractions must increase strictly within [0,1]")
    def lerp(a, b, t):
        return round(a + (b-a)*t, 4)
    start = {"end_dy_mm": 0.0, "end_dz_mm": 0.0, "end_pitch_deg": 0.0}
    stages = profile.get("stages", [profile])
    if not stages:
        raise ValueError("Profile has no motion stages")
    result = []
    for stage_index, end in enumerate(stages):
        for t in fractions:
            if stage_index and t == 0:
                continue  # Do not repeat the preceding segment endpoint.
            result.append({
                "fraction": round((stage_index + t)/len(stages), 4),
                "stage": stage_index + 1,
                "dy_mm": lerp(start["end_dy_mm"], end["end_dy_mm"], t),
                "dz_mm": lerp(start["end_dz_mm"], end["end_dz_mm"], t),
                "pitch_deg": lerp(start["end_pitch_deg"], end["end_pitch_deg"], t),
            })
        start = end
    return result


def check_profiles(names, probe, max_poses=24):
    """probe(pose)-> status dict. Cache duplicate origins. Never call incomplete routes clear."""
    if not names or not 1 <= max_poses <= 500:
        raise ValueError("Must supply profiles and a reasonable pose limit")
    unknown = [n for n in names if n not in PROFILES]
    if unknown:
        raise ValueError(f"Unknown path profiles: {unknown}")
    cache = {}
    paths = []
    for name in names:
        path = []
        end_state = None
        for p in poses_for_profile(PROFILES[name]):
            key = (p["dy_mm"], p["dz_mm"], p["pitch_deg"])
            if key not in cache:
                if len(cache) >= max_poses:
                    end_state = "POSE_BUDGET_EXHAUSTED"
                    break
                cache[key] = probe(p)
            record = {**p, **cache[key]}
            path.append(record)
            if record["status"] != "SAMPLED_POSE_CLEAR":
                end_state = record["status"]
                break
        if end_state is None:
            end_state = "ALL_SAMPLED_WAYPOINTS_CLEAR_NOT_SWEPT"
        paths.append({"profile": name, "status": end_state,
                      "waypoints_tested": len(path), "waypoints": path})
    return {"unique_positions_tested": len(cache), "path_results": paths,
            "continuous_entry_path_certified": False, "swept_motion_tested": False}


def rotated_at_pose(base, pivot, pose):
    """Tilt the whole assembly around world-X through installed midpoint, then translate."""
    angle = pose["pitch_deg"]
    if angle:
        part = base.rotate(pivot, (pivot[0] + 1, pivot[1], pivot[2]), angle)
    else:
        part = base
    if pose["dy_mm"] or pose["dz_mm"]:
        part = part.translate((0, pose["dy_mm"], pose["dz_mm"]))
    return part.Solids()


def run(manufacturer, case_file, out_dir, profiles=DEFAULT_PROFILES,
        max_poses=24, max_booleans=700):
    import cadquery as cq
    dim = json.loads(DIM.read_text(encoding="utf-8"))
    ref = json.loads(REF.read_text(encoding="utf-8"))
    if not manufacturer.is_file() or not case_file.is_file():
        raise FileNotFoundError("Both original manufacturer STEP and V2 case STEP required")
    manufacturer_sha = verified_source(manufacturer, ref)
    original, raw_solids = import_manufacturer(manufacturer)
    source_bbox = check_original_bounds(original, ref)
    if len(raw_solids) != ref["source"]["solid_count"]:
        raise ValueError("Unexpected manufacturer STEP solid count")
    installed = installed_solids(original, placement(dim, ref))
    if len(installed) != len(raw_solids):
        raise ValueError("Lost solids when aligning screen")
    case = cq.importers.importStep(str(case_file)).val()
    if not case.isValid() or len(case.Solids()) != 1:
        raise ValueError("Expected unchanged, valid single-solid case STEP")
    body = cq.Compound.makeCompound(installed)
    bbox = body.BoundingBox()
    pivot = ((bbox.xmin + bbox.xmax)/2, (bbox.ymin + bbox.ymax)/2,
             (bbox.zmin + bbox.zmax)/2)

    def probe(pose):
        parts = rotated_at_pose(body, pivot, pose)
        if len(parts) != ref["source"]["solid_count"]:
            raise ValueError("Lost model solids during rigid pose rotation")
        result = screen_pose(case, parts, 0, 0, max_booleans)
        clash = result.get("first_intersection_bbox_xyz_mm")
        where = f"; XYZ clash bounds={clash}" if clash is not None else ""
        print(f"dy={pose['dy_mm']:+6.2f}, dz={pose['dz_mm']:+6.2f}, "
              f"pitch={pose['pitch_deg']:+5.2f}: {result['status']} "
              f"({result['exact_booleans_run']}/{result['potentially_intersecting_parts']} Booleans)"
              f"{where}", flush=True)
        # Original solver sees part-already-transformed so its internal 0,0 offsets are not route offsets.
        return {k:v for k,v in result.items() if k not in ("dy_mm", "dz_mm")}

    scan = check_profiles(profiles, probe, max_poses)
    report = {
        "study": "REV B SCREEN REMOVAL: SAMPLED RIGID EXTRACTION POSES ONLY",
        "manufacturer_step_sha256": manufacturer_sha,
        "case_step_sha256": hashlib.sha256(case_file.read_bytes()).hexdigest(),
        "manufacturer_solid_count": len(installed),
        "source_bbox_verification": source_bbox,
        "screen_pivot_world_xyz_mm": [round(v, 3) for v in pivot],
        "solid_penetration_threshold_mm3": 0.05,
        "case_or_lid_modified": False,
        "screen_screws_or_cables_modeled": False,
        "assumed_glass_recess_mm": 3.25,
        "profiles": list(profiles),
        **scan,
        "fabrication_approved": False,
        "warnings": [
            "The reverse extraction waypoints do not test swept motion between poses.",
            "Inward face-normal motion (Y+ and Z- for selected 55 degree face) may itself clash with existing LCD supports.",
            "A blocked sampled position rejects only that particular rigid pose/route.",
            "No cable, screw head, driver, carrier rail, print tolerances or fitted hardware modeled.",
            "Any clear path waypoints are NOT physical insertion proof or measured minimum clearance.",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "waveshare_extraction_waypoint_report.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Wrote:", target)
    print("No continuous installation route certified.")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manufacturer-step", required=True, type=Path)
    ap.add_argument("--case-step", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--profiles", nargs="+", choices=tuple(PROFILES), default=list(DEFAULT_PROFILES))
    ap.add_argument("--max-total-poses", type=int, default=24)
    ap.add_argument("--max-booleans-per-pose", type=int, default=700)
    a = ap.parse_args()
    if not 1 <= a.max_total_poses <= 500 or not 1 <= a.max_booleans_per_pose <= 1000:
        ap.error("Invalid checking budgets")
    run(a.manufacturer_step, a.case_step, a.out_dir,
        tuple(a.profiles), a.max_total_poses, a.max_booleans_per_pose)


if __name__ == "__main__":
    main()
