#!/usr/bin/env python3
"""
File: multi_model_slope_analysis.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Makes slope plots as seen in Gitlab issues.

Usage:
    slope_plots_cordex.py make-plots -d <domain> [-v <var_option]

Options:
    -d <domain>, --domain=<domain>
    -v <var_option>, --var_option=<var_option>

    -h, --help
    --option=<n>
"""


import xarray as xr
import matplotlib.pyplot as plt
from docopt import docopt
import numpy as np
import matplotlib.colors as colors
import matplotlib.cm as cm
import cartopy.crs as ccrs
import os
from ds_store_remover import ds_store_remover


'''
scale_factors = {
    "heat": 1,
    "drought": 31536000,
    "wind": 1,
    "flood": 86400,
    "HDW_proxy": 1
}

metrics = {
    "heat": "tasmax",
    "drought": "precipitation",
    "wind": "sfcWindmax",
    "flood": "pr_max",
    "HDW_proxy": "hdw_proxy"
}

long_names = {
    "heat": "Daily Maximum Near-Surface Air Temperature",
    "drought": "Precipitation",
    "wind": "Daily Maximum Near-Surface Wind Speed",
    "flood": "Precipitation",
    "HDW_proxy": "HDW_proxy"
}

units = {
    "heat": "K",
    "drought": "mm/year",
    "wind": "m/s",
    "flood": "mm/day",
    "HDW_proxy": ""
}
'''


labels = {
    "timmean": {
        "pr_yearmax": "Maximum daily precipitation (mm/s)",
        "pr_yearsum": "Total annual precipitation (mm/s)",
        "sfcWindmax": "Maxmimum annual wind speed (m/s)",
        "tasmax": "Maximum annual heat (K)",
        "hurs": "Maximum annual humidity (%)"
        },
    "slope": {
        "pr_yearmax": "Change in maximum daily precipitation (mm/s)",
        "pr_yearsum": "Change in total annual precipitation (mm/s)",
        "sfcWindmax": "Change in maxmimum annual wind speed (m/s)",
        "tasmax": "Change in maximum annual heat (K)",
        "hurs": "Change in maximum annual humidity (%)"
        },
}


def plot_model_type(domain, data_sets, cmap, axes, add, var, vmin, vmax, fig,
                    model_names, type, labels, centered_log=False, skip=2,
                    slope_log=False):
    '''Makes plots of slopes or timemeans of a variable and domain combo. '''

    for i, model in enumerate(model_names):
        ax = axes.ravel()[i*skip+add]

        ax.coastlines()
        ax.gridlines(alpha=0.2)

        # hack to just remove the right portion of the data causing issue
        if domain == "AUS-44":
            ax.set_extent([88, 180, -55, 12], crs=ccrs.PlateCarree())

        ds = data_sets[model]

        if domain == "EUR-44":
            pole_longitude = -162.0
            pole_latitude = 39.25
        elif domain == "AFR-44":
            pole_longitude = 180
            pole_latitude = 90
        elif domain == "AUS-44":
            pole_longitude = -321.38+180
            pole_latitude = -60.31
        elif domain == "EAS-44":
            pole_longitude = -64.78
            pole_latitude = 77.61
        elif domain == "SAM-44":
            pole_longitude = -56.06
            pole_latitude = 70.6
        elif domain == "NAM-44":
            pole_longitude = 83.0
            pole_latitude = 42.5
        elif domain == "CAM-44":
            pole_longitude = 113.98
            pole_latitude = 75.74

        central_rotated_longitude = 0

        rotated_pole_c = ccrs.RotatedPole(
            pole_longitude, pole_latitude, central_rotated_longitude)

        if centered_log:
            vmax = max(-vmin, vmax)
            vmin = -vmax
        '''
        ds = ds.where(
            (ds.coords["rlon"] >= ds.coords["rlon"].min()) &
            (ds.coords["rlon"] <= ds.coords["rlon"].max()),
            drop=True)

        ds = ds.where(
            (ds.coords["lon"] >= ds.coords["lon"].min()) &
            (ds.coords["lon"] <= ds.coords["lon"].max()),
            drop=True)
        '''

        if "rlon" in ds.coords:
            xvar = "rlon"
            yvar = "rlat"
        else:
            xvar = "x"
            yvar = "y"

        print("Trying to plot:")
        print(f"Model: {model}")

        if model == "ICHEC-EC-EARTH_CCLM4-8-17-CLM3-5":
            __import__('IPython').embed()

        # fix "looped" rlons
        if "rlon" in ds.coords:
            if any(ds.coords["rlon"] > 180):
                ds.coords["rlon"] = (
                    ((ds.coords["rlon"] + 180) % 360) - 180)

        if domain == "SAM-44":
            ds.coords["rlon"] = ds.coords["rlon"] % 360

        ds = ds.data_vars[var]

        ds.plot(
            ax=ax, transform=rotated_pole_c, vmin=vmin, vmax=vmax, cmap=cmap,
            add_colorbar=False)  # ), x=xvar, y=yvar)

        print("Plot succesful")

        # TODO: this isn't general
        # this bit of code is not ideal
        if var == "hurs":
            ii = 1
        elif var == "sfcWindmax":
            ii = 4
        elif domain == "NAM-44":  # test
            # if var == "pr":
            ii = 1
        elif domain == "EAS-44":
            if var == "pr":
                ii = 3
        else:
            ii = 4
        if i == ii:
            cbar_ax = fig.add_axes([0.14+add*0.42, 0.08, 0.33, 0.015])
            norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
            mappable = cm.ScalarMappable(norm=norm, cmap=cmap)

            if var == "pr":
                var_type = f"pr_{type}"
            else:
                var_type = var
            if add == 0:
                label = labels["timmean"][var_type]
            elif add == 1:
                label = labels["slope"][var_type]
            plt.colorbar(orientation="horizontal", mappable=mappable,
                         cax=cbar_ax, label=label)


def make_plot(domain, var_option):
    '''executes the making of plots, considers variable option from args'''

    path = "data-link/cordex-data"
    path_domain = f"{path}/mon/{domain}"

    if var_option is None:
        vars = ds_store_remover(os.listdir(path_domain))
    else:
        vars = [var_option]

    for var in vars:

        path_var = f"{path_domain}/{var}"

        make_plots_var(domain, var, path, path_var, type="yearmax")

        if var == "pr":

            make_plots_var(domain, var, path, path_var, type="yearsum")

    return


def make_plots_var(domain, var, path, path_var, type):
    '''makes plots for a particular variable'''

    path_slope = f"{path_var}/slope"
    path_timmean = f"{path_var}/timmean"

    model_names = []
    slopes = {}
    timmeans = {}

    slopes_min = []
    slopes_max = []

    timmean_min = []
    timmean_max = []

    driving_models = ds_store_remover(os.listdir(path_slope))

    for driving_model in driving_models:
        path_driving_model = f"{path_slope}/{driving_model}"
        rcms = ds_store_remover(os.listdir(path_driving_model))

        for rcm in rcms:
            # TODO: could make the following into a function for reuse
            # SLOPE
            path_rcm = f"{path_driving_model}/{rcm}"
            model_name = f"{driving_model}_{rcm}"
            model_names.append(model_name)

            files = ds_store_remover(os.listdir(path_rcm))
            files = [file for file in files if type in file]
            files = [file for file in files if type in file]
            file = files[0]

            data_set = xr.open_dataset(f"{path_rcm}/{file}").isel(time=0)

            if domain == "AUS-44":

                if var == "pr":
                    if model_name == "ICHEC-EC-EARTH_CCLM4-8-17-CLM3-5":
                        data_set[var] = data_set[var]/24
                    elif model_name == "MPI-M-MPI-ESM-LR_CCLM4-8-17-CLM3-5":
                        data_set[var] = data_set[var]/24

            # here would be the place to scale data if wanted

            # testing
            print("\n")
            print("\n")
            print("Testing:")
            print(f"Path: {path}")
            print(f"Domain: {domain}")
            print(f"Var: {var}")
            print(f"Driving model: {driving_model}")
            print(f"RCM: {rcm}")
            print(f"Type: {type}")

            if "rlon" in data_set.coords:
                data_set.coords["rlon"] = data_set.coords["rlon"] % 360

            # this might need to be edited on the fly to make more defined
            if var == "sfcWindmax":
                slopes_min.append(data_set[var].quantile(0.1))
                slopes_max.append(data_set[var].quantile(0.9))
            if var == "hurs":
                slopes_min.append(data_set[var].quantile(0.2))
                slopes_max.append(data_set[var].quantile(0.8))
            if var == "pr":
                slopes_min.append(data_set[var].quantile(0.1))
                slopes_max.append(data_set[var].quantile(0.9))
            elif var == "tasmax":
                slopes_min.append(data_set[var].quantile(0.05))
                slopes_max.append(data_set[var].quantile(0.95))
            else:
                slopes_min.append(data_set[var].min())
                slopes_max.append(data_set[var].max())

            slopes[model_name] = data_set

            # TIMMEAN
            # TODO: this and the part above are similar and could be general
            path_rcm = f"{path_timmean}/{driving_model}/{rcm}"

            files = ds_store_remover(os.listdir(path_rcm))
            files = [file for file in files if type in file]
            files = [file for file in files if type in file]
            file = files[0]

            data_set = xr.open_dataset(f"{path_rcm}/{file}")

            if domain == "AUS-44":

                if var == "pr":
                    if model_name == "ICHEC-EC-EARTH_CCLM4-8-17-CLM3-5":
                        data_set[var] = data_set[var]/24
                    elif model_name == "MPI-M-MPI-ESM-LR_CCLM4-8-17-CLM3-5":
                        data_set[var] = data_set[var]/24

            if var == "pr":
                timmean_min.append(data_set[var].quantile(0.01))
                timmean_max.append(data_set[var].quantile(0.99))
            else:
                timmean_min.append(data_set[var].min())
                timmean_max.append(data_set[var].max())

            timmeans[model_name] = data_set

    vmax_s, vmin_s = np.max(slopes_max), np.min(slopes_min)
    vmax_t, vmin_t = np.max(timmean_max), np.min(timmean_min)

    if domain == "EUR-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=-162.0,
             pole_latitude=39.25,
             central_rotated_longitude=0)
    elif domain == "AFR-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=180,
             pole_latitude=90,
             central_rotated_longitude=0)
    elif domain == "AUS-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=-321.38+180,
             pole_latitude=-60.31,
             central_rotated_longitude=0)
    elif domain == "EAS-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=-64.78,
             pole_latitude=77.61,
             central_rotated_longitude=0)
    elif domain == "SAM-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=-56.06,
             pole_latitude=70.6,
             central_rotated_longitude=0)
        # to fix the projection
        rp = rotated_pole_map
        map_crs = ccrs.RotatedPole(
            rp.proj4_params['lon_0'] - 180,
            rp.proj4_params['o_lat_p'],
            rp.proj4_params['o_lon_p'] + 180)
        rotated_pole_map = map_crs
    elif domain == "NAM-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=83.0,
             pole_latitude=42.5,
             central_rotated_longitude=0)
    elif domain == "CAM-44":
        rotated_pole_map = ccrs.RotatedPole(
             pole_longitude=113.98,
             pole_latitude=75.74,
             central_rotated_longitude=0)

    print("Model Names:")
    for mn in model_names:
        print(mn)

    aspect_ratio = 1.0
    wid = 20
    hi = wid * aspect_ratio

    nrows, ncols = len(model_names), 2

    fig, axes = plt.subplots(nrows, ncols,
                             subplot_kw=dict(projection=rotated_pole_map),
                             figsize=(wid, hi))

    if var == "pr":
        cmap = "Blues"
    elif var == "hurs":
        cmap = "Blues"
    else:
        cmap = "inferno"

    plot_model_type(domain=domain, data_sets=timmeans, cmap=cmap, axes=axes,
                    add=0, var=var, vmin=vmin_t, vmax=vmax_t, fig=fig,
                    model_names=model_names, type=type, labels=labels)

    if var == "pr":
        cmap = "RdBu"
        centered_log = True
    elif var == "hurs":
        cmap = "RdBu"
        centered_log = True
    elif var == "tasmax":
        cmap = "inferno"
        centered_log = False
    else:
        cmap = "RdBu_r"
        centered_log = True

    plot_model_type(domain=domain, data_sets=slopes, cmap=cmap, axes=axes,
                    add=1, var=var, vmin=vmin_s, vmax=vmax_s, fig=fig,
                    model_names=model_names, type=type, labels=labels,
                    slope_log=True, centered_log=centered_log)

    for mn in model_names:
        print(mn+"\n")

    for i, model_name in enumerate(model_names):
        for j, col in enumerate(["Timmean", "Slope"]):
            ax = axes[i, j]
            if i == 0:
                ax.set_title(col, size=22)
            else:
                ax.set_title("")

            if j == 0:
                ax.text(-0.07, 0.55, model_name, va='bottom', ha='center',
                        rotation='vertical', rotation_mode='anchor',
                        transform=ax.transAxes, size=12)

    plt.draw()

    xmin, xmax = ax.get_xbound()
    ymin, ymax = ax.get_ybound()
    y2x_ratio = (ymax-ymin)/(xmax-xmin) * nrows/ncols

    fig.set_figheight(wid * y2x_ratio)

    # title = f"Slope of trend and bias estimate for {var} metric."
    # fig.suptitle(title, size=30)

    save_path = f"{path}/plots/{domain}/slope"
    os.makedirs(save_path, exist_ok=True)
    save_file = f"{var}_{type}_slope.png"

    save_path = f"{save_path}/{save_file}"

    save_statement = f"Saving slope plots for domain: {domain}, variable: "
    save_statement = f"{save_statement}{var}, type: {type} to: {save_path}."
    print(save_statement)
    plt.savefig(save_path, bbox_inches='tight')


def main(args):

    if args['make-plots']:

        domain = args['--domain']

        if '--var_option' in args:
            var_option = args['--var_option']
        else:
            var_option = None

        make_plot(domain, var_option)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
