#!/usr/bin/env python3
"""
File: cordex_eur_domain_test.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    script to test projections and lat/lons, not needed anymore.

Usage:
    slope_plots_cordex.py

Options:

    -h, --help
    --option=<n>
"""


import xarray as xr
import matplotlib.pyplot as plt
from docopt import docopt
import cartopy.crs as ccrs


def make_plot():

    path = ("data-link/cordex-data/mon/EUR-44/pr/combined_rcp85/"
            "MPI-M-MPI-ESM-LR/RCA4/pr_EUR-44_MPI-M-MPI-ESM-LR_rcp85_r1i1p1"
            "_SMHI-RCA4_v1_mon_1950-2100_yearmax.nc")

    ds = xr.open_dataset(path)

    ds = ds.isel(time=0)

    # __import__('IPython').embed()

    rotated_pole_map = ccrs.RotatedPole(
        pole_longitude=-162.0,
        pole_latitude=39.25,
        central_rotated_longitude=0)  # 49.68)

    ax = plt.axes(projection=rotated_pole_map)
    ax.coastlines()
    ax.gridlines(alpha=0.2)

    ds.data_vars["pr"].plot(ax=ax, transform=rotated_pole_map, cmap="GnBu")

    plt.show()


def main(args):

    make_plot()


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
