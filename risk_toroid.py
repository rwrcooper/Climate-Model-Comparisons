#!/usr/bin/env python3
"""
File: risk_toroid.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    First iteration of this idea. Creates torioid/spider plot of ensemble
    metrics.

Usage:
    risk_toroid.py make-toroid -d <domain>

Options:
    -d <domain>, --domain=<domain>

    -h, --help
    --option=<n>
"""

from docopt import docopt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


path = "slope_tables"


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
}


def ds_store_remover(dirs):
    'Removes .DS_Store from dir list.'

    dirs = [dir for dir in dirs if dir != ".DS_Store"]
    return dirs


def get_slope(path_var, domain, var, cities_lat_lon, type):

    # TODO: generalise for var and type
    slope_table_path = f"{path}/{domain}_{var}_{type}.csv"

    df = pd.read_csv(slope_table_path)

    df = df.drop(df[df.city != "wr"].index)

    df = df.drop(columns=["Unnamed: 0", "city"])

    slope = df

    return slope


def get_slopes(path, domain, cities_lat_lon):

    vars = ["tasmax", "pr", "hurs", "sfcWindmax"]

    slopes = {}

    for var in vars:
        if var != "pr":
            slopes[f"{var}_yearmax"] = get_slope(path, domain, var,
                                                 cities_lat_lon,
                                                 type="yearmax")
        else:
            slopes[f"{var}_yearmax"] = get_slope(path, domain, var,
                                                 cities_lat_lon,
                                                 type="yearmax")
            slopes[f"{var}_yearsum"] = get_slope(path, domain, var,
                                                 cities_lat_lon,
                                                 type="yearsum")
    return slopes


def make_toroid(path, domain, cities_lat_lon):

    slopes = get_slopes(path, domain, cities_lat_lon)

    sv = {}

    for var in slopes:
        sv[var] = {}
        sv[var]["min"] = slopes[var].slope.min()
        sv[var]["mean"] = slopes[var].slope.mean()
        sv[var]["max"] = slopes[var].slope.max()

    df = pd.DataFrame(sv)

    df.pr_yearmax = df.pr_yearmax*60*60*24
    df.pr_yearsum = df.pr_yearsum*60*60*24*365

    haz_lims = df
    haz_lims = haz_lims.drop(index=["mean"])

    haz_lims.tasmax_yearmax["min"] = 0
    haz_lims.tasmax_yearmax["max"] = 0.05

    haz_lims.pr_yearmax["min"] = -0.05
    haz_lims.pr_yearmax["max"] = 0.05

    haz_lims.pr_yearsum["min"] = -100
    haz_lims.pr_yearsum["max"] = 100

    haz_lims.hurs_yearmax["min"] = -0.01
    haz_lims.hurs_yearmax["max"] = 0.01

    haz_lims.sfcWindmax_yearmax["min"] = -0.0075
    haz_lims.sfcWindmax_yearmax["max"] = 0.0075

    haz_lims = haz_lims.rename(index={'min': 'lb'})
    haz_lims = haz_lims.rename(index={'max': 'ub'})

    radii = pd.concat([df, haz_lims])
    radii = radii.reindex(["lb", "min", "mean", "max", "ub"])

    for col in radii.columns:
        # print(f"Doing the thing for column: {col}")
        diff = radii[col]["ub"] - radii[col]["lb"]
        # print(radii[col]["lb"])
        # print(radii[col]["min"])
        # print(radii[col]["mean"])
        # print(radii[col]["max"])
        # print(radii[col]["ub"])
        # print(f"Diff: {diff}")
        # print("Now trying the thing")
        # print(((radii[col]["min"]-radii[col]["lb"])/diff)*2 + 1)
        radii[col]["min"] = ((radii[col]["min"]-radii[col]["lb"])/diff)*2 + 1
        # print(((radii[col]["mean"]-radii[col]["lb"])/diff)*2 + 1)
        radii[col]["mean"] = ((radii[col]["mean"]-radii[col]["lb"])/diff)*2 + 1
        # print(((radii[col]["max"]-radii[col]["lb"])/diff)*2 + 1)
        radii[col]["max"] = ((radii[col]["max"]-radii[col]["lb"])/diff)*2 + 1

        radii[col]["lb"] = 1
        radii[col]["ub"] = 3

    thetas = {}
    for i, col in enumerate(df.columns):
        thetas[col] = (np.pi*2/len(df.columns))*i+np.pi/2

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.grid(False)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    # ax.set_theta_zero_location('N')

    for i, haz in enumerate(thetas):
        # TODO: protentially redifine thetas
        # maybe change ordering
        # 5 isn't general
        theta_space = np.linspace(thetas[haz], thetas[haz]+np.pi*2/5, 100)

        if i == len(thetas)-1:
            col_index = 0
        else:
            col_index = i+1

        radius_space_min = np.linspace(
            radii[haz]["min"], radii.iloc[:, col_index]["min"], 100)
        radius_space_mean = np.linspace(
            radii[haz]["mean"], radii.iloc[:, col_index]["mean"], 100)
        radius_space_max = np.linspace(
            radii[haz]["max"], radii.iloc[:, col_index]["max"], 100)

        plt.polar(theta_space, radius_space_min, 'g.', markersize=4)
        plt.polar(theta_space, radius_space_mean, 'g.', markersize=4)
        plt.polar(theta_space, radius_space_max, 'g.', markersize=4)

    for haz in thetas:
        radius_space = np.linspace(1, 3, 100)
        theta_space = np.full(100, thetas[haz])
        plt.polar(theta_space, radius_space, 'b.', markersize=4)

    theta_space = np.linspace(0, np.pi*2, 500)
    radius_space_lb = np.full(500, 1)
    radius_space_ub = np.full(500, 3)

    plt.polar(theta_space, radius_space_lb, 'b.', markersize=4)
    plt.polar(theta_space, radius_space_ub, 'b.', markersize=4)

    plt.show()


def main(args):

    domain = args['--domain']

    if args['make-toroid']:
        make_toroid(path, domain, cities_lat_lon)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
