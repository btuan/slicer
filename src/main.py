#!/usr/bin/env python3

import click
from copy import deepcopy
from pprint import PrettyPrinter

import slicer
import stlimport


@click.command()
@click.option("--stl", help="Path to input STL file.")
@click.option("-v", "--verbose", default=False, is_flag=True, help="Toggle to True for verbosity.")
def run(stl, verbose):
    # Initialize verbose logger.
    p = PrettyPrinter(indent=4)
    pprint = p.pprint

    if verbose:
        print("Loading STL: '{}'\n".format(stl))

    # Parse the STL mesh into a form we can work with.
    parsed, auxdata = stlimport.parse_stl(stl, verbose=verbose)
    if verbose:
        print("Output of parsed STL:")
        pprint(parsed)
        print("\nAuxiliary metadata:")
        pprint(auxdata)
        print("STL mesh ingestion done.\n")

    # Slice the parsed STL mesh
    params = deepcopy(slicer.DEFAULT_PARAMETERS)
    sliced = slicer.slice_model(parsed, auxdata, params, verbose=verbose)
    if verbose:
        print("Output of sliced mesh:")
        pprint(sliced)
        print("Slicing done.\n")

    # DONE

if __name__ == "__main__":
    run()

