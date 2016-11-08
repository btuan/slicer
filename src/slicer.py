#!/usr/bin/env python3

import math
import numpy as np

# Parameters, all defined in millimeters
DEFAULT_PARAMETERS = {
    "infill": 0.2,
    "perimeters": 1,
    "layer_height": 0.2,
    "nozzle_diameter": 0.4,
    "resolution": 0.1,
}


class Hexagon:
    """ Simple definition of points of a hexagon, with points scaled to parameter unit. """
    def __init__(self, unit):
        # Defined in points of (top, bottom, middle) and (left, right), e.g. denoted "bl" for "bottom left"
        self.mr = (unit * 0.5, unit * 0.0)
        self.tr = (unit * 0.5/2.0, unit * 0.5 * math.sqrt(3.0)/2.0)
        self.tl = (unit * (-0.5)/2.0, unit * 0.5 * math.sqrt(3.0)/2.0)
        self.ml = (unit * (-0.5), unit * 0.0)
        self.bl = (unit * (-0.5)/2.0, unit * 0.5 * (-math.sqrt(3.0)/2.0))
        self.br = (unit * 0.5/2.0, unit * 0.5 * (-math.sqrt(3.0)/2.0))


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
    infill = generate_infill_and_supports(auxdata, params, verbose)

    sliced = perimeters + infill
    sliced.sort(key=lambda x: x[0][2])

    return sliced


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
                perimeters += intersect(facet, z_ind, params, auxdata, verbose)

    if verbose:
        print("Perimeters generated.")

    # TODO: Sequence perimeters by closest to previous point.
    return perimeters


def generate_infill_and_supports(auxdata, params, verbose):
    if params["infill"] == 0:
        return []

    max_x = auxdata["x_max"] - auxdata["x_min"]
    max_y = auxdata["y_max"] - auxdata["y_min"]
    max_z = auxdata["z_max"] - auxdata["z_min"]
    unit = math.sqrt(max_x * max_y) * (1.00000001 - params["infill"]) / 2

    # Hexagonal infill. Define hexagonal tessellation absolute to coordinate system.
    horiz = []
    h = Hexagon(unit)
    for x_off in np.arange(0, max_x + unit * 1.5, unit * 1.5):
        horiz += [((h.mr[0] + x_off, h.mr[1]), (h.br[0] + x_off, h.br[1])),
                            ((h.bl[0] + x_off, h.bl[1]), (h.ml[0] + x_off, h.ml[1])),
                            ((h.ml[0] + x_off, h.ml[1]), (h.tl[0] + x_off, h.tl[1])),
                            ((h.tl[0] + x_off, h.tl[1]), (h.tr[0] + x_off, h.tr[1])),
                            ((h.tr[0] + x_off, h.tr[1]), (h.mr[0] + x_off, h.mr[1])),
                            ((h.mr[0] + x_off, h.mr[1]), (h.mr[0] + x_off + unit / 2, h.mr[1]))]

    vert = []
    for y_off in np.arange(0, max_y + unit * 0.5 * math.sqrt(3), unit * 0.5 * math.sqrt(3)):
        raw_tessellation = [((x1, y1 + y_off), (x2, y2 + y_off)) for ((x1, y1), (x2, y2)) in horiz]

        strict_in = [seg for seg in raw_tessellation if
                     0 <= seg[0][0] <= max_x and 0 <= seg[1][0] <= max_x and
                     0 <= seg[0][1] <= max_y and 0 <= seg[1][1] <= max_y]
        almost_in = [seg for seg in raw_tessellation if seg not in strict_in and
                     ((0 <= seg[0][0] <= max_x and 0 <= seg[0][1] <= max_y) or
                      (0 <= seg[1][0] <= max_x and 0 <= seg[1][1] <= max_y))]

        for ((x1, y1), (x2, y2)) in almost_in:
            x1, x2 = min(max(0, x1), max_x), min(max(0, x2), max_x)
            y1, y2 = min(max(0, y1), max_y), min(max(0, y2), max_x)
            vert.append(((x1, y1), (x2, y2)))

        vert += strict_in

    infill = []
    for z_off in np.arange(0, max_z, params["layer_height"]):
        infill += [((x1, y1, z_off), (x2, y2, z_off)) for ((x1, y1), (x2, y2)) in vert]

    return infill


# TODO: Factor out support material from infill patterns.
# def generate_supports():
#     pass


def intersect(facet, z_ind, params, auxdata, verbose):
    segments = []
    points_abv_layer = [vtx for vtx in facet["vertices"] if vtx[2] > z_ind + params["layer_height"]]
    points_blw_layer = [vtx for vtx in facet["vertices"] if vtx[2] < z_ind + params["layer_height"]]
    points_mid_layer = [vtx for vtx in facet["vertices"] if z_ind <= vtx[2] <= z_ind + params["layer_height"]]

    # Case 1, when facet is close to coplanar to build plate.
    if 1.0 - params["nozzle_diameter"] / 10.00 <= abs(facet["normal"][2]) \
            <= 1.0 + params["nozzle_diameter"] / 10.00:
        vertices = [vtx for vtx in facet["vertices"]]
        x_min = min(list(map(lambda x: x[0], vertices)))
        x_max = max(list(map(lambda x: x[0], vertices)))
        y_min = min(list(map(lambda y: y[1], vertices)))
        y_max = max(list(map(lambda y: y[1], vertices)))

        # TODO: Alternate x-y orientation of filament "scans" per even/odd layer.
        if True or (z_ind / params["layer_height"]) % 2 == 0:
            lefts = [vtx for vtx in vertices if vtx[0] == x_min]
            rights = [vtx for vtx in vertices if vtx[0] == x_max]
            centers = [vtx for vtx in vertices if vtx not in lefts and vtx not in rights]

            # Case 1, left side has collinear points on x-axis.
            def fill_case_1(left1, left2, right):
                xl1, yl1 = left1[0], left1[1]
                xl2, yl2 = left2[0], left2[1]
                xr, yr = right[0], right[1]

                for x_ind in np.arange(x_min, x_max + params["layer_height"], params["layer_height"]):
                    t1 = (x_ind - xl1) / (xr - xl1)
                    t2 = (x_ind - xl2) / (xr - xl2)
                    segments.append((
                        (x_ind, (yr - yl1) * t1 + yl1, z_ind),
                        (x_ind, (yr - yl2) * t2 + yl2, z_ind),
                    ))

            # Case 2, right side has collinear points on x-axis.
            def fill_case_2(left, right1, right2):
                xl, yl = left[0], left[1]
                xr1, yr1 = right1[0], right1[1]
                xr2, yr2 = right2[0], right2[1]

                for x_ind in np.arange(x_min, x_max + params["layer_height"], params["layer_height"]):
                    t1 = (x_ind - xl) / (xr1 - xl)
                    t2 = (x_ind - xl) / (xr2 - xl)
                    segments.append((
                        (x_ind, (yr1 - yl) * t1 + yl, z_ind),
                        (x_ind, (yr2 - yl) * t2 + yl, z_ind),
                    ))

            # Call the function that we've made for case 1.
            if len(lefts) == 2:
                fill_case_1(lefts[0], lefts[1], rights[0])

            elif len(rights) == 2:
                fill_case_2(lefts[0], rights[0], rights[1])

            # Case 3, no points are not collinear on x-axis. Degenerates to case 2 + case 1.
            else:
                # Find the midpoint on the line between the left and right affine equations.
                x_mid = centers[0][0]
                t = (x_mid - lefts[0][0]) / (rights[0][0] - lefts[0][0])
                y_mid = (rights[0][1] - lefts[0][1]) * t + lefts[0][1]
                midpoint = (x_mid, y_mid, z_ind)

                fill_case_2(lefts[0], centers[0], midpoint)
                fill_case_1(centers[0], midpoint, rights[0])

        else:
            # Scan horizontally, iterating from minimal y point, going to maximal y point.
            for y_ind in np.arange(y_min, y_max + params["layer_height"], params["layer_height"]):
                pass

    # Any other case, where facet is not oriented close to surface.
    else:
        # Case 1. One point amid layer. This is below our printing capability. Ignore this case.
        # Case 2. Two points in layer. Triangle inequality guarantees third point also in segment.
        if len(points_mid_layer) == 2:
            x1, y1, z1 = points_mid_layer[0][0], points_mid_layer[0][1], z_ind
            x2, y2, z2 = points_mid_layer[1][0], points_mid_layer[1][1], z_ind
            segments.append(((x1, y1, z1), (x2, y2, z2)))

        # Case 3. No points in layer.
        elif len(points_mid_layer) == 0:
            # Case 3a. Two points below layer.
            if len(points_blw_layer) == 2:
                px, py, pz = points_abv_layer[0][0], points_abv_layer[0][1], points_abv_layer[0][2]
                x1, y1, z1 = points_blw_layer[0][0], points_blw_layer[0][1], points_blw_layer[0][2]
                x2, y2, z2 = points_blw_layer[1][0], points_blw_layer[1][1], points_blw_layer[1][2]

            # Case 3b. Two points above layer.
            else:
                px, py, pz = points_blw_layer[0][0], points_blw_layer[0][1], points_blw_layer[0][2]
                x1, y1, z1 = points_abv_layer[0][0], points_abv_layer[0][1], points_abv_layer[0][2]
                x2, y2, z2 = points_abv_layer[1][0], points_abv_layer[1][1], points_abv_layer[1][2]

            # Generate parametric equations for the two lines and solve for x, y coordinates.
            t1 = (z_ind - pz) / (z1 - pz)
            t2 = (z_ind - pz) / (z2 - pz)

            # Calculate the intercepts of the lines with the z = z_ind plane.
            segments.append((
                ((x1 - px) * t1 + px, (y1 - py) * t1 + py, z_ind),
                ((x2 - px) * t2 + px, (y2 - py) * t2 + py, z_ind),
            ))

    # Round to a reasonable precision.
    precision = 5
    for ind, (p1, p2) in enumerate(segments):
        segments[ind] = (
            (round(p1[0], precision), round(p1[1], precision), round(p1[2], precision)),
            (round(p2[0], precision), round(p2[1], precision), round(p2[2], precision)),
        )

    return segments
