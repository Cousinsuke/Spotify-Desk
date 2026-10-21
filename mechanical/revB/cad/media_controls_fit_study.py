#!/usr/bin/env python3
"""Independent Rev B rounded, physically rotated 180 deg media keycap and MX mount study.

Units mm. Uses nominal Cherry MX mounting/motion dimensions and deliberately
ASSUMED keycap section, not the actual Krome Keycaps product CAD. Original
Rev B and prior rotated shell assets are never overwritten. Python stdlib
for JSON/SVG; CadQuery/Shapely for experimental step assembly exports.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
from html import escape
from rotated_case_prototype import load, geometry_parameters, make_shell

HERE=Path(__file__).resolve().parent

def assumptions(path=None):
    return json.loads(Path(path or HERE/'keycap_mount_assumptions.json').read_text(encoding='utf-8'))


def study(dim, ref, casecfg, cap):
    p=geometry_parameters(dim,ref,casecfg)
    width=cap['cap_width_mm']; well=cap['well_width_mm']
    plate=cap['switch_plate_top_inward_mm']
    rest=-cap['cap_rest_above_skin_mm']; travel=cap['switch_total_travel_nominal_mm']
    deep=cap['cap_depth_assumed_mm']
    if not (0 < width < well < cap['well_outer_support_width_mm'] < dim['key_pitch']):
        raise ValueError('Cap/well/reinforcement must be positive, separated, and fit 30mm key pitch')
    if not(0 < cap['switch_plate_aperture_mm'] < cap['switch_flange_width_nominal_mm'] < well):
        raise ValueError('Switch flange and well must clear the mounting plate opening')
    if plate <= cap['well_outer_support_width_mm']*0 or cap['switch_plate_thickness_mm']<=0:
        raise ValueError('Plate requires positive depth and thickness')
    clearance=plate-(rest+deep+travel)
    if clearance < 0: raise ValueError('Keycap skirt would pass through switch-retaining plate on full stroke')
    if cap['cap_rest_above_skin_mm'] < 0 or travel<=0:raise ValueError('Invalid travel and external cap location')
    shellwall=casecfg['case_wall_mm']
    if plate <= shellwall+1:raise ValueError('Recessed plate must sit beyond 3mm face thickness')
    outer=cap['well_outer_support_width_mm']
    lowerface=dim['keys_v']+outer/2
    if lowerface >= dim['front_face_length']-3:raise ValueError('Too close to chin boundary')
    w=dim['screen_outer'][1]
    glass_end=dim['screen_origin'][1]+w
    support_begin=dim['keys_v']-outer/2
    if support_begin <= glass_end:raise ValueError('Recess support may intrude into full LCD module projection')
    stroke=[{'position':'REST','cap_top_w_mm':rest,'cap_skirt_bottom_w_mm':round(rest+deep,3)},
            {'position':'FULL_PRESS','cap_top_w_mm':round(rest+travel,3),'cap_skirt_bottom_w_mm':round(rest+travel+deep,3)}]
    stemtop=plate-cap['switch_top_above_plate_assumed_mm']-cap['stem_top_above_switch_housing_mm']
    return {'status':'IDEALISED MX RECESSED KEYCAP STUDY; NOT VERIFIED PHYSICAL COMPONENT FIT',
            'physical_fit_verified':False,'outer_case_size_mm':[dim['width'],dim['depth'],dim['height']],
            'case_variant':'rounded R5 derived rotated-180 experimental only',
            'key_centres_x_mm':dim['keys_x'],'key_center_v_mm':dim['keys_v'],
            'cap_width_mm':width,'keycap_body_depth_assumed_mm':deep,
            'well_width_mm':well,'lateral_clearance_each_side_mm':round((well-width)/2,3),
            'support_collar_outer_width_mm':outer,
            'plate_width_mm':outer,'plate_square_cutout_mm':cap['switch_plate_aperture_mm'],
            'plate_top_w_mm':plate,'plate_thickness_mm':cap['switch_plate_thickness_mm'],
            'unpressed_cap_exterior_height_mm':cap['cap_rest_above_skin_mm'],
            'switch_nominal_total_travel_mm':travel,
            'keycap_rest_and_pressed':stroke,
            'cap_skirt_to_plate_gap_at_full_press_mm':round(clearance,3),
            'switch_stem_tip_at_rest_w_assumed_mm':round(stemtop,3),
            'keycap_stem_tip_overlap_assumed_mm':round(stemtop-rest,3),
            'min_support_to_full_lcd_v_gap_mm':round(support_begin-glass_end,3),
            'knob':{'x':dim['knob_x'],'v':dim['knob_v'],'diameter_mm':cap['knob_diameter_mm'],
                    'above_skin_assumed_mm':cap['knob_exterior_height_assumed_mm']},
            'rotated_window':p['display_aperture'],
            'assumptions_unverified':['cap sidewall, internal socket and MX cross stem engagement',
                'MX housing/clip geometry, tolerance after printing and local plate retention',
                'full 4mm stroke depends on exact MX model and keycap profile',
                'switch solder lugs, PCB/backside wiring, collared well assembly/print supports',
                'knob attachment screw, washer/nut, push travel and shaft engagement',
                'real USB-C1 male plug, four-pin I2C harness and mainboard rear clearance']}


def icon_svg(name,fill='#F6F7FB',px=512):
    # Standalone, ORIGINAL custom print master SVG with matching 1U white media glyphs.
    # 100x100 viewbox. No fonts, bitmaps, brand logo, SVG external href, or raster dependences.
    glyph={
      'previous':'<path d="M24 26 H35 V74 H24 Z M69 26 V74 L37 50 Z"/>',
      'play_pause':'<path d="M18 26 L49 50 L18 74 Z M61 26 H71 V74 H61 Z M79 26 H89 V74 H79 Z"/>',
      'next':'<path d="M76 26 H87 V74 H76 Z M31 26 V74 L74 50 Z"/>',
    }
    if name not in glyph:raise ValueError('unknown icon')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 100 100"><title>{escape(name)} media keycap legend</title><g fill="{escape(fill)}">{glyph[name]}</g></svg>\n'


def layout_svg(dim,cfg,cap,result):
    win=result['rotated_window'];xs=dim['keys_x'];v=dim['keys_v'];cw=cap['cap_width_mm'];well=cap['well_width_mm']
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-3 -16 163 148" width="1304" height="1184">',
      '<rect x="-3" y="-16" width="163" height="148" fill="#11151d"/>',
      '<text x="0" y="-8" font-family="Arial" font-size="4" fill="#f8fafb">Rounded Rev B / 180 degree board / low-set media keys (CONCEPT)</text>',
      f'<rect x="0" y="0" width="{dim["width"]}" height="{dim["front_face_length"]}" rx="5" fill="#34404a" stroke="#647481" stroke-width=".55"/>',
      f'<rect x="{win["x"]}" y="{win["v"]}" width="{win["width"]}" height="{win["height"]}" rx="1.5" fill="#06131c" stroke="#0c1118" stroke-width="1.1"/>',
      '<text x="18" y="44" font-size="6" font-family="Arial" fill="#c6e3fb">SPOTIFY</text>',
      '<text x="18" y="50" font-size="3.2" font-family="Arial" fill="#8db6cb">800 x 480 SIMULATED SCREEN</text>',
      f'<circle cx="{dim["knob_x"]}" cy="{dim["knob_v"]}" r="{cap["knob_diameter_mm"]/2}" fill="#13171d" stroke="#a3acb9" stroke-width=".9"/>',
      f'<circle cx="{dim["knob_x"]}" cy="{dim["knob_v"]}" r="{cap["knob_diameter_mm"]/2-1.2}" fill="none" stroke="#465462" stroke-width=".5"/>']
    for name,x in zip(('previous','play_pause','next'),xs):
        parts.extend([f'<rect x="{x-well/2}" y="{v-well/2}" width="{well}" height="{well}" rx="1.6" fill="#192128" stroke="#06090c" stroke-width=".6"/>',
         f'<rect x="{x-cw/2}" y="{v-cw/2}" width="{cw}" height="{cw}" rx="1.4" fill="#14171c" stroke="#515c65" stroke-width=".45"/>',
         f'<g transform="translate({x-5.5} {v-5.5}) scale(.11)" fill="#eef0f3">'+{
          'previous':'<path d="M24 26 H35 V74 H24 Z M69 26 V74 L37 50 Z"/>',
          'play_pause':'<path d="M18 26 L49 50 L18 74 Z M61 26 H71 V74 H61 Z M79 26 H89 V74 H79 Z"/>',
          'next':'<path d="M76 26 H87 V74 H76 Z M31 26 V74 L74 50 Z"/>'}[name]+'</g>'])
    parts.extend(['<text x="0" y="119" font-family="Arial" font-size="3.6" fill="#ecf2f8">Trial: 18.0mm caps inside 19.2mm wells / 0.6mm lateral nominal gap / 2mm proud at rest</text>',
    '<text x="0" y="126" font-family="Arial" font-size="3.0" fill="#eab682">Not for fabrication: cap underside, actual switch travel, 1.5mm clip plate &amp; real male USB plug unverified.</text>', '</svg>'])
    return '\n'.join(parts)+'\n'


def section_svg(cap,res):
    # Explicit visual section (X horizontal, W inwards/down) showing rest & downstroke in separated boxes.
    cw=cap['cap_width_mm'];well=cap['well_width_mm'];outer=cap['well_outer_support_width_mm'];top=cap['switch_plate_top_inward_mm'];travel=cap['switch_total_travel_nominal_mm']
    o=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 590" width="1080" height="590">',
       '<rect width="1080" height="590" fill="#151b23"/>',
       '<text x="48" y="45" fill="#f0f4fa" font-family="Arial" font-size="25">MX recessed keycap section / ASSUMED, not measured</text>']
    for j,(title,offset) in enumerate([('UNPRESSED',0),('FULL PRESS (4 mm)',travel)]):
        xx=75+j*540;cy=190;s=11;
        wtop=-cap['cap_rest_above_skin_mm']+offset
        def px(v):return xx+220+v*s
        def py(w):return cy+w*s
        def rect(x1,x2,w1,w2,color):o.append(f'<rect x="{px(x1):.1f}" y="{py(w1):.1f}" width="{(x2-x1)*s:.1f}" height="{(w2-w1)*s:.1f}" fill="{color}"/>')
        o.append(f'<text x="{xx}" y="98" fill="#e9f1f7" font-family="Arial" font-size="19">{title}</text>')
        # 3mm outer wall with cap through-well
        rect(-18,-well/2,0,3,'#536270');rect(well/2,18,0,3,'#536270')
        # ring continuation
        rect(-outer/2,-well/2,3,top,'#37454f');rect(well/2,outer/2,3,top,'#37454f')
        # switch clip plate
        rect(-outer/2,-cap['switch_plate_aperture_mm']/2,top,top+1.5,'#c9a967')
        rect(cap['switch_plate_aperture_mm']/2,outer/2,top,top+1.5,'#c9a967')
        # approximate MX switch body
        rect(-7.8,7.8,top-6.6,top,'#477f8e')
        rect(-7,7,top,top+5,'#477f8e')
        rect(-2,2,top-10.2+offset,top-6.6+offset,'#a2c0c4')
        # cap outer skirt only (not internally accurate)
        rect(-cw/2,cw/2,wtop,wtop+1.1,'#111215')
        rect(-cw/2,-cw/2+1.0,wtop+1,wtop+cap['cap_depth_assumed_mm'],'#111215')
        rect(cw/2-1,cw/2,wtop+1,wtop+cap['cap_depth_assumed_mm'],'#111215')
        o.append(f'<path d="M {px(-17)} {py(0)} L {px(17)} {py(0)}" stroke="#dfded8" stroke-dasharray="6,5"/>')
        o.append(f'<text x="{xx+15}" y="{py(-2.1)}" fill="#cad6e2" font-size="14" font-family="Arial">Exterior skin W=0</text>')
        o.append(f'<text x="{xx+15}" y="{py(23)}" fill="#ffcb95" font-size="15" font-family="Arial">CROSS-SECTION NOT TO SCALE FOR INTERNAL STEM</text>')
    o+=['<text x="42" y="545" fill="#ecddc3" font-size="20" font-family="Arial">Full-press skirt-to-plate gap: '+str(res['cap_skirt_to_plate_gap_at_full_press_mm'])+' mm trial; 1.5 mm plate / 19.2 mm well.</text>',
       '</svg>']
    return '\n'.join(o)+'\n'


def _face_plane(dim):
    import cadquery as cq
    ang=math.radians(dim['face_tilt_deg']);run=dim['front_face_length']*math.cos(ang)
    height=dim['front_chin']+dim['front_face_length']*math.sin(ang)
    return cq.Plane(origin=(0,run,height),xDir=(1,0,0),normal=(0,math.sin(ang),-math.cos(ang)))


def cad_build(dim, ref, casecfg, cap, target):
    import cadquery as cq
    p=geometry_parameters(dim,ref,casecfg)
    shell=cq.Workplane(obj=make_shell(dim,p,'rounded',casecfg))
    plane=_face_plane(dim)
    def block(cx,cv,w0,w1,ww,hh):
        return (cq.Workplane(plane).transformed(offset=(0,0,w0))
             .center(cx,cv).rect(ww,hh).extrude(w1-w0))
    well=cap['well_width_mm'];outer=cap['well_outer_support_width_mm'];pt=cap['switch_plate_top_inward_mm'];pth=cap['switch_plate_thickness_mm']
    for kx in dim['keys_x']:
        # Replace old 14mm-through aperture with 19.2mm cap skirt well.
        shell=shell.cut(block(kx,dim['keys_v'],-1,pt+pth+1,well,well))
    # Fuse reinforcing well walls and 1.5mm clip-bearing plate to the original 3mm shell.
    for kx in dim['keys_x']:
        cv=dim['keys_v']
        ring=block(kx,cv,2.80,pt,outer,outer).cut(block(kx,cv,2.79,pt+.1,well,well))
        support=block(kx,cv,pt,pt+pth,outer,outer).cut(block(kx,cv,pt-.1,pt+pth+.1,cap['switch_plate_aperture_mm'],cap['switch_plate_aperture_mm']))
        shell=shell.union(ring).union(support)
    solid=shell.val()
    if not solid.isValid():raise ValueError('Generated rounded shell not valid')
    stemtop=pt-cap['switch_top_above_plate_assumed_mm']-cap['stem_top_above_switch_housing_mm']
    assy=cq.Assembly(name='SpotifyDeskR180RecessedMediaDesignOnly')
    assy.add(solid,name='rounded_shell_experimental',color=cq.Color(.20,.24,.28))
    glass=block(dim['screen_origin'][0]+dim['screen_outer'][0]/2,dim['screen_origin'][1]+dim['screen_outer'][1]/2,
                casecfg['front_glass_inward_w_mm'],casecfg['front_glass_inward_w_mm']+16.906,
                *dim['screen_outer']).val()
    assy.add(glass,name='Waveshare_full_bbox_ASSUMED_MOUNT',color=cq.Color(.08,.22,.27))
    for idx,(n,kx) in enumerate(zip(('previous','play_pause','next'),dim['keys_x'])):
        cv=dim['keys_v']
        # Hollow-looking cap: top roof and four 1mm nominal side skirts; these are envelopes, NOT correct stems.
        w0=-cap['cap_rest_above_skin_mm']; w1=w0+cap['cap_depth_assumed_mm']; cw=cap['cap_width_mm'];side=1.0
        lid=block(kx,cv,w0,w0+1.2,cw,cw)
        skirt=block(kx,cv,w0+1.19,w1,cw,cw).cut(block(kx,cv,w0+1.18,w1+.1,cw-2*side,cw-2*side))
        capshape=lid.union(skirt).val()
        assy.add(capshape,name=n+'_cap_ASSUMED',color=cq.Color(.055,.067,.08))
        head=block(kx,cv,pt-6.6,pt,15.6,15.6).val()
        base=block(kx,cv,pt,pt+5,14,14).val()
        tip=block(kx,cv,stemtop,pt-6.6,4,4).val()
        assy.add(head,name=n+'_MX_head_ASSUMED',color=cq.Color(.35,.51,.55))
        assy.add(base,name=n+'_MX_base_ASSUMED',color=cq.Color(.25,.36,.41))
        assy.add(tip,name=n+'_MX_stem',color=cq.Color(.72,.83,.85))
        # approximate printed icons as independently colored solids on lid
        for j,polygon in enumerate(_icon_polygons(n)):
            shp=(cq.Workplane(plane).transformed(offset=(0,0,w0-.10))
                 .center(kx,cv).polyline(polygon).close().extrude(.11).val())
            assy.add(shp,name=f'{n}_white_symbol_{j}',color=cq.Color(.97,.98,.99))
    knob=cq.Workplane(plane).transformed(offset=(0,0,-cap['knob_exterior_height_assumed_mm'])).center(dim['knob_x'],dim['knob_v']).circle(cap['knob_diameter_mm']/2).extrude(cap['knob_exterior_height_assumed_mm']).val()
    assy.add(knob,name='black_knurled_knob_OUTER_ENVELOPE',color=cq.Color(.09,.10,.11))
    target.mkdir(exist_ok=True,parents=True)
    cq.exporters.export(solid,str(target/'spotify_desk_rounded180_recessed_3keys_EXPERIMENTAL.step'))
    assy.save(str(target/'spotify_desk_rounded180_with_cap_knob_ENVELOPES.step'))
    return solid


def _icon_polygons(name):
    # approximate XY face contour, independent of SVG packaging
    if name=='previous':return [[(-4.5,-3.2),(-3.3,-3.2),(-3.3,3.2),(-4.5,3.2)],[(-2.6,0),(3.8,-3.2),(3.8,3.2)]]
    if name=='next':return [[(4.5,-3.2),(3.3,-3.2),(3.3,3.2),(4.5,3.2)],[(2.6,0),(-3.8,-3.2),(-3.8,3.2)]]
    if name=='play_pause':return [[(-4.4,-3.2),(-4.4,3.2),(.5,0)],[(1.7,-3.2),(2.9,-3.2),(2.9,3.2),(1.7,3.2)],[(3.9,-3.2),(5.1,-3.2),(5.1,3.2),(3.9,3.2)]]
    raise ValueError(name)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report-only',action='store_true',help='Generate JSON and SVG without CadQuery')
    args=ap.parse_args()
    dim,ref,cfg=load();cap=assumptions();r=study(dim,ref,cfg,cap)
    args.out_dir.mkdir(exist_ok=True,parents=True)
    (args.out_dir/'media_controls_fit_report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    (args.out_dir/'media_controls_front.svg').write_text(layout_svg(dim,cfg,cap,r),encoding='utf-8')
    (args.out_dir/'mx_recess_section.svg').write_text(section_svg(cap,r),encoding='utf-8')
    for name in ('previous','play_pause','next'):
        (args.out_dir/(name+'_white_legend.svg')).write_text(icon_svg(name),encoding='utf-8')
    if not args.report_only:
        solid=cad_build(dim,ref,cfg,cap,args.out_dir)
        print('CAD B-rep valid:',solid.isValid(),'volume',round(solid.Volume()),'mm^3')
    print('Rounded R180 MEDIA KEY STUDY (not print-ready). Cap rest above skin %.1fmm, assumed cap depth %.1fmm, travel %.1fmm.'%(cap['cap_rest_above_skin_mm'],cap['cap_depth_assumed_mm'],cap['switch_total_travel_nominal_mm']))
    print('Keycap well: %.1fmm; side gap %.2fmm; plate top %.1fmm inward, %.1fmm thick.'%(cap['well_width_mm'],r['lateral_clearance_each_side_mm'],cap['switch_plate_top_inward_mm'],cap['switch_plate_thickness_mm']))
    print('At full press: nominal skirt-to-plate gap %.2fmm; actual cap/MX internal fit UNVERIFIED.'%r['cap_skirt_to_plate_gap_at_full_press_mm'])
    print('Outputs:',args.out_dir)

if __name__=='__main__':main()
