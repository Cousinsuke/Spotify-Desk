#!/usr/bin/env python3
"""Make THREE *separate* experimental R5 USB-left Rev B CAD models.

Trial keycap-rest heights: 2, 4 and 6 mm above sloping enclosure face.
Moves BOTH keycap resting plane AND underlying MX clip plate per height, to keep
nominal stem engagement and skirt-to-plate full travel margin the same. No real
cap/male USB/keyboard switch dimensions are measured. Experimental STEP CAD is
NOT a manufacture-ready case and never overwrites the previous CAD.

--report-only requires Python stdlib. Actual .step generation requires CadQuery
and Shapely; a separately published output ZIP contains all generated models.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
from html import escape

from rotated_case_prototype import load
from media_controls_fit_study import (
    assumptions, study, cad_build, layout_svg, section_svg, icon_svg,
)

HERE = Path(__file__).resolve().parent
SPEC = HERE / 'keycap_height_variant_parameters.json'


def load_spec(path=None):
    return json.loads(Path(path or SPEC).read_text(encoding='utf-8'))


def variant(base_cap, variant_spec, height):
    """Adjust plate and cap as one assembly; nominal stem engagement unchanged."""
    valid = variant_spec['heights_above_front_mm']
    height = float(height)
    if height not in valid:
        raise ValueError(f'Height {height} must be one of {valid}')
    if not 0 < height < 10:
        raise ValueError('Cap must be above panel, but is not a tall keyboard stack')
    cap = copy.deepcopy(base_cap)
    ref_h = variant_spec['reference_height_mm']
    ref_plate = variant_spec['reference_plate_top_inward_mm']
    delta = height - ref_h
    plate = ref_plate + delta * variant_spec['plate_shift_per_mm_height']
    if plate < variant_spec['minimum_plate_front_inward_mm']:
        raise ValueError('Retaining plate moves too close to outer skin')
    cap['cap_rest_above_skin_mm'] = height
    cap['switch_plate_top_inward_mm'] = round(plate, 3)
    return cap


def all_variant_reports(dim, ref, cfg, base_cap, spec):
    out = {}
    for height in spec['heights_above_front_mm']:
        cap = variant(base_cap, spec, height)
        a = study(dim, ref, cfg, cap)
        if abs(a['cap_skirt_to_plate_gap_at_full_press_mm'] - spec['full_travel_skirt_to_plate_guard_mm']) > 1e-5:
            raise ValueError('Full stroke margin is not preserved')
        if height > spec['reference_height_mm']:
            original=study(dim,ref,cfg,variant(base_cap,spec,spec['reference_height_mm']))
            if abs(a['keycap_stem_tip_overlap_assumed_mm'] - original['keycap_stem_tip_overlap_assumed_mm']) > 1e-5:
                raise ValueError('Nominal stem tip engagement is not preserved')
        out[height] = {'cap':cap,'report':a}
    return out


def comparison_svg(dim, cfg, all_results):
    """Three-panel dimensioned vector front elevation, not a photorealistic render."""
    win = next(iter(all_results.values()))['report']['rotated_window']
    case_w=dim['width']; L=dim['front_face_length']
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1250 460" width="1250" height="460">',
           '<rect width="1250" height="460" fill="#111620"/>',
           '<text x="34" y="35" font-size="23" font-family="Arial" fill="#f0f4fa">Spotify Desk Rev B / rounded / USB LEFT / media cap resting heights</text>',
           '<text x="34" y="59" font-size="15" font-family="Arial" fill="#aebbc9">Dimensioned design comparison; 18 mm cap envelope, 4 mm assumed travel and 1.5 mm MX clip plate</text>']
    scale=2.1
    for i,(height,data) in enumerate(all_results.items()):
        cap=data['cap']; report=data['report']; sx=36+i*405; ty=115
        def f(x): return sx+x*scale
        def g(v): return ty+v*scale
        parts += [f'<rect x="{sx-3}" y="{ty-38}" width="{case_w*scale+13}" height="344" rx="12" fill="#1b2230" stroke="#586878"/>',
                  f'<text x="{sx+9}" y="{ty-9}" font-size="20" font-family="Arial" fill="#ffffff">{height:g} mm raised</text>',
                  f'<rect x="{f(0)}" y="{g(0)}" width="{case_w*scale}" height="{L*scale}" rx="10.5" fill="#35414f" stroke="#9cabb5"/>',
                  f'<rect x="{f(win["x"])}" y="{g(win["v"])}" width="{win["width"]*scale}" height="{win["height"]*scale}" rx="3" fill="#071923" stroke="#4b728b"/>',
                  f'<circle cx="{f(dim["knob_x"])}" cy="{g(dim["knob_v"])}" r="{cap["knob_diameter_mm"]*scale/2}" fill="#121417" stroke="#b8c1c9" stroke-width="2"/>']
        parts.append(f'<text x="{f(win["x"]+5)}" y="{g(win["v"]+27)}" fill="#70abc6" font-size="15" font-family="Arial">800 x 480</text>')
        for sym,kx in zip(('PREV','PLAY','NEXT'),dim['keys_x']):
            kw=cap['well_width_mm']*scale; c=cap['cap_width_mm']*scale
            parts.append(f'<rect x="{f(kx)-kw/2}" y="{g(dim["keys_v"])-kw/2}" width="{kw}" height="{kw}" rx="3.4" fill="#11161c" stroke="#879099"/>')
            parts.append(f'<rect x="{f(kx)-c/2}" y="{g(dim["keys_v"])-c/2}" width="{c}" height="{c}" rx="3.0" fill="#1d222a" stroke="#e5e6e9" stroke-width=".7"/>')
            paths={'PREV':'M12 9 L12 29 M31 9 L14 19 L31 29 Z', 'PLAY':'M12 9 L25 19 L12 29 Z M30 9 L30 29 M36 9 L36 29', 'NEXT':'M30 9 L30 29 M11 9 L28 19 L11 29 Z'}
            z=f(kx)-20; y=g(dim['keys_v'])-20
            parts.append(f'<path d="{paths[sym]}" transform="translate({z:.2f} {y:.2f})" stroke="#f5f7fa" stroke-width="1.6" fill="none"/>')
        parts.append(f'<text x="{sx+12}" y="{g(L)+28}" font-size="15" font-family="Arial" fill="#d7e2eb">Plate: {report["plate_top_w_mm"]:g} mm inward   /   full press guard: {report["cap_skirt_to_plate_gap_at_full_press_mm"]:g} mm</text>')
    parts.append('<text x="34" y="443" font-size="14" fill="#deae81" font-family="Arial">NOTE: same enclosure silhouette; changes are in cap and switch-retaining-plate Z/W positions. Nominal MX stems only, not fitted parts.</text>')
    return '\n'.join(parts+['</svg>'])+'\n'


def side_comparison_svg(capbase, all_results):
    """W-to-depth diagram with fixed panel reference for all three positions."""
    o=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 490" width="1200" height="490">',
       '<rect width="1200" height="490" fill="#141922"/>',
       '<text x="26" y="36" fill="#f6f8fc" font-family="Arial" font-size="23">Switch section comparison / same theoretical stem engagement</text>',
       '<text x="26" y="60" fill="#d3dee7" font-family="Arial" font-size="15">W (inward): zero at external skin. Caps above case have negative W. Not a measured cap or switch.</text>']
    for n,(height,v) in enumerate(all_results.items()):
        d=v['report'];cap=v['cap'];ox=20+n*400;scale=10;cy=226
        def px(x):return ox+200+x*scale
        def py(w):return cy+w*scale
        def rect(x1,x2,w1,w2,color):
            o.append(f'<rect x="{px(x1):.2f}" y="{py(w1):.2f}" width="{(x2-x1)*scale:.2f}" height="{(w2-w1)*scale:.2f}" fill="{color}"/>')
        well=cap['well_width_mm'];outer=cap['well_outer_support_width_mm'];pt=cap['switch_plate_top_inward_mm'];h=height;dp=cap['cap_depth_assumed_mm'];tr=cap['switch_total_travel_nominal_mm']
        o += [f'<rect x="{ox}" y="90" width="385" height="347" rx="8" fill="#202a35"/>',
              f'<text x="{ox+20}" y="124" fill="#fbfbfd" font-family="Arial" font-size="22">{h:g} mm proud at REST</text>',
              f'<text x="{ox+20}" y="147" fill="#bacbdd" font-family="Arial" font-size="14">Mount plate top W = {pt:.1f} mm</text>']
        rect(-17,-well/2,0,3,'#7c8b98');rect(well/2,17,0,3,'#7c8b98')
        rect(-outer/2,-well/2,3,pt,'#556671');rect(well/2,outer/2,3,pt,'#556671')
        clip=cap['switch_plate_aperture_mm']/2
        rect(-outer/2,-clip,pt,pt+1.5,'#ebb46b');rect(clip,outer/2,pt,pt+1.5,'#ebb46b')
        rect(-7.8,7.8,pt-6.6,pt,'#5893a3')
        # Cap outer lid and side skirts at rest
        rect(-cap['cap_width_mm']/2,cap['cap_width_mm']/2,-h,-h+1,'#161719')
        rect(-cap['cap_width_mm']/2,-cap['cap_width_mm']/2+1,-h+1,-h+dp,'#161719')
        rect(cap['cap_width_mm']/2-1,cap['cap_width_mm']/2,-h+1,-h+dp,'#161719')
        # Stems (approx)
        rect(-2.1,2.1,pt-10.2,pt-6.6,'#b4cace')
        o += [f'<path d="M {px(-18)} {py(0)} H {px(18)}" stroke="#f0f5f8" stroke-dasharray="6,4"/>',
              f'<text x="{ox+22}" y="405" fill="#c8d6e2" font-size="14" font-family="Arial">Stroke {tr:g} mm → plate guard {d["cap_skirt_to_plate_gap_at_full_press_mm"]:g} mm</text>']
    o.append('<text x="25" y="470" fill="#e9b57e" font-family="Arial" font-size="15">Cap body depth 8 mm, skirt and stem are illustrative. Actual cap depth, clip tabs, return and tolerance NOT proven.</text>')
    return '\n'.join(o+['</svg>'])+'\n'


def _validate_heights(spec):
    v=spec['heights_above_front_mm']
    if v != [2.,4.,6.]:
        raise ValueError('This curated comparison package is specifically 2, 4 and 6mm')
    if len(set(v))!=3:raise ValueError('Duplicate heights')


def generate(outdir, report_only=False):
    dim,ref,cfg=load(); base=assumptions(); spec=load_spec();_validate_heights(spec)
    variants=all_variant_reports(dim,ref,cfg,base,spec)
    outdir.mkdir(exist_ok=True,parents=True)
    summary={'physical_fit_verified':False,'case_type':'R5 rounded, USB on LEFT, Waveshare physically rotated 180 deg',
             'manufacture_ready':False,'mx_switch_travel_mm_assumed':base['switch_total_travel_nominal_mm'],
             'keycap_width_mm_assumed':base['cap_width_mm'],
             'well_width_mm':base['well_width_mm'],
             'heights':{f'{h:g}mm':row['report'] for h,row in variants.items()},
             'note':'Trial caps are not specific purchasable keycap CAD; inspect the three STEP assembly files in FreeCAD before selection.'}
    (outdir/'three_heights_report.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (outdir/'three_heights_front_comparison.svg').write_text(comparison_svg(dim,cfg,variants),encoding='utf-8')
    (outdir/'three_heights_section_comparison.svg').write_text(side_comparison_svg(base,variants),encoding='utf-8')
    for name in ('previous','play_pause','next'):
        (outdir/f'{name}_white_legend.svg').write_text(icon_svg(name),encoding='utf-8')
    for h,row in variants.items():
        label=f'{h:g}mm'
        folder=outdir/label
        folder.mkdir(exist_ok=True,parents=True)
        cap=row['cap'];data=row['report']
        (folder/'variant_settings.json').write_text(json.dumps(cap,indent=2)+'\n',encoding='utf-8')
        (folder/'fit_report.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        lay=layout_svg(dim,cfg,cap,data).replace('low-set media keys (CONCEPT)',f'{h:g}mm raised media keys (CONCEPT)').replace(' / 2mm proud at rest',f' / {h:g}mm proud at rest')
        (folder/f'media_controls_front_{label}.svg').write_text(lay,encoding='utf-8')
        (folder/f'mx_section_{label}.svg').write_text(section_svg(cap,data),encoding='utf-8')
        if not report_only:
            solid=cad_build(dim,ref,cfg,cap,folder)
            if not solid.isValid() or len(solid.Solids())!=1:
                raise ValueError(f'{h}mm exported shell not a single valid solid')
            print(f'  {label}: rounded B-Rep valid, vol={solid.Volume():.1f} mm3, plate W={cap["switch_plate_top_inward_mm"]:.1f}mm')
        else: print(f'  {label}: geometry JSON/SVG, plate W={cap["switch_plate_top_inward_mm"]:.1f}mm')
    print('Three height comparison: 2/4/6mm / nominal full press guard 1.5mm / MX stem engagement invariant.')
    print('Generated:',outdir)
    print('NOT FIT-VERIFIED: keycap and switch dimensions/real travel unknown, USB side opening and screen mounts provisional.')
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report-only',action='store_true')
    args=ap.parse_args()
    generate(args.out_dir,args.report_only)

if __name__=='__main__':main()
