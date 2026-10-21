#!/usr/bin/env python3
"""Conservative Rev B X/V projection fit audit, not a 3D collision or fabrication test.

Reads the checked-in dimensions.json. Cable extension and 2mm design guard are
parametric trial assumptions, NOT manufacturer limits.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ENCODER_BODY_MM = 13.2  # Bourns nominal body; terminals not included
DEFAULT_SCENARIOS = (14., 17., 20., 25.)
DEFAULT_GUARD_MM = 2.  # design exploration, not an approved tolerance


def audit(dimensions: dict, cable_mm: float, guard_mm: float = DEFAULT_GUARD_MM) -> dict:
    if cable_mm < 0 or guard_mm < 0:
        raise ValueError("Cable extension and design guard must be non-negative")
    sx, sv = dimensions["screen_origin"]
    sw, sh = dimensions["screen_outer"]
    keys = dimensions["keys_x"]
    key_v = dimensions["keys_v"]
    knob_x = dimensions["knob_x"]
    width = dimensions["width"]
    screen_right = sx + sw
    encoder_left = knob_x - ENCODER_BODY_MM/2
    gap = encoder_left - (screen_right + cable_mm)
    additional = max(0., guard_mm-gap)
    return dict(
        cable_extension_mm=cable_mm,
        trial_guard_mm=guard_mm,
        screen_right_mm=screen_right,
        encoder_body_left_mm=encoder_left,
        lateral_gap_mm=round(gap, 3),
        meets_trial_2d_guard=gap >= guard_mm-1e-9,
        extra_knob_shift_mm=round(additional, 3),
        width_if_shift_knob_and_right_edge_mm=round(width+additional, 3),
        key_row_center_error_mm=round(sum(keys)/len(keys)-(sx+sw/2), 6),
        lcd_to_keycap_gap_mm=round(key_v-9-(sv+sh), 3),
        lcd_to_switch_opening_gap_mm=round(key_v-7-(sv+sh), 3),
        body_to_side_inner_wall_mm=round(
            width-dimensions["wall_assumed"]-(knob_x+ENCODER_BODY_MM/2), 3),
        knob_to_outer_edge_mm=round(width-(knob_x+dimensions["knob_d"]/2), 3),
        physical_fit_verified=False)


def make_svg(dimensions: dict, cable_mm: float, guard_mm: float = DEFAULT_GUARD_MM) -> str:
    """Illustrative front projection only. SVG viewBox coordinates are nominal mm."""
    a=audit(dimensions,cable_mm,guard_mm)
    w=dimensions["width"];h=dimensions["front_face_length"]
    sx,sv=dimensions["screen_origin"];sw,sh=dimensions["screen_outer"]
    ox,ov=dimensions["display_visible_offset"]
    vw,vh=dimensions["display_visible"]
    kx,kv=dimensions["knob_x"],dimensions["knob_v"]
    color="#f3ac48" if a["meets_trial_2d_guard"] else "#ef6e56"
    keys="\n".join(
        f'<rect x="{x-9:.2f}" y="{dimensions["keys_v"]-9:.2f}" width="18" height="18" '
        'fill="#d9e6ee" stroke="#6e8292" stroke-width=".6"/>'
        for x in dimensions["keys_x"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-7 -17 {w+14} {h+44}" width="{5*(w+14)}" height="{5*(h+44)}">
<title>Rev B conceptual fit projection (NOT connector geometry)</title>
<rect width="{w}" height="{h}" fill="#282f3a" stroke="#8096a8" stroke-width="1"/>
<rect x="{sx}" y="{sv}" width="{sw}" height="{sh}" fill="#113743" stroke="#83b8c4" stroke-width=".6"/>
<rect x="{sx+ox}" y="{sv+ov}" width="{vw}" height="{vh}" fill="#2684a4" opacity=".85"/>
<!-- Assumed X cable extension. The 33mm V band is illustrative, not a manufacturer connector position. -->
<rect x="{a["screen_right_mm"]}" y="23" width="{cable_mm}" height="33" fill="{color}"
fill-opacity=".4" stroke="{color}" stroke-dasharray="1.4 1.2" stroke-width=".65"/>
{keys}
<circle cx="{kx}" cy="{kv}" r="{dimensions["knob_d"]/2}" fill="#101217" stroke="#eee" stroke-width=".75"/>
<rect x="{kx-6.6}" y="{kv-6.6}" width="13.2" height="13.2" fill="none"
stroke="#ffad71" stroke-width=".7" stroke-dasharray="1.5 1"/>
<g font-family="Arial,sans-serif" font-size="3.2" fill="#edf2f7">
<text x="0" y="-9">Rev B / front X-V plane / 156 x 110 mm</text>
<text x="0" y="120">I2C extension trial: {cable_mm:.1f} mm; assumed lateral gap {a["lateral_gap_mm"]:.1f} mm</text>
<text x="0" y="125">Trial guard: {guard_mm:.1f} mm / projection pass={a["meets_trial_2d_guard"]}</text>
<text x="0" y="130">NOT physical connector geometry, 3D clearance, or a manufacturing drawing.</text>
</g></svg>
'''


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dimensions",type=Path,default=Path(__file__).with_name("dimensions.json"))
    p.add_argument("--cable-mm",type=float,nargs="*",default=list(DEFAULT_SCENARIOS))
    p.add_argument("--guard-mm",type=float,default=DEFAULT_GUARD_MM)
    p.add_argument("--svg",type=Path,help="Illustrative SVG for the first cable scenario")
    args=p.parse_args()
    d=json.loads(args.dimensions.read_text(encoding="utf-8"))
    print("REV B FRONT-PLANE STUDY ONLY; not physically fit-verified.")
    print("Assumed cable  X gap   trial guard   2D result   extra case width")
    for length in args.cable_mm:
        a=audit(d,length,args.guard_mm)
        print(f'{length:>7.1f} mm   {a["lateral_gap_mm"]:>6.1f} mm   '
              f'{args.guard_mm:>5.1f} mm      '
              f'{"PASS" if a["meets_trial_2d_guard"] else "CHECK":5}        '
              f'+{a["extra_knob_shift_mm"]:.1f} mm -> {a["width_if_shift_knob_and_right_edge_mm"]:.1f} mm')
    print("OPEN: real I2C plug/bend & V location, encoder terminals/nut/push, MX retention, "
          "LCD holes, USB-C access, Z collision, standoffs and fasteners.")
    if args.svg:
        if not args.cable_mm:
            p.error("--svg needs at least one --cable-mm value")
        args.svg.write_text(make_svg(d,args.cable_mm[0],args.guard_mm),encoding="utf-8")
        print(f"Wrote illustrative SVG: {args.svg}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
