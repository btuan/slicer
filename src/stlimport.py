#!/usr/bin/env python3


def parse_stl(stlpath, verbose=False):
    parsed = []

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

                parsed[-1].get("vertices", []).append(
                    tuple(map(float, line.split()[1:]))
                )

    return parsed

