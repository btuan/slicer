#!/usr/bin/env python3

import math
import numpy as np

# Parameters, all defined in millimeters
DEFAULT_PARAMETERS = {
    "infill": 0.2,
    "perimeters": 1,
    "layer_height": 0.2,
    "nozzle_diam": 0.4,
}

REGULAR_HEXAGON = (
    (1.0, 0.0),
    (1.0/2.0, math.sqrt(3.0)/2.0),
    (-1.0/2.0, math.sqrt(3.0)/2.0),
    (-1.0, 0.0),
    (-1.0/2.0, -math.sqrt(3.0)/2.0),
    (1.0/2.0, -math.sqrt(3.0)/2.0),
)


def slice_model(parsed_stl, auxdata, params, verbose=False):
    # Use auxdata to perform offset calculation. Object should be aligned to Cartesian 0.
    off_x, off_y, off_z = -1.0 * auxdata["x_min"], -1.0 * auxdata["y_min"], -1.0 * auxdata["z_min"]
    if verbose:
        print("Offsets: {:+0.2f}x\t{:+0.2f}y\t{:+0.2f}z".format(off_x, off_y, off_z))

    # Sort the facets by minimum z-coordinate while applying offsets.
    parsed_stl.sort(key=lambda facet: min([vertex[2] for vertex in facet["vertices"]]))
    facets = [{"normal": d["normal"],
               "vertices": (
                   (d["vertices"][0][0] + off_x, d["vertices"][0][1] + off_y, d["vertices"][0][2] + off_z),
                   (d["vertices"][1][0] + off_x, d["vertices"][1][1] + off_y, d["vertices"][1][2] + off_z),
                   (d["vertices"][2][0] + off_x, d["vertices"][2][1] + off_y, d["vertices"][2][2] + off_z),
               )}
              for d in parsed_stl]

    perimeters = generate_perimeters(facets, auxdata, params, verbose)

    return parsed_stl


def generate_perimeters(facets, auxdata, params, verbose):
    if verbose:
        print("Generating perimeters.")

    # Quick function to round to arbitrary layer-height precision to a single decimal place.
    def my_round(x, base):
        return round(base * round(float(x) / base), 1)

    # Iterate over facets until inclusive maximal z-range is hit
    perimeters = []
    z_max = my_round(auxdata["z_max"] - auxdata["z_min"], params["layer_height"])
    for z_ind in np.arange(0, z_max + params["layer_height"], params["layer_height"]):
        for facet in facets:
            min_z = min([vertex[2] for vertex in facet["vertices"]])
            max_z = max([vertex[2] for vertex in facet["vertices"]])

            # Skip this iteration if facet is all above the current z-index.
            if min_z >= z_ind + params["layer_height"]:
                continue
            # SKip this iteration if facet is all below the current z-index.
            elif max_z < z_ind:
                continue
            # Otherwise, calculate the intersection of this facet
            else:
                perimeters += intersect(facet, z_ind, params)

    if verbose:
        print("Perimeters generated.")

    return perimeters


def generate_infill():
    # Hexagonal infill. Define hexagonal tessellation absolute relative to coordinate system.
    # Next perimeter is always going to be the opposite direction.
    pass


def generate_supports():
    pass


def intersect(facet, layer, params):
    # Determine top/bottom layers by normal vector orientation.
    # Check min and max of each layer for intersections.
    segments = []

    # Simple case, when facet is close to perpendicular, take average segment.
    if facet["normal"][2] < params["nozzle_diameter"] / 10.0:
        pass

    # Other simple case, when facet is close to coplanar to build plate.
    elif 1.0 - params["nozzle_diameter"] / 10.00 <= abs(facet["normal"][2]) \
           <= 1.0 + params["nozzle_diameter"] / 10.00:
        pass

    # Complex case, projecting facet onto trapezoid. When facet has some z-normal.
    else:
        pass

    return segments


