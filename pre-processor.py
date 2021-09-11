#!/usr/bin/env python3
"""
File: pre-processor.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Pre-processes CRODEX data to then be used in analyses. Executes the 4 types
    of pre-processing we need to then produce intercomparrison plots.
    Evaluation and rcp convert the models to yearly metrics through a yearsum
    or yearmax depending on relevance to speci hazard.

Usage:
    pre-processor.py evaluation -d <domain> [-v <var_option]
    pre-processor.py rcp -d <domain> [-v <var_option]
    pre-processor.py timeseries -d <domain> [-v <var_option]
    pre-processor.py slope -d <domain> [-v <var_option]

Options:
    -d <domain>, --domain=<domain>
    -v <var_option>, --var_option=<var_option>

    -h, --help
    --option=<n>
"""


from docopt import docopt
import xarray as xr
import os
from ds_store_remover import ds_store_remover
import json


path = "data-link/cordex-data/mon"


# load cities_lat_lon
dict = open("cities_lat_lon.json")
cities_lat_lon = json.load(dict)


dist = 1


def pre_process_data_given_var_option(path, domain, type, var):
    '''preprocesses data given choice of variable, domain and type, type can be
    evaluation, rcp, timeseries or slope. '''

    path_var = f"{path}/{var}"

    if type == "evaluation":
        pre_process_eval(path_var, domain, var)
    elif type == "rcp":
        pre_process_rcp85(path_var, domain, var)
    elif type == "timeseries":
        pre_process_timeseries(
            path_var,
            domain,
            var,
            cities_lat_lon,
            experiment="rcp85")

        pre_process_timeseries(
            path_var,
            domain,
            var,
            cities_lat_lon,
            experiment="evaluation")

        pre_process_eval_ensmean(
            path,
            domain,
            var,
            cities_lat_lon)

    elif type == "slope":
        pre_process_slope_timmean(path_var, domain, var)


def pre_process_data(path, domain, type, var_option):
    '''execute preprocessing for a given domain, type and variable option.'''

    path = f"{path}/{domain}"

    vars = ds_store_remover(os.listdir(path))

    if var_option is None:
        for var in vars:
            pre_process_data_given_var_option(path, domain, type, var)

    else:
        pre_process_data_given_var_option(path, domain, type, var_option)


def pre_process_eval(path, domain, var):
    '''preprocess evaluation data.'''
    driving_model = "ECMWF-ERAINT"
    raw_file_path = f"{path}/evaluation/{driving_model}"
    out_path = f"{path}/combined_eval/{driving_model}"

    rcms = ds_store_remover(os.listdir(raw_file_path))
    for rcm in rcms:
        eval_mergetime(raw_file_path, rcm, out_path, type="yearmax")

        if var == "pr":
            eval_mergetime(raw_file_path, rcm, out_path, type="yearsum")


def eval_mergetime(path, rcm, out_path, type):
    '''merge ecvaluation data.'''
    print(f"Path: {path}/{rcm}")
    file_first = ds_store_remover(os.listdir(f"{path}/{rcm}"))[0]
    file_last = ds_store_remover(os.listdir(f"{path}/{rcm}"))[-1]
    file_name = file_first[:-16]

    start_year = file_first[-16:-12]
    end_year = file_last[-9:-5]

    infiles = f"{path}/{rcm}/*"
    file_name = f"{file_name}{start_year}-{end_year}_{type}.nc"

    save_path = f"{out_path}/{rcm}"
    os.makedirs(save_path, exist_ok=True)
    outfile = f"{save_path}/{file_name}"

    cmd = f"cdo -L -{type} -mergetime {infiles} {outfile}"
    print(f"Running command: {cmd}")
    os.system(cmd)


def pre_process_rcp85(path, domain, var):
    '''combines historical and rcp data'''

    os.makedirs(f"{path}/combined_rcp85", exist_ok=True)

    driving_models = ds_store_remover(os.listdir(f"{path}/rcp85"))
    for driving_model in driving_models:
        rcms = ds_store_remover(
                   os.listdir(
                       f"{path}/rcp85/{driving_model}"))
        for rcm in rcms:

            os.makedirs(
                f"{path}/combined_rcp85/{driving_model}/{rcm}",
                exist_ok=True)

            file_name = ds_store_remover(
                os.listdir(f"{path}/rcp85/{driving_model}/{rcm}"))[0][:-16]
            save_file = f"{file_name}1950-2100_yearmax.nc"
            infile_hist = f"{path}/historical/{driving_model}/{rcm}/*"
            infile_rcp = f"{path}/rcp85/{driving_model}/{rcm}/*"
            infiles = f"{infile_hist} {infile_rcp}"
            outfile = f"{path}/combined_rcp85/{driving_model}/{rcm}"
            outfile = f"{outfile}/{save_file}"
            cmd = f"cdo -L -yearmax -mergetime {infiles} {outfile}"
            print(f"Running command: {cmd}")
            os.system(cmd)

            if var == "pr":
                save_file = f"{file_name}1950-2100_yearsum.nc"
                outfile = f"{path}/combined_rcp85/{driving_model}/{rcm}"
                outfile = f"{outfile}/{save_file}"
                cmd = f"cdo -L -yearsum -mergetime {infiles} {outfile}"
                print(f"Running command: {cmd}")
                os.system(cmd)


def make_ensmean(domain, city, var, path_timeseries_eval, type):
    '''makes ensemble mean of data'''

    driving_model = "ECMWF-ERAINT"

    infiles = []
    rcms = ds_store_remover(os.listdir(path_timeseries_eval))
    rcms = [rcm for rcm in rcms if rcm != "ensmean"]
    for rcm in rcms:
        files = ds_store_remover(os.listdir(
            f"{path_timeseries_eval}/{rcm}"))

        files = [file for file in files if type in file]
        files = [file for file in files if city in file]

        print(f"Path: {path}")
        print(f"driving_model: {driving_model}")
        print(f"rcm: {rcm}")
        print(f"city: {city}")

        file = files[0]
        file = f"{path_timeseries_eval}/{rcm}/{file}"

        infiles.append(file)

    infiles = " ".join(infiles)

    out_path = f"{path_timeseries_eval}/ensmean"

    outfile = f"{var}_{domain}_{driving_model}_evaluation_ensmean_{type}"
    outfile = f"{outfile}_{city}.nc"

    outfile = f"{out_path}/{outfile}"

    cmd = f"cdo -L -ensmean {infiles} {outfile}"
    print(f"Running command: {cmd}")
    os.system(cmd)


def pre_process_eval_ensmean(path, domain, var, cities_lat_lon):
    ''''''
    path_timeseries_eval = f"{path}/{var}/timeseries"
    path_timeseries_eval = f"{path_timeseries_eval}/ECMWF-ERAINT"
    path_ensmean = f"{path_timeseries_eval}/ensmean"

    os.makedirs(path_ensmean, exist_ok=True)

    for city in cities_lat_lon[domain]:

        make_ensmean(domain, city, var, path_timeseries_eval, type="yearmax")

        if var == "pr":
            make_ensmean(domain, city, var, path_timeseries_eval,
                         type="yearsum")


def pre_process_timeseries(path, domain, var, cities_lat_lon, experiment):
    '''makes timeseries data for domain, variable and each city'''

    os.makedirs(f"{path}/timeseries", exist_ok=True)

    if experiment == "rcp85":
        driving_models = ds_store_remover(os.listdir(f"{path}/combined_rcp85"))
    elif experiment == "evaluation":
        driving_models = ["ECMWF-ERAINT"]

    for driving_model in driving_models:
        rcms = ds_store_remover(
            os.listdir(f"{path}/{experiment}/{driving_model}"))

        if experiment == "evaluation":
            rcms = [rcm for rcm in rcms if rcm != "ensmean"]

        for rcm in rcms:
            os.makedirs(
                f"{path}/timeseries/{driving_model}/{rcm}",
                exist_ok=True)

            print("Searching this dir for file name.")
            print(f"{path}/{experiment}/{driving_model}/{rcm}")
            file_name = ds_store_remover(
                os.listdir(
                    f"{path}/{experiment}/{driving_model}/{rcm}"))[0][:-16]

            for city in cities_lat_lon[domain]:
                pre_process_city_rcp(domain, var, path, driving_model, rcm,
                                     city, file_name, cities_lat_lon,
                                     type="yearmax", experiment=experiment)

                if var == "pr":
                    pre_process_city_rcp(domain, var, path, driving_model, rcm,
                                         city, file_name, cities_lat_lon,
                                         type="yearsum", experiment=experiment)


def pre_process_city_rcp(domain, var, path, driving_model, rcm, city,
                         file_name, cities_lat_lon, type, experiment):
    ''''''

    if experiment == "rcp85":
        experiment_ext = "rcp85"
        start_year = "1950"
        end_year = "2100"
    elif experiment == "evaluation":
        experiment_ext = "eval"

    print(f"Path: {path}/combined_{experiment_ext}/{driving_model}/{rcm}")

    files = ds_store_remover(
        os.listdir(f"{path}/combined_{experiment_ext}/{driving_model}/{rcm}"))
    infile = [file for file in files if type in file]

    if infile:

        infile = infile[0]

        if experiment == "evaluation":

            start_year = infile[-20:-16]
            end_year = infile[-15:-11]

        infile_path = f"{path}/combined_{experiment_ext}/{driving_model}/{rcm}"
        infile = f"{infile_path}/{infile}"

        outfile = f"{path}/timeseries/{driving_model}/{rcm}"
        save_file = f"{file_name}{start_year}-{end_year}_{type}_{city}.nc"
        outfile = f"{outfile}/{save_file}"

        if city != "wr":

            data_set = xr.open_dataset(infile)

            time_bnds = data_set.time_bnds

            try:
                data_set = data_set.where(
                    (cities_lat_lon[domain][city][
                        "lat"] - dist < data_set.lat) &
                    (cities_lat_lon[domain][city][
                        "lat"] + dist > data_set.lat) &
                    (cities_lat_lon[domain][city][
                        "lon"] - dist < data_set.lon) &
                    (cities_lat_lon[domain][city][
                        "lon"] + dist > data_set.lon),
                    drop=True)

            except:
                print(f"Domain: {domain}")
                print(f"City: {city}")
                print("Error: City not found in data set.")
                return

            temp_file_path = f"{path}/timeseries/{driving_model}/{rcm}"
            temp_file = f"{temp_file_path}/temp.nc"

            data_set["time_bnds"] = time_bnds

            data_set.to_netcdf(temp_file)

            infile = temp_file

        temp_file_selyear = "temp.nc"

        operation = f"-selyear,{start_year}/{end_year}"
        cmd = f"cdo -L {operation} {infile} {temp_file_selyear}"
        print(f"Running command: {cmd}")
        os.system(cmd)

        cmd = f"cdo -L -fldmean {temp_file_selyear} {outfile}"
        print(f"Running command: {cmd}")
        os.system(cmd)

        cmd_rm = f"rm {temp_file_selyear}"
        print(f"Removing temp file: {temp_file_selyear}")
        os.system(cmd_rm)

        if city != "wr":
            cmd_rm = f"rm {temp_file}"
            print(f"Running command: {cmd}")
            os.system(cmd_rm)
    else:
        print("No such file.")


def make_slope_timmean(path, domain, var, driving_model, rcm, type):
    '''make slopes and timmeans of a single model'''

    path_combined_rcp85 = f"{path}/combined_rcp85"

    path_rcm = f"{path_combined_rcp85}/{driving_model}/{rcm}"
    infile = ds_store_remover(os.listdir(path_rcm))

    infile = [file for file in infile if type in file]
    print(f"Path: {path_rcm}")
    print(f"Infiles: {infile}")

    infile = infile[0]
    print(f"Infile: {infile}")

    infile = f"{path_rcm}/{infile}"

    save_dir_timmean = f"{path}/timmean/{driving_model}/{rcm}"
    save_dir_slope = f"{path}/slope/{driving_model}/{rcm}"

    print(f"Making dir: {save_dir_timmean}")
    os.makedirs(save_dir_timmean, exist_ok=True)
    print(f"Making dir: {save_dir_slope}")
    os.makedirs(save_dir_slope, exist_ok=True)

    outfile_timmean = f"{var}_{domain}_{driving_model}_rcp85_{rcm}_{type}"
    outfile_timmean = f"{outfile_timmean}_timmean.nc"
    outfile_timmean = f"{save_dir_timmean}/{outfile_timmean}"

    outfile_intercept = f"{var}_{domain}_{driving_model}_rcp85_{rcm}_{type}"
    outfile_intercept = f"{outfile_intercept}_intercept.nc"
    outfile_intercept = f"{save_dir_slope}/{outfile_intercept}"

    outfile_slope = f"{var}_{domain}_{driving_model}_rcp85_{rcm}_{type}"
    outfile_slope = f"{outfile_slope}_slope.nc"
    outfile_slope = f"{save_dir_slope}/{outfile_slope}"

    ops_timmean = "-timmean -selyear,1981/2010"
    cmd_timmean = f"cdo -L {ops_timmean} {infile} {outfile_timmean}"

    print(f"Running command: {cmd_timmean}")
    os.system(cmd_timmean)

    # hack to allow trend operation to work, permission denied in outfile2
    # (outfile_slope)
    cmd_hack = f'echo "" > {outfile_slope}'
    print(f"Running command: {cmd_hack}")
    os.system(cmd_hack)

    ops_slope = "-trend -selyear,2000/2100"
    cmd_slope = (f"cdo -L {ops_slope} {infile} {outfile_intercept} "
                 f"{outfile_slope}")

    print(f"Running command: {cmd_slope}")
    os.system(cmd_slope)

    cmd_rm_intercept = f"rm {save_dir_slope}/*intercept*nc"
    print(f"Running command: {cmd_rm_intercept}")
    os.system(cmd_rm_intercept)


def pre_process_slope_timmean(path, domain, var):
    '''make slopes and timmeans for all models given a domain and variable
        combo of data for each model using the combined data set'''

    path_combined_rcp85 = f"{path}/combined_rcp85"

    driving_models = ds_store_remover(os.listdir(path_combined_rcp85))

    for driving_model in driving_models:
        rcms = ds_store_remover(
            os.listdir(f"{path_combined_rcp85}/{driving_model}"))
        for rcm in rcms:

            make_slope_timmean(
                path,
                domain,
                var,
                driving_model,
                rcm,
                type="yearmax")

            if var == "pr":

                make_slope_timmean(
                    path,
                    domain,
                    var,
                    driving_model,
                    rcm,
                    type="yearsum")


def main(args):

    if args['evaluation']:
        type = "evaluation"
    elif args['rcp']:
        type = "rcp"
    elif args['timeseries']:
        type = 'timeseries'
    elif args['slope']:
        type = 'slope'

    domain = args['--domain']

    if '--var_option' in args:
        var_option = args['--var_option']
    else:
        var_option = None

    pre_process_data(path, domain, type, var_option)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
