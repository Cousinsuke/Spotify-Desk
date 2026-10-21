#!/usr/bin/env python3
"""Compare bounding boxes extracted from Waveshare's official STEP to Rev B.

Pure standard library. Orientation follows FRONT of glass (+STEP Z), not a rear
photograph. The source STEP is not bundled. Cable-plug extensions are hypothetical.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import html

HERE=Path(__file__).resolve().parent

@dataclass(frozen=True)
class Box:
    name: str
    minimum: tuple[float,float,float]
    maximum: tuple[float,float,float]
    @property
    def center(self):
        return tuple((a+b)/2 for a,b in zip(self.minimum,self.maximum))


def transform(raw,reference,dim):
    """Map STEP XYZ to front-face X(right)/V(down)/W(inward), for flush glass.

    STEP +Z is the viewer-facing glass side; STEP +Y is visually upward.
    The exact position of installed glass relative to panel front is unresolved.
    """
    xlo,ylo,zlo,xhi,yhi,zhi=raw
    x0,y0,_,_,ymax,zfront=reference['step_coordinates']['front_touch_datum_box_xyz']
    sx,sv=dim['screen_origin']
    offset=reference['reference_alignment']['assumed_front_glass_w_mm']
    return Box('',(round(sx+xlo-x0,3),round(sv+ymax-yhi,3),round(offset+zfront-zhi,3)),
                   (round(sx+xhi-x0,3),round(sv+ymax-ylo,3),round(offset+zfront-zlo,3)))


def mapped_parts(reference,dim):
    return {name:Box(name,transform(data['box'],reference,dim).minimum,
                         transform(data['box'],reference,dim).maximum)
            for name,data in reference['parts'].items()}


def gap_x(a,b):
    return round(b.minimum[0]-a.maximum[0],3)


def overlap_3d(a,b):
    ext=[min(a.maximum[i],b.maximum[i])-max(a.minimum[i],b.minimum[i]) for i in range(3)]
    return tuple(round(x,3) for x in ext) if all(e>1e-7 for e in ext) else None


def study(dim,ref,usb_extension=14.0,i2c_extension=6.0):
    if usb_extension < 0 or i2c_extension < 0:
        raise ValueError('Cable extension must be non-negative')
    p=mapped_parts(ref,dim)
    knobs=dim['knob_x'],dim['knob_v']
    # Existing Rev B internal-packaging reference envelope is *assumed*.
    a={'encoder_size':13.2,'encoder_w_start':3.3,'encoder_w_depth':14.8}
    encoder=Box('encoder_body',(knobs[0]-6.6,knobs[1]-6.6,a['encoder_w_start']),
                (knobs[0]+6.6,knobs[1]+6.6,a['encoder_w_start']+a['encoder_w_depth']))
    usb=p['usb_type_c1']; i2c=p['i2c_4pin_socket']
    # Extending the bare socket's outward face by a trial distance. The W/V
    # ranges are deliberately copied from the socket body, NOT a mating plug.
    usb_probe=Box('hypothetical_usb_cable',
                 (usb.maximum[0],usb.minimum[1],usb.minimum[2]),
                 (usb.maximum[0]+usb_extension,usb.maximum[1],usb.maximum[2]))
    i2c_probe=Box('hypothetical_i2c_cable',
                 (i2c.minimum[0]-i2c_extension,i2c.minimum[1],i2c.minimum[2]),
                 (i2c.minimum[0],i2c.maximum[1],i2c.maximum[2]))
    # Assumed 3mm wall only. These are NOT accurate rounded-case or aperture tests.
    innerleft=dim['wall_assumed']
    inner_right=dim['width']-innerleft
    overlaps={'usb_to_encoder':overlap_3d(usb_probe,encoder),
              'i2c_to_encoder':overlap_3d(i2c_probe,encoder)}
    stands=[p[k].center for k in p if k.startswith('standoff_')]
    xs=sorted(set(round(x[0],3) for x in stands))
    vs=sorted(set(round(x[1],3) for x in stands))
    assert len(xs)==2 and len(vs)==2
    return {
        'physical_fit_verified':False,
        'basis':'Waveshare STEP solid bounding boxes for assembled connectors, hypothetical mating cables',
        'dimensions_mm':{'case_width':dim['width'],'front_length':dim['front_face_length'],
                         'complete_step_depth':round(p['full_assembly'].maximum[2]-p['full_assembly'].minimum[2],3),
                         'step_standoff_pitch_x':round(xs[1]-xs[0],3),
                         'step_standoff_pitch_v':round(vs[1]-vs[0],3)},
        'front_view_orientation':{'left':'4-pin I2C and other PH peripheral sockets',
                                 'right':'USB Type-C1 (USB) and Type-C2 (USB-UART)'},
        'mapped_components':{k:{'min':v.minimum,'max':v.maximum} for k,v in p.items()},
        'encoder_assumed':{'min':encoder.minimum,'max':encoder.maximum},
        'trial_usb_extension_mm':usb_extension,'trial_i2c_extension_mm':i2c_extension,
        'probes':{'usb':{'min':usb_probe.minimum,'max':usb_probe.maximum},
                  'i2c':{'min':i2c_probe.minimum,'max':i2c_probe.maximum}},
        'gap_usb_socket_to_encoder_body_x_mm':gap_x(usb,encoder),
        'gap_i2c_socket_to_nominal_left_inner_wall_mm':round(i2c.minimum[0]-innerleft,3),
        'trial_usb_encoder_overlap_xyz_mm':overlaps['usb_to_encoder'],
        'trial_i2c_encoder_overlap_xyz_mm':overlaps['i2c_to_encoder'],
        'trial_i2c_inner_left_margin_mm':round(i2c_probe.minimum[0]-innerleft,3),
        'trial_usb_inner_right_margin_mm':round(inner_right-usb_probe.maximum[0],3),
        'caveats':['STEP bare socket bounds are not the mating plug or cable strain relief',
                   'Encoder W depth and panel seating are existing unmeasured assumptions',
                   'Touch model has front/rear placement but no known case mounting datum',
                   'Board model 2023 revision could differ from shipped touch SKU 25948',
                   'The case, right/left wall port openings and electrical routing are not designed',
                   'Sharp inner wall approximation; rounded R5 locally varies']
    }


def svg_layout(dim,results):
    # Front-view vector diagram, derived from STEP instance bounding boxes.
    sx,sv=dim['screen_origin'];sw,sh=dim['screen_outer']
    p=results['mapped_components']
    parts=[('usb_type_c1','#f1a94e','USB'),('usb_type_c2','#f1a94e','UART'),
           ('i2c_4pin_socket','#6fdcb0','I2C')]
    els=[f'<rect x="0" y="0" width="{dim["width"]}" height="{dim["front_face_length"]}" fill="#242b39" stroke="#b4bdc9" stroke-width=".6"/>',
         f'<rect x="{sx}" y="{sv}" width="{sw}" height="{sh}" fill="#142936" stroke="#3ea0bf" stroke-width=".6"/>']
    for name,color,label in parts:
        r=p[name];x1,v1,_=r['min'];x2,v2,_=r['max']
        els.append(f'<rect x="{x1}" y="{v1}" width="{x2-x1:.3f}" height="{v2-v1:.3f}" fill="{color}" stroke="#fff" stroke-width=".3"/>')
        xlab=119 if name.startswith('usb') else 18
        ylab=(v1+v2)/2
        els.append(f'<text x="{xlab}" y="{ylab+1}" fill="{color}" font-family="Arial" font-size="3.2">{label}</text>')
    for k in ['standoff_top_left','standoff_top_right','standoff_bottom_left','standoff_bottom_right']:
        r=p[k];x=(r['min'][0]+r['max'][0])/2;v=(r['min'][1]+r['max'][1])/2
        els.append(f'<circle cx="{x}" cy="{v}" r="2.75" fill="none" stroke="#eeee7f" stroke-width=".7"/>')
    for kx in dim['keys_x']:
        els.append(f'<rect x="{kx-9}" y="{dim["keys_v"]-9}" width="18" height="18" fill="#d3dde8" stroke="#eff5fa" stroke-width=".4"/>')
    els.append(f'<circle cx="{dim["knob_x"]}" cy="{dim["knob_v"]}" r="{dim["knob_d"]/2}" fill="#0f1118" stroke="#ffffff" stroke-width=".7"/>')
    els.append(f'<rect x="{dim["knob_x"]-6.6}" y="{dim["knob_v"]-6.6}" width="13.2" height="13.2" fill="none" stroke="#f6aa50" stroke-dasharray="2,1" stroke-width=".5"/>')
    els.append('<text x="0" y="-8" font-size="4" fill="#efefef" font-family="Arial">Rev B FRONT GLASS VIEW: USB right, I2C left</text>')
    els.append('<text x="0" y="120" font-size="3.1" fill="#d8e5ef" font-family="Arial">Manufacturer STEP socket bodies &amp; standoffs; positions approximately registered to Rev B.</text>')
    els.append('<text x="0" y="126" font-size="3.1" fill="#d8e5ef" font-family="Arial">No mating cable, fastener geometry or hardware fit established. Blue LCD outline 106.1x67.8mm.</text>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -15 165 148" width="1155" height="1036">\n'+'\n'.join(els)+'\n</svg>\n'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dimensions',type=Path,default=HERE/'dimensions.json')
    ap.add_argument('--step-reference',type=Path,default=HERE/'waveshare_step_reference.json')
    ap.add_argument('--usb-reach-mm',type=float,default=14.0)
    ap.add_argument('--i2c-reach-mm',type=float,default=6.0)
    ap.add_argument('--out-dir',type=Path)
    args=ap.parse_args()
    dim=json.loads(args.dimensions.read_text(encoding='utf-8'))
    ref=json.loads(args.step_reference.read_text(encoding='utf-8'))
    res=study(dim,ref,args.usb_reach_mm,args.i2c_reach_mm)
    print('WAVESHARE STEP FRONT-VIEW REFERENCE (actual socket solids; CABLES ASSUMED)')
    print('Manufacturer model: USB and UART at display right; 4-pin I2C at display left.')
    print('Full model front-to-back extent: %.3f mm'%res['dimensions_mm']['complete_step_depth'])
    print('Nominal standoff pitch: %.3f x %.3f mm'%(res['dimensions_mm']['step_standoff_pitch_x'],res['dimensions_mm']['step_standoff_pitch_v']))
    print('USB housing -> encoder body X gap: %.3f mm (body placement assumed)'%res['gap_usb_socket_to_encoder_body_x_mm'])
    print('I2C housing -> nominal left case INNER wall: %.3f mm'%res['gap_i2c_socket_to_nominal_left_inner_wall_mm'])
    print('USB plug outward trial reach %.1f mm: simulated encoder overlap %s'%(args.usb_reach_mm,res['trial_usb_encoder_overlap_xyz_mm']))
    print('I2C plug outward trial reach %.1f mm: nominal inner-left wall margin %.3f mm'%(args.i2c_reach_mm,res['trial_i2c_inner_left_margin_mm']))
    print('NOT VERIFIED: plug mating geometry, cable turns, actual installed board offset, enclosure service openings.')
    if args.out_dir:
        args.out_dir.mkdir(parents=True,exist_ok=True)
        (args.out_dir/'waveshare_step_comparison.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
        (args.out_dir/'waveshare_step_front_overlay.svg').write_text(svg_layout(dim,res),encoding='utf-8')
        print('Wrote:',args.out_dir)

if __name__=='__main__':main()
