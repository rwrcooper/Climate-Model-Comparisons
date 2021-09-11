#!/usr/bin/env python3
"""
File: data-mover.py
Author: riley cooper
Email: rwr.cooper@gmail.com
Description:
    Script to move data to different directory organisation.
    Not very relevant any more.

Usage:
    data-mover.py change-structure
    data-mover.py to-hard-drive

Options:
    -h, --help
    --option=<n>
"""


from docopt import docopt
import os


path_initial = "data/cordex-data"
path_hd = "data-link/cordex-data"


def ds_store_remover(dirs):
    'Removes .DS_Store from dir list.'

    dirs = [dir for dir in dirs if dir != ".DS_Store"]
    return dirs


def new_dir_maker(var, dom, driving_model, rcm, tim, exp):
    new_dir = f"{path_initial}/{tim}/{dom}/{var}/{exp}/{driving_model}/{rcm}"
    return new_dir


def move_data():

    vars = ds_store_remover(os.listdir(path_initial))
    for var in vars:
        path_var = f"{path_initial}/{var}"
        doms = ds_store_remover(os.listdir(path_var))
        for dom in doms:
            path_dom = f"{path_var}/{dom}"
            driving_models = ds_store_remover(os.listdir(path_dom))
            for driving_model in driving_models:
                path_driv = f"{path_dom}/{driving_model}"
                rcms = ds_store_remover(os.listdir(path_driv))
                for rcm in rcms:
                    path_rcm = f"{path_driv}/{rcm}"
                    tims = ds_store_remover(os.listdir(path_rcm))
                    for tim in tims:
                        path_tim = f"{path_rcm}/{tim}"
                        exps = ds_store_remover(os.listdir(path_tim))
                        for exp in exps:
                            path_exp = f"{path_tim}/{exp}"
                            old_dir = path_exp
                            print(f"Old dir: {old_dir}")
                            new_dir = new_dir_maker(var, dom, driving_model,
                                                    rcm, tim, exp)
                            print(f"New dir: {new_dir}")
                            os.makedirs(new_dir, exist_ok=True)
                            cmd = f"mv {old_dir}/* {new_dir}"
                            print(f"Running command: {cmd}")
                            os.system(cmd)


def move_data_hd():

    tims = ds_store_remover(os.listdir(path_initial))
    for tim in tims:
        path_tim = f"{tim}"
        doms = ds_store_remover(os.listdir(f"{path_initial}/{path_tim}"))
        for dom in doms:
            path_dom = f"{path_tim}/{dom}"
            vars = ds_store_remover(os.listdir(f"{path_initial}/{path_dom}"))
            for var in vars:
                path_var = f"{path_dom}/{var}"
                exps = ds_store_remover(os.listdir(
                    f"{path_initial}/{path_var}"))
                for exp in exps:
                    path_exp = f"{path_var}/{exp}"
                    driving_models = ds_store_remover(os.listdir(
                        f"{path_initial}/{path_exp}"))
                    for driving_model in driving_models:
                        path_driv = f"{path_exp}/{driving_model}"
                        rcms = ds_store_remover(os.listdir(
                            f"{path_initial}/{path_driv}"))
                        for rcm in rcms:
                            path_rcm = f"{path_driv}/{rcm}"

                            old_dir = f"{path_initial}/{path_rcm}"
                            print(f"Old dir: {old_dir}")

                            new_dir = f"{path_hd}/{path_rcm}"
                            print(f"New dir: {new_dir}")

                            os.makedirs(new_dir, exist_ok=True)

                            cmd = f"mv {old_dir}/* {new_dir}"
                            print(f"Running command: {cmd}")

                            os.system(cmd)


def main(args):

    if args["to-hard-drive"]:
        move_data_hd()

    elif args["change-structure"]:
        move_data()


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
