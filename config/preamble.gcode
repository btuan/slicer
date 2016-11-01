M106 ; fan on
M190 S75 ; set bed temperature
M104 S190 ; set temperature
G28 ; home all axes
G1 Z5 F5000 ; lift nozzle

M109 S190 ; wait for temperature to be reached
G21 ; set units to millimeters
G90 ; use absolute coordinates
M82 ; use absolute distances for extrusion

G92 E0
G1 Z0.300 F1500.00

