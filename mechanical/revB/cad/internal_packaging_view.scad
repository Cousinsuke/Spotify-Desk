/* SPOTIFY DESK REV B: 3D INTERNAL PACKAGING STUDY, not manufacturing geometry.
  All unknown parts (ports, connectors, standoffs, wiring etc) are illustrative.
  Run internal_packaging.py to regenerate scenario-specific parameters and report.
  Does NOT edit existing sharp/R5 STEP files or implement accurate R5 fillets.
  World X=left-to-right; Y=backwards along desk; Z=vertical from desk.
  Local X=left-to-right, V=down inclined face, W=inward perpendicular to face.
*/
include <internal_packaging_params.scad>

$fn = 48;
show_case = true;
show_components = true;
show_mounting_markers = true;
show_interior_board = true;
show_bottom_access = true;
show_overlap = true;
run = FACE * cos(ANGLE);
height = CHIN + FACE * sin(ANGLE);
depth = run + ROOF;
// Columns: local X, V and W transformed to world X, Y and Z. Inward is +W.
module face_coordinates() {
  multmatrix([[1,0,0,0],
              [0,-cos(ANGLE),sin(ANGLE),run],
              [0,-sin(ANGLE),-cos(ANGLE),height],
              [0,0,0,1]]) children();
}
module face_box(x,v,w,dx,dv,dw) {
  face_coordinates() translate([x,v,w]) cube([dx,dv,dw]);
}
module side_prism(outline,ww,xx=0){
  translate([xx,0,0])
    multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
      linear_extrude(height=ww) polygon(outline);
}
module side_approx_shell(){
  section=[[0,0],[depth,0],[depth,height],[run,height],[0,CHIN]];
  difference(){
    side_prism(section,W);
    // OpenSCAD offset creates a *nominal* 3mm inner wall; no real screw bosses.
    translate([WALL,0,0])
      multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
        linear_extrude(height=W-2*WALL)
          offset(delta=-WALL) polygon(section);
    // Screen viewing aperture from original Rev B dimensions (NOT toleranced).
    face_box(SCREEN_X+5.23,SCREEN_V+4.35,-2,95.54,54.36,10);
    for(x=KEY_X) face_box(x-7,KEY_V-7,-2,14,14,10);
    face_coordinates() translate([KNOB_X,KNOB_V,-2]) cylinder(d=7.3,h=12);
  }
}
module module_lcd(){
  face_box(SCREEN_X,SCREEN_V,SCREEN_IN,SCREEN_W,SCREEN_H,SCREEN_DEPTH);
}
module mx_bodies(){
  for(x=KEY_X) face_box(x-SWITCH_SIZE/2,KEY_V-SWITCH_SIZE/2,
                      SWITCH_IN,SWITCH_SIZE,SWITCH_SIZE,SWITCH_DEPTH);
}
module encoder_body(){
  face_box(KNOB_X-ENCODER_SIZE/2,KNOB_V-ENCODER_SIZE/2,ENCODER_IN,
           ENCODER_SIZE,ENCODER_SIZE,ENCODER_DEPTH);
}
module encoder_terminals(){
  face_box(KNOB_X-ENCODER_SIZE/2,KNOB_V-ENCODER_SIZE/2,
           ENCODER_IN+ENCODER_DEPTH,ENCODER_SIZE,ENCODER_SIZE,TERMINAL_DEPTH);
}
module right_i2c_envelope(){
  face_box(SCREEN_X+SCREEN_W,I2C_V,I2C_IN,I2C_EXTENSION,I2C_V_LEN,I2C_DEPTH);
}
module left_usb_envelope(){
  face_box(SCREEN_X-USB_EXTENSION,USB_V,USB_IN,USB_EXTENSION,USB_V_LEN,USB_DEPTH);
}
module top_control_surfaces(){
  face_coordinates(){
    for(x=KEY_X)
      color([.85,.9,.96,1])translate([x-9,KEY_V-9,-7.2])cube([18,18,6.8]);
    color([.09,.09,.11,1])translate([KNOB_X,KNOB_V,-8])cylinder(d=KNOB_D,h=7.8);
  }
}
module fixing_markers(){
  // Nominal 98x60 centres, 4mm inboard from board edges. NOT correct screw bores.
  for(x=[SCREEN_X+4,SCREEN_X+4+FIX_PITCH_X])
   for(v=[SCREEN_V+4,SCREEN_V+4+FIX_PITCH_V])
    color([.98,.73,.3,.65])
     face_coordinates()translate([x,v,SCREEN_IN])cylinder(d=FIXING_MARKER_D,h=6.8);
}
module aw_board_envelope(){
  // World-coordinate board placement copied from the historical Rev B assembly.
  // Placement is an arbitrary trial, not an assembly fixture.
  translate(AW_BOARD_WORLD_MIN)cube(AW_BOARD_SIZE);
}
module bottom_access_zone(){
  // Conceptual hatch swept keepout rather than printable removable hatch geometry.
  translate([11,12,0])cube([W-22,depth-24,HATCH_CLEARANCE_Z]);
}
if(show_case) color([.28,.34,.43,.2])side_approx_shell();
if(show_components){
 color([.05,.65,.84,.8])module_lcd();
 color([.38,.7,.8,.85])mx_bodies();
 color([.78,.49,.19,.95])encoder_body();
 color([.8,.65,.25,.55])encoder_terminals();
 color([.97,.39,.28,.45])right_i2c_envelope();
 color([.96,.61,.22,.5])left_usb_envelope();
 top_control_surfaces();
}
if(show_mounting_markers)fixing_markers();
if(show_interior_board)color([.63,.36,.72,.6])aw_board_envelope();
if(show_bottom_access)color([.26,.85,.47,.13])bottom_access_zone();
if(show_overlap)color([1,0,.1,.92])intersection(){right_i2c_envelope();encoder_body();}
// The true sharp and R5 original STEP cases are unchanged and are not rendered.
echo("NOT FOR FABRICATION: R5 and real port/bore/hatch geometry are not represented.");
