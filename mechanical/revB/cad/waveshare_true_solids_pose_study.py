#!/usr/bin/env python3
"""Inspect a *local* full Waveshare STEP using real solids against unchanged Rev B case.

This screening does NOT find/certify a continuous entry trajectory. The 2023
manufacturer STEP and the V2 case STEP are required as command-line inputs.
No board source data, private paths or binary CAD models are checked into Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE / "waveshare_step_reference.json"
DIM = HERE / "dimensions.json"
DEFAULT_POSES = ((-7, -110), (-7, -75), (-7, -40), (-7, -20), (-7, 0), (0, 0))


def placement(dim, reference, glass_recess_mm=3.25):
    """Return an orthonormal raw STEP XYZ -> installed world XYZ transform.

    Source STEP: X right, Y up, Z out of glass.
    Physically rotate board 180 degrees in the face plane (USB ends LEFT).
    Rev B world: X right, desk Y back, Z up, face slopes 55 degrees.
    """
    if not 0 <= glass_recess_mm <= 10:
        raise ValueError("Invalid trial glass recess")
    sx, sv = dim["screen_origin"]
    sw, sh = dim["screen_outer"]
    x0, _, _, _, ymax, zfront = reference["step_coordinates"]["front_touch_datum_box_xyz"]
    a = math.radians(dim["face_tilt_deg"])
    c, s = math.cos(a), math.sin(a)
    x_offset = sx + sw + x0
    v_offset = sv + sh - ymax
    w_offset = glass_recess_mm + zfront
    run = dim["front_face_length"] * c
    return (
        (-1.0, 0.0, 0.0, x_offset),
        (0.0, -c, -s, run - v_offset*c + w_offset*s),
        (0.0, -s, c, dim["height"] - v_offset*s - w_offset*c),
    )


def map_point(rows, xyz):
    return tuple(sum(rows[i][j] * xyz[j] for j in range(3)) + rows[i][3] for i in range(3))


def boxes_overlap(a, b, eps=1e-7):
    """Fast *necessary* test. An overlap here is not a true solid collision."""
    return (a.xmax >= b.xmin-eps and b.xmax >= a.xmin-eps
            and a.ymax >= b.ymin-eps and b.ymax >= a.ymin-eps
            and a.zmax >= b.zmin-eps and b.zmax >= a.zmin-eps)


def verified_source(step_path, reference):
    expected = int(reference["source"]["step_bytes"])
    if step_path.stat().st_size != expected:
        raise ValueError("STEP byte size differs from the documented 2023 reference; inspect revision first")
    return hashlib.sha256(step_path.read_bytes()).hexdigest()


def import_manufacturer(step_path):
    """Transfer all STEP roots. Do NOT substitute assembly's filled bounding box."""
    import cadquery as cq
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    reader = STEPControl_Reader()
    if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
        raise ValueError("Unable to read manufacturer's STEP")
    if reader.TransferRoots() < 1:
        raise ValueError("STEP has no transferable roots")
    shape = cq.Shape.cast(reader.OneShape())
    solids = shape.Solids()
    if not solids:
        raise ValueError("STEP contains no solids")
    return shape, solids


def installed_solids(source, rows):
    import cadquery as cq
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    t = gp_Trsf()
    t.SetValues(*[n for row in rows for n in row])
    # Apply a single rigid mapping to avoid drifting from the manufacturer datums.
    mapped = cq.Shape.cast(BRepBuilderAPI_Transform(source.wrapped, t, True).Shape())
    return mapped.Solids()


def check_original_bounds(shape, reference, tol=0.30):
    actual = shape.BoundingBox()
    want = reference["parts"]["full_assembly"]["box"]
    got = (actual.xmin, actual.ymin, actual.zmin,
           actual.xmax, actual.ymax, actual.zmax)
    delta = max(abs(g-w) for g,w in zip(got, want))
    if delta > tol:
        raise ValueError(f"Source STEP extent differs from documented model (max delta {delta:.3f} mm)")
    return {"actual_step_bbox_xyz_mm": [round(v, 4) for v in got],
            "max_reference_box_deviation_mm": round(delta, 4)}


def bbox_xyz_mm(shape):
    """Six world-coordinate bounding extents, useful for local collision diagnosis."""
    b = shape.BoundingBox()
    return [round(v, 3) for v in (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)]


def screen_pose(case, solids, dy, dz, max_booleans):
    """Broad-phase rejection and exact solid booleans for a *single* sampled pose.

    If the per-pose compute budget is exhausted or a boolean raises, the pose is
    explicitly INDETERMINATE, never misreported as collision-free.
    """
    cb = case.BoundingBox()
    candidates = []
    for i, solid in enumerate(solids):
        placed = solid.translate((0, dy, dz))
        if boxes_overlap(cb, placed.BoundingBox()):
            candidates.append((i, placed))
    booleans = 0
    errors = []
    for i, part in candidates:
        if booleans >= max_booleans:
            return {"dy_mm": dy, "dz_mm": dz, "status": "INDETERMINATE_LIMIT",
                    "potentially_intersecting_parts": len(candidates),
                    "exact_booleans_run": booleans, "uncertified": True}
        try:
            intersected = case.intersect(part)
            volume = float(intersected.Volume())
        except Exception as exc:
            errors.append(f"part {i}: {type(exc).__name__}: {str(exc)[:160]}")
            return {"dy_mm": dy, "dz_mm": dz, "status": "INDETERMINATE_BOOLEAN_ERROR",
                    "potentially_intersecting_parts": len(candidates),
                    "exact_booleans_run": booleans, "errors": errors, "uncertified": True}
        booleans += 1
        if volume > 0.05:
            return {"dy_mm": dy, "dz_mm": dz, "status": "SAMPLED_SOLID_COLLISION",
                    "first_colliding_solid_index": i, "first_intersection_mm3": round(volume, 4),
                    "first_colliding_solid_bbox_xyz_mm": bbox_xyz_mm(part),
                    "first_intersection_bbox_xyz_mm": bbox_xyz_mm(intersected),
                    "potentially_intersecting_parts": len(candidates),
                    "exact_booleans_run": booleans, "uncertified": True}
    return {"dy_mm": dy, "dz_mm": dz, "status": "SAMPLED_POSE_CLEAR",
            "potentially_intersecting_parts": len(candidates),
            "exact_booleans_run": booleans, "uncertified": True}


def run(screen_step, case_step, out_dir, max_booleans=160, positions=DEFAULT_POSES):
    import cadquery as cq

    dims = json.loads(DIM.read_text(encoding="utf-8"))
    ref = json.loads(REF.read_text(encoding="utf-8"))
    if not screen_step.is_file() or not case_step.is_file():
        raise FileNotFoundError("Both manufacturer STEP and V2 case STEP must exist locally")
    screen_sha = verified_source(screen_step, ref)
    original, source_solids = import_manufacturer(screen_step)
    source_measure = check_original_bounds(original, ref)
    if len(source_solids) != ref["source"]["solid_count"]:
        raise ValueError(f"Expected {ref['source']['solid_count']} source solids; found {len(source_solids)}. Confirm import semantics")
    rows = placement(dims, ref)
    solids = installed_solids(original, rows)
    if len(solids) != len(source_solids):
        raise ValueError("A STEP solid was lost during rotation/placement")
    case = cq.importers.importStep(str(case_step)).val()
    if not case.isValid() or len(case.Solids()) != 1:
        raise ValueError("Unchanged V2 case must contain exactly one valid solid")
    pose_results = []
    for dy, dz in positions:
        result = screen_pose(case, solids, dy, dz, max_booleans)
        pose_results.append(result)
        print(f"dy={dy:6.1f}  dz={dz:7.1f}  {result['status']}  "
              f"booleans={result['exact_booleans_run']}/{result['potentially_intersecting_parts']}", flush=True)
    report = {
        "study": "TRUE WAVESHARE CAD SOLID SCREENING (DISCRETE POSES ONLY)",
        "manufacturer_step_sha256": screen_sha,
        "case_step_sha256": hashlib.sha256(case_step.read_bytes()).hexdigest(),
        "manufacturer_solid_count": len(solids),
        "collision_volume_threshold_mm3": 0.05,
        "source_bbox_verification": source_measure,
        "trial_glass_inward_w_mm": 3.25,
        "physical_screen_rotation_deg": 180,
        "selected_exterior_and_V2_lid_unchanged": True,
        "case_modified": False,
        "moving_screen_includes_physical_cables_or_rail_addons": False,
        "each_pose_checks_real_step_solids_not_filled_prism": True,
        "pose_results": pose_results,
        "continuous_entry_path_certified": False,
        "screen_mount_screw_access_certified": False,
        "fabrication_approved": False,
        "warnings": [
            "Discrete stationary rigid poses are not a continuous insertion path.",
            "SAMPLED_POSE_CLEAR applies only to exact model at one sampled pose above a 0.05 mm3 penetration threshold, not adjoining motion.",
            "First-collision BBOX values show WHERE model material intersects, not whether the interference is an intentional mount or a manufactured tolerance issue.",
            "No male USB, I2C plug, cable bending, screws, hand clearance or extra carrier rails modeled.",
            "Manufacturer model is from 2023 and may not match board revision supplied.",
            "Only a physical assembly mock-up and measured mating hardware can validate a manufacturable case."
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / "waveshare_true_solids_pose_report.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Wrote:", destination)
    print("NO continuous insertion or physical fit certification.")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manufacturer-step", type=Path, required=True)
    ap.add_argument("--case-step", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--max-booleans-per-pose", type=int, default=160,
                    help="Limit exact per-solid intersections per sampled pose; hitting limit means INDETERMINATE")
    ap.add_argument("--seated-only", action="store_true",
                    help="Skip staging samples; exhaustively check final seated (dy=0,dz=0) only")
    args = ap.parse_args()
    if not 1 <= args.max_booleans_per_pose <= 1000:
        ap.error("--max-booleans-per-pose must be 1..1000")
    run(args.manufacturer_step, args.case_step, args.out_dir,
        max_booleans=args.max_booleans_per_pose,
        positions=((0.0, 0.0),) if args.seated_only else DEFAULT_POSES)


if __name__ == "__main__":
    main()
