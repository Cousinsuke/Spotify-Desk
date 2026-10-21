#!/usr/bin/env python3
"""Side-by-side physical 0/180-degree Waveshare STEP front-view orientation study.

Uses original source measurements, never mutates the original sharp/R5 Rev B
CAD or assumes any cable/plug geometry is manufacturer-certified.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from manufacturer_fit_compare import Box, mapped_parts, overlap_3d

HERE = Path(__file__).resolve().parent

def rotated_parts(dim: dict, ref: dict, rotation_deg: int):
    """Rotate assembled LCD 180 in its *front plane*, leaving glass outward.

    Local X right and V downward, W inward. This is NOT a rear-face flip.
    """
    if rotation_deg not in (0, 180):
        raise ValueError('Only 0 and 180 degree orientations are supported')
    original = mapped_parts(ref, dim)
    if rotation_deg == 0:
        return original
    sx,sv = dim['screen_origin']; sw,sh = dim['screen_outer']
    xsum, vsum = 2*sx+sw, 2*sv+sh
    return {
        name: Box(name,
                  (round(xsum-box.maximum[0],3),round(vsum-box.maximum[1],3),box.minimum[2]),
                  (round(xsum-box.minimum[0],3),round(vsum-box.minimum[1],3),box.maximum[2]))
        for name,box in original.items()
    }

def display_aperture(dim, rotation_deg):
    """The nominal visible pixel window, not a toleranced production opening."""
    if rotation_deg not in (0,180):
        raise ValueError('Only 0 and 180 degree orientations supported')
    sx,sv=dim['screen_origin']; sw,sh=dim['screen_outer']
    ox,ov=dim['display_visible_offset']; vw,vh=dim['display_visible']
    if rotation_deg==180:
        ox,ov=sw-ox-vw,sh-ov-vh
    return {'x':round(sx+ox,3),'v':round(sv+ov,3),
            'width':vw,'height':vh}

def probe(socket: Box, side: str, reach: float, name: str):
    """A hypothetical straight prism projected from the socket outer edge."""
    if reach < 0: raise ValueError('Cable extension cannot be negative')
    if side=='left':
        return Box(name,(round(socket.minimum[0]-reach,3),socket.minimum[1],socket.minimum[2]),
                   (socket.minimum[0],socket.maximum[1],socket.maximum[2]))
    if side=='right':
        return Box(name,(socket.maximum[0],socket.minimum[1],socket.minimum[2]),
                   (round(socket.maximum[0]+reach,3),socket.maximum[1],socket.maximum[2]))
    raise ValueError(side)

def compare(dim: dict,ref: dict,rotation_deg: int,
            usb_reach_mm:float=14.,i2c_reach_mm:float=6.):
    if min(usb_reach_mm,i2c_reach_mm)<0: raise ValueError('Trial reaches must be nonnegative')
    p=rotated_parts(dim,ref,rotation_deg)
    usb_side='left' if rotation_deg==180 else 'right'
    i2c_side='right' if rotation_deg==180 else 'left'
    usb=p['usb_type_c1'];uart=p['usb_type_c2'];i2c=p['i2c_4pin_socket']
    usb_probe=probe(usb,usb_side,usb_reach_mm,'trial_usb_cable')
    i2c_probe=probe(i2c,i2c_side,i2c_reach_mm,'trial_i2c_cable')
    kx=dim['knob_x'];kv=dim['knob_v']
    # Existing unmeasured encoder-body placement from previous Rev B study.
    encoder=Box('assumed_encoder_body',(kx-6.6,kv-6.6,3.3),(kx+6.6,kv+6.6,18.1))
    left_wall=dim['wall_assumed'];right_wall=dim['width']-left_wall
    left_socket=p['usb_type_c1'] if rotation_deg==180 else p['i2c_4pin_socket']
    left_probe=usb_probe if rotation_deg==180 else i2c_probe
    right_socket=p['i2c_4pin_socket'] if rotation_deg==180 else p['usb_type_c1']
    right_probe=i2c_probe if rotation_deg==180 else usb_probe
    window=display_aperture(dim,rotation_deg)
    original_window=display_aperture(dim,0)
    stands=[p[k].center for k in p if k.startswith('standoff_')]
    xvals=sorted(set(round(x,3) for x,y,w in stands))
    vvals=sorted(set(round(v,3) for x,v,w in stands))
    return {'rotation_deg':rotation_deg,'physical_fit_verified':False,
            'usb_front_side':usb_side,'i2c_front_side':i2c_side,
            'windows_power_source':'main USB Type-C1 nominal 5V input; electrical accessibility untested',
            'case_width_mm':dim['width'],
            'display_window_nominal':window,
            'window_shift_vs_original_mm':{'x':round(window['x']-original_window['x'],3),
                                           'v':round(window['v']-original_window['v'],3)},
            'visible_screen_to_keycap_top_gap_mm':round(dim['keys_v']-9-(window['v']+window['height']),3),
            'mounting_pitch_x_v_mm':[round(xvals[1]-xvals[0],3),round(vvals[1]-vvals[0],3)],
            'usb_type_c1':{'min':usb.minimum,'max':usb.maximum},
            'usb_uart_type_c2':{'min':uart.minimum,'max':uart.maximum},
            'i2c_4pin':{'min':i2c.minimum,'max':i2c.maximum},
            'mapped_parts':{name:{'min':part.minimum,'max':part.maximum} for name,part in p.items()},
            'probes':{'usb':{'min':usb_probe.minimum,'max':usb_probe.maximum},
                      'i2c':{'min':i2c_probe.minimum,'max':i2c_probe.maximum}},
            'trial_usb_reach_mm':usb_reach_mm,'trial_i2c_reach_mm':i2c_reach_mm,
            'usb_probe_to_encoder_overlap_xyz_mm':overlap_3d(usb_probe,encoder),
            'i2c_probe_to_encoder_overlap_xyz_mm':overlap_3d(i2c_probe,encoder),
            'nominal_left_housing_to_inner_wall_x_mm':round(left_socket.minimum[0]-left_wall,3),
            'nominal_right_housing_to_inner_wall_x_mm':round(right_wall-right_socket.maximum[0],3),
            'trial_left_cable_to_inner_wall_x_mm':round(left_probe.minimum[0]-left_wall,3),
            'trial_right_cable_to_inner_wall_x_mm':round(right_wall-right_probe.maximum[0],3),
            'trial_right_socket_to_encoder_x_mm':round(encoder.minimum[0]-right_socket.maximum[0],3),
            'assumed_encoder_body':{'min':encoder.minimum,'max':encoder.maximum},
            'warnings':['Mating cables, bend radii and side-wall port cutouts are not modelled',
                        'Rotated screen aperture is relocated; the existing CAD aperture is not changed',
                        'Software 180 degree display and GT911 touch mapping untested on ESP32 hardware',
                        'Actual board revision/port power behaviour/antenna and screw hardware unverified',
                        'Nominal 3mm inner wall is not a designed shell opening',
                        'No print or physical fit claim, retained sharp and R5 STEP files untouched']}

def touch_rotate_180(x:int,y:int,width:int=800,height:int=480):
    """Conceptual touch mapping in pixel coordinates, not GT911 driver code."""
    if not(0<=x<width and 0<=y<height):raise ValueError('Coordinate out of bounds')
    return width-1-x,height-1-y

def make_svg(dim,results):
    """Static front-view diagram comparing the physical orientations."""
    chunks=[]
    cw=dim['width'];ch=dim['front_face_length']
    for idx,result in enumerate(results):
        offset=idx*(cw+24)
        t=f'{result["rotation_deg"]}°'
        s=[f'<g transform="translate({offset:.3f} 0)">',
           f'<text x="0" y="-10" fill="#f7fafc" font-family="Arial" font-size="4.8">Physical {t}: USB {result["usb_front_side"]} / I2C {result["i2c_front_side"]}</text>',
           f'<rect x="0" y="0" width="{cw}" height="{ch}" fill="#202936" stroke="#c7d4df" stroke-width=".7"/>',
           f'<rect x="{dim["screen_origin"][0]}" y="{dim["screen_origin"][1]}" width="{dim["screen_outer"][0]}" height="{dim["screen_outer"][1]}" fill="#163f52" stroke="#66c9e9" stroke-width=".6"/>']
        win=result['display_window_nominal']
        s.append(f'<rect x="{win["x"]}" y="{win["v"]}" width="{win["width"]}" height="{win["height"]}" fill="#1f6a87" stroke="#9ee1fa" stroke-width=".4"/>')
        for key,color,label in [('usb_type_c1','#f49a46','USB'),('usb_uart_type_c2','#f49a46','UART'),('i2c_4pin','#6ce5ae','I2C')]:
            part=result[key];a=part['min'];b=part['max']
            s.append(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]:.3f}" height="{b[1]-a[1]:.3f}" fill="{color}" stroke="#fff" stroke-width=".5"/>')
            lx=18 if result['rotation_deg']==180 and key.startswith('usb') else (120 if result['rotation_deg']==0 and key.startswith('usb') else (120 if result['rotation_deg']==180 else 20))
            s.append(f'<text x="{lx}" y="{(a[1]+b[1])/2:.2f}" font-family="Arial" font-size="3.6" fill="{color}">{label}</text>')
        for key in [k for k in result['mapped_parts'] if k.startswith('standoff_')]:
            part=result['mapped_parts'][key];a=part['min'];b=part['max']; cx=(a[0]+b[0])/2;cv=(a[1]+b[1])/2
            s.append(f'<circle cx="{cx:.3f}" cy="{cv:.3f}" r="2.75" stroke="#f4db83" stroke-width=".6" fill="none"/>')
        for x in dim['keys_x']:
            s.append(f'<rect x="{x-9}" y="{dim["keys_v"]-9}" width="18" height="18" fill="#edf2f8" stroke="#f7f9fd" stroke-width=".5"/>')
        s.append(f'<circle cx="{dim["knob_x"]}" cy="{dim["knob_v"]}" r="{dim["knob_d"]/2}" fill="#0e1016" stroke="#fff" stroke-width=".8"/>')
        s.append(f'<text x="0" y="122" font-family="Arial" font-size="3.6" fill="#ccdbe8">Window vertical change: {result["window_shift_vs_original_mm"]["v"]:+.2f} mm; nominal visible-to-key gap {result["visible_screen_to_keycap_top_gap_mm"]:.2f} mm</text>')
        s.append('</g>');chunks+=s
    total=2*(cw+24)-24
    chunks.append(f'<text x="0" y="133" font-family="Arial" font-size="3.9" fill="#cbd5df">Based on measured 2023 Waveshare STEP socket housings and existing Rev B positions. No physical plugs, cables or port cuts.</text>')
    chunks.append(f'<text x="0" y="140" font-family="Arial" font-size="3.8" fill="#f9b35e">Both orientations are concepts. Firmware display and touch 180° correction is required and untested.</text>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -18 340 166" width="1360" height="664"><title>Rev B Waveshare physical normal versus rotated-180 orientation</title><rect x="-4" y="-18" width="340" height="166" fill="#15202b"/>'+''.join(chunks)+'</svg>\n'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dimensions',type=Path,default=HERE/'dimensions.json')
    ap.add_argument('--step-reference',type=Path,default=HERE/'waveshare_step_reference.json')
    ap.add_argument('--usb-reach-mm',type=float,default=14.)
    ap.add_argument('--i2c-reach-mm',type=float,default=6.)
    ap.add_argument('--out-dir',type=Path)
    args=ap.parse_args()
    dim=json.loads(args.dimensions.read_text(encoding='utf-8'))
    ref=json.loads(args.step_reference.read_text(encoding='utf-8'))
    scenarios=[compare(dim,ref,r,args.usb_reach_mm,args.i2c_reach_mm) for r in (0,180)]
    print('Manufacturer STEP physical orientation study; bare socket boxes, unmeasured plugs.')
    for r in scenarios:
        print(f'\nPhysical {r["rotation_deg"]}°: USB {r["usb_front_side"]}, I2C {r["i2c_front_side"]}')
        print(f'  Trial left cable to nominal inner wall: {r["trial_left_cable_to_inner_wall_x_mm"]:+.3f} mm')
        print(f'  Trial right cable to nominal inner wall: {r["trial_right_cable_to_inner_wall_x_mm"]:+.3f} mm')
        print(f'  Trial USB-to-encoder overlap: {r["usb_probe_to_encoder_overlap_xyz_mm"]}')
        print(f'  Trial I2C-to-encoder overlap: {r["i2c_probe_to_encoder_overlap_xyz_mm"]}')
        print(f'  Display window V shift: {r["window_shift_vs_original_mm"]["v"]:+.2f} mm')
    print('\nNot fabrication approved: actual connectors/cables, mount and firmware rotation untested.')
    if args.out_dir:
        args.out_dir.mkdir(parents=True,exist_ok=True)
        (args.out_dir/'orientation_180_comparison.json').write_text(json.dumps(scenarios,indent=2)+'\n',encoding='utf-8')
        (args.out_dir/'orientation_180_comparison.svg').write_text(make_svg(dim,scenarios),encoding='utf-8')
        print('Wrote:',args.out_dir)

if __name__=='__main__':main()
