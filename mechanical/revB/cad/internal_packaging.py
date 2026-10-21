#!/usr/bin/env python3
"""Rev B parametric X/V/inward-W envelope study (no verified physical fit).

Python stdlib only. Reports exact intersections between conceptual rectangular
boxes aligned with the inclined face, and possible breaches of a nominal 3mm
sharp-wedge inner envelope. These are conservative, *unmeasured* shapes.
"""
from __future__ import annotations
from dataclasses import dataclass
import argparse
import itertools
import json
import math
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent

@dataclass(frozen=True)
class Envelope:
    name: str
    minimum: tuple[float, float, float]  # front X, down-front V, inward W
    size: tuple[float, float, float]
    source: str  # catalog, source CAD, or ASSUMED

    @property
    def maximum(self):
        return tuple(a + b for a,b in zip(self.minimum,self.size))


def boxes(dim, cfg):
    sx,sv = dim['screen_origin']; sw,sh = dim['screen_outer']
    keyv = dim['keys_v']; cx,cv = dim['knob_x'],dim['knob_v']
    a = cfg['assumptions']
    out=[Envelope('screen_module', (sx,sv,a['screen_inward_start']),
                  (sw,sh,a['screen_depth']), 'Waveshare outer XY; depth/offset ASSUMED')]
    for label,kx in zip(('previous','play_pause','next'),dim['keys_x']):
        out.append(Envelope('mx_'+label,
                    (kx-a['switch_size']/2,keyv-a['switch_size']/2,a['switch_inward_start']),
                    (a['switch_size'],a['switch_size'],a['switch_depth']),
                    'nominal MX XY; depth/offset ASSUMED'))
    out.append(Envelope('encoder_body',
        (cx-a['encoder_size']/2,cv-a['encoder_size']/2,a['encoder_inward_start']),
        (a['encoder_size'],a['encoder_size'],a['encoder_depth']),
        'nominal Bourns PEC11 XY; inward depth ASSUMED'))
    out.append(Envelope('encoder_terminal_envelope',
        (cx-a['encoder_size']/2,cv-a['encoder_size']/2,a['encoder_inward_start']+a['encoder_depth']),
        (a['encoder_size'],a['encoder_size'],a['encoder_terminal_depth']),
        'entire terminal bounding prism ASSUMED; not a real contact layout'))
    out.append(Envelope('right_i2c_cable',
        (sx+sw,a['i2c_v_start'],a['i2c_inward_start']),
        (a['i2c_extension'],a['i2c_v_length'],a['i2c_inward_depth']),
        'position, length, bend, depth all ASSUMED'))
    out.append(Envelope('left_usb_cable',
        (sx-a['usb_extension'],a['usb_v_start'],a['usb_inward_start']),
        (a['usb_extension'],a['usb_v_length'],a['usb_inward_depth']),
        'location, length, bend, depth all ASSUMED'))
    return out


def overlap(a:Envelope,b:Envelope):
    extents=[min(a.maximum[i],b.maximum[i])-max(a.minimum[i],b.minimum[i]) for i in range(3)]
    return tuple(round(v,3) for v in extents) if all(v>1e-7 for v in extents) else None


def world_yz(v,w,dim):
    ang=math.radians(dim['face_tilt_deg'])
    run=dim['front_face_length']*math.cos(ang)
    height=dim['front_chin']+dim['front_face_length']*math.sin(ang)
    return (run-v*math.cos(ang)+w*math.sin(ang),
            height-v*math.sin(ang)-w*math.cos(ang))


def enclosure_margin(box:Envelope, dim):
    """Minimum signed boundary clearance to hypothetical sharp wedge inner wall.

    Applies to component bounding boxes only. Does not model shell apertures,
    rounded R5 corner setbacks, cables curved in 3D, clips or fasteners.
    """
    ang=math.radians(dim['face_tilt_deg'])
    run=dim['front_face_length']*math.cos(ang)
    height=dim['front_chin']+dim['front_face_length']*math.sin(ang)
    depth=run+dim['rear_roof']
    poly=((0,0),(depth,0),(depth,height),(run,height),(0,dim['front_chin']))
    wall=dim['wall_assumed']
    margin=min(box.minimum[0]-wall,dim['width']-wall-box.maximum[0])
    for v in (box.minimum[1],box.maximum[1]):
        for w in (box.minimum[2],box.maximum[2]):
            y,z=world_yz(v,w,dim)
            for (y1,z1),(y2,z2) in zip(poly,poly[1:]+poly[:1]):
                edge=math.hypot(y2-y1,z2-z1)
                signed=((y2-y1)*(z-z1)-(z2-z1)*(y-y1))/edge-wall
                margin=min(margin,signed)
    return round(margin,3)


def study(dim,cfg):
    parts=boxes(dim,cfg)
    pairs=[]
    for a,b in itertools.combinations(parts,2):
        intersection=overlap(a,b)
        if intersection:
            pairs.append({'a':a.name,'b':b.name,'intersection_xyz_mm':intersection,
                          'verified_collision':False})
    margins=[{'name':box.name,'min_nominal_inner_case_margin_mm':enclosure_margin(box,dim),
              'needs_review':enclosure_margin(box,dim)<0} for box in parts]
    return {'units':'mm','audit_kind':'rectangular front-plane 3D reference envelopes ONLY',
            'physical_fit_verified':False,
            'case_width_mm':dim['width'],
            'screen_centered_key_row_mm':round(sum(dim['keys_x'])/len(dim['keys_x'])-
                      (dim['screen_origin'][0]+dim['screen_outer'][0]/2),6),
            'envelopes':[box.__dict__ for box in parts],
            'pairwise_overlaps':pairs,'sharp_case_inner_boundary_margins':margins,
            'not_modelled':['right I2C actual plug shape and rear-plane routing',
                  'USB physical port/plug and service opening',
                  'screen PCB rear structures and screw bores',
                  'physical MX locking tabs, pins, supports and keycaps',
                  'knob grub screw, M7 nut/washer and press travel',
                  'AW9523B real placement, wiring, clips and spacers',
                  'Wi-Fi antenna actual restricted area',
                  'bottom hatch/screw bosses and R5 true shell intersection',
                  'electrical compatibility or firmware']}


def write_scad_params(dim,cfg):
    a=cfg['assumptions']
    values={
        'W':dim['width'],'FACE':dim['front_face_length'],
        'ANGLE':dim['face_tilt_deg'],'CHIN':dim['front_chin'],'ROOF':dim['rear_roof'],
        'WALL':dim['wall_assumed'],'SCREEN_X':dim['screen_origin'][0],
        'SCREEN_V':dim['screen_origin'][1],
        'SCREEN_W':dim['screen_outer'][0],'SCREEN_H':dim['screen_outer'][1],
        'SCREEN_IN':a['screen_inward_start'],'SCREEN_DEPTH':a['screen_depth'],
        'KEY_X':dim['keys_x'],'KEY_V':dim['keys_v'],
        'SWITCH_SIZE':a['switch_size'],'SWITCH_IN':a['switch_inward_start'],
        'SWITCH_DEPTH':a['switch_depth'],
        'KNOB_X':dim['knob_x'],'KNOB_V':dim['knob_v'],
        'KNOB_D':dim['knob_d'],'ENCODER_SIZE':a['encoder_size'],
        'ENCODER_IN':a['encoder_inward_start'],'ENCODER_DEPTH':a['encoder_depth'],
        'TERMINAL_DEPTH':a['encoder_terminal_depth'],
        'I2C_EXTENSION':a['i2c_extension'],'I2C_V':a['i2c_v_start'],
        'I2C_V_LEN':a['i2c_v_length'],'I2C_IN':a['i2c_inward_start'],
        'I2C_DEPTH':a['i2c_inward_depth'],
        'USB_EXTENSION':a['usb_extension'],'USB_V':a['usb_v_start'],
        'USB_V_LEN':a['usb_v_length'],'USB_IN':a['usb_inward_start'],
        'USB_DEPTH':a['usb_inward_depth'],
        'FIX_PITCH_X':dim['display_nominal_fixing_centers'][0],
        'FIX_PITCH_V':dim['display_nominal_fixing_centers'][1],
        'FIXING_MARKER_D':a['fixing_marker_diameter'],
        'AW_BOARD_SIZE':a['aw_board_size'],
        'AW_BOARD_WORLD_MIN':a['aw_board_world_min'],
        'HATCH_CLEARANCE_Z':a['hatch_clearance_height'],
    }
    lines=['// AUTO-GENERATED from dimensions.json + internal_packaging_assumptions.json.',
           '// Assumed geometry: NOT a manufacturer fit specification.','']
    for k,v in values.items():
        lines.append(k+' = '+json.dumps(v,separators=(',',':'))+';')
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dimensions',type=Path,default=HERE/'dimensions.json')
    p.add_argument('--assumptions',type=Path,default=HERE/'internal_packaging_assumptions.json')
    p.add_argument('--i2c-extension',type=float,default=None,help='Override assumed right cable reach, mm')
    p.add_argument('--usb-extension',type=float,default=None,help='Override assumed left cable reach, mm')
    p.add_argument('--out-dir',type=Path,help='Write report + standalone OpenSCAD view to this folder')
    p.add_argument('--verify-defaults',action='store_true',help='Fail if checked-in SCAD parameters are stale')
    args=p.parse_args()
    dim=json.loads(args.dimensions.read_text(encoding='utf-8'))
    cfg=json.loads(args.assumptions.read_text(encoding='utf-8'))
    if args.i2c_extension is not None:cfg['assumptions']['i2c_extension']=args.i2c_extension
    if args.usb_extension is not None:cfg['assumptions']['usb_extension']=args.usb_extension
    for field,val in cfg['assumptions'].items():
        if isinstance(val,(int,float)) and val < 0:
            p.error(f'{field} must be >= 0')
    param_text=write_scad_params(dim,cfg)
    if args.verify_defaults and param_text!=(HERE/'internal_packaging_params.scad').read_text(encoding='utf-8'):
        p.error('SCAD parameters no longer match JSON sources: regenerate before committing')
    result=study(dim,cfg)
    print('Rev B 3D RECTANGULAR ENVELOPE STUDY (unmeasured parts; NOT physical fit verified)')
    print('Sharp/R5 original cases remain unchanged; sharp-profile reference bounds only.')
    print('Case width:',dim['width'],'mm. I2C assumption:',cfg['assumptions']['i2c_extension'],
          'mm; USB assumption:',cfg['assumptions']['usb_extension'],'mm')
    for c in result['pairwise_overlaps']:
        print('POSSIBLE OVERLAP:',c['a'],'vs',c['b'], 'X/V/W:',c['intersection_xyz_mm'])
    if not result['pairwise_overlaps']:print('No overlap among these simplified boxes.')
    for c in result['sharp_case_inner_boundary_margins']:
        if c['needs_review']:
            print('NOMINAL CASE INNER-BOUNDARY ENCROACHMENT:',c['name'],
                  c['min_nominal_inner_case_margin_mm'],'mm (opening/re-route may be intended)')
    print('No standoff, screw, connector, antenna, clip or physical fit verification.')
    if args.out_dir:
        args.out_dir.mkdir(parents=True,exist_ok=True)
        (args.out_dir/'internal_packaging_params.scad').write_text(param_text,encoding='utf-8')
        shutil.copyfile(HERE/'internal_packaging_view.scad',args.out_dir/'internal_packaging_view.scad')
        (args.out_dir/'internal_packaging_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print('Wrote SCAD view + parameters + JSON report to:',args.out_dir)

if __name__=='__main__':main()
