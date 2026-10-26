#!/usr/bin/env python3
"""Separate Rev B R5 USB-left 4mm screwless hook-and-click underside closure.

Front: two rigid tucked locating tongues. Rear: one integral, **trial**
side-bending printed latch beam whose nose engages a shallow case-side keeper
pocket. Four reference Waveshare screen screw mounts remain. No lid screws.

The 2023 board STEP/cable, flex endurance, FDM print settings and installation
through the underside hatch are NOT certified. --report-only uses Python stdlib.
CadQuery+Shapely are needed only to export the optional experimental STEP solids.
Never overwrites older cover/case CAD files.
"""
from __future__ import annotations
import argparse,json,math,tempfile
from pathlib import Path
from rotated_case_prototype import load
from rear_cover_screen_mount_study import report as old_mount_report,face_plane
from media_controls_fit_study import cad_build,assumptions
from media_controls_height_variants import variant,load_spec

HERE=Path(__file__).resolve().parent
SETTINGS=HERE/'hook_click_cover_parameters.json'


def configuration(path=None):
    return json.loads(Path(path or SETTINGS).read_text(encoding='utf-8'))


def layout(dim,ref,casecfg,cfg):
    if cfg['rotation_deg']!=180 or cfg['cap_rest_height_mm']!=4:
        raise ValueError('Use chosen R5 180deg USB-left 4mm key layout')
    if cfg['hatch_inset_x_mm']!=casecfg['bottom_access_nominal']['edge_x_mm'] or cfg['hatch_inset_y_mm']!=casecfg['bottom_access_nominal']['edge_y_mm']:
        raise ValueError('Cover shall use existing shell underside hole')
    gap=cfg['cover']['perimeter_gap_mm']; thickness=cfg['cover']['thickness_mm']; z=cfg['cover']['bottom_z_mm']
    w=dim['width'];depth=dim['depth'];x0=cfg['hatch_inset_x_mm'];y0=cfg['hatch_inset_y_mm'];cover=cfg['cover'];hooks=cfg['front_hooks'];catch=cfg['rear_latch']
    if not (.2 <=gap<=.6 and 1.5<=thickness<=3.0):raise ValueError('Unrealistic print/gap study')
    if not(cover['support_lip_z_min_mm']>=z+thickness+.2 and cover['support_lip_height_mm']>0):raise ValueError('Lid would intersect support lip')
    if len(hooks['x_centers_mm'])!=2 or not (35<hooks['x_centers_mm'][0]<70 and 90<hooks['x_centers_mm'][1]<120):raise ValueError('Use two separated fixed locating hooks')
    if hooks['tongue_z_bottom_mm']<z or hooks['tongue_z_top_mm']>=cover['support_lip_z_min_mm']:
        raise ValueError('Front hook z not within intended retention slot')
    if hooks['pocket_z_bottom_mm']>=hooks['tongue_z_bottom_mm'] or hooks['pocket_z_top_mm']<=hooks['tongue_z_top_mm']:
        raise ValueError('Hook pocket has inadequate z clearance')
    bw=catch['beam_free_x_mm']-catch['beam_root_x_mm'];beamdepth=catch['beam_depth_y_mm']
    if not(20<=bw<=32 and 1.4<=beamdepth<=3.2 and catch['nominal_rear_release_stroke_mm']>=1.4):raise ValueError('Bad latch flexure proportions')
    # Rear latch nose retracts from >case rear hole Y to inside the hole at stated travel.
    hole_rear=depth-y0
    rear_tab_max_y=hole_rear+catch['tongue_engagement_rear_mm']
    if rear_tab_max_y-catch['nominal_rear_release_stroke_mm']>=hole_rear-gap/2:
        raise ValueError('Release stroke too small to clear rear edge')
    coords={'x_min':x0+gap,'x_max':w-x0-gap,'y_min':y0+gap,'y_max':depth-y0-gap,'z_min':z,'z_max':z+thickness}
    hooklist=[{'center_x_mm':x,'x_min_mm':x-hooks['tongue_width_mm']/2,'x_max_mm':x+hooks['tongue_width_mm']/2,
        'y_min_mm':y0-hooks['tongue_front_projection_mm'],'y_max_mm':coords['y_min']+1.2,
        'z_min_mm':hooks['tongue_z_bottom_mm'],'z_max_mm':hooks['tongue_z_top_mm']} for x in hooks['x_centers_mm']]
    rear={'nose_x_min_mm':catch['notch_left_x_mm']+1.0,'nose_x_max_mm':catch['notch_right_x_mm']-1.0,
        'nose_y_max_mm':rear_tab_max_y,'pocket_y_min_mm':hole_rear-0.4,
        'pocket_y_max_mm':rear_tab_max_y+0.8,'pocket_z_min_mm':catch['rear_pocket_z_bottom_mm'],
        'pocket_z_max_mm':catch['rear_pocket_z_top_mm']}
    # Reuse original source-grounded display mounting layout, even though its lid gets redesigned.
    old=configuration_old_mount()
    screen=old_mount_report(dim,ref,casecfg,old)
    if len(screen['screen_standoff_centers_and_seats'])!=4 or screen['screen_standoff_pitch_mm']!=[98.,60.]:
        raise ValueError('Retained nominal 98x60 screen mounting pattern missing')
    return {'status':'EXPERIMENTAL HOOK + FLEX CATCH; NOT PRINT/FIT APPROVED',
      'cover_screw_count':0,'screen_mount_screw_count':4,'screen_mount_pitch_mm':screen['screen_standoff_pitch_mm'],
      'cover_body':coords,'front_hooks':hooklist,'rear_latch':rear,
      'release_stroke_trial_mm':catch['nominal_rear_release_stroke_mm'],
      'lid_volume_guess_mm3':round((coords['x_max']-coords['x_min'])*(coords['y_max']-coords['y_min'])*thickness,1),
      'frame_insertion_issue':'Underside aperture Y depth about 59mm; actual Waveshare 68.3mm module insertion and screw-tool reach still unresolved',
      'physical_fit_verified':False,'original_cad_preserved':True,'warnings':cfg['warnings']}


def configuration_old_mount():
    return json.loads((HERE/'rear_cover_screen_mount_study.json').read_text(encoding='utf-8'))


def xy_box(cq,x1,x2,y1,y2,z1,z2):
    if not (x2>x1 and y2>y1 and z2>z1):raise ValueError('Invalid box')
    return cq.Workplane('XY').box(x2-x1,y2-y1,z2-z1).translate(((x1+x2)/2,(y1+y2)/2,(z1+z2)/2))


def rounded_lid(cq,dat,cfg):
    b=dat['cover_body'];c=cfg['cover'];cx=(b['x_max']+b['x_min'])/2;cy=(b['y_max']+b['y_min'])/2
    out=(cq.Workplane('XY').workplane(offset=b['z_min']).center(cx,cy)
         .rect(b['x_max']-b['x_min'],b['y_max']-b['y_min']).extrude(c['thickness_mm'])
         .edges('|Z').fillet(c['corner_radius_mm']))
    # Make one deliberate U-shaped relief around an x-oriented spring: full
    # plate window first, then beam and rearmost nose joined back at its x-root.
    l=cfg['rear_latch'];front=l['beam_front_y_mm'];back=front+l['beam_depth_y_mm'];root=l['beam_root_x_mm'];free=l['beam_free_x_mm']
    clear=xy_box(cq,root+2,free+5,front-l['slot_gap_mm'],dat['cover_body']['y_max']+.3,b['z_min']-.1,b['z_max']+.15)
    out=out.cut(clear)
    beam=xy_box(cq,root,free,front,back,b['z_min'],b['z_max'])
    out=out.union(beam)
    # Compliant free end is joined to beam in XY; narrow rear-projecting nose
    # is lifted in Z so existing rear-wall material below forms a keeper shelf.
    # The arm can bend in the cover plane toward the FRONT to disengage.
    nose=dat['rear_latch'];xmin=nose['nose_x_min_mm'];xmax=nose['nose_x_max_mm']
    tip=xy_box(cq,xmin,xmax,back-.45,nose['nose_y_max_mm'],1.55,2.50)
    out=out.union(tip)
    # two protruding rigid leading tongues, connected to upper part of lid
    for h in dat['front_hooks']:
        out=out.union(xy_box(cq,h['x_min_mm'],h['x_max_mm'],h['y_min_mm'],h['y_max_mm'],h['z_min_mm'],h['z_max_mm']))
    return out.val()


def add_screen_brackets(cq,dim,ref,casecfg,shell):
    """Same four anchor beams/rings as documented 2026-10-23 model, lid boss-free."""
    old=configuration_old_mount()
    screen=old_mount_report(dim,ref,casecfg,old)
    b=old['screen_brackets'];plane=face_plane(dim)
    def local_rect(cx,cv,w0,w1,ww,ll):
        return cq.Workplane(plane).transformed(offset=(0,0,w0)).center(cx,cv).rect(ww,ll).extrude(w1-w0)
    def local_disk(cx,cv,w0,w1,diam):
        return cq.Workplane(plane).transformed(offset=(0,0,w0)).center(cx,cv).circle(diam/2).extrude(w1-w0)
    for row in screen['screen_standoff_centers_and_seats']:
        x,v,seat,rear,av=(row[k] for k in ('x','v','seat_front_w_mm','rear_w_mm','anchor_v_mm'))
        anchor=local_rect(x,av,b['anchor_front_w_mm'],seat+1,b['anchor_width_mm'],b['anchor_v_length_mm'])
        span=abs(v-av)+b['anchor_v_length_mm']/2
        beam=local_rect(x,(v+av)/2,seat,rear+b['anchor_to_flange_rear_extension_mm'],b['beam_width_mm'],span)
        pad=local_disk(x,v,seat,rear,b['flange_diameter_mm'])
        shell=shell.union(anchor).union(beam).union(pad)
        shell=shell.cut(local_disk(x,v,seat-.2,rear+b['anchor_to_flange_rear_extension_mm']+.2,b['fastener_diameter_mm']))
    return shell


def build_cad(dim,ref,casecfg,cfg,outdir):
    import cadquery as cq
    dat=layout(dim,ref,casecfg,cfg)
    cap=variant(assumptions(),load_spec(),4.0)
    with tempfile.TemporaryDirectory(prefix='r5_hook_4mm_base_') as temp:
        base=cad_build(dim,ref,casecfg,cap,Path(temp))
    shell=cq.Workplane(obj=base)
    shell=add_screen_brackets(cq,dim,ref,casecfg,shell)
    c=cfg['cover'];body=dat['cover_body'];lip=c['lip_inner_overlap_mm'];anch=c['lip_outer_anchor_mm']
    midx=dim['width']/2;midy=dim['depth']/2;x0=cfg['hatch_inset_x_mm'];y0=cfg['hatch_inset_y_mm']
    holew=dim['width']-2*x0;holed=dim['depth']-2*y0
    def rect(ww,dd,z0,z1):
        return (cq.Workplane('XY').workplane(offset=z0).center(midx,midy).rect(ww,dd).extrude(z1-z0))
    ring=rect(holew+2*anch,holed+2*anch,c['support_lip_z_min_mm'],c['support_lip_z_min_mm']+c['support_lip_height_mm'])
    inner=rect(holew-2*lip,holed-2*lip,c['support_lip_z_min_mm']-.2,c['support_lip_z_min_mm']+c['support_lip_height_mm']+.2)
    shell=shell.union(ring.cut(inner))
    # Hook pockets, retaining material as a roof ABOVE the receiving tongue.
    hooks=cfg['front_hooks']
    for h in dat['front_hooks']:
        half=hooks['pocket_width_extra_mm']/2
        pocket=xy_box(cq,h['x_min_mm']-half,h['x_max_mm']+half,
                      h['y_min_mm']-.35,body['y_min']+.2,
                      hooks['pocket_z_bottom_mm'],hooks['pocket_z_top_mm'])
        shell=shell.cut(pocket)
    rear=dat['rear_latch'];l=cfg['rear_latch']
    # A SHORT pocket in the rear frame, *not* the full-width feed slot of slider.
    # A low uncut wall below Z=1.35 acts as the catch keeper shelf.
    pocket=xy_box(cq,l['notch_left_x_mm'],l['notch_right_x_mm'],
        rear['pocket_y_min_mm'],rear['pocket_y_max_mm'],rear['pocket_z_min_mm'],rear['pocket_z_max_mm'])
    shell=shell.cut(pocket)
    lid=rounded_lid(cq,dat,cfg);solid=shell.val()
    if not solid.isValid() or len(solid.Solids())!=1:raise ValueError('Case with standoff mounts, lip and pockets must be one valid solid')
    if not lid.isValid() or len(lid.Solids())!=1:raise ValueError('Integral lid, front tongues and rear sprung beam must be one valid solid')
    overlap=solid.intersect(lid).Volume()
    if overlap>.005:raise ValueError(f'Case/lid intersect in closed position {overlap:.4f} mm^3')
    outdir.mkdir(parents=True,exist_ok=True)
    casepath=outdir/'spotify_R5_4mm_hook_click_CASE_trial.step';coverpath=outdir/'spotify_R5_4mm_hook_click_LID_trial.step'
    cq.exporters.export(solid,str(casepath));cq.exporters.export(lid,str(coverpath))
    asm=cq.Assembly(name='SpotifyDesk_R5_4mm_hook_click_closed')
    asm.add(solid,name='case_with_LCD_screw_mounts',color=cq.Color(.19,.24,.29))
    asm.add(lid,name='separate_hook_click_bottom_cover',color=cq.Color(.51,.59,.68))
    asm.save(str(outdir/'spotify_R5_4mm_hook_click_ASSEMBLED_trial.step'))
    exp=cq.Assembly(name='SpotifyDesk_R5_4mm_hook_click_open')
    exp.add(solid,name='case_with_LCD_screw_mounts',color=cq.Color(.19,.24,.29))
    exp.add(lid.translate((0,0,-14)),name='bottom_cover_removed_for_service',color=cq.Color(.51,.59,.68))
    exp.save(str(outdir/'spotify_R5_4mm_hook_click_REMOVED_trial.step'))
    from cadquery import importers
    loaded=[importers.importStep(str(x)).val() for x in [casepath,coverpath]]
    if any(not x.isValid() or len(x.Solids())!=1 for x in loaded):raise ValueError('STEP reopen geometry invalid')
    result={'cad_verified':True,'separate_valid_solids':2,'step_roundtrip':True,'closed_case_lid_intersection_mm3':round(overlap,6),
        'case_volume_mm3':round(solid.Volume(),3),'cover_volume_mm3':round(lid.Volume(),3),
        'case_width_mm':round(solid.BoundingBox().xlen,3),
        'files':[x.name for x in [casepath,coverpath]]+['spotify_R5_4mm_hook_click_ASSEMBLED_trial.step','spotify_R5_4mm_hook_click_REMOVED_trial.step'],
        'installation_sweep_not_physically_verified':True,'latch_released_geometry_not_certified':True}
    return result


def underside_svg(dim,d,c):
    scale=3.7;ox=62;oy=92;b=d['cover_body'];rear=d['rear_latch']
    points=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="555" viewBox="0 0 1050 555">',
    '<rect width="1050" height="555" fill="#101820"/>',
    '<text x="55" y="43" font-family="Arial" font-size="24" fill="#ecf2f5">Rounded Spotify Desk / hook-and-click underside cover</text>',
    '<text x="55" y="69" font-family="Arial" font-size="14" fill="#b9c7d3">Two green front locating tongues + one gold rear finger release; zero cover screws</text>',
    f'<rect x="{ox}" y="{oy}" width="{dim["width"]*scale:.2f}" height="{dim["depth"]*scale:.2f}" rx="16" fill="#3c4c5b" stroke="#acc0d1"/>',
    f'<rect x="{ox+b["x_min"]*scale:.2f}" y="{oy+b["y_min"]*scale:.2f}" width="{(b["x_max"]-b["x_min"])*scale:.2f}" height="{(b["y_max"]-b["y_min"])*scale:.2f}" rx="5" fill="#7e98af" stroke="#e8edf4"/>']
    for h in d['front_hooks']:
        points.append(f'<rect x="{ox+h["x_min_mm"]*scale:.2f}" y="{oy+h["y_min_mm"]*scale:.2f}" width="{(h["x_max_mm"]-h["x_min_mm"])*scale:.2f}" height="{(h["y_max_mm"]-h["y_min_mm"])*scale:.2f}" fill="#7dd4a7" stroke="white"/>')
    l=c['rear_latch'];p=rear
    points.extend([f'<rect x="{ox+l["beam_root_x_mm"]*scale:.2f}" y="{oy+l["beam_front_y_mm"]*scale:.2f}" width="{(l["beam_free_x_mm"]-l["beam_root_x_mm"])*scale:.2f}" height="{l["beam_depth_y_mm"]*scale:.2f}" fill="#efc072"/>',
    f'<rect x="{ox+p["nose_x_min_mm"]*scale:.2f}" y="{oy+(l["beam_front_y_mm"]+l["beam_depth_y_mm"])*scale:.2f}" width="{(p["nose_x_max_mm"]-p["nose_x_min_mm"])*scale:.2f}" height="{(p["nose_y_max_mm"]-l["beam_front_y_mm"]-l["beam_depth_y_mm"])*scale:.2f}" fill="#f3bf64"/>',
    '<text x="65" y="463" fill="#b4e5c6" font-family="Arial" font-size="17">FRONT → insert rigid tongues first</text>',
    '<text x="65" y="492" fill="#f2c68c" font-family="Arial" font-size="17">REAR → press to click; press latch toward FRONT to release</text>',
    '<text x="65" y="520" fill="#e2a676" font-family="Arial" font-size="13">Schematic geometry; elastically flexed latch travel and printed retention force unverified</text>','</svg>'])
    return '\n'.join(points)+'\n'


def latch_section_svg(dim,d,c):
    pts=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="500" viewBox="0 0 1050 500">',
    '<rect width="1050" height="500" fill="#121922"/>',
    '<text x="45" y="38" font-family="Arial" font-size="24" fill="#f5f8fb">Hook-and-click bottom panel: operating sequence</text>',
    '<text x="45" y="69" font-family="Arial" font-size="14" fill="#b7cad8">XY diagrams are schematic, NOT dimensioned bend-radius/force certification.</text>']
    for k,(label,sub) in enumerate([('1. LOCATE FRONT','Two rigid tongues slide under frame lip'),('2. CLICK REAR','Flexible in-plane arm bends and enters pocket'),('3. PRESS TO RELEASE','Push free tip toward FRONT, lift lid')]):
        x=45+k*335
        pts.extend([f'<rect x="{x}" y="100" width="315" height="285" rx="12" fill="#243240" stroke="#465a6a"/>',
        f'<text x="{x+16}" y="136" font-family="Arial" font-size="20" fill="#fafafa">{label}</text>',
        f'<text x="{x+16}" y="166" font-family="Arial" font-size="13" fill="#c7d2dc">{sub}</text>',
        f'<rect x="{x+43}" y="226" width="222" height="84" rx="4" fill="#718fa5" stroke="#e4edf4"/>'])
        if k==0:
            for cx in [x+87,x+218]:pts.append(f'<rect x="{cx}" y="205" width="22" height="29" fill="#8edbb2"/>')
            pts.append(f'<path d="M {x+155} 349 V 302" stroke="#8edbb2" stroke-width="4"/>')
        elif k==1:
            pts.extend([f'<rect x="{x+135}" y="299" width="52" height="26" fill="#f1b766"/>',f'<path d="M {x+161} 335 V 308" stroke="#f1b766" stroke-width="4"/>'])
        else:
            pts.extend([f'<rect x="{x+135}" y="299" width="52" height="26" fill="#f1b766"/>',f'<path d="M {x+164} 319 V 276" stroke="#f1b766" stroke-width="4"/>'])
    pts.extend(['<text x="47" y="437" fill="#d7e7f1" font-size="16" font-family="Arial">Four screen standoffs retain M2.5 reference screw holes; underside cover has NONE.</text>',
    '<text x="47" y="466" fill="#f0b37b" font-size="15" font-family="Arial">IMPORTANT: actual PETG flexure travel and mechanical click strength require a coupon print.</text>','</svg>'])
    return '\n'.join(pts)+'\n'


def generate(outdir,report_only=False,config=None):
    dim,ref,casecfg=load();cfg=configuration(config);data=layout(dim,ref,casecfg,cfg)
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'hook_click_underside_plan.svg').write_text(underside_svg(dim,data,cfg),encoding='utf-8')
    (outdir/'hook_click_operation.svg').write_text(latch_section_svg(dim,data,cfg),encoding='utf-8')
    cad=None
    if not report_only:cad=build_cad(dim,ref,casecfg,cfg,outdir)
    (outdir/'hook_click_design_report.json').write_text(json.dumps({'layout':data,'cad':cad},indent=2)+'\n',encoding='utf-8')
    print('Rev B R5 USB-left / 4mm keys: two rigid hook tongues and ONE rear flex release')
    print('Zero cover screws; four 98x60 nominal LCD screw mount positions retained.')
    print('Design status: latch bending and real screen insertion NOT VERIFIED')
    print('Generated:',outdir)
    return {'layout':data,'cad':cad}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',required=True,type=Path)
    p.add_argument('--report-only',action='store_true')
    p.add_argument('--config',type=Path)
    a=p.parse_args();generate(a.out_dir,a.report_only,a.config)
if __name__=='__main__':main()
