#!/usr/bin/env python3
"""Rev B assembly-screening: staged/tilted screen entry and pre-attachable carrier bars.

No stock shell or V2 hook-click lid changes. 2023 Waveshare manufacturer AABBs
are conservative proxies: no actual installed module, screws or mating cables.
--report-only needs stdlib; --case-step enables sampled CadQuery checks and
reference STEP solids. All new bracket solids are OPTION ONLY, not installed.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from rotated_case_prototype import load
from orientation_180_study import rotated_parts
from screen_install_path_study import (report as old_report, local_to_world,
    part_box_cad,face_plane,expanded_box_corners_world)
from rear_cover_screen_mount_study import report as mounts_report,load_specification

HERE=Path(__file__).resolve().parent
SPEC=HERE/'screen_install_bracket_options.json'

def cfg(path=None):return json.loads(Path(path or SPEC).read_text(encoding='utf-8'))

def describe(dims,ref,casecfg,options):
    if options['rotation_deg']!=180 or options['rest_keycap_mm']!=4.0:
        raise ValueError('Only selected R5, flipped physical board and 4mm key case')
    old=old_report(dims,ref,casecfg,options['legacy_screen_install_settings'])
    p=old['board_projection']; mounts=mounts_report(dims,ref,casecfg,load_specification())
    pts=mounts['screen_standoff_centers_and_seats']
    xs=sorted(set(round(r['x'],3) for r in pts));vs=sorted(set(round(r['v'],3) for r in pts))
    if len(xs)!=2 or len(vs)!=2 or round(xs[1]-xs[0],2)!=98.0 or round(vs[1]-vs[0],2)!=60.0:
        raise ValueError('Manufacturer mounting geometry unexpected')
    rail=options['preassembled_carrier']; test=options['entry_samples'];access=options['access_screw_trial']
    if not (7 <= rail['bar_width_x_mm'] <=10 and 62 <= rail['length_v_mm'] <=68):raise ValueError('bad rail dimensions')
    if not (2 <= rail['bar_thickness_w_mm']<=4 and rail['board_hole_diameter_mm']>=2.5):raise ValueError('bad bar/hole dimensions')
    if options['trial_rear_glass_w_mm']!=3.25:raise ValueError('Changed unverified screen datum unexpectedly')
    if len(test['temporary_y_shifts_mm'])>8 or len(test['temporary_tilt_deg'])>8 or len(test['approach_z_offsets_mm'])>15:raise ValueError('Excessive CAD samples')
    if sorted(set(test['temporary_y_shifts_mm']))!=test['temporary_y_shifts_mm']:raise ValueError('shifts must sort')
    if 0 not in test['temporary_y_shifts_mm'] or 0 not in test['temporary_tilt_deg'] or 0 not in test['approach_z_offsets_mm']:raise ValueError('include zero pose')
    if not 3<=access['shaft_diameter_mm']<=6 or not 10<=access['tool_length_mm']<=100:raise ValueError('tool trial invalid')
    fit_range=p['staging_y_translation_range_for_bbox_mm'];yp=rail['ear_v_mm']
    # Approx bracket accessory added behind module; may exceed empty 2D hatch margin.
    seats=[]
    for x in xs:
        row=[r for r in pts if round(r['x'],3)==x]
        seats.append({'bar_x_mm':x,'board_v_holes_mm':sorted(round(r['v'],3) for r in row),
          'back_seat_start_w_mm':round(min(r['seat_front_w_mm'] for r in row),3),
          'bar_width_x_mm':rail['bar_width_x_mm'],
          'ear_x_mm':round(x+rail['ear_inset_x_mm']*(1 if x<dims['width']/2 else -1),3),
          'ear_v_mm':yp})
    if abs(seats[0]['bar_x_mm']-12.05)>0.01 or abs(seats[1]['bar_x_mm']-110.05)>0.01:raise ValueError('Unexpected standoff X positions')
    return {'status':'SCREEN ENTRY + BRACKET DESIGN OPTIONS ONLY: NO VERIFIED PHYSICAL INSTALLATION',
      'case_modified':False,'hook_click_v2_cover_modified':False,'screen_screws_retained':4,'lid_screws':0,
      'source_reference':'2023 Waveshare full assembly extracted BOUNDING PRISM, not real 693-body collision mesh',
      'physical_rotation_deg':180,'screen_module_x_mm':106.106,'board_projection_desk_y_mm':p['projected_desk_y_depth_mm'],
      'hatch_opening_y_mm':p['hatch_desk_y_depth_mm'],
      'seated_y_footprint_mm':p['projected_desk_y_minmax_mm'],
      'screen_mount_centres_x_mm':xs,'screen_mount_centres_v_mm':vs,
      'projected_y_stage_translation_range_mm':fit_range,
      'staged_y_range_is_2d_only':True,
      'trial_preassembled_sidebars':seats,
      'bracket_bars_without_case_mating_structure':True,
      'two_vertical_underbody_screw_positions_tried':True,
      'case_needs_new_underside_accessible_screw_bosses_for_carrier':True,
      'warnings':options['warnings']}


def geometry_svg(dims,data,options):
    p=[]; xs,vs=data['screen_mount_centres_x_mm'],data['screen_mount_centres_v_mm'];s=4.0
    px=lambda x:60+x*s
    py=lambda v:95+v*s
    p.extend(['<svg xmlns="http://www.w3.org/2000/svg" width="1150" height="645" viewBox="0 0 1150 645">',
      '<rect width="1150" height="645" fill="#0d131c"/>',
      '<text x="42" y="37" fill="#f5f7fb" font-family="Arial" font-size="24">Waveshare carrier-bars concept - board screws on bench first</text>',
      '<text x="42" y="64" fill="#c7d4e5" font-family="Arial" font-size="15">Two rails along full display height; NOT compatible with the unchanged case mounting arms without redesign</text>',
      f'<rect x="{px(8):.1f}" y="{py(8):.1f}" width="{106.1*s:.1f}" height="{67.8*s:.1f}" rx="8" fill="#223e53" stroke="#95bed4" stroke-width="2"/>'])
    bar=options['preassembled_carrier']
    for seat in data['trial_preassembled_sidebars']:
        x=seat['bar_x_mm'];ear=seat['ear_x_mm'];y=bar['ear_v_mm']
        p.append(f'<rect x="{px(x-bar["bar_width_x_mm"]/2):.1f}" y="{py(bar["bar_start_v_mm"]):.1f}" width="{bar["bar_width_x_mm"]*s:.1f}" height="{bar["length_v_mm"]*s:.1f}" rx="3" fill="#65b7a2" fill-opacity=".5" stroke="#8de3ce" stroke-width="2"/>')
        for v in seat['board_v_holes_mm']:
            p.append(f'<circle cx="{px(x):.1f}" cy="{py(v):.1f}" r="6" fill="#101820" stroke="#e5edf2" stroke-width="2"/>')
        p.append(f'<circle cx="{px(ear):.1f}" cy="{py(y):.1f}" r="10" fill="#dcaf6a" stroke="#fbd292" stroke-width="2"/>')
    p.extend(['<text x="590" y="132" font-family="Arial" fill="#b5f1df" font-size="19">4 existing Waveshare screw axes (98 x 60mm)</text>',
       '<text x="590" y="172" font-family="Arial" fill="#ffcf8d" font-size="19">2 trial vertical fastening ears (gold)</text>',
       '<text x="590" y="220" font-family="Arial" fill="#e0e7f3" font-size="16">Assemble LCD into twin bars on a bench,</text>',
       '<text x="590" y="246" font-family="Arial" fill="#e0e7f3" font-size="16">then insert assembly and screw to CASE using</text>',
       '<text x="590" y="272" font-family="Arial" fill="#e0e7f3" font-size="16">accessible UNDERBODY fasteners.</text>',
       '<text x="590" y="318" font-family="Arial" fill="#ffbeaa" font-size="16">Case-side attachment seats not built!</text>',
       '<text x="590" y="345" font-family="Arial" fill="#ffbeaa" font-size="16">Interference, screw access and cable fit unverified.</text>',
       '<text x="590" y="415" font-family="Arial" fill="#c5d3e0" font-size="14">Same R5 body, USB-left, 4mm caps, hook-click V2 lid</text>',
       '<text x="46" y="530" font-family="Arial" fill="#a9c2da" font-size="17">CONCEPT ONLY - rails do not alter source CAD shell or replace its fixed brackets.</text>',
       '<text x="46" y="560" font-family="Arial" fill="#e4ae7a" font-size="16">A carrier could make LCD fastening on a workbench possible - but needs an assembly route and case anchors.</text>',
       '</svg>'])
    return '\n'.join(p)+'\n'

def entry_svg(data,options):
    z0=540;s=5.;X0=78; h_min,h_max=12.,71.093
    y_min,y_max=data['seated_y_footprint_mm'];shifts=data['projected_y_stage_translation_range_mm']
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="580" viewBox="0 0 1100 580">',
       '<rect width="1100" height="580" fill="#0f1720"/>',
       '<text x="35" y="39" font-family="Arial" fill="#f3f7fb" font-size="24">Underbody entry: staging a 3D box is not the same as installing the real LCD</text>',
       '<text x="35" y="68" font-family="Arial" fill="#acccdf" font-size="16">Desk Y (front to rear, mm), box rotated with the fitted 55 degree screen face</text>']
    py=lambda y:X0+y*s
    o.extend([f'<rect x="{py(0)}" y="175" width="{83.093*s}" height="146" fill="#334457" stroke="#93b3cc" stroke-width="2"/>',
      f'<rect x="{py(h_min)}" y="176" width="{(h_max-h_min)*s}" height="143" fill="#101820" stroke="#8de1db" stroke-width="2"/>',
      f'<rect x="{py(y_min)}" y="207" width="{(y_max-y_min)*s}" height="65" fill="#eab46e" fill-opacity=".65" stroke="#efc48c"/>',
      f'<text x="{py(y_min)+7}" y="248" fill="#18202a" font-size="14">SEATED screen bbox</text>',
      f'<rect x="{py(y_min-7)}" y="354" width="{(y_max-y_min)*s}" height="65" fill="#65b8ae" fill-opacity=".6" stroke="#9ae1d5"/>',
      '<text x="83" y="464" fill="#acdcdb" font-family="Arial" font-size="15">Blue-green rectangle: -7mm desk-Y shift to pass theoretical 2D hatch footprint.</text>',
      '<text x="83" y="492" fill="#efc28d" font-family="Arial" font-size="15">Orange rectangle: nominal seated screen extends 4.04mm past rear hatch edge.</text>',
      '<text x="83" y="530" fill="#dfe5ed" font-family="Arial" font-size="14">Neither projected rectangle is a swept 3D rigid-body path, nor the actual PCB silhouette.</text>', '</svg>'])
    return '\n'.join(o)+'\n'


def make_board_carriers(dim,ref,casecfg,options,d):
    import cadquery as cq
    a=options['preassembled_carrier'];rows=d['trial_preassembled_sidebars'];plane=face_plane(dim)
    rail_solids=[]
    for i,row in enumerate(rows):
        x=row['bar_x_mm'];seat=row['back_seat_start_w_mm'];v0=a['bar_start_v_mm'];vl=a['length_v_mm'];th=a['bar_thickness_w_mm'];ear_x=row['ear_x_mm'];v=a['ear_v_mm'];
        bar=(cq.Workplane(plane).transformed(offset=(0,0,seat)).center(x,v0+vl/2).rect(a['bar_width_x_mm'],vl).extrude(th))
        for hole_v in row['board_v_holes_mm']:
            bore=(cq.Workplane(plane).transformed(offset=(0,0,seat-.25)).center(x,hole_v).circle(a['board_hole_diameter_mm']/2).extrude(th+.5))
            bar=bar.cut(bore)
        # A *sideways* integral mounting ear provides a possible underside-access screw
        # location, to be fastened to a redesigned case boss (not in original shell).
        bridge=(cq.Workplane(plane).transformed(offset=(0,0,seat)).center((x+ear_x)/2,v).rect(abs(ear_x-x)+3.8,8.0).extrude(th))
        bar=bar.union(bridge)
        px,py,pz=local_to_world(dim,ear_x,v,seat+th/2)
        pad=(cq.Workplane('XY').workplane(offset=pz-1.5).center(px,py).circle(a['vertical_ear_diameter_mm']/2).extrude(3.0))
        bar=bar.union(pad)
        drill=(cq.Workplane('XY').workplane(offset=pz-3.0).center(px,py).circle(a['vertical_ear_hole_mm']/2).extrude(6.0))
        bar=bar.cut(drill)
        shape=bar.val();
        if len(shape.Solids())!=1 or not shape.isValid():raise ValueError('Trial mounting rail invalid/disconnected')
        rail_solids.append(shape)
    return rail_solids


def cad_check(dims,ref,casecfg,options,data,case_path,outdir):
    import cadquery as cq
    from screen_install_path_study import part_box_cad
    base=Path(case_path)
    if not base.is_file():raise FileNotFoundError(base)
    old=cq.importers.importStep(str(base)).val()
    if not old.isValid() or len(old.Solids())!=1:raise ValueError('Original case invalid')
    board=part_box_cad(dims,rotated_parts(dims,ref,180)['full_assembly'],options['trial_rear_glass_w_mm']);centre=board.Center()
    tilts=options['entry_samples']['temporary_tilt_deg'];ys=options['entry_samples']['temporary_y_shifts_mm'];dzs=options['entry_samples']['approach_z_offsets_mm'];arr=[]
    for angle in tilts:
        angled=board.rotate((centre.x,centre.y,centre.z),(centre.x+1,centre.y,centre.z),angle)
        for dy in ys:
            for dz in dzs:
                test=angled.translate((0,dy,dz));volume=round(float(old.intersect(test).Volume()),2)
                arr.append({'tilt_deg':angle,'desk_y_shift_mm':dy,'vertical_z_offset_mm':dz,'proxy_case_intersection_mm3':volume,'conservative_proxy_free':volume<=0.05})
    # These grid points cannot form a certified safe continuous insertion path.
    rails=make_board_carriers(dims,ref,casecfg,options,data)
    rail_intersections=[round(float(old.intersect(s).Volume()),2) for s in rails]
    # Two underbody service driver axes, vertical in world frame.
    shaft=options['access_screw_trial'];r=shaft['shaft_diameter_mm']/2;l=shaft['tool_length_mm'];axes=[]
    for row in data['trial_preassembled_sidebars']:
        xc=row['ear_x_mm'];v=row['ear_v_mm'];seat=row['back_seat_start_w_mm'];world=local_to_world(dims,xc,v,seat+options['preassembled_carrier']['bar_thickness_w_mm']/2)
        tool=(cq.Workplane('XY').workplane(offset=world[2]-l).center(xc,world[1]).circle(r).extrude(l)).val()
        axes.append({'ear_x_mm':xc,'ear_v_mm':v,'shaft_start_z_mm':round(world[2]-l,2),'trial_case_material_intersection_mm3':round(float(old.intersect(tool).Volume()),2)})
    outdir.mkdir(exist_ok=True,parents=True)
    cq.exporters.export(rails[0],str(outdir/'Waveshare_trial_preassembled_LEFT_RAIL.step'))
    cq.exporters.export(rails[1],str(outdir/'Waveshare_trial_preassembled_RIGHT_RAIL.step'))
    ass=cq.Assembly(name='Waveshare_REMOVABLE_SIDE_RAIL_CONCEPT_ONLY')
    ass.add(old,name='ORIGINAL_UNMODIFIED_case',color=cq.Color(.19,.25,.32))
    ass.add(rails[0],name='TRIAL_left_side_rail',color=cq.Color(.35,.8,.68))
    ass.add(rails[1],name='TRIAL_right_side_rail',color=cq.Color(.35,.8,.68))
    ass.add(board,name='CONSERVATIVE_2023_full_board_prism',color=cq.Color(.80,.59,.30))
    ass.save(str(outdir/'Waveshare_carrier_bars_IN_CASE_CLASHES_UNRESOLVED.step'))
    # Pre-mounted screen + rails staged below in theoretical Y-projection fit position
    staged=cq.Assembly(name='Waveshare_SCREEN_STAGED_Y_MINUS_7_Z_MINUS_65_PROXY')
    staged.add(old,name='ORIGINAL_case',color=cq.Color(.19,.25,.32))
    staged.add(board.translate((0,-7,-65)),name='conservative_board_staged',color=cq.Color(.8,.58,.28))
    for i,rail in enumerate(rails):staged.add(rail.translate((0,-7,-65)),name=f'preassembled_bar_{i}',color=cq.Color(.36,.8,.65))
    staged.save(str(outdir/'Waveshare_preassembly_STAGED_POSITION_UNVERIFIED.step'))
    for name in ['Waveshare_trial_preassembled_LEFT_RAIL.step','Waveshare_trial_preassembled_RIGHT_RAIL.step']:
        sol=cq.importers.importStep(str(outdir/name)).val()
        if not sol.isValid() or len(sol.Solids())!=1:raise ValueError('Rail STEP failed roundtrip')
    original_again=cq.importers.importStep(str(base)).val()
    if abs(original_again.Volume()-old.Volume())>1e-6:raise ValueError('Original case changed')
    min_by_z={}
    for z in dzs:
        group=[a for a in arr if a['vertical_z_offset_mm']==z]
        best=min(group,key=lambda x:x['proxy_case_intersection_mm3']);min_by_z[str(z)]=best
    return {'sampled_poses':len(arr),'poses':arr,'best_sample_by_vertical_offset':min_by_z,
      'full_assembled_693_solid_NOT_used':True,
      'continuous_collision_free_path_NOT_verified':True,
      'source_case_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),
      'rail_case_intersection_mm3':rail_intersections,'vertical_ear_tool_access_trial':axes,
      'brackets_are_NOT_fitted_or_case_bosses_NOT_added':True,
      'exported_reference_steps':4}


def generate(out_dir,report_only=False,case_step=None):
    dim,ref,casecfg=load(); options=cfg(); options['legacy_screen_install_settings']=json.loads((HERE/'screen_install_study_parameters.json').read_text())
    d=describe(dim,ref,casecfg,options);out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'carrier_bar_mounting_plan.svg').write_text(geometry_svg(dim,d,options),encoding='utf-8')
    (out/'staged_entry_2d_projection.svg').write_text(entry_svg(d,options),encoding='utf-8')
    if not report_only:
        if case_step is None:raise ValueError('--case-step required for CAD mode; report-only works without it')
        d['cad_samples']=cad_check(dim,ref,casecfg,options,d,case_step,out)
    d['cad_sweep_performed']=not report_only
    (out/'screen_entry_and_preassembly_report.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print('Staging Y range of conservative box (2D only):',d['projected_y_stage_translation_range_mm'])
    print('4 Waveshare mounting screw targets on 98x60 pitch; pre-assembly bars + 2 underside bolt ears are conceptual.')
    if 'cad_samples' in d:
        a=d['cad_samples'];print('Sampled screen prism poses:',a['sampled_poses'],' / NO continuous collision-free route certified')
        print('Two bars vs UNMODIFIED case trial clash mm^3:',a['rail_case_intersection_mm3'])
        print('Underbody tool path intersection mm^3:',[v['trial_case_material_intersection_mm3'] for v in a['vertical_ear_tool_access_trial']])
    else:print('STEP case not loaded; theoretical dimensions only. Windows stdlib check.')
    print('DO NOT ALTER BASELINE CASE: Mounting bars are not designed case attachment solutions.')
    print('Output:',out)
    return d

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('--out-dir',type=Path,required=True)
    pa.add_argument('--report-only',action='store_true')
    pa.add_argument('--case-step',type=Path)
    a=pa.parse_args();generate(a.out_dir,a.report_only,a.case_step)
if __name__=='__main__':main()
