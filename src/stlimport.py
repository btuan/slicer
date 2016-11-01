#!/usr/bin/env python3


def parse_stl(stlpath, verbose=False):
    """
    Parses an STL mesh into a list of dictionaries representing facets.

    stlpath  --     path to STL file input
    verbose  --     verbosity boolean

    Returns
        parsed
            List of dictionaries, with the following form:
            {
                "normal"    :   (n1, n2, n3),
                "vertices"  :   [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3)]
            }

        auxdata
            Dictionary of auxiliary metadata scraped through iteration.
            {
                "x_min"     :   float,
                "x_max"     :   float,
                "y_min"     :   float,
                "y_max"     :   float,
                "z_min"     :   float,
                "z_max"     :   float
            }
    """
    parsed = []
    auxdata = {
        "x_min": None,
        "x_max": None,
        "y_min": None,
        "y_max": None,
        "z_min": None,
        "z_max": None,
    }

    with open(stlpath, "r") as f:
        for line in f:
            line = line.strip()

            # First line of the ASCII file definition
            if line == "solid ASCII":
                continue

            # Add a new facet to the object.
            elif line.startswith("facet normal"):
                parsed.append({
                    "normal": tuple(map(float, line.split()[2:]))
                })

            # Add a point to the previously appended facet.
            elif line.startswith("vertex"):
                if "vertices" not in parsed[-1]:
                    parsed[-1]["vertices"] = []

                parsed[-1]["vertices"].append(tuple(map(float, line.split()[1:])))

                # Update auxiliary metadata parameters.
                x, y, z = parsed[-1]["vertices"][-1]

                if auxdata["x_min"] is None or x < auxdata["x_min"]:
                    auxdata["x_min"] = x
                if auxdata["x_max"] is None or x > auxdata["x_max"]:
                    auxdata["x_max"] = x

                if auxdata["y_min"] is None or y < auxdata["y_min"]:
                    auxdata["y_min"] = y
                if auxdata["y_max"] is None or y > auxdata["y_max"]:
                    auxdata["y_max"] = y

                if auxdata["z_min"] is None or z < auxdata["z_min"]:
                    auxdata["z_min"] = z
                if auxdata["z_max"] is None or z > auxdata["z_max"]:
                    auxdata["z_max"] = z

    return parsed, auxdata

