#!/usr/bin/env python3

import math


def export(sliced, preamble, cleanup, outpath, verbose):
    f = open(outpath, "w")

    if preamble is not None:
        with open(preamble, "r") as g:
            for line in g:
                print(line.strip(), file=f)

    e_off = 0
    for (x1, y1, z1), (x2, y2, z2) in sliced:
        if e_off > 100:
            e_off = 0
            print("G92 E0", file=f)

        e_dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        print("G1 X{:0.5f} Y{:0.5f} Z{:0.5f}".format(x1, y1, z1), file=f)
        print("G1 X{:0.5f} Y{:0.5f} E{:0.5f}".format(x2, y2, e_off + e_dist), file=f)
        e_off += e_dist

    if cleanup is not None:
        with open(cleanup, "r") as g:
            for line in g:
                print(line.strip(), file=f)

