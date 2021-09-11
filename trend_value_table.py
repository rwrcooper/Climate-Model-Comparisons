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
import json


path = "data-link/cordex-data/mon"


# load cities_lat_lon
dict = open("cities_lat_lon.json")
cities_lat_lon = json.load(dict)


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
