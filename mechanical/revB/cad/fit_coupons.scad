/* Rev B component-mount fit coupons; NOT a finished enclosure or switch specification.
   Print five separate 24 x 24 mm coupons in left-to-right order.
   #1 MX 14.0mm nominal square, 1.5mm thick
   #2 MX 14.2mm trial square, 1.5mm thick
   #3 encoder dia 7.0mm, 3.0mm panel
   #4 encoder dia 7.3mm, 3.0mm panel
   #5 encoder dia 7.3mm, 1.5mm panel
   All tolerances approximate; test with the exact owned MX and Adafruit PID 377.
   Check snap engagement, nut/washer support, grub screw and push-click travel.
*/
$fn=80;
tile=24;
pitch=29;

module mx_cutout(cut=14.0,thick=1.5) {
    difference() {
        cube([tile,tile,thick]);
        translate([tile/2,tile/2,-0.5])
            linear_extrude(thick+1) square([cut,cut],center=true);
    }
}

module encoder_cutout(bore=7.3,thick=3) {
    difference() {
        cube([tile,tile,thick]);
        translate([tile/2,tile/2,-0.5]) cylinder(d=bore,h=thick+1);
    }
}

translate([0*pitch,0,0]) mx_cutout(14.0,1.5);
translate([1*pitch,0,0]) mx_cutout(14.2,1.5);
translate([2*pitch,0,0]) encoder_cutout(7.0,3.0);
translate([3*pitch,0,0]) encoder_cutout(7.3,3.0);
translate([4*pitch,0,0]) encoder_cutout(7.3,1.5);
