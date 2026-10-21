#!/usr/bin/env python3
"""Rev B experimental 180-degree touchscreen enclosure prototypes.

Generates separate SHARP and R5-ROUNDED STEP shell references with a provisional
left-side USB-C1 wall passage and relocated rotated display aperture. Based on
Waveshare STEP *socket housing* bounding boxes, not actual cable geometry.
NEVER overwrites the previously accepted Rev B CAD source or exports.
Requires CadQuery/Shapely for actual STEP exports; JSON mode uses Python stdlib.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from orientation_180_study import compare,rotated_parts,display_aperture

HERE=Path(__file__).resolve().parent


def load(dimensions=None,reference=None,configuration=None):
    return tuple(json.loads(Path(p).read_text(encoding='utf-8')) for p in (
        dimensions or HERE/'dimensions.json', reference or HERE/'waveshare_step_reference.json',
        configuration or HERE/'rotated_case_parameters.json'))


def geometry_parameters(dim,ref,cfg):
    if cfg['physical_rotation_deg']!=180:raise ValueError('Prototype requires physical 180-degree module rotation')
    wall=cfg['case_wall_mm']
    if wall<=0 or abs(wall-dim['wall_assumed'])>1e-6:raise ValueError('Wall parameter must match retained Rev B wall assumption')
    window=display_aperture(dim,180)
    source=rotated_parts(dim,ref,180)
    usb=source['usb_type_c1']
    uart=source['usb_type_c2']
    h7=source['i2c_4pin_socket']
    p=cfg['usb_c1_service_slot']
    if any(p[k]<0 for k in p):raise ValueError('USB slot allowances must be >=0')
    if cfg['front_glass_inward_w_mm']<wall:raise ValueError('Front-glass reference may not intersect front face material')
    # USB-C1 measured in *source STEP* at glass W=0; translate to seating datum.
    shift=cfg['front_glass_inward_w_mm']
    port={
        'x_min':-p['outer_x_extra_mm'],
        'x_max':usb.minimum[0]+p['reach_past_socket_inner_edge_x_mm'],
        'v_min':usb.minimum[1]-p['v_margin_mm'],
        'v_max':usb.maximum[1]+p['v_margin_mm'],
        'w_min':usb.minimum[2]+shift-p['w_margin_mm'],
        'w_max':usb.maximum[2]+shift+p['w_margin_mm'],
    }
    if port['v_min']<0 or port['v_max']>dim['front_face_length']:
        raise ValueError('USB slot extends past sloping front')
    if port['w_min']<wall:raise ValueError('USB service slot intersects frontal skin; reposition module, do not silently cut face')
    if port['x_max']<=wall or port['x_min']>=0:raise ValueError('USB slot must pass through left wall')
    gap=dim['keys_v']-9-(window['v']+window['height'])
    if gap < 1:raise ValueError('Rotated display aperture collides with MX keycaps')
    return {
        'design_status':'EXPERIMENTAL, NOT FIT-VERIFIED OR READY TO PRINT',
        'units':'mm','orientation_deg':180,
        'outer_width_mm':dim['width'],'face_length_mm':dim['front_face_length'],
        'face_angle_deg':dim['face_tilt_deg'],'wall_assumed_mm':wall,
        'display_aperture':window,
        'original_aperture':display_aperture(dim,0),
        'visible_to_keycap_top_gap_mm':round(gap,3),
        'usb_c1_measured_bare_housing':{'min':usb.minimum,'max':usb.maximum},
        'usb_uart_c2_measured_bare_housing':{'min':uart.minimum,'max':uart.maximum},
        'right_i2c_measured_bare_housing':{'min':h7.minimum,'max':h7.maximum},
        'left_usb_c1_service_slot_trial':{k:round(v,3) for k,v in port.items()},
        'glass_inward_mount_datum_assumed_mm':shift,
        'assembled_step_rear_w_max_at_datum_mm':round(source['full_assembly'].maximum[2]+shift,3),
        'nominal_mount_pitch_mm':dim['display_nominal_fixing_centers'],
        'experimental_case_variants':['sharp','rounded'],
        'unmodelled':[
           'no actual USB-C male plug/cable geometry or environmental sealing',
           'no LCD bearing ledge/mounting bosses or validated thread size',
           'no real rotary body/shaft/nut/terminal clearance or 180 degree touch firmware',
           'no 3D collision check against 693-solid Waveshare manufacturer STEP assembly',
           'no load/print wall strength, clip, tool/tolerance or final bottom hatch',
           'no UART access slot (optional future service access)',
           'no I2C harness bend, antenna, expander mount, airflow, strain relief'
        ]
    }


def make_shell(dim,par,variant,cfg):
    """Independent B-rep case; returns CadQuery shape. No manufacturer geometry included."""
    import cadquery as cq
    from shapely.geometry import Polygon
    if variant not in ('sharp','rounded'):raise ValueError('Unknown case variant')
    ang=math.radians(dim['face_tilt_deg'])
    run=dim['front_face_length']*math.cos(ang)
    rise=dim['front_face_length']*math.sin(ang)
    height=dim['front_chin']+rise
    depth=run+dim['rear_roof']
    outline=[(0,0),(depth,0),(depth,height),(run,height),(0,dim['front_chin'])]
    width=dim['width'];wall=cfg['case_wall_mm']
    inner=Polygon(outline).buffer(-wall,join_style=2)
    if inner.is_empty: raise ValueError('Inner cavity failed')
    def prism(pts,ww,xx=0):return cq.Workplane('YZ').polyline(pts).close().extrude(ww).translate((xx,0,0))
    shell=prism(outline,width)
    if variant=='rounded':shell=shell.edges().fillet(cfg['rounded_edge_radius_mm'])
    shell=shell.cut(prism(list(inner.exterior.coords)[:-1],width-2*wall,wall))
    bottom=cfg['bottom_access_nominal']
    # Existing Rev B underside cutout: unfastened access hole, not a hatch.
    hatch=cq.Workplane('XY').box(width-2*bottom['edge_x_mm'],depth-2*bottom['edge_y_mm'],bottom['vertical_cut_height_mm'],centered=(True,True,False)).translate((width/2,depth/2,-3))
    shell=shell.cut(hatch)
    norm=(0,math.sin(ang),-math.cos(ang))
    # Face plane origin is sloped TOP; Workplane Y axis points DOWN the slope.
    plane=cq.Plane(origin=(0,run,height),xDir=(1,0,0),normal=norm)
    def cut_face(xmin,xmax,vmin,vmax,wmin,wmax):
        if not (xmin<xmax and vmin<vmax and wmin<wmax):raise ValueError('Invalid cut')
        return (cq.Workplane(plane).transformed(offset=(0,0,wmin))
             .center((xmin+xmax)/2,(vmin+vmax)/2)
             .rect(xmax-xmin,vmax-vmin).extrude(wmax-wmin))
    win=par['display_aperture']; extra=cfg['display_aperture_extra_each_side_mm']
    shell=shell.cut(cut_face(win['x']-extra,win['x']+win['width']+extra,
               win['v']-extra,win['v']+win['height']+extra,-1,5))
    for kx in dim['keys_x']:
        half=cfg['mx_aperture_mm']/2
        shell=shell.cut(cut_face(kx-half,kx+half,dim['keys_v']-half,dim['keys_v']+half,-1,8))
    # Encoder mounting trial M7; screw/nut and press travel not modeled.
    shell=shell.cut(cq.Workplane(plane).transformed(offset=(0,0,-1))
                    .center(dim['knob_x'],dim['knob_v'])
                    .circle(cfg['encoder_bore_mm']/2).extrude(8))
    port=par['left_usb_c1_service_slot_trial']
    # Only cuts shell near LEFT side wall, NOT a front USB aperture.
    shell=shell.cut(cut_face(port['x_min'],port['x_max'],port['v_min'],port['v_max'],port['w_min'],port['w_max']))
    return shell.val()


def make_reference_envelopes(dim,par,cfg):
    import cadquery as cq
    ang=math.radians(dim['face_tilt_deg']);run=dim['front_face_length']*math.cos(ang)
    height=dim['front_chin']+dim['front_face_length']*math.sin(ang)
    plane=cq.Plane(origin=(0,run,height),xDir=(1,0,0),normal=(0,math.sin(ang),-math.cos(ang)))
    def part(xlo,xhi,vlo,vhi,wlo,whi):
        return (cq.Workplane(plane).transformed(offset=(0,0,wlo)).center((xlo+xhi)/2,(vlo+vhi)/2)
            .rect(xhi-xlo,vhi-vlo).extrude(whi-wlo).val())
    sx,sv=dim['screen_origin'];sw,sh=dim['screen_outer'];w=cfg['front_glass_inward_w_mm']
    out={'lcd_full_assembled_bbox':part(sx,sx+sw,sv,sv+sh,w,w+16.906)}
    for k,source in [('usb_c1_socket','usb_c1_measured_bare_housing'),('usb_uart_c2_socket','usb_uart_c2_measured_bare_housing'),('right_i2c_socket','right_i2c_measured_bare_housing')]:
        lo,hi=par[source]['min'],par[source]['max']
        out[k]=part(lo[0],hi[0],lo[1],hi[1],lo[2]+w,hi[2]+w)
    return out


def make_summary_svg(dim,par):
    win=par['display_aperture']; port=par['left_usb_c1_service_slot_trial']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -15 166 146" width="996" height="876">',
        '<rect x="-5" y="-15" width="166" height="146" fill="#172431"/>',
        '<text x="1" y="-8" fill="#e9f3f9" font-size="3.8" font-family="Arial">Experimental Rev B / physically rotated LCD 180 degrees</text>',
        f'<rect x="0" y="0" width="{dim["width"]}" height="{dim["front_face_length"]}" fill="#313f4c" stroke="#b8c9d5"/>',
        f'<rect x="{dim["screen_origin"][0]}" y="{dim["screen_origin"][1]}" width="{dim["screen_outer"][0]}" height="{dim["screen_outer"][1]}" fill="#144558" stroke="#7cc8e2"/>',
        f'<rect x="{win["x"]}" y="{win["v"]}" width="{win["width"]}" height="{win["height"]}" fill="#1682aa"/>',
        f'<rect x="0" y="{port["v_min"]}" width="3" height="{port["v_max"]-port["v_min"]}" fill="#e7a349"/>']
    for k,color in [('usb_c1_measured_bare_housing','#edc165'),('usb_uart_c2_measured_bare_housing','#edc165'),('right_i2c_measured_bare_housing','#91d7a2')]:
        lo,hi=par[k]['min'],par[k]['max'];svg.append(f'<rect x="{lo[0]}" y="{lo[1]}" width="{hi[0]-lo[0]}" height="{hi[1]-lo[1]}" fill="{color}" stroke="white" stroke-width=".3"/>')
    for kx in dim['keys_x']:svg.append(f'<rect x="{kx-9}" y="{dim["keys_v"]-9}" width="18" height="18" fill="#d4dde6" stroke="white" stroke-width=".3"/>')
    svg.extend([f'<circle cx="{dim["knob_x"]}" cy="{dim["knob_v"]}" r="{dim["knob_d"]/2}" fill="#151618" stroke="white"/>',
       '<text x="0" y="119" fill="#ffffff" font-size="3.4" font-family="Arial">Orange LEFT side patch = USB-C1 trial wall opening (inward section, NOT frontal hole).</text>',
       '<text x="0" y="125" fill="#e8edf1" font-size="3.2" font-family="Arial">No real plugs, screw bosses, USB-UART port, I2C cable or verified LCD mounting.</text>',
       '</svg>'])
    return '\n'.join(svg)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--report-only',action='store_true',help='Only export JSON/SVG, no CadQuery required')
    p.add_argument('--variants',choices=['sharp','rounded','both'],default='both')
    args=p.parse_args()
    dim,ref,cfg=load();par=geometry_parameters(dim,ref,cfg)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    (args.out_dir/'rotated_case_experimental_report.json').write_text(json.dumps(par,indent=2)+'\n')
    (args.out_dir/'rotated_case_front_overview.svg').write_text(make_summary_svg(dim,par))
    print('Rev B rotated 180 degree case ALTERNATIVE (not physically validated)')
    print('Case:',dim['width'],'mm wide; visible aperture',par['display_aperture'])
    print('Left USB-C1 wall slot (trial):',par['left_usb_c1_service_slot_trial'])
    if not args.report_only:
        import cadquery as cq
        variants=['sharp','rounded'] if args.variants=='both' else [args.variants]
        for version in variants:
            shell=make_shell(dim,par,version,cfg)
            if not shell.isValid():raise RuntimeError(version+' STEP shell invalid')
            path=args.out_dir/f'spotify_desk_rotated180_{version}_experimental.step'
            cq.exporters.export(shell,str(path))
            print(f'{version} STEP:',path.name,'volume',round(shell.Volume(),1),'mm^3',len(shell.Faces()),'faces')
            assy=cq.Assembly(name='SpotifyDeskExperimentalRotated180_'+version)
            assy.add(shell,name='case_experimental',color=cq.Color(.20,.28,.35))
            cols={'lcd_full_assembled_bbox':cq.Color(.1,.44,.6),'usb_c1_socket':cq.Color(.9,.58,.24),'usb_uart_c2_socket':cq.Color(.78,.45,.21),'right_i2c_socket':cq.Color(.23,.73,.44)}
            for k,shape in make_reference_envelopes(dim,par,cfg).items():
                assy.add(shape,name=k,color=cols[k])
            assy.save(str(args.out_dir/f'spotify_desk_rotated180_{version}_envelope_assembly.step'))
    print('NOT FOR FABRICATION. Retained Rev B sharp/R5 manufacturer-independent CAD untouched.')

if __name__=='__main__':main()
