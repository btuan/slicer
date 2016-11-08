#!/bin/bash
set -e

if [[ ! -e gcode/ ]]; then mkdir gcode/; fi

for x in $(find models/*|awk '{match($1,"/.*stl$");print(substr($1,RSTART+1,RLENGTH-5))}')
do
    echo -n "Slicing models/$x.stl..."
	time python3 ./src/main.py --stl models/$x.stl --preamble config/preamble.gcode --cleanup config/cleanup.gcode --outpath gcode/$x.gcode
    echo -e "Done.\n"
done

echo "Sliced model gcode in directory gcode/"
ls gcode/
