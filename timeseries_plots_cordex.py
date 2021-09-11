#!/usr/bin/env python3
"""
File: timeseries_plots_cordex.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Script for creation of timeseries plots of a hazard for cities in a domain.

Usage:
    timeseries_plots_cordex.py make-plots -d <domain> [-v <var_option]

Options:
    -d <domain>, --domain=<domain>
    -v <var_option>, --var_option=<var_option>

    -h, --help
    --option=<n>
"""


import xarray as xr
import matplotlib.pyplot as plt
from docopt import docopt
from csaps import csaps
import pandas as pd
import os
from ds_store_remover import ds_store_remover
import json


# load cities_lat_lon
dict = open("cities_lat_lon.json")
cities_lat_lon = json.load(dict)


# load city_long_names
dict = open("city_long_names.json")
city_long_names = json.load(dict)


def smoother(data, smoothing=1e-3):
    '''Smooths timeseries data for better visualisation of trend in a plot. '''

    spline_fn = csaps(data.index.year, data.values, smooth=smoothing)
    predictions = pd.Series(spline_fn(data.index.year), index=data.index)

    return predictions


def make_colors(data_path, domain, var):
    '''makes a list of colours depending on how many are needed for a
    particular domain variable.'''

    colors = {}

    # TODO: will need to add more colors depending on number of models
    # TODO: make a better colouring system
    # length = 22
    color_list = [
        "tab:blue",
        "tab:orange",
        "tab:red",
        "tab:green",
        "tab:purple",
        "tab:brown",
        "tab:pink",
        "tab:cyan",
        "cornflowerblue",
        "midnightblue",
        "lime",
        "darkred",
        "lightcoral",
        "darkmagenta",
        "deeppink",
        "turquoise",
        "sandybrown",
        "darkslategrey",
        "darkgoldenrod",
        "mediumslateblue",
        "mediumspringgreen",
        "gold",
        "gold", # testing from here on
        "gold",
        "gold",
        "gold",
        "gold",
        "gold",
        "gold",
        "gold",
    ]

    path_timeseries = f"{data_path}/{domain}/{var}/timeseries"

    counter = 0

    driving_models = ds_store_remover(os.listdir(path_timeseries))
    driving_models = [dm for dm in driving_models if dm != "ECMWF-ERAINT"]
    for driving_model in driving_models:
        rcms = ds_store_remover(
            os.listdir(f"{path_timeseries}/{driving_model}"))
        for rcm in rcms:
            model_name = f"{driving_model}_{rcm}"
            colors[model_name] = color_list[counter]
            counter = counter + 1
    return colors


def make_plots(domain, var_option):
    '''produce plots for all variables'''
    data_path = "data-link/cordex-data/mon"
    plot_path = "data-link/cordex-data/plots"

    if var_option is None:
        vars = ds_store_remover(os.listdir(f"{data_path}/{domain}"))
    else:
        vars = [var_option]

    for var in vars:

        colors = make_colors(data_path, domain, var)
        make_plot(domain, data_path, plot_path, colors, var,
                  type="yearmax")

        if var == "pr":
            make_plot(domain, data_path, plot_path, colors, var,
                      type="yearsum")
    return


def make_plot(domain, data_path, plot_path, colors, var, type):
    '''make a plot for a domain and variable combo'''

    path_timeseries = f"{data_path}/{domain}/{var}/timeseries"

    nrows = int(len(cities_lat_lon[domain])/2)

    fig, axes = plt.subplots(nrows, 2, figsize=(20, 2+4*nrows))

    for i, city in enumerate(cities_lat_lon[domain]):
        ax = axes.ravel()[i]
        driving_models = ds_store_remover(os.listdir(path_timeseries))

        # loop over driving_models
        for driving_model in driving_models:
            rcms = ds_store_remover(
                os.listdir(f"{path_timeseries}/{driving_model}"))

            for rcm in rcms:

                model_name = f"{driving_model}_{rcm}"

                data_set_path = f"{path_timeseries}/{driving_model}/{rcm}"
                files = ds_store_remover(os.listdir(data_set_path))
                files = [file for file in files if city in file]
                files = [file for file in files if type in file]

                if files != []:

                    file = files[0]
                    ds = xr.open_dataset(f"{data_set_path}/{file}")

                    # Fix known problem with downloaded data sets
                    if domain == "AUS-44" and var == "pr":
                        if model_name == "ICHEC-EC-EARTH_CCLM4-8-17-CLM3-5":
                            ds[var] = ds[var]/24
                        elif model_name == "MPI-M-MPI-ESM-LR_CCLM4-8-17-CLM3-5":
                            ds[var] = ds[var]/24

                    try:
                        ds = ds[var].squeeze(drop=True).to_dataframe()[var]
                    except:
                        print(f"Driving model: {driving_model}")
                        print(f"RCM: {rcm}")
                        print(f"City: {city}")
                        __import__('IPython').embed()

                    # change form CFTimeIndex to DatetimeIndex
                    # this test could be changed if a problem occurs
                    if ds.index.dtype == "O":
                        ds.index = ds.index.to_datetimeindex()

                    ds.plot(ax=ax, color="black", alpha=0.2, label="",
                            zorder=-1)
                    if "ERAINT" not in model_name:
                        smoother(ds).plot(
                            ax=ax,

                            label=model_name if i == nrows*2-1 else "",
                            color=colors[model_name])

        ax.set_title(f"{city_long_names[domain][city]}")

    title = f"Timeseries plots for domain: {domain}, variable: {var},"
    title = f"{title} type: {type}."
    fig.suptitle(title, size=22)

    # this is not very general FIX
    fig.legend(loc="lower center", ncol=5)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.125)

    save_dir = f"{plot_path}/{domain}/timeseries"
    os.makedirs(save_dir, exist_ok=True)
    save_file = f"{var}_{type}_timeseries.png"
    save_file = f"{save_dir}/{save_file}"

    print(f"Saving plot to: {save_file}")
    plt.savefig(save_file)


def main(args):

    if args['make-plots']:

        if '--var_option' in args:
            var_option = args['--var_option']
        else:
            var_option = None

        domain = args['--domain']

        make_plots(domain, var_option)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
