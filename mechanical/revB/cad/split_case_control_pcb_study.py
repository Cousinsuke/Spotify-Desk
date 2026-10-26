#!/usr/bin/env python3
"""Independent Rev B-C split R5 front/rear shell and one L-shaped controls PCB trial.

Concept geometry only: NO clips, screen mounts, fasteners, wiring or print approval.
This source does not overwrite or import the hook-click V2 case/lid or vendor STEP.
--report-only uses stdlib; 3D STEP exports require CadQuery and Shapely.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
DIM=HERE/'dimensions.json'
SPEC=HERE/'split_case_control_pcb_parameters.json'


def study(dim,cfg):
    a=math.radians(dim['face_tilt_deg'])
    expected_depth=dim['front_face_length']*math.cos(a)+dim['rear_roof']
    expected_height=dim['front_chin']+dim['front_face_length']*math.sin(a)
    if abs(expected_depth-dim['depth'])>.01 or abs(expected_height-dim['height'])>.01:
        raise ValueError('Wedge exterior no longer matches Rev B dimensions')
    if (dim['width'],dim['rounding_external'],dim['face_tilt_deg'])!=(156.0,5.0,55.0):
        raise ValueError('Keep selected 156mm R5 55-degree appearance')
    if cfg['physical_rotation_deg']!=180 or cfg['keycap_rest_height_mm']!=4:
        raise ValueError('Must keep selected USB-left, 4mm resting caps')
    wall=float(cfg['wall_mm']); seam=float(cfg['seam_inward_w_mm']); gap=float(cfg['seam_gap_mm'])
    if not(2.5<=wall<=4 and 21<=seam<=27 and .2<=gap<=.8):
        raise ValueError('Trial seam or wall parameters outside considered range')
    wpcb=cfg['control_pcb_front_w_mm'];tpcb=cfg['control_pcb_thickness_mm']
    if wpcb<wall+3 or wpcb+tpcb>seam-gap/2-1:
        raise ValueError('PCB trial outside available front shell depth')
    points=cfg['control_pcb_outline_xv_mm']
    if len(points)<6 or not all(len(p)==2 and 5<=p[0]<=dim['width']-5 and
                                 5<=p[1]<=dim['front_face_length']-5 for p in points):
        raise ValueError('Bad L PCB outline')
    if dim['keys_x'] != [31.05,61.05,91.05] or dim['keys_v']!=91 or (dim['knob_x'],dim['knob_v'])!=(138,44):
        raise ValueError('User selected key row and encoder position changed')
    sx,sv=dim['screen_origin'];sw,sh=dim['screen_outer'];ox,ov=dim['display_visible_offset']
    vw,vh=dim['display_visible']
    window={'x':round(sx+sw-ox-vw,3),'v':round(sv+sh-ov-vh,3),'width':vw,'height':vh}
    return {
        'status':'REV BC PROVISIONAL SPLIT CASE/PCB GEOMETRY ONLY; NO PRINT OR FIT APPROVAL',
        'full_shell_extents_mm':{'width':dim['width'],'depth':round(dim['depth'],3),'height':round(dim['height'],3)},
        'outer_R_mm':dim['rounding_external'],'face_tilt_deg':dim['face_tilt_deg'],
        'wall_trial_mm':wall,'face_plane_seam_inward_w_mm':seam,
        'open_perimeter_seam_gap_mm':gap,'screen_orientation_deg':180,
        'screen_visible_window_xv_mm':window,'screen_nominal_mount_pitch_mm':dim['display_nominal_fixing_centers'],
        'screen_nominal_four_mount_targets_xv_mm':[[x,v] for x in (12.05,110.05) for v in (11.8,71.8)],
        'key_centers_xv_mm':[[x,dim['keys_v']] for x in dim['keys_x']],
        'keycap_rest_above_face_mm':4.0,'encoder_center_xv_mm':[dim['knob_x'],dim['knob_v']],
        'control_pcb_outline_xv_mm':points,'control_pcb_front_w_mm':wpcb,'control_pcb_thickness_mm':tpcb,
        'original_case_and_lid_modified':False,'bottom_hatch_in_new_variant':False,
        'screen_manufacturer_solids_included':False,'pcb_electronics_or_traces_included':False,
        'clips_or_screw_receivers_designed':False,'physical_print_approved':False,
        'warnings':[
            'Separate shell STEP shapes have an open perimeter seam with no structural locking mechanism.',
            'The actual Waveshare screen and mounting fasteners are not present: dimensions are targets, not installed bosses.',
            'The single L-shaped control PCB is UNPOPULATED: no traces, pads, holes, switch/encoder solder footprints or mounting.',
            'Mechanical switch plate, four-millimetre cap travel, encoder nut and contact geometry remain unresolved.',
            'No measured USB plug/I2C harness, 3.3V verification, radio antenna keepout or physical printer tolerances.'
        ],
    }


def face_plane(cq,dim):
    a=math.radians(dim['face_tilt_deg'])
    return cq.Plane(origin=(0,dim['front_face_length']*math.cos(a),dim['height']),
                    xDir=(1,0,0),normal=(0,math.sin(a),-math.cos(a)))


def make_geometry(dim,cfg):
    import cadquery as cq
    from shapely.geometry import Polygon
    info=study(dim,cfg)
    width=dim['width'];depth=dim['depth'];height=dim['height'];wall=cfg['wall_mm']
    face_len=dim['front_face_length'];run=depth-dim['rear_roof']
    outline=[(0,0),(depth,0),(depth,height),(run,height),(0,dim['front_chin'])]
    inner=Polygon(outline).buffer(-wall,join_style=2)
    if inner.is_empty:raise ValueError('No inset shell cavity')
    def yz_prism(poly,xlen,xoffset=0):
        return cq.Workplane('YZ').polyline(poly).close().extrude(xlen).translate((xoffset,0,0))
    whole=yz_prism(outline,width).edges().fillet(dim['rounding_external'])
    whole=whole.cut(yz_prism(list(inner.exterior.coords)[:-1],width-2*wall,wall))
    plane=face_plane(cq,dim)
    def rect(x0,x1,v0,v1,w0,w1):
        return (cq.Workplane(plane).transformed(offset=(0,0,w0))
                .center((x0+x1)/2,(v0+v1)/2).rect(x1-x0,v1-v0).extrude(w1-w0))
    win=info['screen_visible_window_xv_mm']
    whole=whole.cut(rect(win['x'],win['x']+win['width'],win['v'],win['v']+win['height'],-3,10))
    for x in dim['keys_x']:
        whole=whole.cut(rect(x-9.6,x+9.6,dim['keys_v']-9.6,dim['keys_v']+9.6,-3,10))
    whole=whole.cut(cq.Workplane(plane).transformed(offset=(0,0,-3))
                    .center(dim['knob_x'],dim['knob_v'])
                    .circle(cfg['encoder_trial_bore_mm']/2).extrude(13))
    # A preserved approximate rotated screen left power passage, NOT plug fit.
    whole=whole.cut(rect(*cfg['usb_c1_left_trial_local_xv_w_mm'])).val()
    seam=cfg['seam_inward_w_mm'];gap=cfg['seam_gap_mm']
    def face_halfspace(upto):
        return (cq.Workplane(plane).transformed(offset=(0,0,-180))
                .center(width/2,face_len/2).rect(600,600).extrude(180+upto).val())
    front=whole.intersect(face_halfspace(seam-gap/2))
    rear=whole.cut(face_halfspace(seam+gap/2))
    if any(not s.isValid() or len(s.Solids())!=1 for s in [front,rear]):
        raise ValueError('Front and rear must each form a connected valid B-Rep')
    if front.intersect(rear).Volume()>.001:raise ValueError('Two half-shells overlap')
    pcb=(cq.Workplane(plane).transformed(offset=(0,0,cfg['control_pcb_front_w_mm']))
         .polyline(cfg['control_pcb_outline_xv_mm']).close()
         .extrude(cfg['control_pcb_thickness_mm']).val())
    if not pcb.isValid() or len(pcb.Solids())!=1:raise ValueError('Trial control PCB invalid')
    overlap=front.intersect(pcb).Volume()+rear.intersect(pcb).Volume()
    info['cad']={
        'front_valid':True,'rear_valid':True,'control_pcb_valid':True,
        'front_rear_volumetric_overlap_mm3':round(front.intersect(rear).Volume(),5),
        'pcb_against_both_shells_overlap_mm3':round(overlap,5),
        'front_volume_mm3':round(front.Volume(),2),'rear_volume_mm3':round(rear.Volume(),2),
        'control_pcb_volume_mm3':round(pcb.Volume(),2)}
    return info,front,rear,pcb


def diagram_svg(dim,info):
    width=dim['width'];face_len=dim['front_face_length'];p=info['control_pcb_outline_xv_mm']
    polygon=' '.join(f'{x*3:.1f},{v*3:.1f}' for x,v in p)
    win=info['screen_visible_window_xv_mm']
    keys=''.join(f'<rect x="{(x-9)*3:.1f}" y="{(dim["keys_v"]-9)*3:.1f}" width="54" height="54" fill="#e8eef6"/>' for x in dim['keys_x'])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="475" viewBox="0 0 960 475">
<rect width="960" height="475" fill="#14202b"/><text x="28" y="38" font-family="Arial" font-size="21" fill="#f6fafc">Spotify Desk Rev B-C - proposed front controls carrier</text>
<text x="28" y="62" font-family="Arial" font-size="13" fill="#a9c0d1">Trial single L-shaped controls PCB. Original R5 exterior, LCD position, key row and encoder retained.</text>
<g transform="translate(60 95)"><rect x="0" y="0" width="{width*3:.1f}" height="{face_len*3:.1f}" rx="9" fill="#465a6b" stroke="#a9c1d2" stroke-width="3"/>
<path d="M {polygon} Z" fill="#5ea694" stroke="#b5f1d4" stroke-width="2"/>
<rect x="{win['x']*3:.1f}" y="{win['v']*3:.1f}" width="{win['width']*3:.1f}" height="{win['height']*3:.1f}" fill="#153f59" stroke="#95cee9" stroke-width="2"/>
{keys}<circle cx="{dim['knob_x']*3}" cy="{dim['knob_v']*3}" r="{dim['knob_d']*1.5}" fill="#141b23" stroke="#fff" stroke-width="2"/></g>
<text x="560" y="117" font-family="Arial" font-size="16" fill="#dbe7f0">Back shell is split at W={info['face_plane_seam_inward_w_mm']:.1f} mm</text>
<text x="560" y="143" font-family="Arial" font-size="15" fill="#c2d5e4">Seam gap: {info['open_perimeter_seam_gap_mm']:.1f} mm trial</text>
<text x="560" y="195" font-family="Arial" font-size="15" fill="#f5c89b">No structural screen mounts or snap clips yet.</text>
<text x="560" y="220" font-family="Arial" font-size="15" fill="#f5c89b">No PCB solder footprints / electrical circuit.</text>
<text x="560" y="245" font-family="Arial" font-size="15" fill="#f5c89b">Manufacturer STEP fit still pending.</text>
</svg>
'''


def generate(dim,cfg,outdir,report_only=False):
    import pathlib
    outdir=pathlib.Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    info=study(dim,cfg)
    (outdir/'split_case_control_pcb_concept.svg').write_text(diagram_svg(dim,info),encoding='utf-8')
    if not report_only:
        import cadquery as cq
        info,front,rear,pcb=make_geometry(dim,cfg)
        files={
          'front': 'SpotifyDesk_RevBC_FRONT_CARRIER_TRIAL.step',
          'rear': 'SpotifyDesk_RevBC_REAR_TUB_TRIAL.step',
          'pcb': 'SpotifyDesk_RevBC_CONTROL_PCB_OUTLINE_ONLY.step'}
        for name,shape in [('front',front),('rear',rear),('pcb',pcb)]:
            path=outdir/files[name]
            cq.exporters.export(shape,str(path))
            imported=cq.importers.importStep(str(path)).val()
            if not imported.isValid() or len(imported.Solids())!=1:
                raise ValueError(f'Invalid STEP round-trip: {name}')
        assy=cq.Assembly(name='SpotifyDesk_RevBC_SPLIT_CONCEPT_ONLY')
        assy.add(front,name='front_carrier_NO_MOUNTS',color=cq.Color(.2,.34,.43))
        assy.add(rear,name='rear_tub_NO_CATCH',color=cq.Color(.35,.42,.49))
        assy.add(pcb,name='controls_L_outline_UNPOPULATED',color=cq.Color(.20,.52,.41))
        assy.save(str(outdir/'SpotifyDesk_RevBC_REFERENCE_ASSEMBLY.step'))
        info['cad']['step_exports_verified']=True
    (outdir/'split_case_control_pcb_report.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    print('Rev BC provisional two-piece shell and L PCB: not print/fit approved. Output:',outdir)
    return info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dimensions',type=Path,default=DIM)
    p.add_argument('--parameters',type=Path,default=SPEC)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--report-only',action='store_true')
    args=p.parse_args()
    generate(json.loads(args.dimensions.read_text(encoding='utf-8')),
             json.loads(args.parameters.read_text(encoding='utf-8')),
             args.out_dir,args.report_only)

if __name__=='__main__':
    main()
