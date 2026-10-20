// Spotify Desk Thing - Phase 6 envelope study - REFERENCE ONLY, NOT A PRINTABLE CASE
// Units: mm. No drill holes, wall design, switch retention or display recess is certified.
// trial=0 compact 150x105; trial=1 roomy 165x110 (leading candidate).
trial=1;
$fn=64;
panel_w=trial==0 ? 150 : 165;
panel_h=trial==0 ? 105 : 110;
panel_t=3; // placeholder only, not verified
screen_xy=trial==0 ? [8,7] : [11,8];
key_centres=trial==0 ? [39,69,99] : [40,70,100];
key_y=trial==0 ? 86 : 91;
knob_xy=trial==0 ? [131,41] : [142,44];
screen_size=[106.1,67.8]; // exact touch display outer envelope nominal
active_offset=[5.23,4.35]; active_size=[95.54,54.36];
knob_d=15.1; knob_total_h=15.2; // KZ0087 listed dimensions
encoder_body=[13.2,13.2,13.2]; // Z depth placeholder, not a verified package dimension
mx_cap=[18,18,7]; // z visible height illustrative
mx_switch=[14,14,14]; // plate opening reference; z depth illustrative
aw_board=[38,23,1.6]; // AW9523B x/y manufacturer; z thickness illustrative
// XY top-left origin in drawings; z=0 front-face plane, negative behind face.
// Purple markers are nominal projected rear-board mounting centres, NOT drill holes.
module study() {
 color([.9,.94,.97,.22]) translate([0,0,-panel_t]) cube([panel_w,panel_h,panel_t]);
 color([.12,.31,.43,.78]) translate([screen_xy[0],screen_xy[1],-.5]) cube([screen_size[0],screen_size[1],1]);
 color([.03,.52,.62,.83]) translate([screen_xy[0]+active_offset[0],screen_xy[1]+active_offset[1],.55]) cube([active_size[0],active_size[1],.2]);
 for (xx=[4,102],yy=[4,64])
   color([.65,.38,.75,.9]) translate([screen_xy[0]+xx,screen_xy[1]+yy,-2]) cylinder(d=2,h=3);
 for (i=[0:2]) {
  color([.18,.20,.27]) translate([key_centres[i]-9,key_y-9,1]) cube(mx_cap);
  color([.13,.49,.57,.53]) translate([key_centres[i]-7,key_y-7,-17]) cube(mx_switch);
 }
 color([.21,.25,.29]) translate([knob_xy[0],knob_xy[1],2]) cylinder(d=knob_d,h=knob_total_h);
 color([.65,.65,.71,.52]) translate([knob_xy[0]-6.6,knob_xy[1]-6.6,-16]) cube(encoder_body);
 // Placeholder right-side I2C cable corridor: 14 mm is an ASSUMPTION.
 color([1,.54,.12,.27]) translate([screen_xy[0]+106.1,screen_xy[1]+27,-9]) cube([14,26,9]);
 // AW expansion board is on DIFFERENT mounting depth; no standoff spec.
 color([.65,.33,.68,.5]) translate([screen_xy[0]+42,screen_xy[1]+21,-29]) cube(aw_board);
}
study();
