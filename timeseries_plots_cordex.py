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


cities_lat_lon = {
    "AUS-44": {
        "wr": 0,  # Whole Region
        "syd": {"lat": -33.8688, "lon": 151.2093},  # Sydney
        "ali": {"lat": -23.6980, "lon": 133.8807},  # Adelaide
        "per": {"lat": -31.9505, "lon": 115.8605},  # Perth
        "mel": {"lat": -37.8136, "lon": 144.9631},  # Melbourne
        "auc": {"lat": -36.8483, "lon": 174.7625},  # Aucland
    },
    "EUR-44": {
        "wr": 0,  # Whole Region
        "ldn": {"lat": 51.5074, "lon": -0.1278},  # London
        "lis": {"lat": 38.7223, "lon": -9.1393},  # Lisbon
        "mad": {"lat": 40.4168, "lon": -3.7038},  # Madrid
        "rom": {"lat": 41.9028, "lon": 12.4964},  # Rome
        "osl": {"lat": 59.9139, "lon": 10.7522},  # Oslo
        "bud": {"lat": 47.4979, "lon": 19.0402},  # Budapest
        "ber": {"lat": 52.5200, "lon": 13.4050},  # Berlin
    },
    "AFR-44": {
        "wr": 0,  # Whole Region
        "cai": {"lat": 30.0444, "lon": 31.2357},  # Cairo
        "mar": {"lat": 31.6295, "lon": -7.9811},  # Marrakesh
        "cap": {"lat": -33.9249, "lon": 18.4241},  # Capetown
        "lus": {"lat": -15.3875, "lon": 28.3228},  # Lusaka
        "ant": {"lat": -18.8792, "lon": 47.5079},  # Antananarivo
        "aga": {"lat": 16.9742, "lon": 7.9865},  # Agadez
        "abu": {"lat": 24.4539, "lon": 54.3773},  # Abu Dhabi
    },
    "SAM-44": {
        "wr": 0,  # Whole Region
        "bue": {"lat": -34.6037, "lon": -58.3816},  # Buenos Aires
        "rio": {"lat": -22.9068, "lon": -43.1729},  # Rio de Janeiro
        "san": {"lat": -33.4489, "lon": -70.6693},  # Santiago
        "lim": {"lat": -12.0464, "lon": -77.0428},  # Lima
        "cru": {"lat": -17.8146, "lon": -63.1561},  # Santa Cruz de la Sierra
        "bog": {"lat": 4.7110, "lon": -74.0721},  # Bogota
        "car": {"lat": 10.4806, "lon": -66.9036},  # Caracas
    },
    "EAS-44": {
        "wr": 0,  # Whole Region
        "tok": {"lat": 35.6762, "lon": 139.6503},  # Tokyo
        "bei": {"lat": 39.9042, "lon": 116.4074},  # Beijing
        "ban": {"lat": 13.7563, "lon": 100.5018},  # Bangkok
        "kat": {"lat": 27.7172, "lon": 85.3240},  # Kathmandu
        "han": {"lat": 21.0278, "lon": 105.8342},  # Hanoi
        "new": {"lat": 28.6139, "lon": 77.2090},  # New Delhi
        "man": {"lat": 14.5995, "lon": 120.9842},  # Manila
    },
    "NAM-44": {
        "wr": 0,  # Whole Region
        "los": {"lat": 34.0522, "lon": -118.2437},  # Los Angeles
        "new": {"lat": 40.7128, "lon": -74.0060},  # New York
        "mia": {"lat": 25.7617, "lon": -80.1918},  # Miami
        "las": {"lat": 36.1699, "lon": -115.1398},  # Las Vegas
        "van": {"lat": 49.2827, "lon": -123.1207},  # Vancouver
        "anc": {"lat": 61.2181, "lon": -149.9003},  # Anchorage
        "hou": {"lat": 29.7604, "lon": -95.3698},  # Houston
    },
    "CAM-44": {
        "wr": 0,  # Whole Region
        "mex": {"lat": 19.4326, "lon": -99.1332},  # mexico city
        "kin": {"lat": 18.0179, "lon": -76.8099},  # kingston
        "hav": {"lat": 23.1136, "lon": -82.3666},  # havana
        "spr": {"lat": 18.4655, "lon": -66.1057},  # san juan puerto rico
        "mer": {"lat": 20.9674, "lon": -89.5926},  # merida
        "mon": {"lat": 25.6866, "lon": -100.3161},  # monterrey
        "tij": {"lat": 32.5149, "lon": -117.0382},  # tijuana
        "her": {"lat": 29.0730, "lon": -110.9559},  # hermosillo
        "gua": {"lat": 20.6597, "lon": -103.3496},  # guadalajara
    },
}


city_long_names = {
    "AUS-44": {
        "wr": "Whole region",
        "syd": "Syndey",
        "ali": "Alice Springs",
        "per": "Perth",
        "mel": "Melbourne",
        "auc": "Auckland",
        },
    "EUR-44": {
        "wr": "Whole region",
        "ldn": "London",
        "edn": "Edinburgh",
        "bel": "Belfast",
        "bri": "Bristol",
        "lis": "Lisbon",
        "mad": "Madrid",
        "rom": "Rome",
        "rey": "Reykjavic",
        "osl": "Oslo",
        "bud": "Budapest",
        "ber": "Berlin",
    },
    "AFR-44": {
        "wr": "Whole region",
        "cai": "Cairo",
        "mar": "Marrakesh",
        "cap": "Cape Town",
        "lus": "Lusaka",
        "ant": "Antananarivo",
        "aga": "Agadez",
        "abu": "Abu Dhabi",
    },
    "SAM-44": {
        "wr": "Whole region",
        "bue": "Buenos Aires",
        "rio": "Rio de Janeiro",
        "san": "Santiago",
        "lim": "Lima",
        "cru": "Santa Cruz de la Sierra",
        "bog": "Bogota",
        "car": "Caracas",
    },
    "EAS-44": {
        "wr": "Whole region",
        "tok": "Tokyo",
        "bei": "Beijing",
        "ban": "Bangkok",
        "kat": "Kathmandu",
        "han": "Hanoi",
        "new": "New Delhi",
        "man": "Manila",
    },
    "NAM-44": {
        "wr": "Whole region",
        "los": "Los Angeles",
        "new": "New York",
        "mia": "Miami",
        "las": "Las Vegas",
        "van": "Vancouver",
        "anc": "Anchorage",
        "hou": "Houston",
    },
    "CAM-44": {
        "wr": "Whole region",
        "mex": "Mexico City",
        "kin": "Kingston",
        "hav": "Havana",
        "spr": "San Juan",
        "mer": "Merida",
        "mon": "Monterrey",
        "tij": "Tijuana",
        "her": "Hermosillo",
        "gua": "Guadalajara",
    },
}


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

        # another quick test

        # quick test
        if domain == "EUR-44":
            if var == "tasmax" or var == "hurs":
                driving_models = [dm for dm in driving_models if dm != "MOHC-HadGEM2-ES"]

        # fix
        if domain == "AFR-44":
            if var == "sfcWindmax":
                driving_models = [dm for dm in driving_models if dm != "MOHC-HadGEM2-ES"]

        if domain == "AFR-44":
            if var == "pr":
                driving_models = [dm for dm in driving_models if dm != "MPI-M-MPI-ESM-MR"]

        # loop over driving_models
        for driving_model in driving_models:
            rcms = ds_store_remover(
                os.listdir(f"{path_timeseries}/{driving_model}"))

            # quick fix
            if domain == "EUR-44":
                if var == "tasmax":
                    if driving_model == "MPI-M-MPI-ESM-LR":
                        rcms = [rcm for rcm in rcms if rcm != "CCLM4-8-17"]

            for rcm in rcms:

                model_name = f"{driving_model}_{rcm}"

                data_set_path = f"{path_timeseries}/{driving_model}/{rcm}"
                files = ds_store_remover(os.listdir(data_set_path))
                files = [file for file in files if city in file]
                files = [file for file in files if type in file]

                if files != []:

                    file = files[0]
                    ds = xr.open_dataset(f"{data_set_path}/{file}")

                    # Fix known data problem
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
                    # but the test is not the best
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

        # TODO: Time ticks need fixing so I'll leave comments for now

        # TODO: fix from here to fix formatting and possibly the ticks etc
        # ax.set_xticks([1960, 1980, 2000, 2020, 2040, 2060, 2080, 2100])
        # if city != "cap" and city != "aga":
        if city == "cap" or city == "aga":
            ax.get_xaxis().set_visible(True)
        # else:
        # TODO: another weird test
        # if city == "cap" or city == "aga":
        #     ax.set_xticks([1960, 1980, 2000, 2020, 2040, 2060, 2080, 2100])

    title = f"Timeseries plots for domain: {domain}, variable: {var},"
    title = f"{title} type: {type}."
    fig.suptitle(title, size=22)

    # TODO: this is not very general
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
