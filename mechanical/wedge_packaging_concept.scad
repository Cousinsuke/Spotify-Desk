/* Spotify Desk Thing — Phase 6 WEDGE PACKAGING CONCEPT (NOT FABRICATION CAD)
   All units millimetres. Sloping surface uses prior 165x110 face layout.
   Prototype envelopes only: holes, mounting, ports, depth/lead clearance,
   antenna restrictions and electrical safety are not production validated.
   Modes: "exterior", "ghost", "cutaway", "shell_only".
*/
$fn=48;
mode="exterior";
tilt_deg=55;             // degrees FROM desk/horizontal. PROVISIONAL.
face_width=165;         // across desktop. User has not approved case envelope.
face_length=110;        // along sloped face (not vertical height)
front_chin=16;          // keeps lower key bodies away from the floor. ASSUMED.
rear_roof=20;           // adds upper rear depth behind LCD. ASSUMED.
wall=3;                 // initial illustrative shell thickness
floor_lid_thickness=2;  // indicative bottom service hatch
face_run=face_length*cos(tilt_deg);
face_rise=face_length*sin(tilt_deg);
height_total=front_chin+face_rise;
depth_total=face_run+rear_roof;
screen_x=11; screen_v=8;
screen_w=106.1; screen_l=67.8;
visible_x=5.23; visible_v=4.35; visible_w=95.54; visible_l=54.36;
key_centres=[40,70,100]; key_v=91;
knob_x=142; knob_v=44;
profile_pts=[[0,0],[depth_total,0],[depth_total,height_total],
             [face_run,height_total],[0,front_chin]];
// x=width, v=down sloped face from top, w=inward normal to face.
module face_frame(){
 translate([0,face_run,height_total]) rotate([180+tilt_deg,0,0]) children();
}
module extruded_profile(pts,span=face_width){
 rotate([0,0,90]) rotate([90,0,0])
 linear_extrude(height=span,convexity=8) polygon(points=pts);
}
module shell_geometry(){
 difference(){
  extruded_profile(profile_pts);
  // Swept interior is a visual cavity, not structurally engineered.
  translate([wall,0,0]) rotate([0,0,90]) rotate([90,0,0])
   linear_extrude(height=face_width-2*wall,convexity=8)
    offset(delta=-wall) polygon(points=profile_pts);
  // Bottom hatch opening only, with no finished mounting clips/fasteners.
  translate([9,9,-1]) cube([face_width-18,depth_total-18,5]);
 }
}
module bottom_hatch(){
 color([.19,.22,.27,.85]) translate([9.8,9.8,.9])
  cube([face_width-19.6,depth_total-19.6,floor_lid_thickness]);
}
module screen_envelopes(){
 face_frame(){
  color([.06,.11,.16]) translate([screen_x,screen_v,-1.5])
   cube([screen_w,screen_l,1.55]);
  color([.12,.29,.35]) translate([screen_x+visible_x,screen_v+visible_v,-1.75])
   cube([visible_w,visible_l,.20]);
  // Screen module envelope behind face: 8.8mm is NOT verified max depth.
  color([.22,.60,.70,.62]) translate([screen_x,screen_v,wall])
   cube([screen_w,screen_l,8.8]);
  // These 98x60 nominal pitched markers are NOT drill holes.
  for(xx=[4,102],vv=[4,64]) color([.73,.36,.82])
   translate([screen_x+xx,screen_v+vv,wall+.1])
    cylinder(d=2.4,h=2.1);
 }
}
module keys_envelopes(){
 for(i=[0:2]) face_frame(){
  color([.82,.85,.90]) translate([key_centres[i]-9,key_v-9,-7])
   cube([18,18,6.9]);
  // 14x14 switch XY nominal; 18mm Z is a provisional package estimate.
  color([.45,.75,.83,.82]) translate([key_centres[i]-7,key_v-7,wall])
   cube([14,14,18]);
 }
}
module knob_encoder_envelopes(){
 face_frame(){
  // Exposes ~8mm of KZ0087: styling intent, actual fit not certified.
  color([.19,.22,.26]) translate([knob_x,knob_v,-8.3])
   cylinder(d=15.1,h=8.1);
  // 13.2mm body XY nominal; 17mm inwards INCLUDING LEADS is assumed.
  color([.58,.62,.69,.92]) translate([knob_x-6.6,knob_v-6.6,wall])
   cube([13.2,13.2,17]);
  // 14x26x11 side corridor: invented I2C plug/cable allowance.
  color([1,.60,.20,.27]) translate([screen_x+screen_w,screen_v+27,wall])
   cube([14,26,11]);
 }
}
module aw_expander(){
 // Candidate accessible horizontal location near removable base, unverified.
 color([.71,.44,.81,.85]) translate([24,43,10]) cube([38,23,1.6]);
 color([.86,.73,.92,.7]) translate([27,46,11.6]) cube([6,6,4]);
}
module service_envelopes(){
 // Zones ONLY (left USB, rear cable/exit), not port cutouts.
 color([.98,.79,.40,.3]) translate([2,25,22]) cube([10,21,13]);
 color([.25,.82,.52,.25]) translate([face_width-19,depth_total-10,14])
  cube([13,8,12]);
}
if(mode=="exterior"){
 color([.17,.20,.23,.98]) shell_geometry(); bottom_hatch();
 screen_envelopes(); keys_envelopes(); knob_encoder_envelopes();
}
else if(mode=="ghost"){
 color([.55,.66,.73,.20]) shell_geometry(); bottom_hatch();
 screen_envelopes(); keys_envelopes(); knob_encoder_envelopes();
 aw_expander(); service_envelopes();
}
else if(mode=="cutaway"){
 color([.48,.56,.65,.32]) difference(){
  shell_geometry();
  translate([-1,-1,-1])
   cube([face_width*.38,depth_total+2,height_total+2]);
 }
 bottom_hatch(); screen_envelopes();keys_envelopes();
 knob_encoder_envelopes();aw_expander();service_envelopes();
}
else if(mode=="shell_only"){
 color([.5,.59,.65]) shell_geometry(); bottom_hatch();
}
