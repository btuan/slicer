# A Simple Slicer
Brian Tuan

Ideally should slice STL meshes into G-Code toolpaths.

Tested on a few geometric primitives (sphere, cube, etc.).

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
