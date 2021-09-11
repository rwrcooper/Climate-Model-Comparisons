#!/usr/bin/env python3
"""
File: rlat_rlon_test.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Tests rlat and rlon WRF data with other cordex AUS-44 data.

Usage:
    rlat_rlon_test.py

Options:
    -h, --help
    --option=<n>
"""


from docopt import docopt
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def check_coordinates():
    path = "data-link/cordex-data/"

    clm_file = ("mon/AUS-44/tasmax/evaluation/ECMWF-ERAINT/CCLM4-8-17-CLM3-5/"
                "tasmax_AUS-44_ECMWF-ERAINT_evaluation_r1i1p1_"
                "CLMcom-CCLM4-8-17-CLM3-5_v1_mon_198101-199012.nc")
    clm_file = f"{path}/{clm_file}"

    wrf_file = ("mon/AUS-44/tasmax/evaluation/ECMWF-ERAINT/WRF360J/"
                "tasmax_AUS-44_ECMWF-ERAINT_evaluation_r1i1p1_"
                "UNSW-WRF360J_v1_mon_197901-198012.nc")
    wrf_file = f"{path}/{wrf_file}"

    clm = xr.open_dataset(clm_file)
    wrf = xr.open_dataset(wrf_file)
    wrf_correct = xr.open_dataset(wrf_file)
    # narclim = xr.open_dataset(f"{path}/cordex-wrf-test/sftlf_NARCliM.nc")
    cordex = xr.open_dataset(f"{path}/cordex-wrf-test/sftlf_AUS-44.nc")

    variables = {
        "clm": "tasmax",
        "wrf": "tasmax",
        "wrf_corrrect": "tasmax",
        # "cordex": "sftlf"
    }

    model_names = {
        "clm": clm,
        "wrf": wrf,
        "wrf_corrrect": wrf_correct,
        # "cordex": cordex
    }

    titles = {
        "clm": "CLMcom-CCLM4-8-17-CLM3-5",
        "wrf": "WRF original",
        "wrf_corrrect": "WRF corrected",
    }

    correct_rlon = cordex.coords["rlon"]
    correct_rlat = cordex.coords["rlat"]

    wrf_correct.coords["rlon"] = correct_rlon
    wrf_correct.coords["rlat"] = correct_rlat

    rotated_pole_map = ccrs.PlateCarree()

    fig, axes = plt.subplots(
        3, 1, subplot_kw=dict(projection=rotated_pole_map), figsize=(10, 7))

    for i, model in enumerate(model_names):
        ax = axes.ravel()[i]
        ax.coastlines()
        ax.gridlines(alpha=0.2)

        model_name = model

        model = model_names[model]
        model.coords["rlon"] = model.coords["rlon"] % 360

        if "rotated_pole" in model.data_vars:
            rotated_pole_c = ccrs.RotatedPole(
                model.rotated_pole.grid_north_pole_longitude,
                model.rotated_pole.grid_north_pole_latitude,
                central_rotated_longitude=0)
        else:
            rotated_pole_c = ccrs.RotatedPole(
                141.38,
                60.31,
                central_rotated_longitude=0)

        model = model[variables[model_name]][0]

        model.plot(ax=ax, transform=rotated_pole_c, add_colorbar=False)
        ax.set_title(titles[model_name])

    plt.savefig("plots/wrf_coord_test.png", bbox_inches='tight')
    print("plot saved to plots/coord_test1.png")


def main(args):

    check_coordinates()


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
