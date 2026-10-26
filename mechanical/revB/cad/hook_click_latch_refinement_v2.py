#!/usr/bin/env python3
"""Refine R5 4mm USB-left hook-and-click lid, retaining all earlier CAD unchanged.

Adds concave spring-root fillets, a top-side assembly cam (bottom locking
shoulder remains), and an underside thumb pad. Builds two printable *geometry*
test coupons of the actual latch and representative keeper. Elastic snap forces,
material fatigue and physical assembly remain unmeasured. --report-only stdlib.
"""
from __future__ import annotations
import argparse, json, tempfile, math
from pathlib import Path
import hook_click_cover_study as previous

HERE=Path(__file__).resolve().parent
SPEC=HERE/'hook_click_latch_refinement_v2.json'


def config(path=None):
    return json.loads(Path(path or SPEC).read_text(encoding='utf-8'))


def analyze(dim,ref,casecfg,baseline,refined):
    layout=previous.layout(dim,ref,casecfg,baseline)
    l=refined['latch']; arm=baseline['rear_latch']; nose=layout['rear_latch']
    radius=float(l['root_inside_fillet_mm']); relief=float(l['cam_y_retraction_at_top_mm'])
    shoulder=float(l['cam_full_ledge_below_z_mm']);top=float(l['cam_tip_top_z_mm'])
    L=arm['beam_free_x_mm']-arm['beam_root_x_mm'];t=arm['beam_depth_y_mm'];d=arm['nominal_rear_release_stroke_mm']
    if not (.3<=radius<=.75 and .5<relief<d and 1.6<=shoulder<=2.1 and shoulder<top-.2):
        raise ValueError('Unsuitable fillet/cam shoulder geometry')
    pad=l['finger_pad'];b=layout['cover_body'];nmin=nose['nose_x_min_mm'];nmax=nose['nose_x_max_mm']
    if not (pad['x_min']<arm['beam_free_x_mm']<pad['x_max']<arm['beam_free_x_mm']+5):
        raise ValueError('Thumb pad must overlap tip without joining case or lid island')
    if not (pad['y_min']<arm['beam_front_y_mm']+t<pad['y_max']<b['y_max']-.4):
        raise ValueError('Thumb pad must meet beam and remain inside lid hatch')
    if not (pad['z_min']==b['z_min'] and b['z_min']<pad['z_max']<b['z_max']):
        raise ValueError('Thumb pad must lie within cover thickness')
    # Beam-in-plane, small-deflection ideal uniform cantilever upper-order estimate
    strain_estimate=1.5*t*d/(L*L)
    y_outer=nose['nose_y_max_mm']; hole_rear=dim['depth']-baseline['hatch_inset_y_mm']
    if y_outer-relief>=hole_rear:
        raise ValueError('Leading upper cam tip would not clear the keeper in Y')
    return {'version':'v2 root relief + self-centering catch cam + thumb pad + two real-geometry coupons',
            'fabrication_approved':False,'physically_click_tested':False,
            'unchanged_case_and_screen_mounts':True,'lid_screws':0,'screen_screw_targets':4,
            'rounded_root_fillet_mm':radius,'ramped_nose_y_retraction_top_mm':relief,
            'cam_shoulder_bottom_z_mm':1.55,'cam_flat_shoulder_to_z_mm':shoulder,
            'cam_top_z_mm':top,'nose_outer_y_at_rest_mm':round(y_outer,3),
            'nose_top_leading_y_mm':round(y_outer-relief,3),
            'keeper_inner_edge_y_mm':round(hole_rear,3),
            'assumed_release_stroke_mm':d,'estimated_ideal_beam_surface_strain_percent':round(100*strain_estimate,3),
            'strain_is_approximate_not_fea':True,'finger_pad_bbox':pad,
            'coupon_is_only_local_latch_not_complete_hatch':True,
            'remaining_gates':refined['warnings']}


def box(cq,a):
    return previous.xy_box(cq,a['x_min'],a['x_max'],a['y_min'],a['y_max'],a['z_min'],a['z_max']).val()


def refine_lid(cq,old_lid,baseline,study,refined):
    """Refine exact predecessor lid, only local latch beam and underside grip.

    Fillet internal root corners in full Z. Cam relieves *upper* edge in Z
    (top enters first when installed upward); bottom remains square retention.
    """
    l=baseline['rear_latch'];r=refined['latch'];oldnose=study['rear_latch']
    # Root at x=beam_root+root_overlap, both flexure shoulder corners.
    x=l['beam_root_x_mm']+l['root_overlap_mm']
    candidates=[]
    for edge in old_lid.Edges():
        bb=edge.BoundingBox()
        if (abs(bb.xmin-x)<.015 and bb.zlen>baseline['cover']['thickness_mm']-.1
            and any(abs(bb.ymin-y)<.015 for y in (l['beam_front_y_mm'],l['beam_front_y_mm']+l['beam_depth_y_mm']))):
            candidates.append(edge)
    if len(candidates)!=2:
        raise ValueError(f'Expected two vertical internal root edges; got {len(candidates)}')
    rounded=cq.Workplane(obj=old_lid).newObject(candidates).fillet(r['root_inside_fillet_mm']).val()
    outer=oldnose['nose_y_max_mm'];xmin=oldnose['nose_x_min_mm'];xmax=oldnose['nose_x_max_mm']
    ztop=r['cam_tip_top_z_mm'];ledge=r['cam_full_ledge_below_z_mm']; retreat=r['cam_y_retraction_at_top_mm']
    # Cut small triangular wedge into TOP/outward nose so +Z cover closing
    # encounters a slope, while lower retaining surface stays square.
    chamfer=(cq.Workplane('YZ', origin=(xmin-.03,0,0))
              .polyline([(outer-retreat,ztop+.025),(outer+.08,ztop+.025),(outer+.08,ledge)])
              .close().extrude(xmax-xmin+.06).val())
    with_cam=rounded.cut(chamfer)
    pad=box(cq,r['finger_pad'])
    result=with_cam.fuse(pad)
    if not result.isValid() or len(result.Solids())!=1:raise ValueError('Revised lid is not one valid solid')
    if result.Volume()<=0:raise ValueError('Missing latch body')
    return result


def latch_coupon(cq, lid, case, dim,base,refined,study):
    """Cropped *exact* V2 latch beam and local keeper for small test printing.

    Fixture is cropped from ACTUAL case geometry (not a made-up rectangular
    locking wall); this confirms the coupon reproduces the same keeper geometry.
    """
    r=refined['latch'];lb=r['coupon_lid_bbox'];fb=r['coupon_frame_bbox']
    coupon_lid=lid.intersect(box(cq,lb))
    coupon_frame=case.intersect(box(cq,fb))
    if any(not s.isValid() or len(s.Solids())!=1 for s in (coupon_lid,coupon_frame)):
        raise ValueError('Latch or keeper crop is not a single solid')
    if coupon_lid.intersect(coupon_frame).Volume()>.005:
        raise ValueError('Coupon installed positions intersect')
    return coupon_lid,coupon_frame


def view_svg(report):
    a=report
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="510" viewBox="0 0 1100 510">
<rect width="1100" height="510" fill="#141b24"/>
<text x="35" y="39" font-family="Arial" font-size="23" fill="white">Rev B latch V2 — top cam, rounded spring root and thumb pad</text>
<text x="35" y="67" font-family="Arial" font-size="15" fill="#adc1d1">Conceptual cross-section; pressing underside lid upward (+Z) is NOT an elastic snap simulation</text>
<g transform="translate(62 140)">
<rect x="0" y="0" width="445" height="300" rx="10" fill="#263643" stroke="#536a7b"/>
<text x="16" y="31" fill="#fff" font-family="Arial" font-size="19">CAM + LOCKING SHOULDER</text>
<rect x="120" y="82" width="225" height="32" fill="#728a9e"/>
<rect x="304" y="114" width="41" height="89" fill="#728a9e"/>
<path d="M240 100 L292 135 L292 195 L240 195Z" fill="#e2aa63" stroke="#ffe0a6" stroke-width="2"/>
<path d="M240 131 L292 167" stroke="#fef4df" stroke-width="2.5"/>
<text x="22" y="236" fill="#dce6eb" font-family="Arial" font-size="16">Upper bevel guides closing</text>
<text x="22" y="258" fill="#dce6eb" font-family="Arial" font-size="16">Lower square edge retains lid</text>
</g>
<g transform="translate(560 140)">
<rect width="490" height="300" rx="10" fill="#263643" stroke="#536a7b"/>
<text x="17" y="31" fill="#fff" font-family="Arial" font-size="19">FLEX BEAM + TEST COUPON</text>
<rect x="45" y="105" width="60" height="80" rx="8" fill="#879eaf"/>
<path d="M105 145 L333 145" stroke="#e3b66a" stroke-width="21" stroke-linecap="round"/>
<rect x="322" y="124" width="50" height="42" rx="6" fill="#e3b66a"/>
<path d="M341 192 L341 171" stroke="#ffdf9e" stroke-width="3"/>
<text x="24" y="227" fill="#dce6eb" font-family="Arial" font-size="15">Root fillet: {a['rounded_root_fillet_mm']:.2f} mm</text>
<text x="24" y="250" fill="#dce6eb" font-family="Arial" font-size="15">Trial deflection: {a['assumed_release_stroke_mm']:.1f} mm</text>
<text x="24" y="273" fill="#f3c48c" font-family="Arial" font-size="13">Ideal beam strain ~{a['estimated_ideal_beam_surface_strain_percent']:.2f}% (not a rating)</text>
</g>
<text x="34" y="487" fill="#f0ad7c" font-family="Arial" font-size="15">No proof of click force, flex durability, printer tolerances or Waveshare installation. Print small coupon first.</text>
</svg>\n'''


def generate(outdir,report_only=False,parameters=None):
    dim,ref,casecfg=previous.load();baseline=previous.configuration()
    updated=config(parameters);analysis=analyze(dim,ref,casecfg,baseline,updated)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'hook_click_latch_v2_design.svg').write_text(view_svg(analysis),encoding='utf-8')
    stats={'status':'prototype, not fit certified','analysis':analysis,'cad':None}
    if not report_only:
        import cadquery as cq
        from cadquery import exporters,importers
        with tempfile.TemporaryDirectory(prefix='hook_v1_base_') as temp:
            previous.build_cad(dim,ref,casecfg,baseline,Path(temp))
            case=importers.importStep(str(Path(temp)/'spotify_R5_4mm_hook_click_CASE_trial.step')).val()
        dat=previous.layout(dim,ref,casecfg,baseline)
        lid=refine_lid(cq,previous.rounded_lid(cq,dat,baseline),baseline,dat,updated)
        if case.intersect(lid).Volume()>.005:raise ValueError('V2 case-lid resting collision')
        small_lid,small_frame=latch_coupon(cq,lid,case,dim,baseline,updated,dat)
        exports={'case':'SpotifyDesk_R5_hook_click_v2_CASE.step',
                 'lid':'SpotifyDesk_R5_hook_click_v2_LID.step',
                 'coupon_lid':'SpotifyDesk_latch_v2_test_LID.step',
                 'coupon_frame':'SpotifyDesk_latch_v2_test_FRAME.step'}
        for key,shape in [('case',case),('lid',lid),('coupon_lid',small_lid),('coupon_frame',small_frame)]:
            exporters.export(shape,str(outdir/exports[key]))
        # Two STL files of actual cropped geometry. Keep units millimetres.
        exporters.export(small_lid,str(outdir/'SpotifyDesk_latch_v2_test_LID.stl'),tolerance=.08,angularTolerance=.16)
        exporters.export(small_frame,str(outdir/'SpotifyDesk_latch_v2_test_FRAME.stl'),tolerance=.08,angularTolerance=.16)
        assembly=cq.Assembly(name='SpotifyDesk_R5_4mm_V2_hook_click')
        assembly.add(case,name='main_case_LCDFastenersUnchanged',color=cq.Color(.20,.25,.30))
        assembly.add(lid,name='improved_rear_latch_cover',color=cq.Color(.64,.48,.28))
        assembly.save(str(outdir/'SpotifyDesk_R5_hook_click_v2_ASSEMBLY.step'))
        exploded=cq.Assembly(name='SpotifyDesk_R5_4mm_V2_open')
        exploded.add(case,name='main_case_LCDFastenersUnchanged',color=cq.Color(.20,.25,.30))
        exploded.add(lid.translate((0,0,-14)),name='cover_removed',color=cq.Color(.64,.48,.28))
        exploded.save(str(outdir/'SpotifyDesk_R5_hook_click_v2_EXPLODED.step'))
        coupon=cq.Assembly(name='SpotifyDesk_exact_rear_latch_cropped_coupon')
        coupon.add(small_frame,name='actual_keeper_crop',color=cq.Color(.28,.36,.44))
        coupon.add(small_lid,name='actual_latch_crop',color=cq.Color(.87,.65,.36))
        coupon.save(str(outdir/'SpotifyDesk_latch_v2_test_ASSEMBLY.step'))
        for k in exports:
            reloaded=importers.importStep(str(outdir/exports[k])).val()
            if not reloaded.isValid() or len(reloaded.Solids())!=1:
                raise ValueError('STEP round-trip failed: '+k)
        if small_lid.translate((0,0,-.65)).intersect(small_frame).Volume()<.10:
            raise ValueError('Coupon does not show a retaining undercut under downward pull')
        stats['cad']={'valid_solids':4,'step_reimport_success':True,
             'closed_case_lid_intersection_mm3':round(case.intersect(lid).Volume(),6),
             'coupon_closed_overlap_mm3':round(small_lid.intersect(small_frame).Volume(),6),
             'coupon_downward_rigid_pull_interference_mm3':round(small_lid.translate((0,0,-.65)).intersect(small_frame).Volume(),4),
             'unchanged_case_volume_mm3':round(case.Volume(),3),'v2_lid_volume_mm3':round(lid.Volume(),3),
             'files':sorted([p.name for p in outdir.glob('*.step')]+[p.name for p in outdir.glob('*.stl')])}
    (outdir/'hook_click_latch_v2_report.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
    print('Rev B hook-and-click V2; test coupon is a cropped MATCHING LATCH + KEEPER')
    print('Fillet',analysis['rounded_root_fillet_mm'],'mm; cam retraction',analysis['ramped_nose_y_retraction_top_mm'],'mm')
    print('Ideal beam strain estimate',analysis['estimated_ideal_beam_surface_strain_percent'],'percent: NOT physical proof')
    print('Cover screws 0; LCD screw targets 4; original models unchanged')
    if stats['cad']:print('STEP solids verified:',stats['cad']['valid_solids'],'/ 4; closed clash=',stats['cad']['closed_case_lid_intersection_mm3'],'mm3')
    print('Output:',outdir)
    return stats


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',required=True,type=Path)
    p.add_argument('--report-only',action='store_true')
    p.add_argument('--parameters',type=Path)
    a=p.parse_args();generate(a.out_dir,a.report_only,a.parameters)
if __name__=='__main__':main()
