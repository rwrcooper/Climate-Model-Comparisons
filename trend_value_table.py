#!/usr/bin/env python3
"""
File: trend_value_table.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Script to make heatmap and table of values for the slope values of
    time-series data for a hazard and location pair.

Usage:
    trend_value_table.py pre-process -d <domain> [-v <var_option]
    trend_value_table.py make-table -d <domain> [-v <var_option>]

Options:
    -d <domain>, --domain=<domain>
    -v <var_option>, --var_option=<var_option>

    -h, --help
    --option=<n>
"""


from docopt import docopt
import xarray as xr
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from ds_store_remover import ds_store_remover


path = "data-link/cordex-data/mon"


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


def get_slopes(path_var, domain, var, cities_lat_lon, type):
    '''Calculate slopes for variables over 1951-2100 for each model for each
    city'''

    table = {
        "driving_model": [],
        "rcm": [],
        "city": [],
        "slope": [],
        }
    path_timeslope = f"{path_var}/timeseries_slopes"

    driving_models = ds_store_remover(os.listdir(path_timeslope))

    for driving_model in driving_models:
        path_dm = f"{path_timeslope}/{driving_model}"
        rcms = ds_store_remover(os.listdir(path_dm))

        for rcm in rcms:
            path_rcm = f"{path_dm}/{rcm}"

            for city in cities_lat_lon[domain]:

                files = ds_store_remover(os.listdir(path_rcm))

                # print(f"Rcm path: {path_rcm}")
                # print(f"Files: {files}")

                files = [file for file in files if city in file]
                files = [file for file in files if type in file]
                files = [file for file in files if "slope" in file]

                # print(f"City: {city}")
                # print(f"Type: {type}")
                # print(f"Revised files: {files}")

                file = f"{path_rcm}/{files[0]}"

                ds = xr.open_dataset(file)

                if type == "yearsum":
                    slope = float(ds.data_vars[var][0][0][0])  # *60*60*24*365
                elif type == "yearmax":
                    slope = float(ds.data_vars[var][0][0][0])  # *60*60*24

                if domain == "AUS-44":
                    if var == "pr":
                        if driving_model == "ICHEC-EC-EARTH":
                            if rcm == "CCLM4-8-17-CLM3-5":
                                slope = slope/24
                        elif driving_model == "MPI-M-MPI-ESM-LR":
                            if rcm == "CCLM4-8-17-CLM3-5":
                                slope = slope/24

                table["driving_model"].append(driving_model)
                table["rcm"].append(rcm)
                table["city"].append(city)
                table["slope"].append(slope)

    table = pd.DataFrame(table)

    csv_save = f'slope_tables/{domain}_{var}_{type}.csv'
    print(f"Saving table to: {csv_save}")
    table.to_csv(csv_save)

    table_gb = table.groupby(
        ['driving_model', 'rcm', 'city', 'slope']).size().to_frame()

    html_save = f'slope_tables/{domain}_{var}_{type}.html'
    print(f"Saving table to: {html_save}")

    with open(html_save, 'w') as f:
        f.write(table_gb.to_html())

    table_test = table.set_index(
        ["driving_model", "rcm", "city"]).unstack("city").T

    vmin = table.slope.min()
    vmax = table.slope.max()

    if var != "tasmax":
        vmax = max(-vmin, vmax)
        vmin = -vmax

    if var == "pr":
        cmap = "RdBu"
    elif var == "hurs":
        cmap = "RdBu"
    elif var == "sfcWindmax":
        cmap = "RdBu_r"
    elif var == "tasmax":
        cmap = "inferno"

    # vmin, vmax, quantiles - this can be altered if required
    if var == "pr":
        hm = sns.heatmap(table_test, cmap=cmap, vmin=vmin*0.95, vmax=vmax*0.95)
    else:
        hm = sns.heatmap(table_test, cmap=cmap, vmin=vmin, vmax=vmax)

    fig = hm.get_figure()

    plt.tight_layout()

    save_dir = f"data-link/cordex-data/plots/{domain}/slope_heatmaps"

    os.makedirs(save_dir, exist_ok=True)

    save_file = f"{domain}_{var}_{type}_slopes_heatmap.png"

    save_path = f"{save_dir}/{save_file}"

    print(f"Saving heatmap to: {save_path}")
    fig.savefig(save_path, dpi=400)
    plt.close()


def getslope_given_var_option(path, domain, cities_lat_lon, type, var):
    '''extract slope given variable'''

    path_var = f"{path}/{var}"

    if var == "pr":
        get_slopes(path_var, domain, var, cities_lat_lon,
                   type="yearmax")
        get_slopes(path_var, domain, var, cities_lat_lon,
                   type="yearsum")
    else:
        get_slopes(path_var, domain, var, cities_lat_lon,
                   type="yearmax")


def make_table(path, domain, type, cities_lat_lon, var_option):
    '''Make a table of values of the slopes.'''

    path = f"{path}/{domain}"

    vars = ds_store_remover(os.listdir(path))

    if var_option is None:
        for var in vars:
            getslope_given_var_option(path, domain, cities_lat_lon, type, var)
    else:
        getslope_given_var_option(path, domain, cities_lat_lon, type,
                                  var=var_option)


def make_slope(path_var, domain, var, cities_lat_lon, type):
    '''calculates slopes for a domain, var combo.'''

    path_timeslope = f"{path_var}/timeseries_slopes"
    path_timeseries = f"{path_var}/timeseries"
    os.makedirs(path_timeslope, exist_ok=True)

    driving_models = ds_store_remover(os.listdir(path_timeseries))
    driving_models = [dm for dm in driving_models if "ERAINT" not in dm]

    for driving_model in driving_models:
        path_dm = f"{path_timeseries}/{driving_model}"
        rcms = ds_store_remover(os.listdir(path_dm))

        for rcm in rcms:
            path_rcm = f"{path_dm}/{rcm}"

            for city in cities_lat_lon[domain]:

                files = ds_store_remover(os.listdir(path_rcm))
                files = [file for file in files if city in file]
                files = [file for file in files if type in file]

                print(f"Path: {path_rcm}")

                infile = f"{path_rcm}/{files[0]}"

                save_path = f"{path_timeslope}/{driving_model}/{rcm}"

                os.makedirs(save_path, exist_ok=True)

                outfile_int = f"temp/{driving_model}_{rcm}_{city}_{type}"
                outfile_int = outfile_int + "_intercept.nc"

                outfile_slope = f"temp/{driving_model}_{rcm}_{city}_{type}"
                outfile_slope = outfile_slope + "_slope.nc"

                # make files
                cmd = f"touch {outfile_int}"
                print(f"Running command: {cmd}")
                os.system(cmd)

                cmd = f"touch {outfile_slope}"
                print(f"Running command: {cmd}")
                os.system(cmd)

                cmd = "cdo -L -trend -selyear,2000/2100 "
                cmd = cmd + f"{infile} {outfile_int} {outfile_slope}"
                print(f"Running command: {cmd}")
                os.system(cmd)

                os.system(f"mv {outfile_slope} {save_path}")


def make_slope_given_var_option(path, domain, cities_lat_lon, type, var):
    '''calculate sopes given a variable'''

    path_var = f"{path}/{var}"

    if var == "pr":
        make_slope(path_var, domain, var, cities_lat_lon,
                   type="yearmax")
        make_slope(path_var, domain, var, cities_lat_lon,
                   type="yearsum")
    else:
        make_slope(path_var, domain, var, cities_lat_lon,
                   type="yearmax")


def pre_process(path, domain, type, cities_lat_lon, var_option):
    '''Execute all pre processing'''

    path = f"{path}/{domain}"

    vars = ds_store_remover(os.listdir(path))

    if var_option is None:
        for var in vars:
            make_slope_given_var_option(path, domain, cities_lat_lon, type,
                                        var)

    else:
        make_slope_given_var_option(path, domain, cities_lat_lon, type,
                                    var=var_option)


def main(args):

    domain = args['--domain']

    if '--var_option' in args:
        var_option = args['--var_option']
    else:
        var_option = None

    if args['pre-process']:
        pre_process(path, domain, type, cities_lat_lon, var_option)
    elif args['make-table']:
        make_table(path, domain, type, cities_lat_lon, var_option)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
