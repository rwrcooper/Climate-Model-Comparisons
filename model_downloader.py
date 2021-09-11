#!/usr/bin/env python3
"""
File: model_downloader.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Downloads CORDEX model data sets from ESGF, and saves in organised
    directories. This downloader checks if files are already downloaded
    before downloading again. Arguments that must be included:
    domain: e.g. AUS-44
    variable: e.g. tasmax
    time_frequency e.g. day
    experiment: e.g. rcp85
    Options for including driving_model (GCM) and rcm_name.

Usage:
    model_downloader -d <domain>... -v <variable>... -t <time_frequency>... -e <experiment>... [-g <driving_model>]...[-r <rcm_name>]...

Options:
    -d <domain>, --domains=<domain>
    -v <variable>, --variables=<variable>
    -t <time_frequency>, --time_frequencies=<time_frequency>
    -e <experiment>, --experiments=<experiment>
    -g <driving_model>, --driving_models=<driving_model>
    -r <rcm_name>, --rcm_names=<rcm_name>

    -h, --help
    --option=<n>
"""

from pyesgf.search import SearchConnection
import os
from pyesgf.logon import LogonManager
import ssl
import tempfile
from docopt import docopt

ssl._create_default_https_context = ssl._create_unverified_context


# openid = 'https://esgf-data.dkrz.de/esgf-idp/openid/rileycooper'
openid = 'https://esgf.nci.org.au/esgf-idp/openid/riley'


password = 'ZjLaYpWNP0*'
openid_c = 'riley'


def connection():
    '''creates a connection to ESGF'''

    conn = SearchConnection('https://esgf-node.llnl.gov/esg-search',
                            distrib=True)

    # conn = SearchConnection('https://esgf-data.dkrz.de/search/esgf-dkrz/',
    #                         distrib=True)

    # openid = 'https://esgf.nci.org.au/esgf-idp/openid/riley'

    lm = LogonManager()
    try:
        lm.logon_with_openid(openid, password)
    except:
        lm.logon_with_openid(openid, password, bootstrap=True)

    print("Connection secured.")
    return conn


meta_data = ['time_frequency', 'domain', 'variable', 'experiment',
             'driving_model', 'rcm_name']

file_path = "data-link/cordex-data"


def make_path(result):
    '''Makes a path to where the data will be saved.'''

    file_path = "data-link/cordex-data"

    path_list = []
    ds_json = result.json
    for data in meta_data:

        to_append = ds_json[data][0]
        path_list.append(to_append)

    dir = file_path
    for i in path_list:
        dir = dir + "/" + i
    return dir


def download_data(result, download_dir):
    '''Downoads a single data set from a search of ESGF and saves in given
    directory (path).'''

    fc = result.file_context()
    wget_script_content = fc.get_download_script()

    script_path = tempfile.mkstemp(suffix='.sh', prefix='download-')[1]
    with open(script_path, "w") as writer:
        writer.write(wget_script_content)

    print(f'Runnng script: {script_path}')

    os.system(f"bash {script_path}")
    os.system(f"mv *nc {download_dir}")


def download_cordex_data(search_args):
    '''Searches ESGF and downloads all data that matches the search.'''

    print("Creating connection.")
    conn = connection()

    ctx = conn.new_context(
        project='CORDEX',
        domain=search_args["domains"],
        time_frequency=search_args["time_frequencies"],
        variable=search_args["variables"],
        experiment=search_args["experiments"],
        driving_model=search_args["driving_models"],
        rcm_name=search_args["rcm_names"]
        )

    hc = ctx.hit_count

    if hc == 0:
        print("No models matching search arguments.")
    else:
        print(f"Number of datasets matching search arguments: {hc}")

    for result in ctx.search(ignore_facet_check=True):

        download_dir_path = make_path(result)
        print(f"Saving files to: {download_dir_path}")
        os.makedirs(download_dir_path, exist_ok=True)

        files_to_download = result.json["number_of_files"]
        files_in_dir = len(
            [file for file in os.listdir(download_dir_path) if ".nc" in file])

        if not files_to_download == files_in_dir:
            print(f"Downloading {files_to_download} files.")
            print(f"Files to download: {files_to_download}")
            print(f"Files currently in dir: {files_in_dir}")
            # __import__('IPython').embed()
            if files_in_dir == 0:
                download_data(result, download_dir_path)
        else:
            if files_in_dir == files_to_download:
                print("Files already downloaded.")
            else:
                print("Warning: files in directory != files to download.")


def make_search_args(args):
    '''Creates strings to be used in ESGF search to create a new context.'''

    search_items = ["domains", "variables", "time_frequencies", "experiments",
                    "driving_models", "rcm_names"]

    search_args = {}

    for search_item in search_items:
        search_args[search_item] = ",".join(args["--"+search_item])

    for search_item in search_items[-2:]:
        if search_args[search_item] == "":
            search_args[search_item] = None

    return search_args


def main(args):

    search_args = make_search_args(args)
    download_cordex_data(search_args)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
