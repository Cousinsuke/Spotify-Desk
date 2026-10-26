#!/usr/bin/env python3
"""Waveshare screen insertion / fastener reach study for Rev B hook-click V2.

Two modes:
--report-only: Python standard library, 2023 manufacturer STEP-extracted boxes.
--case-step EXISTING_CASE.step: OPTIONAL CadQuery checks using exact V2 CASE geometry
against conservative board/component BBOX proxies and sampled insertion poses;
writes reference STEP assemblies. Never silently claims a valid path or revises CAD.

World frame: X across front; desk Y front to rear; Z upward.
Display local: X right, V down slope, W inward normal. Actual main board flipped
180 degrees in the FRONT plane; touch glass faces outwards throughout.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from rotated_case_prototype import load
from orientation_180_study import rotated_parts
from rear_cover_screen_mount_study import report as brackets_report,load_specification

HERE=Path(__file__).resolve().parent
SPEC=HERE/'screen_install_study_parameters.json'


def settings(path=None):
    return json.loads(Path(path or SPEC).read_text(encoding='utf-8'))


def local_to_world(dim,x,v,w):
    a=math.radians(dim['face_tilt_deg'])
    return (x, dim['front_face_length']*math.cos(a)-v*math.cos(a)+w*math.sin(a),
            dim['height']-v*math.sin(a)-w*math.cos(a))


def expanded_box_corners_world(dim,part,glass_w):
    a,b=part.minimum,part.maximum
    return [local_to_world(dim,x,v,w+glass_w)
            for x in [a[0],b[0]] for v in [a[1],b[1]] for w in [a[2],b[2]]]


def bounds(points,axis):
    return (min(row[axis] for row in points),max(row[axis] for row in points))


def proxy_footprint(dim,ref,cfg):
    if cfg['rotation_deg']!=180 or not 0 <= cfg['trial_glass_recess_inward_w_mm'] <= 10:
        raise ValueError('Study only supports the selected 180-degree glass-front orientation')
    box=rotated_parts(dim,ref,180)['full_assembly'];corners=expanded_box_corners_world(dim,box,cfg['trial_glass_recess_inward_w_mm'])
    x0,x1=bounds(corners,0);y0,y1=bounds(corners,1);z0,z1=bounds(corners,2)
    hatch=cfg_read_hatch(dim)
    w=hatch['x_max']-hatch['x_min'];d=hatch['y_max']-hatch['y_min'];bw=x1-x0;by=y1-y0
    # A projected bounding footprint can be shifted within the entry; this
    # demonstrates ONLY a necessary projection test, not a rigid 3D path.
    need_reposition_back=max(0.0,y1-hatch['y_max']);need_reposition_front=max(0.0,hatch['y_min']-y0)
    min_shift=hatch['y_min']-y0;max_shift=hatch['y_max']-y1
    if min_shift>max_shift and by<=d+1e-8:raise ValueError('Inconsistent footprint shift algebra')
    return {'board_source':'2023 Waveshare STEP extracted full-assembly 3D bounds (conservative rectangular prism)',
            'local_bbox_x_v_w_mm':{'min':list(box.minimum),'max':list(box.maximum)},
            'projected_x_minmax_mm':[round(x0,3),round(x1,3)],
            'projected_desk_y_minmax_mm':[round(y0,3),round(y1,3)],
            'world_z_minmax_mm':[round(z0,3),round(z1,3)],
            'projected_desk_y_depth_mm':round(by,3),
            'hatch':hatch, 'hatch_desk_y_depth_mm':round(d,3),
            'hatch_x_width_mm':round(w,3),
            'projection_desk_y_slack_mm':round(d-by,3),
            'projection_x_slack_mm':round(w-bw,3),
            'registered_nominal_y_rear_overhang_mm':round(need_reposition_back,3),
            'staging_y_translation_range_for_bbox_mm':[round(min_shift,3),round(max_shift,3)],
            'straight_z_projection_at_final_alignment_entirely_in_hatch':bool(y0>=hatch['y_min'] and y1<=hatch['y_max'] and x0>=hatch['x_min'] and x1<=hatch['x_max']),
            'projected_bounding_footprint_fits_after_y_shift':bool(bw<=w and by<=d),
            'projection_not_swept_collision_proof':True}


def cfg_read_hatch(dim):
    old=load_specification(); h=old['rear_opening']
    return {'x_min':h['x_edge_mm'],'x_max':dim['width']-h['x_edge_mm'],
            'y_min':h['y_edge_mm'],'y_max':dim['depth']-h['y_edge_mm']}


def screw_axes(dim,ref,casecfg,cfg):
    old=load_specification();b=brackets_report(dim,ref,casecfg,old)
    rows=b['screen_standoff_centers_and_seats'];radius=cfg['tool_shank_radius_mm']
    if len(rows)!=4 or b['screen_standoff_pitch_mm']!=[98.,60.]:raise ValueError('Mounting patterns differ from 2023 model')
    if not (1.0<=radius<=4.0):raise ValueError('Tool proxy radius outside study range')
    positions=[]
    for row in rows:
        x,v,w=(row[k] for k in ('x','v','rear_w_mm'))
        wp=local_to_world(dim,x,v,w+0.25)
        positions.append({'name':row['name'],'x_mm':x,'v_mm':v,
                          'flange_rear_w_mm':w,'tool_start_xyz_mm':[round(a,3) for a in wp],
                          'tool_axis':'positive local W (toward inside/back of case)',
                          'fastener_thread_and_driver_unverified':True})
    return positions


def report(dim,ref,casecfg,cfg):
    fp=proxy_footprint(dim,ref,cfg)
    result={'status':'SCREEN INSTALLATION STUDY ONLY; NO COMPLETE INSERTION OR SCREW ACCESS VERIFIED',
       'physically_tested':False,'case_modified':False,'case_includes_latch_v2_unchanged':True,
       'screen_mount_screw_targets':4,'cover_screws':0,
       'board_projection':fp,'screw_axes':screw_axes(dim,ref,casecfg,cfg),
       'trial_glass_recess_inward_w_mm':cfg['trial_glass_recess_inward_w_mm'],
       'warnings':cfg['warnings']}
    if not fp['projected_bounding_footprint_fits_after_y_shift']:
        result['projection_screening']='FAIL: board proxy footprint exceeds opening for any simple vertical approach at fixed orientation'
    elif not fp['straight_z_projection_at_final_alignment_entirely_in_hatch']:
        result['projection_screening']='SOME STAGING POSSIBLE BY FOOTPRINT: nominal seated XY footprint overhangs aperture; a lateral shift/tilt likely required. 3D sweeps needed.'
    else:result['projection_screening']='PROJECTION FITS: still not proof of unobstructed 3D insertion'
    return result


def face_plane(dim):
    import cadquery as cq
    a=math.radians(dim['face_tilt_deg'])
    return cq.Plane(origin=(0,dim['front_face_length']*math.cos(a),dim['height']),xDir=(1,0,0),normal=(0,math.sin(a),-math.cos(a)))


def part_box_cad(dim,part,glass_w):
    import cadquery as cq
    a,b=part.minimum,part.maximum
    return (cq.Workplane(face_plane(dim)).transformed(offset=(0,0,a[2]+glass_w))
            .center((a[0]+b[0])/2,(a[1]+b[1])/2)
            .rect(b[0]-a[0],b[1]-a[1]).extrude(b[2]-a[2]).val())


def screw_tool_cad(dim,row,length,radius):
    import cadquery as cq
    return (cq.Workplane(face_plane(dim)).transformed(offset=(0,0,row['flange_rear_w_mm']+0.25))
            .center(row['x_mm'],row['v_mm']).circle(radius).extrude(length).val())


def clearance_sweep(dim,ref,casecfg,cfg,case_step,outdir):
    import cadquery as cq
    if not Path(case_step).is_file():raise FileNotFoundError(case_step)
    case=cq.importers.importStep(str(case_step)).val()
    if not case.isValid() or len(case.Solids())!=1:raise ValueError('Source case must be a single valid solid')
    p=rotated_parts(dim,ref,180);glass_w=cfg['trial_glass_recess_inward_w_mm']
    board=part_box_cad(dim,p['full_assembly'],glass_w)
    glass=part_box_cad(dim,p['touch_glass'],glass_w)
    cen=board.Center(); sweep=[]
    tilts=cfg['sampled_tilt_angles_about_global_x_deg']; staging=cfg['vertical_staging_offsets_z_mm']
    if 0. not in tilts or 0. not in staging:raise ValueError('Must include nominal un-tilted final position')
    if len(tilts)>8 or len(staging)>40:raise ValueError('Too many slow CAD sweep samples')
    for angle in tilts:
        for dz in staging:
            axis=(cen.x+1,cen.y,cen.z)
            q=board.rotate((cen.x,cen.y,cen.z),axis,angle).translate((0,0,dz))
            g=glass.rotate((cen.x,cen.y,cen.z),axis,angle).translate((0,0,dz))
            overlap=float(case.intersect(q).Volume())
            go=float(case.intersect(g).Volume())
            sweep.append({'tilt_degrees':angle,'z_staging_mm':dz,
                          'full_assembly_bbox_case_overlap_mm3':round(overlap,2),
                          'touch_glass_bbox_case_overlap_mm3':round(go,2),
                          'case_clash_conservative_proxy':overlap>0.1})
    tool=[]
    for row in screw_axes(dim,ref,casecfg,cfg):
        for length in cfg['tool_lengths_mm']:
            solid=screw_tool_cad(dim,row,length,cfg['tool_shank_radius_mm'])
            tool.append({'standoff':row['name'],'shaft_radius_mm':cfg['tool_shank_radius_mm'],
              'length_mm':length,'case_intersection_mm3':round(case.intersect(solid).Volume(),2)})
    outdir.mkdir(exist_ok=True,parents=True)
    assy=cq.Assembly(name='Waveshare2023_FullAssemblyBBox_vs_Unchanged_R5_case')
    assy.add(case,name='unmodified_latch_v2_case',color=cq.Color(.2,.27,.34))
    assy.add(board,name='conservative_full_step_3d_bbox_nominal_seated',color=cq.Color(.25,.58,.78))
    assy.add(glass,name='conservative_touch_glass_bbox_nominal_seated',color=cq.Color(.45,.8,.75))
    assy.save(str(outdir/'Waveshare_Screen_Installation_BBox_Reference_ASSEMBLY.step'))
    exploded=cq.Assembly(name='Screen_Installation_UNVERIFIED_Staging_Reference')
    exploded.add(case,name='unmodified_hook_click_case',color=cq.Color(.2,.27,.34))
    exploded.add(board.translate((0,0,-60)),name='board_full_bbox_staged_60mm_below',color=cq.Color(.22,.61,.80))
    exploded.save(str(outdir/'Waveshare_Screen_BBox_Staged_Below_ASSEMBLY.step'))
    return {'basis':'REAL CASE STEP + conservative Waveshare manufacturer source EXTRACTED BOUNDING BOXES; not 693 STEP solid clearance',
      'case_valid':True,'case_volume_mm3':round(case.Volume(),3),'full_bbox_volume_mm3':round(board.Volume(),3),
      'sweep':sweep,'driver_shaft_samples':tool,
      'nominal_unrotated_bbox_case_intersection_mm3':next(x['full_assembly_bbox_case_overlap_mm3'] for x in sweep if x['tilt_degrees']==0 and x['z_staging_mm']==0),
      'nominal_unrotated_touch_glass_bbox_case_intersection_mm3':next(x['touch_glass_bbox_case_overlap_mm3'] for x in sweep if x['tilt_degrees']==0 and x['z_staging_mm']==0),
      'full_manufacturer_solid_intersection_not_run':True,
      'no_collision_free_continuous_route_certified':True}


def drawings(dim,r):
    b=r['board_projection'];h=b['hatch']; ymin,ymax=b['projected_desk_y_minmax_mm'];
    x0=90;xscale=9;z0=115
    def ty(y):return x0+xscale*y
    w='1100'; H='470'
    v=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 1100 470">',
      '<rect width="1100" height="470" fill="#121a24"/>',
      '<text x="45" y="47" font-family="Arial" fill="#f0f5fc" font-size="24">Rev B Waveshare installation: bottom hatch DESK-Y projection</text>',
      '<text x="45" y="71" font-family="Arial" fill="#a7becf" font-size="15">Manufacturer 2023 full assembly bounding prism / physical 180-degree board flip / trial W=3.25mm</text>',
      '<text x="45" y="111" font-family="Arial" fill="#e7e8ec" font-size="18">Rear toward right →       (X width is 106.1mm, inside 134mm opening)</text>',
      f'<rect x="{ty(0)}" y="166" width="{dim["depth"]*xscale}" height="142" rx="8" fill="#313c4b" stroke="#91a4b9"/>',
      f'<rect x="{ty(h["y_min"])}" y="167" width="{(h["y_max"]-h["y_min"])*xscale}" height="140" fill="#0c1824" stroke="#8fb8cb" stroke-width="3"/>',
      f'<rect x="{ty(ymin)}" y="206" width="{(ymax-ymin)*xscale}" height="59" fill="#d58c49" fill-opacity=".85" stroke="#ffca81" stroke-width="2"/>',
      f'<text x="{ty(ymin)+13}" y="242" fill="#111820" font-family="Arial" font-size="14">Projected full module: {b["projected_desk_y_depth_mm"]:.2f}mm</text>',
      f'<path d="M {ty(h["y_max"]):.1f} 151 V 320" stroke="#96d5ec" stroke-dasharray="6 5"/>',
      f'<text x="{ty(h["y_max"])+10:.1f}" y="153" font-size="14" fill="#b9e8f6">Hatch rear boundary</text>',
      f'<text x="{ty(ymin):.1f}" y="330" font-size="14" fill="#e8b46e">Board face projection</text>',
      f'<text x="{ty(h["y_min"]):.1f}" y="357" font-size="14" fill="#9fe1f9">Hatch 59.09mm</text>',
      f'<text x="45" y="410" font-size="17" fill="#f0bd88" font-family="Arial">Nominal board extends {b["registered_nominal_y_rear_overhang_mm"]:.2f}mm past rear hatch edge; it could fit in projection after shifting forward, not a solved 3D path.</text>',
      '<text x="45" y="440" fill="#b4c9dc" font-size="14" font-family="Arial">NOTE: projected footprint is necessary but NOT sufficient. 3D case/screen support and screwdriver clashes evaluated separately.</text>', '</svg>']
    return '\n'.join(v)+'\n'



def side_section_svg(dim,result):
    """Desk Y/Z side cross-section showing full bbox vs case and screw reach."""
    fp=result['board_projection']
    full=rotated_parts(dim,load()[1],180)['full_assembly']
    glass=rotated_parts(dim,load()[1],180)['touch_glass']
    inset=result['trial_glass_recess_inward_w_mm']
    side_w=1100;side_h=690
    scale=4.4;Y0=160;Z0=590
    def px(y):return Y0+scale*y
    def py(z):return Z0-scale*z
    def pairs(box):
        return [(y,z) for _,y,z in expanded_box_corners_world(dim,box,inset)]
    def hull(pts):
        pts=sorted(set(pts))
        if len(pts)<=2:return pts
        def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lower=[]
        for point in pts:
            while len(lower)>=2 and cross(lower[-2],lower[-1],point)<=0:lower.pop()
            lower.append(point)
        upper=[]
        for point in pts[::-1]:
            while len(upper)>=2 and cross(upper[-2],upper[-1],point)<=0:upper.pop()
            upper.append(point)
        return lower[:-1]+upper[:-1]
    def polygon(seq):return ' '.join(f'{px(y):.1f},{py(z):.1f}' for y,z in seq)
    face_top=dim['front_face_length']*math.cos(math.radians(dim['face_tilt_deg']))
    h=fp['hatch'];rear=dim['depth'];top=dim['height']
    side=[(0,0),(0,dim['front_chin']),(face_top,top),(rear,top),(rear,0),(h['y_max'],0),(h['y_max'],8),(h['y_min'],8),(h['y_min'],0)]
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{side_w}" height="{side_h}" viewBox="0 0 {side_w} {side_h}">',
      '<rect width="1100" height="690" fill="#121a24"/>',
      '<text x="36" y="46" font-family="Arial" font-size="24" fill="#f0f5fb">Screen / enclosure Y–Z reference section (side view)</text>',
      '<text x="36" y="71" font-family="Arial" font-size="15" fill="#adbfcc">R5 shell silhouette = conceptual cross-section; 2023 Waveshare bounding rectangles (not real PCB geometry)</text>',
      f'<polygon points="{polygon(side)}" fill="#343f4c" stroke="#93aabc" stroke-width="3"/>',
      f'<polygon points="{polygon(hull(pairs(full)))}" fill="#f1aa60" fill-opacity="0.25" stroke="#f7b36c" stroke-width="2.5"/>',
      f'<polygon points="{polygon(hull(pairs(glass)))}" fill="#9be3d9" fill-opacity="0.30" stroke="#95f4df" stroke-width="2"/>',
      f'<path d="M {px(h["y_min"]):.1f} {py(8):.1f} V {py(-4):.1f} M {px(h["y_max"]):.1f} {py(8):.1f} V {py(-4):.1f}" stroke="#a9dbf1" stroke-width="2" stroke-dasharray="6 4"/>',
      f'<text x="{px(12)+15:.1f}" y="{py(4):.1f}" font-family="Arial" font-size="11" fill="#b3e0f4">Underside access (lid removed)</text>',
      '<text x="590" y="182" font-family="Arial" font-size="16" fill="#f0be81">Orange: FULL 3D envelope projected onto Y/Z</text>',
      '<text x="590" y="208" font-family="Arial" font-size="16" fill="#a3e9dd">Green: touch-glass envelope</text>',
      '<text x="590" y="244" font-family="Arial" font-size="15" fill="#d6e6ee">Screw shafts: simple straight W-axis probes</text>']
    for row in result['screw_axes']:
        _,v,w=row['x_mm'],row['v_mm'],row['flange_rear_w_mm']
        _,y0,z0=local_to_world(dim,0,v,w+0.25)
        _,y1,z1=local_to_world(dim,0,v,w+40.25)
        o.append(f'<path d="M {px(y0):.2f} {py(z0):.2f} L {px(y1):.2f} {py(z1):.2f}" stroke="#ff7790" stroke-width="2" stroke-dasharray="5 4"/>')
    o.extend(['<text x="590" y="278" font-family="Arial" font-size="14" fill="#ff9bad">Red dashed = trial straight screwdriver axis, not verified access</text>',
      '<text x="36" y="645" fill="#f7c08d" font-family="Arial" font-size="15">Bounds overlap in this projection and case-solid probe warns of material clashes. NO complete insertion path proven.</text>',
      '<text x="36" y="670" fill="#b0bfca" font-family="Arial" font-size="13">Section is an illustrative Y/Z union silhouette, not a manufacturing cross-section or accurate threaded screw drawing.</text>', '</svg>'])
    return '\n'.join(o)+'\n'


def generate(outdir,report_only=False,case_step=None):
    dim,ref,casecfg=load();cfg=settings()
    r=report(dim,ref,casecfg,cfg)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    r['sampled_3d_screening_performed']=False
    if case_step is not None and not report_only:
        r['cad_screening']=clearance_sweep(dim,ref,casecfg,cfg,case_step,outdir)
        r['sampled_3d_screening_performed']=True
    (outdir/'screen_installation_2023_reference_report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    (outdir/'waveshare_underside_projection.svg').write_text(drawings(dim,r),encoding='utf-8')
    (outdir/'waveshare_installation_side_section.svg').write_text(side_section_svg(dim,r),encoding='utf-8')
    b=r['board_projection']
    print(f"2023 Waveshare full bounding prism: {b['projected_desk_y_depth_mm']:.2f}mm desk Y / hatch {b['hatch_desk_y_depth_mm']:.2f}mm; projection slack {b['projection_desk_y_slack_mm']:.2f}mm")
    print(f"Nominal rear footprint overhang vs hatch: {b['registered_nominal_y_rear_overhang_mm']:.2f}mm; shift range Y={b['staging_y_translation_range_for_bbox_mm']}")
    print('Screen screws: 4 M2.5 trial targets, 98x60mm; board installed W datum and driver model unverified.')
    if r['sampled_3d_screening_performed']:
        c=r['cad_screening'];print('CONSERVATIVE full-board proxy at seated pose vs original case:',c['nominal_unrotated_bbox_case_intersection_mm3'],'mm3');print('Touch glass proxy seated clash:',c['nominal_unrotated_touch_glass_bbox_case_intersection_mm3'],'mm3')
        for row in c['driver_shaft_samples']:
            if row['length_mm']==40:print('Screw tool shaft 40mm probe:',row)
    else:print('3D sample tests skipped (report-only); case STEP not imported.')
    print('NO CERTIFIED INSERTION ROUTE: a small projected envelope does not prove 3D clearance or screw-driver reach.')
    print('Wrote:',outdir)
    return r


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',required=True,type=Path)
    ap.add_argument('--report-only',action='store_true')
    ap.add_argument('--case-step',type=Path,help='Optional unchanged previous hook-click V2 CASE STEP for sampled B-Rep collision study')
    args=ap.parse_args();generate(args.out_dir,args.report_only,args.case_step)

if __name__=='__main__':main()
