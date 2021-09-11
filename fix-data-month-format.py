#!/usr/bin/env python3
"""
File: fix-data-month-format.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Changes file name format for cordex monthly data from YYYYMMDD to YYYYMM,
    to be used only when files names use YYYYMMDD instead of the standard
    YYYYMM. Doesn't check format beofre executing change, this needs to be done
    manually.

Usage:
    fix-data-month-format.py -p <path>

Options:
    -p <path>, --path=<path>

    -h, --help
    --option=<n>
"""

from docopt import docopt
import os


def ds_store_remover(dirs):
    '''Removes .DS_Store from dir list.'''

    dirs = [dir for dir in dirs if dir != ".DS_Store"]
    return dirs


def fix_format(path):
    '''change format from YYYYMMDD to YYYYMM'''

    # get file names
    files = ds_store_remover(os.listdir(path))

    for file in files:
        # create new file names
        file_new = f"{file[0:-14]}-{file[-11:-5]}.nc"

        # change file name
        cmd = f"mv {path}/{file} {path}/{file_new}"
        print(f"Running command: {cmd}")
        os.system(cmd)


def main(args):

    path = args['--path']

    fix_format(path)


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
