#!/usr/bin/env python3
"""
File: easy_model_downloader.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Easy downloader: downloads all 'needed' data for a given domain, variable,
    time_frequecy triplet. That is, historical data, rcp85 scenario and
    evaluation data, using the model_downloader.py script.

Usage:
    easy_model_downloader.py -d <domain>... -v <variable>... -t <time_frequency>

Options:
    -d <domain>, --domains=<domain>
    -v <variable>, --variable=<variable>
    -t <time_frequency>, --time_frequency=<time_frequency>

    -h, --help
    --option=<n>
"""


import os
from docopt import docopt


script_dir = "scripts/multi-model"


def model_downloader(domains, variables, time_frequency):
    '''Funciton to download CORDEX data
        from ESGF using model_downloader.py script.'''

    cmd = f"python3 {script_dir}/model_downloader.py"

    # get domain selections from arguments
    domain_options = " -d ".join(domains)
    # format for use as arguments running with model_downloader.py
    domain_options = f"-d {domain_options}"

    # get variable selections from arguments
    variable_options = " -v ".join(variables)
    # format for use as arguments running with model_downloader.py
    variable_options = f"-v {variable_options}"

    # collate all arguments
    options = f"{domain_options} {variable_options} -t {time_frequency}"

    # add all relevant experiments (hard coded)
    experiments = "-e historical -e rcp85 -e evaluation"

    # make and run command
    cmd = f"{cmd} {options} {experiments}"
    print(f"Running command: {cmd}")
    os.system(cmd)

    return


def main(args):

    domains = args['--domains']
    variables = args['--variable']
    time_frequency = args['--time_frequency']

    model_downloader(domains, variables, time_frequency)

    return


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
