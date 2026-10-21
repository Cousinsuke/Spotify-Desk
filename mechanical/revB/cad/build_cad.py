#!/usr/bin/env python3
"""Spotify Desk Thing Phase 6 Rev B: editable conceptual CAD (not manufacturing release).
Uses nominal manufacturer dimensions where identified; marks all other geometry as assumed.
Two matched versions: SHARP vs ROUNDED R5 mm external edges.
"""
from __future__ import annotations
import math,json,os,zipfile,subprocess,shutil
from pathlib import Path
import cadquery as cq
from cadquery import Vector
from shapely.geometry import Polygon
import ezdxf
from ezdxf import units
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.lib.pagesizes import landscape,A3
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

DIR=Path(__file__).resolve().parent
W=156.; FACE=110.; ANG=55.; CHIN=16.; ROOF=20.; WALL=3.
RUN=FACE*math.cos(math.radians(ANG)); RISE=FACE*math.sin(math.radians(ANG))
DEPTH=RUN+ROOF; HEIGHT=CHIN+RISE
S_X=8.; S_V=8.; S_W=106.1; S_H=67.8
A_X=5.23; A_V=4.35; A_W=95.54; A_H=54.36
KEY_V=91.; KEY_PITCH=30.; SCREEN_CENTER=S_X+S_W/2
KEY_X=[round(SCREEN_CENTER-KEY_PITCH,3),round(SCREEN_CENTER,3),round(SCREEN_CENTER+KEY_PITCH,3)]
KNOB_X=138.;KNOB_V=44.;KNOB_D=15.1
R_OUT=5.; R_BEZEL=2.5
I2C_ALLOW=14. # Provisional horizontal cable keepout, NOT manufacturer specification
SQUARE_SIDE=[(0,0),(DEPTH,0),(DEPTH,HEIGHT),(RUN,HEIGHT),(0,CHIN)]
VERSIONS=['sharp','rounded']

META=dict(width=W,front_face_length=FACE,face_tilt_deg=ANG,front_chin=CHIN,rear_roof=ROOF,depth=DEPTH,height=HEIGHT,wall_assumed=WALL,rounding_external=R_OUT,
          screen_origin=(S_X,S_V),screen_outer=(S_W,S_H),display_visible=(A_W,A_H),display_visible_offset=(A_X,A_V),
          display_nominal_fixing_centers=(98,60), keys_x=KEY_X, keys_v=KEY_V,key_pitch=KEY_PITCH,
          knob_x=KNOB_X,knob_v=KNOB_V,knob_d=KNOB_D,i2c_approx_clearance=I2C_ALLOW,
          screen_center_x=SCREEN_CENTER, keys_mean_x=sum(KEY_X)/3,
          screen_knob_gap=KNOB_X-KNOB_D/2-(S_X+S_W),
          knob_right_margin=W-(KNOB_X+KNOB_D/2),
          screen_to_keys_gap=KEY_V-9-(S_V+S_H),
          encoder_body_to_i2c_assumed_gap=(KNOB_X-13.2/2)-(S_X+S_W+I2C_ALLOW))
(DIR/'dimensions.json').write_text(json.dumps(META,indent=2))

# ----- B-REP model ------------------------------------------------------------
plane=cq.Plane(origin=(0,RUN,HEIGHT),xDir=(1,0,0),normal=(0,math.sin(math.radians(ANG)),-math.cos(math.radians(ANG))))
# Workplane x=panel X, y=v down face, z=inward normal

def face_plane(exterior_offset=0):
    out=(0,-math.sin(math.radians(ANG)),math.cos(math.radians(ANG)))
    return cq.Plane(origin=(0,RUN+exterior_offset*out[1],HEIGHT+exterior_offset*out[2]), xDir=(1,0,0),normal=(0,-out[1],-out[2]))

def shape_on_face(cx,cv,ww,hh,z0=0,thickness=1):
    return cq.Workplane(face_plane(exterior_offset=-z0)).center(cx,cv).rect(ww,hh).extrude(thickness).val()

def cylinder_on_face(cx,cv,diam,z0=0,thickness=1):
    return cq.Workplane(face_plane(exterior_offset=-z0)).center(cx,cv).circle(diam/2).extrude(thickness).val()

def side_prism(points, width, x0=0):
    return cq.Workplane('YZ').polyline(points).close().extrude(width).translate((x0,0,0))

poly=Polygon(SQUARE_SIDE)
inner=poly.buffer(-WALL,join_style=2)
assert not inner.is_empty
inner_coords=list(inner.exterior.coords)[:-1]
models={}
for version in VERSIONS:
    outer=side_prism(SQUARE_SIDE,W)
    if version=='rounded':
        outer=outer.edges().fillet(R_OUT)
    cavity=side_prism(inner_coords,W-2*WALL,WALL)
    shell=outer.cut(cavity)
    # illustrative wide underside access, no production fasteners yet
    bottom_hatch=cq.Workplane('XY').box(W-22,DEPTH-24,8,centered=(True,True,False)).translate((W/2,DEPTH/2,-3))
    shell=shell.cut(bottom_hatch)
    # front apertures: 95.54x54.36 is visible rectangle, NOT an approved mask tolerance
    def panel_cutter(cx,cv,w,h):
        # project cutter to front plane, through provisional 3mm face
        if version=='rounded' and w>30:
            # screen aperture: 2.5mm corner radius in local x-y plane
            a=cq.Workplane(face_plane(1)).center(cx,cv).rect(w-2*R_BEZEL,h).extrude(18)
            b=cq.Workplane(face_plane(1)).center(cx,cv).rect(w,h-2*R_BEZEL).extrude(18)
            for dx in (-w/2+R_BEZEL,w/2-R_BEZEL):
                for dv in (-h/2+R_BEZEL,h/2-R_BEZEL):
                    a=a.union(cq.Workplane(face_plane(1)).center(cx+dx,cv+dv).circle(R_BEZEL).extrude(18))
            return a.union(b)
        return cq.Workplane(face_plane(1)).center(cx,cv).rect(w,h).extrude(18)
    shell=shell.cut(panel_cutter(S_X+A_X+A_W/2,S_V+A_V+A_H/2,A_W,A_H))
    # nominal 14x14 switch apertures; DO NOT USE AS FINAL 3D print tolerance
    for kx in KEY_X: shell=shell.cut(panel_cutter(kx,KEY_V,14,14))
    shell=shell.cut(cq.Workplane(face_plane(1)).center(KNOB_X,KNOB_V).circle(3.65).extrude(17))
    shell= shell.val()
    # component envelopes. Intentional intersections are NOT verified clearances.
    visible=shape_on_face(S_X+A_X+A_W/2,S_V+A_V+A_H/2,A_W,A_H,z0=-.9,thickness=.8)
    module=shape_on_face(S_X+S_W/2,S_V+S_H/2,S_W,S_H,z0=3.3,thickness=6.8)
    # White or grey button keycaps as observed in rendered reference.
    caps=[shape_on_face(kx,KEY_V,18,18,z0=-7.2,thickness=6.8) for kx in KEY_X]
    switches=[shape_on_face(kx,KEY_V,14,14,z0=3.2,thickness=16.8) for kx in KEY_X]
    knob=cylinder_on_face(KNOB_X,KNOB_V,KNOB_D,z0=-8,thickness=7.8)
    encoder=shape_on_face(KNOB_X,KNOB_V,13.2,13.2,z0=3.3,thickness=14.8)
    expander=cq.Workplane('XY').box(38,23,1.6,centered=(False,False,False)).translate((24,43,10)).val()
    models[version]={'case':shell,'display_envelope':module,'visible':visible,'knob':knob,'encoder_envelope':encoder,'aw9523b':expander}
    for i in range(3):
        models[version][f'keycap_{i+1}']=caps[i]
        models[version][f'switch_envelope_{i+1}']=switches[i]
    # STEP casings are drawings / preliminary parts. No certified screw bosses.
    cq.exporters.export(shell,str(DIR/f'spotify_desk_{version}_case_reference.step'))
    cq.exporters.export(shell,str(DIR/f'spotify_desk_{version}_case_reference.stl'),tolerance=0.3,angularTolerance=0.2)
    assy=cq.Assembly(name=f'SpotifyDeskRevB_{version}')
    cols={'case':cq.Color(0.19,0.22,0.27),'display_envelope':cq.Color(.10,.25,.32),
          'visible':cq.Color(.10,.33,.41),'knob':cq.Color(.12,.13,.16),'encoder_envelope':cq.Color(.52,.54,.58),
          'aw9523b':cq.Color(.53,.31,.58)}
    for name,sol in models[version].items():
        if name.startswith('keycap'): co=cq.Color(.91,.92,.95)
        elif name.startswith('switch_'): co=cq.Color(.34,.59,.67)
        else: co=cols.get(name,cq.Color(.7,.7,.7))
        assy.add(sol,name=name,color=co)
    assy.save(str(DIR/f'spotify_desk_{version}_envelope_assembly.step'))
    # Separate STL for reference visualization, matching CAD model, no mounting detail.
    for name in ['visible','knob']+[f'keycap_{i+1}' for i in range(3)]:
        cq.exporters.export(models[version][name],str(DIR/f'_{version}_{name}.stl'),tolerance=0.3,angularTolerance=0.2)
    scad='''// OpenSCAD viewer of same CAD B-REP exports (not a designed 3D printable case)\n$fn=72;\n'''
    c='#303740' if version=='sharp' else '#3B434B'
    scad+=f'color("{c}") import("spotify_desk_{version}_case_reference.stl",convexity=10);\n'
    scad+=f'color("#124055") import("_{version}_visible.stl",convexity=5);\n'
    for i in range(3):scad+=f'color("#E3E9EC") import("_{version}_keycap_{i+1}.stl",convexity=5);\n'
    scad+=f'color("#161C22") import("_{version}_knob.stl",convexity=5);\n'
    (DIR/f'_viewer_{version}.scad').write_text(scad)
    print('CAD',version,'body volume',round(shell.Volume(),1),'faces',len(shell.Faces()))

# ----- DXF 2D orthographic drawings -------------------------------------------
def add_mm_dim(ms,p1,p2,offset,layer='DIMENSIONS',textfmt='{:.1f}',direction='h'):
    # Custom unequivocally basic geometry dimensions in mm. No blocks or external fonts.
    x1,y1=p1;x2,y2=p2
    if direction=='h':
        dimy=offset
        for x,y in [(x1,y1),(x2,y2)]:ms.add_line((x,y),(x,dimy+(.7 if dimy>y else -.7)),dxfattribs={'layer':layer})
        ms.add_line((x1,dimy),(x2,dimy),dxfattribs={'layer':layer})
        for x,sgn in [(x1,1),(x2,-1)]:
            ms.add_line((x,dimy),(x+sgn*2,dimy+.65),dxfattribs={'layer':layer})
            ms.add_line((x,dimy),(x+sgn*2,dimy-.65),dxfattribs={'layer':layer})
        val=abs(x2-x1)
        ms.add_text(textfmt.format(val),dxfattribs={'layer':layer,'height':3,'insert':((x1+x2)/2,dimy+1.2)})
    else:
        dimx=offset
        for x,y in [(x1,y1),(x2,y2)]:ms.add_line((x,y),(dimx+(.7 if dimx>x else -.7),y),dxfattribs={'layer':layer})
        ms.add_line((dimx,y1),(dimx,y2),dxfattribs={'layer':layer})
        for y,sgn in [(y1,1),(y2,-1)]:
            ms.add_line((dimx,y),(dimx+.65,y+sgn*2),dxfattribs={'layer':layer})
            ms.add_line((dimx,y),(dimx-.65,y+sgn*2),dxfattribs={'layer':layer})
        val=abs(y2-y1)
        ms.add_text(textfmt.format(val),dxfattribs={'layer':layer,'height':3,'insert':(dimx+1.2,(y1+y2)/2)})

def arc_roundrect_points(x,y,w,h,r,steps=8):
    # x,y origin lower-left in CAD coordinate; r in mm
    if r<=0:return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    points=[]
    for cx,cy,start in [(x+w-r,y+r,-90),(x+w-r,y+h-r,0),(x+r,y+h-r,90),(x+r,y+r,180)]:
        for i in range(steps+1):
            a=math.radians(start+90*i/steps);points.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return points

def side_pts_rounded(points,r,n=10):
    # Rounded polygon outline sampled at each vertex, true tangent arc using vector arithmetic.
    # Outer polygon side points (clockwise or counterclockwise) returned approx CAD fillet R5.
    ret=[];N=len(points)
    for i,p in enumerate(points):
        prev=points[(i-1)%N];nxt=points[(i+1)%N]
        va=(prev[0]-p[0],prev[1]-p[1]);vb=(nxt[0]-p[0],nxt[1]-p[1])
        la=math.hypot(*va);lb=math.hypot(*vb)
        a=(va[0]/la,va[1]/la);b=(vb[0]/lb,vb[1]/lb)
        theta=math.acos(max(-1,min(1,a[0]*b[0]+a[1]*b[1])))
        dist=min(r/math.tan(theta/2),la*.25,lb*.25)
        pc=(p[0]+a[0]*dist,p[1]+a[1]*dist)
        qc=(p[0]+b[0]*dist,p[1]+b[1]*dist)
        mid=(a[0]+b[0],a[1]+b[1]);mnorm=math.hypot(*mid)
        if mnorm<1e-7:ret.append(p);continue
        bis=(mid[0]/mnorm,mid[1]/mnorm)
        rr=dist*math.tan(theta/2)
        c=(p[0]+bis[0]*(rr/math.sin(theta/2)),p[1]+bis[1]*(rr/math.sin(theta/2)))
        a1=math.atan2(pc[1]-c[1],pc[0]-c[0]);a2=math.atan2(qc[1]-c[1],qc[0]-c[0]);da=(a2-a1+math.pi)%(2*math.pi)-math.pi
        for j in range(n+1):
            a0=a1+da*j/n;ret.append((c[0]+rr*math.cos(a0),c[1]+rr*math.sin(a0)))
    return ret

for version in VERSIONS:
    d=ezdxf.new('R2010');d.units=units.MM;d.header['$INSUNITS']=4
    for lay,col,lt in [('CASE_OUTLINE',7,'CONTINUOUS'),('LCD_MODULE',5,'CONTINUOUS'),('DISPLAY_WINDOW',4,'CONTINUOUS'),('KEYCAPS',7,'CONTINUOUS'),('SWITCH_APERTURES',6,'DASHED'),('ROTARY',2,'CONTINUOUS'),('REFERENCE_HOLES',6,'CONTINUOUS'),('I2C_ASSUMED_ZONE',30,'DASHED'),('CENTERLINES',3,'CENTER'),('DIMENSIONS',1,'CONTINUOUS'),('NOTES',8,'CONTINUOUS')]:
        try:d.layers.new(lay,dxfattribs={'color':col,'linetype':lt})
        except Exception:d.layers.new(lay,dxfattribs={'color':col})
    ms=d.modelspace()
    def rect(x,y,w,h,layer,r=0):
        ms.add_lwpolyline(arc_roundrect_points(x,y,w,h,r),close=True,dxfattribs={'layer':layer})
    def ring(x,y,r,layer):ms.add_circle((x,y),r,dxfattribs={'layer':layer})
    # FRONT view: x=width, y=-v (down slope)
    rect(0,-FACE,W,FACE,'CASE_OUTLINE',R_OUT if version=='rounded' else 0)
    rect(S_X,-S_V-S_H,S_W,S_H,'LCD_MODULE')
    rect(S_X+A_X,-S_V-A_V-A_H,A_W,A_H,'DISPLAY_WINDOW',R_BEZEL if version=='rounded' else 0)
    for x in [S_X+4,S_X+102]:
        for v in [S_V+4,S_V+64]:ring(x,-v,1.1,'REFERENCE_HOLES')
    for kx in KEY_X:
        rect(kx-9,-KEY_V-9,18,18,'KEYCAPS',1.3 if version=='rounded' else 0)
        rect(kx-7,-KEY_V-7,14,14,'SWITCH_APERTURES')
        ms.add_line((kx,-KEY_V-11),(kx,-KEY_V+11),dxfattribs={'layer':'CENTERLINES'})
    ring(KNOB_X,-KNOB_V,KNOB_D/2,'ROTARY');ring(KNOB_X,-KNOB_V,3.65,'SWITCH_APERTURES')
    rect(KNOB_X-6.6,-KNOB_V-6.6,13.2,13.2,'REFERENCE_HOLES')
    rect(S_X+S_W,-(S_V+27+26),I2C_ALLOW,26,'I2C_ASSUMED_ZONE')
    ms.add_line((SCREEN_CENTER,-1),(SCREEN_CENTER,-FACE+1),dxfattribs={'layer':'CENTERLINES'})
    add_mm_dim(ms,(0,0),(W,0),12,direction='h')
    add_mm_dim(ms,(0,0),(0,-FACE),-16,direction='v')
    add_mm_dim(ms,(S_X,-S_V),(S_X+S_W,-S_V),-4,direction='h')
    add_mm_dim(ms,(KEY_X[0],-KEY_V),(KEY_X[1],-KEY_V),-114,direction='h')
    add_mm_dim(ms,(KEY_X[1],-KEY_V),(KEY_X[2],-KEY_V),-114,direction='h')
    ms.add_text(f'FRONT - {version.upper()} | SCALE 1:1 | x to right, y down',dxfattribs={'layer':'NOTES','height':4,'insert':(0,21)})
    ms.add_text('KEY ROW CENTRED AT DISPLAY X=61.05',dxfattribs={'layer':'NOTES','height':3.0,'insert':(0,-128)})
    ms.add_text('VISIBLE WINDOW 95.54 x 54.36; FULL LCD 106.10 x 67.80',dxfattribs={'layer':'NOTES','height':2.5,'insert':(0,-135)})
    # SIDE view at x >= 218: local x = DEPTH along tabletop, y = height
    shift=220
    points=side_pts_rounded(SQUARE_SIDE,R_OUT) if version=='rounded' else SQUARE_SIDE
    ms.add_lwpolyline([(shift+yy,zz) for yy,zz in points],close=True,dxfattribs={'layer':'CASE_OUTLINE'})
    # front face center line with slope marked
    ms.add_line((shift,CHIN),(shift+RUN,HEIGHT),dxfattribs={'layer':'CENTERLINES'})
    add_mm_dim(ms,(shift,0),(shift+DEPTH,0),-16,direction='h')
    add_mm_dim(ms,(shift+DEPTH,0),(shift+DEPTH,HEIGHT),shift+DEPTH+14,direction='v')
    add_mm_dim(ms,(shift+RUN,HEIGHT),(shift+DEPTH,HEIGHT),HEIGHT+12,direction='h')
    add_mm_dim(ms,(shift,0),(shift,CHIN),shift-11,direction='v')
    ms.add_text('SIDE SECTION - 55 DEG FROM DESK',dxfattribs={'layer':'NOTES','height':3.3,'insert':(shift,HEIGHT+22)})
    ms.add_text('FRONT CHIN 16 / REAR ROOF 20',dxfattribs={'layer':'NOTES','height':3.,'insert':(shift,-26)})
    ms.add_text('ASSUMED 3mm WALL / SERVICE HATCH = CONCEPT',dxfattribs={'layer':'NOTES','height':2.6,'insert':(shift,-32)})
    d.saveas(DIR/f'spotify_desk_{version}_dimensioned.dxf')
    ezdxf.readfile(DIR/f'spotify_desk_{version}_dimensioned.dxf')

# ----- PDF ReportLab CAD sheets ------------------------------------------------
PAGE_W,PAGE_H=landscape(A3);PT=72/25.4
INK=HexColor('#19314A');MUTED=HexColor('#5A7085');ACC=HexColor('#087E93')
ORANGE=HexColor('#BC7932');LIGHT=HexColor('#D4E8EF');DARK=HexColor('#2B3948')
PDF=DIR/'Spotify_Desk_RevB_dimensioned_CAD_comparison.pdf'
cv=canvas.Canvas(str(PDF),pagesize=(PAGE_W,PAGE_H));cv.setTitle('Spotify Desk Thing - Rev B normal and rounded dimensioned CAD study')
def mm(x):return x*PT

def para(lines,x,y,leading=15,font=9,colour=INK):
    cv.setFont('Helvetica',font);cv.setFillColor(colour)
    for line in lines:
        cv.drawString(x,y,line);y-=leading
    return y

def header(name,sub,page):
    cv.setFillColor(DARK);cv.rect(0,PAGE_H-66,PAGE_W,66,stroke=0,fill=1)
    cv.setFillColor(HexColor('#FFFFFF'));cv.setFont('Helvetica-Bold',21);cv.drawString(46,PAGE_H-39,name)
    cv.setFillColor(HexColor('#C5DEE4'));cv.setFont('Helvetica',9);cv.drawString(47,PAGE_H-55,sub)
    cv.setFillColor(MUTED);cv.setFont('Helvetica',8);cv.drawRightString(PAGE_W-42,22,f'SPOTIFY DESK THING | REV B | PAGE {page} | NOT FOR FABRICATION')
    cv.setStrokeColor(HexColor('#D3E0E5'));cv.line(42,37,PAGE_W-42,37)

def annotate_text(x,y,text,font=9,color=INK):
    cv.setFillColor(color);cv.setFont('Helvetica',font);cv.drawString(x,y,text)

def dimension_h(px1,px2,refy,dmy,label):
    cv.setLineWidth(.75);cv.setStrokeColor(ACC)
    for px in (px1,px2): cv.line(px,refy,px,dmy+(-5 if dmy<refy else 5))
    cv.line(px1,dmy,px2,dmy)
    for px,direc in [(px1,1),(px2,-1)]:
        cv.line(px,dmy,px+direc*6,dmy+2);cv.line(px,dmy,px+direc*6,dmy-2)
    cv.setFillColor(ACC);cv.setFont('Helvetica-Bold',8)
    cv.drawCentredString((px1+px2)/2,dmy+5,label)

def dimension_v(py1,py2,refx,dmx,label):
    cv.setLineWidth(.7);cv.setStrokeColor(ACC)
    for yy in (py1,py2):cv.line(refx,yy,dmx+(-4 if dmx<refx else 4),yy)
    cv.line(dmx,py1,dmx,py2)
    for yy,direc in [(py1,1),(py2,-1)]:
        cv.line(dmx,yy,dmx-2,yy+direc*6);cv.line(dmx,yy,dmx+2,yy+direc*6)
    cv.saveState();cv.translate(dmx-5,(py1+py2)/2);cv.rotate(90);cv.setFillColor(ACC);cv.setFont('Helvetica-Bold',8);cv.drawCentredString(0,0,label);cv.restoreState()

def draw_round_rect(x,y,w,h,r,fill=0,stroke=1):
    cv.roundRect(x,y,w,h,r,stroke=stroke,fill=fill)

def draw_front(version,xx=mm(42),top=PAGE_H-mm(58)):
    # top origin where v increases down; vector projections 1:1 at A3 100% if printed actual size.
    def X(u):return xx+mm(u)
    def Y(v):return top-mm(v)
    r=R_OUT if version=='rounded' else 0
    cv.setFillColor(HexColor('#F0F4F7'));cv.setStrokeColor(INK);cv.setLineWidth(1.35)
    draw_round_rect(X(0),Y(FACE),mm(W),mm(FACE),mm(r),fill=1,stroke=1)
    cv.setFillColor(HexColor('#D9E4E9'));cv.setStrokeColor(MUTED);cv.rect(X(S_X),Y(S_V+S_H),mm(S_W),mm(S_H),stroke=1,fill=1)
    cv.setFillColor(HexColor('#163B48'));cv.setStrokeColor(ACC)
    draw_round_rect(X(S_X+A_X),Y(S_V+A_V+A_H),mm(A_W),mm(A_H),mm(R_BEZEL if version=='rounded' else 0),fill=1,stroke=1)
    for kx in KEY_X:
        cv.setStrokeColor(INK);cv.setFillColor(HexColor('#FFFFFF'))
        draw_round_rect(X(kx-9),Y(KEY_V+9),mm(18),mm(18),mm(1.5 if version=='rounded' else 0),fill=1)
        cv.setStrokeColor(ACC);cv.setDash(2,2)
        cv.rect(X(kx-7),Y(KEY_V+7),mm(14),mm(14),stroke=1,fill=0);cv.setDash()
    cv.setFillColor(HexColor('#38474D'));cv.setStrokeColor(INK)
    cv.circle(X(KNOB_X),Y(KNOB_V),mm(KNOB_D/2),fill=1,stroke=1)
    # right-edge I2C 14mm assumption
    cv.setStrokeColor(ORANGE);cv.setDash(3,3)
    cv.rect(X(S_X+S_W),Y(S_V+53),mm(I2C_ALLOW),mm(26),fill=0,stroke=1);cv.setDash()
    for sx in (S_X+4,S_X+102):
        for sv in (S_V+4,S_V+64):
            cv.setStrokeColor(HexColor('#A184B5'));cv.circle(X(sx),Y(sv),2.7,fill=0,stroke=1)
    # centreline across face
    cv.setDash(5,4);cv.setStrokeColor(ACC);cv.line(X(SCREEN_CENTER),Y(2),X(SCREEN_CENTER),Y(FACE-2));cv.setDash()
    dimension_h(X(0),X(W),Y(0),Y(-10),'156.00 mm overall')
    dimension_v(Y(0),Y(FACE),X(0),X(-13),'110.00 mm along slope')
    dimension_h(X(S_X),X(S_X+S_W),Y(S_V),Y(-3),'106.10 mm LCD module')
    dimension_h(X(KEY_X[0]),X(KEY_X[1]),Y(KEY_V),Y(104),'30.00 mm')
    dimension_h(X(KEY_X[1]),X(KEY_X[2]),Y(KEY_V),Y(104),'30.00 mm')
    annotate_text(X(0),Y(116),'FRONT (TRUE 1:1 at A3 / no auto scaling)',8,MUTED)
    annotate_text(X(0),Y(122),'Middle key at X = 61.05 = LCD centre',9,ACC)
    return X,Y

def draw_side(version,xx=mm(252),base=PAGE_H-mm(167)):
    def X(y):return xx+mm(y)
    def Y(z):return base+mm(z)
    # cad side polygon
    pts=side_pts_rounded(SQUARE_SIDE,R_OUT) if version=='rounded' else SQUARE_SIDE
    cv.setStrokeColor(INK);cv.setFillColor(HexColor('#EEF2F5'))
    cv.setLineWidth(1.4);path=cv.beginPath()
    for i,(yy,zz) in enumerate(pts):
        if i==0:path.moveTo(X(yy),Y(zz))
        else:path.lineTo(X(yy),Y(zz))
    path.close();cv.drawPath(path,stroke=1,fill=1)
    # 3mm assumed floor shell, visual
    cv.setStrokeColor(MUTED);cv.setDash(3,4)
    cv.line(X(0),Y(3),X(DEPTH),Y(3));cv.setDash()
    dimension_h(X(0),X(DEPTH),Y(0),Y(-10),'83.09 mm depth')
    dimension_v(Y(0),Y(HEIGHT),X(DEPTH),X(DEPTH+13),'106.11 mm high')
    dimension_h(X(RUN),X(DEPTH),Y(HEIGHT),Y(HEIGHT+10),'20.00 mm roof')
    dimension_v(Y(0),Y(CHIN),X(0),X(-10),'16 mm')
    annotate_text(X(0),Y(HEIGHT+19),'SIDE (55 deg from tabletop)',8,MUTED)
    annotate_text(X(0),Y(-18),'110.00 mm angled face length',9,INK)
    if version=='rounded':annotate_text(X(0),Y(-23),'R5 reference outer fillets (not approved tooling)',8,ORANGE)
    else:annotate_text(X(0),Y(-23),'Crisp edges: no external rounding',8,ORANGE)

# Cover page
header('Spotify Desk | Revised compact wedge CAD','Two matching variants: SHARP corners and ROUNDED corners | manufacturer dimensions + explicit assumptions',1)
ref1=DIR.parent/'minimal_wedge_shaped_desk_controller.png';ref2=DIR.parent/'rounded_charcoal_desktop_controller.png'
# Images 1448x1086 aspect 4:3
photo_w=490;photo_h=photo_w*1086/1448
if ref1.exists():cv.drawImage(str(ref1),60,340,photo_w,photo_h)
if ref2.exists():cv.drawImage(str(ref2),640,340,photo_w,photo_h)
annotate_text(62,329,'SHARP: industrial styling reference - not a dimensioned photo',10,INK)
annotate_text(642,329,'ROUNDED: R5 outer-edge CAD variant - appearance reference',10,INK)
cv.setFillColor(HexColor('#EFF7F8'));cv.roundRect(58,88,PAGE_W-116,204,10,fill=1,stroke=0)
para(['CHANGES FROM EARLIER CAD','Outer width: 165 -> 156 mm  |  compact around right-side knob','3 key centres: X = 31.05 / 61.05 / 91.05 mm, centred on the LCD (X = 61.05 mm)','Knob centre: (138,44) mm  |  knob OD 15.1 mm  |  bezel-to-knob OD gap 16.35 mm','Front plane: 156 x 110 mm  |  55 deg above desk  |  front chin 16 mm  |  rear roof 20 mm','Outside body: 156 W x 83.09 D x 106.11 H mm','All dimensions in mm. No fastener bores, USB opening or connector routing is certified.'],78,268,24,12)
para(['ATTENTION: Front reference images are aesthetic concepts, not measured drawings.','The A3 technical sheets on pages 2 and 3 are true XY scale when printed at 100% on A3.','Rounded edges reduce available material near perimeter; real component and cable fit still needs testing.'],78,95,15,9,MUTED)
cv.showPage()
for pg,variant in enumerate(VERSIONS,2):
    header(f'Rev B | {variant.capitalize()} corners','A3 1:1 concept plan: front face measured along slope, side measured along desk/vertical axis',pg)
    draw_front(variant);draw_side(variant)
    cv.setFillColor(HexColor('#F1F6F8'));cv.roundRect(46,60,PAGE_W-92,128,6,fill=1,stroke=0)
    rows=[
        'DISPLAY 106.10 x 67.80  |  VIEWABLE ~95.54 x 54.36  |  98 x 60 NOMINAL MOUNT PITCH (BORE NOT VERIFIED)',
        'KEYCAPS 18 x 18 NOMINAL  |  3 KEYS AT X=31.05 / 61.05 / 91.05, V=91  |  30 MM SPACING',
        'KNOB 15.1 DIA AT (138,44)  |  10.45 RIGHT EDGE MARGIN  |  16.35 LCD-TO-KNOB CLEARANCE',
        'LCD-TO-KEYCAP GAP 6.20  |  14 MM ORANGE I2C BAND IS AN ASSUMPTION  |  ENCODER-TO-BAND 3.30 MM',
        'R5 CORNERS' if variant=='rounded' else 'SHARP OUTER CORNERS',
        'CAUTION: 3 MM CASE WALL, BUTTON HOLES, KNOB BUSH HOLE AND INTERNAL Z DEPTH ARE PROTOTYPE ASSUMPTIONS',
    ]
    para(rows,66,170,17,9,INK)
    cv.showPage()

header('Rev B | Assembly envelopes and approvals','CAD STEP and OpenSCAD are editable. 3D shell geometry is concept only; do not use for manufacturing without fit tests.',4)
rows=[
    ('MANUFACTURER / USER SOURCED','ASSUMPTIONS IN THIS CAD MODEL'),
    ('LCD module outer 106.1 x 67.8 mm','Front face 156 x 110, 55 degree tilt'),
    ('Visible region approx 95.54 x 54.36 mm','16 mm toe, 20 mm back roof, 3 mm wall'),
    ('LCD mounting pitch approx 98 x 60','R5 exterior rounds, R2.5 aperture corners'),
    ('Three 18 x 18 mm user-proposed keycaps','14 x 14 mm nominal switch openings, not toleranced'),
    ('KZ0087 OD 15.1, H 15.2 mm','Knob visibly stands ~8 mm proud'),
    ('AW9523B PCB approx 38 x 23 mm','Display rear depth 6.8 mm and switch Z depth 16.8 mm'),
    ('Encoder body footprint about 13.2 x 13.2','14 mm cable corridor and 3.3 mm nominal lateral gap'),
    ('Encoder click 0.5 +/-0.2 mm','Bottom hatch opening size and wall feature'),
]
starty=680
for i,(a,b) in enumerate(rows):
    yy=starty-i*48
    cv.setFillColor(HexColor('#EDF4F7') if i%2 else HexColor('#FFFFFF'));cv.rect(60,yy-15,PAGE_W-120,40,fill=1,stroke=0)
    annotate_text(73,yy,a,11 if i==0 else 10,INK)
    annotate_text(PAGE_W/2+16,yy,b,11 if i==0 else 10,INK)
cv.setFillColor(HexColor('#FFF1E0'));cv.roundRect(60,110,PAGE_W-120,105,7,fill=1,stroke=0)
para(['PRE-MANUFACTURING CHECKS','Confirm LCD connector orientation + bend, genuine mounting-hole diameter, USB access and antenna clearance.',
      'Measure exact MX switch model/depth, plate clips and keycaps; test KZ0087 press/grub screw engagement.',
      'Confirm AW9523B reset/boot wiring and input protection; the drawing does not certify 3.3 V circuits.'],78,187,21,10,INK)
cv.showPage();cv.save()
print('PDF',PDF)

# Render PDF for visual review by separate skill command later.
# Bundle only curated output + script, no internal temp STL files.
keep=['Spotify_Desk_RevB_dimensioned_CAD_comparison.pdf','dimensions.json','build_cad.py',
 'spotify_desk_sharp_case_reference.step','spotify_desk_rounded_case_reference.step',
 'spotify_desk_sharp_envelope_assembly.step','spotify_desk_rounded_envelope_assembly.step',
 'spotify_desk_sharp_dimensioned.dxf','spotify_desk_rounded_dimensioned.dxf']
(DIR/'README.txt').write_text('Spotify Desk Thing - Phase 6 CAD Rev B (PROVISIONAL)\n\n'+
 'SHARP and ROUNDED 5mm corner concept variants. 156 x 110 mm front, 55deg slope,\n'+
 '156 x 83.09 x 106.11 mm bounding case; 3 media keys mathematically centred on screen.\n\n'+
 'EDITABLE CAD: paired STEP case solids + STEP reference assemblies; DXF dimensioned front+side; Python generator; dimension JSON.\n'+
 'PDF: 4 page A3 vector dimensioned comparison with prior aesthetic image references.\n'+
 'NOT MANUFACTURING READY: LCD screw bores, MX cutout tolerances, case fasteners, USB/JST openings, real Z/connector geometry, LCD fit, electronics still open.\n'+
 'The 14mm I2C corridor, 3mm wall, rear envelope and switch depths are assumptions.\n')
keep.append('README.txt')
with zipfile.ZipFile(DIR/'Spotify_Desk_RevB_CAD_Shared_Package.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name in keep:z.write(DIR/name,name)
print('ZIP',DIR/'Spotify_Desk_RevB_CAD_Shared_Package.zip')
print('metrics',META)
