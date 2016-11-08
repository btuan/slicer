# A Simple Slicer
Brian Tuan

Ideally should slice STL meshes into G-Code toolpaths.

Tested on a few geometric primitives (sphere, cube, etc.).
GCode read at `images/HollowCylinder.png`.

Hosted at http://github.com/btuan/slicer

## Slicing Philosophy
Models are sliced from bottom to top, with supports and infill being the same
hexagonal honeycomb pattern as specified by infill parameters. Default params
are located at the top of the `src/slicer.py` file and may be modified to de-
sire. Further specification of infill vs supports may be added in the future.

## Usage
Help menu:
```
$ ./src/main.py --help
Usage: main.py [OPTIONS]

Options:
  --stl TEXT       Path to input STL file.
  --preamble TEXT  Path to GCode preamble.
  --cleanup TEXT   Path to GCode cleanup.
  --outpath TEXT   Path to output location of GCode.
  -v, --verbose    Toggle to True for verbosity.
  --help           Show this message and exit.
```

Example run:
```
$ ./src/main.py --stl models/10uCubeRef.stl --preamble config/preamble.gcode --cleanup config/cleanup.gcode --outpath out.gcode
```

Automated testing:
```
$ ./make_models.sh
```
