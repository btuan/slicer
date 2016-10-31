#!/usr/bin/env python3

import click
from pprint import PrettyPrinter

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

    parsed = stlimport.parse_stl(stl, verbose=verbose)

    if verbose:
        print("Output of parsed STL:")
        pprint(parsed)
        print("")

    if verbose:
        print("Done.")


if __name__ == "__main__":
    run()

