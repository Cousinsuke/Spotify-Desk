#!/usr/bin/env python3
"""Experimental 4mm R5 Rev B: independent removable underside cover and
provisional manufacturer-standoff-aligned touchscreen support cantilevers.

Regenerates base rounded USB-left shell from the existing 4mm source generator.
Does NOT modify any previous CAD or claim a physically fitted enclosure.
--report-only is Python-standard-library only (no CadQuery required).
"""
from __future__ import annotations
import argparse
import json
import math
import tempfile
from pathlib import Path

from rotated_case_prototype import load,geometry_parameters
from orientation_180_study import rotated_parts
from media_controls_fit_study import assumptions,cad_build
from media_controls_height_variants import load_spec,variant

HERE=Path(__file__).resolve().parent
SPEC=HERE/'rear_cover_screen_mount_study.json'


def load_specification(path=None):
    return json.loads(Path(path or SPEC).read_text(encoding='utf-8'))


def report(dim, reference, casecfg, settings):
    if settings['physical_rotation_deg']!=180 or settings['cap_rest_height_mm']!=4.0:
        raise ValueError('Only the chosen 180-degree module and 4mm cap version are supported')
    h=settings['rear_opening']; cover=settings['cover']; lip=settings['case_lip']; bolt=settings['cover_fasteners']; bracket=settings['screen_brackets']
    w=dim['width'];depth=dim['depth']
    base_cut=casecfg['bottom_access_nominal']
    if any(abs(h[a]-base_cut[b])>1e-5 for a,b in [('x_edge_mm','edge_x_mm'),('y_edge_mm','edge_y_mm'),('cut_height_mm','vertical_cut_height_mm')]):
        raise ValueError('Hatch opening must match existing Rev B shell cutout')
    ox=h['x_edge_mm']; oy=h['y_edge_mm']; open_w=w-2*ox;open_d=depth-2*oy
    gap=cover['perimeter_clearance_mm']; plate_w=open_w-2*gap;plate_d=open_d-2*gap
    if not .2<=gap<=.8:raise ValueError('Cover trial perimeter clearance must be between .2 and .8mm')
    if not 0<cover['corner_radius_mm']<min(plate_w,plate_d)/5: raise ValueError('Cover corner radius invalid')
    if not(0<cover['bottom_z_mm'] and cover['bottom_z_mm']+cover['thickness_mm']<=lip['bottom_z_mm']+.05):
        raise ValueError('Cover top must rest at/under supporting ledge and stay inside lower face')
    if lip['inner_overlap_mm']<1.4 or lip['outer_overlap_mm']<1:raise ValueError('Insufficient nominal seating lip')
    xoff=bolt['inset_x_mm'];yoff=bolt['inset_y_mm'];ys=[yoff,depth-yoff];xs=[xoff,w-xoff]
    fasteners=[{'x':x,'y':y} for y in ys for x in xs]
    if (xoff-bolt['boss_diameter_mm']/2)<(ox+gap) or (yoff-bolt['boss_diameter_mm']/2)<(oy+gap):
        raise ValueError('Boss location clips cover perimeter')
    if not 0<bolt['pilot_diameter_mm']<cover['screw_clearance_diameter_mm']<bolt['boss_diameter_mm']-3.0:
        raise ValueError('Screw diameter/strength geometry invalid')
    src=rotated_parts(dim,reference,180)
    glass=casecfg['front_glass_inward_w_mm']
    # Standoff is actual named geometry from manufacturer's old 2023 assembly.
    screen=[]
    for name in sorted(k for k in src if k.startswith('standoff_')):
        x,v,_=src[name].center
        seat=src[name].maximum[2]+glass+bracket['flange_front_clearance_mm']
        anchor=bracket['anchor_v_top_mm'] if v<dim['screen_origin'][1]+dim['screen_outer'][1]/2 else bracket['anchor_v_bottom_mm']
        screen.append({'name':name,'x':round(x,3),'v':round(v,3),
                       'seat_front_w_mm':round(seat,3),'rear_w_mm':round(seat+bracket['flange_thickness_mm'],3),
                       'anchor_v_mm':anchor})
    if len(screen)!=4:raise ValueError('Manufacturer reference should have exactly 4 standoffs')
    sx=sorted(set(x['x'] for x in screen));sv=sorted(set(x['v'] for x in screen))
    if len(sx)!=2 or len(sv)!=2:raise ValueError('Manufacturer mounting rectangle unexpected')
    if abs((sx[1]-sx[0])-98)>.05 or abs((sv[1]-sv[0])-60)>.05:
        raise ValueError('98x60mm pitch did not match board STEP')
    if bracket['anchor_v_top_mm']+bracket['anchor_v_length_mm']/2>=dim['screen_origin'][1]-0.5:
        raise ValueError('Top anchor invades full manufacturer glass footprint')
    if bracket['anchor_v_bottom_mm']-bracket['anchor_v_length_mm']/2<=dim['screen_origin'][1]+dim['screen_outer'][1]+.5:
        raise ValueError('Bottom anchor invades full manufacturer glass footprint')
    if bracket['flange_diameter_mm']<=bracket['fastener_diameter_mm']+4:
        raise ValueError('Screen support ring web is too thin for this trial')
    out={'status':'CASE/BOTTOM LID AND SCREEN SUPPORT CONCEPT ONLY; NOT FIT OR FABRICATION VALIDATED',
         'chosen_case':'R5 156mm USB-left / physically rotated Waveshare 180 / 4mm MX keycaps',
         'original_cad_preserved':True,'physical_fit_verified':False,
         'bottom_opening_mm':{'x_min':ox,'x_max':w-ox,'y_min':oy,'y_max':depth-oy},
         'bottom_cover_mm':{'x_min':ox+gap,'x_max':w-ox-gap,'y_min':oy+gap,'y_max':depth-oy-gap,'z_min':cover['bottom_z_mm'],'z_max':cover['bottom_z_mm']+cover['thickness_mm']},
         'lip_support_inner_reach_mm':lip['inner_overlap_mm'],
         'cover_screw_centers_xyz_mm':[[x['x'],x['y'],0] for x in fasteners],
         'screen_standoff_centers_and_seats':screen,
         'screen_standoff_pitch_mm':[round(sx[1]-sx[0],3),round(sv[1]-sv[0],3)],
         'screen_board_max_inward_w_at_trial_datum_mm':round(src['full_assembly'].maximum[2]+glass,3),
         'selected_keycap_rest_height_mm':4.0,
         'hardware_unverified':settings['tolerances_unverified']}
    return out


def face_plane(dim):
    import cadquery as cq
    a=math.radians(dim['face_tilt_deg'])
    return cq.Plane(origin=(0,dim['front_face_length']*math.cos(a),dim['height']),
                    xDir=(1,0,0),normal=(0,math.sin(a),-math.cos(a)))


def build_cad(dim, ref, cfg, settings, output):
    import cadquery as cq
    data=report(dim,ref,cfg,settings)
    cap=variant(assumptions(),load_spec(),4.0)
    with tempfile.TemporaryDirectory(prefix='spotify_4mm_base_') as t:
        original=cad_build(dim,ref,cfg,cap,Path(t))
    original_vol=original.Volume()
    shell=cq.Workplane(obj=original)
    hatch=settings['rear_opening']; lid=settings['cover']; lip=settings['case_lip']; screw=settings['cover_fasteners']; b=settings['screen_brackets'];
    width=dim['width'];depth=dim['depth']
    w_open=width-2*hatch['x_edge_mm'];d_open=depth-2*hatch['y_edge_mm']
    def xy_rect(ww,dd,cx,cy,z0,z1):
        return cq.Workplane('XY').workplane(offset=z0).center(cx,cy).rect(ww,dd).extrude(z1-z0)
    def xy_cyl(d,cx,cy,z0,z1):
        return cq.Workplane('XY').workplane(offset=z0).center(cx,cy).circle(d/2).extrude(z1-z0)
    # Support ledge overhangs the original opening by 2mm inward and spans
    # outside its edge to fuse onto the shell's existing underside web.
    ring=xy_rect(w_open+2*lip['outer_overlap_mm'],d_open+2*lip['outer_overlap_mm'],width/2,depth/2,
                 lip['bottom_z_mm'],lip['bottom_z_mm']+lip['height_mm'])
    core=xy_rect(w_open-2*lip['inner_overlap_mm'],d_open-2*lip['inner_overlap_mm'],width/2,depth/2,
                 lip['bottom_z_mm']-.1,lip['bottom_z_mm']+lip['height_mm']+.1)
    shell=shell.union(ring.cut(core))
    # 4 screw bosses are attached to ledge using actual horizontal bridging
    # webs, not floating unsupported CAD cylinders.
    for x,y,_ in data['cover_screw_centers_xyz_mm']:
        boss=xy_cyl(screw['boss_diameter_mm'],x,y,screw['boss_base_z_mm'],screw['boss_base_z_mm']+screw['boss_height_mm'])
        towards_left=x<width/2; near_front=y<depth/2
        edge_x=hatch['x_edge_mm']-lip['outer_overlap_mm'] if towards_left else width-(hatch['x_edge_mm']-lip['outer_overlap_mm'])
        edge_y=hatch['y_edge_mm']-lip['outer_overlap_mm'] if near_front else depth-(hatch['y_edge_mm']-lip['outer_overlap_mm'])
        bx=xy_rect(abs(x-edge_x)+1,screw['bridge_width_mm'],(x+edge_x)/2,y,
                   lip['bottom_z_mm'],lip['bottom_z_mm']+screw['bridge_height_mm'])
        by=xy_rect(screw['bridge_width_mm'],abs(y-edge_y)+1,x,(y+edge_y)/2,
                   lip['bottom_z_mm'],lip['bottom_z_mm']+screw['bridge_height_mm'])
        shell=shell.union(boss).union(bx).union(by)
        shell=shell.cut(xy_cyl(screw['pilot_diameter_mm'],x,y,lid['bottom_z_mm']+lid['thickness_mm']-.05,
                                screw['boss_base_z_mm']+screw['boss_height_mm']+.2))
    # Four screen support posts. Anchors are deliberately just beyond the full
    # LCD module footprint (top and bottom in V), with *rear* cantilever beams
    # leading to drilled pads aimed at the STEP's actual 98 x 60mm standoffs.
    # Clearance against the 693-solid manufacturer's assembly is NOT proven.
    plane=face_plane(dim)
    def local_rect(cx,cv,w0,w1,ww,ll):
        return cq.Workplane(plane).transformed(offset=(0,0,w0)).center(cx,cv).rect(ww,ll).extrude(w1-w0)
    def local_disk(cx,cv,w0,w1,diam):
        return cq.Workplane(plane).transformed(offset=(0,0,w0)).center(cx,cv).circle(diam/2).extrude(w1-w0)
    for row in data['screen_standoff_centers_and_seats']:
        x=row['x'];v=row['v'];seat=row['seat_front_w_mm'];rear=row['rear_w_mm'];av=row['anchor_v_mm']
        # Landing region just behind the nominal front skin and outside module
        anchor=local_rect(x,av,b['anchor_front_w_mm'],seat+1,
                          b['anchor_width_mm'],b['anchor_v_length_mm'])
        # Beam remains behind the board (seat W) until the M2.5 standoff target.
        span=abs(v-av)+b['anchor_v_length_mm']/2
        beam=local_rect(x,(v+av)/2,seat,rear+b['anchor_to_flange_rear_extension_mm'],
                        b['beam_width_mm'],span)
        pad=local_disk(x,v,seat,rear,b['flange_diameter_mm'])
        shell=shell.union(anchor).union(beam).union(pad)
        shell=shell.cut(local_disk(x,v,seat-.20,rear+b['anchor_to_flange_rear_extension_mm']+.20,
                                   b['fastener_diameter_mm']))
    solid=shell.val()
    if not solid.isValid() or len(solid.Solids())!=1:
        raise ValueError('Integrated shell does not form a valid single solid')
    if solid.Volume()<=original_vol:raise ValueError('Lid supports added no material')
    # Separate flush-ish cover with 0.4 mm nominal all-sided perimeter clearance
    # and four through-holes. This is independently removable from shell.
    c=data['bottom_cover_mm'];cw=c['x_max']-c['x_min'];ch=c['y_max']-c['y_min']
    cover=(cq.Workplane('XY').workplane(offset=c['z_min']).center(width/2,depth/2)
           .rect(cw,ch).extrude(c['z_max']-c['z_min']).edges('|Z').fillet(lid['corner_radius_mm']))
    for x,y,_ in data['cover_screw_centers_xyz_mm']:
        cover=cover.cut(xy_cyl(lid['screw_clearance_diameter_mm'],x,y,c['z_min']-.2,c['z_max']+.2))
    lidshape=cover.val()
    if not lidshape.isValid() or len(lidshape.Solids())!=1:
        raise ValueError('Rear cover is not a single valid STEP solid')
    # Non-interpenetration is expected except for touching separation planes.
    cl=solid.intersect(lidshape)
    if cl.Volume()>0.5:raise ValueError(f'Cover volumetric intersection with shell: {cl.Volume():.2f}mm3')
    output.mkdir(parents=True,exist_ok=True)
    casepath=output/'spotify_revB_R5_USBleft_4mm_case_with_mounts_EXPERIMENTAL.step'
    lidpath=output/'spotify_revB_removable_rear_cover_EXPERIMENTAL.step'
    cq.exporters.export(solid,str(casepath))
    cq.exporters.export(lidshape,str(lidpath))
    assy=cq.Assembly(name='SpotifyDeskRevB_4mm_screen_and_hatch_concept')
    assy.add(solid,name='rounded_case_with_mounts',color=cq.Color(.18,.23,.29))
    assy.add(lidshape,name='removable_bottom_plate',color=cq.Color(.30,.37,.43))
    # Four target standoffs, abstracted from measured STEP, not imported vendor CAD.
    for row in data['screen_standoff_centers_and_seats']:
        part=local_disk(row['x'],row['v'],row['seat_front_w_mm']-5.66,row['seat_front_w_mm'],5.5).val()
        assy.add(part,name='manufacturer_standoff_TARGET_'+row['name'],color=cq.Color(.95,.72,.34))
    assy.save(str(output/'spotify_revB_case_cover_and_screen_target_ASSEMBLY.step'))
    exploded=cq.Assembly(name='SpotifyDeskRevB_4mm_rear_cover_exploded')
    exploded.add(solid,name='case',color=cq.Color(.18,.23,.29))
    lid_ex=lidshape.translate((0,0,-10.0))
    exploded.add(lid_ex,name='rear_cover_removed_10mm',color=cq.Color(.30,.37,.43))
    exploded.save(str(output/'spotify_revB_rear_cover_exploded_ASSEMBLY.step'))
    return {'original_4mm_case_volume_mm3':round(original_vol,3),
            'shell_with_supports_volume_mm3':round(solid.Volume(),3),
            'rear_cover_volume_mm3':round(lidshape.Volume(),3),
            'cover_case_overlap_mm3':round(cl.Volume(),6),
            'case_valid':True,'cover_valid':True,'both_single_solid':True,
            'files':[casepath.name,lidpath.name,
             'spotify_revB_case_cover_and_screen_target_ASSEMBLY.step',
             'spotify_revB_rear_cover_exploded_ASSEMBLY.step']}


def plan_svg(dim,data,settings):
    """Bottom plan: panel/screws; sloped face uses X/V, not the desk Y axis."""
    w=dim['width'];d=dim['depth'];s=3.1;x0=60;y0=106
    coords=data['bottom_cover_mm'];o=[
      '<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="610" viewBox="0 0 1050 610">',
      '<rect width="1050" height="610" fill="#111922"/>',
      '<text x="60" y="48" font-family="Arial" font-size="25" fill="#edf4f8">Rear cover / underside plan (concept)</text>',
      '<text x="60" y="77" font-family="Arial" font-size="15" fill="#aebdc8">Actual case 156 × 83.09 mm / 4 removable screws / lid separately exportable</text>',
      f'<rect x="{x0}" y="{y0}" width="{w*s}" height="{d*s}" rx="14" fill="#364651" stroke="#a9bbc9" stroke-width="2"/>',
      f'<rect x="{x0+data["bottom_opening_mm"]["x_min"]*s}" y="{y0+data["bottom_opening_mm"]["y_min"]*s}" width="{(data["bottom_opening_mm"]["x_max"]-data["bottom_opening_mm"]["x_min"])*s}" height="{(data["bottom_opening_mm"]["y_max"]-data["bottom_opening_mm"]["y_min"])*s}" fill="#0c1218" stroke="#e3b078" stroke-width="2"/>',
      f'<rect x="{x0+coords["x_min"]*s}" y="{y0+coords["y_min"]*s}" width="{(coords["x_max"]-coords["x_min"])*s}" height="{(coords["y_max"]-coords["y_min"])*s}" rx="6" fill="#657e91" stroke="#edf4fb" stroke-width="1"/>',
    ]
    for x,y,_ in data['cover_screw_centers_xyz_mm']:
        o.append(f'<circle cx="{x0+x*s:.1f}" cy="{y0+y*s:.1f}" r="7" fill="#101922" stroke="#f2f5f7" stroke-width="2"/>')
    o += [f'<text x="{x0}" y="425" font-family="Arial" font-size="15" fill="#e4b878">Screw centres X={settings["cover_fasteners"]["inset_x_mm"]} / {w-settings["cover_fasteners"]["inset_x_mm"]} mm</text>',
         f'<text x="{x0}" y="450" font-family="Arial" font-size="15" fill="#b8cad7">Y={settings["cover_fasteners"]["inset_y_mm"]} / {d-settings["cover_fasteners"]["inset_y_mm"]:.3f} mm</text>',
         '<text x="60" y="540" font-family="Arial" font-size="15" fill="#e8b374">M2.5 hardware/pilot fit, material strength and panel tolerance not proven.</text>', '</svg>']
    return '\n'.join(o)+'\n'


def screen_svg(dim,data):
    s=3.6;x0=50;y0=105
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="950" height="600" viewBox="0 0 950 600">',
       '<rect width="950" height="600" fill="#111922"/>',
       '<text x="50" y="42" font-family="Arial" font-size="24" fill="#f6f7fa">Screen support alignment / face X,V</text>',
       '<text x="50" y="67" font-family="Arial" font-size="15" fill="#c8d5df">180-degree Waveshare / nominal 98 × 60 mm M2.5 standoff centres from manufacturer STEP</text>',
       f'<rect x="{x0}" y="{y0}" width="{dim["width"]*s}" height="{dim["front_face_length"]*s}" rx="12" fill="#303c49" stroke="#b4bdc8"/>',
       f'<rect x="{x0+dim["screen_origin"][0]*s}" y="{y0+dim["screen_origin"][1]*s}" width="{dim["screen_outer"][0]*s}" height="{dim["screen_outer"][1]*s}" fill="#1a485d" stroke="#66bed6" stroke-width="1"/>']
    for p in data['screen_standoff_centers_and_seats']:
        px=x0+p['x']*s;pv=y0+p['v']*s
        an=y0+p['anchor_v_mm']*s
        o += [f'<path d="M {px:.1f} {an:.1f} V {pv:.1f}" stroke="#d0b06c" stroke-width="25"/>',
              f'<circle cx="{px:.1f}" cy="{pv:.1f}" r="13.5" fill="#d4aa68" stroke="#f9e3b5" stroke-width="2"/>',
              f'<circle cx="{px:.1f}" cy="{pv:.1f}" r="5" fill="#1d2530"/>']
    o.extend(['<text x="50" y="551" font-family="Arial" font-size="15" fill="#e3af7a">Brackets behind display glass; direct interference with PCB / antenna / ribbon remains unverified.</text>', '</svg>'])
    return '\n'.join(o)+'\n'


def generate(outdir, report_only=False, spec_file=None):
    dim,ref,cfg=load();spec=load_specification(spec_file)
    r=report(dim,ref,cfg,spec)
    outdir.mkdir(parents=True,exist_ok=True)
    result={'geometry':r, 'cad_build':None}
    (outdir/'rear_screen_mount_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (outdir/'rear_cover_bottom_plan.svg').write_text(plan_svg(dim,r,spec),encoding='utf-8')
    (outdir/'screen_mount_front_plan.svg').write_text(screen_svg(dim,r),encoding='utf-8')
    if not report_only:
        cad=build_cad(dim,ref,cfg,spec,outdir)
        result['cad_build']=cad
        (outdir/'rear_screen_mount_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Experimental R5 USB-left 4mm rear cover and LCD mount support: NOT FIT-VERIFIED')
    print('Cover: 0.4mm nominal perimeter gap, 2mm thick, 4x M2.5 nominal screw positions')
    print('Screen mount: 98x60mm 2023 manufacturer standoff pitch; no full 693-part interference inspection')
    print('Output:',outdir)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',required=True,type=Path)
    p.add_argument('--report-only',action='store_true',help='JSON/SVG only, Python standard library')
    p.add_argument('--config',type=Path,help='Optional trial dimension JSON')
    args=p.parse_args()
    generate(args.out_dir,args.report_only,args.config)


if __name__=='__main__':main()
