// HyraX wrist module - Mark I case (Phase 4, ESP32)
// Units: mm throughout.
// part = "shell" | "diffuser" | "back" | "preview" (all three laid out)

part = "preview";

// ---------------------------------------------------------------------
// Core dimensions - edit these as real parts get measured
// ---------------------------------------------------------------------
case_d        = 45;     // outer case diameter (bold scale)
wall          = 2;      // side wall thickness
shell_h       = 16;     // main shell height, rim to top face

groove_depth  = 1;      // diffuser ring groove, at the very top
groove_d      = 38;
bezel_depth   = 2;      // visible window band (narrowest opening)
bezel_d       = 32;
pocket_depth  = 3;      // recess where the round display PCB seats
pocket_d      = 35;

inner_d       = case_d - 2*wall;   // main electronics cavity diameter
back_h        = 2;                 // back plate thickness
back_clear    = 0.3;               // friction-fit clearance

mic_d         = 2.5;
mic_angle     = 200;
button_d      = 3.5;
button_angle  = -20;
speaker_hole_d = 1.2;
speaker_hole_count = 7;
speaker_angle  = 110;
speaker_z      = 6;

lug_width  = 5;
lug_length = 7;
lug_height = 4;
lug_hole_d = 1.8;

$fn = 100;

// ---------------------------------------------------------------------
// Strap lug, protrudes from rim at 12 o'clock; mirror for 6 o'clock
// ---------------------------------------------------------------------
module lug() {
    translate([-lug_width/2, case_d/2 - 5, shell_h/2 - lug_height/2])
    difference() {
        cube([lug_width, lug_length, lug_height]);
        translate([lug_width/2, lug_length - 2, lug_height/2])
            rotate([0,90,0])
                cylinder(d=lug_hole_d, h=lug_width+4, center=true);
    }
}

module radial_hole(angle, z, dia) {
    rotate([0,0,angle])
        translate([case_d/2 - wall, 0, z])
            rotate([0,90,0])
                cylinder(d=dia, h=wall*4, center=true);
}

// ---------------------------------------------------------------------
// Main shell: face with display window/pocket, mic, button, speaker
// grille, strap lugs, open electronics bay at the bottom.
// ---------------------------------------------------------------------
module case_shell() {
    difference() {
        union() {
            cylinder(d=case_d, h=shell_h);
            lug();
            mirror([0,1,0]) lug();
        }

        // diffuser groove + start of the display opening
        translate([0,0, shell_h - groove_depth])
            cylinder(d=groove_d, h=groove_depth + 0.5);

        // visible bezel window (narrowest point)
        translate([0,0, shell_h - groove_depth - bezel_depth])
            cylinder(d=bezel_d, h=bezel_depth + 0.5);

        // pocket for the round display PCB
        translate([0,0, shell_h - groove_depth - bezel_depth - pocket_depth])
            cylinder(d=pocket_d, h=pocket_depth + 0.5);

        // main electronics bay, open at the bottom rim
        cylinder(d=inner_d, h=shell_h - groove_depth - bezel_depth - pocket_depth + 0.5);

        // mic port
        radial_hole(mic_angle, shell_h/2, mic_d);

        // button hole
        radial_hole(button_angle, shell_h/2, button_d);

        // speaker grille cluster
        for (i = [0:speaker_hole_count-1]) {
            rotate([0,0, speaker_angle + i*6 - (speaker_hole_count-1)*3])
                radial_hole(speaker_angle + i*6 - (speaker_hole_count-1)*3, speaker_z, speaker_hole_d);
        }
    }
}

// ---------------------------------------------------------------------
// Diffuser ring: translucent insert, sits in the groove around the
// display window for the LED edge-glow effect.
// ---------------------------------------------------------------------
module diffuser_ring() {
    linear_extrude(height = groove_depth + 0.4)
        difference() {
            circle(d = groove_d - 0.2);
            circle(d = bezel_d + 0.2);
        }
}

// ---------------------------------------------------------------------
// Back plate: friction-fit cap that closes the electronics bay.
// ---------------------------------------------------------------------
module back_plate() {
    difference() {
        cylinder(d = inner_d - back_clear, h = back_h);
        // center vent slot for the battery compartment
        translate([0,-1,-0.5])
            cube([10, 2, back_h + 1]);
        // two finger notches for prying it back out
        translate([inner_d/2 - 4, 0, -0.5]) cylinder(d=6, h=back_h+1);
        translate([-(inner_d/2 - 4), 0, -0.5]) cylinder(d=6, h=back_h+1);
    }
}

// ---------------------------------------------------------------------
// Render selection
// ---------------------------------------------------------------------
if (part == "shell") {
    case_shell();
} else if (part == "diffuser") {
    diffuser_ring();
} else if (part == "back") {
    back_plate();
} else {
    // preview: all three parts laid out side by side for inspection
    case_shell();
    translate([70, 0, 0]) diffuser_ring();
    translate([130, 0, 0]) back_plate();
}
