def ds_store_remover(dirs):
    'Removes .DS_Store from dir list.'

    dirs = [dir for dir in dirs if dir != ".DS_Store"]
    return dirs
