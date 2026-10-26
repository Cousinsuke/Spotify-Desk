#!/usr/bin/env python3
"""Screw-free sliding underside cover for experimental R5 USB-LEFT Rev B case.

The screen keeps four M2.5 *candidate* fastener holes. The cover has NO
screw holes/bosses; two continuous left/right rails capture a 2mm slide-in
plate, which feeds through a rear underside throat with a finger pull tab.

Nominal geometry is untested for slip retention, wear, tolerance, stiffness,
noncolliding LCD insertion, and FDM print orientation. **NOT printable yet**.
Use --report-only on stock Windows Python; CadQuery/Shapely for STEP outputs.
"""
from __future__ import annotations
import argparse
import json
import math
import tempfile
from pathlib import Path

from rotated_case_prototype import load
from orientation_180_study import rotated_parts
from media_controls_fit_study import assumptions, cad_build
from media_controls_height_variants import load_spec, variant

HERE=Path(__file__).resolve().parent
SPEC=HERE/'slide_in_rear_cover_study.json'


def specification(path=None):
    return json.loads(Path(path or SPEC).read_text(encoding='utf-8'))


def layout(dim, ref, cfg, data):
    if data['physical_rotation_deg']!=180 or data['cap_rest_height_mm']!=4.0:
        raise ValueError('Only 180-degree USB-left, 4mm keys supported')
    cut=cfg['bottom_access_nominal'];h=data['rear_opening'];cover=data['cover'];r=data['sliding_rails'];b=data['screen_brackets']
    if any(abs(h[a]-cut[c])>1e-5 for a,c in [('x_edge_mm','edge_x_mm'),('y_edge_mm','edge_y_mm'),('cut_height_mm','vertical_cut_height_mm')]):
        raise ValueError('Bottom hatch must match unchanged base geometry')
    w=dim['width'];depth=dim['depth'];ox=h['x_edge_mm'];oy=h['y_edge_mm']
    g=cover['perimeter_clearance_mm']
    if not .3<=g<=.7:raise ValueError('Unproven cover plan clearance outside cautious trial range')
    if cover['thickness_mm']<1.6:raise ValueError('Too thin for a slide plate trial')
    p={'x_min':ox+g,'x_max':w-ox-g,'y_min':oy+g,'y_max':depth-oy-g,
       'z_min':cover['bottom_z_mm'],'z_max':cover['bottom_z_mm']+cover['thickness_mm']}
    if not (r['lower_rail_z_max_mm']+.15<=p['z_min'] and
            p['z_max']+.20<=r['upper_rail_z_min_mm'] and
            r['upper_rail_z_min_mm']<=r['upper_rail_z_max_mm'] and
            r['lower_rail_z_min_mm']<r['lower_rail_z_max_mm']):
        raise ValueError('Sliding panel collides vertically with support rail')
    if not(r['overhang_into_opening_mm']>g+1.5 and r['outer_overlap_into_case_mm']>=1.5):
        raise ValueError('Rails do not support panel sufficiently in plan')
    if not(p['z_max']+.15<=r['mouth_cut_upper_z_mm']<r['upper_rail_z_min_mm']):
        raise ValueError('Entry opening blocks sliding panel or weakens upper rail')
    if cover['pull_tab_width_mm']>=p['x_max']-p['x_min'] or cover['pull_tab_width_mm']<12:
        raise ValueError('Pull tab width unsafe or out of range')
    if not .25<=cover['pull_tab_rear_projection_mm']<=1.5:raise ValueError('Pull tab must be accessible but not overly exposed')
    if not 0<cover['pull_tab_overlap_mm']<5:raise ValueError('Need overlapping join to slide plate')
    if cover['thumb_grip_groove_depth_mm'] >= cover['thickness_mm']/3:
        raise ValueError('Thumb grip weakens cover')
    if 'cover_fasteners' in data:raise ValueError('Bottom cover must have no screw hardware')
    # Include the screen supports from the previously validated manufacturer orientation, unchanged.
    vendor=rotated_parts(dim,ref,180)
    glass=cfg['front_glass_inward_w_mm']
    screen=[]
    for name in sorted(k for k in vendor if k.startswith('standoff_')):
        x,v,_=vendor[name].center
        seat=vendor[name].maximum[2]+glass+b['flange_front_clearance_mm']
        anchor=b['anchor_v_top_mm'] if v<dim['screen_origin'][1]+dim['screen_outer'][1]/2 else b['anchor_v_bottom_mm']
        screen.append({'name':name,'x':round(x,3),'v':round(v,3),
                'seat_front_w_mm':round(seat,3),'rear_w_mm':round(seat+b['flange_thickness_mm'],3),'anchor_v_mm':anchor})
    if len(screen)!=4:raise ValueError('Expected four manufacturer M2.5 target mounts')
    sx=sorted(set(a['x'] for a in screen));sv=sorted(set(a['v'] for a in screen))
    if abs(sx[1]-sx[0]-98)>.05 or abs(sv[1]-sv[0]-60)>.05:raise ValueError('Manufacturer mount pattern mismatch')
    if b['anchor_v_top_mm']+b['anchor_v_length_mm']/2>=dim['screen_origin'][1]-0.5:raise ValueError('Top bracket anchor projects into screen')
    if b['anchor_v_bottom_mm']-b['anchor_v_length_mm']/2<=dim['screen_origin'][1]+dim['screen_outer'][1]+.5:raise ValueError('Bottom bracket anchor projects into screen')
    return {'status':'SCREWLESS SLIDE-IN UNDERSIDE LID TRIAL. NOT FIT / PRINT / RETENTION VERIFIED.',
            'case':'R5 156mm USB LEFT / physically flipped Waveshare / 4mm nominal cap rise',
            'original_models_unchanged':True,'physical_fit_verified':False,
            'opening':{'x_min':ox,'x_max':w-ox,'y_min':oy,'y_max':depth-oy},
            'cover_body':p,
            'tab':{'x_min':w/2-cover['pull_tab_width_mm']/2,'x_max':w/2+cover['pull_tab_width_mm']/2,
                   'y_min':p['y_max']-cover['pull_tab_overlap_mm'],
                   'y_max':depth+cover['pull_tab_rear_projection_mm'],
                   'z_min':p['z_min'],'z_max':p['z_max']},
            'slide_direction':'Y+: withdraw toward REAR; insert toward Y- from rear opening',
            'rail_lower_top_z_mm':r['lower_rail_z_max_mm'],
            'rail_upper_bottom_z_mm':r['upper_rail_z_min_mm'],
            'rear_entry_mouth_top_z_mm':r['mouth_cut_upper_z_mm'],
            'side_rail_overlap_on_cover_mm':round(r['overhang_into_opening_mm']-g,3),
            'cover_screw_count':0,'screen_screw_count':len(screen),
            'screen_mounts':screen,'screen_pitch_mm':[98,60],
            'positive_retention_verified':False,'retention_warning':data['retention_note'],
            'open_questions':data['hardware_unverified']}


def face_plane(dim):
    import cadquery as cq
    a=math.radians(dim['face_tilt_deg'])
    return cq.Plane(origin=(0,dim['front_face_length']*math.cos(a),dim['height']),
                    xDir=(1,0,0),normal=(0,math.sin(a),-math.cos(a)))


def build(dim,ref,cfg,settings,out):
    import cadquery as cq
    report=layout(dim,ref,cfg,settings)
    cap=variant(assumptions(),load_spec(),4.0)
    with tempfile.TemporaryDirectory(prefix='spotify_R5_4mm_base_') as t:
        base=cad_build(dim,ref,cfg,cap,Path(t))
    before=base.Volume();shell=cq.Workplane(obj=base)
    W=dim['width'];D=dim['depth'];r=settings['sliding_rails'];l=settings['cover'];h=settings['rear_opening'];b=settings['screen_brackets']
    ox=h['x_edge_mm'];oy=h['y_edge_mm'];run=D-2*oy
    def box_xyz(x0,x1,y0,y1,z0,z1):
        if not(x0<x1 and y0<y1 and z0<z1):raise ValueError('Bad XYZ prism')
        return cq.Workplane('XY').workplane(offset=z0).center((x0+x1)/2,(y0+y1)/2).rect(x1-x0,y1-y0).extrude(z1-z0)
    # Cut a true feed-through slot across the original solid REAR wall at
    # low Z; unlike a blind underbody pocket this permits translation along Y.
    # Bottom is OPEN at rear mouth: don't leave a wafer-thin 0.3mm wall web.
    mouth=box_xyz(ox-.6,W-ox+.6,D-oy-r['mouth_y_overlap_mm'],D+2,-1,
                  r['mouth_cut_upper_z_mm'])
    shell=shell.cut(mouth)
    # Two retaining rails, both extending from original SIDE perimeter into
    # the hatch. Paired *lower* + *upper* continuous lips capture the slide.
    rails=[]
    for side in ('left','right'):
        if side=='left':
            x0=ox-r['outer_overlap_into_case_mm'];x1=ox+r['overhang_into_opening_mm']
        else:
            x0=W-ox-r['overhang_into_opening_mm'];x1=W-ox+r['outer_overlap_into_case_mm']
        for level,z0,z1 in (('bottom',r['lower_rail_z_min_mm'],r['lower_rail_z_max_mm']),
                            ('top',r['upper_rail_z_min_mm'],r['upper_rail_z_max_mm'])):
            # Keep rails inside original underbody rectangular hatch, up to
            # throat entrance. Cover can slide to the rear beyond these lips.
            shell=shell.union(box_xyz(x0,x1,oy,D-oy,z0,z1))
            rails.append({'side':side,'position':level,'x_range':[round(x0,3),round(x1,3)],
                          'z_range':[z0,z1]})
    # Manufacturer aligned front-panel (X,V,W) screen mounts from previous
    # study. Still only screen hardware has M2.5 trial screw holes.
    plane=face_plane(dim)
    def locrect(cx,cv,w0,w1,ww,ll):
        return cq.Workplane(plane).transformed(offset=(0,0,w0)).center(cx,cv).rect(ww,ll).extrude(w1-w0)
    def locdisk(cx,cv,w0,w1,d):
        return cq.Workplane(plane).transformed(offset=(0,0,w0)).center(cx,cv).circle(d/2).extrude(w1-w0)
    for target in report['screen_mounts']:
        x=target['x'];v=target['v'];s=target['seat_front_w_mm'];rear=target['rear_w_mm'];av=target['anchor_v_mm']
        anchor=locrect(x,av,b['anchor_front_w_mm'],s+1,b['anchor_width_mm'],b['anchor_v_length_mm'])
        span=abs(v-av)+b['anchor_v_length_mm']/2
        beam=locrect(x,(v+av)/2,s,rear+b['anchor_to_flange_rear_extension_mm'],b['beam_width_mm'],span)
        pad=locdisk(x,v,s,rear,b['flange_diameter_mm'])
        shell=shell.union(anchor).union(beam).union(pad)
        shell=shell.cut(locdisk(x,v,s-.20,rear+b['anchor_to_flange_rear_extension_mm']+.20,b['fastener_diameter_mm']))
    shell_solid=shell.val()
    if not shell_solid.isValid() or len(shell_solid.Solids())!=1:raise ValueError('Shell must be one valid solid')
    p=report['cover_body'];tab=report['tab']
    plate=box_xyz(p['x_min'],p['x_max'],p['y_min'],p['y_max'],p['z_min'],p['z_max'])
    tabsh=box_xyz(tab['x_min'],tab['x_max'],tab['y_min'],tab['y_max'],tab['z_min'],tab['z_max'])
    plate=plate.union(tabsh)
    # Three shallow underside fingernail-grip grooves near rear exposed tab.
    n=l['thumb_grip_groove_count'];groove_w=l['thumb_grip_groove_width_mm'];depth=l['thumb_grip_groove_depth_mm']
    for i in range(n):
        x=W/2+(i-(n-1)/2)*2.7
        notch=box_xyz(x-groove_w/2,x+groove_w/2,D-.85,D+.2,p['z_min']-.1,p['z_min']+depth)
        plate=plate.cut(notch)
    lid=plate.val()
    if not lid.isValid() or len(lid.Solids())!=1:raise ValueError('Lid must be a single solid')
    collision=shell_solid.intersect(lid).Volume()
    if collision>0.05:raise ValueError('Closed cover intersects case %.3f mm3'%collision)
    # Swept path: withdraw cover along +Y while maintaining x/z constant.
    # Excluding physical flexibility/detents; all intermediate rigid positions
    # have to be nonintersecting for a genuine slide-in architecture.
    sweep=[]
    for y_move in [0,3,8,15,25,40,55,66,74,82]:
        moved=lid.translate((0,y_move,0))
        volume=shell_solid.intersect(moved).Volume()
        sweep.append({'slide_y_offset_mm':y_move,'overlap_mm3':round(volume,5)})
        if volume>.12:raise ValueError('Slide blocked at +%.1fmm by %.3fmm3' %(y_move,volume))
    out.mkdir(parents=True,exist_ok=True)
    cq.exporters.export(shell_solid,str(out/'spotify_R5_USBleft_4mm_SLIDER_case_experimental.step'))
    cq.exporters.export(lid,str(out/'spotify_R5_SLIDE_IN_bottom_lid_experimental.step'))
    assy=cq.Assembly(name='SpotifyDeskR5_4mm_screwless_slider')
    assy.add(shell_solid,name='body_with_side_rails_and_screen_mounts',color=cq.Color(.19,.24,.29))
    assy.add(lid,name='screwless_underside_slider',color=cq.Color(.36,.42,.48))
    for row in report['screen_mounts']:
        assy.add(locdisk(row['x'],row['v'],row['seat_front_w_mm']-5.66,row['seat_front_w_mm'],5.5).val(),
                  name='M2_5_SCREEN_TARGET_'+row['name'],color=cq.Color(.93,.70,.30))
    assy.save(str(out/'spotify_R5_4mm_slider_installed_REFERENCE_ASSEMBLY.step'))
    exp=cq.Assembly(name='SpotifyDeskR5_slider_withdrawn_38mm')
    exp.add(shell_solid,name='case',color=cq.Color(.19,.24,.29))
    exp.add(lid.translate((0,38,0)),name='lid_partway_slid_out',color=cq.Color(.36,.42,.48))
    exp.save(str(out/'spotify_R5_4mm_slider_open_38mm_REFERENCE_ASSEMBLY.step'))
    return {'case_solid_valid':True,'lid_solid_valid':True,'case_original_volume_mm3':round(before,2),
            'case_slide_support_volume_mm3':round(shell_solid.Volume(),2),
            'lid_volume_mm3':round(lid.Volume(),2),'closed_overlap_mm3':round(collision,5),
            'sweep':sweep,'rail_count':len(rails),'rail_positions':rails,
            'case_outer_width_mm':round(shell_solid.BoundingBox().xlen,3),
            'lid_free_of_screw_holes':True,'positive_lock_mechanism_untested':True}


def underside_svg(dim,rpt):
    d=dim['depth'];w=dim['width'];s=3.6;x0=60;y0=95;p=rpt['cover_body'];t=rpt['tab'];
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="550" viewBox="0 0 1050 550">',
      '<rect width="1050" height="550" fill="#121923"/>',
      '<text x="58" y="38" fill="#ffffff" font-size="24" font-family="Arial">Spotify Desk R5 / screwless sliding underside panel</text>',
      '<text x="58" y="66" fill="#cad4de" font-size="15" font-family="Arial">Slides out toward the REAR (+Y). Side guide lips capture the cover; no rear-panel screws.</text>',
      f'<rect x="{x0}" y="{y0}" width="{w*s}" height="{d*s}" rx="15" fill="#374653" stroke="#93abbf" stroke-width="2"/>',
      f'<rect x="{x0+11*s}" y="{y0+12*s}" width="{(w-22)*s}" height="{(d-24)*s}" fill="#131d27" stroke="#d4dbe0"/>',
      f'<rect x="{x0+p["x_min"]*s}" y="{y0+p["y_min"]*s}" width="{(p["x_max"]-p["x_min"])*s}" height="{(p["y_max"]-p["y_min"])*s}" fill="#667f94" stroke="#e5f0f6" stroke-width="1.4"/>',
      f'<rect x="{x0+t["x_min"]*s}" y="{y0+t["y_min"]*s}" width="{(t["x_max"]-t["x_min"])*s}" height="{(t["y_max"]-t["y_min"])*s}" fill="#8495a5"/>']
    for x in [11,145]:
        dx=x-2 if x<80 else x-3
        lines.append(f'<rect x="{x0+dx*s}" y="{y0+12*s}" width="{5*s}" height="{(d-24)*s}" fill="#c6a46c" opacity=".78"/>')
    lines += [f'<text x="{x0+160}" y="{y0+(d+17)*s}" font-family="Arial" font-size="17" fill="#efc28d">Slide OUT ↓ toward rear</text>',
              '<text x="60" y="489" font-family="Arial" font-size="15" fill="#d8e1e9">Gold = captured side rail zones (underside). Pull tab is centered at rear. Screen screws remain.</text>',
              '<text x="60" y="513" font-family="Arial" font-size="14" fill="#e9b779">No latch durability or full physical cable/board insertion proof. Do not fabricate as final design.</text>','</svg>']
    return '\n'.join(lines)+'\n'


def side_section_svg(dim,rpt):
    l=rpt['cover_body'];bottom=rpt['rail_lower_top_z_mm'];top=rpt['rail_upper_bottom_z_mm'];m=rpt['rear_entry_mouth_top_z_mm']
    # Diagram not manufacturing scale; clear z dimensions and rail capture.
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450">',
       '<rect width="1000" height="450" fill="#141b25"/>',
       '<text x="45" y="39" fill="white" font-family="Arial" font-size="23">Slide cover section: side guide rails and open rear entrance</text>',
       '<text x="45" y="65" fill="#c7d7e6" font-family="Arial" font-size="15">Looking along rear-to-front slide path. Inward Z is upward in diagram.</text>',
       '<rect x="155" y="115" width="145" height="210" fill="#506575"/>',
       '<rect x="700" y="115" width="145" height="210" fill="#506575"/>',
       '<rect x="290" y="265" width="420" height="60" fill="#647c8e" stroke="#eaf1fa" stroke-width="3"/>',
       '<rect x="290" y="132" width="420" height="35" fill="#647c8e"/>',
       '<rect x="250" y="188" width="500" height="67" fill="#9cb1c2" stroke="white" stroke-width="2"/>',
       '<text x="375" y="225" font-family="Arial" font-size="16" fill="#172333">2 mm sliding cover</text>',
       '<text x="45" y="371" font-family="Arial" font-size="15" fill="#d4e3ed">Lower rails Z ≤ %.2f mm / lid Z %.2f…%.2f / upper rails start Z %.2f mm</text>'%(bottom,l['z_min'],l['z_max'],top),
       '<text x="45" y="400" font-family="Arial" font-size="15" fill="#d5ae79">Rear wall throat is cut up to Z %.2f mm for access. Dimensions conceptual.</text>'%m, '</svg>']
    return '\n'.join(o)+'\n'


def generate(folder, report_only=False, jsonpath=None):
    dim,ref,cfg=load();settings=specification(jsonpath)
    spec=layout(dim,ref,cfg,settings)
    folder.mkdir(exist_ok=True,parents=True)
    (folder/'slide_cover_underside_plan.svg').write_text(underside_svg(dim,spec),encoding='utf-8')
    (folder/'slide_cover_rail_section.svg').write_text(side_section_svg(dim,spec),encoding='utf-8')
    buildinfo=None
    if not report_only:buildinfo=build(dim,ref,cfg,settings,folder)
    result={'plan':spec,'cad_build':buildinfo}
    (folder/'slide_cover_design_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Screwless sliding underside cover — R5 USB LEFT / 4mm keys / screen mount screws retained')
    print('Rear lid: 2.0mm plate, %.2fmm plan gap, 2 side channels, pull tab; ZERO lid screw holes'%settings['cover']['perimeter_clearance_mm'])
    print('Screen: %d M2.5 trial screw positions on %sx%s pattern'%(spec['screen_screw_count'],*spec['screen_pitch_mm']))
    print('Design note: friction/positive retention not validated; real slide, insertion and CAD fit pending')
    print('Files:',folder)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report-only',action='store_true')
    ap.add_argument('--config',type=Path)
    args=ap.parse_args()
    generate(args.out_dir,args.report_only,args.config)

if __name__=='__main__':main()
